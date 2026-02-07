#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

ALLOWLIST_DOMAINS = {
    "github.com",
    "shields.io",
    "example.com",
    "example.internal",
    "tannner.com",
    "thehelm.com",
    "tailscale.com",
    "gmail.com",
    "linkedin.com",
    "contributor-covenant.org",
    "docker.com",
    "caddyserver.com",
    "ollama.ai",
    "docs.docker.com",
    "pytest.org",
}

ALLOWLIST_IPS = {
    "10.0.0.0",
    "127.0.0.1",
}

PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("ip", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("domain", re.compile(r"\b[a-zA-Z0-9-]+\.(com|net|org|io|ai|dev|app|co)\b")),
]


def is_allowed_domain(value: str) -> bool:
    return value.lower() in ALLOWLIST_DOMAINS


def scan_text(text):
    hits = []
    for name, rx in PATTERNS:
        for m in rx.finditer(text):
            value = m.group(0)
            if name == "domain" and is_allowed_domain(value):
                continue
            if name == "email":
                domain = value.split("@")[-1].lower()
                if is_allowed_domain(domain):
                    continue
            if name == "ip" and value in ALLOWLIST_IPS:
                continue
            hits.append((name, value))
    return hits


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".pyc"}:
            continue
        # Skip test files — they contain intentional fake PII for testing
        if "tests" in path.parts and path.name.startswith("test_"):
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
    args = parser.parse_args()
    if args.self_check:
        raise SystemExit(self_check(Path(".")))


if __name__ == "__main__":
    main()
