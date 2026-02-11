"""Tests for bootstrap.sh structure and .env.example."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestBootstrap:
    def test_bootstrap_exists_and_executable(self):
        bs = ROOT / "bootstrap.sh"
        assert bs.exists(), "bootstrap.sh must exist"
        assert bs.stat().st_mode & 0o111, "bootstrap.sh must be executable"

    def test_bootstrap_has_shebang(self):
        text = (ROOT / "bootstrap.sh").read_text()
        assert text.startswith("#!/"), "bootstrap.sh must have a shebang line"

    def test_bootstrap_uses_strict_mode(self):
        text = (ROOT / "bootstrap.sh").read_text()
        assert "set -euo pipefail" in text


class TestEnvExample:
    def test_env_example_exists(self):
        assert (ROOT / ".env.example").exists()

    def test_env_example_has_required_vars(self):
        text = (ROOT / ".env.example").read_text()
        required = ["DOMAIN", "TAILSCALE_IP", "DATA_DIR", "BACKUP_DIR"]
        for var in required:
            assert var in text, f".env.example must define {var}"

    def test_env_example_has_no_real_secrets(self):
        text = (ROOT / ".env.example").read_text()
        for line in text.splitlines():
            if "=" in line and not line.strip().startswith("#"):
                _, value = line.split("=", 1)
                value = value.strip()
                assert value in (
                    "", "change-me", "example.com", "100.x.x.x",
                    "/srv/helm-suite", "/srv/helm-suite/photos",
                    "/mnt/nas/Backups/helm-suite",
                    "http://127.0.0.1:11434",
                    "America/Los_Angeles",
                    "postgres", "immich",
                ), f"Suspicious value in .env.example: {value}"


class TestProjectStructure:
    def test_readme_exists(self):
        assert (ROOT / "README.md").exists()

    def test_license_exists(self):
        assert (ROOT / "LICENSE").exists()

    def test_config_example_exists(self):
        assert (ROOT / "config" / "example.yaml").exists()

    def test_gitignore_blocks_env(self):
        text = (ROOT / ".gitignore").read_text()
        assert ".env" in text, ".gitignore must block .env files"

    def test_gitignore_blocks_databases(self):
        text = (ROOT / ".gitignore").read_text()
        assert "*.db" in text, ".gitignore must block database files"
