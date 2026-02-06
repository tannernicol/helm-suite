# Family-Safe Networking

How to set up your HelmV2 for family use with DNS filtering,
parental controls, and easy access for non-technical family members.

## DNS Filtering with Blocky or Pi-hole

### Option 1: Blocky (recommended, lightweight)

```yaml
# Add to infra/compose/blocky/docker-compose.yml
services:
  blocky:
    image: spx01/blocky:latest
    container_name: blocky
    ports:
      - "127.0.0.1:53:53/tcp"
      - "127.0.0.1:53:53/udp"
    volumes:
      - ./config.yml:/app/config.yml:ro
    restart: unless-stopped
```

### Option 2: Pi-hole

```yaml
services:
  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    ports:
      - "127.0.0.1:53:53/tcp"
      - "127.0.0.1:53:53/udp"
      - "127.0.0.1:8053:80"
    environment:
      - WEBPASSWORD=${PIHOLE_PASSWORD}
    volumes:
      - pihole-data:/etc/pihole
      - pihole-dns:/etc/dnsmasq.d
    restart: unless-stopped

volumes:
  pihole-data:
  pihole-dns:
```

## Network-Level Configuration

Set your router's DNS to point to the HelmV2 server:

1. Access router admin (usually 192.168.1.1)
2. Set primary DNS to your server's local IP (e.g., 192.168.1.10)
3. Set secondary DNS to a public resolver (8.8.8.8) as fallback

This applies filtering to all devices on the network, including phones,
tablets, and smart TVs.

## Per-User Access with Authelia

Set up different access levels in Authelia:

```yaml
# authelia configuration.yml
access_control:
  default_policy: one_factor
  rules:
    # Kids can access photos and search
    - domain:
        - "photos.home.example.com"
        - "search.home.example.com"
      subject: "group:kids"
      policy: one_factor

    # Adults get full access
    - domain: "*.home.example.com"
      subject: "group:adults"
      policy: one_factor

    # Admin services require 2FA
    - domain:
        - "grafana.home.example.com"
        - "auth.home.example.com"
      subject: "group:admin"
      policy: two_factor
```

## Easy Phone Access

1. Install Tailscale on family phones
2. Share your tailnet with family members
3. Bookmark common services (photos, search)

For Immich specifically, install the Immich app and point it to your
`photos.home.example.com` URL.

## Content Filtering Blocklists

Popular blocklist sources for family filtering:

- **Steven Black's Unified Hosts**: Ad + malware + social + gambling + porn
- **Energized Protection**: Comprehensive family-safe filtering
- **OISD Big**: Balanced blocking for ads, trackers, and adult content

Add to your DNS filtering solution's blocklist configuration.

## Tips

- **Shared photo library**: Everyone in the family contributes to Immich
- **Private search**: SearxNG doesn't track or profile anyone
- **Local AI**: Kids can interact with Ollama for homework help (no data leaves home)
- **Git hosting**: Teach kids to code with their own Gitea instance
