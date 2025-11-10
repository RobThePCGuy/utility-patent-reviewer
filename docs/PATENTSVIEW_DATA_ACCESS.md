# PatentsView Bulk Data Access - Current Status

**Last Verified:** November 9, 2025
**Status:** ✅ Working

## Summary

The PatentsView bulk data download system is **fully functional** using the original S3 URLs. No code changes were needed. The previous implementation was correct; it just needed the `requests` library installed.

## Data Source

**Base URL:** `https://s3.amazonaws.com/data.patentsview.org/download/`

**Format:** Tab-separated values (TSV) files compressed in ZIP archives

## Available Files (Verified Working)

| File | Size | Status | Last Modified |
|------|------|--------|---------------|
| g_patent.tsv.zip | 217 MB | ✅ OK | Sep 9, 2025 |
| g_patent_abstract.tsv.zip | 1.6 GB | ✅ OK | Sep 9, 2025 |
| g_application.tsv.zip | 67 MB | ✅ OK | Sep 9, 2025 |
| g_cpc_current.tsv.zip | 466 MB | ✅ OK | Sep 9, 2025 |
| g_inventor_not_disambiguated.tsv.zip | 962 MB | ✅ OK | Sep 9, 2025 |
| g_assignee_not_disambiguated.tsv.zip | 465 MB | ✅ OK | Sep 9, 2025 |

**Total Size:** ~3.8 GB compressed, ~15 GB uncompressed

## What Changed in 2025

### ❌ Discontinued
- **PatentsView Legacy API** - Shut down May 1, 2025
  - Old endpoint: `api.patentsview.org` (returns 410 Gone)
  - Replaced by new PatentSearch API

### ✅ Still Working
- **S3 Bulk Downloads** - No changes
  - Same URLs as 2024 and earlier
  - Same file structure and format
  - Data updated quarterly

## Official Documentation

- **PatentsView Download Page:** https://patentsview.org/download/data-download-tables
- **Official Code Examples:** https://github.com/PatentsView/PatentsView-Code-Examples
- **Data Dictionary:** Available on PatentsView website

## Implementation Details

### Current Code (in `mcp_server/patent_corpus.py`)

```python
# This is CORRECT and working:
PATENTSVIEW_BASE_URL = "https://s3.amazonaws.com/data.patentsview.org/download/"
```

### Download Method

```python
from mcp_server.patent_corpus import PatentCorpusDownloader

downloader = PatentCorpusDownloader()
result = downloader.download_file("g_patent.tsv.zip")  # Downloads 217 MB
```

### Requirements

- `requests` library (listed in requirements.txt)
- Internet connection
- ~15-20 GB disk space for full corpus

## Testing

Run the included test script:

```bash
python scripts/test_download.py
```

Expected output:
```
Testing PatentsView download...
Downloading g_patent.tsv.zip (217 MB)...
  Progress: 100.0%
  Downloaded g_patent.tsv.zip (217.0 MB)
Extracting g_patent.tsv.zip...
  Extracted to C:\...\mcp_server\patent_corpus\g_patent.tsv
Success! Downloaded to: C:\...\mcp_server\patent_corpus\g_patent.tsv
File size: 227.3 MB
```

## Alternative Access Methods

### 1. Direct Download (curl/wget)
```bash
wget https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip
```

### 2. Pandas (for small samples)
```python
import pandas as pd
df = pd.read_csv(
    "https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip",
    delimiter="\t",
    dtype=str,
    nrows=1000  # Sample first 1000 rows
)
```

### 3. This Tool's CLI
```bash
patent-reviewer download-patents --build-index
```

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'requests'`
**Solution:**
```bash
pip install requests
# or
pip install -r requirements.txt
```

### Error: Download timeout
**Solution:**
- Check internet connection
- Try again (S3 may be temporarily slow)
- Download manually and place in `mcp_server/patent_corpus/`

### Error: Disk space
**Solution:**
- Full corpus needs ~20GB total
- Download individual files as needed
- Use USPTO API instead for online access

## For Repo Users

The code in this repository is **ready to use**. Just ensure:

1. ✅ Dependencies installed: `pip install -r requirements.txt`
2. ✅ Run download: `python scripts/test_download.py` (or full setup)
3. ✅ URLs verified working: November 2025

No code changes needed. The implementation is current and correct.

## Migration Notes

If you're migrating from older PatentsView code:

- **S3 URLs:** No change needed - still working
- **API calls:** Switch to new PatentSearch API if using programmatic queries
- **File format:** Still TSV in ZIP - no change
- **Table structure:** Same column names and schema

## License

PatentsView data is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

Source: United States Patent and Trademark Office (USPTO)
Distributed by: PatentsView.org

---

**Status Summary:** All systems operational. Code is production-ready.
