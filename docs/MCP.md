# MCP Server Pattern

## What is MCP?

Model Context Protocol (MCP) is a standard for giving LLMs access to external
tools. An MCP server exposes functions that an LLM client (like Claude) can call
via a JSON-RPC protocol over stdio.

## Why MCP for Homelab?

With MCP servers running on your infrastructure, your LLM can:

- **Query your databases** without you writing SQL
- **Offload tasks** to local LLMs to save cloud API costs
- **Send notifications** to your phone about completed tasks
- **Access any local service** through a controlled interface

## Architecture

```
LLM Client (Claude Code, etc.)
    |
    | stdio (JSON-RPC)
    |
MCP Server (Python process)
    |
    +-- HTTP --> Ollama API
    +-- SQL  --> SQLite databases
    +-- HTTP --> ntfy.sh
    +-- ...  --> any local service
```

Each MCP server:
- Runs as a child process of the LLM client
- Communicates via stdin/stdout (no network ports needed)
- Registers tools with typed input schemas
- Handles one request at a time

## Included Examples

### 1. SQLite Server (`mcp/sqlite/server.py`)

Read-only database access. Define which databases are allowed and the server
enforces SELECT-only queries.

```json
{
  "tools": [
    "sqlite_query -- Execute a SELECT query",
    "sqlite_schema -- Get table/column schema"
  ]
}
```

### 2. Ollama Server (`mcp/ollama/server.py`)

Offload tasks to your local LLM. Saves cloud API tokens for tasks that a
local model handles fine.

```json
{
  "tools": [
    "ollama_generate -- Generate text with any local model",
    "ollama_code_review -- Review code for bugs/security issues",
    "ollama_summarize -- Summarize text",
    "ollama_models -- List available models"
  ]
}
```

### 3. Notifications Server (`mcp/notifications/server.py`)

Send alerts to desktop and phone from your LLM.

```json
{
  "tools": [
    "notify_desktop -- Linux desktop notification",
    "notify_phone -- Push notification via ntfy.sh",
    "notify_system -- System status alert",
    "notify_history -- View recent notifications"
  ]
}
```

## Configuration

MCP servers are configured in a manifest file that your LLM client reads:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "python3",
      "args": ["mcp/sqlite/server.py"],
      "description": "Read-only database access"
    },
    "ollama": {
      "command": "python3",
      "args": ["mcp/ollama/server.py"],
      "description": "Local LLM inference"
    },
    "notifications": {
      "command": "python3",
      "args": ["mcp/notifications/server.py"],
      "description": "Push notifications"
    }
  }
}
```

For Claude Code, add this to `~/.mcp.json`.

## Writing Your Own MCP Server

Here is the minimal template:

```python
#!/usr/bin/env python3
"""My custom MCP server."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("my-server")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="my_tool",
            description="Does something useful",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "The input value",
                    },
                },
                "required": ["input"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "my_tool":
        result = do_something(arguments["input"])
        return [TextContent(type="text", text=result)]
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
```

### Requirements

```
pip install mcp
```

### Testing

```bash
# Syntax check
python3 -m py_compile mcp/my-server/server.py

# Quick import test
timeout 5 python3 -c "exec(open('mcp/my-server/server.py').read().split('async def main')[0])"
```

## Health Checking

Use `scripts/mcp-health` to verify all servers:

```bash
./scripts/mcp-health
# Checks: syntax, imports, dependencies, external services
```
