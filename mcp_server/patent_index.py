#!/usr/bin/env python3
"""
Patent Corpus Index
Builds and searches a local USPTO patent corpus using RAG
Mirrors MPEPIndex architecture for consistency
"""

import json
import os
import pickle
import site
import sys
from typing import Any, Dict, List, Optional, Tuple

# CRITICAL: Disable user site-packages BEFORE importing third-party packages
# This prevents conflicts with global user installations
site.ENABLE_USER_SITE = False
# Remove user site-packages from sys.path if already added
user_site = site.getusersitepackages()
if user_site in sys.path:
    sys.path.remove(user_site)

import numpy as np  # noqa: E402

try:
    import faiss
    import torch
    from sentence_transformers import CrossEncoder, SentenceTransformer
except ImportError:
    print(
        "Missing dependencies. Install with: pip install sentence-transformers faiss-cpu torch",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None
    print("BM25 not available. Install with: pip install rank-bm25", file=sys.stderr)

from mcp_server.hyde import HyDEQueryExpander  # noqa: E402
from mcp_server.patent_corpus import (  # noqa: E402
    PATENT_INDEX_DIR,
    Patent,
    PatentCorpusDownloader,
    PatentTSVParser,
)
from mcp_server.utils.device import get_device  # noqa: E402


class PatentCorpusIndex:
    """
    Patent corpus search index using hybrid RAG
    Same architecture as MPEPIndex: FAISS + BM25 + HyDE + Reranking
    """

    def __init__(self, use_hyde: bool = True):
        """
        Initialize patent corpus index

        Args:
            use_hyde: Enable HyDE query expansion (default: True)
        """
        self.index_dir = PATENT_INDEX_DIR
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Index files
        self.faiss_file = self.index_dir / "patent_index.faiss"
        self.metadata_file = self.index_dir / "patent_metadata.json"
        self.bm25_file = self.index_dir / "patent_bm25.pkl"

        # Detect and use GPU if available
        self.device = get_device()

        # Models (same as MPEP)
        print("Loading embedding model (BGE-base-en-v1.5)...", file=sys.stderr)
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5", device=self.device)
        self.embedding_dim = 768

        # Cross-encoder for reranking (same as MPEP)
        print("Loading reranker (MS-MARCO MiniLM)...", file=sys.stderr)
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=self.device)

        # HyDE generator
        self.use_hyde = use_hyde
        if use_hyde:
            self.hyde_generator = HyDEQueryExpander()

        # Storage
        self.chunks = []
        self.metadata = []
        self.index = None
        self.bm25 = None

        # Load index if exists
        if self.faiss_file.exists() and self.metadata_file.exists():
            self.load_index()

    def chunk_patent(self, patent: Patent) -> List[Tuple[str, Dict]]:
        """
        Chunk a patent into searchable pieces
        Strategy: Keep semantic units together

        Returns:
            List of (chunk_text, metadata) tuples
        """
        chunks = []

        # 1. Title (always include, often very relevant)
        title_chunk = f"[TITLE] {patent.title}"
        chunks.append(
            (
                title_chunk,
                {
                    "patent_id": patent.patent_id,
                    "section": "title",
                    "cpc_codes": patent.cpc_codes,
                    "filing_date": patent.filing_date,
                    "grant_date": patent.grant_date,
                    "inventors": patent.inventors,
                    "assignee": patent.assignee,
                },
            )
        )

        # 2. Abstract (usually <500 chars, keep whole)
        if patent.abstract:
            abstract_chunk = f"[ABSTRACT] {patent.abstract}"
            chunks.append(
                (
                    abstract_chunk,
                    {
                        "patent_id": patent.patent_id,
                        "section": "abstract",
                        "cpc_codes": patent.cpc_codes,
                        "filing_date": patent.filing_date,
                        "grant_date": patent.grant_date,
                        "inventors": patent.inventors,
                        "assignee": patent.assignee,
                    },
                )
            )

        # 3. Claims (each claim separately, most important for prior art)
        for i, claim in enumerate(patent.claims):
            claim_num = i + 1
            claim_chunk = f"[CLAIM {claim_num}] {claim}"

            chunks.append(
                (
                    claim_chunk,
                    {
                        "patent_id": patent.patent_id,
                        "section": f"claim_{claim_num}",
                        "claim_number": claim_num,
                        "cpc_codes": patent.cpc_codes,
                        "filing_date": patent.filing_date,
                        "grant_date": patent.grant_date,
                        "inventors": patent.inventors,
                        "assignee": patent.assignee,
                    },
                )
            )

        # 4. Description (chunk into 500-char pieces with 100-char overlap)
        if patent.description:
            desc_chunks = self._chunk_text(patent.description, chunk_size=500, overlap=100)
            for i, desc_chunk in enumerate(desc_chunks):
                chunk_text = f"[DESCRIPTION] {desc_chunk}"
                chunks.append(
                    (
                        chunk_text,
                        {
                            "patent_id": patent.patent_id,
                            "section": f"description_{i+1}",
                            "cpc_codes": patent.cpc_codes,
                            "filing_date": patent.filing_date,
                            "grant_date": patent.grant_date,
                            "inventors": patent.inventors,
                            "assignee": patent.assignee,
                        },
                    )
                )

        return chunks

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks (same as MPEP)"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(". ")
                if last_period > chunk_size * 0.6:  # At least 60% into chunk
                    chunk = chunk[: last_period + 1]
                    end = start + last_period + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def build_index(
        self,
        force_rebuild: bool = False,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ):
        """
        Build search index from downloaded patent corpus

        Args:
            force_rebuild: Force rebuild even if index exists
            start_year: Only index patents from this year onwards (e.g., 2020)
            end_year: Only index patents up to this year (e.g., 2025)
        """
        # Check if index exists
        if not force_rebuild and self.index is not None:
            print("Index already loaded", file=sys.stderr)
            return

        if not force_rebuild and self.faiss_file.exists() and self.metadata_file.exists():
            print("Loading existing index...", file=sys.stderr)
            self.load_index()
            return

        print("\nBuilding patent corpus index...", file=sys.stderr)

        # Check if TSV files are downloaded
        downloader = PatentCorpusDownloader()
        tsv_files = downloader.get_downloaded_files()

        if not tsv_files:
            print(
                "No patent corpus downloaded. Run 'patent-reviewer download-patents' first.",
                file=sys.stderr,
            )
            return

        print(f"Found {len(tsv_files)} downloaded TSV files", file=sys.stderr)

        # Parse all patents using TSV parser
        parser = PatentTSVParser()
        all_patents = parser.parse_main_file()  # Parse all patents from g_patent.tsv

        if not all_patents:
            print("No patents parsed from corpus", file=sys.stderr)
            return

        print(f"\nTotal patents parsed: {len(all_patents)}", file=sys.stderr)

        # Filter by year range if specified
        if start_year or end_year:
            print("\nFiltering patents by year range...", file=sys.stderr)
            original_count = len(all_patents)
            filtered_patents = []

            for patent in all_patents:
                # Extract year from grant_date (format: YYYY-MM-DD)
                if patent.grant_date:
                    try:
                        year = int(patent.grant_date[:4])

                        # Check year range
                        if start_year and year < start_year:
                            continue
                        if end_year and year > end_year:
                            continue

                        filtered_patents.append(patent)
                    except (ValueError, IndexError):
                        # Skip patents with invalid dates
                        continue
                else:
                    # Skip patents without grant dates
                    continue

            all_patents = filtered_patents
            year_range = f"{start_year or 'earliest'}-{end_year or 'latest'}"
            print(
                f"  Filtered: {original_count:,} → {len(all_patents):,} patents",
                file=sys.stderr,
            )
            print(f"  Year range: {year_range}", file=sys.stderr)

        if not all_patents:
            print("No patents remaining after filtering", file=sys.stderr)
            return

        # Chunk all patents
        print("\nChunking patents...", file=sys.stderr)
        all_chunks = []
        all_metadata = []

        for i, patent in enumerate(all_patents):
            chunks = self.chunk_patent(patent)
            for chunk_text, metadata in chunks:
                all_chunks.append(chunk_text)
                all_metadata.append(metadata)

            if (i + 1) % 1000 == 0:
                print(f"  Chunked {i + 1}/{len(all_patents)} patents...", file=sys.stderr)

        print(f"Total chunks: {len(all_chunks)}", file=sys.stderr)

        self.chunks = all_chunks
        self.metadata = all_metadata

        # Build FAISS index
        print("\n" + "=" * 60, file=sys.stderr)
        print("GENERATING EMBEDDINGS", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"Total chunks: {len(all_chunks):,}", file=sys.stderr)
        print(f"Device: {self.device.upper()}", file=sys.stderr)

        # Optimize batch size for GPU/CPU
        if self.device == "cuda":
            # Large batch for GPU (RTX 5090 has 24GB RAM)
            batch_size = 256
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU: {gpu_name} ({gpu_memory:.1f}GB)", file=sys.stderr)
            print(f"Batch size: {batch_size}", file=sys.stderr)
            total_batches = (len(all_chunks) + batch_size - 1) // batch_size
            print(f"Total batches: {total_batches:,}", file=sys.stderr)
            # Real-world timing: RTX 5090 processes ~1.4s/batch (measured with 17.6M chunks)
            estimated_seconds = total_batches * 1.4
            estimated_hours = estimated_seconds / 3600
            print(
                f"Estimated time: ~{estimated_seconds:.0f} seconds ({estimated_hours:.1f} hours) with GPU",
                file=sys.stderr,
            )
        else:
            # Smaller batch for CPU
            batch_size = 32
            print(f"Batch size: {batch_size} (CPU)", file=sys.stderr)
            total_batches = (len(all_chunks) + batch_size - 1) // batch_size
            print(f"Total batches: {total_batches:,}", file=sys.stderr)
            # CPU is roughly 10x slower than GPU based on real-world measurements
            estimated_seconds = total_batches * 14
            estimated_hours = estimated_seconds / 3600
            print(
                f"Estimated time: ~{estimated_seconds:.0f} seconds ({estimated_hours:.1f} hours) with CPU",
                file=sys.stderr,
            )

        print("\nProgress will appear below:", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        sys.stderr.flush()

        import time

        start_time = time.time()

        embeddings = self.model.encode(
            all_chunks,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            device=self.device,
        )

        elapsed = time.time() - start_time
        print("-" * 60, file=sys.stderr)
        print(
            f"✓ Generated {len(embeddings):,} embeddings in {elapsed:.1f} seconds",
            file=sys.stderr,
        )
        print(f"  Speed: {len(embeddings) / elapsed:.0f} embeddings/sec", file=sys.stderr)

        print("Building FAISS index...", file=sys.stderr)
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product (cosine similarity)

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)  # type: ignore[call-arg]

        print(f"FAISS index built with {self.index.ntotal} vectors", file=sys.stderr)

        # Build BM25 index
        if BM25Okapi:
            print("Building BM25 index...", file=sys.stderr)
            tokenized = [chunk.lower().split() for chunk in all_chunks]
            self.bm25 = BM25Okapi(tokenized)
            print("BM25 index built", file=sys.stderr)

        # Save index
        self.save_index()

        print("\n✓ Patent corpus index built successfully", file=sys.stderr)
        print(f"  Patents: {len(all_patents)}", file=sys.stderr)
        print(f"  Chunks: {len(all_chunks)}", file=sys.stderr)
        print(
            f"  Index size: {self.faiss_file.stat().st_size / 1024 / 1024:.1f} MB",
            file=sys.stderr,
        )

    def save_index(self):
        """Save index to disk"""
        print("Saving index...", file=sys.stderr)

        # Save FAISS index
        faiss.write_index(self.index, str(self.faiss_file))

        # Save metadata
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "chunks": self.chunks,
                    "metadata": self.metadata,
                },
                f,
            )

        # Save BM25 index
        if self.bm25:
            with open(self.bm25_file, "wb") as f:
                pickle.dump(self.bm25, f)

        print("Index saved", file=sys.stderr)

    def load_index(self):
        """Load index from disk"""
        print("Loading patent index...", file=sys.stderr)

        # Load FAISS index
        self.index = faiss.read_index(str(self.faiss_file))

        # Load metadata
        with open(self.metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.chunks = data["chunks"]
            self.metadata = data["metadata"]

        # Load BM25 index
        if BM25Okapi and self.bm25_file.exists():
            try:
                with open(self.bm25_file, "rb") as f:
                    self.bm25 = pickle.load(f)
                print("Hybrid search enabled", file=sys.stderr)
            except Exception as e:
                print(f"Failed to load BM25 index: {e}", file=sys.stderr)

        print(
            f"Loaded {len(self.chunks)} chunks from {len(set(m['patent_id'] for m in self.metadata))} patents",
            file=sys.stderr,
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        retrieve_k: Optional[int] = None,
        cpc_filter: Optional[str] = None,
        date_range: Optional[Tuple[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search for similar patents

        Args:
            query: Search query (description or claims text)
            top_k: Number of final results after reranking
            retrieve_k: Number of candidates before reranking (default: top_k * 4)
            cpc_filter: Filter by CPC code prefix (e.g., "G06F" for computing)
            date_range: Filter by date range (grant_date: "YYYYMMDD", "YYYYMMDD")

        Returns:
            List of relevant patent chunks with scores
        """
        if self.index is None:
            raise ValueError("Index not built. Run build_index() first.")

        if retrieve_k is None:
            retrieve_k = min(top_k * 4, 50)
        else:
            retrieve_k = min(retrieve_k, 100)

        # Apply HyDE if enabled
        search_query = query
        if self.use_hyde:
            expansions = self.hyde_generator.expand_query(query, num_expansions=2)
            if len(expansions) > 1:
                # Use the hypothetical document (not the original query)
                search_query = expansions[1]
                print("HyDE expanded query", file=sys.stderr)

        # Vector search
        query_embedding = self.model.encode([search_query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, retrieve_k * 2)  # type: ignore[call-arg]
        vector_scores = distances[0]
        vector_indices = indices[0]

        # BM25 keyword search
        bm25_scores = None
        if self.bm25:
            tokenized_query = search_query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)

        # Combine results with RRF (Reciprocal Rank Fusion)
        candidates = {}

        # Add vector results
        for rank, (idx, score) in enumerate(zip(vector_indices, vector_scores)):
            if idx < len(self.chunks):  # Valid index
                candidates[int(idx)] = {
                    "text": self.chunks[idx],
                    "metadata": self.metadata[idx],
                    "vector_score": float(score),
                    "vector_rank": rank + 1,
                }

        # Add BM25 results
        if bm25_scores is not None:
            bm25_ranked = np.argsort(bm25_scores)[::-1][: retrieve_k * 2]
            for rank, idx in enumerate(bm25_ranked):
                if idx in candidates:
                    candidates[idx]["bm25_score"] = float(bm25_scores[idx])
                    candidates[idx]["bm25_rank"] = rank + 1
                else:
                    candidates[int(idx)] = {
                        "text": self.chunks[idx],
                        "metadata": self.metadata[idx],
                        "bm25_score": float(bm25_scores[idx]),
                        "bm25_rank": rank + 1,
                    }

        # Apply filters
        if cpc_filter or date_range:
            filtered_candidates = {}
            for idx, cand in candidates.items():
                meta = cand["metadata"]

                # CPC filter
                if cpc_filter:
                    cpc_codes = meta.get("cpc_codes", [])
                    if not any(code.startswith(cpc_filter) for code in cpc_codes):
                        continue

                # Date range filter
                if date_range:
                    grant_date = meta.get("grant_date", "")
                    if grant_date:
                        grant_date_clean = grant_date.replace("-", "")
                        start_date, end_date = date_range
                        if not (start_date <= grant_date_clean <= end_date):
                            continue

                filtered_candidates[idx] = cand

            candidates = filtered_candidates

        # Compute RRF scores
        k_rrf = 60
        for cand in candidates.values():
            rrf_score = 0.0
            if "vector_rank" in cand:
                rrf_score += 1.0 / (k_rrf + cand["vector_rank"])
            if "bm25_rank" in cand:
                rrf_score += 1.0 / (k_rrf + cand["bm25_rank"])
            cand["rrf_score"] = rrf_score

        # Sort by RRF and take top candidates
        sorted_candidates = sorted(candidates.values(), key=lambda x: x["rrf_score"], reverse=True)[
            :retrieve_k
        ]

        # Cross-encoder reranking
        if len(sorted_candidates) > 0:
            pairs = [[query, cand["text"]] for cand in sorted_candidates]
            rerank_scores = self.reranker.predict(pairs)

            for cand, score in zip(sorted_candidates, rerank_scores):
                cand["rerank_score"] = float(score)

            # Final sort by rerank score
            sorted_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Return top_k results
        results = []
        for cand in sorted_candidates[:top_k]:
            results.append(
                {
                    "text": cand["text"],
                    "patent_id": cand["metadata"]["patent_id"],
                    "section": cand["metadata"]["section"],
                    "cpc_codes": cand["metadata"].get("cpc_codes", []),
                    "filing_date": cand["metadata"].get("filing_date"),
                    "grant_date": cand["metadata"].get("grant_date"),
                    "inventors": cand["metadata"].get("inventors", []),
                    "assignee": cand["metadata"].get("assignee"),
                    "score": cand.get("rerank_score", cand["rrf_score"]),
                }
            )

        return results

    def get_patent_chunks(self, patent_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific patent"""
        chunks = []
        for chunk, meta in zip(self.chunks, self.metadata):
            if meta["patent_id"] == patent_id:
                chunks.append(
                    {
                        "text": chunk,
                        "section": meta["section"],
                        "metadata": meta,
                    }
                )
        return chunks
