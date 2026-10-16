#!/usr/bin/env bash
set -euo pipefail
SELF="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SELF")" && pwd)"
exec python3 "$SCRIPT_DIR/../../../_shared/xhs_live_cli.py" --access write live "$@"
