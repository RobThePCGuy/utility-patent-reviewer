#!/usr/bin/env python3
"""
Command-line interface for Utility Patent Reviewer
Provides easy setup and management commands
"""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

# Import patent corpus management
from mcp_server.patent_corpus import (
    PATENT_INDEX_DIR,
    PatentCorpusDownloader,
    check_patent_corpus_status,
)
from mcp_server.patent_index import PatentCorpusIndex

# Import from server module
from mcp_server.server import (
    INDEX_DIR,
    MPEP_DIR,
    MPEP_DOWNLOAD_URL,
    MPEPIndex,
    check_all_sources,
    check_mpep_pdfs,
    download_35_usc,
    download_37_cfr,
    download_mpep_pdfs,
    download_subsequent_publications,
    extract_mpep_pdfs,
    mcp,
)

# Import path utilities for cross-platform path handling
try:
    from mcp_server.path_utils import PathFormatter
except ImportError:
    try:
        from path_utils import PathFormatter
    except ImportError:
        PathFormatter = None


def configure_mcp_server():
    """
    Register the MCP server with Claude Code using 'claude mcp add' command
    """
    import platform

    # Get correct paths - server.py is in project_root/mcp_server/, not in MPEP_DIR (pdfs/)
    project_root = Path(__file__).parent.parent.resolve()  # Go up from mcp_server/ to project root
    server_script = (project_root / "mcp_server" / "server.py").resolve()
    python_path = Path(sys.executable).resolve()
    is_windows = platform.system() == "Windows"

    print("\n" + "=" * 60, file=sys.stderr)
    print("Registering MCP Server with Claude Code", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Verify paths exist
    if not python_path.exists():
        print(f"\n✗ Python executable not found: {python_path}", file=sys.stderr)
        return False

    if not server_script.exists():
        print(f"\n✗ Server script not found: {server_script}", file=sys.stderr)
        return False

    # On Windows, Claude CLI requires git-bash - set environment variable
    if platform.system() == "Windows":
        try:
            result = subprocess.run(["where", "bash"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                bash_path = result.stdout.strip().split("\n")[0]
                os.environ["CLAUDE_CODE_GIT_BASH_PATH"] = bash_path
        except Exception:
            pass

    # Check if claude command exists
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"], capture_output=True, text=True, timeout=10
        )
        claude_available = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        claude_available = False

    if not claude_available:
        print("\n⚠ Claude CLI not found in PATH", file=sys.stderr)
        print("\nPlease manually register the MCP server:", file=sys.stderr)
        # Use PathFormatter if available, otherwise fallback to basic POSIX conversion
        if PathFormatter:
            python_str, server_str = PathFormatter.format_for_claude_mcp(python_path, server_script)
        else:
            python_str = str(python_path).replace("\\", "/")
            server_str = str(server_script).replace("\\", "/")
        print(
            f'\n  claude mcp add --transport stdio utility-patent-reviewer --scope user -- "{python_str}" "{server_str}"',
            file=sys.stderr,
        )
        return False

    # Remove existing registration if present
    try:
        subprocess.run(
            ["claude", "mcp", "remove", "utility-patent-reviewer"],
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass

    # Register the MCP server with correct format
    # Use PathFormatter for proper cross-platform path handling
    if PathFormatter:
        python_str, server_str = PathFormatter.format_for_claude_mcp(python_path, server_script)
    else:
        python_str = str(python_path).replace("\\", "/")
        server_str = str(server_script).replace("\\", "/")

    try:
        cmd = [
            "claude",
            "mcp",
            "add",
            "--transport",
            "stdio",
            "utility-patent-reviewer",
            "--scope",
            "user",
            "--",
            python_str,
            server_str,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("\n✓ MCP server registered with Claude Code", file=sys.stderr)
            print("  Name: utility-patent-reviewer", file=sys.stderr)
            print(f"  Python: {python_str}", file=sys.stderr)
            print(f"  Script: {server_str}", file=sys.stderr)
            print("\nVerify with: claude mcp list", file=sys.stderr)
            print("\nVerify paths with: patent-reviewer verify-config", file=sys.stderr)
            return True
        else:
            print(f"\n✗ Failed to register MCP server: {result.stderr}", file=sys.stderr)
            print("\nManual registration command:", file=sys.stderr)
            print(
                f'  claude mcp add --transport stdio utility-patent-reviewer --scope user -- "{python_str}" "{server_str}"',
                file=sys.stderr,
            )
            return False
    except Exception as e:
        print(f"\n✗ Failed to register MCP server: {e}", file=sys.stderr)
        print("\nManual registration command:", file=sys.stderr)
        # Use PathFormatter for proper path formatting
        if PathFormatter:
            python_str, server_str = PathFormatter.format_for_claude_mcp(python_path, server_script)
        else:
            python_str = str(python_path).replace("\\", "/")
            server_str = str(server_script).replace("\\", "/")
        print(
            f'  claude mcp add --transport stdio utility-patent-reviewer --scope user -- "{python_str}" "{server_str}"',
            file=sys.stderr,
        )
        return False


def setup_command(args):
    """
    One-command setup: downloads all sources and builds index
    """
    print("\n" + "=" * 60, file=sys.stderr)
    print("Utility Patent Reviewer - Automatic Setup", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Check current status
    sources_status = check_all_sources()
    pdf_count = check_mpep_pdfs()

    print("\nChecking current status...", file=sys.stderr)
    print(
        f"  MPEP PDFs: {'✓' if sources_status['mpep'] else '✗'} ({pdf_count} files)",
        file=sys.stderr,
    )
    print(f"  35 USC:    {'✓' if sources_status['35_usc'] else '✗'}", file=sys.stderr)
    print(f"  37 CFR:    {'✓' if sources_status['37_cfr'] else '✗'}", file=sys.stderr)
    print(
        f"  Updates:   {'✓' if sources_status['subsequent_pubs'] else '✗'}",
        file=sys.stderr,
    )

    # Download missing sources
    downloads_needed = []
    if not sources_status["mpep"]:
        downloads_needed.append("MPEP")
    if not sources_status["35_usc"]:
        downloads_needed.append("35 USC")
    if not sources_status["37_cfr"]:
        downloads_needed.append("37 CFR")
    if not sources_status["subsequent_pubs"]:
        downloads_needed.append("Subsequent Publications")

    if downloads_needed:
        print(f"\nDownloading: {', '.join(downloads_needed)}", file=sys.stderr)
        print("This may take several minutes...\n", file=sys.stderr)

        # Download MPEP if needed
        if "MPEP" in downloads_needed:
            if download_mpep_pdfs(MPEP_DOWNLOAD_URL):
                extract_mpep_pdfs()
            else:
                print("\n✗ MPEP download failed. Cannot continue.", file=sys.stderr)
                return 1

        # Download 35 USC if needed
        if "35 USC" in downloads_needed:
            download_35_usc()

        # Download 37 CFR if needed
        if "37 CFR" in downloads_needed:
            download_37_cfr()

        # Download Subsequent Publications if needed
        if "Subsequent Publications" in downloads_needed:
            download_subsequent_publications()

        print("\n✓ All downloads complete", file=sys.stderr)
    else:
        print("\n✓ All sources already present", file=sys.stderr)

    # Build index
    index_exists = (INDEX_DIR / "mpep_index.faiss").exists()

    if args.rebuild or not index_exists:
        print("\nBuilding search index...", file=sys.stderr)
        print("This will take 5-10 minutes on first run.\n", file=sys.stderr)

        use_hyde = not args.no_hyde
        mpep_index = MPEPIndex(use_hyde=use_hyde)
        mpep_index.build_index(force_rebuild=True)

        print("\n✓ Index built successfully", file=sys.stderr)
    else:
        print("\n✓ Index already exists (use --rebuild to force rebuild)", file=sys.stderr)

    # Configure MCP server
    mcp_configured = configure_mcp_server()

    # Final status
    print("\n" + "=" * 60, file=sys.stderr)
    print("Setup Complete!", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    sources_status = check_all_sources()
    index_exists = (INDEX_DIR / "mpep_index.faiss").exists()

    print("\nFinal status:", file=sys.stderr)
    print(f"  MPEP PDFs: ✓ ({check_mpep_pdfs()} files)", file=sys.stderr)
    print(
        "  35 USC:    ✓" if sources_status["35_usc"] else "  35 USC:    ✗",
        file=sys.stderr,
    )
    print(
        "  37 CFR:    ✓" if sources_status["37_cfr"] else "  37 CFR:    ✗",
        file=sys.stderr,
    )
    print(
        "  Updates:   ✓" if sources_status["subsequent_pubs"] else "  Updates:   ✗",
        file=sys.stderr,
    )
    print("  Index:     ✓" if index_exists else "  Index:     ✗", file=sys.stderr)
    print(
        f"  MCP:       {'✓' if mcp_configured else '⚠ Manual setup required'}",
        file=sys.stderr,
    )

    if mcp_configured:
        print("\nClaude Code Integration:", file=sys.stderr)
        print("  ✓ MCP server registered (user scope)", file=sys.stderr)
        print("  ✓ Available from any directory", file=sys.stderr)
        print("\n  Restart Claude Code, then try:", file=sys.stderr)
        print("    'Search MPEP for claim indefiniteness requirements'", file=sys.stderr)
        print(
            "\n  Slash commands (.claude/commands/) work in this directory:",
            file=sys.stderr,
        )
        print("    /review-claims", file=sys.stderr)
        print("    /review-specification", file=sys.stderr)
        print("    /review-formalities", file=sys.stderr)
        print("    /full-review", file=sys.stderr)
    else:
        print("\n⚠ MCP server auto-registration failed", file=sys.stderr)
        print("  See manual registration command above", file=sys.stderr)

    print("\nNext steps:", file=sys.stderr)
    print("  2. Run: patent-reviewer download-patents", file=sys.stderr)
    print("     (Downloads 9.2M+ patents for local prior art search)", file=sys.stderr)
    print("\n  OR", file=sys.stderr)
    print("\n  2. Get USPTO API key for live patent access:", file=sys.stderr)
    print("     a. Visit: https://data.uspto.gov/myodp", file=sys.stderr)
    print("     b. Create account and verify with ID.me", file=sys.stderr)
    print("     c. Copy your API key from the portal", file=sys.stderr)
    print("     d. Set environment variable:", file=sys.stderr)
    print('        Windows: $env:USPTO_API_KEY="your_key"', file=sys.stderr)
    print('        Linux/Mac: export USPTO_API_KEY="your_key"', file=sys.stderr)

    return 0


def run_server(args):
    """
    Run the MCP server
    """
    # Check if setup has been run
    sources_status = check_all_sources()
    index_exists = (INDEX_DIR / "mpep_index.faiss").exists()

    if not sources_status["mpep"] or not index_exists:
        print(
            "\n✗ Setup not complete. Run 'patent-reviewer setup' first.",
            file=sys.stderr,
        )
        return 1

    print("Initializing MPEP index...", file=sys.stderr)

    global mpep_index
    use_hyde = not args.no_hyde
    mpep_index = MPEPIndex(use_hyde=use_hyde)
    mpep_index.build_index(force_rebuild=False)

    print("Starting MCP server...", file=sys.stderr)
    mcp.run()

    return 0


def status_command(args):
    """
    Show current installation status
    """
    sources_status = check_all_sources()
    pdf_count = check_mpep_pdfs()
    index_exists = (INDEX_DIR / "mpep_index.faiss").exists()

    print("\nUtility Patent Reviewer Status", file=sys.stderr)
    print("=" * 40, file=sys.stderr)

    # GPU Status
    import torch

    print("\nHardware:", file=sys.stderr)
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"  GPU:       ✓ {gpu_name}", file=sys.stderr)
        print(f"  Memory:    {gpu_memory:.1f} GB", file=sys.stderr)
    else:
        print("  GPU:       ✗ Not available (using CPU)", file=sys.stderr)

    print("\nSources:", file=sys.stderr)
    print(
        f"  MPEP PDFs: {'✓' if sources_status['mpep'] else '✗'} ({pdf_count} files)",
        file=sys.stderr,
    )
    print(f"  35 USC:    {'✓' if sources_status['35_usc'] else '✗'}", file=sys.stderr)
    print(f"  37 CFR:    {'✓' if sources_status['37_cfr'] else '✗'}", file=sys.stderr)
    print(
        f"  Updates:   {'✓' if sources_status['subsequent_pubs'] else '✗'}",
        file=sys.stderr,
    )

    print("\nIndex:", file=sys.stderr)
    print(f"  Built:     {'✓' if index_exists else '✗'}", file=sys.stderr)

    if index_exists:
        metadata_file = INDEX_DIR / "mpep_metadata.json"
        if metadata_file.exists():
            import json

            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"  Chunks:    {len(data['chunks']):,}", file=sys.stderr)
                print(
                    f"  Sections:  {len(set(m['section'] for m in data['metadata'])):,}",
                    file=sys.stderr,
                )

    print("\nStorage:", file=sys.stderr)
    print(f"  Location:  {MPEP_DIR.absolute()}", file=sys.stderr)
    print(f"  Index dir: {INDEX_DIR.absolute()}", file=sys.stderr)

    ready = sources_status["mpep"] and index_exists
    print(f"\nStatus: {'Ready' if ready else 'Setup required'}", file=sys.stderr)

    if not ready:
        print("\nRun 'patent-reviewer setup' to complete installation.", file=sys.stderr)

    return 0


def download_patents_command(args):
    """
    Download PatentsView patent corpus for prior art search
    """
    print("\n" + "=" * 60, file=sys.stderr)
    print("PatentsView Patent Corpus Download", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("\nData source: PatentsView (https://patentsview.org)", file=sys.stderr)
    print("Coverage: 9.2+ million granted patents since 1976", file=sys.stderr)

    downloader = PatentCorpusDownloader()

    # Download patents
    include_optional = not args.no_optional
    print("\nDownloading patent corpus...", file=sys.stderr)
    print(
        f"Include claims & descriptions: {'Yes' if include_optional else 'No'}",
        file=sys.stderr,
    )
    if args.max_size:
        print(f"Size limit: {args.max_size} GB", file=sys.stderr)

    success = downloader.download_corpus(
        include_optional=include_optional, max_size_gb=args.max_size
    )

    if not success:
        print("\n✗ Download failed", file=sys.stderr)
        return 1

    # Show what was downloaded
    status = check_patent_corpus_status()
    print(
        f"\n✓ Downloaded {status['files_downloaded']} files ({status['total_size_gb']:.2f} GB)",
        file=sys.stderr,
    )

    # Build index if requested
    if args.build_index:
        print("\n" + "=" * 60, file=sys.stderr)
        print("Building Patent Corpus Index", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        patent_index = PatentCorpusIndex(use_hyde=not args.no_hyde)
        patent_index.build_index(
            force_rebuild=True,
            start_year=getattr(args, "start_year", None),
            end_year=getattr(args, "end_year", None),
        )

        print("\n✓ Patent corpus ready for prior art search", file=sys.stderr)
    else:
        print("\nTo build the search index, run:", file=sys.stderr)
        print("  patent-reviewer build-patent-index", file=sys.stderr)

    return 0


def build_patent_index_command(args):
    """
    Build or rebuild patent corpus search index
    """
    print("\n" + "=" * 60, file=sys.stderr)
    print("Building Patent Corpus Index", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # Check if corpus exists
    status = check_patent_corpus_status()
    if status["files_downloaded"] == 0:
        print("\n✗ No patent corpus downloaded", file=sys.stderr)
        print("Run 'patent-reviewer download-patents' first", file=sys.stderr)
        return 1

    print(
        f"\nFound {status['files_downloaded']} files ({status['total_size_gb']:.2f} GB)",
        file=sys.stderr,
    )
    print(f"Data source: {status['data_source']}", file=sys.stderr)

    # Show year range if specified
    if args.start_year or args.end_year:
        year_range = f"{args.start_year or 'earliest'} to {args.end_year or 'latest'}"
        print(f"\n📅 Year filter: {year_range}", file=sys.stderr)
        print("Only patents within this range will be indexed", file=sys.stderr)

    # Build index
    patent_index = PatentCorpusIndex(use_hyde=not args.no_hyde)
    patent_index.build_index(
        force_rebuild=args.rebuild, start_year=args.start_year, end_year=args.end_year
    )

    print("\n✓ Patent corpus index ready", file=sys.stderr)

    return 0


def patents_status_command(args):
    """
    Show patent corpus status
    """
    print("\n" + "=" * 60, file=sys.stderr)
    print("Patent Corpus Status", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # GPU Status
    import torch

    print("\nHardware:", file=sys.stderr)
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"  GPU:       ✓ {gpu_name}", file=sys.stderr)
        print(f"  Memory:    {gpu_memory:.1f} GB", file=sys.stderr)
    else:
        print("  GPU:       ✗ Not available (using CPU)", file=sys.stderr)

    # Check corpus status
    status = check_patent_corpus_status()

    print(f"\nData Source: {status.get('data_source', 'Unknown')}", file=sys.stderr)
    print(f"Downloaded Files: {status['files_downloaded']}", file=sys.stderr)
    print(f"Total Size: {status['total_size_gb']:.2f} GB", file=sys.stderr)
    print(f"Location: {status['corpus_dir']}", file=sys.stderr)

    # Check index status
    index_exists = (PATENT_INDEX_DIR / "patent_index.faiss").exists()
    print(f"\nIndex Built: {'✓' if index_exists else '✗'}", file=sys.stderr)

    if index_exists:
        metadata_file = PATENT_INDEX_DIR / "patent_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                num_chunks = len(data["chunks"])
                num_patents = len(set(m["patent_id"] for m in data["metadata"]))
                print(f"  Patents: {num_patents:,}", file=sys.stderr)
                print(f"  Chunks: {num_chunks:,}", file=sys.stderr)

    print(f"\nIndex Location: {PATENT_INDEX_DIR}", file=sys.stderr)

    # Status summary
    ready = status["files_downloaded"] > 0 and index_exists
    print(
        f"\nStatus: {'Ready for prior art search' if ready else 'Setup required'}",
        file=sys.stderr,
    )

    if not ready:
        if status["files_downloaded"] == 0:
            print(
                "\nRun 'patent-reviewer download-patents' to download corpus",
                file=sys.stderr,
            )
        elif not index_exists:
            print(
                "\nRun 'patent-reviewer build-patent-index' to build search index",
                file=sys.stderr,
            )

    return 0


def verify_config_command(args):
    """Verify Claude Code MCP configuration"""
    print("\n" + "=" * 70, file=sys.stderr)
    print("Claude Code MCP Configuration Verification", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    # Determine config file location
    home_dir = Path.home()
    config_path = home_dir / ".claude.json"

    # Get expected paths
    project_root = Path(__file__).parent.parent.resolve()
    expected_python = Path(sys.executable).resolve()
    expected_server = (project_root / "mcp_server" / "server.py").resolve()

    print(f"\nExpected Configuration:", file=sys.stderr)
    print(f"  Python: {expected_python}", file=sys.stderr)
    print(f"  Server: {expected_server}", file=sys.stderr)
    print(f"  Config: {config_path}", file=sys.stderr)

    # Check if paths exist
    print(f"\nPath Verification:", file=sys.stderr)
    if expected_python.exists():
        print(f"  ✓ Python executable found", file=sys.stderr)
    else:
        print(f"  ✗ Python executable NOT found: {expected_python}", file=sys.stderr)

    if expected_server.exists():
        print(f"  ✓ Server script found", file=sys.stderr)
    else:
        print(f"  ✗ Server script NOT found: {expected_server}", file=sys.stderr)

    # Check Claude config
    print(f"\nClaude Configuration:", file=sys.stderr)
    if not config_path.exists():
        print(f"  ✗ Config file not found: {config_path}", file=sys.stderr)
        print(
            f"\n  Run 'patent-reviewer setup' or 'python install.py' to create it", file=sys.stderr
        )
        return 1

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        if "mcpServers" not in config:
            print(f"  ✗ No 'mcpServers' section found", file=sys.stderr)
            return 1

        if "utility-patent-reviewer" not in config["mcpServers"]:
            print(f"  ✗ 'utility-patent-reviewer' server not registered", file=sys.stderr)
            print(f"\n  Run: python install.py", file=sys.stderr)
            return 1

        server_config = config["mcpServers"]["utility-patent-reviewer"]
        actual_python = server_config.get("command", "")
        actual_args = server_config.get("args", [])
        actual_server = actual_args[0] if actual_args else ""

        print(f"  ✓ Configuration found", file=sys.stderr)
        print(f"\nActual Configuration:", file=sys.stderr)
        print(f"  Python: {actual_python}", file=sys.stderr)
        print(f"  Server: {actual_server}", file=sys.stderr)

        # Normalize paths for comparison (handle forward/backslash differences)
        def normalize_path(p):
            return str(Path(p).resolve()).lower() if p else ""

        expected_python_norm = normalize_path(expected_python)
        expected_server_norm = normalize_path(expected_server)
        actual_python_norm = normalize_path(actual_python)
        actual_server_norm = normalize_path(actual_server)

        print(f"\nConfiguration Status:", file=sys.stderr)

        python_match = expected_python_norm == actual_python_norm
        server_match = expected_server_norm == actual_server_norm

        if python_match:
            print(f"  ✓ Python path is correct", file=sys.stderr)
        else:
            print(f"  ✗ Python path mismatch!", file=sys.stderr)
            print(f"    Expected: {expected_python}", file=sys.stderr)
            print(f"    Actual:   {actual_python}", file=sys.stderr)

        if server_match:
            print(f"  ✓ Server path is correct", file=sys.stderr)
        else:
            print(f"  ✗ Server path mismatch!", file=sys.stderr)
            print(f"    Expected: {expected_server}", file=sys.stderr)
            print(f"    Actual:   {actual_server}", file=sys.stderr)

        if python_match and server_match:
            print(f"\n✓ Configuration is correct!", file=sys.stderr)
            print(f"\nIf the server still fails:", file=sys.stderr)
            print(f"  1. Restart Claude Code", file=sys.stderr)
            print(f"  2. Check logs in Claude Code", file=sys.stderr)
            print(f"  3. Try: claude mcp list", file=sys.stderr)
            return 0
        else:
            print(f"\n✗ Configuration needs to be fixed!", file=sys.stderr)
            print(f"\nTo fix:", file=sys.stderr)
            print(f"  Option 1: Run 'python install.py' to re-register", file=sys.stderr)
            print(f"  Option 2: Manually edit {config_path}", file=sys.stderr)
            print(f"\nCorrect values:", file=sys.stderr)
            print(f'  "command": "{expected_python.as_posix()}"', file=sys.stderr)
            print(f'  "args": ["{expected_server.as_posix()}"]', file=sys.stderr)
            return 1

    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON in config file: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"  ✗ Error reading config: {e}", file=sys.stderr)
        return 1


def main():
    """
    Main CLI entry point
    """
    parser = argparse.ArgumentParser(
        description="Utility Patent Reviewer - Examiner-level patent analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  patent-reviewer setup                    # Setup MPEP/USC/CFR sources
  patent-reviewer status                   # Show MPEP installation status
  patent-reviewer verify-config            # Verify Claude Code configuration
  patent-reviewer serve                    # Run the MCP server

  patent-reviewer download-patents         # Download PatentsView corpus (all 9.2M+ patents)
  patent-reviewer download-patents --max-size 10  # Limit to 10 GB
  patent-reviewer download-patents --no-optional  # Skip claims & descriptions (faster)
  patent-reviewer build-patent-index       # Build patent search index
  patent-reviewer patents-status           # Show patent corpus status

For more information: https://github.com/RobThePCGuy/utility-patent-reviewer
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Download sources and build index")
    setup_parser.add_argument("--rebuild", action="store_true", help="Force rebuild of index")
    setup_parser.add_argument("--no-hyde", action="store_true", help="Disable HyDE query expansion")
    setup_parser.set_defaults(func=setup_command)

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Run the MCP server")
    serve_parser.add_argument("--no-hyde", action="store_true", help="Disable HyDE query expansion")
    serve_parser.set_defaults(func=run_server)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show installation status")
    status_parser.set_defaults(func=status_command)

    # Verify config command
    verify_parser = subparsers.add_parser(
        "verify-config", help="Verify Claude Code MCP configuration"
    )
    verify_parser.set_defaults(func=verify_config_command)

    # Download patents command
    download_patents_parser = subparsers.add_parser(
        "download-patents",
        help="Download PatentsView patent corpus for prior art search",
    )
    download_patents_parser.add_argument(
        "--no-optional",
        action="store_true",
        help="Skip optional large files (claims, descriptions)",
    )
    download_patents_parser.add_argument(
        "--max-size",
        type=float,
        default=None,
        help="Maximum storage in GB (default: unlimited)",
    )
    download_patents_parser.add_argument(
        "--build-index", action="store_true", help="Build search index after download"
    )
    download_patents_parser.add_argument(
        "--no-hyde", action="store_true", help="Disable HyDE query expansion"
    )
    download_patents_parser.add_argument(
        "--start-year",
        type=int,
        default=None,
        help="Only index patents from this year onwards (e.g., 2020)",
    )
    download_patents_parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        help="Only index patents up to this year (e.g., 2025)",
    )
    download_patents_parser.set_defaults(func=download_patents_command)

    # Build patent index command
    build_index_parser = subparsers.add_parser(
        "build-patent-index", help="Build or rebuild patent corpus search index"
    )
    build_index_parser.add_argument("--rebuild", action="store_true", help="Force rebuild of index")
    build_index_parser.add_argument(
        "--no-hyde", action="store_true", help="Disable HyDE query expansion"
    )
    build_index_parser.add_argument(
        "--start-year",
        type=int,
        default=None,
        help="Only index patents from this year onwards (e.g., 2020)",
    )
    build_index_parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        help="Only index patents up to this year (e.g., 2025)",
    )
    build_index_parser.set_defaults(func=build_patent_index_command)

    # Patents status command
    patents_status_parser = subparsers.add_parser(
        "patents-status", help="Show patent corpus status"
    )
    patents_status_parser.set_defaults(func=patents_status_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Run the selected command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
