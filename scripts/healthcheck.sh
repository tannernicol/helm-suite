#!/usr/bin/env bash
set -euo pipefail

# Helm Suite — service health check
#
# Checks that all expected services are reachable on their
# local ports. Exits non-zero if any service is down.
#
# Usage:
#   ./scripts/healthcheck.sh                  # check all
#   ./scripts/healthcheck.sh caddy ollama     # check specific services

TAILSCALE_IP="${TAILSCALE_IP:-127.0.0.1}"

declare -A SERVICES=(
  [caddy]="443"
  [authelia]="9091"
  [immich]="2283"
  [ollama]="11434"
  [gitea]="3000"
  [searxng]="8080"
  [grafana]="3000"
)

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

failed=0

check_service() {
  local name="$1"
  local port="${SERVICES[$name]}"

  if timeout 3 bash -c "echo >/dev/tcp/${TAILSCALE_IP}/${port}" 2>/dev/null; then
    printf "  ${GREEN}✓${NC}  %-12s :${port}\n" "$name"
  else
    printf "  ${RED}✗${NC}  %-12s :${port}\n" "$name"
    ((failed++))
  fi
}

targets=("$@")
if [[ ${#targets[@]} -eq 0 ]]; then
  targets=("${!SERVICES[@]}")
fi

echo "Helm Suite — health check"
echo ""

for svc in "${targets[@]}"; do
  if [[ -v "SERVICES[$svc]" ]]; then
    check_service "$svc"
  else
    printf "  ?  %-12s (unknown service)\n" "$svc"
    ((failed++))
  fi
done

echo ""
if [[ $failed -gt 0 ]]; then
  echo "${failed} service(s) unreachable."
  exit 1
else
  echo "All services healthy."
fi
