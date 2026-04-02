#!/bin/bash
# list-internal-crews.sh - 列出所有内部 Crew 实例
# 数据来源: ~/.openclaw/crew_templates/TEAM_DIRECTORY.md
set -e

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
TEAM_DIRECTORY_PATH="$OPENCLAW_HOME/crew_templates/TEAM_DIRECTORY.md"

if [ ! -f "$TEAM_DIRECTORY_PATH" ]; then
  echo "❌ Internal crew directory not found: $TEAM_DIRECTORY_PATH"
  echo "   Run ./scripts/setup-crew.sh to regenerate it."
  exit 1
fi

cat "$TEAM_DIRECTORY_PATH"
