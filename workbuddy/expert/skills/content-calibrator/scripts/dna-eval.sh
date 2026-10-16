#!/usr/bin/env bash
# dna-eval.sh — DNA 表现评估聚合引擎 wrapper
# 让 agent 走 PATH 调用，零路径拼接。须从 workspace 根调用（PWD 推导 ROOT）。
#
# 用法：
#   dna-eval.sh --platform <platform> --check                       # 廉价阈值检查（heartbeat 每日）
#   dna-eval.sh --platform <platform>                               # 聚合触发 DNA 的证据
#   dna-eval.sh --platform <platform> --dna-id <id> --force         # 手动触发（不达阈值也评估）
#   dna-eval.sh --platform <platform> --mark-evaluated --ids 3,4,5  # 评估完成后标记
set -euo pipefail
SELF="${BASH_SOURCE[0]}"
while [ -L "$SELF" ]; do SELF="$(readlink -f "$SELF")"; done
SCRIPT_DIR="$(cd "$(dirname "$SELF")" && pwd)"
# 默认从 PWD 推导 ROOT（agent 从 workspace 根调用）
export PUBLISHED_TRACK_ROOT="${PUBLISHED_TRACK_ROOT:-$PWD}"
exec python3 "$SCRIPT_DIR/dna-eval.py" "$@"
