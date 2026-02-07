"""Tests for the redaction scanner."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import redact


class TestAllowlist:
    def test_allowed_domain_passes(self):
        assert redact.is_allowed_domain("github.com")
        assert redact.is_allowed_domain("tannner.com")

    def test_unknown_domain_blocked(self):
        assert not redact.is_allowed_domain("evil.com")

    def test_allowed_ip_not_flagged(self):
        hits = redact.scan_text("server at 127.0.0.1")
        ip_hits = [h for h in hits if h[0] == "ip"]
        assert len(ip_hits) == 0

    def test_private_ip_flagged(self):
        hits = redact.scan_text("server at 192.168.1.100")
        ip_hits = [h for h in hits if h[0] == "ip"]
        assert len(ip_hits) == 1


class TestPatternDetection:
    def test_detects_email(self):
        hits = redact.scan_text("contact me at secret@private.org")
        assert any(h[0] == "email" for h in hits)

    def test_ignores_allowed_email_domain(self):
        hits = redact.scan_text("file an issue on github.com")
        domain_hits = [h for h in hits if h[1] == "github.com"]
        assert len(domain_hits) == 0

    def test_detects_github_token(self):
        fake_token = "ghp_" + "A" * 30
        hits = redact.scan_text(f"token: {fake_token}")
        assert any(h[0] == "github_token" for h in hits)

    def test_detects_unknown_domain(self):
        hits = redact.scan_text("hosted at secretserver.com")
        assert any(h[0] == "domain" and h[1] == "secretserver.com" for h in hits)

    def test_clean_text_no_hits(self):
        hits = redact.scan_text("This is perfectly safe content with no PII.")
        assert len(hits) == 0


class TestSelfCheck:
    def test_self_check_passes(self):
        root = Path(__file__).resolve().parents[1]
        result = redact.self_check(root)
        assert result == 0, "Redaction self-check found PII in the repo"
