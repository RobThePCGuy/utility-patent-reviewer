#!/usr/bin/env python3
"""
Simplified Setup for Utility Patent Reviewer
One command installation and setup

REQUIREMENTS:
- Python 3.9+ must be installed
- Virtual environment must be created and activated BEFORE running this script

NOTE: After installation, Claude Code automatically manages the virtual environment.
      Manual activation is only needed for:
      - Running this install.py script
      - Manually updating dependencies with pip
      - Running direct CLI commands outside Claude Code
      - Troubleshooting or advanced operations

FEATURES:
- Auto-detects OS (Windows/Linux/macOS) and GPU (NVIDIA with CUDA)
- Installs PyTorch with correct CUDA version for GPU
- Downloads USPTO rules (MPEP, 35 USC, 37 CFR)
- Downloads 9.2M patent corpus for offline search - NOT RECOMMENDED
- Registers MCP server with Claude Code - automatic
- Offers PDF cleanup after indexing to save disk space

USAGE:
    # Step 1: Create and activate venv (required for running install.py)
    python -m venv venv
    venv\\Scripts\\activate  (Windows)
    source venv/bin/activate (Linux/macOS)

    # Step 2: Run installer
    python install.py

    # After installation, Claude Code handles venv automatically!

RECENT CHANGES:
- 2025-11-09: Add timeout handling to prevent indefinite hangs
- 2025-11-09: Auto-remove existing MCP registration before re-registering
- 2025-11-08: Fixed installation order - PyTorch installed BEFORE other deps
- 2025-11-08: Added package verification before MPEP download
- 2025-11-08: Auto-installs correct PyTorch for RTX 5090/5080 (CUDA 12.8)
- 2025-11-08: Fixed GPU detection using nvidia-smi with compute capability
- 2025-11-08: Auto-selects CUDA version based on GPU (12.4 or 12.8)
- 2025-11-08: PDFs now stored in pdfs/ directory (not project root)
- 2025-11-08: Added PDF cleanup prompt after successful indexing
"""

import os
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class Colors:
    """Terminal colors for output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(message):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def run_command(cmd, description, check=True, show_output=False):
    """Run shell command with pretty output (secure version without shell=True)"""
    try:
        print_info(f"{description}...")

        # Convert string command to list for secure execution
        if isinstance(cmd, str):
            # Use shlex.split for proper parsing, but handle Windows paths
            if sys.platform == "win32":
                # On Windows, use a simple split that preserves quoted paths
                cmd_list = []
                import re

                # Split on spaces but preserve quoted strings
                parts = re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', cmd)
                for part in parts:
                    # Remove quotes from parts
                    cmd_list.append(part.strip('"'))
            else:
                cmd_list = shlex.split(cmd)
        else:
            cmd_list = cmd

        if show_output:
            # For commands that need to show real-time output (like pip installs)
            result = subprocess.run(cmd_list, check=check)
            if result.returncode == 0:
                print_success(f"{description} complete")
                return True
            else:
                if check:
                    print_error(f"{description} failed")
                return False
        else:
            # For commands where we want to capture output
            result = subprocess.run(cmd_list, check=check, capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"{description} complete")
                return True
            else:
                if check:
                    print_error(f"{description} failed")
                    if result.stderr:
                        print(f"   {result.stderr[:200]}")
                return False
    except Exception as e:
        print_error(f"{description} failed: {e}")
        return False


def detect_environment():
    """Detect user's OS and hardware"""
    print_header("DETECTING YOUR ENVIRONMENT")

    env_info = {
        "os": platform.system(),
        "arch": platform.machine(),
        "python_version": sys.version.split()[0],
        "has_gpu": False,
        "gpu_type": None,
    }

    # Detect GPU using system tools (before PyTorch is installed)
    if env_info["os"] == "Windows":
        # Check for NVIDIA GPU using nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                env_info["has_gpu"] = True
                env_info["gpu_type"] = "NVIDIA"
                # Parse compute capability (e.g., "8.9" for RTX 4090, "12.0" for RTX 5090)
                output = result.stdout.strip()
                if "," in output:
                    compute_cap = output.split(",")[1].strip()
                    env_info["compute_capability"] = float(compute_cap)
        except subprocess.TimeoutExpired:
            print_warning("nvidia-smi timed out - GPU detection skipped")
        except Exception:
            pass
    elif env_info["os"] == "Linux":
        # Try nvidia-smi first
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,compute_cap", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                env_info["has_gpu"] = True
                env_info["gpu_type"] = "NVIDIA"
                # Parse compute capability
                output = result.stdout.strip()
                if "," in output:
                    compute_cap = output.split(",")[1].strip()
                    env_info["compute_capability"] = float(compute_cap)
        except subprocess.TimeoutExpired:
            print_warning("nvidia-smi timed out - GPU detection skipped")
        except Exception:
            pass

        # Try detecting AMD GPU
        if not env_info["has_gpu"]:
            try:
                result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
                if "AMD" in result.stdout and "VGA" in result.stdout:
                    env_info["has_gpu"] = True
                    env_info["gpu_type"] = "AMD"
            except subprocess.TimeoutExpired:
                print_warning("lspci timed out - AMD GPU detection skipped")
            except Exception:
                pass

    print_success(f"OS: {env_info['os']}")
    print_success(f"Architecture: {env_info['arch']}")
    print_success(f"Python: {env_info['python_version']}")

    if env_info["has_gpu"]:
        gpu_msg = f"GPU: {env_info['gpu_type']} detected"
        if env_info.get("compute_capability"):
            gpu_msg += f" (Compute {env_info['compute_capability']})"
        print_success(gpu_msg)

        # RTX 5090/5080 need CUDA 12.8, older GPUs use CUDA 12.4
        if env_info.get("compute_capability", 0) >= 10.0:
            print_info("RTX 5090/5080 detected - will install PyTorch with CUDA 12.8")
            env_info["cuda_version"] = "cu128"
        else:
            env_info["cuda_version"] = "cu124"
    else:
        print_info("No GPU detected - will use CPU")

    return env_info


def check_virtual_environment():
    """Check if running inside a virtual environment"""
    print_header("CHECKING VIRTUAL ENVIRONMENT")

    # Check if we're in a virtual environment
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print_success("Virtual environment is active")
        return True
    else:
        print_error("Virtual environment is NOT active")
        print_info("")
        print_info("Please create and activate a virtual environment first:")
        print_info("(This is only required for running install.py)")
        print_info("")

        if platform.system() == "Windows":
            print_info("Windows (PowerShell):")
            print_info("  python -m venv venv")
            print_info("  venv\\Scripts\\activate")
        else:
            print_info("Linux/macOS:")
            print_info("  python3 -m venv venv")
            print_info("  source venv/bin/activate")

        print_info("")
        print_info("Then run this installer again:")
        print_info("  python install.py")
        print_info("")
        print_info("After installation, Claude Code will manage the venv automatically!")
        return False


def get_venv_python():
    """Get path to Python executable in virtual environment"""
    # Since we're running inside the venv, just use the current Python
    return sys.executable


def install_dependencies(env_info):
    """Install required Python packages with optimal configuration

    Order matters:
    1. Install PyTorch with correct CUDA version FIRST
    2. Then install package dependencies (won't reinstall torch)
    3. Verify all imports work before proceeding
    """
    print_header("INSTALLING DEPENDENCIES")

    venv_python = get_venv_python()

    # Upgrade pip first
    print_info("Installing core dependencies...")
    if not run_command(
        f'"{venv_python}" -m pip install --upgrade pip',
        "Upgrading pip",
        show_output=True,
    ):
        return False

    # Install PyTorch FIRST with correct CUDA version to avoid CPU version being installed by dependencies
    if env_info["has_gpu"] and env_info["gpu_type"] == "NVIDIA":
        cuda_ver = env_info.get("cuda_version", "cu124")
        # Extract CUDA version from cu124 -> 12.4 or cu128 -> 12.8
        cuda_display = f"{cuda_ver[2:4]}.{cuda_ver[4:]}" if len(cuda_ver) == 5 else cuda_ver[2:]
        print_info(f"Installing PyTorch with CUDA {cuda_display}...")
        if not run_command(
            f'"{venv_python}" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/{cuda_ver}',
            f"Installing PyTorch with CUDA {cuda_display}",
            show_output=True,
        ):
            print_error("Failed to install PyTorch with CUDA")
            return False
    else:
        print_info("Installing PyTorch (CPU)...")
        if not run_command(
            f'"{venv_python}" -m pip install torch torchvision torchaudio',
            "Installing PyTorch (CPU)",
            show_output=True,
        ):
            print_error("Failed to install PyTorch")
            return False

    # Now install the rest of the package (won't reinstall torch since it's already there)
    print_info("Installing remaining dependencies...")
    if not run_command(
        f'"{venv_python}" -m pip install -e .',
        "Installing package dependencies",
        show_output=True,
    ):
        return False

    # No need to force reinstall - compatible versions are specified in pyproject.toml

    # Verify critical imports work
    print_info("Verifying installations...")

    # Test each import separately for better error reporting
    test_imports = [
        ("torch", "PyTorch"),
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
        ("numpy", "NumPy"),
    ]

    all_ok = True
    for module, name in test_imports:
        # Use list-based command to avoid shell=True security risk
        verify_cmd = [str(venv_python), "-c", f"import {module}; print('OK')"]
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"{name} import failed")
            if result.stderr:
                # Show full error for debugging
                error_lines = result.stderr.strip().split("\n")
                for line in error_lines[-10:]:  # Last 10 lines
                    print(f"   {line}")
            all_ok = False
        else:
            print_success(f"{name} verified")

    if not all_ok:
        print_error("Some packages failed verification")
        print_info("")
        print_info("This usually means conflicting package versions.")
        print_info("To fix:")
        print_info("  1. Delete the venv directory: rmdir /s venv")
        print_info("  2. Create fresh venv: python -m venv venv")
        print_info("  3. Activate: venv\\Scripts\\activate")
        print_info("  4. Run installer again: python install.py")
        return False

    print_success("All dependencies installed and verified")
    return True


def download_mpep_data():
    """Download and index MPEP data"""
    print_header("DOWNLOADING USPTO EXAMINATION RULES")
    print_info("This will download MPEP, 35 USC, and 37 CFR (~500MB)")
    print_info("Takes about 5-10 minutes depending on your internet speed")

    venv_python = get_venv_python()

    response = input("\nDownload now? (y/n): ").lower()
    if response == "y":
        if run_command(
            f'"{venv_python}" -m mcp_server.cli setup',
            "Downloading MPEP data",
            show_output=True,
        ):
            print_success("USPTO examination rules downloaded and indexed")
            return True
    else:
        print_warning("Skipped MPEP download - you can run 'patent-reviewer setup' later")
    return False


def download_patent_corpus():
    """Download patent corpus for prior art search"""
    print_header("DOWNLOADING PATENT DATABASE (OPTIONAL)")
    print_info("Download 9.2+ million patents for prior art search")
    print_info("Size: ~13GB | Time: 5-60 minutes | Indexing: ~27 hours on RTX 5090 GPU")
    print_info("")
    print_info("Note: THIS METHOD IS NOT RECOMMENDED. Instead use USPTO's live database")
    print_info("      The local corpus provides faster offline semantic search,")
    print_info("      however, the compute time generating the index is INSANE!")

    venv_python = get_venv_python()

    response = input("\nDownload patent corpus now? (y/n): ").lower()
    if response == "y":
        if run_command(
            f'"{venv_python}" -m mcp_server.cli download-patents',
            "Downloading patent corpus",
            check=False,
            show_output=True,
        ):
            print_success("Patent corpus downloaded")

            response = input(
                "\nBuild search index now? (Takes ~27 hours on RTX 5090 GPU) (y/n): "
            ).lower()
            if response == "y":
                run_command(
                    f'"{venv_python}" -m mcp_server.cli download-patents --build-index',
                    "Building search index (this will take a while)",
                    check=False,
                    show_output=True,
                )
            else:
                print_info(
                    "Skipped index build - run 'patent-reviewer download-patents --build-index' later"
                )
            return True
    else:
        print_info(
            "Skipped patent corpus - you can download later with 'patent-reviewer download-patents'"
        )
    return False


def install_graphviz():
    """Install Graphviz for diagram generation"""
    print_header("INSTALLING DIAGRAM TOOLS (OPTIONAL)")
    print_info("Graphviz enables generation of patent-style technical diagrams")

    response = input("\nInstall Graphviz? (y/n): ").lower()
    if response == "y":
        print_info("Attempting automatic installation...")
        run_command(
            f"{sys.executable} scripts/install_graphviz.py",
            "Installing Graphviz",
            check=False,
            show_output=True,
        )
    else:
        print_info("Skipped Graphviz - diagrams will not be available")
        print_info("You can install later by running: python scripts/install_graphviz.py")


def copy_claude_config():
    """Copy .claude directory to user's home directory for Claude Code

    This function selectively copies files and directories from the repository's
    .claude directory to the user's ~/.claude directory while preserving any
    additional user files that don't exist in the repository.

    Behavior:
    - For each entry in the repo's .claude directory:
      - If it is a directory: recursively copy and overwrite the target subdirectory
      - If it is a file: overwrite the file in ~/.claude with the new one
    - All other files/directories in ~/.claude are preserved (not deleted)
    - Creates ~/.claude if it doesn't exist
    - Provides informative output on which files/directories were updated

    Returns:
        bool: True if successful, False otherwise
    """
    print_header("SETTING UP CLAUDE CODE INTEGRATION")

    project_root = Path(__file__).parent.resolve()
    source_claude = project_root / ".claude"

    # Determine user's home directory
    if platform.system() == "Windows":
        home_dir = Path(os.environ.get("USERPROFILE", Path.home()))
    else:
        home_dir = Path.home()

    dest_claude_base = home_dir / ".claude"

    if not source_claude.exists():
        print_warning(".claude directory not found in project")
        return False

    try:
        # Create destination .claude directory if it doesn't exist
        dest_claude_base.mkdir(parents=True, exist_ok=True)
        print_info(f"Using destination: {dest_claude_base}")

        # Track what we update for informative output
        updated_items = []

        # Iterate through each item in the source .claude directory
        for item in source_claude.iterdir():
            item_name = item.name
            dest_item = dest_claude_base / item_name

            if item.is_dir():
                # Handle directory: remove existing and copy fresh
                if dest_item.exists() and dest_item.is_dir():
                    shutil.rmtree(dest_item)
                    print_info(f"Removed existing directory: {item_name}/")
                elif dest_item.exists():
                    # Destination exists but is a file, remove it
                    dest_item.unlink()
                    print_info(f"Removed existing file (replacing with directory): {item_name}")

                # Copy the directory recursively
                shutil.copytree(item, dest_item)
                print_success(f"Copied directory: {item_name}/ to {dest_item}")
                updated_items.append(f"{item_name}/ (directory)")

            elif item.is_file():
                # Handle file: overwrite if exists
                if dest_item.exists():
                    print_info(f"Overwriting existing file: {item_name}")

                # Copy the file
                shutil.copy2(item, dest_item)
                print_success(f"Copied file: {item_name} to {dest_item}")
                updated_items.append(f"{item_name} (file)")

        # Summary output
        if updated_items:
            print_success(f"Claude Code configuration updated at: {dest_claude_base}")
            print_info(f"Updated {len(updated_items)} item(s):")
            for item in updated_items:
                print_info(f"  - {item}")
        else:
            print_warning("No items found to copy from .claude directory")

        print_info("")
        print_info("Available commands in Claude Code:")
        print_info("  /full-review - Complete patent application review")
        print_info("  /review-claims - Analyze claims only")
        print_info("  /review-specification - Check specification")
        print_info("  /review-formalities - Verify formalities")
        print_info("")
        print_info("Available skills:")
        print_info("  @patent-reviewer - USPTO rules and patent analysis")
        print_info("")
        print_info("Note: Your other files in ~/.claude are preserved")

        return True
    except PermissionError as e:
        print_error(f"Permission denied while copying Claude config: {e}")
        print_info("Try running with appropriate permissions or manually copy .claude directory")
        return False
    except OSError as e:
        print_error(f"OS error while copying Claude config: {e}")
        print_info("You can manually copy .claude to your home directory")
        return False
    except Exception as e:
        print_error(f"Failed to copy Claude config: {e}")
        print_info("You can manually copy .claude to your home directory")
        return False


def register_with_claude():
    """Register MCP server with Claude Code"""
    print_header("CONNECTING TO CLAUDE CODE")

    # Get absolute paths - use Path.resolve() to ensure clean absolute paths
    project_root = Path(__file__).parent.resolve()
    python_path = Path(get_venv_python()).resolve()  # sys.executable is already absolute
    server_path = (project_root / "mcp_server" / "server.py").resolve()

    # Verify paths exist
    if not python_path.exists():
        print_error(f"Python executable not found: {python_path}")
        return False

    if not server_path.exists():
        print_error(f"Server file not found: {server_path}")
        return False

    # Check if Claude Code CLI is available
    claude_cli = shutil.which("claude")
    if not claude_cli:
        print_error("Claude Code CLI not found")
        print_info("Please install Claude Code first: https://claude.com/code")
        return False

    # On Windows, Claude CLI requires git-bash
    if platform.system() == "Windows":
        bash_path = shutil.which("bash")
        if bash_path:
            # Set environment variable for Claude CLI to find git-bash
            os.environ["CLAUDE_CODE_GIT_BASH_PATH"] = bash_path
            print_info(f"Set CLAUDE_CODE_GIT_BASH_PATH to: {bash_path}")

    print_info("Registering MCP server...")
    print_info(f"Python: {python_path}")
    print_info(f"Server: {server_path}")

    # Convert to string with forward slashes for cross-platform compatibility
    # Claude CLI expects consistent path format
    python_str = str(python_path).replace("\\", "/")
    server_str = str(server_path).replace("\\", "/")

    # Remove existing registration if present to avoid "already exists" error
    try:
        subprocess.run(
            ["claude", "mcp", "remove", "utility-patent-reviewer"],
            capture_output=True,
            timeout=10,
        )
        print_info("Removed existing MCP server registration")
    except Exception:
        pass

    cmd = f'claude mcp add --transport stdio utility-patent-reviewer --scope user -- "{python_str}" "{server_str}"'

    if run_command(cmd, "Registering with Claude Code", check=False):
        print_success("Successfully registered with Claude Code")
        print_info("")
        print_info("Verify with: claude mcp list")
        print_info("")
        print_info("Expected configuration in ~/.claude.json:")
        print_info(f'  "command": "{python_str}"')
        print_info(f'  "args": ["{server_str}"]')
        print_info("")
        print_warning("IMPORTANT: If the server fails to start, check ~/.claude.json")
        print_warning(f"  Python path should be: {python_str}")
        print_warning(f"  Server path should be: {server_str}")
        return True
    else:
        print_error("Auto-registration failed")
        print_info("")
        print_info("Manual registration command:")
        print(f"\n{cmd}\n")
        print_info("")
        print_info("Or manually edit ~/.claude.json with:")
        print_info(f'  "command": "{python_str}"')
        print_info(f'  "args": ["{server_str}"]')
        return False


def main():
    """Main setup workflow"""
    print(
        f"""
{Colors.HEADER}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║           UTILITY PATENT REVIEWER SETUP                    ║
║           One-Command Installation                         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """
    )

    # Step 1: Check virtual environment
    if not check_virtual_environment():
        return 1

    # Step 2: Detect environment
    env_info = detect_environment()

    # Step 3: Install dependencies
    if not install_dependencies(env_info):
        print_error("Failed to install dependencies")
        return 1

    # Step 4: Download MPEP data
    download_mpep_data()

    # Step 5: Optional patent corpus
    download_patent_corpus()

    # Step 6: Optional Graphviz
    install_graphviz()

    # Step 7: Copy Claude Code configuration
    copy_claude_config()

    # Step 8: Register with Claude Code
    register_with_claude()

    # Done
    venv_activate_cmd = (
        "venv\\Scripts\\activate" if platform.system() == "Windows" else "source venv/bin/activate"
    )

    print(
        f"""
{Colors.OKGREEN}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                    SETUP COMPLETE! ✓                       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.OKCYAN}Next Steps:{Colors.ENDC}

1. {Colors.BOLD}Restart Claude Code{Colors.ENDC} (if it's running)

2. {Colors.BOLD}Try it out:{Colors.ENDC}
   • Open Claude Code
   • Ask: "Search MPEP for claim indefiniteness requirements"
   • Ask: "Review my patent claims for compliance"

3. {Colors.BOLD}Available commands:{Colors.ENDC}
   • /full-review        - Complete patent application review
   • /review-claims      - Analyze claims only
   • /review-specification - Check specification
   • /review-formalities - Verify formalities

{Colors.OKCYAN}Virtual Environment:{Colors.ENDC}
• Claude Code automatically manages the virtual environment for you
• Manual activation is only needed for advanced operations:
  - Running install.py directly
  - Manually updating dependencies with pip
  - Running troubleshooting scripts
  - Other direct CLI operations outside Claude Code
• To activate manually: {venv_activate_cmd}
• To deactivate: deactivate

{Colors.OKCYAN}Need Help?{Colors.ENDC}
• Documentation: See README.md
• Technical details: See ADVANCED-README.md
• GPU Setup: See GPU_SETUP.md
• Issues: https://github.com/RobThePCGuy/utility-patent-reviewer/issues

{Colors.BOLD}Happy patenting!{Colors.ENDC}
    """
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
