#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Helm Suite Bootstrap
# Reads .env, checks prerequisites, generates configs, creates systemd services.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

# -- Colors -------------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; }
header() { echo -e "\n${BOLD}$*${NC}\n$(printf '=%.0s' {1..60})"; }

# -- Load .env ----------------------------------------------------------------
if [[ ! -f "$ENV_FILE" ]]; then
    fail ".env file not found. Copy .env.example to .env and fill in your values."
    echo "  cp .env.example .env"
    exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

info "Loaded config for domain: ${DOMAIN}"

# -- Prerequisite Checks -----------------------------------------------------
header "Checking Prerequisites"

check_cmd() {
    local cmd="$1"
    local name="${2:-$1}"
    local install_hint="${3:-}"
    if command -v "$cmd" &>/dev/null; then
        ok "$name found: $(command -v "$cmd")"
        return 0
    else
        fail "$name not found.${install_hint:+ Install: $install_hint}"
        return 1
    fi
}

PREREQ_OK=true

check_cmd docker "Docker" "https://docs.docker.com/engine/install/" || PREREQ_OK=false
check_cmd "docker compose" "Docker Compose" "Included with Docker Desktop or docker-compose-plugin" 2>/dev/null || \
    check_cmd docker-compose "Docker Compose" "https://docs.docker.com/compose/install/" || PREREQ_OK=false
check_cmd tailscale "Tailscale" "https://tailscale.com/download" || PREREQ_OK=false
check_cmd envsubst "envsubst (gettext)" "sudo apt install gettext / sudo dnf install gettext" || PREREQ_OK=false

# Check Tailscale is connected
if command -v tailscale &>/dev/null; then
    if tailscale status &>/dev/null; then
        TS_IP=$(tailscale ip -4 2>/dev/null || echo "unknown")
        ok "Tailscale connected (IP: ${TS_IP})"
        if [[ "$TS_IP" != "$TAILSCALE_IP" && "$TAILSCALE_IP" != "100.x.x.x" ]]; then
            warn "Tailscale IP ($TS_IP) differs from .env TAILSCALE_IP ($TAILSCALE_IP)"
            warn "Updating TAILSCALE_IP to $TS_IP for this run"
            export TAILSCALE_IP="$TS_IP"
        fi
    else
        warn "Tailscale installed but not connected. Run: sudo tailscale up"
    fi
fi

# Check GPU if enabled
if [[ "${GPU_ENABLED:-false}" == "true" ]]; then
    if command -v nvidia-smi &>/dev/null; then
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1)
        ok "NVIDIA GPU found: ${GPU_NAME}"

        if command -v nvidia-container-runtime &>/dev/null || \
           docker info 2>/dev/null | grep -q nvidia; then
            ok "NVIDIA Container Toolkit installed"
        else
            warn "NVIDIA Container Toolkit not found. GPU containers won't work."
            warn "Install: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
        fi
    else
        warn "GPU_ENABLED=true but nvidia-smi not found. Disabling GPU features."
        export GPU_ENABLED=false
    fi
fi

if [[ "$PREREQ_OK" == "false" ]]; then
    fail "Missing prerequisites. Install them and re-run setup.sh"
    exit 1
fi

# -- Create Directories -------------------------------------------------------
header "Creating Directory Structure"

dirs=(
    "/srv/helm-suite"
    "/srv/helm-suite/caddy"
    "/srv/helm-suite/authelia"
    "/srv/helm-suite/gitea/data"
    "/srv/helm-suite/gitea/config"
    "/srv/helm-suite/immich/upload"
    "/srv/helm-suite/immich/postgres"
    "/srv/helm-suite/grafana/data"
    "/srv/helm-suite/searxng/config"
    "/srv/helm-suite/ollama/models"
    "/srv/helm-suite/monitoring"
)

for dir in "${dirs[@]}"; do
    if [[ ! -d "$dir" ]]; then
        sudo mkdir -p "$dir"
        sudo chown "$(id -u):$(id -g)" "$dir"
        ok "Created $dir"
    else
        ok "Exists: $dir"
    fi
done

# -- Generate Caddyfile -------------------------------------------------------
header "Generating Caddyfile"

CADDY_OUT="/srv/helm-suite/caddy/Caddyfile"

envsubst < "${SCRIPT_DIR}/infra/caddy/Caddyfile.template" > "$CADDY_OUT"
ok "Generated ${CADDY_OUT}"

# Generate site configs
for site_template in "${SCRIPT_DIR}"/infra/caddy/sites/*.caddy; do
    [[ -f "$site_template" ]] || continue
    site_name=$(basename "$site_template")
    envsubst < "$site_template" > "/srv/helm-suite/caddy/sites_${site_name}"
    ok "Generated site: ${site_name}"
done

# Copy snippets
cp "${SCRIPT_DIR}"/infra/caddy/snippets/*.caddy /srv/helm-suite/caddy/ 2>/dev/null || true
ok "Copied Caddy snippets"

# -- Generate Authelia Config -------------------------------------------------
header "Generating Authelia Configuration"

AUTHELIA_OUT="/srv/helm-suite/authelia/configuration.yml"
envsubst < "${SCRIPT_DIR}/infra/authelia/configuration.yml.template" > "$AUTHELIA_OUT"
ok "Generated ${AUTHELIA_OUT}"

# -- Generate Docker Compose Env Files ----------------------------------------
header "Generating Docker Compose Environment"

# Create a shared .env for docker compose files
COMPOSE_ENV="/srv/helm-suite/.env"
cat > "$COMPOSE_ENV" << EOF
# Auto-generated by setup.sh -- do not edit manually
DOMAIN=${DOMAIN}
TAILSCALE_IP=${TAILSCALE_IP}
TIMEZONE=${TIMEZONE:-America/Los_Angeles}
USERNAME=${USERNAME}
GPU_ENABLED=${GPU_ENABLED}
OLLAMA_PORT=${OLLAMA_PORT}
GITEA_HTTP_PORT=${GITEA_HTTP_PORT}
GITEA_SSH_PORT=${GITEA_SSH_PORT}
IMMICH_PORT=${IMMICH_PORT}
SEARXNG_PORT=${SEARXNG_PORT}
AUTHELIA_PORT=${AUTHELIA_PORT}
GRAFANA_PORT=${GRAFANA_PORT}
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
IMMICH_DB_USERNAME=${IMMICH_DB_USERNAME:-immich}
IMMICH_DB_PASSWORD=${IMMICH_DB_PASSWORD}
IMMICH_DB_NAME=${IMMICH_DB_NAME:-immich}
IMMICH_UPLOAD_LOCATION=${IMMICH_UPLOAD_LOCATION:-/srv/helm-suite/immich/upload}
IMMICH_DB_DATA_LOCATION=${IMMICH_DB_DATA_LOCATION:-/srv/helm-suite/immich/postgres}
NTFY_TOPIC=${NTFY_TOPIC:-helm-suite-alerts}
EOF
ok "Generated ${COMPOSE_ENV}"

# -- Generate Systemd Services ------------------------------------------------
header "Generating Systemd Services"

SYSTEMD_OUT="${HOME}/.config/systemd/user"
mkdir -p "$SYSTEMD_OUT"

# Caddy service (system-level, needs sudo)
CADDY_SERVICE="/etc/systemd/system/caddy-sovereign.service"
if [[ ! -f "$CADDY_SERVICE" ]]; then
    sudo tee "$CADDY_SERVICE" > /dev/null << EOF
[Unit]
Description=Caddy Reverse Proxy (Helm Suite)
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=exec
User=${USERNAME}
ExecStart=/usr/bin/caddy run --config /srv/helm-suite/caddy/Caddyfile
ExecReload=/usr/bin/caddy reload --config /srv/helm-suite/caddy/Caddyfile
Restart=always
RestartSec=10
TimeoutStartSec=30
TimeoutStopSec=30
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
EOF
    ok "Created ${CADDY_SERVICE}"
else
    ok "Exists: ${CADDY_SERVICE}"
fi

# Backup timer
BACKUP_SERVICE="${SYSTEMD_OUT}/sovereign-backup.service"
cat > "$BACKUP_SERVICE" << EOF
[Unit]
Description=Helm Suite Backup

[Service]
Type=oneshot
ExecStart=${SCRIPT_DIR}/scripts/backup
Nice=15
IOSchedulingClass=idle
EOF

BACKUP_TIMER="${SYSTEMD_OUT}/sovereign-backup.timer"
cat > "$BACKUP_TIMER" << EOF
[Unit]
Description=Run Helm Suite backup ${BACKUP_SCHEDULE:-daily}

[Timer]
OnCalendar=${BACKUP_SCHEDULE:-daily}
Persistent=true
RandomizedDelaySec=600

[Install]
WantedBy=timers.target
EOF
ok "Created backup timer (${BACKUP_SCHEDULE:-daily})"

# Reload systemd
systemctl --user daemon-reload 2>/dev/null || true
sudo systemctl daemon-reload 2>/dev/null || true

# -- Pull Ollama Models -------------------------------------------------------
if command -v docker &>/dev/null && [[ "${OLLAMA_MODELS:-}" ]]; then
    header "Ollama Model Setup"
    info "Models to pull: ${OLLAMA_MODELS}"
    info "Start Ollama first, then pull models:"
    echo ""
    echo "  cd ${SCRIPT_DIR}/infra/compose/ollama && docker compose up -d"
    IFS=',' read -ra MODELS <<< "$OLLAMA_MODELS"
    for model in "${MODELS[@]}"; do
        model=$(echo "$model" | xargs)
        echo "  docker exec ollama ollama pull ${model}"
    done
    echo ""
fi

# -- Summary ------------------------------------------------------------------
header "Setup Complete"

echo -e "
${GREEN}Configuration generated successfully.${NC}

${BOLD}Generated files:${NC}
  ${DIM}Caddyfile:${NC}      /srv/helm-suite/caddy/Caddyfile
  ${DIM}Authelia:${NC}       /srv/helm-suite/authelia/configuration.yml
  ${DIM}Shared .env:${NC}    /srv/helm-suite/.env
  ${DIM}Caddy service:${NC}  /etc/systemd/system/caddy-sovereign.service
  ${DIM}Backup timer:${NC}   ~/.config/systemd/user/sovereign-backup.timer

${BOLD}Next steps:${NC}
  1. Start services:
     cd ${SCRIPT_DIR}/infra/compose/ollama && docker compose up -d
     cd ${SCRIPT_DIR}/infra/compose/gitea && docker compose up -d
     cd ${SCRIPT_DIR}/infra/compose/authelia && docker compose up -d
     cd ${SCRIPT_DIR}/infra/compose/searxng && docker compose up -d
     cd ${SCRIPT_DIR}/infra/compose/immich && docker compose up -d
     cd ${SCRIPT_DIR}/infra/compose/monitoring && docker compose up -d

  2. Start Caddy:
     sudo systemctl enable --now caddy-sovereign

  3. Enable backup timer:
     systemctl --user enable --now sovereign-backup.timer

  4. Check status:
     ${SCRIPT_DIR}/scripts/homelab status

  5. Run security audit:
     ${SCRIPT_DIR}/scripts/security-audit

${BOLD}Access:${NC}
  https://git.${DOMAIN}      -- Gitea
  https://photos.${DOMAIN}   -- Immich
  https://search.${DOMAIN}   -- SearxNG
  https://grafana.${DOMAIN}  -- Grafana
  https://auth.${DOMAIN}     -- Authelia
"
