#!/bin/bash
# recruit-internal-crew.sh - 注册新内部 Crew 到 openclaw.json
# 用法: ./skills/crew-recruit/scripts/recruit-internal-crew.sh <agent-id> [--template <id>] [--bind <channel>:<accountId>] [--note <text>]
# 内部 Crew 特点：自动加入 Main Agent 的 allowAgents，使用继承模式技能
set -e

OPENCLAW_HOME="$HOME/.openclaw"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 复用 HRBP 的公共库和 add-agent 脚本
HRBP_SKILLS_BASE="$OPENCLAW_HOME/workspace-hrbp/skills"
ADD_AGENT_SCRIPT="$HRBP_SKILLS_BASE/hrbp-recruit/scripts/add-agent.sh"

if [ ! -f "$ADD_AGENT_SCRIPT" ]; then
  echo "❌ add-agent.sh not found at: $ADD_AGENT_SCRIPT"
  echo "   Ensure HRBP workspace is installed (run setup-crew.sh)."
  exit 1
fi

[ -z "$1" ] && {
  echo "Usage: $0 <agent-id> [--template <id>] [--bind <channel>:<accountId>] [--note <text>]"
  exit 1
}

AGENT_ID="$1"
shift

# 内置保护名单
if [ "$AGENT_ID" = "main" ] || [ "$AGENT_ID" = "hrbp" ] || [ "$AGENT_ID" = "it-engineer" ]; then
  echo "❌ '$AGENT_ID' is a protected built-in agent and cannot be recreated."
  exit 1
fi

# 传递给 add-agent.sh，强制 crew-type=internal
exec bash "$ADD_AGENT_SCRIPT" "$AGENT_ID" --crew-type internal "$@"
