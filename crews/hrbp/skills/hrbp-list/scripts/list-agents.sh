#!/bin/bash
# list-agents.sh - 列出所有注册的对外 Crew 及其状态
# 用法: bash ./skills/hrbp-list/scripts/list-agents.sh
# 数据来源: ~/.openclaw/workspace-hrbp/EXTERNAL_CREW_REGISTRY.md（HRBP 维护）
set -e

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
EXTERNAL_REGISTRY="$OPENCLAW_HOME/workspace-hrbp/EXTERNAL_CREW_REGISTRY.md"

if [ ! -f "$EXTERNAL_REGISTRY" ]; then
  echo "❌ External crew registry not found: $EXTERNAL_REGISTRY"
  echo "   No external crews have been recruited yet."
  echo "   Use HRBP recruit flow to add external crew instances."
  exit 1
fi

cat "$EXTERNAL_REGISTRY"
