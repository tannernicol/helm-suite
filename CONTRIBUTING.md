# Contributing

Thanks for improving Helm Suite.

## Workflow

1. Fork the repo and create a branch per change.
2. Update docs when changing setup, architecture, or scripts.
3. Run local validation before opening a PR.
4. Open a PR with impact, risk, and rollback notes.

## Local Validation

```bash
python -m pytest tests/ -v
pre-commit run --all-files
python scripts/redact.py --self-check
bash -n setup.sh
bash -n scripts/security-audit
```

## Pull Request Expectations

- Keep each PR scoped to one deployment concern.
- Preserve private-by-default architecture assumptions.
- Redact all screenshots/logs/config snippets.
- Never include secrets, tokens, private IPs, or internal domains.

## Starter Tasks

- See docs/good-first-issues.md for contributor-friendly tasks with acceptance criteria.
- Follow docs/release-policy.md when preparing release-impacting changes.
