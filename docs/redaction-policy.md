# Redaction Policy

Sanitize outputs before publishing docs, screenshots, issues, or reports.

## Always Redact

- Emails, usernames, and account IDs
- API keys, tokens, and private keys
- Internal domains, hostnames, and private IPs
- Any customer, household, or financial data

## Safe Replacements

- Email: `user@example.com`
- Domain: `home.example.com`
- IP: `10.0.0.0`
- Secret: `REDACTED`

## Verification

Run:

```bash
python scripts/redact.py --self-check
```
