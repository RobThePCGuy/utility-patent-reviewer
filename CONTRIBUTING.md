# Contributing to Utility Patent Reviewer

Thank you for your interest in contributing to the Utility Patent Reviewer! This document provides guidelines and information for contributors.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Commit Messages](#commit-messages)
8. [Pull Request Process](#pull-request-process)
9. [Review Process](#review-process)
10. [Getting Help](#getting-help)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect:

- **Respectful communication** - Be considerate and constructive
- **Collaboration** - Work together toward common goals
- **Openness** - Welcome newcomers and different perspectives
- **Focus on the project** - Keep discussions professional and on-topic

### Unacceptable Behavior

- Harassment, discrimination, or personal attacks
- Publishing others' private information
- Trolling or deliberately derailing discussions
- Any conduct that violates professional standards

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- GitHub account
- Basic understanding of Python, vector search, or patent law (depending on contribution area)

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/utility-patent-reviewer.git
   cd utility-patent-reviewer
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/RobThePCGuy/utility-patent-reviewer.git
   ```

4. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   python install.py
   ```

6. **Verify installation:**
   ```bash
   patent-reviewer status
   ```

### Staying Updated

Keep your fork in sync with upstream:

```bash
git fetch upstream
git checkout dev
git merge upstream/dev
git push origin dev
```

---

## Development Workflow

### Branch Strategy

We use a two-branch workflow:

- **`master`** - Stable releases only
- **`dev`** - Active development (default branch)

### Creating a Feature Branch

1. **Always branch from `dev`:**
   ```bash
   git checkout dev
   git pull upstream dev
   git checkout -b feature/your-feature-name
   ```

2. **Branch naming conventions:**
   - Features: `feature/short-description`
   - Bug fixes: `bugfix/issue-number-description`
   - Documentation: `docs/description`
   - Performance: `perf/description`
   - Refactoring: `refactor/description`

   Examples:
   - `feature/add-european-patent-search`
   - `bugfix/123-fix-mpep-index-corruption`
   - `docs/improve-api-examples`

### Making Changes

1. **Write code** following our [Coding Standards](#coding-standards)

2. **Test your changes** thoroughly

3. **Commit frequently** with clear messages

4. **Keep commits focused** - one logical change per commit

### Before Submitting

1. **Update from dev:**
   ```bash
   git fetch upstream
   git rebase upstream/dev
   ```

2. **Run tests:**
   ```bash
   pytest
   ```

3. **Check code style:**
   ```bash
   ruff check .
   black --check .
   isort --check-only .
   ```

4. **Update documentation** if needed

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- **Line length:** 88 characters (Black default)
- **Quotes:** Double quotes for strings
- **Imports:** Organized with `isort`

### Code Formatting

We use automated formatters:

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .
```

### Linting

We use Ruff for fast Python linting:

```bash
# Run linter
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Dict, Any

def search_mpep(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search MPEP content for relevant passages.

    Args:
        query: Search query string
        top_k: Number of results to return

    Returns:
        List of result dictionaries with text and metadata
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int, param3: bool = False) -> dict:
    """One-line summary of what the function does.

    More detailed explanation if needed. Explain the purpose,
    behavior, and any important notes about usage.

    Args:
        param1: Description of param1
        param2: Description of param2
        param3: Description of param3. Defaults to False.

    Returns:
        Dictionary containing:
            - key1: Description
            - key2: Description

    Raises:
        ValueError: When param2 is negative
        RuntimeError: When external dependency fails

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result["key1"])
        'value'
    """
    pass
```

### Code Organization

- **Keep functions small** - ideally under 50 lines
- **One responsibility per function**
- **Use descriptive names** - no single-letter variables except loop counters
- **Add comments** for complex logic
- **Avoid magic numbers** - use named constants

### Error Handling

```python
# Good - specific exceptions with context
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"Index file not found: {e}")
    raise RuntimeError("MPEP index not built. Run: patent-reviewer setup") from e
except Exception as e:
    logger.exception("Unexpected error in operation")
    raise

# Bad - catch-all without context
try:
    result = risky_operation()
except Exception:
    pass
```

---

## Testing Guidelines

### Writing Tests

We use `pytest` for testing:

```python
def test_search_returns_results():
    """Test that search returns expected number of results."""
    searcher = MPEPSearcher()
    results = searcher.search("claim definiteness", top_k=5)

    assert len(results) == 5
    assert all("text" in r for r in results)
    assert all("section" in r for r in results)

def test_search_handles_empty_query():
    """Test that empty query raises ValueError."""
    searcher = MPEPSearcher()

    with pytest.raises(ValueError, match="Query cannot be empty"):
        searcher.search("")
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mpep_search.py

# Run with coverage
pytest --cov=mcp_server --cov-report=html

# Run verbose
pytest -v

# Run specific test
pytest tests/test_mpep_search.py::test_search_returns_results
```

### Test Coverage

- Aim for 80%+ coverage for new code
- Test both success and failure cases
- Test edge cases and error handling
- Mock external dependencies (APIs, file I/O)

### Testing Checklist

When adding new features, ensure:

- [ ] Unit tests for individual functions
- [ ] Integration tests for workflows
- [ ] Error handling tested
- [ ] Edge cases covered
- [ ] Tests pass on all supported Python versions (3.9-3.12)
- [ ] Tests pass on all supported platforms (Windows, Linux, macOS)

---

## Documentation

### When to Update Documentation

Update documentation when you:

- Add new features
- Change existing behavior
- Fix bugs that affect usage
- Add configuration options
- Change APIs or interfaces

### Documentation Files

- **README.md** - User-facing documentation, setup, and usage
- **ADVANCED-README.md** - Technical details, API reference
- **docs/** - Specific topics (API setup, GPU configuration, etc.)
- **Docstrings** - Function and class documentation
- **CHANGELOG.md** - Record of notable changes (if exists)

### Writing Good Documentation

- **Be clear and concise**
- **Include examples**
- **Use headings and formatting**
- **Keep it up to date**
- **Test instructions yourself**

### Documentation Checklist

- [ ] README.md updated if needed
- [ ] ADVANCED-README.md updated if needed
- [ ] Docstrings added to new functions/classes
- [ ] Examples included
- [ ] Configuration options documented
- [ ] Error messages explained

---

## Commit Messages

### Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation only
- **style:** Formatting, whitespace, etc.
- **refactor:** Code change that neither fixes a bug nor adds a feature
- **perf:** Performance improvement
- **test:** Adding or updating tests
- **chore:** Maintenance tasks, dependency updates

### Examples

```bash
# Feature
feat(search): add support for European Patent Office data

Implement EPO patent search using Espacenet API. Includes:
- API client with rate limiting
- Result normalization to match USPTO format
- Error handling and retries

Closes #123

# Bug fix
fix(index): prevent corruption when building on network drive

Check if path is network drive and copy to local temp directory
before building FAISS index to prevent corruption.

Fixes #456

# Documentation
docs(api): add examples for USPTO API configuration

Add step-by-step guide with screenshots for obtaining and
configuring USPTO API key.
```

### Commit Best Practices

- **Write clear, descriptive subjects** (50 chars or less)
- **Use imperative mood** ("add" not "added" or "adds")
- **Capitalize first letter**
- **No period at the end of subject**
- **Explain what and why** in the body, not how
- **Reference issues** when applicable

---

## Pull Request Process

### Before Opening a PR

1. **Ensure your branch is up to date:**
   ```bash
   git fetch upstream
   git rebase upstream/dev
   ```

2. **Run all checks:**
   ```bash
   pytest
   ruff check .
   black --check .
   isort --check-only .
   ```

3. **Update documentation**

4. **Test on your system** thoroughly

### Opening a Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open PR on GitHub:**
   - Go to your fork on GitHub
   - Click "Pull Request"
   - **Target branch:** `dev` (not `master`)
   - Fill out the PR template completely

3. **PR Title:** Follow commit message format
   - Good: `feat(search): add European Patent Office support`
   - Bad: `updated stuff`

4. **Description:** Explain:
   - What changed
   - Why it changed
   - How to test it
   - Any breaking changes

### After Opening

- **Respond to feedback** promptly
- **Make requested changes** in new commits
- **Don't force-push** after review starts (unless requested)
- **Ask questions** if feedback is unclear
- **Be patient** - reviews may take a few days

### PR Checklist

The PR template includes a checklist. Ensure all items are completed:

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Dependent changes merged

---

## Review Process

### For Contributors

**What to expect:**
- Initial review within 3-5 days
- Constructive feedback on code quality, design, and testing
- Requests for changes or clarification
- Approval when ready

**How to respond:**
- Address each comment
- Ask questions if unclear
- Make requested changes
- Push new commits (don't force-push)
- Mark conversations as resolved when fixed

### For Reviewers

**What to look for:**
- Code quality and maintainability
- Test coverage
- Documentation
- Security concerns
- Performance implications
- Breaking changes

**How to review:**
- Be constructive and respectful
- Explain the "why" behind suggestions
- Distinguish between "must fix" and "nice to have"
- Approve when ready
- Test locally for complex changes

---

## Getting Help

### Where to Ask

- **GitHub Discussions** - Questions, ideas, general discussion
- **Issues** - Bug reports, feature requests
- **Pull Request comments** - Questions about specific changes
- **Discord/Slack** - Real-time chat (if available)

### Before Asking

1. **Search existing issues/discussions**
2. **Check documentation**
3. **Try troubleshooting steps**
4. **Provide context and details**

### Asking Good Questions

Include:
- What you're trying to do
- What you've tried
- What happened vs. what you expected
- Error messages/logs
- Environment details (OS, Python version, etc.)

---

## Recognition

Contributors will be:
- Listed in the project's contributors
- Credited in release notes
- Mentioned in significant features

Thank you for contributing to making patent protection more accessible!

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Questions?

If anything in this guide is unclear, please open a Discussion or Issue!
