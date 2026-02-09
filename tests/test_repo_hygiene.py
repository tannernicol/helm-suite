from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def test_env_example_has_core_keys() -> None:
    env = parse_env(REPO_ROOT / ".env.example")
    required = {
        "DOMAIN",
        "TAILSCALE_IP",
        "USERNAME",
        "TIMEZONE",
        "OLLAMA_PORT",
        "AUTHELIA_JWT_SECRET",
        "AUTHELIA_SESSION_SECRET",
    }
    missing = sorted(required - set(env))
    assert not missing, f"Missing expected keys in .env.example: {missing}"


def test_env_example_uses_safe_placeholders() -> None:
    env = parse_env(REPO_ROOT / ".env.example")
    assert env["DOMAIN"].endswith("example.com")
    assert env["TAILSCALE_IP"] in {"100.x.x.x", "100.64.0.1"}
    assert env["USER_EMAIL"] == "user@example.com"
    assert env["AUTHELIA_JWT_SECRET"].startswith("CHANGE_ME_")
    assert env["AUTHELIA_SESSION_SECRET"].startswith("CHANGE_ME_")


def test_gitignore_protects_env_file() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text()
    assert ".env" in gitignore
    assert "!.env.example" in gitignore


def test_public_hygiene_docs_exist() -> None:
    assert (REPO_ROOT / "docs" / "public-scope.md").exists()
    assert (REPO_ROOT / "docs" / "redaction-policy.md").exists()
