#!/bin/bash
# modify-agent.sh - 修改外部 Crew Agent 的渠道绑定
# 用法: bash ./skills/hrbp-modify/scripts/modify-agent.sh <agent-id> [--bind <channel>:<accountId>] [--unbind <channel>]
# 注意：此脚本仅适用于对外 Crew（crew-type: external）。内部 Crew 不由 HRBP 管理。
set -e

OPENCLAW_HOME="$HOME/.openclaw"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_TEAM_DIRECTORY_SCRIPT="$SCRIPT_DIR/../../hrbp-common/scripts/sync-team-directory.sh"

source "$SCRIPT_DIR/../../hrbp-common/scripts/lib.sh"

usage() {
  echo "Usage: $0 <agent-id> [--bind <channel>:<accountId>] [--unbind <channel>]"
  echo ""
  echo "Options:"
  echo "  --bind <channel>:<accountId>  Add/update channel binding (Mode B)"
  echo "  --unbind <channel>            Remove channel binding"
  echo ""
  echo "Examples:"
  echo "  $0 developer --bind wechat:wx_xxx"
  echo "  $0 developer --unbind wechat"
  exit 1
}

[ -z "$1" ] && usage
AGENT_ID="$1"
shift

validate_agent_id "$AGENT_ID"

# 安全检查：内部 Crew 不由 HRBP modify 管理
if [ "$AGENT_ID" = "main" ] || [ "$AGENT_ID" = "hrbp" ] || [ "$AGENT_ID" = "it-engineer" ]; then
  echo "❌ Agent '$AGENT_ID' is an internal crew managed by Main Agent, not by HRBP."
  echo "   Internal crew modifications require editing workspace files via setup-crew.sh or direct admin action."
  exit 1
fi

# 验证 crew-type 为 external
WORKSPACE_SOUL="$OPENCLAW_HOME/workspace-$AGENT_ID/SOUL.md"
if [ -f "$WORKSPACE_SOUL" ]; then
  CREW_TYPE="$(grep -m1 '^crew-type:' "$WORKSPACE_SOUL" 2>/dev/null | sed 's/^crew-type:[[:space:]]*//' | tr -d '[:space:]')"
  if [ "$CREW_TYPE" = "internal" ]; then
    echo "❌ Agent '$AGENT_ID' is an internal crew (crew-type: internal). HRBP only manages external crews."
    exit 1
  fi
fi

BIND_CHANNEL=""
BIND_ACCOUNT=""
UNBIND_CHANNEL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --bind)
      [ -z "$2" ] && { echo "❌ --bind requires <channel>:<accountId>"; exit 1; }
      BIND_CHANNEL="${2%%:*}"
      BIND_ACCOUNT="${2#*:}"
      shift 2
      ;;
    --unbind)
      [ -z "$2" ] && { echo "❌ --unbind requires <channel>"; exit 1; }
      UNBIND_CHANNEL="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown option: $1"
      usage
      ;;
  esac
done

[ -z "$BIND_CHANNEL" ] && [ -z "$UNBIND_CHANNEL" ] && {
  echo "❌ Must specify --bind or --unbind"
  usage
}

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

echo "🔧 Modifying external crew agent: $AGENT_ID"

AGENT_ID="$AGENT_ID" CONFIG_PATH="$CONFIG_PATH" UNBIND_CHANNEL="$UNBIND_CHANNEL" BIND_CHANNEL="$BIND_CHANNEL" BIND_ACCOUNT="$BIND_ACCOUNT" node -e "
  const fs = require('fs');
  const c = JSON.parse(fs.readFileSync(process.env.CONFIG_PATH, 'utf8'));
  if (!c.bindings) c.bindings = [];

  const unbindChannel = process.env.UNBIND_CHANNEL || '';
  const bindChannel = process.env.BIND_CHANNEL || '';
  const bindAccount = process.env.BIND_ACCOUNT || '';
  const agentId = process.env.AGENT_ID;

  // Remove binding
  if (unbindChannel) {
    const before = c.bindings.length;
    c.bindings = c.bindings.filter(b =>
      !(b.agentId === agentId && b.match?.channel === unbindChannel)
    );
    if (c.bindings.length < before) {
      console.log('  ✅ Removed binding: ' + unbindChannel);
    } else {
      console.log('  ⚠️  No binding found for ' + unbindChannel);
    }
  }

  // Add binding
  if (bindChannel) {
    // Remove existing binding for same agent+channel
    c.bindings = c.bindings.filter(b =>
      !(b.agentId === agentId && b.match?.channel === bindChannel)
    );
    c.bindings.push({
      agentId,
      match: { channel: bindChannel, accountId: bindAccount },
      comment: agentId + ' direct channel binding'
    });
    console.log('  ✅ Added binding: ' + bindChannel + ':' + bindAccount);
  }

  fs.writeFileSync(process.env.CONFIG_PATH, JSON.stringify(c, null, 2) + '\n');
"

if [ -f "$SYNC_TEAM_DIRECTORY_SCRIPT" ]; then
  OPENCLAW_HOME="$OPENCLAW_HOME" CONFIG_PATH="$CONFIG_PATH" bash "$SYNC_TEAM_DIRECTORY_SCRIPT" >/dev/null 2>&1 || {
    echo "  ⚠️  Failed to sync TEAM_DIRECTORY.md"
  }
fi

echo ""
echo "✅ Agent '$AGENT_ID' modified successfully!"
echo ""
echo "⚠️  Restart Gateway to apply changes: ./scripts/dev.sh gateway"
