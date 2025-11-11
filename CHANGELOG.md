# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive GitHub Actions workflows for testing, linting, and releases
- Code quality checks with Ruff, Black, isort, and mypy
- Security scanning with CodeQL, Bandit, TruffleHog, and Safety
- Automated dependency updates via Dependabot
- Issue templates for bugs, features, and questions
- Pull request template with comprehensive checklist
- CODEOWNERS file for automated review requests
- CONTRIBUTING.md with detailed contribution guidelines
- SECURITY.md with security policy and disclosure process
- Documentation for USPTO and PatentsView API setup
- GPU setup documentation
- MCP server with MPEP RAG search capabilities
- Patent search functionality via multiple APIs
- Claude Code skills and commands for patent review

### Changed
- Repository structure organized with `.github/` folder
- Documentation reorganized into `docs/` directory

### Security
- API keys secured via environment variables
- Automated security scanning on all commits and PRs
- Branch protection enabled on master branch

## [1.0.0] - 2025-11-10

### Added
- Initial release
- MCP server implementation
- MPEP search functionality
- Patent corpus search (local)
- USPTO API integration
- PatentsView API integration
- Installation script (`install.py`)
- Test suite (`test_install.py`)
- Claude Code integration with skills and commands
- Patent review commands (`/review-claims`, `/review-specification`, `/full-review`)
- Patent creation command (`/create-patent`)
- Comprehensive documentation (README.md, ADVANCED-README.md)
- MIT License

### Features
- Vector-based MPEP search using FAISS
- Patent corpus search with semantic similarity
- USPTO Patent Examination Data System (PEDS) API support
- PatentsView API for prior art search
- Local-first architecture for privacy
- GPU acceleration support (optional)
- Cross-platform support (Windows, Linux, macOS)
- Python 3.9+ compatibility

### Documentation
- Setup and installation guide
- API configuration instructions
- GPU setup guide
- Environment variables documentation
- Examples and usage patterns
- Contributing guidelines
- Security policy

---

## Notes

### Categories
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

### Versioning
- **Major version** (X.0.0) - Breaking changes
- **Minor version** (0.X.0) - New features, backwards compatible
- **Patch version** (0.0.X) - Bug fixes, backwards compatible

### Links
[Unreleased]: https://github.com/RobThePCGuy/utility-patent-reviewer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/RobThePCGuy/utility-patent-reviewer/releases/tag/v1.0.0
