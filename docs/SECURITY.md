# Security Model

## Core Principle: Zero Public Exposure

Nothing in Helm Suite is reachable from the public internet. Every service
is accessible only through Tailscale VPN.

## Defense Layers

### 1. Network Layer (Tailscale)

- All services bind to `127.0.0.1` or the Tailscale IP
- No port forwarding on the router
- No Cloudflare tunnels or other public ingress
- DNS A records point to the Tailscale IP (not a public IP)
- Only authorized Tailscale devices can reach the server

### 2. TLS Layer (Caddy)

- All traffic is encrypted with TLS
- Certificates from Let's Encrypt (DNS challenge) or self-signed
- HTTP automatically redirects to HTTPS
- Caddy binds to Tailscale IP, not `0.0.0.0`

### 3. Authentication Layer (Authelia)

- SSO protects all sensitive services
- Username/password + optional TOTP 2FA
- Session cookies scoped to `*.yourdomain.com`
- Per-service access policies (some services can bypass auth)
- Brute-force protection with lockout

### 4. Application Layer

- Each service runs in its own Docker container (process isolation)
- Containers have read-only root filesystems where possible
- Resource limits (CPU, memory) prevent runaway containers
- Non-root container users where supported

### 5. Database Layer

- MCP sqlite server only allows SELECT queries
- Forbidden keywords: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER
- Database files are only accessible to their owning service
- Grafana uses read-only database mounts

## Security Audit Script

The `scripts/security-audit` script checks:

1. **DNS records** -- Verifies all `*.yourdomain.com` resolve to Tailscale IP
2. **Port bindings** -- Checks no services listen on `0.0.0.0`
3. **Docker ports** -- Verifies all published ports bind to `127.0.0.1`
4. **Firewall** -- Confirms UFW/firewalld is active with appropriate rules
5. **Tailscale** -- Verifies Tailscale is connected and serving

Run it regularly:

```bash
./scripts/security-audit
```

## Firewall Rules

Recommended UFW rules:

```bash
# Default deny incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH from local network only
sudo ufw allow from 192.168.1.0/24 to any port 22

# Allow Tailscale
sudo ufw allow in on tailscale0

# Enable
sudo ufw enable
```

## Secrets Management

Helm Suite does not store secrets in plaintext config files. Recommended
approaches:

1. **Environment variables** -- Loaded from `.env` (not committed to git)
2. **Docker secrets** -- For production Docker Swarm deployments
3. **pass** -- GPG-encrypted password store for manual credential management
4. **SOPS** -- For encrypting secrets files in the repo

The `.env` file is in `.gitignore` and should never be committed.

## Threat Model

### What we protect against

- Random internet scanners finding your services
- Cloud provider access to your data
- DNS-based service discovery
- Unauthorized device access
- Brute-force login attempts

### What we do NOT protect against

- Physical access to the server
- Compromised Tailscale account (rotate keys regularly)
- Compromised device on your Tailnet (remove untrusted devices)
- Vulnerabilities in upstream Docker images (keep updated)

## Best Practices

1. **Run security-audit daily** -- Set up a cron job or systemd timer
2. **Keep images updated** -- `docker compose pull` regularly
3. **Rotate secrets** -- Change passwords and API keys periodically
4. **Monitor logs** -- Check Grafana dashboards for anomalies
5. **Backup regularly** -- Test restores, not just backups
6. **Minimal Tailscale ACLs** -- Only share what's needed
7. **Enable 2FA** -- In Authelia and on your Tailscale account
