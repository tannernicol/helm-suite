# How to Add a New Service

## Step 1: Choose a Port

Check what's in use:

```bash
./scripts/homelab ports
```

Pick an unused port. Convention: services in the 3000-9999 range.

## Step 2: Create Docker Compose File

Create `infra/compose/myservice/docker-compose.yml`:

```yaml
services:
  myservice:
    image: myservice/myservice:latest
    container_name: myservice
    ports:
      # Always bind to 127.0.0.1 -- never 0.0.0.0
      - "127.0.0.1:8080:8080"
    volumes:
      - myservice-data:/data
    environment:
      - TZ=${TIMEZONE:-America/Los_Angeles}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  myservice-data:
```

## Step 3: Add Caddy Site Block

Add to your Caddyfile (or Caddyfile.template for auto-generation):

```
myservice.${DOMAIN} {
    import tls_config
    import authelia
    reverse_proxy localhost:8080
}
```

Reload Caddy:

```bash
sudo systemctl reload caddy-sovereign
```

## Step 4: Start the Service

```bash
cd infra/compose/myservice
docker compose up -d
```

## Step 5: Verify

```bash
# Check container is running
docker ps | grep myservice

# Check port is listening
ss -tlnp | grep 8080

# Check via Caddy
curl -k https://myservice.yourdomain.com/health

# Run security audit
./scripts/security-audit
```

## Step 6: Add Backup (Optional)

Add the service data path to `scripts/backup`:

```bash
backup_dir "/srv/helmv2/myservice" "myservice"
```

## Tips

- **Always bind to 127.0.0.1** in Docker port mappings
- **Add a healthcheck** so Docker can restart unhealthy containers
- **Use named volumes** for persistent data
- **Add the service to `scripts/homelab`** status checks if desired
- **Run `security-audit`** after any new service to verify no public exposure
