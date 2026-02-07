"""Tests for the demo harness."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDemo:
    def test_demo_runs_with_example_config(self):
        result = subprocess.run(
            [sys.executable, "scripts/demo.py", "--config", "config/example.yaml"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "tools" in data
        assert "status" in data
        assert data["status"] == "demo"

    def test_demo_lists_configured_tools(self):
        result = subprocess.run(
            [sys.executable, "scripts/demo.py", "--config", "config/example.yaml"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        data = json.loads(result.stdout)
        assert "money" in data["tools"]
        assert "notes" in data["tools"]
