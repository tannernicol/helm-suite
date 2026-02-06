# Quick Start -- Get Running in 30 Minutes

## Prerequisites

- A Linux server (Ubuntu 22.04+, Fedora 39+, or Debian 12+)
- A domain name you control
- 15 minutes of patience

## Step 1: Install Tailscale (5 minutes)

```bash
# Install
curl -fsSL https://tailscale.com/install.sh | sh

# Connect
sudo tailscale up

# Note your Tailscale IP
tailscale ip -4
# Example output: 100.64.0.1
```

## Step 2: Install Docker (5 minutes)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

# Fedora
sudo dnf install -y docker docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
```

## Step 3: Configure DNS (5 minutes)

In your DNS provider, create a wildcard A record:

```
*.home.example.com  ->  100.64.0.1  (your Tailscale IP)
```

This routes all subdomains to your server via Tailscale.

## Step 4: Clone and Configure (5 minutes)

```bash
git clone https://github.com/tannernicol/helmv2.git
cd helmv2

cp .env.example .env
```

Edit `.env` with your values:

```bash
DOMAIN=home.example.com
TAILSCALE_IP=100.64.0.1    # From step 1
USERNAME=youruser
USER_EMAIL=you@example.com
GPU_ENABLED=false           # Set true if you have an NVIDIA GPU
```

Generate random secrets:

```bash
# Generate and fill in the Authelia secrets
sed -i "s/CHANGE_ME_jwt_secret/$(openssl rand -hex 32)/" .env
sed -i "s/CHANGE_ME_session_secret/$(openssl rand -hex 32)/" .env
sed -i "s/CHANGE_ME_storage_key/$(openssl rand -hex 32)/" .env
sed -i "s/CHANGE_ME_grafana_password/$(openssl rand -base64 16)/" .env
sed -i "s/CHANGE_ME_immich_db_password/$(openssl rand -base64 16)/" .env
```

## Step 5: Bootstrap (5 minutes)

```bash
./setup.sh
```

This will:
- Check prerequisites
- Create directory structure
- Generate Caddyfile and Authelia config
- Create systemd services

## Step 6: Start Services (5 minutes)

Start the services you want:

```bash
# Gitea (self-hosted Git)
cd infra/compose/gitea && docker compose up -d && cd -

# SearxNG (private search)
cd infra/compose/searxng && docker compose up -d && cd -

# Monitoring (Grafana + Prometheus)
cd infra/compose/monitoring && docker compose up -d && cd -

# Authelia (SSO)
cd infra/compose/authelia && docker compose up -d && cd -
```

Install and start Caddy:

```bash
# Ubuntu/Debian
sudo apt install -y caddy

# Fedora
sudo dnf install -y caddy

# Start with our config
sudo systemctl enable --now caddy-sovereign
```

## Step 7: Verify

```bash
# Check service status
./scripts/homelab status

# Run security audit
./scripts/security-audit

# Open in browser (from a Tailscale-connected device)
# https://git.home.example.com
# https://search.home.example.com
# https://grafana.home.example.com
```

## Optional: GPU Services

If you have an NVIDIA GPU:

```bash
# Install NVIDIA Container Toolkit
# See docs/GPU.md for full instructions

# Start Ollama (local LLMs)
cd infra/compose/ollama && docker compose up -d && cd -
docker exec ollama ollama pull qwen2.5-coder:7b

# Start Immich (photo management with GPU ML)
cd infra/compose/immich && docker compose up -d && cd -
```

## Optional: NAS Backup

```bash
# Mount your NAS
sudo mount -t nfs 192.168.1.100:/share /mnt/nas

# Add to /etc/fstab for persistence
echo "192.168.1.100:/share /mnt/nas nfs defaults,_netdev 0 0" | sudo tee -a /etc/fstab

# Enable backup timer
systemctl --user enable --now sovereign-backup.timer
```

## Troubleshooting

### Can't reach services from phone

1. Make sure Tailscale is running on your phone
2. Check DNS resolves: `nslookup git.home.example.com`
3. Verify Caddy is running: `sudo systemctl status caddy-sovereign`

### Caddy won't start

1. Check the config: `caddy validate --config /srv/helmv2/caddy/Caddyfile`
2. Check port conflicts: `ss -tlnp | grep ':443'`

### Docker containers won't start

1. Check logs: `docker compose logs`
2. Check disk space: `df -h`
3. Check permissions on data directories
