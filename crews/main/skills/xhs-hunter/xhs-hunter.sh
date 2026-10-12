#!/usr/bin/env bash
set -euo pipefail
SELF="$(readlink -f "${BASH_SOURCE[0]}")"
SKILL_DIR="$(cd "$(dirname "$SELF")" && pwd)"
if [ "${1:-}" = live ]; then
  shift
  exec python3 "$SKILL_DIR/../_shared/xhs_live_cli.py" --access read live "$@"
fi
exec python3 "$SKILL_DIR/scripts/xhs_hunter.py" "$@"
