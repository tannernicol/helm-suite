# Helm Suite

**Replace 5 SaaS products with one Linux box and a Tailscale account.**

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI](https://github.com/tannernicol/helm-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/tannernicol/helm-suite/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Shell](https://img.shields.io/badge/shell-bash-blue.svg)](setup.sh)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](infra/compose/)

In 2019, [The Helm](https://www.theverge.com/2019/11/21/20975649/time-best-inventions-2019-list) was named a TIME Best Invention -- a personal server that kept your data in your home. They ran out of funding. The mission didn't.

Helm Suite is a complete blueprint for replacing cloud services with self-hosted infrastructure on hardware you control. Everything runs behind Tailscale with **zero public exposure** -- your services are reachable from your devices, invisible to the rest of the internet.

| You're paying for | Helm Suite replaces it with | Cost |
|---|---|---|
| Google Photos ($30/yr) | **Immich** -- face recognition, maps, ML search | Free |
| GitHub Pro ($48/yr) | **Gitea** -- unlimited private repos, CI runners | Free |
| ChatGPT Plus ($240/yr) | **Ollama** -- run LLMs on your GPU, no data leaves | Free |
| Google Search (your data) | **SearxNG** -- private metasearch, no tracking | Free |
| 1Password/SSO ($36/yr) | **Authelia** -- single sign-on for all services | Free |

**Total saved: ~$350/yr** (plus you own your data)

## At a Glance

- Private-by-default homelab stack with zero public ingress
- SaaS replacement blueprint for photos, search, source control, and AI workflows
- Built-in security audit and policy-gated access patterns
- Local coding-agent and private security-lab reference architecture
- CI + redaction checks to keep public docs safe and clean

## Local App Replication Map

| Cloud SaaS | Local module in Helm Suite | What stays private |
|---|---|---|
| Google Docs | Notes / local docs app pattern | Notes, docs, and personal knowledge |
| Google Photos | Immich | Photos, metadata, ML tags |
| Google Search | SearxNG + local search pattern | Search history and interests |
| Mint | Money app pattern | Financial history and spending data |
| GitHub (personal use) | Gitea | Repo history, issues, local CI metadata |
| Cloud coding copilot | Ollama + Pip-Boy offline coding agent pattern | Prompts, code context, model outputs |
| Cloud security scanners | Grimoire private security lab pattern | Findings, triage notes, local vuln analysis |

## What Makes It Different

Most self-hosting guides show you how to run one container. Helm Suite gives you the whole stack:

- **Zero public exposure** -- Everything binds to your Tailscale IP. Nothing on the public internet, ever.
- **Single config** -- One `.env` file generates Caddy routes, Authelia policies, Docker Compose configs, and systemd services.
- **GPU-first** -- NVIDIA runtime for Ollama (local LLMs), Immich ML (face recognition, CLIP search), and custom models.
- **MCP servers** -- 3 ready-to-use MCP servers so your LLM tools can query databases, run local inference, and send notifications.
- **Offline coding agent ready** -- Pip-Boy pattern for local coding assistance trained from your own workflows.
- **Private security lab ready** -- Grimoire pattern for on-prem vulnerability triage on authorized targets.
- **Security audit built in** -- `security-audit` script checks DNS, port bindings, firewall, Docker, and Cloudflare tunnels.
- **CLI management** -- `homelab status` shows everything at a glance.

## Operational Advantages

### Speed

- LAN-local dashboards and APIs avoid cloud round-trips.
- Local search and indexing reduce query latency for personal corpora.
- Local model inference avoids hosted queue delays and API retries.

### Cost

- Replaces multiple recurring SaaS subscriptions with one stack.
- Reduces paid API dependency for frequent assistant workflows.
- Eliminates recurring migration/export costs between providers.

### Security

- Zero-public-ingress architecture by default (Tailscale-scoped).
- SSO + policy boundaries through Authelia.
- Local backups and snapshots reduce vendor and outage risk.

### Privacy

- Photos, notes, finance, search, and model interactions stay on your hardware.
- No forced telemetry to external SaaS providers for core workflows.
- Retention and deletion policies are fully under your control.

## How It Looks

```
$ ./scripts/homelab status

HELM SUITE STATUS
=======================================================

Infrastructure
  ● Tailscale          100.64.0.1
  ● Caddy              reverse proxy
  ● Docker             12 containers

Services
  ● ollama
  ● gitea
  ● immich_server
  ● immich_machine_learning
  ● searxng
  ● authelia
  ● grafana
  ● prometheus

Ports
  ● :11434  Ollama
  ● :3030   Gitea
  ● :2283   Immich
  ● :8095   SearxNG
  ● :9091   Authelia
  ● :3100   Grafana
```

```
$ ./scripts/security-audit

1. Tailscale Status
  [PASS] Tailscale connected (100.64.0.1)

2. DNS Resolution
  [PASS] git.home.example.com -> 100.64.0.1 (Tailscale IP)
  [PASS] photos.home.example.com -> 100.64.0.1 (Tailscale IP)
  [PASS] search.home.example.com -> 100.64.0.1 (Tailscale IP)

3. Port Bindings
  [PASS] No unexpected 0.0.0.0 bindings

4. Docker Security
  [PASS] No privileged containers

5. Firewall Rules
  [PASS] Tailscale-scoped only

6. Cloudflare Tunnels
  [PASS] No Cloudflare tunnels running

All checks passed. Zero public exposure.
```

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
git clone https://github.com/tannernicol/helm-suite.git
cd helm-suite

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

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for the full walkthrough (30 minutes, start to finish).

## Documentation

- [Architecture](docs/ARCHITECTURE.md) -- Full system design
- [Security Model](docs/SECURITY.md) -- Tailscale-only access, zero public exposure
- [Quick Start](docs/QUICKSTART.md) -- Get running in 30 minutes
- [GPU Setup](docs/GPU.md) -- GPU passthrough for local AI
- [MCP Servers](docs/MCP.md) -- Give your LLMs access to your infrastructure

## Project Structure

```
helm-suite/
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

## MCP Servers

Helm Suite includes 3 MCP servers so your LLM tools can interact with your infrastructure:

| Server | What it does |
|--------|-------------|
| `mcp/sqlite` | Read-only database access with keyword filtering |
| `mcp/ollama` | Local LLM inference -- generation, code review, summarization |
| `mcp/notifications` | Push notifications to desktop and phone via ntfy.sh |

```json
{
  "mcpServers": {
    "ollama": {
      "command": "python3",
      "args": ["mcp/ollama/server.py"]
    }
  }
}
```

See [docs/MCP.md](docs/MCP.md) for the full pattern and how to build your own.

## Project Status

This is a working blueprint extracted from a production homelab. It runs 24/7 and has been through multiple iterations.

- [x] Tailscale-only network with zero public exposure
- [x] Caddy reverse proxy with Authelia SSO
- [x] Docker Compose for all services (Ollama, Immich, Gitea, SearxNG, Monitoring)
- [x] GPU passthrough for local LLMs and photo ML
- [x] Security audit script with 6 automated checks
- [x] CLI management tool (status, health, logs, restart)
- [x] MCP servers for LLM tool integration
- [x] Ansible playbooks for fresh machine bootstrap
- [x] Automated backup with systemd timers
- [ ] Multi-node setup documentation
- [ ] Kubernetes migration path
- [ ] Monitoring/alerting runbook

## Public Hygiene

Before publishing examples, logs, or screenshots:

```bash
python scripts/redact.py --self-check
```

Reference:

- [Security Policy](SECURITY.md)
- [Public Scope](docs/public-scope.md)
- [Redaction Policy](docs/redaction-policy.md)

## Contributing

This is a blueprint, not a product. Fork it, make it yours. If you improve
something that would help others, PRs are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT -- see [LICENSE](LICENSE).
