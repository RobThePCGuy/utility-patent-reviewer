# GitHub Repository Setup - Quick Start Guide

This guide helps you quickly configure your GitHub repository for collaboration and protection.

---

## What Was Created

The following files have been added to help with GitHub collaboration:

### Documentation
- **docs/GITHUB_SETUP.md** - Complete guide to GitHub settings and configuration
- **CONTRIBUTING.md** - Contributor guidelines and development workflow
- **SECURITY.md** - Security policy and vulnerability reporting

### GitHub Templates
- **.github/pull_request_template.md** - Standard PR template
- **.github/ISSUE_TEMPLATE/bug_report.md** - Bug report template
- **.github/ISSUE_TEMPLATE/feature_request.md** - Feature request template
- **.github/ISSUE_TEMPLATE/question.md** - Question/help template
- **.github/ISSUE_TEMPLATE/config.yml** - Issue template configuration

### GitHub Configuration
- **.github/CODEOWNERS** - Automatic code review assignments

---

## Quick Setup (5 Minutes)

### Step 1: Commit and Push These Files

```bash
# Add all new files
git add .github/ docs/GITHUB_SETUP.md CONTRIBUTING.md SECURITY.md docs/GITHUB_QUICK_START.md

# Commit
git commit -m "docs: add GitHub collaboration and security documentation

- Add comprehensive GitHub setup guide
- Add PR and issue templates
- Add CONTRIBUTING.md with development workflow
- Add SECURITY.md with vulnerability reporting process
- Add CODEOWNERS for automatic review assignments"

# Push to GitHub
git push origin dev
```

### Step 2: Configure Branch Protection (2 minutes)

Go to: `Settings → Branches → Add branch protection rule`

**For `master` branch:**
1. Branch name pattern: `master`
2. Enable:
   - ✅ Require a pull request before merging (1-2 approvals)
   - ✅ Require conversation resolution
   - ✅ Block force pushes
   - ✅ Include administrators
3. Click "Create"

**For `dev` branch:**
1. Branch name pattern: `dev`
2. Enable:
   - ✅ Require a pull request before merging (1 approval)
   - ✅ Require conversation resolution
3. Click "Create"

### Step 3: Enable Security Features (1 minute)

Go to: `Settings → Code security and analysis`

Enable:
- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Secret scanning

### Step 4: Configure Repository Features (1 minute)

Go to: `Settings → General → Features`

Enable:
- ✅ Issues
- ✅ Discussions (recommended)
- ✅ Projects (optional)

### Step 5: Configure Merge Settings (1 minute)

Go to: `Settings → General → Pull Requests`

Enable:
- ✅ Allow squash merging (set as default)
- ✅ Allow merge commits
- ✅ Allow rebase merging
- ✅ Automatically delete head branches

---

## What Each File Does

### docs/GITHUB_SETUP.md
**Complete guide covering:**
- Branch protection rules
- Collaborator access levels
- Security settings
- Repository features
- GitHub Actions examples
- Step-by-step configuration

**When to read:** When setting up the repository or adding new collaborators

### CONTRIBUTING.md
**Developer guide covering:**
- Getting started with development
- Code standards and style
- Testing guidelines
- Commit message format
- Pull request process

**When to read:** Before making your first contribution

### SECURITY.md
**Security policy covering:**
- How to report vulnerabilities
- Security best practices
- API key management
- Known limitations
- Response timeline

**When to read:** When handling security issues or reviewing security practices

### Pull Request Template
**Automatically appears when creating PRs:**
- Description sections
- Type of change checklist
- Testing checklist
- Documentation checklist

**Benefit:** Ensures all PRs include necessary information

### Issue Templates
**Provides structured forms for:**
- Bug reports (with environment details)
- Feature requests (with use cases)
- Questions (with troubleshooting steps)

**Benefit:** Makes issues easier to understand and address

### CODEOWNERS
**Automatically requests reviews:**
- When files are modified in a PR
- From appropriate experts
- Based on file paths

**Benefit:** Ensures proper oversight of critical code

---

## Testing Your Setup

### Test Branch Protection

```bash
# Try to push directly to master (should fail)
git checkout master
echo "test" >> test.txt
git add test.txt
git commit -m "test"
git push origin master  # ❌ Should be blocked

# Proper workflow (should work)
git checkout dev
git checkout -b feature/test
git push origin feature/test
# Open PR on GitHub → should require review
```

### Test Issue Templates

1. Go to your repository on GitHub
2. Click "Issues" → "New issue"
3. You should see three template options:
   - Bug Report
   - Feature Request
   - Question or Help Needed
4. Also see links to Discussions and Documentation

### Test CODEOWNERS

1. Create a PR that modifies `.github/` files
2. You should be automatically requested as a reviewer
3. Check PR "Reviewers" section on the right

---

## For Collaborators

### How to Contribute

1. **Fork** the repository (or use a branch if you have Write access)

2. **Clone and setup:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/utility-patent-reviewer.git
   cd utility-patent-reviewer
   git checkout dev
   git checkout -b feature/your-feature
   ```

3. **Make changes** following CONTRIBUTING.md

4. **Open PR** targeting `dev` branch

5. **Address feedback** and get approval

6. **Merge** (maintainer will merge using squash)

### Access Levels

| Role | What You Can Do |
|------|-----------------|
| **Read** | View code, clone, open issues |
| **Triage** | Manage issues and PRs, no code changes |
| **Write** | Create branches, open PRs, need review to merge |
| **Maintain** | Manage settings, webhooks, branch protection |
| **Admin** | Full access including deletion |

**Most collaborators start with Write access.**

---

## Next Steps

### Optional Enhancements

1. **Add GitHub Actions** (automated testing)
   - See examples in docs/GITHUB_SETUP.md
   - Add `.github/workflows/tests.yml`
   - Add `.github/workflows/lint.yml`

2. **Create Project Board** (roadmap)
   - Go to Projects → New project
   - Choose "Board" template
   - Add columns: Backlog, In Progress, Review, Done

3. **Set up Discussions** (community)
   - Go to Settings → Features → Enable Discussions
   - Create categories:
     - 💡 Ideas
     - ❓ Q&A
     - 📣 Announcements
     - 🎉 Show and Tell

4. **Add Labels** (organization)
   - Go to Issues → Labels
   - Add: `priority: high`, `priority: medium`, `priority: low`
   - Add: `status: in progress`, `status: blocked`
   - Add: `good first issue`, `help wanted`

5. **Update Repository Description**
   - Go to Settings → General → Description
   - Add: "Talk to Claude about your invention. Get patent-ready documentation. Local-first AI patent reviewer with USPTO MPEP search."
   - Topics: `patent`, `uspto`, `mpep`, `ai`, `claude`, `mcp-server`, `python`

---

## Checklist

Use this to track your setup progress:

- [ ] Files committed and pushed to GitHub
- [ ] Branch protection enabled for `master`
- [ ] Branch protection enabled for `dev`
- [ ] Security features enabled (Dependabot, secret scanning)
- [ ] Issues and Discussions enabled
- [ ] Merge settings configured
- [ ] Repository description and topics added
- [ ] Tested branch protection by trying to push to `master`
- [ ] Tested issue templates
- [ ] Read CONTRIBUTING.md
- [ ] Read SECURITY.md

---

## Common Questions

**Q: Do I need to do all of this right now?**
A: No! The minimum setup is:
1. Commit the files
2. Enable branch protection on `master`
3. Enable Dependabot alerts

Everything else can be added later as needed.

**Q: What if I'm the only developer?**
A: Many of these practices are still useful for solo developers:
- Branch protection prevents accidental mistakes
- Issue templates help track work
- Security policy documents best practices
- PR templates help with self-review

**Q: Can I customize the templates?**
A: Yes! All templates are markdown files. Edit them to fit your workflow.

**Q: What if a collaborator doesn't follow the guidelines?**
A: Branch protection and required reviews enforce critical rules. For other guidelines, provide friendly feedback in PR reviews.

---

## Getting Help

- **Detailed configuration:** See docs/GITHUB_SETUP.md
- **Development workflow:** See CONTRIBUTING.md
- **Security questions:** See SECURITY.md
- **GitHub docs:** https://docs.github.com/

---

**Ready to collaborate! 🎉**
