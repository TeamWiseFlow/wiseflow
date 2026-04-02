#!/bin/bash
# dismiss-internal-crew.sh - 下线内部 Crew（workspace 归档）
# 用法: ./skills/crew-dismiss/scripts/dismiss-internal-crew.sh <agent-id>
set -e

OPENCLAW_HOME="$HOME/.openclaw"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"
SYNC_TEAM_DIRECTORY_SCRIPT="$OPENCLAW_HOME/workspace-hrbp/skills/hrbp-common/scripts/sync-team-directory.sh"

usage() {
  echo "Usage: $0 <agent-id>"
  exit 1
}

[ -z "$1" ] && usage
AGENT_ID="$1"

if ! printf '%s\n' "$AGENT_ID" | grep -Eq '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'; then
  echo "❌ Invalid agent-id: $AGENT_ID"
  exit 1
fi

# 内置保护名单
if [ "$AGENT_ID" = "main" ] || [ "$AGENT_ID" = "hrbp" ] || [ "$AGENT_ID" = "it-engineer" ]; then
  echo "❌ '$AGENT_ID' is a protected built-in agent and cannot be dismissed."
  exit 1
fi

if [ ! -f "$CONFIG_PATH" ]; then
  echo "❌ Config not found: $CONFIG_PATH"
  exit 1
fi

# 验证 agent 存在
if ! AGENT_ID="$AGENT_ID" CONFIG_PATH="$CONFIG_PATH" node -e "
  const c = JSON.parse(require('fs').readFileSync(process.env.CONFIG_PATH, 'utf8'));
  const exists = (c.agents?.list || []).some((a) => a.id === process.env.AGENT_ID);
  process.exit(exists ? 0 : 1);
" 2>/dev/null; then
  echo "❌ Agent '$AGENT_ID' not found in openclaw.json"
  exit 1
fi

# 验证目标是 internal crew
WORKSPACE="$OPENCLAW_HOME/workspace-$AGENT_ID"
SOUL_FILE="$WORKSPACE/SOUL.md"
CREW_TYPE="external"
if [ -f "$SOUL_FILE" ]; then
  CREW_TYPE="$(grep -m1 '^crew-type:' "$SOUL_FILE" 2>/dev/null | sed 's/^crew-type:[[:space:]]*//' | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')"
fi
if [ "$CREW_TYPE" != "internal" ]; then
  echo "❌ Agent '$AGENT_ID' is not an internal crew (crew-type: $CREW_TYPE)."
  echo "   External crew lifecycle is managed by HRBP."
  exit 1
fi

echo "🗑️  Dismissing internal crew: $AGENT_ID"

# 从配置移除
AGENT_ID="$AGENT_ID" CONFIG_PATH="$CONFIG_PATH" node -e "
  const fs = require('fs');
  const c = JSON.parse(fs.readFileSync(process.env.CONFIG_PATH, 'utf8'));
  const id = process.env.AGENT_ID;

  if (Array.isArray(c.agents?.list)) {
    c.agents.list = c.agents.list.filter((a) => a.id !== id);
  }

  const main = (c.agents?.list || []).find((a) => a.id === 'main');
  if (main?.subagents?.allowAgents) {
    main.subagents.allowAgents = main.subagents.allowAgents.filter((aid) => aid !== id);
  }

  if (Array.isArray(c.bindings)) {
    c.bindings = c.bindings.filter((b) => b.agentId !== id);
  }

  fs.writeFileSync(process.env.CONFIG_PATH, JSON.stringify(c, null, 2) + '\n');
"
echo "  ✅ Removed from openclaw.json"

# 归档 workspace（不直接删除）
if [ -d "$WORKSPACE" ]; then
  ARCHIVE_DIR="$OPENCLAW_HOME/archived"
  mkdir -p "$ARCHIVE_DIR"
  TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
  ARCHIVE_DEST="$ARCHIVE_DIR/workspace-$AGENT_ID-$TIMESTAMP"
  mv "$WORKSPACE" "$ARCHIVE_DEST"
  echo "  ✅ Workspace archived to: $ARCHIVE_DEST"
else
  echo "  ⚠️  No workspace found at $WORKSPACE"
fi

if [ -f "$SYNC_TEAM_DIRECTORY_SCRIPT" ]; then
  OPENCLAW_HOME="$OPENCLAW_HOME" CONFIG_PATH="$CONFIG_PATH" bash "$SYNC_TEAM_DIRECTORY_SCRIPT" >/dev/null 2>&1 || {
    echo "  ⚠️  Failed to sync TEAM_DIRECTORY.md"
  }
fi

echo ""
echo "✅ Internal crew '$AGENT_ID' dismissed successfully!"
echo "⚠️  Restart Gateway to apply changes: ./scripts/dev.sh gateway"
