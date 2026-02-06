"""Shared MCP usage logging.

Logs all tool calls to a JSONL file for debugging and analytics.
"""

import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / ".config" / "helmv2" / "mcp-usage.jsonl"


def log_call(
    server: str, tool: str, arguments: dict | None = None, result_size: int = 0
) -> None:
    """Log an MCP tool call."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "server": server,
        "tool": tool,
        "args_keys": list(arguments.keys()) if arguments else [],
        "result_size": result_size,
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_stats(days: int = 7) -> dict:
    """Get usage stats for the last N days."""
    from datetime import timedelta

    cutoff = datetime.now() - timedelta(days=days)
    stats: dict = {"total": 0, "by_server": {}, "by_tool": {}}

    if not LOG_FILE.exists():
        return stats

    with open(LOG_FILE) as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts < cutoff:
                continue

            stats["total"] += 1
            server = entry["server"]
            tool = entry["tool"]

            stats["by_server"][server] = stats["by_server"].get(server, 0) + 1
            stats["by_tool"][tool] = stats["by_tool"].get(tool, 0) + 1

    return stats
