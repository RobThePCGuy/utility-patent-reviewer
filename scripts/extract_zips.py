#!/usr/bin/env python3
"""
Extract any remaining ZIP files in the patent corpus directory
Useful for Windows file locking issues
"""

import sys
import zipfile
from pathlib import Path

# Script is in scripts/, so go up to project root, then into mcp_server/
project_root = Path(__file__).parent.parent
corpus_dir = project_root / "mcp_server" / "patent_corpus"

print(f"Checking for ZIP files in: {corpus_dir}")

zip_files = list(corpus_dir.glob("*.zip"))

if not zip_files:
    print("No ZIP files found. All files already extracted!")
    sys.exit(0)

print(f"Found {len(zip_files)} ZIP file(s) to extract:")
for zf in zip_files:
    print(f"  - {zf.name} ({zf.stat().st_size / 1024 / 1024:.1f} MB)")

print("\nExtracting...")

for zip_path in zip_files:
    try:
        output_name = zip_path.stem + ".tsv"
        output_path = corpus_dir / output_name

        if output_path.exists():
            print(f"  {zip_path.name}: Already extracted, deleting ZIP...")
            zip_path.unlink()
            continue

        print(f"  {zip_path.name}: Extracting...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".tsv"):
                    zf.extract(name, corpus_dir)
                    extracted = corpus_dir / name

                    # Rename if needed
                    if extracted != output_path:
                        extracted.rename(output_path)

        # Delete ZIP after successful extraction
        zip_path.unlink()
        print(f"    ✓ Extracted to {output_name}")

    except Exception as e:
        print(f"    ✗ Error: {e}")

print("\nDone!")
