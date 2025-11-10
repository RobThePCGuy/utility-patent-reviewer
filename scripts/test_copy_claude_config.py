#!/usr/bin/env python3
"""
Test suite for copy_claude_config() function

Tests that the function:
1. Copies files and directories from repo's .claude to ~/.claude
2. Preserves user files in ~/.claude that don't exist in repo
3. Overwrites only the files/dirs that exist in repo
"""

import os
import shutil
import tempfile
from pathlib import Path
import sys

# Import the function to test
# We need to add the directory to the path
sys.path.insert(0, str(Path(__file__).parent))


# Mock the dependencies for testing
class MockColors:
    HEADER = ""
    OKBLUE = ""
    OKCYAN = ""
    OKGREEN = ""
    WARNING = ""
    FAIL = ""
    ENDC = ""
    BOLD = ""


def mock_print_header(msg):
    print(f"[HEADER] {msg}")


def mock_print_success(msg):
    print(f"[SUCCESS] {msg}")


def mock_print_error(msg):
    print(f"[ERROR] {msg}")


def mock_print_info(msg):
    print(f"[INFO] {msg}")


def mock_print_warning(msg):
    print(f"[WARNING] {msg}")


# Patch the module
import install  # noqa: E402

install.print_header = mock_print_header
install.print_success = mock_print_success
install.print_error = mock_print_error
install.print_info = mock_print_info
install.print_warning = mock_print_warning


def setup_test_environment():
    """Create temporary directories for testing"""
    # Create temp directory for the repo
    repo_dir = tempfile.mkdtemp(prefix="test_repo_")

    # Create temp directory for the home
    home_dir = tempfile.mkdtemp(prefix="test_home_")

    # Create .claude structure in repo
    repo_claude = Path(repo_dir) / ".claude"
    repo_claude.mkdir()

    # Create commands directory
    commands_dir = repo_claude / "commands"
    commands_dir.mkdir()
    (commands_dir / "full-review.md").write_text("# Full Review Command")
    (commands_dir / "review-claims.md").write_text("# Review Claims Command")

    # Create skills directory
    skills_dir = repo_claude / "skills"
    skills_dir.mkdir()
    skill_subdir = skills_dir / "patent-reviewer"
    skill_subdir.mkdir()
    (skill_subdir / "SKILL.md").write_text("# Patent Reviewer Skill")

    # Create CLAUDE.md file
    (repo_claude / "CLAUDE.md").write_text("# Claude Configuration\n\nThis is the main config.")

    return repo_dir, home_dir


def setup_existing_user_files(home_dir):
    """Create some existing user files in ~/.claude"""
    dest_claude = Path(home_dir) / ".claude"
    dest_claude.mkdir(exist_ok=True)

    # Create a custom user file
    (dest_claude / "my_custom_config.json").write_text('{"custom": "data"}')

    # Create a custom user directory
    custom_dir = dest_claude / "my_custom_commands"
    custom_dir.mkdir()
    (custom_dir / "custom_cmd.md").write_text("# My Custom Command")

    # Create old versions of files that should be overwritten
    (dest_claude / "CLAUDE.md").write_text("# Old Claude Configuration")

    old_commands = dest_claude / "commands"
    old_commands.mkdir()
    (old_commands / "old_command.md").write_text("# Old Command")

    return dest_claude


def test_basic_copy():
    """Test basic copying of .claude directory"""
    print("\n=== Test 1: Basic Copy ===")
    repo_dir, home_dir = setup_test_environment()

    try:
        # Patch the install module to use our test directories
        original_file = install.__file__
        install.__file__ = str(Path(repo_dir) / "install.py")

        # Patch platform and os.environ
        original_environ = os.environ.copy()
        os.environ["USERPROFILE"] = home_dir
        os.environ["HOME"] = home_dir

        # Run the function
        result = install.copy_claude_config()

        # Restore
        install.__file__ = original_file
        os.environ.clear()
        os.environ.update(original_environ)

        # Verify
        dest_claude = Path(home_dir) / ".claude"
        assert result is True, "Function should return True"
        assert dest_claude.exists(), "~/.claude should exist"
        assert (dest_claude / "CLAUDE.md").exists(), "CLAUDE.md should be copied"
        assert (dest_claude / "commands").is_dir(), "commands/ should be copied"
        assert (
            dest_claude / "commands" / "full-review.md"
        ).exists(), "commands/full-review.md should exist"
        assert (dest_claude / "skills").is_dir(), "skills/ should be copied"
        assert (
            dest_claude / "skills" / "patent-reviewer" / "SKILL.md"
        ).exists(), "skills/patent-reviewer/SKILL.md should exist"

        print("[PASS] Basic copy works correctly")

    finally:
        shutil.rmtree(repo_dir)
        shutil.rmtree(home_dir)


def test_preserve_user_files():
    """Test that user files are preserved"""
    print("\n=== Test 2: Preserve User Files ===")
    repo_dir, home_dir = setup_test_environment()

    try:
        # Setup existing user files
        dest_claude = setup_existing_user_files(home_dir)

        # Verify user files exist before
        assert (dest_claude / "my_custom_config.json").exists(), "User file should exist before"
        assert (dest_claude / "my_custom_commands").is_dir(), "User directory should exist before"

        # Patch the install module
        original_file = install.__file__
        install.__file__ = str(Path(repo_dir) / "install.py")

        original_environ = os.environ.copy()
        os.environ["USERPROFILE"] = home_dir
        os.environ["HOME"] = home_dir

        # Run the function
        result = install.copy_claude_config()

        # Restore
        install.__file__ = original_file
        os.environ.clear()
        os.environ.update(original_environ)

        # Verify user files are still there
        assert result is True, "Function should return True"
        assert (dest_claude / "my_custom_config.json").exists(), "User file should be preserved"
        assert (dest_claude / "my_custom_commands").is_dir(), "User directory should be preserved"
        assert (
            dest_claude / "my_custom_commands" / "custom_cmd.md"
        ).exists(), "User file in custom dir should be preserved"

        # Verify content of user file wasn't changed
        content = (dest_claude / "my_custom_config.json").read_text()
        assert content == '{"custom": "data"}', "User file content should be unchanged"

        print("[PASS] User files are preserved correctly")

    finally:
        shutil.rmtree(repo_dir)
        shutil.rmtree(home_dir)


def test_overwrite_existing():
    """Test that existing files/dirs from repo are overwritten"""
    print("\n=== Test 3: Overwrite Existing Files ===")
    repo_dir, home_dir = setup_test_environment()

    try:
        # Setup existing user files including old versions
        dest_claude = setup_existing_user_files(home_dir)

        # Verify old content
        old_content = (dest_claude / "CLAUDE.md").read_text()
        assert old_content == "# Old Claude Configuration", "Old CLAUDE.md should exist"
        assert (dest_claude / "commands" / "old_command.md").exists(), "Old command should exist"

        # Patch the install module
        original_file = install.__file__
        install.__file__ = str(Path(repo_dir) / "install.py")

        original_environ = os.environ.copy()
        os.environ["USERPROFILE"] = home_dir
        os.environ["HOME"] = home_dir

        # Run the function
        result = install.copy_claude_config()

        # Restore
        install.__file__ = original_file
        os.environ.clear()
        os.environ.update(original_environ)

        # Verify files were overwritten
        assert result is True, "Function should return True"

        # Check CLAUDE.md was overwritten
        new_content = (dest_claude / "CLAUDE.md").read_text()
        assert (
            new_content == "# Claude Configuration\n\nThis is the main config."
        ), "CLAUDE.md should be overwritten"

        # Check commands directory was replaced (old_command.md should be gone)
        assert not (
            dest_claude / "commands" / "old_command.md"
        ).exists(), "Old command should be removed"
        assert (dest_claude / "commands" / "full-review.md").exists(), "New commands should exist"

        print("[PASS] Existing files are overwritten correctly")

    finally:
        shutil.rmtree(repo_dir)
        shutil.rmtree(home_dir)


def test_no_source_directory():
    """Test handling when .claude directory doesn't exist in repo"""
    print("\n=== Test 4: No Source Directory ===")
    repo_dir = tempfile.mkdtemp(prefix="test_repo_")
    home_dir = tempfile.mkdtemp(prefix="test_home_")

    try:
        # Don't create .claude in repo

        # Patch the install module
        original_file = install.__file__
        install.__file__ = str(Path(repo_dir) / "install.py")

        original_environ = os.environ.copy()
        os.environ["USERPROFILE"] = home_dir
        os.environ["HOME"] = home_dir

        # Run the function
        result = install.copy_claude_config()

        # Restore
        install.__file__ = original_file
        os.environ.clear()
        os.environ.update(original_environ)

        # Verify
        assert result is False, "Function should return False when source doesn't exist"

        print("[PASS] Handles missing source directory correctly")

    finally:
        shutil.rmtree(repo_dir)
        shutil.rmtree(home_dir)


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing copy_claude_config() function")
    print("=" * 60)

    try:
        test_basic_copy()
        test_preserve_user_files()
        test_overwrite_existing()
        test_no_source_directory()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
