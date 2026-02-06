<div align="center">
  <img src="logo.svg" width="96" height="96" alt="Helm Suite logo" />
  <h1>Helm Suite</h1>
  <p><strong>Local-first personal ops stack -- SaaS replacement blueprint</strong></p>
  <p>
    <a href="https://tannner.com">tannner.com</a> ·
    <a href="https://github.com/tannernicol/helm-suite">GitHub</a>
  </p>
</div>

---

## What it does

Helm Suite is a reference blueprint for consolidating personal workflows -- finance, notes, research -- into private, self-hosted tools with zero data sprawl. It documents the architecture, integration patterns, and security boundaries needed to replace common SaaS tools with a unified, local-first stack you fully control.

## Key features

- Privacy-first architecture with explicit data boundaries
- Explicit trust boundaries between all components
- Integrated finance, notes, and research tools
- Security-first defaults with least-privilege access

## Stack

- Python
- FastAPI
- SQLite

## Getting started

```bash
git clone https://github.com/tannernicol/helm-suite.git
cd helm-suite
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/demo.py --config config/example.yaml
```

## Author

**Tanner Nicol** — Principal Security Infrastructure Engineer
[tannner.com](https://tannner.com) · [GitHub](https://github.com/tannernicol) · [LinkedIn](https://linkedin.com/in/tanner-nicol-60b21126)
