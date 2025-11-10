# GitHub Repository Settings Guide

Complete guide to configuring GitHub settings for the Utility Patent Reviewer project to promote collaboration while maintaining security.

---

## Table of Contents

1. [Branch Protection Rules](#branch-protection-rules)
2. [Collaborator Access](#collaborator-access)
3. [Security Settings](#security-settings)
4. [Repository Features](#repository-features)
5. [Merge Settings](#merge-settings)
6. [GitHub Actions & Automation](#github-actions--automation)
7. [Quick Setup Checklist](#quick-setup-checklist)

---

## Branch Protection Rules

Branch protection prevents accidental or unauthorized changes to important branches.

### Configure Protection for `master` Branch

**Path:** Settings → Branches → Add branch protection rule

**Branch name pattern:** `master`

**Recommended Settings:**

#### Protect matching branches
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1** (or 2 for higher security)
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (if CODEOWNERS file exists)

- ✅ **Require status checks to pass before merging** (if you have CI/CD)
  - ✅ Require branches to be up to date before merging
  - Add status checks: `tests`, `lint` (when you add them)

- ✅ **Require conversation resolution before merging**
  - Ensures all review comments are addressed

- ✅ **Require signed commits** (optional - higher security)
  - Only allow commits signed with verified GPG keys

- ✅ **Require linear history**
  - Prevents merge commits, forces rebase or squash

- ✅ **Include administrators**
  - Enforce all rules even for repository admins

#### Rules applied to everyone
- ✅ **Block force pushes**
  - Prevents history rewriting on master

- ✅ **Restrict deletions**
  - Prevents branch deletion

- ⚠️ **Restrict who can push to matching branches** (optional)
  - Only allow specific users/teams to push
  - Consider allowing "Maintainers" only

### Configure Protection for `dev` Branch

**Branch name pattern:** `dev`

**Recommended Settings:**

- ✅ **Require a pull request before merging**
  - ✅ Require approvals: **1**

- ✅ **Require conversation resolution before merging**

- ✅ **Allow force pushes** (for maintainers only)
  - Enables rebasing and history cleanup during development

- ✅ **Block deletions**

**Why less strict than master?**
- `dev` is for active development
- Allows more flexibility for experimentation
- Still requires review before merging

---

## Collaborator Access

**Path:** Settings → Collaborators and teams

### Access Level Recommendations

| Role | Access Level | Permissions |
|------|-------------|-------------|
| **Core Contributors** | Write | Push to branches, manage issues/PRs |
| **Code Reviewers** | Triage | Manage issues/PRs, cannot push code |
| **Maintainers** | Maintain | Manage settings, webhooks, branch protection |
| **Repository Owner** | Admin | Full access including deletion |

### Adding Collaborators

1. Click **Add people**
2. Enter GitHub username or email
3. Select role: **Write** (recommended starting point)
4. Send invitation

### Best Practices

- Start new contributors with **Write** access
- Use **branch protection** to require reviews (not direct pushes)
- Promote to **Maintain** after 5-10 quality contributions
- Reserve **Admin** for repository owner and 1-2 trusted maintainers

---

## Security Settings

**Path:** Settings → Code security and analysis

### Recommended Security Configuration

#### Dependency Graph
- ✅ **Enable** - Tracks your project dependencies
- Automatically enabled for public repos

#### Dependabot Alerts
- ✅ **Enable** - Notifies you of security vulnerabilities
- Configure: Settings → Notifications → Security alerts

#### Dependabot Security Updates
- ✅ **Enable** - Automatically creates PRs to fix vulnerabilities
- Review and merge these PRs promptly

#### Dependabot Version Updates (optional)
```yaml
# Create .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

#### Secret Scanning
- ✅ **Enable** (free for public repos)
- Detects API keys, tokens, passwords in commits
- Alerts you before pushing secrets

#### Code Scanning (GitHub Advanced Security)
- Available for public repos or GitHub Enterprise
- Runs CodeQL analysis on every push/PR
- ✅ **Enable** if available

### Environment Variables Security

**Never commit these files:**
- `.env` files (already in `.gitignore`)
- `.mcp.json` (already in `.gitignore`)
- API keys or tokens
- Private keys

**Use GitHub Secrets for CI/CD:**
- Settings → Secrets and variables → Actions
- Add: `USPTO_API_KEY`, `PATENTSVIEW_API_KEY`

---

## Repository Features

**Path:** Settings → General → Features

### Enable These Features

#### Issues
- ✅ **Enable Issues**
- Use for bug reports, feature requests, questions
- Configure issue templates (see below)

#### Discussions
- ✅ **Enable Discussions** (recommended)
- Use for Q&A, announcements, general discussion
- Keeps issues focused on actionable items

Categories:
- 💡 Ideas (feature requests)
- ❓ Q&A (questions)
- 📣 Announcements
- 🎉 Show and Tell (user showcases)

#### Projects
- ✅ **Enable Projects** (optional)
- Use for roadmap planning
- Kanban boards for organizing work

#### Wiki
- ⚠️ **Consider enabling** (optional)
- Alternative: Use `/docs` folder in repo (current approach - better!)
- Wikis are separate from main repo and harder to maintain

#### Sponsorships
- ⚠️ Optional - if you want to accept sponsorships
- Adds "Sponsor" button to repo

---

## Merge Settings

**Path:** Settings → General → Pull Requests

### Merge Options

Recommended configuration:

- ✅ **Allow merge commits**
  - Preserves full commit history
  - Use when: Multiple related commits should stay grouped

- ✅ **Allow squash merging** (recommended default)
  - Combines all PR commits into one
  - Use when: Cleaning up work-in-progress commits
  - Default commit message: PR title and description

- ✅ **Allow rebase merging**
  - Applies commits individually onto base branch
  - Use when: Maintaining linear history

**Recommended default:** Squash merging
- Keeps master/dev history clean
- Each PR = one commit
- Easy to revert features

### Automatic Branch Management

- ✅ **Automatically delete head branches**
  - Cleans up after PR merge
  - Keeps branch list manageable

- ✅ **Always suggest updating pull request branches**
  - Prompts to update PR when base branch changes
  - Reduces merge conflicts

- ⚠️ **Allow auto-merge** (optional)
  - PRs auto-merge when all checks pass
  - Use with caution - ensure good test coverage

### Pull Request Suggestions

- ✅ **Allow users to add branches that have no commits to pull requests**
  - Useful for work-in-progress PRs

---

## GitHub Actions & Automation

### Basic Testing Workflow

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ dev, master ]
  pull_request:
    branches: [ dev, master ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        if [ -f mcp_server/requirements.txt ]; then pip install -r mcp_server/requirements.txt; else echo "No requirements.txt"; fi

    - name: Run tests
      run: |
        pytest --cov=mcp_server --cov-report=xml || echo "No tests yet"

    - name: Upload coverage
      # Note: codecov/codecov-action@v4 may require a CODECOV_TOKEN. See https://github.com/codecov/codecov-action/releases for details.
      uses: codecov/codecov-action@v4
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
```

### Linting Workflow

Create `.github/workflows/lint.yml`:

```yaml
name: Lint

on:
  push:
    branches: [ dev, master ]
  pull_request:
    branches: [ dev, master ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install linters
      run: |
        pip install ruff black isort

    - name: Run Ruff
      run: ruff check .

    - name: Run Black
      run: black --check .

    - name: Run isort
      run: isort --check-only .
```

### Auto-assign Issues

Create `.github/workflows/auto-assign.yml`:

```yaml
name: Auto Assign

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  assign:
    runs-on: ubuntu-latest
    steps:
      - uses: kentaro-m/auto-assign-action@v1
        with:
          assignees: |
            - RobThePCGuy
```

---

## Quick Setup Checklist

Use this checklist to configure your repository:

### Security & Protection
- [ ] Enable branch protection on `master` (require 1-2 reviews)
- [ ] Enable branch protection on `dev` (require 1 review)
- [ ] Require conversation resolution before merging
- [ ] Block force pushes to `master`
- [ ] Enable Dependabot alerts
- [ ] Enable Dependabot security updates
- [ ] Enable secret scanning
- [ ] Add GitHub Actions secrets (USPTO_API_KEY, etc.)

### Collaboration Features
- [ ] Enable Issues
- [ ] Enable Discussions
- [ ] Create issue templates (bug, feature, question)
- [ ] Create PR template
- [ ] Create CONTRIBUTING.md
- [ ] Create CODEOWNERS file
- [ ] Add collaborators with appropriate access levels
- [ ] Configure issue labels

### Merge & Branch Management
- [ ] Enable squash merging (default)
- [ ] Enable automatically delete head branches
- [ ] Enable suggest updating PR branches
- [ ] Require linear history (optional)

### Repository Information
- [ ] Set repository description
- [ ] Add topics/tags for discoverability
- [ ] Set website URL
- [ ] Verify LICENSE file (MIT)
- [ ] Create SECURITY.md
- [ ] Add README badges (build status, license, etc.)

### Automation (Optional)
- [ ] Set up GitHub Actions for testing
- [ ] Set up linting workflow
- [ ] Set up auto-assign
- [ ] Configure Dependabot version updates

---

## Common Workflows

### For Collaborators: Contributing Code

1. **Fork** the repository (or create a branch if you have Write access)
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/utility-patent-reviewer.git`
3. **Create branch** from `dev`: `git checkout -b feature/your-feature-name`
4. **Make changes** and commit frequently
5. **Push** to your fork: `git push origin feature/your-feature-name`
6. **Open PR** targeting `dev` branch
7. **Address review feedback**
8. **Merge** after approval (maintainer will merge)

### For Maintainers: Reviewing PRs

1. **Read the description** - understand what and why
2. **Check out the branch** locally (optional):
   ```bash
   gh pr checkout 123
   ```
3. **Review code changes** - look for:
   - Code quality and style
   - Security issues
   - Test coverage
   - Documentation updates
4. **Test locally** if needed
5. **Leave comments** - be constructive and specific
6. **Request changes** or **Approve**
7. **Merge** using squash merge (default)

### For Maintainers: Release Process

1. Merge `dev` into `master`:
   ```bash
   git checkout master
   git merge dev --no-ff
   ```
2. Tag the release:
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```
3. Create GitHub Release:
   - Go to Releases → Draft new release
   - Select tag
   - Write release notes
   - Publish

---

## Additional Resources

- [GitHub Docs - Managing Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Docs - Repository Security](https://docs.github.com/en/code-security/getting-started/securing-your-repository)
- [GitHub Skills - Introduction to GitHub](https://skills.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message standard

---

## Questions?

If you need help configuring any of these settings, open a Discussion or Issue!
