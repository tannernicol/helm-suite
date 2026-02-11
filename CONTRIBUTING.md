# Contributing

Thanks for your interest in Helm Suite.

## Getting Started

```bash
pip install -r requirements.txt pytest
python -m pytest tests/ -v
bash -n bootstrap.sh
```

## Pull Requests

1. Fork the repo and create a branch per change.
2. Update docs when changing setup, architecture, or scripts.
3. Run tests and `bash -n` syntax checks before opening a PR.
4. Never include secrets, tokens, private IPs, or internal domains.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
