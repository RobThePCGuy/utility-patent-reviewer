#!/usr/bin/env python3
"""
Graphviz Installation Helper for utility-patent-reviewer
Run this script to check and install Graphviz on your system
"""

import sys
from pathlib import Path

# Script is in scripts/, go up to project root, then into mcp_server/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "mcp_server"))

from graphviz_installer import GraphvizInstaller  # noqa: E402


def main():
    print("=" * 60)
    print("Graphviz Installation Helper")
    print("utility-patent-reviewer MCP Server")
    print("=" * 60)
    print()

    installer = GraphvizInstaller()
    print(installer.get_diagnostic_info())
    print()

    if installer.status["ready"]:
        print("✓ Graphviz is ready to use!")
        print(f"  Version: {installer.status['version']}")
        print(f"  Location: {installer.status['dot_executable']}")
        return 0

    print("⚠ Graphviz is not properly installed.")
    print()

    response = input("Would you like to attempt automatic installation? (y/n): ")

    if response.lower() in ["y", "yes"]:
        print()
        print("Attempting automatic installation...")
        print()

        success, message = installer.try_auto_install()
        print(message)
        print()

        if success:
            print("✓ Installation completed!")
            print()
            print("IMPORTANT: You may need to restart your terminal or IDE")
            print("           for the changes to take effect.")
            return 0
        else:
            print("✗ Automatic installation failed or not available.")
            print()
            print("Please follow the manual installation instructions above.")
            return 1
    else:
        print()
        print("Manual installation required.")
        print("Please follow the instructions above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
