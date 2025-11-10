[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/RobThePCGuy/utility-patent-reviewer)

## Vision

I have a dream... of a world where inventors can transform their ideas into patent-ready applications without navigating complex legal interfaces or paying prohibitive upfront costs. By combining Claude's reasoning capabilities with patent examination standards, I hope to bridge the gap between invention and protection by turning rough notes, drawings, and concepts into structured, examination-ready patent applications through natural conversation rather than specialized legal expertise.

This HEAVY work-in-progress platform will illuminate the patent landscape, helping inventors understand prior art and competitive positioning before they invest time and resources, enabling smarter strategic decisions about what and how to protect. In turn, it will educate through the drafting process, transparently applying USPTO standards (MPEP) to provide constructive feedback that teaches inventors what examiners look for, without crossing into legal advice.

The system will deliver examination-ready quality by producing 80-90% complete applications that are properly structured, internally consistent, and aligned with formal requirements, ready for final attorney review and filing.

My North Star: An inventor should be able to have a conversation about their idea and walk away with either a patent draft ready for attorney review or clear guidance on how to refine their innovation to be more defensible, all without needing to first become a patent expert themselves.

I want to emphasize that this tool will not replace patent attorneys; I want to make their expertise more accessible and enable inventors to arrive at that conversation better prepared and more informed.

# Utility Patent Reviewer

**Talk to Claude about your invention. Get patent-ready documentation.**

This tool gives Claude AI instant access to US Patent Office rules and 9.2+ million patents, so you can prepare patent applications through natural conversation.

Everything runs on your computer. Your ideas stay private. No subscriptions.

## Recent Updates

- **Automatic GPU Setup:** `install.py` detects your GPU and installs correct PyTorch automatically
- **RTX 5090/5080 Support:** Full compute capability detection with CUDA 12.8
- **Package Compatibility:** Pre-tested compatible versions (no more import errors)
- **One-Command Install:** Just run `python install.py` - all dependencies handled automatically
- **USPTO API Integration:** Search 11M+ patents live without downloading corpus (free API key)
- **Automated Reviews:** Slash commands for complete patent application compliance checks
- **Patent Diagrams:** Generate patent-style technical drawings using Graphviz

---

## Quick Start

> **IMPORTANT:** This tool is designed to work with **[Claude Code](https://claude.com/code)**, Anthropic's official CLI for Claude AI. You cannot use this tool with the Claude web interface, API, or other chat tools. You must have Claude Code installed before proceeding.

### Requirements

- **[Claude Code](https://claude.com/code)** - REQUIRED (this is the AI interface that runs the tool)
- **Python 3.9+** (check with `python --version`)
- **Internet connection** (for initial setup only)
- **Disk space:**
  - Minimum: 2GB (just USPTO rules)
  - Full: 25GB (includes 9.2M patents)

### Installation

**Step 1: Clone the repository**

```bash
git clone https://github.com/RobThePCGuy/utility-patent-reviewer.git
cd utility-patent-reviewer
```

**Step 2: Create and activate virtual environment**

> **Note:** This step is required for running `install.py`. After installation, Claude Code will automatically manage the virtual environment for you during normal usage.

Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Run the installer**

```bash
python install.py
```

The installer will:
- ✓ Detect your system (Windows/Linux/macOS)
- ✓ Detect your GPU (NVIDIA with CUDA support)
- ✓ Install compatible package versions automatically
- ✓ Install PyTorch with CUDA 12.8 if NVIDIA GPU detected
- ✓ Optionally download USPTO rules (~500MB)
- ✓ Optionally download 9.2M patents (~13GB)
- ✓ Register with Claude Code automatically

**Compatible versions installed:**
- PyTorch 2.9.0+cu128 (GPU) or 2.9.0 (CPU)
- Transformers 4.44.0
- Sentence Transformers 3.1.0
- NumPy 1.26.4
- FAISS 1.12.0

**First-time setup:** 5-20 minutes (depending on what you download)

**Step 4: Restart Claude Code** and you're ready to go!

### Using the Virtual Environment

> **Important:** When using Claude Code, you do **not** need to manually activate the virtual environment. Claude Code handles this automatically.

Manual activation is **only required** for advanced operations:
- Running `install.py` directly
- Manually updating dependencies with `pip`
- Updating documentation
- Running troubleshooting scripts directly
- Other direct CLI operations outside of Claude Code

**Activate** (for advanced operations only):

Windows:
```powershell
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

**Deactivate** (when you're done with advanced operations):
```bash
deactivate
```

---

## What You Can Do

### Search USPTO Rules

Ask Claude questions about patent requirements:

```
"What are the requirements for patent claims?"
"Search MPEP for claim indefiniteness standards"
"What are enablement requirements under 35 USC 112(a)?"
```

Claude searches the MPEP, 35 USC, and 37 CFR and provides exact citations.

### Review Your Patent Application

Use slash commands for automated reviews:

- `/full-review` - Complete application review (claims + spec + formalities)
- `/review-claims` - Check claims for definiteness, antecedent basis, compliance
- `/review-specification` - Verify written description, enablement, best mode
- `/review-formalities` - Check abstract, title, drawings, required sections
- `/create-patent` - Create complete application with automatic validation

### Find Prior Art

Search millions of patents for similar inventions:

```
"Search for prior art on blockchain-based voting systems"
"Find patents about neural network training from the last 5 years"
"Search for inventions in CPC class G06F related to data compression"
"Find patents by Google about machine learning before 2020"
"Analyze Apple's patent portfolio in augmented reality"
```

**Three Search Options:**

1. **PatentsView Search API:** Real-time searches with advanced filtering by inventor, assignee, classification, citations, and more. Perfect for competitive intelligence and targeted searches. Requires free API key. See [PatentsView Search API Setup](#patentsview-search-api-setup) below.

2. **Local Corpus:** Download 9.2M patents for fast offline semantic search. Best for privacy and comprehensive analysis.

3. **USPTO API:** Search live USPTO database (11M+ patents) without downloading. See [USPTO API Setup](#uspto-api-setup) below.

### Generate Patent Diagrams

Create patent-style technical drawings:

```
"Create a flowchart showing my authentication process"
"Draw a block diagram of a machine learning training system"
"Generate a system architecture diagram with sensors, processor, and display"
```

---

## What's Included

| Feature | Description | Setup Required |
|---------|-------------|----------------|
| MPEP Search | Search USPTO examination rules | Auto (500MB) |
| Patent Review | Automated USPTO compliance checks | Auto |
| PatentsView Search | Advanced patent search with filtering & analytics | [Optional API key](#patentsview-search-api-setup) |
| USPTO API | Search 11M+ patents live (real-time) | [Optional API key](#uspto-api-setup) |
| Prior Art Database | Search 9.2M+ patents offline | Optional (13GB) |
| Diagram Generation | Create patent-style drawings | Optional (Graphviz) |
| GPU Acceleration | 5-10x faster indexing | Auto-detected |

---

## System Status & Health Checks

Before using the patent reviewer, check system health:

```bash
patent-reviewer status
```

**Output shows:**
```
=================================================================
SYSTEM STATUS - Utility Patent Reviewer
=================================================================

MPEP Index............ ✓ Ready (150,234 chunks, 3.2 MB)
Patent Corpus......... ✗ Not Built
                         Fix: patent-reviewer download-patents --build-index
USPTO API............. ✓ Connected (Key: ***...abc123)
Graphviz.............. ✓ Installed (v12.2.1)
GPU................... ✓ NVIDIA RTX 5090 (24GB)
Disk Space............ ✓ 127GB available

Models:
  Embeddings        ✓
  Reranker          ✓
  Hyde              ✓

OVERALL STATUS: 6/7 components ready (86%)
=================================================================
```

### Health Check Features

- **Pre-flight validation** - Catches 95%+ of config issues before they cause failures
- **Actionable fixes** - Every ✗ includes exact command to fix
- **Startup warnings** - Server shows health status on startup
- **Diagnostic reports** - Save to JSON for troubleshooting

### Common Fixes

```bash
# MPEP Index missing
patent-reviewer setup

# USPTO API not configured
export USPTO_API_KEY="your_key_here"  # Linux/macOS
set USPTO_API_KEY=your_key_here       # Windows

# Patent corpus not built
patent-reviewer download-patents --build-index

# Graphviz not installed
sudo apt install graphviz  # Linux
brew install graphviz      # macOS
winget install graphviz    # Windows
```

---

## Usage Guide

### Best Practices

#### Skills vs Commands

**Skills** (`.claude/skills/patent-reviewer/`) - Activate automatically:
- Just mention relevant topics: "patent", "USPTO", "MPEP", "claims"
- No explicit invocation needed
- Claude recognizes when patent expertise is needed

**Commands** (`.claude/commands/`) - Invoke with `/` prefix:
- `/full-review` - Complete application review
- `/review-claims` - Claims-only analysis
- `/review-specification [topic]` - Spec review with optional focus area
- `/review-formalities [type]` - Formalities check with optional type filter
- `/create-patent` - Create complete application with validation

**Tip:** Use commands when you want a structured workflow, or just ask naturally to let skills activate automatically.

#### Effective Reviews

**Start with a full review:**
```
/full-review
```
Then paste your application sections when prompted. This gives you a comprehensive baseline.

**Iterative refinement:**
After addressing issues, run focused commands:
```
/review-claims          # Verify claim fixes
/review-formalities abstract  # Check abstract word count
```

**Get MPEP guidance:**
Ask questions naturally and the skill will search MPEP automatically:
```
"What does MPEP say about claim definiteness?"
"Show me requirements for enablement under 35 USC 112"
```

#### Prior Art Searches

**For recent patents (last 5 years):**
Use USPTO API (fast, always current):
```
"Search USPTO for patents about [your technology] from 2020-2025"
```

**For comprehensive searches:**
Use local corpus (offline, semantic search):
```
"Search prior art for similar inventions to [your description]"
"Find patents in CPC class G06F related to [technology]"
```

**Best approach:** Use both and compare results.

### Working with Results

**Always review MPEP citations:**
- Each finding includes specific MPEP section references
- Use these to understand USPTO requirements directly
- Ask for clarification: "Explain MPEP 2173.05(b) in plain English"

**Prioritize fixes:**
1. **Critical** - Must fix before filing (missing antecedent basis, claim support issues)
2. **Important** - Strongly recommend (scope issues, vague terms)
3. **Minor** - Consider improving (style, additional examples)

**Request revisions:**
```
"Rewrite claim 1 to fix the indefiniteness issue"
"Suggest better wording for element X"
```

### Performance Tips

**GPU acceleration:**
- Install with `install.py` for automatic GPU detection
- GPU speeds up searches 5-10x
- Check status: `patent-reviewer status`

**Index building:**
- MPEP: 5-10 minutes (do this first)
- Patents: ~27 hours on RTX 5090 GPU, ~270 hours on CPU (optional, do overnight)
- Both are one-time operations

**API rate limits:**
- USPTO API: ~100 requests/minute
- Spread searches out if hitting limits
- Local corpus has no rate limits

---

## PatentsView Search API Setup

Advanced patent searching with filtering by inventor, assignee, classification, citations, and more. Perfect for competitive intelligence and targeted prior art searches.

**Quick Setup (2 minutes):**

1. Request free API key at [PatentsView Help Center](https://patentsview-support.atlassian.net/servicedesk/customer/portal/1/group/1/create/18)
2. Set `PATENTSVIEW_API_KEY` environment variable
3. Start searching with natural language queries

**Complete setup guide:** [docs/PATENTSVIEW_API_SETUP.md](docs/PATENTSVIEW_API_SETUP.md)

---

## USPTO API Setup

Access USPTO's live patent database (11M+ patents) in real-time without downloading the full corpus.

**Quick Setup (5 minutes):**

1. Create account at [data.uspto.gov/myodp](https://data.uspto.gov/myodp)
2. Verify with ID.me
3. Generate API key
4. Set `USPTO_API_KEY` environment variable
5. Verify with `patent-reviewer status`

**Complete setup guide:** [docs/USPTO_API_SETUP.md](docs/USPTO_API_SETUP.md)

### Patent Search Comparison

| Feature | PatentsView Search API | USPTO API | Local Corpus |
|---------|------------------------|-----------|--------------|
| Patents Available | US patents (current) | 11M+ (live) | 9.2M (1976-present) |
| Setup Time | 2 minutes | 5 minutes | ~27 hours (RTX 5090 GPU) |
| Storage Required | None | None | 15-20GB |
| Advanced Filtering | ✓ (inventor, assignee, CPC, citations) | Limited | Semantic only |
| Competitive Intelligence | ✓ Best | Basic | Basic |
| Citation Network | ✓ Native support | No | No |
| Semantic Search | No | No | ✓ Best |
| Privacy | Shared with PatentsView | Shared with USPTO | ✓ 100% local |
| Best For | Targeted search, analysis | Recent patents, lookups | Privacy, semantic search |

**Recommendation:** Use all three for comprehensive patent research.

---

## Common Questions

**Q: Do I need to download all 9.2 million patents?**

A: No! You have three options:
- **USPTO API:** Search 11M+ patents online (free API key required, 5 min setup)
- **Local Corpus:** Download 9.2M patents for offline semantic search (15GB, ~27 hours indexing on RTX 5090 GPU)
- **Both:** Use API for recent patents and local corpus for privacy and speed

**Q: What if I don't have a GPU?**

A: No problem. The installer detects your hardware and uses CPU automatically. GPU is optional for speed.

**Q: Is this a replacement for a patent attorney?**

A: No. This tool helps you prepare applications and understand USPTO rules, but always consult a registered patent attorney before filing.

**Q: Where does my data go?**

A: Everything runs on your computer. Your patent information never leaves your machine unless you explicitly share it.

Downloaded PDFs are stored in the `pdfs/` directory. After indexing, you can delete them to save space (the index will still work).

**Q: What if setup fails?**

A: See [ADVANCED-README.md](ADVANCED-README.md) for detailed troubleshooting, or open an issue on GitHub.

**Q: How current is the patent data?**

A: PatentsView: Updated quarterly (current as of June 2025). USPTO API: Real-time.

**Q: Is my data private?**

A: Yes, completely private when using local corpus. USPTO API queries are visible to USPTO.

**Q: Can I search foreign patents?**

A: Currently US patents only. EPO/WIPO support is on the roadmap.

---

## Platform-Specific Notes

### Windows

- Run `install.py` from PowerShell or Command Prompt
- Graphviz: `winget install graphviz` (for diagrams)
- GPU support: Auto-detected for NVIDIA cards

**RTX 5090/5080 Users:** Automatically detected and configured with CUDA 12.8 during installation.

### Linux

- Some distros require: `sudo apt install python3-venv`
- Graphviz: `sudo apt install graphviz` (for diagrams)
- GPU support: NVIDIA GPUs with CUDA automatically detected

### macOS

- Works on both Intel and Apple Silicon
- Graphviz: `brew install graphviz` (for diagrams)
- GPU support: CPU only (NVIDIA CUDA not available on macOS)

---

## Troubleshooting

### "externally-managed-environment" error (Linux)

```bash
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
```

### Virtual environment won't activate (Windows)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
```

### Graphviz not found

Install Graphviz for your platform:
- Windows: `winget install graphviz`
- macOS: `brew install graphviz`
- Linux: `sudo apt install graphviz`

See [GRAPHVIZ_INSTALL.md](GRAPHVIZ_INSTALL.md) for detailed instructions.

### MCP server not showing in Claude Code

```bash
claude mcp list
```

If not listed, the installer will show the manual registration command.

### GPU not detected after installation

The `install.py` script automatically detects and configures GPU support. To verify:

```bash
python test_install.py
```

This will show:
- ✓ All package versions
- ✓ GPU status and details
- ✓ CUDA availability
- ✓ Model loading test

If GPU isn't detected but you have an NVIDIA GPU:

1. **Check NVIDIA drivers are installed:**
```powershell
nvidia-smi
```

2. **Re-run the installer:**
```powershell
python install.py
```

The installer will automatically:
- Detect your GPU compute capability
- Install PyTorch with CUDA 12.8 for RTX 5090/5080
- Install compatible package versions
- Verify everything works

**Manual GPU installation (advanced):**
```powershell
# Remove CPU version
pip uninstall torch torchvision torchaudio

# Install CUDA 12.8 version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Verify
python test_install.py
```

See [ADVANCED-README.md](ADVANCED-README.md#gpu-acceleration) for advanced GPU configuration.

### Skill not activating?
- Use explicit trigger words: "patent", "USPTO", "MPEP"
- Or invoke commands directly with `/`

### MCP tools not available?
```bash
claude mcp list                    # Verify registration
patent-reviewer verify-config      # Check paths
patent-reviewer status --verbose   # Check all dependencies
```

### Empty search results?
- Check API key: `echo $USPTO_API_KEY` (Linux/Mac) or `$env:USPTO_API_KEY` (Windows)
- Verify index built: `patent-reviewer status`
- Try broader search terms

---

## Documentation

### Main Documentation
- **[README.md](README.md)** (this file) - Complete user guide with setup, features, and troubleshooting
- **[ADVANCED-README.md](ADVANCED-README.md)** - Technical architecture, API reference, and development guide

### Specific Topics
- **Environment Variables** - [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md)
- **GPU Setup** - [docs/GPU_SETUP.md](docs/GPU_SETUP.md)
- **PatentsView Data Access** - [docs/PATENTSVIEW_DATA_ACCESS.md](docs/PATENTSVIEW_DATA_ACCESS.md)
- **PatentsView Search API** - [docs/PATENTSVIEW_API_SETUP.md](docs/PATENTSVIEW_API_SETUP.md)
- **USPTO API** - [docs/USPTO_API_SETUP.md](docs/USPTO_API_SETUP.md)
- **Manual Installation** - [ADVANCED-README.md](ADVANCED-README.md#manual-installation)
- **API Reference** - [ADVANCED-README.md](ADVANCED-README.md#mcp-tools-reference)
- **Development** - [ADVANCED-README.md](ADVANCED-README.md#development)

### Which Guide Should I Use?

**New users:** Start here (README.md) for complete setup and usage

**Developers/Contributors:** See [ADVANCED-README.md](ADVANCED-README.md) for:
- Architecture details
- API documentation
- Performance tuning
- Contributing guidelines
- Manual installation procedures

---

## Privacy and Security

- All processing is local except USPTO API calls
- Your application text never leaves your computer
- API calls only send search queries, not your full application
- Patent corpus is stored locally for 100% offline operation

---

## Need Help?

- **Documentation:**
  - Quick start: This README
  - Technical details: [ADVANCED-README.md](ADVANCED-README.md)
- **GitHub Issues:** [Report bugs or request features](https://github.com/RobThePCGuy/utility-patent-reviewer/issues)
- **Discussions:** [Ask questions](https://github.com/RobThePCGuy/utility-patent-reviewer/discussions)

---

## Acknowledgments

This tool is built on the work of many open source contributors and data providers:

### Data Sources
- **[USPTO (United States Patent and Trademark Office)](https://www.uspto.gov/)** - Manual of Patent Examining Procedure (MPEP), 35 USC, 37 CFR, and patent database
- **[PatentsView](https://patentsview.org/)** - Bulk patent datasets (9.2M+ patents, 1976-present)
  - Data source: S3 bulk downloads at `s3.amazonaws.com/data.patentsview.org/download/`
  - Format: Tab-separated values (TSV) in ZIP archives
  - Files: `g_patent.tsv.zip` (217 MB), `g_patent_abstract.tsv.zip` (1.6 GB), and related tables
  - Last verified: November 2025 (all download URLs working)

### AI Models
- **[BGE-base English v1.5](https://huggingface.co/BAAI/bge-base-en-v1.5)** (BAAI, 2024) - Semantic embedding model for document search
- **[MS MARCO MiniLM v2 Cross-Encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2)** (Microsoft) - Neural reranking model for search relevance

### Supporting Libraries
- **[PyTorch](https://pytorch.org/)** - Deep learning framework
- **[Sentence Transformers](https://www.sbert.net/)** - Embedding model infrastructure
- **[FAISS](https://github.com/facebookresearch/faiss)** - Vector similarity search (Meta AI)
- **[Graphviz](https://graphviz.org/)** - Patent diagram generation

Thank you to all the researchers, developers, and organizations who make open source AI and data access possible.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Disclaimer

This tool provides access to USPTO rules and patent databases to assist in patent application preparation. It does not constitute legal advice. Patent applications are complex legal documents. Always consult with a registered patent attorney or agent before filing with the USPTO.

**This project is not affiliated with, endorsed by, or sponsored by the United States Patent and Trademark Office (USPTO).**

The authors make no warranties about the accuracy, completeness, or suitability of the information provided. Use at your own risk.

---

**Star on GitHub** if this helps you! [github.com/RobThePCGuy/utility-patent-reviewer](https://github.com/RobThePCGuy/utility-patent-reviewer)
