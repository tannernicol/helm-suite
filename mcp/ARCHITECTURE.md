# MCP Architecture

This directory contains MCP (Model Context Protocol) servers that give your
LLM tools access to local infrastructure.

## Layout

```
mcp/
  manifest.json.template   # Server manifest (configure in ~/.mcp.json)
  ARCHITECTURE.md           # This document
  lib/
    logger.py               # Shared usage logging
  sqlite/
    server.py               # Read-only database access
  ollama/
    server.py               # Local LLM inference
  notifications/
    server.py               # Push notifications
```

## How MCP Works

1. Your LLM client (Claude Code, etc.) reads the manifest
2. For each configured server, it spawns a child process
3. Communication happens over stdin/stdout using JSON-RPC
4. The server registers tools with typed input schemas
5. The LLM calls tools as needed during conversation

## Adding a New Server

1. Create a directory: `mcp/myserver/`
2. Write `server.py` following the template in `docs/MCP.md`
3. Add an entry to `manifest.json.template`
4. Run `scripts/mcp-health` to verify

## Security

- SQLite server enforces SELECT-only queries
- All servers run as the current user (no elevated privileges)
- Logging tracks all tool calls for audit
- Servers only access resources you explicitly configure
