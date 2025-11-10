# Utility Patent Reviewer - Advanced Documentation

## Documentation Guide

- **[README.md](README.md)** - Complete user guide with setup, features, and troubleshooting
- **[ADVANCED-README.md](ADVANCED-README.md)** (this file) - Technical architecture, API reference, and development guide

> **New here?** See [README.md](README.md) for complete setup and usage guide.

This document contains technical architecture details, manual installation procedures, performance tuning, API documentation, and development guidelines for advanced users and contributors.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Manual Installation](#manual-installation)
- [MCP Server Configuration](#mcp-server-configuration)
- [MCP Tools Reference](#mcp-tools-reference)
- [Data Sources](#data-sources)
- [Performance Optimization](#performance-optimization)
- [GPU Acceleration](#gpu-acceleration)
- [Diagram Generation](#diagram-generation)
- [USPTO API Setup](#uspto-api-setup)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)

---

## Architecture Overview

### System Components

```
utility-patent-reviewer/
├── mcp_server/              # MCP server implementation
│   ├── server.py           # Main MCP server entry point
│   ├── cli.py              # CLI commands
│   ├── mpep_search.py      # MPEP/statute vector search (in server.py)
│   ├── patent_corpus.py    # Patent corpus management
│   ├── patent_index.py     # Patent indexing and search
│   ├── uspto_api.py        # USPTO live API integration
│   ├── diagram_generator.py # Technical diagram generation
│   ├── index/              # MPEP indexes (created on first run)
│   ├── patent_corpus/      # Patent data files (created when downloaded)
│   └── patent_index/       # Patent indexes (created when built)
├── .claude/                 # Claude Code integration
│   ├── commands/           # Slash commands
│   │   ├── full-review.md
│   │   ├── review-claims.md
│   │   ├── review-specification.md
│   │   └── review-formalities.md
│   └── skills/             # Agent Skills
│       └── patent-reviewer.md
├── pdfs/                    # MPEP, 35 USC, 37 CFR PDFs (created on setup)
├── install.py              # Automated installation script
└── requirements.txt        # Python dependencies
```

### Technology Stack

**Core Framework:**
- FastMCP for MCP server
- PyMuPDF for PDF extraction
- BeautifulSoup4 + lxml for XML/HTML parsing
- Requests for HTTP clients

**RAG & Search:**
- BGE-base-en-v1.5 embeddings (768-dim, SOTA 2025)
- FAISS for vector search (inner product similarity)
- BM25Okapi for keyword search
- Cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
- Reciprocal Rank Fusion for hybrid search
- HyDE query expansion (3 modes)

**Diagram Generation:**
- Graphviz (DOT language)
- SVG manipulation
- Multiple layout engines

---

## Manual Installation

> **Recommended:** Use `python install.py` for automatic installation with GPU detection and compatible versions.

If the automated installer doesn't work for your environment, follow these manual steps:

### Step 1: Clone Repository

```bash
git clone https://github.com/RobThePCGuy/utility-patent-reviewer.git
cd utility-patent-reviewer
```

### Step 2: Create Virtual Environment

> **Note:** Virtual environment activation is only needed for running these manual installation commands. Claude Code will automatically manage the virtual environment during normal usage.

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Note:** Some Linux distributions require installing python3-venv first:
```bash
sudo apt install python3-venv  # Debian/Ubuntu
sudo yum install python3-venv  # RedHat/CentOS
```

### Step 3: Install PyTorch with CUDA (GPU users)

> **Note:** This manual installation is for advanced users who need direct control. The automated `install.py` script handles this automatically.

**Install PyTorch FIRST** (before other dependencies):

```bash
# For all NVIDIA GPUs (RTX 5090/5080 and older)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

**Why PyTorch first?** Installing `pip install -e .` will install CPU-only PyTorch. Installing CUDA PyTorch first prevents this.

### Step 4: Install Dependencies

**Install compatible versions:**
```bash
pip install --upgrade pip
pip install -e .
```

This installs:
- transformers==4.44.0
- sentence-transformers==3.1.0  
- numpy==1.26.4
- All other dependencies with compatible versions

**Verify installation:**
```bash
python test_install.py
```

**CPU Only:**
```bash
pip install torch
```

### Step 4: Download MPEP Data

```bash
patent-reviewer setup
```

Downloads and indexes (~500MB):
- MPEP (Manual of Patent Examining Procedure)
- 35 USC (United States Code Title 35)
- 37 CFR (Code of Federal Regulations Title 37)

**Time:** 5-15 minutes depending on internet speed

### Step 5: (Optional) Download Patent Corpus

```bash
patent-reviewer download-patents
patent-reviewer download-patents --build-index
```

Downloads 9.2M+ patents from PatentsView (~13GB)

**Time:**
- Download: 30-60 minutes
- Indexing: ~27 hours (RTX 5090 GPU) / ~270 hours (CPU)

### Step 6: (Optional) Install Graphviz

For diagram generation:

```bash
python scripts/install_graphviz.py
```

Or manually:
- Windows: `winget install graphviz`
- macOS: `brew install graphviz`
- Linux: `sudo apt install graphviz`

See [GRAPHVIZ_INSTALL.md](GRAPHVIZ_INSTALL.md) for details.

### Step 7: Register MCP Server

**Important:** If you're re-registering after an update, first remove the existing registration:
```bash
claude mcp remove utility-patent-reviewer
```

**Linux/macOS:**
```bash
claude mcp add --transport stdio utility-patent-reviewer --scope user -- \
  $(pwd)/venv/bin/python3 $(pwd)/mcp_server/server.py
```

**Windows (PowerShell):**
```powershell
claude mcp add --transport stdio utility-patent-reviewer --scope user -- `
  "$PWD\venv\Scripts\python.exe" "$PWD\mcp_server\server.py"
```

**Verify:**
```bash
claude mcp list
```

---

## MCP Server Configuration

### Configuration File Location

The MCP server is registered in Claude Code's configuration:
- **Linux/macOS:** `~/.config/claude/mcp_config.json`
- **Windows:** `%APPDATA%\claude\mcp_config.json`

### Configuration Format

```json
{
  "mcpServers": {
    "utility-patent-reviewer": {
      "command": "/path/to/venv/bin/python3",
      "args": ["/path/to/mcp_server/server.py"],
      "transport": "stdio"
    }
  }
}
```

### Environment Variables

Optional environment variables for configuration:

```bash
# USPTO API key (optional, increases rate limits)
export USPTO_API_KEY="your-api-key-here"

# Force CPU mode (multi-user setups)
export FORCE_CPU=1

# GPU selection
export CUDA_VISIBLE_DEVICES="0,1"
```

---

## MCP Tools Reference

### MPEP & Statute Search

#### `search_mpep`

Search MPEP, 35 USC, and 37 CFR with semantic similarity.

**Parameters:**
- `query` (str): Search query
- `top_k` (int, default=5): Number of results
- `retrieve_k` (int, optional): Candidates before reranking
- `source_filter` (str, optional): Filter by source ("MPEP", "35_USC", "37_CFR")

**Returns:**
```python
[
    {
        "text": "MPEP section text...",
        "section": "MPEP 2173",
        "page": 475,
        "relevance_score": 6.5,
        "has_statute": true
    }
]
```

#### `get_mpep_section`

Retrieve specific MPEP section by number.

**Parameters:**
- `section_number` (str): MPEP section (e.g., "2173")
- `max_chunks` (int, default=50): Maximum chunks to return

---

### Patent Analysis Tools

#### `review_patent_claims`

Automated claims analysis against MPEP guidelines.

**Parameters:**
- `claims_text` (str): Full text of all claims

**Returns:** Analysis with relevant MPEP sections and recommendations.

#### `review_specification`

Review specification requirements.

**Parameters:**
- `specification_topic` (str): Topic to review

#### `check_formalities`

Check formality requirements.

**Parameters:**
- `check_type` (str): Type of check (e.g., "abstract", "drawings")

---

### USPTO API Tools

#### `search_uspto_api`

Search live USPTO patent database.

**Parameters:**
- `query` (str): Search query
- `limit` (int, default=25, max=100): Number of results
- `start_year` (int, optional): Filter from year
- `end_year` (int, optional): Filter to year
- `application_type` (str, optional): "Utility", "Design", "Plant"

**Requires:** USPTO_API_KEY environment variable (free at https://developer.uspto.gov)

#### `get_uspto_patent`

Get specific patent by number.

**Parameters:**
- `patent_number` (str): USPTO patent number

---

### Prior Art Search (Local Corpus)

#### `search_prior_art`

Semantic search over local patent corpus.

**Parameters:**
- `description` (str): Invention description
- `top_k` (int, default=10): Results to return
- `cpc_filter` (str, optional): CPC code prefix (e.g., "G06F")
- `years_back` (int, optional): Search last N years

**Requires:** Patent corpus downloaded and indexed

#### `get_patent_details`

Get full patent details by ID.

**Parameters:**
- `patent_id` (str): USPTO patent number

---

### Diagram Generation

#### `render_diagram`

Render Graphviz DOT code to image.

**Parameters:**
- `dot_code` (str): Complete DOT language code
- `filename` (str, default="diagram"): Output filename
- `output_format` (str, default="svg"): "svg", "png", or "pdf"
- `engine` (str, default="dot"): Layout engine

**Requires:** Graphviz installed

#### `create_flowchart`

Generate patent-style flowchart from steps.

**Parameters:**
- `steps` (list): List of step dicts with id, label, shape, next
- `filename` (str): Output filename

#### `create_block_diagram`

Generate block diagram for system architecture.

**Parameters:**
- `blocks` (list): List of block dicts
- `connections` (list): List of connection tuples

---

## Data Sources

### MPEP & Statutes

**Source:** USPTO official publications
**Format:** PDF (converted to text)
**Coverage:** Complete MPEP, 35 USC, 37 CFR
**Size:** ~500MB
**Update Frequency:** Manual (quarterly)

**Updating MPEP:**
```bash
patent-reviewer setup --force-download
```

### Patent Corpus

**Source:** PatentsView (https://patentsview.org)
**Format:** Tab-delimited (TSV)
**Coverage:** 9.2+ million patents (1976-present)
**Size:** ~13GB compressed
**Update Frequency:** Quarterly (data as of June 30, 2025)

**Structure:**
```
mcp_server/
├── patent_corpus/
│   └── g_patent_*.parquet   # Patent grants (6 files)
└── patent_index/
    ├── patent_index.faiss   # FAISS vector index
    └── patent_metadata.json # Patent metadata
```

**Updating Patents:**
```bash
patent-reviewer download-patents --update
```

---

## Performance Optimization

### Vector Search

**Embedding Model:** BGE-base-en-v1.5 (768-dim)
- Fast, high quality
- ~80MB model size

**Alternative Models:**
```python
# In mcp_server/config.py
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Better quality
# Or
EMBEDDING_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"  # Faster
```

**Reranking Model:** cross-encoder/ms-marco-MiniLM-L-6-v2

### Index Building Performance

**GPU Acceleration:**
- NVIDIA RTX 5090: ~27 hours (17.6M chunks at 1.4s/batch)
- Older NVIDIA GPUs: ~30-40 hours
- CPU: ~270 hours (10x slower than GPU)

**Memory Requirements:**
- Minimum: 8GB RAM
- Recommended: 16GB RAM
- GPU VRAM: 4GB+ recommended (24GB for RTX 5090)

**Batch Size Tuning:**
```python
# In patent_search.py
EMBED_BATCH_SIZE = 32  # Increase if you have more VRAM
RERANK_BATCH_SIZE = 16
```

### Search Performance

- **MPEP Search:** ~100-500ms per query
- **Patent Search:** ~500-2000ms per query
- **USPTO API:** ~1-3 seconds per query (network dependent)

---

## GPU Acceleration

The `install.py` script automatically detects your GPU and installs the correct PyTorch version with CUDA support for 5-10x faster performance.

### Automatic GPU Setup

Just run the installer:
```bash
python install.py
```

The installer will:
1. Detect your GPU compute capability
2. Install PyTorch 2.9.0+cu128 for RTX 5090/5080 and other NVIDIA GPUs
3. Install compatible package versions (transformers 4.44.0, sentence-transformers 3.1.0)
4. Verify GPU is working

### Check Current GPU Status

```bash
python test_install.py
```

This shows:
- GPU model and VRAM
- CUDA availability
- Package versions
- Compatibility status

Or use:
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Manual PyTorch Installation (if needed)

**RTX 5090/5080 and All NVIDIA GPUs (CUDA 12.8):**

Windows:
```powershell
pip uninstall torch torchvision torchaudio
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

Linux/macOS:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

Visit https://pytorch.org/get-started/locally/ for latest versions.

### Compatible Package Versions

**Tested and working together:**
- PyTorch: 2.9.0+cu128 (CUDA 12.8)
- Transformers: 4.44.0
- Sentence Transformers: 3.1.0
- NumPy: 1.26.4
- FAISS-CPU: 1.12.0

**Important:** Don't use `pip install -r requirements.txt` directly - it may install incompatible versions. Always use `python install.py`.

### GPU Compatibility Table

| GPU Generation | Compute Capability | PyTorch Version | CUDA Version | Auto-Install |
|----------------|-------------------|-----------------|--------------|--------------|
| RTX 5090/5080 | 12.0 (sm_120) | 2.9.0+cu128 | 12.8 | ✓ |
| RTX 4090/4080 | 8.9 (sm_89) | 2.9.0+cu128 | 12.8 | ✓ |
| RTX 3090/3080 | 8.6 (sm_86) | 2.9.0+cu128 | 12.8 | ✓ |
| RTX 2080 Ti | 7.5 (sm_75) | 2.9.0+cu128 | 12.8 | ✓ |
| GTX 1080 Ti | 6.1 (sm_61) | 2.9.0+cu128 | 12.8 | ✓ |

**Tested Configuration (RTX 5090):**
- Driver: 581.80
- PyTorch: 2.9.0+cu128
- CUDA: 12.8
- Transformers: 4.44.0
- Sentence Transformers: 3.1.0
- FAISS: 1.12.0 (CPU on Windows, GPU on Linux)

See [GPU_SETUP.md](GPU_SETUP.md) for complete RTX 5090 setup guide with performance benchmarks.

### Optional: FAISS GPU (Linux only)

```bash
pip uninstall faiss-cpu
pip install faiss-gpu-cu12
```

**Note:** FAISS-GPU is Linux-only. Windows users will use CPU FAISS but still benefit from PyTorch GPU acceleration for embeddings (where most time is spent).

### Requirements

- NVIDIA GPU with CUDA support (GTX 10 series or newer)
- NVIDIA drivers installed (latest recommended)
- CUDA 11.8 or newer

See [GPU_SETUP.md](GPU_SETUP.md) for detailed GPU configuration.

---

## Diagram Generation

Graphviz is used to generate patent-style technical diagrams.

### Installation

**Windows:**
```powershell
winget install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Linux:**
```bash
sudo apt install graphviz  # Debian/Ubuntu
sudo yum install graphviz  # RedHat/CentOS
```

### Verify Installation

```bash
dot -V
patent-reviewer status
```

### Usage

Ask Claude to create diagrams:
- "Create a flowchart for my authentication process"
- "Draw a block diagram of my system architecture"
- "Generate a patent-style diagram with reference numbers"

Generated diagrams are saved to `diagrams/` directory.

See [GRAPHVIZ_INSTALL.md](GRAPHVIZ_INSTALL.md) for troubleshooting.

---

## USPTO API Setup

Access USPTO's live patent database (11M+ patents) without downloading the full corpus.

### 1. Create USPTO Account

1. Go to [data.uspto.gov/myodp](https://data.uspto.gov/myodp)
2. Click "I don't have a MyUSPTO account"
3. Complete registration and verify email

### 2. Verify with ID.me

1. Return to [data.uspto.gov/myodp](https://data.uspto.gov/myodp)
2. Click "Verify MyUSPTO account with ID.me"
3. Complete ID.me verification (self-service or video call)

### 3. Get Your API Key

1. Log in to [data.uspto.gov/myodp](https://data.uspto.gov/myodp)
2. Copy your API key (never expires if used yearly)

### 4. Configure API Key

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('USPTO_API_KEY', 'your_api_key', 'User')
```

**Linux/macOS:**
```bash
echo 'export USPTO_API_KEY="your_api_key"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Verify

```bash
patent-reviewer status
```

### USPTO API vs Local Corpus

| Feature | USPTO API | Local Corpus |
|---------|-----------|--------------|
| Patents Available | 11M+ (live) | 9.2M (1976-present) |
| Data Freshness | Real-time | Quarterly |
| Setup Time | 5 minutes | ~27 hours (RTX 5090 GPU) |
| Storage Required | None | 15-20GB |
| Internet Required | Yes | No |
| Search Speed | API latency | Instant |
| Privacy | Shared with USPTO | 100% local |

**Recommendation:** Use both for maximum capability.

---

## Development

### Project Structure

```
src/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py              # MCP server
│   ├── mpep_search.py         # MPEP search
│   ├── patent_search.py       # Patent search
│   ├── uspto_api.py           # USPTO API
│   ├── diagram_generator.py   # Diagrams
│   └── cli.py                 # CLI
├── tests/
│   ├── test_mpep_search.py
│   ├── test_patent_search.py
│   └── test_uspto_api.py
└── install.py
```

### Running Tests

```bash
pytest tests/ -v
```

### Adding New MCP Tools

1. **Define tool in server.py:**

```python
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="my_new_tool",
            description="Description",
            inputSchema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            }
        )
    ]
```

2. **Implement tool handler:**

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None):
    if name == "my_new_tool":
        result = my_implementation(arguments["param1"])
        return [types.TextContent(type="text", text=json.dumps(result))]
```

### Adding New Slash Commands

Create markdown file in `.claude/commands/`:

```markdown
---
description: Brief description
allowed-tools: tool1, tool2, tool3
model: claude-sonnet-4-5-20250929
---

# Command Name

Command implementation...

Use $ARGUMENTS for all args or $1, $2, $3 for positional args.
```

---

## Troubleshooting

### Common Issues

#### "Patent corpus index not built"

**Cause:** Downloaded corpus but haven't built index
**Fix:**
```bash
patent-reviewer download-patents --build-index
```

#### "Graphviz not installed"

**Cause:** System Graphviz not installed or not in PATH
**Fix:**
```bash
python scripts/install_graphviz.py
```

Or see [GRAPHVIZ_INSTALL.md](GRAPHVIZ_INSTALL.md)

#### "USPTO API key not configured"

**Cause:** Using USPTO API without key (rate limited)
**Fix:**
```bash
export USPTO_API_KEY="your-api-key"
```

#### "CUDA out of memory" during indexing

**Cause:** GPU doesn't have enough VRAM
**Fix:**
```python
# In patent_search.py, reduce batch size
EMBED_BATCH_SIZE = 16  # or 8
```

Or build index on CPU:
```bash
export CUDA_VISIBLE_DEVICES=""
patent-reviewer download-patents --build-index
```

#### MCP server not showing in Claude Code

**Cause:** Registration failed or path incorrect
**Fix:**

1. Check registration:
   ```bash
   claude mcp list
   ```

2. Check config file:
   ```bash
   # Linux/macOS
   cat ~/.config/claude/mcp_config.json

   # Windows
   type %APPDATA%\claude\mcp_config.json
   ```

3. Re-register with absolute paths
4. Restart Claude Code

#### Slow search performance

**MPEP Search:**
- Check if index exists: `ls mcp_server/index/`
- Rebuild index: `patent-reviewer setup --force-download`

**Patent Search:**
- Check GPU usage in logs
- Reduce `top_k` parameter
- Use `cpc_filter` to narrow scope

### Debug Mode

Enable detailed logging:

```bash
export PATENT_REVIEWER_DEBUG=1
claude --debug
```

Check logs:
```bash
# Linux/macOS
tail -f ~/.config/claude/logs/mcp.log

# Windows
type %APPDATA%\claude\logs\mcp.log
```

---

## FAQ

### General Questions

**Q: Is this tool free to use?**

A: Yes, completely free and open source under MIT License.

**Q: Can I use this without internet?**

A: Yes, once you download MPEP and patent corpus, everything runs 100% locally.

**Q: Do I need a GPU?**

A: No, GPU is optional. The app works fine on CPU, just 5-10x slower for index building.

### Setup Questions

**Q: How much disk space do I need?**

A: Minimum 2GB (MPEP only). Recommended 25GB (MPEP + full patent corpus + indices).

**Q: How long does setup take?**

A: MPEP: 15-20 minutes first time. Patent corpus: ~27 hours on RTX 5090 GPU, ~270 hours on CPU.

**Q: Can I install on multiple machines?**

A: Yes, just clone and run install.py on each machine.

### Usage Questions

**Q: Does this replace a patent attorney?**

A: No. This tool helps prepare documentation and understand requirements, but always consult a registered patent attorney before filing.

**Q: How current is the patent data?**

A: PatentsView: Updated quarterly (current as of June 30, 2025). USPTO API: Real-time.

**Q: Can I search foreign patents?**

A: Currently US patents only. EPO/WIPO support is on the roadmap.

### Technical Questions

**Q: What embedding model is used?**

A: BGE-base-en-v1.5 (768-dim), currently state-of-the-art for retrieval tasks.

**Q: Is my data private?**

A: Yes, completely private when using local corpus. USPTO API queries are visible to USPTO.

---

## Contributing

This project is open source and welcomes contributions!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests as needed
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Areas for Contribution

- Additional diagram templates
- More patent metadata extraction
- Performance optimizations
- Additional slash commands
- Documentation improvements
- Bug fixes
- Test coverage

### Development Setup

```bash
git clone https://github.com/RobThePCGuy/utility-patent-reviewer.git
cd utility-patent-reviewer
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
pytest
```

### Code Style

- Follow PEP 8
- Use Black for formatting
- Add type hints where applicable
- Write docstrings for public APIs
- Keep functions focused and testable

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Support

**Technical Issues:**
- GitHub Issues: https://github.com/RobThePCGuy/utility-patent-reviewer/issues
- Discussions: https://github.com/RobThePCGuy/utility-patent-reviewer/discussions

**Documentation:**
- Main README: [README.md](README.md)
- Graphviz Setup: [GRAPHVIZ_INSTALL.md](GRAPHVIZ_INSTALL.md)
- GPU Setup: [GPU_SETUP.md](GPU_SETUP.md)
- Claude Code Docs: https://docs.claude.com/en/docs/claude-code

---

**For simple installation, see [README.md](README.md)**
