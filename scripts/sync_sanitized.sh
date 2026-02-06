#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${RSYNC_SOURCE:-}" ]]; then
  echo "Set RSYNC_SOURCE to the internal source directory" >&2
  exit 1
fi

rsync -av --delete "$RSYNC_SOURCE/" ./docs/
python3 scripts/redact.py --self-check
