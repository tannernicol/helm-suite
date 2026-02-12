<div align="center">
  <img src="logo.svg" width="96" height="96" alt="Helm Suite logo" />
  <h1>Helm Suite</h1>
  <p><strong>Replace 5 SaaS products with one Linux box and a Tailscale account.</strong></p>
  <p>
    <a href="https://tannner.com">tannner.com</a> ·
    <a href="https://github.com/tannernicol/helm-suite">GitHub</a>
  </p>

[![CI](https://github.com/tannernicol/helm-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/tannernicol/helm-suite/actions/workflows/ci.yml)
</div>

---

<p align="center">
  <img src="docs/demo.gif" alt="Helm Suite demo" width="700" />
</p>

In 2019, [The Helm](https://www.theverge.com/2019/11/21/20975649/time-best-inventions-2019-list) was named a TIME Best Invention — a personal server that kept your data in your home. They ran out of funding. The mission didn't.

Helm Suite is a complete blueprint for replacing cloud services with self-hosted infrastructure on hardware you control. Everything runs behind Tailscale with **zero public exposure** — your services are reachable from your devices, invisible to the rest of the internet.

| You're paying for | Helm Suite replaces it with | Cost |
|---|---|---|
| Google Photos ($30/yr) | **Immich** — face recognition, maps, ML search | Free |
| GitHub Pro ($48/yr) | **Gitea** — unlimited private repos, CI runners | Free |
| ChatGPT Plus ($240/yr) | **Ollama** — run LLMs on your GPU, no data leaves | Free |
| Google Search (your data) | **SearxNG** — private metasearch, no tracking | Free |
| 1Password/SSO ($36/yr) | **Authelia** — single sign-on for all services | Free |

**Total saved: ~$350/yr** (plus you own your data)

**This repo is the complete blueprint. From zero to a private personal cloud in one bootstrap.**

## What You'll End Up With

- **Reverse proxy** (Caddy) with automatic HTTPS on your own domain
- **Photo library** (Immich) — Google Photos replacement, fully private
- **Finance dashboard** (Money App) — Mint replacement for accounts, spending, net worth
- **Local docs + notes** (Notes App) — Google Docs-style personal knowledge workspace
- **Private search** (SearXNG + Homelab Search) — Google Search replacement for web + your own corpus
- **Local Git forge** (Gitea) — GitHub replacement for personal repos and issues
- **AI stack** (Ollama) — local LLMs, no cloud dependency
- **Offline coding agent** (Pip-Boy) — local code assistant trained by Claude/Codex workflows
- **Secure networking** (Tailscale) — access everything from anywhere, zero public exposure
- **Auth gateway** (Authelia) — SSO for all your services
- **Automated backups** to NAS with versioned snapshots

## Local App Replication Map

| Cloud SaaS | Local App in Helm Suite | What You Keep |
| --- | --- | --- |
| Google Docs | Notes App | Your documents and notes on local storage |
| Google Photos | Immich / Photos AI | Photo library + metadata under your control |
| Google Search | SearXNG + Homelab Search | Private search behavior and indexed corpus |
| Mint | Money App | Financial history and analytics in your DB |
| GitHub (personal use) | Gitea | Source control, issues, and repo history |
| Cloud AI copilots | Ollama + Pip-Boy offline coding agent | Prompt history, model outputs, and custom workflows |

## Why This Is Better in Practice

### Speed
- Most reads are LAN-local, so dashboards and search avoid WAN round-trips.
- Local indexing/search is immediate against your own data.
- Local model inference removes cloud queue latency and API retry churn.

### Cost
- Replaces multiple recurring SaaS subscriptions with one homelab stack.
- Reduces ongoing API usage for everyday assistant and search workflows.

### Security
- Zero public exposure by default: private mesh access through Tailscale.
- Consistent auth boundary with Authelia SSO + 2FA across sensitive apps.
- Local backups and snapshots reduce outage and vendor lock-in risk.

### Privacy
- Personal photos, notes, finance data, and search history stay on your hardware.
- AI workflows can run fully local without sending prompt/context data to third parties.
- You decide retention, logging, and deletion policies across the entire stack.

## Quick Start

```bash
git clone https://github.com/tannernicol/helm-suite.git
cd helm-suite

# 1. Configure
cp .env.example .env && vim .env

# 2. Bootstrap
./bootstrap.sh
```

```
$ ./bootstrap.sh
→ caddy ✓  immich ✓  ollama ✓  authelia ✓
→ All services on Tailscale. Zero public exposure.
```

> **Note:** This repo provides bootstrap tooling, example configs, and architecture documentation. Production configs (credentials, domain-specific rules, service tuning) are kept private for operational security. The templates here are ready to customize for your own setup.

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

All services bind to `127.0.0.1` or your Tailscale IP. Caddy handles TLS termination and forwards auth to Authelia. Nothing is reachable from the public internet.

## What's Included

```
helm-suite/
  .env.example                  # All configurable variables
  bootstrap.sh                  # One-command setup
  config/
    docker-compose.yml          # Multi-service stack
    Caddyfile.example           # Reverse proxy template
    helm-service@.service       # Systemd template for native services
    example.yaml                # Service configuration
  scripts/
    healthcheck.sh              # Service health monitoring
    demo.py                     # Demo harness
  docs/
    architecture.md             # System design
    setup.md                    # Detailed setup guide
    examples.md                 # Usage examples
    faq.md                      # Common questions
```

## What Makes It Different

Most self-hosting guides show you how to run one container. Helm Suite gives you the whole stack:

- **Zero public exposure** — Everything binds to your Tailscale IP. Nothing on the public internet, ever.
- **Single config** — One `.env` file drives Caddy routes, Docker Compose, and systemd services.
- **GPU-first** — NVIDIA runtime for Ollama and Immich ML (face recognition, CLIP search).
- **Security audit built in** — `healthcheck.sh` checks service status across the stack.

## Prerequisites

- Linux server (Fedora, Ubuntu, or similar)
- [Tailscale](https://tailscale.com) account (free tier works)
- Docker + Docker Compose
- A domain name (optional but recommended)
- NVIDIA GPU (optional, for Ollama/Immich ML)

## Threat Model

**In scope — what Helm Suite defends against:**

- **Public internet exposure** — zero services are publicly routable; all traffic flows through Tailscale's WireGuard mesh, eliminating the attack surface of open ports and public DNS
- **Unauthorized access to dashboards** — Authelia enforces SSO with 2FA on all sensitive services (finance, photos, admin UIs); no service relies solely on "it's on the VPN" for access control
- **TLS misconfiguration** — Caddy handles certificate issuance and renewal automatically; no manual cert management, no expired certificates, no plaintext HTTP between client and proxy
- **Vendor lock-in and data loss** — all data (photos, finances, AI models) lives on hardware you control with automated versioned backups to NAS; no third-party service can sunset your data

**Out of scope — what Helm Suite intentionally does not defend against:**

- **Physical access to the NAS** — if an attacker has physical access to the machine, disk encryption and boot security are your responsibility; this blueprint does not configure FDE
- **Tailscale account compromise** — if your Tailscale identity is compromised, the attacker joins the mesh; Authelia provides a second layer, but Tailscale is the network perimeter
- **Supply chain attacks on containers** — Immich, Ollama, and other services are pulled from upstream images; Helm Suite does not verify image signatures or run admission control
- **Lateral movement post-compromise** — services run on the same host without network segmentation between containers; a compromised service may reach other local services

## Architecture (Mermaid)

```mermaid
flowchart TB
    Client([Devices\nPhone / Laptop / Desktop])
    Client -->|WireGuard tunnel| TS[Tailscale Mesh]

    TS --> Caddy[Caddy\nReverse Proxy + TLS]

    Caddy --> Authelia[Authelia\nSSO + 2FA]

    Authelia -->|authenticated| Immich[Immich\nPhoto Library]
    Authelia -->|authenticated| Money[Money App\nFinance Dashboard]
    Authelia -->|authenticated| OllamaSvc[Ollama\nLocal LLMs]
    Authelia -->|authenticated| Custom[Custom Apps]

    Immich --> Storage[(NAS\nPhotos + Backups)]
    Money --> SQLite[(SQLite)]
    SQLite --> Storage
    OllamaSvc --> Models[(Model Weights\nLocal Disk)]

    subgraph Backup Pipeline
        Systemd[Systemd Timers] -->|versioned snapshots| Storage
    end
```

## Author

**Tanner Nicol** — [tannner.com](https://tannner.com) · [GitHub](https://github.com/tannernicol)

## License

MIT — see [LICENSE](LICENSE).
