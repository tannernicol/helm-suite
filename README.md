# HelmV2 -- Host Your Own Internet

> Named in homage to [The Helm](https://thehelm.com), a personal server company
> that believed your data should live in your home. They ran out of funding, but
> the mission lives on.

A complete blueprint for building private, self-hosted infrastructure: local AI,
photo management, Git hosting, private search, and more. All behind Tailscale
with zero public exposure.

## Why?

You shouldn't need to trust cloud providers with your family photos, personal AI
conversations, financial data, or search history. HelmV2 gives you the
blueprint to host everything yourself on hardware you own.

## What You Get

| Service | What It Does | Stack |
|---------|-------------|-------|
| **Ollama** | Local LLM inference (GPU) | Docker + NVIDIA |
| **Immich** | Google Photos replacement | Docker + GPU ML |
| **Gitea** | GitHub replacement | Docker |
| **SearxNG** | Private search engine | Docker |
| **Authelia** | Single sign-on | Docker + Redis |
| **Caddy** | Reverse proxy + TLS | Systemd |
| **MCP Servers** | LLM tool access | Python + stdio |
| **Monitoring** | Prometheus + Grafana | Docker |

## What Makes It Different

- **Zero public exposure** -- Everything binds to Tailscale IP. Nothing on the public internet.
- **Single config** -- One `.env` file generates all infrastructure configs.
- **GPU-first** -- NVIDIA runtime for Ollama, Immich ML, and custom models.
- **MCP server pattern** -- 3 example MCP servers so your LLMs can access your infrastructure.
- **Self-healing** -- Systemd services with health checks, auto-restart, resource limits.
- **Family-safe** -- DNS filtering, SSO, network-level controls.

## Architecture

```
                     Tailscale VPN (100.x.x.x)
                              |
            +------- your.domain.com -------+
            |                               |
        +---+---+                      +----+----+
        | Caddy |--- TLS + Auth ------>| Authelia|
        +---+---+                      +---------+
            |
    +-------+-------+-------+-------+-------+
    |       |       |       |       |       |
 Ollama  Immich  Gitea  SearxNG  Grafana  Apps
 :11434  :2283   :3030  :8095    :3100    :...
    |       |
  [GPU]   [GPU]
```

All services bind to `127.0.0.1` or your Tailscale IP. Caddy handles TLS
termination and forwards auth to Authelia. Nothing is reachable from the
public internet.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/tannernicol/helmv2.git
cd helmv2

# 2. Configure
cp .env.example .env
# Edit .env with your domain, IPs, and preferences

# 3. Bootstrap
./setup.sh

# 4. Start services
cd infra/compose/ollama && docker compose up -d
cd infra/compose/gitea && docker compose up -d
# ... or use the CLI:
./scripts/homelab status
```

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for the full walkthrough.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) -- Full system design
- [Security Model](docs/SECURITY.md) -- Tailscale-only access, zero public exposure
- [Quick Start](docs/QUICKSTART.md) -- Get running in 30 minutes
- [GPU Setup](docs/GPU.md) -- GPU passthrough for local AI
- [MCP Servers](docs/MCP.md) -- Give your LLMs access to your infrastructure

## Project Structure

```
helmv2/
  .env.example              # All configurable variables
  setup.sh                  # Interactive bootstrap
  docs/                     # Architecture, security, guides
  infra/
    caddy/                  # Reverse proxy templates
    authelia/               # SSO configuration
    compose/                # Docker Compose for each service
    systemd/                # Service and timer templates
  mcp/                      # MCP server examples (sqlite, ollama, notifications)
  scripts/                  # CLI tools (homelab, security-audit, mcp-health, backup)
  ansible/                  # Automated machine bootstrap
  examples/                 # How-to guides
```

## Requirements

- Linux server (Ubuntu 22.04+ or Fedora 39+ recommended)
- Tailscale account (free for personal use)
- Docker + Docker Compose
- NVIDIA GPU (optional, for Ollama/Immich ML acceleration)
- Domain name (for TLS certificates)

## Contributing

This is a blueprint, not a product. Fork it, make it yours. If you improve
something that would help others, PRs are welcome.

## License

MIT -- see [LICENSE](LICENSE).
