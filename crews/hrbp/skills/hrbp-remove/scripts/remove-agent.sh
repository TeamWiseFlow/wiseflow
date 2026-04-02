#!/bin/bash
# remove-agent.sh - 从 openclaw.json 移除外部 Crew Agent（workspace 归档不删除）
# 用法: bash ./skills/hrbp-remove/scripts/remove-agent.sh <agent-id>
# 注意：此脚本仅适用于对外 Crew（crew-type: external）。内部 Crew 不由 HRBP 管理。
set -e

OPENCLAW_HOME="$HOME/.openclaw"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_TEAM_DIRECTORY_SCRIPT="$SCRIPT_DIR/../../hrbp-common/scripts/sync-team-directory.sh"

source "$SCRIPT_DIR/../../hrbp-common/scripts/lib.sh"

usage() {
  echo "Usage: $0 <agent-id>"
  echo ""
  echo "Removes an agent from openclaw.json and archives its workspace."
  echo "Protected agents (main, hrbp, it-engineer) cannot be removed."
  exit 1
}

[ -z "$1" ] && usage
AGENT_ID="$1"

validate_agent_id "$AGENT_ID"

# 安全检查：保护内部 Crew — main、hrbp 和 it-engineer
if [ "$AGENT_ID" = "main" ] || [ "$AGENT_ID" = "hrbp" ] || [ "$AGENT_ID" = "it-engineer" ]; then
  echo "❌ Agent '$AGENT_ID' is an internal crew and cannot be removed by HRBP."
  echo "   Internal crews are managed by Main Agent via setup-crew.sh."
  exit 1
fi

# 验证 crew-type 为 external（防止误删内部 Crew）
WORKSPACE_SOUL="$OPENCLAW_HOME/workspace-$AGENT_ID/SOUL.md"
if [ -f "$WORKSPACE_SOUL" ]; then
  CREW_TYPE="$(grep -m1 '^crew-type:' "$WORKSPACE_SOUL" 2>/dev/null | sed 's/^crew-type:[[:space:]]*//' | tr -d '[:space:]')"
  if [ "$CREW_TYPE" = "internal" ]; then
    echo "❌ Agent '$AGENT_ID' is an internal crew (crew-type: internal). HRBP only manages external crews."
    exit 1
  fi
fi

# 验证 openclaw.json 存在
if [ ! -f "$CONFIG_PATH" ]; then
  echo "❌ Config not found: $CONFIG_PATH"
  exit 1
fi

# 验证 agent 存在
if ! AGENT_ID="$AGENT_ID" CONFIG_PATH="$CONFIG_PATH" node -e "
  const c = JSON.parse(require('fs').readFileSync(process.env.CONFIG_PATH, 'utf8'));
  const exists = (c.agents?.list || []).some(a => a.id === process.env.AGENT_ID);
  process.exit(exists ? 0 : 1);
" 2>/dev/null; then
  echo "❌ Agent '$AGENT_ID' not found in openclaw.json"
  exit 1
fi

echo "🗑️  Removing external crew agent: $AGENT_ID"

# 1. 从 openclaw.json 移除
AGENT_ID="$AGENT_ID" CONFIG_PATH="$CONFIG_PATH" node -e "
  const fs = require('fs');
  const c = JSON.parse(fs.readFileSync(process.env.CONFIG_PATH, 'utf8'));
  const agentId = process.env.AGENT_ID;

  // 从 agents.list 移除
  if (c.agents?.list) {
    c.agents.list = c.agents.list.filter(a => a.id !== agentId);
  }

  // 从 Main Agent 的 allowAgents 移除
  const main = (c.agents?.list || []).find(a => a.id === 'main');
  if (main?.subagents?.allowAgents) {
    main.subagents.allowAgents = main.subagents.allowAgents.filter(id => id !== agentId);
  }

  // 从 bindings 移除
  if (c.bindings) {
    c.bindings = c.bindings.filter(b => b.agentId !== agentId);
  }

  fs.writeFileSync(process.env.CONFIG_PATH, JSON.stringify(c, null, 2) + '\n');
"
echo "  ✅ Removed from openclaw.json"

# 2. 归档 workspace（不直接删除）
WORKSPACE="$OPENCLAW_HOME/workspace-$AGENT_ID"
if [ -d "$WORKSPACE" ]; then
  ARCHIVE_DIR="$OPENCLAW_HOME/archived"
  mkdir -p "$ARCHIVE_DIR"
  TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  ARCHIVE_DEST="$ARCHIVE_DIR/workspace-$AGENT_ID-$TIMESTAMP"
  mv "$WORKSPACE" "$ARCHIVE_DEST"
  echo "  ✅ Workspace archived to: $ARCHIVE_DEST"
else
  echo "  ⚠️  No workspace found at $WORKSPACE"
fi

# 3. 更新 HRBP 的 EXTERNAL_CREW_REGISTRY.md
HRBP_REGISTRY="$OPENCLAW_HOME/workspace-hrbp/EXTERNAL_CREW_REGISTRY.md"
if [ -f "$HRBP_REGISTRY" ]; then
  if grep -q "^| $AGENT_ID " "$HRBP_REGISTRY" 2>/dev/null; then
    TMP_REGISTRY="$(mktemp "${HRBP_REGISTRY}.tmp.XXXXXX")"
    grep -v "^| $AGENT_ID " "$HRBP_REGISTRY" > "$TMP_REGISTRY"
    mv "$TMP_REGISTRY" "$HRBP_REGISTRY"
    echo "  ✅ Removed from HRBP EXTERNAL_CREW_REGISTRY.md"
  fi
fi

if [ -f "$SYNC_TEAM_DIRECTORY_SCRIPT" ]; then
  OPENCLAW_HOME="$OPENCLAW_HOME" CONFIG_PATH="$CONFIG_PATH" bash "$SYNC_TEAM_DIRECTORY_SCRIPT" >/dev/null 2>&1 || {
    echo "  ⚠️  Failed to sync TEAM_DIRECTORY.md"
  }
fi

echo ""
echo "✅ Agent '$AGENT_ID' removed successfully!"
echo "   Workspace archived (not deleted) — can be recovered from:"
echo "   $ARCHIVE_DIR/"
echo ""
echo "⚠️  Restart Gateway to apply changes: ./scripts/dev.sh gateway"
