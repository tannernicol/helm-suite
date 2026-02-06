# Architecture

## Overview

HelmV2 runs on a single Linux machine with an optional NAS for storage.
All services are accessed through Tailscale VPN -- nothing is exposed to the
public internet.

## Network Topology

```
  Your Devices (phone, laptop, desktop)
         |
    [Tailscale VPN]
         |
    100.x.x.x (your server's Tailscale IP)
         |
    +----+----+
    |  Caddy  |  Reverse proxy, TLS termination
    +----+----+
         |
    +----+---+----+
    |    |   |    |
    v    v   v    v
  Auth  App App  App    (all on 127.0.0.1:PORT)
```

## Component Layers

### Layer 1: Network (Tailscale)

Tailscale creates a WireGuard mesh VPN between your devices. Your server gets a
stable IP (100.x.x.x) that only your authorized devices can reach.

Key properties:
- No port forwarding required
- Works behind NAT/firewalls
- DNS can point `*.yourdomain.com` to the Tailscale IP
- MagicDNS for device-to-device resolution

### Layer 2: Reverse Proxy (Caddy)

Caddy binds to the Tailscale IP and `127.0.0.1`. It handles:
- TLS termination with your domain's certificates
- Routing `service.yourdomain.com` to the correct backend port
- Forwarding authentication to Authelia for protected services
- HTTP-to-HTTPS redirects

### Layer 3: Authentication (Authelia)

Authelia provides single sign-on (SSO) for all web services:
- Username/password with optional TOTP 2FA
- Session cookies shared across all `*.yourdomain.com` subdomains
- Per-service access control policies
- Caddy's `forward_auth` directive checks every request

### Layer 4: Services (Docker + Systemd)

Services run as Docker containers (managed by Docker Compose) or native
systemd services. Each service:
- Binds to `127.0.0.1` only (never `0.0.0.0`)
- Gets a unique port
- Has health checks and auto-restart
- Uses environment variables from the shared `.env`

### Layer 5: Storage (NAS)

Optional network-attached storage for:
- Photo library (Immich)
- Backup destination
- Media files
- Shared documents

Mounted via NFS or SMB at a configurable path (default: `/mnt/nas`).

## Service Map

```
Port    Service         Type        GPU   Auth
------  -------------   ----------  ----  ----
9091    Authelia         Docker      No    --
11434   Ollama           Docker      Yes   No
2283    Immich           Docker      Yes   Yes
3030    Gitea            Docker      No    Yes
8095    SearxNG          Docker      No    Yes
3100    Grafana          Docker      No    Yes
9090    Prometheus       Docker      No    No
```

## MCP Server Architecture

MCP (Model Context Protocol) servers give your LLM tools access to local
infrastructure. They communicate over stdio and are launched by the LLM client.

```
Claude / LLM Client
    |
    +-- stdio --> sqlite MCP server --> local databases
    |
    +-- stdio --> ollama MCP server --> Ollama API
    |
    +-- stdio --> notifications MCP server --> ntfy.sh / notify-send
```

Each MCP server:
- Is a standalone Python script
- Uses the `mcp` library for protocol handling
- Registers tools with JSON Schema input definitions
- Runs as a child process of the LLM client

## Directory Layout

```
/srv/helmv2/           # Runtime data
  caddy/Caddyfile               # Generated Caddy config
  authelia/configuration.yml    # Generated Authelia config
  .env                          # Generated shared env
  gitea/                        # Gitea data + config
  immich/                       # Immich uploads + DB
  grafana/                      # Grafana data
  searxng/                      # SearxNG config
  ollama/                       # Ollama model storage
  monitoring/                   # Prometheus data

~/.config/systemd/user/         # User systemd units
/etc/systemd/system/            # System systemd units
```

## Data Flow

### Web Request

1. User opens `https://photos.yourdomain.com` on phone
2. DNS resolves to Tailscale IP (100.x.x.x)
3. Tailscale routes the request to the server
4. Caddy receives the request, terminates TLS
5. Caddy forwards auth check to Authelia
6. Authelia verifies session cookie (or redirects to login)
7. Caddy proxies to Immich on 127.0.0.1:2283
8. Immich serves the response

### MCP Tool Call

1. User asks Claude "what's in my database?"
2. Claude invokes the `sqlite_query` tool
3. MCP protocol sends the request via stdio to the sqlite server
4. Server executes a read-only SELECT query
5. Results are returned as JSON via stdio
6. Claude formats and presents the data
