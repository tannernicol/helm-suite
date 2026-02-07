#!/usr/bin/env bash
set -euo pipefail

# Helm Suite — Bootstrap Script
# Sets up the directory structure and validates prerequisites.

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BOLD}Helm Suite Bootstrap${NC}"
echo "========================================"

# -- Check prerequisites -------------------------------------------------------
check_cmd() {
    if command -v "$1" &>/dev/null; then
        echo -e "  $1 ${GREEN}✓${NC}"
    else
        echo -e "  $1 ${RED}✗${NC}  (install: $2)"
        MISSING=1
    fi
}

MISSING=0
echo -e "\n${BOLD}Checking prerequisites${NC}"
check_cmd "docker"     "https://docs.docker.com/get-docker/"
check_cmd "caddy"      "https://caddyserver.com/docs/install"
check_cmd "tailscale"  "https://tailscale.com/download"
check_cmd "ollama"     "https://ollama.ai/download"
check_cmd "python3"    "your package manager"

if [[ "$MISSING" -eq 1 ]]; then
    echo -e "\n${RED}Missing prerequisites above. Install them and re-run.${NC}"
    exit 1
fi

# -- Load environment ----------------------------------------------------------
if [[ ! -f .env ]]; then
    echo -e "\n${RED}.env not found. Copy .env.example to .env and fill in your values:${NC}"
    echo "  cp .env.example .env && vim .env"
    exit 1
fi

# shellcheck source=/dev/null
source .env

echo -e "\n${BOLD}Configuration${NC}"
echo "  Domain:     ${DOMAIN:-not set}"
echo "  Data dir:   ${DATA_DIR:-not set}"
echo "  Backup dir: ${BACKUP_DIR:-not set}"

# -- Create directory structure ------------------------------------------------
echo -e "\n${BOLD}Creating directories${NC}"
DATA="${DATA_DIR:-/srv/helm-suite}"
for dir in caddy authelia immich grafana searxng; do
    mkdir -p "${DATA}/${dir}"
    echo "  ${DATA}/${dir} ✓"
done

# -- Summary -------------------------------------------------------------------
echo -e "\n${BOLD}Next steps${NC}"
echo "  1. Configure Caddy:    vim ${DATA}/caddy/Caddyfile"
echo "  2. Configure Authelia:  vim ${DATA}/authelia/configuration.yml"
echo "  3. Start services:     see docs/setup.md"
echo ""
echo -e "${GREEN}Bootstrap complete.${NC}"
