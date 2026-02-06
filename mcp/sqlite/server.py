#!/usr/bin/env python3
"""SQLite MCP Server -- Read-only database access for LLM tools.

Exposes selected SQLite databases to your LLM via MCP protocol.
Only SELECT queries are allowed. Configure ALLOWED_DBS to control
which databases are accessible.

Usage:
    python3 server.py

Configure in your MCP client (e.g., ~/.mcp.json):
    {
        "mcpServers": {
            "sqlite": {
                "command": "python3",
                "args": ["/path/to/mcp/sqlite/server.py"]
            }
        }
    }
"""

import asyncio
import json
import sqlite3
import sys
from pathlib import Path

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
# Add your databases here. Keys are user-facing names, values are file paths.
ALLOWED_DBS: dict[str, Path] = {
    "example": Path.home() / "data" / "example.db",
    # "myapp": Path("/srv/myapp/data.db"),
}

# SQL keywords that are never allowed in queries
FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "CREATE",
    "ALTER",
    "ATTACH",
    "DETACH",
    "REPLACE",
    "GRANT",
    "REVOKE",
]

# ---- Server -----------------------------------------------------------------
server = Server("sqlite-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    db_names = ", ".join(ALLOWED_DBS.keys()) if ALLOWED_DBS else "(none configured)"
    return [
        Tool(
            name="sqlite_query",
            description=(
                f"Execute a read-only SQL query. Available databases: {db_names}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name",
                        "enum": list(ALLOWED_DBS.keys()),
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute (read-only)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max rows to return (default 100)",
                        "default": 100,
                    },
                },
                "required": ["database", "query"],
            },
        ),
        Tool(
            name="sqlite_schema",
            description="Get the schema (tables and columns) of a database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name",
                        "enum": list(ALLOWED_DBS.keys()),
                    },
                },
                "required": ["database"],
            },
        ),
    ]


def _validate_query(query: str) -> str | None:
    """Validate a SQL query is read-only. Returns error message or None."""
    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
        return "Only SELECT queries are allowed"
    for word in FORBIDDEN_KEYWORDS:
        if word in query_upper:
            return f"{word} operations are not allowed"
    return None


def _get_db(db_name: str) -> tuple[Path | None, str | None]:
    """Look up a database by name. Returns (path, error)."""
    if db_name not in ALLOWED_DBS:
        return None, f"Unknown database '{db_name}'. Available: {list(ALLOWED_DBS.keys())}"
    db_path = ALLOWED_DBS[db_name]
    if not db_path.exists():
        return None, f"Database file not found: {db_path}"
    return db_path, None


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    log_call("sqlite", name, arguments)

    if name == "sqlite_query":
        db_name = arguments.get("database", "")
        query = arguments.get("query", "").strip()
        limit = arguments.get("limit", 100)

        db_path, error = _get_db(db_name)
        if error:
            return [TextContent(type="text", text=f"Error: {error}")]

        error = _validate_query(query)
        if error:
            return [TextContent(type="text", text=f"Error: {error}")]

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"

            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            results = [dict(row) for row in rows]
            output = json.dumps(results, indent=2, default=str)
            log_call("sqlite", name, arguments, len(output))
            return [TextContent(type="text", text=output)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "sqlite_schema":
        db_name = arguments.get("database", "")
        db_path, error = _get_db(db_name)
        if error:
            return [TextContent(type="text", text=f"Error: {error}")]

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

            schema: dict = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [
                    {
                        "name": row[1],
                        "type": row[2],
                        "notnull": bool(row[3]),
                        "pk": bool(row[5]),
                    }
                    for row in cursor.fetchall()
                ]
                schema[table] = columns

            conn.close()
            return [TextContent(type="text", text=json.dumps(schema, indent=2))]

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
