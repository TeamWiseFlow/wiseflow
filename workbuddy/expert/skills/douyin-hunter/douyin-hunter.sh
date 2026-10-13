#!/usr/bin/env bash
set -euo pipefail
SELF="${BASH_SOURCE[0]}"
while [ -L "$SELF" ]; do SELF="$(readlink -f "$SELF")"; done
SCRIPT_DIR="$(cd "$(dirname "$SELF")" && pwd)"
if [ "${1:-}" = live ]; then
  shift
  exec python3 "$SCRIPT_DIR/../_shared/douyin_live_cli.py" --access read "$@"
fi
exec python3 "$SCRIPT_DIR/scripts/douyin_hunter.py" "$@"
