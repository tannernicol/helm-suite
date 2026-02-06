#!/usr/bin/env python3
"""Notifications MCP Server -- Push alerts to desktop and phone.

Sends notifications via:
- Desktop: notify-send (Linux)
- Phone: ntfy.sh (free, no signup required)

Usage:
    python3 server.py

Requires:
    pip install mcp httpx

Set NTFY_TOPIC environment variable to your unique ntfy.sh topic.
Subscribe to that topic in the ntfy app on your phone.
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Add lib to path for shared logging
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
try:
    from logger import log_call
except ImportError:

    def log_call(*args, **kwargs):
        pass


# ---- Configuration ----------------------------------------------------------
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "helmv2-alerts")
NOTIFY_LOG = (
    Path.home() / ".config" / "helmv2" / "notifications.jsonl"
)

# ---- Server -----------------------------------------------------------------
server = Server("notifications-mcp")


def _log_notification(notif: dict) -> None:
    """Append a notification to the local log."""
    NOTIFY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTIFY_LOG, "a") as f:
        f.write(json.dumps(notif, default=str) + "\n")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="notify_desktop",
            description="Send a desktop notification (Linux notify-send).",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Notification title"},
                    "message": {"type": "string", "description": "Notification body"},
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "normal", "critical"],
                        "default": "normal",
                    },
                },
                "required": ["title", "message"],
            },
        ),
        Tool(
            name="notify_phone",
            description=(
                "Send a push notification to phone via ntfy.sh. "
                "Subscribe to your topic in the ntfy app to receive."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Notification title"},
                    "message": {"type": "string", "description": "Notification body"},
                    "priority": {
                        "type": "string",
                        "enum": ["min", "low", "default", "high", "urgent"],
                        "default": "default",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Emoji tags (e.g., ['warning', 'tada'])",
                    },
                },
                "required": ["title", "message"],
            },
        ),
        Tool(
            name="notify_system",
            description="Send a system status alert to both desktop and phone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name"},
                    "status": {
                        "type": "string",
                        "enum": ["error", "warning", "info", "success"],
                    },
                    "message": {"type": "string", "description": "Alert message"},
                },
                "required": ["service", "status", "message"],
            },
        ),
        Tool(
            name="notify_history",
            description="Get recent notification history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent notifications to show",
                        "default": 20,
                    },
                },
            },
        ),
    ]


async def _send_desktop(
    title: str, message: str, urgency: str = "normal"
) -> bool:
    """Send a desktop notification via notify-send."""
    try:
        subprocess.run(
            ["notify-send", "-u", urgency, "-a", "HelmV2", title, message],
            timeout=5,
            check=False,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


async def _send_phone(
    title: str,
    message: str,
    priority: str = "default",
    tags: list[str] | None = None,
) -> bool:
    """Send a push notification via ntfy.sh."""
    headers: dict[str, str] = {
        "Title": title,
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = ",".join(tags)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://ntfy.sh/{NTFY_TOPIC}",
                content=message,
                headers=headers,
            )
            return resp.status_code == 200
    except Exception:
        return False


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    log_call("notifications", name, arguments)
    try:
        if name == "notify_desktop":
            title = arguments.get("title", "")
            message = arguments.get("message", "")
            urgency = arguments.get("urgency", "normal")

            success = await _send_desktop(title, message, urgency)
            _log_notification(
                {
                    "type": "desktop",
                    "title": title,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"sent": success, "type": "desktop"}),
                )
            ]

        elif name == "notify_phone":
            title = arguments.get("title", "")
            message = arguments.get("message", "")
            priority = arguments.get("priority", "default")
            tags = arguments.get("tags", [])

            success = await _send_phone(title, message, priority, tags)
            _log_notification(
                {
                    "type": "phone",
                    "title": title,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "sent": success,
                            "type": "phone",
                            "topic": NTFY_TOPIC,
                            "note": f"Subscribe to '{NTFY_TOPIC}' in ntfy app to receive",
                        }
                    ),
                )
            ]

        elif name == "notify_system":
            service = arguments.get("service", "unknown")
            status = arguments.get("status", "info")
            message = arguments.get("message", "")

            status_icons = {
                "error": "[ERROR]",
                "warning": "[WARN]",
                "info": "[INFO]",
                "success": "[OK]",
            }
            title = f"{status_icons.get(status, '[?]')} {service}: {status.upper()}"

            urgency = "critical" if status == "error" else "normal"
            priority = "high" if status == "error" else "default"
            tags = ["rotating_light"] if status == "error" else ["bell"]

            desktop_ok = await _send_desktop(title, message, urgency)
            phone_ok = await _send_phone(title, message, priority, tags)

            _log_notification(
                {
                    "type": "system",
                    "service": service,
                    "status": status,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "sent": desktop_ok or phone_ok,
                            "desktop": desktop_ok,
                            "phone": phone_ok,
                        }
                    ),
                )
            ]

        elif name == "notify_history":
            limit = arguments.get("limit", 20)
            history: list[dict] = []
            if NOTIFY_LOG.exists():
                with open(NOTIFY_LOG) as f:
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        if line.strip():
                            history.append(json.loads(line))
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"history": history[-limit:]}, indent=2),
                )
            ]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
