# Security Policy

## Overview

The Utility Patent Reviewer handles sensitive intellectual property information. We take security seriously and appreciate the community's help in identifying and responsibly disclosing security vulnerabilities.

---

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 1.0.x   | :white_check_mark: | Current stable release |
| < 1.0   | :x:                | Pre-release versions not supported |

**Recommendation:** Always use the latest stable version for the most up-to-date security fixes.

---

## Security Model

### Local-First Architecture

This tool is designed with privacy and security in mind:

- **Local Processing** - All patent analysis runs on your computer
- **No Cloud Storage** - Your patent applications never leave your machine
- **Optional APIs** - External API calls (USPTO, PatentsView) only send search queries, not full applications
- **Open Source** - Code is transparent and auditable

### Data Handling

**What stays local:**
- Patent application text
- Your invention details
- MPEP index and patent corpus
- MCP server configuration

**What may be sent externally:**
- Search queries to USPTO API (if configured)
- Search queries to PatentsView API (if configured)
- Anonymous usage statistics (if enabled in Claude Code)

---

## Known Security Considerations

### API Keys

**Storage:**
- API keys should be stored in environment variables, not committed to git
- `.env` files are automatically excluded via `.gitignore`
- `.mcp.json` files (which may contain paths) are also excluded

**Best practices:**
```bash
# Good - Environment variables
export USPTO_API_KEY="your_key_here"
export PATENTSVIEW_API_KEY="your_key_here"

# Bad - Don't commit these
# .env
# .mcp.json with embedded keys
```

### File System Access

**MCP Server Access:**
- The MCP server runs with your user permissions
- Can read/write files in the project directory
- Be cautious with `additionalDirectories` in `.claude/settings.json`
- Use `.claude/settings.json` permissions rules to restrict sensitive files

**Recommended permissions:**
```json
{
  "permissions": {
    "allow": ["*.py", "*.md", "*.json", "*.txt"],
    "deny": [".env", "*.pem", "*.key", "secrets.json"]
  }
}
```

### Virtual Environment

**Isolation:**
- Always use a virtual environment (`venv`)
- Prevents conflicts with system packages
- Isolates dependencies

**Verification:**
```bash
# Check you're in venv
which python  # Should show venv path

# Verify isolation
pip list  # Should only show project dependencies
```

### Dependencies

**Supply Chain Security:**
- We pin dependency versions in `requirements.txt`
- Regular updates for security patches
- Automated Dependabot alerts enabled

**How to stay secure:**
1. Enable GitHub Dependabot alerts
2. Review and merge security updates promptly
3. Run `pip install --upgrade` regularly

---

## Reporting a Vulnerability

**IMPORTANT:** Please do not report security vulnerabilities through public GitHub issues.

### How to Report

**Preferred method:** GitHub Security Advisories
1. Go to the [Security tab](https://github.com/RobThePCGuy/utility-patent-reviewer/security)
2. Click "Report a vulnerability"
3. Fill out the advisory form

**Alternative method:** No email option available. Please use GitHub Security Advisories only.
### What to Include

Help us understand the issue by providing:

1. **Description** - Clear explanation of the vulnerability
2. **Impact** - What could an attacker do?
3. **Affected versions** - Which versions are vulnerable?
4. **Steps to reproduce** - Detailed reproduction steps
5. **Proof of concept** - Code or commands demonstrating the issue (if applicable)
6. **Suggested fix** - If you have ideas for fixing it (optional)
7. **Credit** - How you'd like to be credited (optional)

### Example Report

```
Title: API Key Exposure in Logs

Description:
The USPTO API client logs the full API request URL, which includes
the API key as a query parameter. This exposes the key in log files.

Impact:
Attackers with access to log files can extract API keys and make
unauthorized API requests.

Affected Versions:
1.0.0 - 1.0.5

Steps to Reproduce:
1. Configure USPTO_API_KEY environment variable
2. Run a patent search
3. Check logs in console output
4. API key is visible in logged URLs

Proof of Concept:
[DEBUG] Making request to: https://api.uspto.gov/search?apikey=SECRET_KEY_HERE

Suggested Fix:
Redact API keys from logged URLs or use header-based authentication.
```

---

## Response Timeline

We take security reports seriously and will respond according to the following timeline:

| Timeline | Action |
|----------|--------|
| **< 48 hours** | Acknowledge receipt of your report |
| **< 1 week** | Initial assessment and severity rating |
| **< 2 weeks** | Proposed fix or mitigation plan |
| **< 4 weeks** | Patch released (for critical vulnerabilities) |
| **After fix** | Public disclosure (coordinated with reporter) |

**Note:** Timeline may vary based on severity and complexity.

---

## Severity Classification

We use the following severity levels:

### Critical
- Remote code execution
- Exposure of all user data
- Privilege escalation to system admin

**Response:** Immediate patch within 48-72 hours

### High
- API key exposure
- Access to sensitive user data
- Denial of service

**Response:** Patch within 1-2 weeks

### Medium
- Information disclosure
- Bypass of security features
- Limited data access

**Response:** Patch in next minor release (2-4 weeks)

### Low
- Security misconfiguration
- Minimal impact vulnerabilities
- Theoretical attacks requiring unlikely conditions

**Response:** Patch in next major release or provide workaround

---

## Security Best Practices for Users

### Installation

1. **Verify source:**
   ```bash
   # Clone from official repo
   git clone https://github.com/RobThePCGuy/utility-patent-reviewer.git

   # Verify it's the official repo
   git remote -v
   ```

2. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Review code before running:**
   - Check `install.py` before execution
   - Review `mcp_server/server.py` for MCP functionality
   - Audit any code that accesses file system or network

### Configuration

1. **Protect API keys:**
   ```bash
   # Use environment variables
   export USPTO_API_KEY="your_key_here"

   # Never commit .env files
   echo ".env" >> .gitignore
   ```

2. **Configure permissions:**
   ```json
   // .claude/settings.json
   {
     "permissions": {
       "deny": [".env", "*.pem", "*.key", "secrets.json", ".ssh/*"]
     }
   }
   ```

3. **Limit MCP server access:**
   ```json
   // .claude/settings.json
   {
     "additionalDirectories": [
       "/path/to/safe/directory"
     ]
   }
   ```

### Ongoing Maintenance

1. **Keep updated:**
   ```bash
   git pull origin master
   pip install --upgrade -r requirements.txt
   ```

2. **Monitor for alerts:**
   - Watch the GitHub repository
   - Enable Dependabot alerts
   - Subscribe to security advisories

3. **Review dependencies:**
   ```bash
   pip list --outdated
   pip install --upgrade pip
   ```

---

## Known Limitations

### What This Tool Does NOT Protect Against

1. **Malicious PDF files** - The tool processes MPEP and patent PDFs. Only use trusted sources.

2. **Compromised dependencies** - We rely on PyPI packages. Supply chain attacks are possible.

3. **System-level access** - MCP server runs with your user permissions. Protect your account.

4. **Network interception** - API calls use HTTPS, but ensure your network is secure.

5. **Physical access** - If someone has physical access to your machine, they can access your files.

### Mitigations

- Only download PDFs from official USPTO sources
- Use virtual environments to isolate dependencies
- Enable GitHub Dependabot for automated security updates
- Use a firewall and secure network
- Encrypt your disk drive

---

## Security Updates

### Notification Channels

**How we communicate security updates:**
1. GitHub Security Advisories (primary)
2. Release notes on GitHub
3. CHANGELOG.md updates
4. GitHub Discussions (for awareness)

**How to stay informed:**
- Watch the repository for security advisories
- Enable notifications for releases
- Check CHANGELOG.md regularly

### Applying Updates

```bash
# Check current version
git describe --tags

# Pull latest changes
git pull origin master

# Update dependencies
pip install --upgrade -r requirements.txt

# Verify update
patent-reviewer status
```

---

## Disclosure Policy

### Coordinated Disclosure

We follow coordinated (responsible) disclosure:

1. Reporter submits vulnerability privately
2. We verify and develop a fix
3. We release the fix
4. We publicly disclose the vulnerability (90 days after fix or sooner with reporter agreement)

### Public Recognition

With your permission, we will:
- Credit you in the security advisory
- Mention you in release notes
- Add you to SECURITY_CREDITS.md (if created)

If you prefer to remain anonymous, we will respect that.

---

## Security Credits

We would like to thank the following individuals for responsibly disclosing security vulnerabilities:

*No vulnerabilities reported yet.*

---

## Additional Resources

### Security-Related Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Secure development practices
- [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md) - API key management
- [.gitignore](.gitignore) - Files excluded from version control

### External Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Common web application security risks
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

## Questions?

For security-related questions (not vulnerabilities), you can:
- Open a Discussion on GitHub (for general security questions)
For actual vulnerabilities, please use the reporting process above.

---

**Last Updated:** 2025-01-10

**Next Review:** 2025-04-10 (quarterly reviews)
