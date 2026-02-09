#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

ALLOWLIST_DOMAINS = {
    "example.com",
    "home.example.com",
    "github.com",
    "shields.io",
    "tailscale.com",
    "docker.com",
    "caddyserver.com",
    "ollama.ai",
    "ollama.com",
    "theverge.com",
    "tannner.com",
    "linkedin.com",
}

ALLOWLIST_IPS = {
    "10.0.0.0",
}

ALLOWLIST_SECRETS = {
    "tskey-auth-xxxxx",
    "tskey-REDACTED",
}

PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("tailscale_key", re.compile(r"\btskey-[A-Za-z0-9_-]+\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)?PRIVATE KEY-----")),
]

REPLACEMENTS = {
    "email": "user@example.com",
    "tailscale_key": "tskey-REDACTED",
    "github_token": "REDACTED_TOKEN",
    "aws_access_key": "REDACTED_AWS_KEY",
    "private_key": "REDACTED_PRIVATE_KEY",
}


def is_allowed_domain(value: str) -> bool:
    return value.lower() in ALLOWLIST_DOMAINS


def scan_text(text: str):
    hits = []
    for name, rx in PATTERNS:
        for m in rx.finditer(text):
            value = m.group(0)
            if name == "email":
                domain = value.split("@")[-1].lower()
                if is_allowed_domain(domain):
                    continue
            if name in {"tailscale_key", "github_token", "aws_access_key", "private_key"} and value in ALLOWLIST_SECRETS:
                continue
            hits.append((name, value))
    return hits


def redact_text(text: str) -> str:
    for name, rx in PATTERNS:
        text = rx.sub(REPLACEMENTS[name], text)
    return text


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue
        if ".pytest_cache" in path.parts:
            continue
        if "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"}:
            continue
        yield path


def self_check(root: Path) -> int:
    problems = []
    for path in iter_files(root):
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        hits = scan_text(text)
        if hits:
            problems.append((path, hits[:3]))
    if problems:
        for path, hits in problems:
            print(f"{path}: {hits}")
        return 1
    print("redaction check: OK")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--in", dest="input")
    parser.add_argument("--out", dest="output")
    args = parser.parse_args()

    root = Path(".")
    if args.self_check:
        raise SystemExit(self_check(root))

    if not args.input or not args.output:
        parser.error("--in and --out are required unless --self-check")
    text = Path(args.input).read_text()
    Path(args.output).write_text(redact_text(text))


if __name__ == "__main__":
    main()
