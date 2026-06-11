# Security Policy

## Supported Versions

Only the latest stable release receives security fixes. Older versions are not backported.

| Version | Supported |
| ------- | --------- |
| 1.3.x (latest) | ✅ |
| < 1.3 | ❌ |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

To report a vulnerability, use GitHub's private vulnerability reporting:

1. Go to the [Security Advisories](https://github.com/gowdhamp/scaffoldr/security/advisories/new) page.
2. Click **"Report a vulnerability"** and fill in the details.
3. You will receive a response within **7 days**.

If GitHub's private reporting is unavailable, email **gowdhamp.official@gmail.com** with the subject line `[scaffoldr] Security Vulnerability`.

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- The scaffoldr version and OS/platform affected

## Disclosure Policy

- Vulnerabilities are triaged and a fix is targeted within **14 days** of confirmation.
- A [GitHub Security Advisory](https://github.com/gowdhamp/scaffoldr/security/advisories) is published once a fix is released.
- Credit is given to the reporter unless they prefer to remain anonymous.

## Scope

Scaffoldr is a local CLI tool that generates configuration files. The primary security considerations are:

- **Template injection** — malicious content in wizard inputs being rendered unsafely into generated files.
- **Credential exposure** — passwords and passphrases entered during the wizard being written insecurely to disk or logs.
- **Dependency vulnerabilities** — issues in third-party packages (Typer, Rich, Jinja2, etc.).

Out of scope: issues in tools that scaffoldr generates configs *for* (borgmatic, autorestic, Docker, etc.).
