#!/usr/bin/env python3
"""Test PatentsView download"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.patent_corpus import PatentCorpusDownloader

print("Testing PatentsView download...", file=sys.stderr)
downloader = PatentCorpusDownloader()

# Test downloading just the main patent file
print("Downloading g_patent.tsv.zip (217 MB)...", file=sys.stderr)
result = downloader.download_file("g_patent.tsv.zip")

if result:
    print(f"Success! Downloaded to: {result}", file=sys.stderr)
    print(f"File size: {result.stat().st_size / 1024 / 1024:.1f} MB", file=sys.stderr)
else:
    print("Download failed!", file=sys.stderr)
    sys.exit(1)
