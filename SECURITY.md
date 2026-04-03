# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in kraken-connector, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email **terrylgarner@protonmail.com** with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact

You should receive an acknowledgment within 48 hours. We will work with you to understand the issue and coordinate a fix before any public disclosure.

## API Key Safety

kraken-connector handles Kraken API keys and secrets for authenticated endpoints. Keep the following in mind:

- Never commit API keys or secrets to version control
- Use environment variables or a secrets manager to supply credentials at runtime
- The library redacts credentials from `repr()` output, but avoid logging client objects at debug level in production
