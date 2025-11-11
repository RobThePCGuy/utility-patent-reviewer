#!/usr/bin/env python3
"""
USPTO MPEP RAG MCP Server
Provides intelligent retrieval from the Manual of Patent Examining Procedure
"""

import json
import os

# CRITICAL: Disable user site-packages BEFORE importing third-party packages
# This prevents conflicts with global user installations
import site
import socket
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import health check system for startup validation
try:
    from .health_check import SystemHealthChecker
except ImportError:
    try:
        from health_check import SystemHealthChecker
    except ImportError:
        SystemHealthChecker = None

# Import automated patent analyzers
try:
    from .claims_analyzer import ClaimsAnalyzer
    from .formalities_checker import FormalitiesChecker
    from .specification_analyzer import SpecificationAnalyzer
except ImportError:
    try:
        from claims_analyzer import ClaimsAnalyzer
        from formalities_checker import FormalitiesChecker
        from specification_analyzer import SpecificationAnalyzer
    except ImportError:
        ClaimsAnalyzer = None
        FormalitiesChecker = None
        SpecificationAnalyzer = None

# Import consolidated downloaders
try:
    from .downloaders import FileDownloader
except ImportError:
    from downloaders import FileDownloader

# Import device utilities
try:
    from .utils.device import get_device
except ImportError:
    from utils.device import get_device

site.ENABLE_USER_SITE = False
# Remove user site-packages from sys.path if already added
user_site = site.getusersitepackages()
if user_site in sys.path:
    sys.path.remove(user_site)

# FastMCP for building MCP servers
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: mcp package not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# PDF processing
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF not found. Install with: pip install PyMuPDF", file=sys.stderr)
    sys.exit(1)

# Vector search capabilities
try:
    import faiss
    import numpy as np
    import torch
    from sentence_transformers import CrossEncoder, SentenceTransformer
except ImportError:
    print(
        "Error: Required packages not found. Install with: pip install sentence-transformers faiss-cpu numpy torch",
        file=sys.stderr,
    )
    sys.exit(1)

# BM25 for hybrid search
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print(
        "Warning: rank-bm25 not found. Hybrid search disabled. Install with: pip install rank-bm25",
        file=sys.stderr,
    )
    BM25Okapi = None


# Initialize MCP server
mcp = FastMCP("utility-patent-reviewer")

# Global variables for the RAG system
MPEP_DIR = Path(__file__).parent.parent / "pdfs"
INDEX_DIR = Path(__file__).parent / "index"

# Patent corpus support (lazy import to avoid circular dependencies)
patent_corpus_index = None

# Global MPEP index (initialized on first use)
mpep_index: Optional["MPEPIndex"] = None

# Ensure directories exist
MPEP_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# USPTO MPEP download URL (9th Edition, Revision 01.2024)
MPEP_DOWNLOAD_URL = "https://www.uspto.gov/web/offices/pac/mpep/e9r-01-2024.zip"

# USPTO Consolidated Patent Laws (35 USC) - July 2025 Update
USC_35_DOWNLOAD_URL = "https://www.uspto.gov/web/offices/pac/mpep/consolidated_laws.pdf"
USC_35_FILE = "consolidated_laws.pdf"

# USPTO Consolidated Patent Rules (37 CFR) - July 2025 Update
CFR_37_DOWNLOAD_URL = "https://www.uspto.gov/web/offices/pac/mpep/consolidated_rules.pdf"
CFR_37_FILE = "consolidated_rules.pdf"

# USPTO Subsequent Publications (After January 31, 2024) - July 2025 Update
SUBSEQUENT_PUBS_URL = "https://www.uspto.gov/web/offices/pac/mpep/subsequent-publications.pdf"
SUBSEQUENT_PUBS_FILE = "subsequent_publications.pdf"


def download_mpep_pdfs(url: str = MPEP_DOWNLOAD_URL, dest_dir: Path = MPEP_DIR) -> bool:
    """Download MPEP PDFs from USPTO website"""
    zip_path = dest_dir / "mpep-pdfs.zip"
    manual_instructions = (
        "1. Go to https://www.uspto.gov/web/offices/pac/mpep/index.html\n"
        "2. Download MPEP PDF files (mpep-0100.pdf through mpep-2900.pdf)\n"
        f"3. Place them in: {dest_dir.absolute()}"
    )
    return FileDownloader.download_with_progress(
        url=url,
        dest_path=zip_path,
        file_description="MPEP PDFs",
        timeout_seconds=300,
        use_mb=True,
        manual_instructions=manual_instructions,
    )


def extract_mpep_pdfs(dest_dir: Path = MPEP_DIR) -> bool:
    """Extract MPEP PDFs from downloaded zip file"""
    zip_path = dest_dir / "mpep-pdfs.zip"

    if not zip_path.exists():
        print(f"✗ Zip file not found: {zip_path}", file=sys.stderr)
        return False

    print(f"\nExtracting MPEP PDFs to {dest_dir.absolute()}", file=sys.stderr)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            pdf_files = [f for f in zip_ref.namelist() if f.endswith(".pdf")]
            total = len(pdf_files)

            for i, file in enumerate(pdf_files, 1):
                zip_ref.extract(file, dest_dir)
                print(f"\rExtracting: {i}/{total} files", end="", file=sys.stderr)

            print(f"\n✓ Extracted {total} PDF files", file=sys.stderr)

        print("✓ Cleaning up zip file", file=sys.stderr)
        zip_path.unlink()
        return True

    except Exception as e:
        print(f"\n✗ Extraction failed: {e}", file=sys.stderr)
        return False


def check_mpep_pdfs(dest_dir: Path = MPEP_DIR) -> int:
    """Check how many MPEP PDFs are available"""
    pdf_files = list(dest_dir.glob("mpep-*.pdf"))
    return len(pdf_files)


def download_35_usc(dest_dir: Path = MPEP_DIR) -> bool:
    """Download 35 USC Consolidated Patent Laws PDF from USPTO"""
    pdf_path = dest_dir / USC_35_FILE
    print("This contains Title 35 U.S.C. (Patent Laws) as of July 2025...", file=sys.stderr)
    return FileDownloader.download_with_progress(
        url=USC_35_DOWNLOAD_URL,
        dest_path=pdf_path,
        file_description="35 USC Consolidated Patent Laws",
        timeout_seconds=120,
        use_mb=False,
    )


def download_37_cfr(dest_dir: Path = MPEP_DIR) -> bool:
    """Download 37 CFR Consolidated Patent Rules PDF from USPTO"""
    pdf_path = dest_dir / CFR_37_FILE
    print("This contains Title 37 C.F.R. (Patent Rules) as of July 2025...", file=sys.stderr)
    return FileDownloader.download_with_progress(
        url=CFR_37_DOWNLOAD_URL,
        dest_path=pdf_path,
        file_description="37 CFR Consolidated Patent Rules",
        timeout_seconds=120,
        use_mb=False,
    )


def download_subsequent_publications(dest_dir: Path = MPEP_DIR) -> bool:
    """Download Subsequent Publications (updates after Jan 31, 2024) PDF from USPTO"""
    pdf_path = dest_dir / SUBSEQUENT_PUBS_FILE
    print("This contains policy updates after MPEP Revision 01.2024...", file=sys.stderr)
    return FileDownloader.download_with_progress(
        url=SUBSEQUENT_PUBS_URL,
        dest_path=pdf_path,
        file_description="Subsequent Publications",
        timeout_seconds=120,
        use_mb=False,
    )


def check_all_sources(dest_dir: Path = MPEP_DIR) -> Dict[str, bool]:
    """Check which source documents are available"""
    return {
        "mpep": check_mpep_pdfs(dest_dir) > 0,
        "35_usc": (dest_dir / USC_35_FILE).exists(),
        "37_cfr": (dest_dir / CFR_37_FILE).exists(),
        "subsequent_pubs": (dest_dir / SUBSEQUENT_PUBS_FILE).exists(),
    }


class MPEPIndex:
    """Manages indexing and retrieval of MPEP documents with advanced RAG techniques"""

    def __init__(self, use_hyde: bool = True):
        # Detect and use GPU if available
        self.device = get_device()

        print("Loading embedding model (BGE-base)...", file=sys.stderr)
        self.model = SentenceTransformer("BAAI/bge-base-en-v1.5", device=self.device)

        print("Loading reranker model...", file=sys.stderr)
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=self.device)

        # Initialize HyDE query expander
        self.use_hyde = use_hyde
        self.hyde_expander = None
        if use_hyde:
            try:
                from mcp_server.hyde import HyDEQueryExpander

                self.hyde_expander = HyDEQueryExpander(backend="auto")
            except Exception as e:
                print(
                    f"HyDE initialization failed: {e}. Continuing without HyDE.",
                    file=sys.stderr,
                )
                self.use_hyde = False

        self.chunks = []
        self.metadata = []
        self.index = None
        self.bm25 = None
        self.index_file = INDEX_DIR / "mpep_index.faiss"
        self.metadata_file = INDEX_DIR / "mpep_metadata.json"
        self.bm25_file = INDEX_DIR / "mpep_bm25.json"

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with contextual metadata"""
        chunks = []
        doc = None
        try:
            doc = fitz.open(pdf_path)
            section = self._extract_section_from_filename(pdf_path.name)

            for page_num, page in enumerate(doc):  # type: ignore[arg-type]
                text = page.get_text()
                if text.strip():
                    # Use common chunking helper
                    page_chunks = self._chunk_text_with_metadata(
                        text=text,
                        section_label=section,
                        base_metadata={
                            "source": "MPEP",
                            "file": pdf_path.name,
                            "page": page_num + 1,
                            "section": section,
                            "is_statute": False,
                            "is_regulation": False,
                            "is_update": False,
                        },
                    )
                    chunks.extend(page_chunks)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
        finally:
            if doc is not None:
                doc.close()
        return chunks

    def _extract_section_from_filename(self, filename: str) -> str:
        """Extract MPEP section number from filename"""
        # mpep-0100.pdf -> MPEP 100
        # mpep-2100.pdf -> MPEP 2100
        parts = filename.replace(".pdf", "").split("-")
        if len(parts) > 1:
            section = parts[1]
            if section.startswith("0") and len(section) == 4:
                section = section.lstrip("0") or "0"
            return f"MPEP {section}"
        return filename

    def _chunk_text_with_metadata(
        self,
        text: str,
        section_label: str,
        base_metadata: Dict[str, Any],
        chunk_size: int = 500,
        overlap: int = 100,
        min_chunk_length: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Common helper to chunk text and attach metadata with cross-reference detection.

        Args:
            text: Raw text to chunk
            section_label: Label to prepend (e.g., "MPEP 100", "35 U.S.C. §101")
            base_metadata: Base metadata dict to include in all chunks
            chunk_size: Characters per chunk
            overlap: Overlapping characters between chunks
            min_chunk_length: Minimum chunk length to keep

        Returns:
            List of chunk dictionaries with text and metadata
        """
        import re

        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i : i + chunk_size]
            if len(chunk_text.strip()) < min_chunk_length:
                continue

            # Prepend section context to chunk
            contextualized_text = f"[{section_label}] {chunk_text}"

            # Detect cross-references in chunk
            has_mpep_ref = bool(re.search(r"MPEP\s*§?\s*\d+", chunk_text))
            has_usc_ref = bool(re.search(r"35 U\.?S\.?C\.?\s*§?\s*\d+", chunk_text))
            has_cfr_ref = bool(re.search(r"37 C\.?F\.?R\.?\s*§?\s*\d+", chunk_text))

            # Merge base metadata with detected references
            chunk_metadata = {
                "text": contextualized_text,
                **base_metadata,
                "has_mpep_ref": has_mpep_ref,
                "has_usc_ref": has_usc_ref,
                "has_cfr_ref": has_cfr_ref,
                "has_statute": has_usc_ref,
                "has_rule_ref": has_cfr_ref,
            }

            chunks.append(chunk_metadata)

        return chunks

    def extract_text_from_usc(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from 35 USC PDF with statute section detection"""
        import re

        chunks = []
        doc = None
        try:
            doc = fitz.open(pdf_path)
            current_section = "35 U.S.C."

            for page_num, page in enumerate(doc):  # type: ignore[arg-type]
                text = page.get_text()
                if not text.strip():
                    continue

                # Detect section headers: "§ 100", "§ 101", etc.
                section_matches = list(re.finditer(r"§\s*(\d+)\.?\s+([^\n]{1,80})", text))

                # If we found sections on this page, process them
                if section_matches:
                    for match in section_matches:
                        section_num = match.group(1)
                        section_title = match.group(2).strip()
                        current_section = f"35 U.S.C. §{section_num} - {section_title}"

                # Chunk the text using common helper
                page_chunks = self._chunk_text_with_metadata(
                    text=text,
                    section_label=current_section,
                    base_metadata={
                        "source": "35_USC",
                        "file": pdf_path.name,
                        "section": current_section,
                        "page": page_num + 1,
                        "has_statute": True,  # Override: USC is always statute
                        "is_statute": True,
                        "is_regulation": False,
                        "is_update": False,
                    },
                )
                chunks.extend(page_chunks)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
        finally:
            if doc is not None:
                doc.close()
        return chunks

    def extract_text_from_cfr(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from 37 CFR PDF with rule section detection"""
        import re

        chunks = []
        doc = None
        try:
            doc = fitz.open(pdf_path)
            current_rule = "37 C.F.R."
            current_part = "Part 1"

            for page_num, page in enumerate(doc):  # type: ignore[arg-type]
                text = page.get_text()
                if not text.strip():
                    continue

                # Detect part headers: "PART 1", "PART 5", etc.
                part_match = re.search(r"PART\s+(\d+)", text)
                if part_match:
                    current_part = f"Part {part_match.group(1)}"

                # Detect rule sections: "§ 1.1", "§ 1.16", etc.
                rule_matches = list(re.finditer(r"§\s*(\d+\.\d+)\s+([^\n]{1,80})", text))

                if rule_matches:
                    for match in rule_matches:
                        rule_num = match.group(1)
                        rule_title = match.group(2).strip()
                        current_rule = f"37 C.F.R. §{rule_num} - {rule_title}"

                # Chunk the text using common helper
                page_chunks = self._chunk_text_with_metadata(
                    text=text,
                    section_label=current_rule,
                    base_metadata={
                        "source": "37_CFR",
                        "file": pdf_path.name,
                        "part": current_part,
                        "section": current_rule,
                        "page": page_num + 1,
                        "is_statute": False,
                        "is_regulation": True,
                        "is_fee_schedule": "fee" in text.lower() and "$" in text,
                        "is_update": False,
                    },
                )
                chunks.extend(page_chunks)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
        finally:
            if doc is not None:
                doc.close()
        return chunks

    def extract_text_from_subsequent_pubs(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text from Subsequent Publications PDF with update tracking"""
        import re

        chunks = []
        doc = None
        try:
            doc = fitz.open(pdf_path)
            current_doc_type = "Update"
            current_doc_title = "Subsequent Publication"
            fr_citation = None
            effective_date = None

            for page_num, page in enumerate(doc):  # type: ignore[arg-type]
                text = page.get_text()
                if not text.strip():
                    continue

                # Detect document type
                if re.search(r"Final\s+[Rr]ule", text):
                    current_doc_type = "Final Rule"
                elif re.search(r"Memorandum", text, re.IGNORECASE):
                    current_doc_type = "Memorandum"
                elif re.search(r"Official\s+Gazette", text, re.IGNORECASE):
                    current_doc_type = "OG Notice"

                # Extract Federal Register citation: "90 FR 3036"
                fr_match = re.search(r"(\d+)\s+FR\s+(\d+)", text)
                if fr_match:
                    fr_citation = f"{fr_match.group(1)} FR {fr_match.group(2)}"
                    current_doc_title = f"{current_doc_type} {fr_citation}"

                # Extract effective date
                date_match = re.search(r"effective\s+(\w+\s+\d+,\s+\d{4})", text, re.IGNORECASE)
                if date_match:
                    effective_date = date_match.group(1)

                # Detect affected MPEP sections
                mpep_sections_affected = list(set(re.findall(r"MPEP\s*§?\s*(\d+(?:\.\d+)?)", text)))

                # Chunk the text using common helper
                page_chunks = self._chunk_text_with_metadata(
                    text=text,
                    section_label=current_doc_title,
                    base_metadata={
                        "source": "SUBSEQUENT",
                        "file": pdf_path.name,
                        "section": current_doc_title,
                        "doc_type": current_doc_type,
                        "fr_citation": fr_citation,
                        "effective_date": effective_date,
                        "mpep_sections_affected": mpep_sections_affected,
                        "page": page_num + 1,
                        "is_statute": False,
                        "is_regulation": False,
                        "is_update": True,
                        "supersedes_mpep": True,
                    },
                )
                chunks.extend(page_chunks)
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
        finally:
            if doc is not None:
                doc.close()
        return chunks

    def _offer_pdf_cleanup(self):
        """Ask user if they want to delete PDF files after successful indexing"""

        # Find all PDFs in MPEP_DIR
        pdf_files = list(MPEP_DIR.glob("*.pdf"))

        if not pdf_files:
            return

        # Calculate total size
        total_size_mb = sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)

        print(f"\n{'='*60}", file=sys.stderr)
        print("PDF Cleanup Option", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(
            f"Found {len(pdf_files)} PDF files ({total_size_mb:.1f} MB)",
            file=sys.stderr,
        )
        print(f"Location: {MPEP_DIR}", file=sys.stderr)
        print("\nThe index has been successfully built from these PDFs.", file=sys.stderr)
        print("You can now delete the PDF files to save disk space.", file=sys.stderr)
        print("The index will continue to work without them.", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

        try:
            response = input("\nDelete PDF files? (y/n): ").lower().strip()

            if response == "y":
                deleted_count = 0
                for pdf_file in pdf_files:
                    try:
                        pdf_file.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"Failed to delete {pdf_file.name}: {e}", file=sys.stderr)

                print(
                    f"\n✓ Deleted {deleted_count} PDF files ({total_size_mb:.1f} MB freed)",
                    file=sys.stderr,
                )
            else:
                print(f"\nPDF files kept in {MPEP_DIR}", file=sys.stderr)
                print("You can manually delete them later if needed.", file=sys.stderr)
        except EOFError:
            # Non-interactive mode, skip cleanup
            print(
                "\nRunning in non-interactive mode, skipping PDF cleanup.",
                file=sys.stderr,
            )
            print(f"To manually delete PDFs later: rm {MPEP_DIR}/*.pdf", file=sys.stderr)

    def build_index(self, force_rebuild: bool = False):
        """Build or load the FAISS index with BM25"""
        if not force_rebuild and self.index_file.exists() and self.metadata_file.exists():
            # Load existing index
            self.index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.chunks = data["chunks"]
                self.metadata = data["metadata"]
            print(f"Loaded existing index with {len(self.chunks)} chunks", file=sys.stderr)

            # Load BM25 index from pickle if available
            if BM25Okapi and self.bm25_file.exists():
                try:
                    import pickle

                    print("Loading BM25 index from disk...", file=sys.stderr)
                    # Note: pickle is only used for locally-generated index files (trusted source)
                    with open(self.bm25_file, "rb") as f:
                        self.bm25 = pickle.load(f)  # nosec B301 - loading trusted local index
                    print("Hybrid search enabled", file=sys.stderr)
                except Exception as e:
                    print(
                        f"Failed to load BM25 index: {e}, rebuilding...",
                        file=sys.stderr,
                    )
                    tokenized = [chunk.lower().split() for chunk in self.chunks]
                    self.bm25 = BM25Okapi(tokenized)
            return

        # Build new index from all available sources
        print("Building new index from all patent law sources...", file=sys.stderr)
        all_chunks = []

        # 1. Process MPEP PDFs
        mpep_files = sorted(MPEP_DIR.glob("mpep-*.pdf"))
        if mpep_files:
            print(f"Processing {len(mpep_files)} MPEP PDFs...", file=sys.stderr)
            for pdf_file in mpep_files:
                print(f"  {pdf_file.name}...", file=sys.stderr)
                chunks = self.extract_text_from_pdf(pdf_file)
                all_chunks.extend(chunks)
            print(
                f"  ✓ Extracted {len([c for c in all_chunks if c.get('source') != '35_USC' and c.get('source') != '37_CFR' and c.get('source') != 'SUBSEQUENT'])} MPEP chunks",
                file=sys.stderr,
            )

        # 2. Process 35 USC (Patent Laws)
        usc_file = MPEP_DIR / USC_35_FILE
        if usc_file.exists():
            print("Processing 35 USC (Patent Laws)...", file=sys.stderr)
            usc_chunks = self.extract_text_from_usc(usc_file)
            all_chunks.extend(usc_chunks)
            print(f"  ✓ Extracted {len(usc_chunks)} statute chunks", file=sys.stderr)
        else:
            print("  ⚠ 35 USC not found (run --download-statutes to add)", file=sys.stderr)

        # 3. Process 37 CFR (Patent Rules)
        cfr_file = MPEP_DIR / CFR_37_FILE
        if cfr_file.exists():
            print("Processing 37 CFR (Patent Rules)...", file=sys.stderr)
            cfr_chunks = self.extract_text_from_cfr(cfr_file)
            all_chunks.extend(cfr_chunks)
            print(f"  ✓ Extracted {len(cfr_chunks)} regulation chunks", file=sys.stderr)
        else:
            print(
                "  ⚠ 37 CFR not found (run --download-regulations to add)",
                file=sys.stderr,
            )

        # 4. Process Subsequent Publications (Updates)
        sub_pubs_file = MPEP_DIR / SUBSEQUENT_PUBS_FILE
        if sub_pubs_file.exists():
            print(
                "Processing Subsequent Publications (post-Jan 2024 updates)...",
                file=sys.stderr,
            )
            update_chunks = self.extract_text_from_subsequent_pubs(sub_pubs_file)
            all_chunks.extend(update_chunks)
            print(f"  ✓ Extracted {len(update_chunks)} update chunks", file=sys.stderr)
        else:
            print(
                "  ⚠ Subsequent Publications not found (run --download-updates to add)",
                file=sys.stderr,
            )

        if not all_chunks:
            raise ValueError(
                "No chunks extracted from any sources. Run patent-reviewer setup to download sources."
            )

        # Create embeddings (no prefix for documents with BGE)
        print(
            f"Creating embeddings for {len(all_chunks)} chunks on {self.device}...",
            file=sys.stderr,
        )
        texts = [chunk["text"] for chunk in all_chunks]

        # Optimize batch size for GPU/CPU
        if self.device == "cuda":
            batch_size = 256  # Large batch for GPU
            print(f"Using GPU batch size: {batch_size}", file=sys.stderr)
        else:
            batch_size = 32  # Smaller batch for CPU
            print(f"Using CPU batch size: {batch_size}", file=sys.stderr)

        embeddings = self.model.encode(
            texts, batch_size=batch_size, show_progress_bar=True, device=self.device
        )
        print(f"✓ Generated {len(embeddings):,} embeddings", file=sys.stderr)

        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype("float32"))  # type: ignore[call-arg]

        self.chunks = texts
        # Preserve all metadata from all source types
        self.metadata = []
        for c in all_chunks:
            meta = {
                "source": c.get("source", "MPEP"),
                "file": c["file"],
                "page": c["page"],
                "section": c["section"],
                "has_statute": c.get("has_statute", False),
                "has_mpep_ref": c.get("has_mpep_ref", False),
                "has_rule_ref": c.get("has_rule_ref", False),
                "is_statute": c.get("is_statute", False),
                "is_regulation": c.get("is_regulation", False),
                "is_update": c.get("is_update", False),
            }
            # Add source-specific fields
            if c.get("source") == "37_CFR":
                meta["part"] = c.get("part")
                meta["is_fee_schedule"] = c.get("is_fee_schedule", False)
            elif c.get("source") == "SUBSEQUENT":
                meta["doc_type"] = c.get("doc_type")
                meta["fr_citation"] = c.get("fr_citation")
                meta["effective_date"] = c.get("effective_date")
                meta["mpep_sections_affected"] = c.get("mpep_sections_affected", [])
                meta["supersedes_mpep"] = c.get("supersedes_mpep", False)

            self.metadata.append(meta)

        # Build BM25 index for hybrid search
        if BM25Okapi:
            import pickle

            print("Building BM25 index for hybrid search...", file=sys.stderr)
            tokenized = [chunk.lower().split() for chunk in texts]
            self.bm25 = BM25Okapi(tokenized)
            # Persist BM25 index to disk
            with open(self.bm25_file, "wb") as f:
                pickle.dump(self.bm25, f)
            print("Hybrid search enabled", file=sys.stderr)

        # Save index
        faiss.write_index(self.index, str(self.index_file))
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump({"chunks": self.chunks, "metadata": self.metadata}, f)

        print(f"Index built and saved with {len(self.chunks)} chunks", file=sys.stderr)

        # Offer to clean up PDF files after successful indexing
        self._offer_pdf_cleanup()

    def search(
        self,
        query: str,
        top_k: int = 5,
        retrieve_k: Optional[int] = None,
        source_filter: Optional[str] = None,
        is_statute: Optional[bool] = None,
        is_regulation: Optional[bool] = None,
        is_update: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Advanced hybrid search with HyDE expansion and reranking

        Args:
            query: Search query
            top_k: Number of final results to return after reranking
            retrieve_k: Number of candidates to retrieve before reranking (default: top_k * 4, max 50)
            source_filter: Filter by source ("MPEP", "35_USC", "37_CFR", "SUBSEQUENT", or None for all)
            is_statute: Filter for statute content (True/False/None)
            is_regulation: Filter for regulation content (True/False/None)
            is_update: Filter for recent updates (True/False/None)
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        if retrieve_k is None:
            retrieve_k = min(top_k * 4, 50)
        else:
            retrieve_k = min(retrieve_k, 100)  # Cap at 100 for performance
        candidates = {}

        # HyDE Query Expansion (if enabled)
        queries_to_search = [query]
        if self.use_hyde and self.hyde_expander:
            try:
                expanded_queries = self.hyde_expander.expand_query(query, num_expansions=3)
                queries_to_search = expanded_queries
                print(
                    f"HyDE: Expanded to {len(queries_to_search)} queries",
                    file=sys.stderr,
                )
            except Exception as e:
                print(f"HyDE expansion failed: {e}, using original query", file=sys.stderr)

        # Search with each query variant (original + hypothetical docs)
        for query_idx, search_query in enumerate(queries_to_search):
            query_weight = 1.0 if query_idx == 0 else 0.5  # Weight original query higher

            # Vector search with BGE query prefix (recommended format)
            query_with_prefix = f"query: {search_query}"
            query_embedding = self.model.encode([query_with_prefix])
            vec_distances, vec_indices = self.index.search(
                query_embedding.astype("float32"), retrieve_k
            )

            # Add vector search results with RRF scoring
            for rank, (idx, dist) in enumerate(zip(vec_indices[0], vec_distances[0])):
                rrf_contribution = query_weight * (1.0 / (60 + rank + 1))

                if idx in candidates:
                    candidates[idx]["rrf_score"] += rrf_contribution
                    candidates[idx]["vector_score"] = max(
                        candidates[idx].get("vector_score", 0), float(1 / (1 + dist))
                    )
                else:
                    candidates[idx] = {
                        "text": self.chunks[idx],
                        "metadata": self.metadata[idx],
                        "vector_score": float(1 / (1 + dist)),
                        "rrf_score": rrf_contribution,
                    }

            # Hybrid search: add BM25 results if available
            if self.bm25:
                tokenized_query = search_query.lower().split()
                bm25_scores = self.bm25.get_scores(tokenized_query)
                bm25_top_indices = np.argsort(bm25_scores)[::-1][:retrieve_k]

                for rank, idx in enumerate(bm25_top_indices):
                    rrf_contribution = query_weight * (1.0 / (60 + rank + 1))

                    if idx in candidates:
                        candidates[idx]["rrf_score"] += rrf_contribution
                        candidates[idx]["bm25_score"] = max(
                            candidates[idx].get("bm25_score", 0),
                            float(bm25_scores[idx]),
                        )
                    else:
                        candidates[idx] = {
                            "text": self.chunks[idx],
                            "metadata": self.metadata[idx],
                            "bm25_score": float(bm25_scores[idx]),
                            "rrf_score": rrf_contribution,
                        }

        # Apply metadata filters if specified
        if (
            source_filter
            or is_statute is not None
            or is_regulation is not None
            or is_update is not None
        ):
            filtered_candidates = {}
            for idx, cand_data in candidates.items():
                meta = cand_data["metadata"]

                # Check source filter
                if source_filter and meta.get("source", "MPEP") != source_filter:
                    continue

                # Check statute filter
                if is_statute is not None and meta.get("is_statute", False) != is_statute:
                    continue

                # Check regulation filter
                if is_regulation is not None and meta.get("is_regulation", False) != is_regulation:
                    continue

                # Check update filter
                if is_update is not None and meta.get("is_update", False) != is_update:
                    continue

                filtered_candidates[idx] = cand_data

            candidates = filtered_candidates

        # Sort by RRF score and get top candidates for reranking
        sorted_candidates = sorted(
            candidates.items(), key=lambda x: x[1]["rrf_score"], reverse=True
        )[:retrieve_k]

        # Rerank with cross-encoder using ORIGINAL query only
        rerank_pairs = [[query, cand[1]["text"]] for cand in sorted_candidates]
        rerank_scores = self.reranker.predict(rerank_pairs)

        # Combine rerank scores with candidates
        final_results = []
        for (idx, cand), rerank_score in zip(sorted_candidates, rerank_scores):
            final_results.append(
                {
                    "text": cand["text"],
                    "metadata": cand["metadata"],
                    "relevance_score": float(rerank_score),
                    "hybrid_rrf_score": cand["rrf_score"],
                }
            )

        # Sort by reranker score and return top_k
        final_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return final_results[:top_k]


# ============================================================================
# MCP TOOL DEFINITIONS
# ============================================================================


@mcp.tool()
def search_mpep(
    query: str,
    top_k: int = 5,
    retrieve_k: Optional[int] = None,
    source_filter: Optional[str] = None,
    is_statute: Optional[bool] = None,
    is_regulation: Optional[bool] = None,
    is_update: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """Search USPTO MPEP manual for relevant information.

    Hybrid search (FAISS + BM25) with optional filters for source type (MPEP/35_USC/37_CFR/SUBSEQUENT),
    statutes, regulations, and updates. Returns ranked results with relevance scores and citation metadata.
    """
    top_k = min(top_k, 20)  # Cap at 20 results
    results = mpep_index.search(
        query,
        top_k,
        retrieve_k=retrieve_k,
        source_filter=source_filter,
        is_statute=is_statute,
        is_regulation=is_regulation,
        is_update=is_update,
    )

    # Format results with citation metadata and source type
    formatted_results = []
    for i, r in enumerate(results):
        result = {
            "rank": i + 1,
            "source": r["metadata"].get("source", "MPEP"),
            "section": r["metadata"]["section"],
            "file": r["metadata"]["file"],
            "page": r["metadata"]["page"],
            "has_statute": r["metadata"].get("has_statute", False),
            "has_mpep_ref": r["metadata"].get("has_mpep_ref", False),
            "has_rule_ref": r["metadata"].get("has_rule_ref", False),
            "is_statute": r["metadata"].get("is_statute", False),
            "is_regulation": r["metadata"].get("is_regulation", False),
            "is_update": r["metadata"].get("is_update", False),
            "relevance_score": round(r["relevance_score"], 3),
            "text": r["text"],
        }

        # Add source-specific fields if present
        if r["metadata"].get("source") == "SUBSEQUENT":
            result["doc_type"] = r["metadata"].get("doc_type")
            result["fr_citation"] = r["metadata"].get("fr_citation")
            result["effective_date"] = r["metadata"].get("effective_date")

        formatted_results.append(result)

    return formatted_results


@mcp.tool()
def get_mpep_section(section_number: str, max_chunks: int = 50) -> Dict[str, Any]:
    """Get all text chunks from a specific MPEP section number (e.g., "2100", "700", "608")."""
    # Find all chunks from the specified section
    section_pattern = f"MPEP {section_number}"
    matching_chunks = [
        {"text": chunk, "metadata": meta}
        for chunk, meta in zip(mpep_index.chunks, mpep_index.metadata)
        if section_pattern in meta["section"]
    ]

    if not matching_chunks:
        return {"error": f"No content found for MPEP section {section_number}"}

    # Return requested number of chunks
    return {
        "section": section_number,
        "total_chunks": len(matching_chunks),
        "chunks": matching_chunks[:max_chunks],
    }


@mcp.tool()
def review_patent_claims(claims_text: str) -> Dict[str, Any]:
    """Analyze patent claims for 35 USC 112(b) compliance: antecedent basis, definiteness, subjective terms, cross-references, and structure."""

    # Run automated analysis
    if ClaimsAnalyzer:
        analyzer = ClaimsAnalyzer()
        analysis_results = analyzer.analyze_claims(claims_text)

        # Also get relevant MPEP guidance for context
        mpep_results = mpep_index.search(
            "claim definiteness antecedent basis 35 USC 112(b)", top_k=5
        )

        mpep_refs = []
        for r in mpep_results:
            mpep_refs.append(
                {
                    "section": r["metadata"]["section"],
                    "page": r["metadata"]["page"],
                    "text": r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"],
                }
            )

        return {
            "analysis_type": "automated",
            "claim_count": analysis_results["claim_count"],
            "independent_claims": analysis_results["independent_count"],
            "dependent_claims": analysis_results["dependent_count"],
            "compliance_score": analysis_results["compliance_score"],
            "total_issues": analysis_results["total_issues"],
            "critical_issues": analysis_results["critical_issues"],
            "important_issues": analysis_results["important_issues"],
            "minor_issues": analysis_results["minor_issues"],
            "issues_by_type": analysis_results["issues_by_type"],
            "summary": analysis_results["summary"],
            "issues": analysis_results["issues"],
            "mpep_references": mpep_refs,
        }

    # Fallback to MPEP search if analyzer not available
    else:
        print("WARNING: ClaimsAnalyzer not available, falling back to MPEP search", file=sys.stderr)
        results = mpep_index.search(claims_text, top_k=10)

        formatted = []
        for r in results:
            formatted.append(
                {
                    "section": r["metadata"]["section"],
                    "page": r["metadata"]["page"],
                    "text": r["text"],
                }
            )

        return {
            "analysis_type": "mpep_search_only",
            "warning": "Automated analysis unavailable - showing MPEP references only",
            "relevant_sections": formatted,
        }


@mcp.tool()
def review_specification(claims_text: str, specification: str) -> Dict[str, Any]:
    """Analyze specification support for claims per 35 USC 112(a): written description, enablement, and best mode."""

    # Run automated analysis
    if ClaimsAnalyzer and SpecificationAnalyzer:
        # Parse claims first
        claims_analyzer = ClaimsAnalyzer()
        parsed_claims = claims_analyzer._parse_claims(claims_text)

        # Analyze specification support
        spec_analyzer = SpecificationAnalyzer()
        analysis_results = spec_analyzer.analyze_specification_support(parsed_claims, specification)

        # Get relevant MPEP guidance
        mpep_results = mpep_index.search("written description enablement 35 USC 112(a)", top_k=5)

        mpep_refs = []
        for r in mpep_results:
            mpep_refs.append(
                {
                    "section": r["metadata"]["section"],
                    "page": r["metadata"]["page"],
                    "text": r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"],
                }
            )

        return {
            "analysis_type": "automated",
            "specification_paragraphs": analysis_results["specification_paragraphs"],
            "indexed_terms": analysis_results["indexed_terms"],
            "total_issues": analysis_results["total_issues"],
            "critical_issues": analysis_results["critical_issues"],
            "important_issues": analysis_results["important_issues"],
            "written_description_issues": analysis_results["written_description_issues"],
            "enablement_issues": analysis_results["enablement_issues"],
            "spec_coverage": analysis_results["spec_coverage"],
            "summary": analysis_results["summary"],
            "compliant": analysis_results["compliant"],
            "issues": analysis_results["issues"],
            "mpep_references": mpep_refs,
        }

    # Fallback to MPEP search if analyzers not available
    else:
        print(
            "WARNING: Specification analyzer not available, falling back to MPEP search",
            file=sys.stderr,
        )
        results = mpep_index.search(
            "specification written description enablement 35 USC 112", top_k=10
        )

        formatted = []
        for r in results:
            formatted.append(
                {
                    "section": r["metadata"]["section"],
                    "page": r["metadata"]["page"],
                    "text": r["text"],
                }
            )

        return {
            "analysis_type": "mpep_search_only",
            "warning": "Automated analysis unavailable - showing MPEP references only",
            "guidance": formatted,
        }


@mcp.tool()
def check_formalities(
    abstract: Optional[str] = None,
    title: Optional[str] = None,
    specification: Optional[str] = None,
    drawings_present: bool = False,
) -> Dict[str, Any]:
    """Check patent application formalities per MPEP 608: abstract (50-150 words), title (≤500 chars), required sections, and drawing references."""

    # Run automated analysis
    if FormalitiesChecker:
        checker = FormalitiesChecker()
        analysis_results = checker.check_all_formalities(
            abstract=abstract,
            title=title,
            specification=specification,
            drawings_present=drawings_present,
        )

        # Get relevant MPEP guidance
        mpep_results = mpep_index.search("formalities abstract title drawings MPEP 608", top_k=5)

        mpep_refs = []
        for r in mpep_results:
            mpep_refs.append(
                {
                    "section": r["metadata"]["section"],
                    "page": r["metadata"]["page"],
                    "text": r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"],
                }
            )

        return {
            "analysis_type": "automated",
            "overall_compliant": analysis_results["overall_compliant"],
            "ready_to_file": analysis_results["compliance_summary"]["ready_to_file"],
            "summary": analysis_results["compliance_summary"]["summary"],
            "critical_issues": analysis_results["compliance_summary"]["critical_issues"],
            "warnings": analysis_results["compliance_summary"]["warnings"],
            "info": analysis_results["compliance_summary"]["info"],
            "abstract": analysis_results["results"]["abstract"],
            "title": analysis_results["results"]["title"],
            "drawings": analysis_results["results"]["drawings"],
            "sections": analysis_results["results"]["sections"],
            "issues": analysis_results["issues"],
            "mpep_references": mpep_refs,
        }

    # Fallback to MPEP search if checker not available
    else:
        print(
            "WARNING: FormalitiesChecker not available, falling back to MPEP search",
            file=sys.stderr,
        )
        results = mpep_index.search(
            "formalities abstract title drawings requirements MPEP 608", top_k=10
        )

        formatted = []
        for r in results:
            formatted.append(
                {
                    "section": r["metadata"]["section"],
                    "page": r["metadata"]["page"],
                    "text": r["text"],
                }
            )

        return {
            "analysis_type": "mpep_search_only",
            "warning": "Automated analysis unavailable - showing MPEP references only",
            "requirements": formatted,
        }


# USPTO API Tools

uspto_client = None


def _ensure_uspto_client():
    """Lazy load USPTO API client"""
    global uspto_client
    if uspto_client is None:
        from mcp_server.uspto_api import USPTOClient

        uspto_client = USPTOClient()
    return uspto_client


@mcp.tool()
def search_uspto_api(
    query: str,
    limit: int = 25,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    application_type: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search USPTO Open Data Portal API (live database). Requires USPTO_API_KEY environment variable. Supports year range and application type filters."""
    try:
        client = _ensure_uspto_client()

        # Check if API key is available
        if not client.api_key:
            return [
                {
                    "error": "No USPTO API key found. Set USPTO_API_KEY environment variable.",
                    "info": "Get your API key at: https://data.uspto.gov/myodp",
                }
            ]

        # Perform search
        results = client.search_patents_simple(
            query=query,
            limit=min(limit, 100),
            start_year=start_year,
            end_year=end_year,
            application_type=application_type,
            status=status,
        )

        # Format results
        from mcp_server.uspto_api import format_patent_result

        formatted_results = []
        for i, patent in enumerate(results, 1):
            formatted_results.append(
                {
                    "rank": i,
                    "patent_number": patent.patent_number,
                    "application_number": patent.application_number,
                    "title": patent.title,
                    "filing_date": patent.filing_date,
                    "grant_date": patent.grant_date,
                    "type": patent.application_type,
                    "status": patent.status,
                    "inventors": patent.inventors,
                    "applicants": patent.applicants,
                    "formatted": format_patent_result(patent, verbose=False),
                }
            )

        return formatted_results

    except Exception as e:
        return [{"error": f"USPTO API search failed: {str(e)}"}]


@mcp.tool()
def get_uspto_patent(patent_number: str) -> Dict[str, Any]:
    """Get detailed patent information from USPTO API by patent number (e.g., "11234567" or "US11234567")."""
    try:
        client = _ensure_uspto_client()

        if not client.api_key:
            return {
                "error": "No USPTO API key found. Set USPTO_API_KEY environment variable.",
                "info": "Get your API key at: https://data.uspto.gov/myodp",
            }

        # Clean patent number
        clean_number = patent_number.replace("US", "").replace("us", "").replace(",", "")

        # Get patent
        patent = client.get_patent_by_number(clean_number)

        if not patent:
            return {"error": f"Patent {patent_number} not found in USPTO database"}

        from mcp_server.uspto_api import format_patent_result

        return {
            "patent_number": patent.patent_number,
            "application_number": patent.application_number,
            "title": patent.title,
            "filing_date": patent.filing_date,
            "grant_date": patent.grant_date,
            "type": patent.application_type,
            "status": patent.status,
            "inventors": patent.inventors,
            "applicants": patent.applicants,
            "formatted": format_patent_result(patent, verbose=True),
            "raw_metadata": patent.raw_data.get("applicationMetaData", {}),
        }

    except Exception as e:
        return {"error": f"Failed to retrieve patent: {str(e)}"}


@mcp.tool()
def get_recent_uspto_patents(
    days: int = 7, application_type: str = "Utility", limit: int = 100
) -> List[Dict[str, Any]]:
    """Get recently granted patents from USPTO API. Default: last 7 days of utility patents."""
    try:
        client = _ensure_uspto_client()

        if not client.api_key:
            return [
                {
                    "error": "No USPTO API key found. Set USPTO_API_KEY environment variable.",
                    "info": "Get your API key at: https://data.uspto.gov/myodp",
                }
            ]

        # Get recent patents
        results = client.get_recent_patents(
            days=days, application_type=application_type, limit=limit
        )

        # Format results
        from mcp_server.uspto_api import format_patent_result

        formatted_results = []
        for i, patent in enumerate(results, 1):
            formatted_results.append(
                {
                    "rank": i,
                    "patent_number": patent.patent_number,
                    "title": patent.title,
                    "grant_date": patent.grant_date,
                    "filing_date": patent.filing_date,
                    "inventors": patent.inventors,
                    "formatted": format_patent_result(patent),
                }
            )

        return formatted_results

    except Exception as e:
        return [{"error": f"Failed to retrieve recent patents: {str(e)}"}]


@mcp.tool()
def check_uspto_api_status() -> Dict[str, Any]:
    """Check USPTO API accessibility and API key validity."""
    try:
        client = _ensure_uspto_client()

        if not client.api_key:
            return {
                "ready": False,
                "api_key_configured": False,
                "message": "No USPTO API key found. Set USPTO_API_KEY environment variable.",
                "setup_url": "https://data.uspto.gov/myodp",
            }

        # Test API connection
        is_working = client.check_api_status()

        return {
            "ready": is_working,
            "api_key_configured": True,
            "api_url": client.BASE_URL,
            "message": ("USPTO API is ready" if is_working else "USPTO API connection failed"),
        }

    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "message": "Failed to check USPTO API status",
        }


# Patent Prior Art Search Tools


def _ensure_patent_index():
    """Lazy load patent corpus index"""
    global patent_corpus_index
    if patent_corpus_index is None:
        try:
            from mcp_server.patent_corpus import PATENT_INDEX_DIR
            from mcp_server.patent_index import PatentCorpusIndex

            # Check if index exists
            if not (PATENT_INDEX_DIR / "patent_index.faiss").exists():
                raise ValueError(
                    "Patent corpus index not built. "
                    "Run 'patent-reviewer download-patents --build-index' first."
                )

            patent_corpus_index = PatentCorpusIndex(use_hyde=True)
            patent_corpus_index.build_index(force_rebuild=False)
        except ImportError as e:
            raise ValueError(f"Patent corpus module not available: {e}")

    return patent_corpus_index


@mcp.tool()
def search_prior_art(
    description: str,
    top_k: int = 10,
    retrieve_k: Optional[int] = None,
    cpc_filter: Optional[str] = None,
    years_back: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Search local patent corpus for prior art. Supports CPC code filters (e.g., "G06F") and year range limits."""
    try:
        index = _ensure_patent_index()
    except ValueError as e:
        return [{"error": str(e)}]

    # Cap top_k
    top_k = min(top_k, 20)

    # Calculate date range if years_back specified
    date_range = None
    if years_back:
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=years_back * 365)
        date_range = (start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))

    # Search
    results = index.search(
        query=description,
        top_k=top_k,
        retrieve_k=retrieve_k,
        cpc_filter=cpc_filter,
        date_range=date_range,
    )

    return results


@mcp.tool()
def get_patent_details(patent_id: str) -> Dict[str, Any]:
    """Get complete patent information with all text chunks by patent number (e.g., "10123456" or "US10123456")."""
    try:
        index = _ensure_patent_index()
    except ValueError as e:
        return {"error": str(e)}

    # Clean patent ID (remove "US" prefix if present)
    clean_id = patent_id.replace("US", "").replace("us", "")

    # Get all chunks for this patent
    chunks = index.get_patent_chunks(clean_id)

    if not chunks:
        return {"error": f"Patent {patent_id} not found in corpus"}

    # Organize by section
    sections = {}
    metadata = chunks[0]["metadata"] if chunks else {}

    for chunk in chunks:
        section = chunk["section"]
        if section not in sections:
            sections[section] = []
        sections[section].append(chunk["text"])

    return {
        "patent_id": clean_id,
        "cpc_codes": metadata.get("cpc_codes", []),
        "filing_date": metadata.get("filing_date"),
        "grant_date": metadata.get("grant_date"),
        "inventors": metadata.get("inventors", []),
        "assignee": metadata.get("assignee"),
        "sections": sections,
        "total_chunks": len(chunks),
    }


@mcp.tool()
def check_patent_corpus_status() -> Dict[str, Any]:
    """Check status of patent corpus download and search index."""
    try:
        from mcp_server.patent_corpus import check_patent_corpus_status as check_status

        return check_status()
    except ImportError:
        return {"error": "Patent corpus module not available"}


# Patent Diagram Generation Tools


@mcp.tool()
def render_diagram(
    dot_code: str,
    filename: str = "diagram",
    output_format: str = "svg",
    engine: str = "dot",
) -> Dict[str, Any]:
    """
    Render a technical diagram from Graphviz DOT code.

    Use this tool to convert DOT language code into patent-style technical drawings.
    Claude should generate the DOT code based on user's description, then call this tool to render it.

    Args:
        dot_code: Complete Graphviz DOT language code for the diagram
        filename: Output filename (without extension, default: "diagram")
        output_format: Output format - "svg" (default), "png", or "pdf"
        engine: Graphviz layout engine - "dot" (hierarchical), "neato" (spring),
                "fdp" (force-directed), "circo" (circular), "twopi" (radial)

    Returns:
        Dict with "path" (file path), "format", "success", and optional "error"

    Example DOT code:
        digraph Example {
            A [label="Start"];
            B [label="Process"];
            C [label="End"];
            A -> B -> C;
        }
    """
    try:
        from mcp_server.diagram_generator import (
            PatentDiagramGenerator,
            check_graphviz_installed,
        )

        # Check if Graphviz is available
        status = check_graphviz_installed()
        if not status["ready"]:
            return {
                "success": False,
                "error": "Graphviz not installed. Install with: sudo apt install graphviz && pip install graphviz",
                "status": status,
            }

        generator = PatentDiagramGenerator()
        output_path = generator.render_dot_diagram(
            dot_code=dot_code,
            filename=filename,
            output_format=output_format,
            engine=engine,
        )

        return {
            "success": True,
            "path": str(output_path.absolute()),
            "format": output_format,
            "message": f"Diagram rendered successfully to {output_path.name}",
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to render diagram: {str(e)}"}


@mcp.tool()
def create_flowchart(
    steps: List[Dict[str, Any]], filename: str = "flowchart", output_format: str = "svg"
) -> Dict[str, Any]:
    """
    Create a patent-style flowchart from a list of steps.

    Args:
        steps: List of step dictionaries with keys:
            - "id": Unique identifier (e.g., "start", "step1")
            - "label": Display label (e.g., "Initialize System")
            - "shape": Node shape - "box" (default), "ellipse" (start/end), "diamond" (decision)
            - "next": List of next step IDs (e.g., ["step2", "step3"])
        filename: Output filename (default: "flowchart")
        output_format: Output format - "svg" (default), "png", or "pdf"

    Returns:
        Dict with "path", "format", "success", and optional "error"

    Example steps:
        [
            {"id": "start", "label": "Start", "shape": "ellipse", "next": ["step1"]},
            {"id": "step1", "label": "Process Data", "shape": "box", "next": ["decision"]},
            {"id": "decision", "label": "Valid?", "shape": "diamond", "next": ["step2", "end"]},
            {"id": "step2", "label": "Save Result", "shape": "box", "next": ["end"]},
            {"id": "end", "label": "End", "shape": "ellipse", "next": []}
        ]
    """
    try:
        from mcp_server.diagram_generator import (
            PatentDiagramGenerator,
            check_graphviz_installed,
        )

        status = check_graphviz_installed()
        if not status["ready"]:
            return {
                "success": False,
                "error": "Graphviz not installed. Install with: sudo apt install graphviz && pip install graphviz",
            }

        generator = PatentDiagramGenerator()
        output_path = generator.create_flowchart(
            steps=steps, filename=filename, output_format=output_format
        )

        return {
            "success": True,
            "path": str(output_path.absolute()),
            "format": output_format,
            "num_steps": len(steps),
            "message": f"Flowchart with {len(steps)} steps rendered to {output_path.name}",
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to create flowchart: {str(e)}"}


@mcp.tool()
def create_block_diagram(
    blocks: List[Dict[str, Any]],
    connections: List[List[str]],
    filename: str = "block_diagram",
    output_format: str = "svg",
) -> Dict[str, Any]:
    """
    Create a patent-style block diagram showing system components and connections.

    Args:
        blocks: List of block dictionaries with keys:
            - "id": Unique identifier (e.g., "input", "processor")
            - "label": Display label (use \\n for line breaks, e.g., "Input\\nSensor")
            - "type": Block type - "input", "output", "process", "storage", "decision", or "default"
        connections: List of connection lists, each with 2-3 elements:
            - [from_id, to_id] or [from_id, to_id, label]
        filename: Output filename (default: "block_diagram")
        output_format: Output format - "svg" (default), "png", or "pdf"

    Returns:
        Dict with "path", "format", "success", and optional "error"

    Example:
        blocks = [
            {"id": "sensor", "label": "Input\\nSensor", "type": "input"},
            {"id": "cpu", "label": "Central\\nProcessor", "type": "process"},
            {"id": "display", "label": "Output\\nDisplay", "type": "output"}
        ]
        connections = [
            ["sensor", "cpu", "raw data"],
            ["cpu", "display", "processed data"]
        ]
    """
    try:
        from mcp_server.diagram_generator import (
            PatentDiagramGenerator,
            check_graphviz_installed,
        )

        status = check_graphviz_installed()
        if not status["ready"]:
            return {
                "success": False,
                "error": "Graphviz not installed. Install with: sudo apt install graphviz && pip install graphviz",
            }

        # Convert connections to tuples with proper typing
        from typing import Tuple

        connections_tuples: List[Tuple[str, str, Optional[str]]] = [
            (conn[0], conn[1], conn[2] if len(conn) > 2 else None) for conn in connections
        ]

        generator = PatentDiagramGenerator()
        output_path = generator.create_block_diagram(
            blocks=blocks,
            connections=connections_tuples,
            filename=filename,
            output_format=output_format,
        )

        return {
            "success": True,
            "path": str(output_path.absolute()),
            "format": output_format,
            "num_blocks": len(blocks),
            "num_connections": len(connections),
            "message": f"Block diagram with {len(blocks)} blocks rendered to {output_path.name}",
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to create block diagram: {str(e)}"}


@mcp.tool()
def add_diagram_references(svg_path: str, reference_map: Dict[str, int]) -> Dict[str, Any]:
    """
    Add patent-style reference numbers to an existing SVG diagram.

    Args:
        svg_path: Path to input SVG file (from render_diagram or create_* tools)
        reference_map: Dictionary mapping element text/label to reference number
            Example: {"Input Sensor": 10, "Processor": 20, "Display": 30}

    Returns:
        Dict with "path" to annotated SVG, "success", and optional "error"

    Note: Reference numbers are added in parentheses after matching text (e.g., "Processor (20)")
    """
    try:
        from pathlib import Path

        from mcp_server.diagram_generator import PatentDiagramGenerator

        generator = PatentDiagramGenerator()
        input_path = Path(svg_path)

        if not input_path.exists():
            return {"success": False, "error": f"SVG file not found: {svg_path}"}

        output_path = generator.add_reference_numbers(
            svg_path=input_path, reference_map=reference_map
        )

        return {
            "success": True,
            "path": str(output_path.absolute()),
            "num_references": len(reference_map),
            "message": f"Added {len(reference_map)} reference numbers to {output_path.name}",
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to add references: {str(e)}"}


@mcp.tool()
def get_diagram_templates() -> Dict[str, Any]:
    """
    Get common patent diagram templates in DOT language.

    Returns:
        Dictionary mapping template names to DOT code. Templates include:
        - "simple_flowchart": Basic process flow with start/end
        - "system_block": System architecture with components
        - "method_steps": Sequential method steps with numbering
        - "component_hierarchy": Hierarchical component structure

    Use these as starting points and modify the DOT code as needed.
    """
    try:
        from mcp_server.diagram_generator import PatentDiagramGenerator

        generator = PatentDiagramGenerator()
        templates = generator.get_templates()

        return {
            "success": True,
            "templates": templates,
            "available": list(templates.keys()),
            "message": f"Retrieved {len(templates)} diagram templates",
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to get templates: {str(e)}"}


@mcp.tool()
def check_diagram_tools_status() -> Dict[str, Any]:
    """
    Check if diagram generation tools are installed and ready.

    Returns:
        Status information about Graphviz installation and readiness
    """
    try:
        from mcp_server.diagram_generator import check_graphviz_installed

        status = check_graphviz_installed()

        if status["ready"]:
            message = f"Diagram tools ready. Graphviz version {status['version']}"
        elif status["python_package"] and not status["system_command"]:
            message = "Python package installed but system Graphviz missing. Install with: sudo apt install graphviz"
        elif not status["python_package"]:
            message = "Python graphviz package missing. Install with: pip install graphviz"
        else:
            message = "Diagram tools not ready"

        return {**status, "message": message}

    except Exception as e:
        return {"ready": False, "error": f"Failed to check status: {str(e)}"}


@mcp.resource("mpep://index/stats")
def get_index_stats() -> str:
    """Get statistics about the MPEP index"""
    stats = {
        "total_chunks": len(mpep_index.chunks),
        "total_metadata": len(mpep_index.metadata),
        "index_exists": mpep_index.index is not None,
        "sections": len(set(m["section"] for m in mpep_index.metadata)),
    }
    return json.dumps(stats, indent=2)


def _parse_args():
    """Parse command line arguments"""
    import argparse

    parser = argparse.ArgumentParser(description="USPTO MPEP RAG MCP Server")
    parser.add_argument("--rebuild-index", action="store_true", help="Force rebuild of the index")
    parser.add_argument(
        "--download-mpep", action="store_true", help="Download MPEP PDFs from USPTO"
    )
    parser.add_argument(
        "--download-all",
        action="store_true",
        help="Download all sources (MPEP, 35 USC, 37 CFR, Subsequent Publications)",
    )
    parser.add_argument(
        "--download-statutes",
        action="store_true",
        help="Download 35 USC Consolidated Patent Laws",
    )
    parser.add_argument(
        "--download-regulations",
        action="store_true",
        help="Download 37 CFR Consolidated Patent Rules",
    )
    parser.add_argument(
        "--download-updates",
        action="store_true",
        help="Download Subsequent Publications (post-Jan 2024 updates)",
    )
    parser.add_argument(
        "--mpep-url",
        type=str,
        default=MPEP_DOWNLOAD_URL,
        help="Custom MPEP download URL",
    )
    parser.add_argument("--no-hyde", action="store_true", help="Disable HyDE query expansion")
    return parser.parse_args()


def _handle_mpep_download(mpep_url):
    """Handle MPEP PDF download"""
    pdf_count = check_mpep_pdfs()
    if pdf_count > 0:
        response = input(f"\n{pdf_count} MPEP PDFs already exist. Download anyway? (y/N): ")
        if response.lower() != "y":
            print("Skipping download", file=sys.stderr)
        else:
            if download_mpep_pdfs(mpep_url):
                extract_mpep_pdfs()
    else:
        if download_mpep_pdfs(mpep_url):
            extract_mpep_pdfs()

    pdf_count = check_mpep_pdfs()
    print(f"\n✓ Found {pdf_count} MPEP PDF files", file=sys.stderr)

    if pdf_count == 0:
        print("\n✗ No MPEP PDFs found. Cannot build index.", file=sys.stderr)
        sys.exit(1)

    print(
        "\nReady to build index. Run with --rebuild-index to continue.",
        file=sys.stderr,
    )
    sys.exit(0)


def _handle_additional_downloads(args):
    """Handle downloads for 35 USC, 37 CFR, and Subsequent Publications"""
    sources_status = check_all_sources()
    downloads_performed = []

    # Download 35 USC
    if args.download_all or args.download_statutes:
        if sources_status["35_usc"]:
            print(
                f"\n35 USC already exists at {MPEP_DIR / USC_35_FILE}",
                file=sys.stderr,
            )
        if download_35_usc():
            downloads_performed.append("35 USC")

    # Download 37 CFR
    if args.download_all or args.download_regulations:
        if sources_status["37_cfr"]:
            print(
                f"\n37 CFR already exists at {MPEP_DIR / CFR_37_FILE}",
                file=sys.stderr,
            )
        if download_37_cfr():
            downloads_performed.append("37 CFR")

    # Download Subsequent Publications
    if args.download_all or args.download_updates:
        if sources_status["subsequent_pubs"]:
            print(
                f"\nSubsequent Publications already exists at {MPEP_DIR / SUBSEQUENT_PUBS_FILE}",
                file=sys.stderr,
            )
        if download_subsequent_publications():
            downloads_performed.append("Subsequent Publications")

    # Summary
    if downloads_performed:
        print(
            f"\n✓ Successfully downloaded: {', '.join(downloads_performed)}",
            file=sys.stderr,
        )
        print(
            "\nNote: These sources are not yet indexed. Run with --rebuild-index to include them.",
            file=sys.stderr,
        )
    else:
        print("\n✓ All requested sources already present", file=sys.stderr)

    # Show current status
    sources_status = check_all_sources()
    print("\nCurrent source status:", file=sys.stderr)
    print(f"  MPEP PDFs: {'✓' if sources_status['mpep'] else '✗'}", file=sys.stderr)
    print(f"  35 USC:    {'✓' if sources_status['35_usc'] else '✗'}", file=sys.stderr)
    print(f"  37 CFR:    {'✓' if sources_status['37_cfr'] else '✗'}", file=sys.stderr)
    print(
        f"  Updates:   {'✓' if sources_status['subsequent_pubs'] else '✗'}",
        file=sys.stderr,
    )

    sys.exit(0)


def _check_prerequisites(rebuild_index):
    """Check that prerequisites are met before starting server"""
    pdf_count = check_mpep_pdfs()
    index_exists = (INDEX_DIR / "mpep_index.faiss").exists() and (
        INDEX_DIR / "mpep_metadata.json"
    ).exists()

    # First-run check: no index and no PDFs
    if not index_exists and pdf_count == 0:
        print("\n✗ No MPEP PDFs and no existing index found.", file=sys.stderr)
        print("\nTo get started:", file=sys.stderr)
        print("  1. python mcp_server/server.py --download-mpep", file=sys.stderr)
        print("  2. python mcp_server/server.py --rebuild-index", file=sys.stderr)
        print(
            "\nAlternatively, manually download MPEP PDFs and place in project root.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Rebuild check: trying to rebuild but no PDFs
    if pdf_count == 0 and rebuild_index:
        print("\n✗ No MPEP PDFs found.", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("1. Run with --download-mpep to download automatically", file=sys.stderr)
        print("2. Manually download PDFs and place in project root", file=sys.stderr)
        sys.exit(1)


def _run_health_checks():
    """Run pre-flight health checks and display warnings"""
    if not SystemHealthChecker:
        return

    print("\nRunning pre-flight health checks...", file=sys.stderr)
    checker = SystemHealthChecker()
    health_status = checker.check_all_dependencies(verbose=False)

    # Display warnings for missing optional components
    warnings = []
    if not health_status["patent_corpus"].get("ready", False):
        warnings.append("Patent corpus not available - prior art search will be limited")
    if not health_status["uspto_api"].get("available", False):
        warnings.append("USPTO API not configured - live patent search disabled")
    if health_status["gpu_status"].get("status") != "available":
        warnings.append(
            f"GPU not available: {health_status['gpu_status'].get('details', 'Using CPU mode')}"
        )

    if warnings:
        print("\n⚠️  Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"  - {warning}", file=sys.stderr)
        print("\nServer will start with limited functionality.", file=sys.stderr)
        print("Run 'patent-reviewer status --verbose' for details.\n", file=sys.stderr)
    else:
        print("✓ All systems operational\n", file=sys.stderr)


def main():
    """Main entry point"""
    args = _parse_args()

    # Handle download requests
    if args.download_mpep:
        _handle_mpep_download(args.mpep_url)

    if (
        args.download_all
        or args.download_statutes
        or args.download_regulations
        or args.download_updates
    ):
        _handle_additional_downloads(args)

    # Check prerequisites
    _check_prerequisites(args.rebuild_index)

    # Initialize MPEP index
    global mpep_index
    use_hyde = not args.no_hyde
    print("Initializing MPEP index...", file=sys.stderr)
    mpep_index = MPEPIndex(use_hyde=use_hyde)
    mpep_index.build_index(force_rebuild=args.rebuild_index)

    # Run health checks
    _run_health_checks()

    # Run the MCP server
    print("Starting MCP server...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
