#!/usr/bin/env bash
# video-review.sh — video-review 顶层 wrapper（薄转发）
# 让 agent 用 `video-review <成片或项目目录> [参数...]` 走 PATH，零路径拼接。
# 内部转发到 scripts/review.py；wrapper 自身只是 exec 转发，不改语义。
set -euo pipefail
SELF="${BASH_SOURCE[0]}"
# Resolve symlink (wrapper is ln -sfn'd into ~/.xiaobei-workbuddy/bin) so SCRIPT_DIR points at the real skill dir.
while [ -L "$SELF" ]; do SELF="$(readlink -f "$SELF")"; done
SCRIPT_DIR="$(cd "$(dirname "$SELF")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/review.py" "$@"
