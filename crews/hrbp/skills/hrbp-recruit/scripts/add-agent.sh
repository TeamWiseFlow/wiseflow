#!/bin/bash
# add-agent.sh - 注册新 Agent 到 openclaw.json
# 用法: bash ./skills/hrbp-recruit/scripts/add-agent.sh <agent-id> [--crew-type <internal|external>] [--bind <channel>:<accountId>] [--builtin-skills <skill1,skill2|all>] [--template-id <template-id>] [--note <text>]
#
# crew-type 决定技能解析模式：
#   internal（对内 Crew）：inherit 模式 —— 基线技能 + 额外 - 拒绝 + workspace
#                         项目级 / add-on 全局 skills 不自动继承，需在 BUILTIN_SKILLS 显式声明
#                         加入 Main Agent 的 allowAgents（可通过 spawn 路由）
#   external（对外 Crew）：declare 模式 —— 仅 DECLARED_SKILLS + workspace 技能
#                         不加入 allowAgents（bind-only，不可通过 Main Agent 路由）
#
# 默认 crew-type = external（对外更受控，更安全）
set -e

OPENCLAW_HOME="$HOME/.openclaw"
CONFIG_PATH="$OPENCLAW_HOME/openclaw.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_TEAM_DIRECTORY_SCRIPT="$SCRIPT_DIR/../../hrbp-common/scripts/sync-team-directory.sh"

source "$SCRIPT_DIR/../../hrbp-common/scripts/lib.sh"

usage() {
  echo "Usage: $0 <agent-id> [--crew-type <internal|external>] [--bind <channel>:<accountId>] [--builtin-skills <skill1,skill2|all>] [--template-id <template-id>] [--note <text>]"
  echo ""
  echo "Options:"
  echo "  --crew-type <type>            Crew type: 'internal' or 'external' (default: external)"
  echo "  --bind <channel>:<accountId>  Bind agent to a channel (Mode B direct routing)"
  echo "  --builtin-skills <skills>     [internal only] Additional bundled skills (comma-separated)"
  echo "  --template-id <template-id>   Source template id (for registry)"
  echo "  --note <text>                 Optional note (for registry)"
  echo ""
  echo "Examples:"
  echo "  $0 cs-product-a --crew-type external --bind feishu:product-a-bot"
  echo "  $0 sales-analyst --crew-type internal --template-id developer --note '销售数据分析'"
  exit 1
}

split_skill_tokens() {
  local raw="$1"
  printf '%s\n' "$raw" \
    | sed 's/#.*$//' \
    | tr ',' '\n' \
    | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' \
    | awk 'NF'
}

list_default_global_skill_names() {
  cat <<'EOF'
1password
healthcheck
model-usage
nano-pdf
skill-creator
ordercli
session-logs
tmux
weather
xurl
video-frames
EOF
}

list_workspace_skill_names() {
  local workspace_dir="$1"
  local workspace_skills_dir="$workspace_dir/skills"

  if [ ! -d "$workspace_skills_dir" ]; then
    return
  fi

  for skill_dir in "$workspace_skills_dir"/*/; do
    [ -d "$skill_dir" ] || continue
    if [ -f "${skill_dir}SKILL.md" ]; then
      basename "$skill_dir"
    fi
  done | sort
}

find_bundled_skills_dir() {
  if [ -n "$OPENCLAW_BUNDLED_SKILLS_DIR" ] && [ -d "$OPENCLAW_BUNDLED_SKILLS_DIR" ]; then
    printf '%s\n' "$OPENCLAW_BUNDLED_SKILLS_DIR"
    return
  fi

  if command -v openclaw >/dev/null 2>&1; then
    local openclaw_bin=""
    openclaw_bin="$(command -v openclaw)"
    local sibling_skills_dir
    sibling_skills_dir="$(cd "$(dirname "$openclaw_bin")" && pwd)/skills"
    if [ -d "$sibling_skills_dir" ]; then
      printf '%s\n' "$sibling_skills_dir"
      return
    fi
  fi

  local current_dir=""
  current_dir="$(cd "$(dirname "$0")" && pwd)"
  local i=0
  while [ "$i" -lt 10 ]; do
    if [ -d "$current_dir/openclaw/skills" ]; then
      printf '%s\n' "$current_dir/openclaw/skills"
      return
    fi
    local parent_dir=""
    parent_dir="$(dirname "$current_dir")"
    [ "$parent_dir" = "$current_dir" ] && break
    current_dir="$parent_dir"
    i=$((i + 1))
  done
}

list_bundled_skill_names() {
  local bundled_dir="$1"
  [ -n "$bundled_dir" ] || return
  [ -d "$bundled_dir" ] || return

  local disabled_skills=""
  disabled_skills="$(
    CONFIG_PATH="$CONFIG_PATH" node -e '
const fs = require("fs");
const path = process.env.CONFIG_PATH;
if (!path || !fs.existsSync(path)) process.exit(0);
try {
  const c = JSON.parse(fs.readFileSync(path, "utf8"));
  const entries = c?.skills?.entries || {};
  for (const [name, entry] of Object.entries(entries)) {
    if (entry && entry.enabled === false) console.log(name);
  }
} catch (_) {}
'
  )"

  for skill_dir in "$bundled_dir"/*/; do
    [ -d "$skill_dir" ] || continue
    if [ -f "${skill_dir}SKILL.md" ]; then
      local skill_name
      skill_name="$(basename "$skill_dir")"
      if [ -n "$disabled_skills" ] && printf '%s\n' "$disabled_skills" | grep -Fxq "$skill_name"; then
        continue
      fi
      printf '%s\n' "$skill_name"
    fi
  done | sort
}

resolve_denied_skill_names() {
  local denied_file="$1"
  [ -f "$denied_file" ] || return 0
  split_skill_tokens "$(cat "$denied_file")"
}

resolve_additional_bundled_skill_names() {
  local raw_tokens="$1"
  local bundled_dir="$2"
  local tokens=""
  tokens="$(split_skill_tokens "$raw_tokens")"

  [ -n "$tokens" ] || return 0

  if printf '%s\n' "$tokens" | grep -Eiq '^(all|\*)$'; then
    local available=""
    available="$(list_bundled_skill_names "$bundled_dir")"
    if [ -n "$available" ]; then
      printf '%s\n' "$available"
      return
    fi
    echo "  ⚠️  Cannot resolve bundled skills for 'all'. Set OPENCLAW_BUNDLED_SKILLS_DIR or pass explicit skill names." >&2
    return
  fi

  while IFS= read -r token; do
    [ -n "$token" ] || continue
    printf '%s\n' "$token"
  done <<< "$tokens"
}

# 读取对外 Crew 的声明式技能列表
list_declared_skill_names() {
  local declared_file="$1"
  [ -f "$declared_file" ] || return 0
  split_skill_tokens "$(cat "$declared_file")" \
    | grep -Ev '^(self-improving|self-improve)$' \
    | sort -u
}

# 构建技能 JSON
# crew_type = "internal" → inherit 模式（基线 + 额外 - 拒绝 + workspace）
# crew_type = "external" → declare 模式（DECLARED_SKILLS + workspace 只）
build_agent_skills_json() {
  local workspace_dir="$1"
  local bundled_raw="$2"
  local denied_names="$3"
  local bundled_dir="$4"
  local crew_type="${5:-external}"

  local workspace_skills=""
  workspace_skills="$(list_workspace_skill_names "$workspace_dir")"

  if [ "$crew_type" = "external" ]; then
    # declare 模式：仅 DECLARED_SKILLS + workspace
    local declared_file="$workspace_dir/DECLARED_SKILLS"
    local declared_skills=""
    declared_skills="$(list_declared_skill_names "$declared_file")"

    printf '%s\n%s\n' "$declared_skills" "$workspace_skills" \
      | awk 'NF && !seen[$0]++' \
      | node -e '
const fs = require("fs");
const lines = fs.readFileSync(0, "utf8")
  .split(/\r?\n/)
  .map((line) => line.trim())
  .filter(Boolean);
console.log(JSON.stringify(Array.from(new Set(lines))));
'
    return
  fi

  # inherit 模式（internal crew）
  local baseline_bundled=""
  baseline_bundled="$(list_default_global_skill_names)"
  local additional_bundled=""
  additional_bundled="$(resolve_additional_bundled_skill_names "$bundled_raw" "$bundled_dir")"

  local merged_global_skills=""
  merged_global_skills="$(printf '%s\n%s\n' "$baseline_bundled" "$additional_bundled" \
    | awk 'NF && !seen[$0]++')"

  local allowed_bundled=""
  if [ -n "$denied_names" ]; then
    while IFS= read -r skill; do
      [ -n "$skill" ] || continue
      if ! printf '%s\n' "$denied_names" | grep -Fxq "$skill"; then
        allowed_bundled="$allowed_bundled"$'\n'"$skill"
      fi
    done <<< "$merged_global_skills"
  else
    allowed_bundled="$merged_global_skills"
  fi

  printf '%s\n%s\n' "$allowed_bundled" "$workspace_skills" \
    | awk 'NF && !seen[$0]++' \
    | node -e '
const fs = require("fs");
const lines = fs.readFileSync(0, "utf8")
  .split(/\r?\n/)
  .map((line) => line.trim())
  .filter(Boolean);
console.log(JSON.stringify(Array.from(new Set(lines))));
'
}

[ -z "$1" ] && usage
AGENT_ID="$1"
shift

validate_agent_id "$AGENT_ID"

CREW_TYPE="external"  # 默认 external（更安全）
BIND_CHANNEL=""
BIND_ACCOUNT=""
BUILTIN_SKILLS_RAW=""
TEMPLATE_ID=""
RECRUIT_NOTE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --crew-type)
      [ -z "$2" ] && { echo "❌ --crew-type requires <internal|external>"; exit 1; }
      case "$2" in
        internal|external) CREW_TYPE="$2" ;;
        *) echo "❌ Invalid crew-type: $2 (must be 'internal' or 'external')"; exit 1 ;;
      esac
      shift 2
      ;;
    --bind)
      [ -z "$2" ] && { echo "❌ --bind requires <channel>:<accountId>"; exit 1; }
      BIND_CHANNEL="${2%%:*}"
      BIND_ACCOUNT="${2#*:}"
      shift 2
      ;;
    --builtin-skills)
      [ -z "$2" ] && { echo "❌ --builtin-skills requires <skill1,skill2|all>"; exit 1; }
      BUILTIN_SKILLS_RAW="$2"
      shift 2
      ;;
    --template-id)
      [ -z "$2" ] && { echo "❌ --template-id requires <template-id>"; exit 1; }
      TEMPLATE_ID="$2"
      shift 2
      ;;
    --template)
      [ -z "$2" ] && { echo "❌ --template requires <template-id>"; exit 1; }
      TEMPLATE_ID="$2"
      shift 2
      ;;
    --note)
      [ -z "$2" ] && { echo "❌ --note requires <text>"; exit 1; }
      RECRUIT_NOTE="$2"
      shift 2
      ;;
    *)
      echo "❌ Unknown option: $1"
      usage
      ;;
  esac
done

[ -n "$TEMPLATE_ID" ] || TEMPLATE_ID="$AGENT_ID"
[ -n "$RECRUIT_NOTE" ] || RECRUIT_NOTE="auto-registered by hrbp-recruit"

sanitize_inline_text() {
  local raw="$1"
  printf '%s\n' "$raw" \
    | tr '\n' ' ' \
    | sed 's/[|]/\//g; s/[[:space:]]\+/ /g; s/^ //; s/ $//'
}

TEMPLATE_ID_SANITIZED="$(sanitize_inline_text "$TEMPLATE_ID")"
RECRUIT_NOTE_SANITIZED="$(sanitize_inline_text "$RECRUIT_NOTE")"
TODAY_DATE="$(date +%F)"

# 验证 workspace 存在
WORKSPACE="$OPENCLAW_HOME/workspace-$AGENT_ID"
if [ ! -d "$WORKSPACE" ]; then
  echo "❌ Workspace not found: $WORKSPACE"
  echo "   Create the workspace first, then run this script."
  exit 1
fi

# 对外 Crew 安全约束：必须声明技能，且必须有反馈目录
if [ "$CREW_TYPE" = "external" ]; then
  DECLARED_FILE="$WORKSPACE/DECLARED_SKILLS"
  if [ ! -f "$DECLARED_FILE" ]; then
    echo "❌ External crew requires DECLARED_SKILLS: $DECLARED_FILE"
    echo "   External crews use declare-mode and must explicitly declare allowed skills."
    exit 1
  fi
  if split_skill_tokens "$(cat "$DECLARED_FILE")" | grep -Eq '^(self-improving|self-improve)$'; then
    echo "❌ External crew cannot declare self-improving skills."
    exit 1
  fi
  mkdir -p "$WORKSPACE/feedback"
fi

BUILTIN_FILE="$WORKSPACE/BUILTIN_SKILLS"
if [ -z "$BUILTIN_SKILLS_RAW" ] && [ -f "$BUILTIN_FILE" ]; then
  BUILTIN_SKILLS_RAW="$(cat "$BUILTIN_FILE")"
fi

BUNDLED_SKILLS_DIR="$(find_bundled_skills_dir)"
DENIED_FILE="$WORKSPACE/DENIED_SKILLS"
DENIED_NAMES="$(resolve_denied_skill_names "$DENIED_FILE")"
SKILLS_JSON="[]"

SKILLS_JSON="$(build_agent_skills_json \
  "$WORKSPACE" \
  "$BUILTIN_SKILLS_RAW" \
  "$DENIED_NAMES" \
  "$BUNDLED_SKILLS_DIR" \
  "$CREW_TYPE")"

if [ "$CREW_TYPE" = "external" ]; then
  if SKILLS_JSON="$SKILLS_JSON" node -e '
const skills = JSON.parse(process.env.SKILLS_JSON || "[]");
const blocked = new Set(["self-improving", "self-improve"]);
process.exit(skills.some((s) => blocked.has(s)) ? 0 : 1);
'; then
    echo "❌ External crew final skill set contains blocked self-improving skill."
    exit 1
  fi
fi

# 技能模式描述（用于日志）
if [ "$CREW_TYPE" = "external" ]; then
  SKILLS_MODE="declare-mode (DECLARED_SKILLS + workspace only)"
else
  HAS_ADDITIONAL_BUILTINS="false"
  if [ -n "$(split_skill_tokens "$BUILTIN_SKILLS_RAW")" ]; then
    HAS_ADDITIONAL_BUILTINS="true"
  fi

  if [ "$HAS_ADDITIONAL_BUILTINS" = "true" ] && [ -n "$DENIED_NAMES" ]; then
    SKILLS_MODE="inherit: baseline+additional-denied+workspace"
  elif [ "$HAS_ADDITIONAL_BUILTINS" = "true" ]; then
    SKILLS_MODE="inherit: baseline+additional+workspace"
  elif [ -n "$DENIED_NAMES" ]; then
    SKILLS_MODE="inherit: baseline-denied+workspace"
  else
    SKILLS_MODE="inherit: baseline+workspace"
  fi
fi

# 验证 openclaw.json 存在
if [ ! -f "$CONFIG_PATH" ]; then
  echo "❌ Config not found: $CONFIG_PATH"
  exit 1
fi

# 检查 agent 是否已存在
if AGENT_ID="$AGENT_ID" CONFIG_PATH="$CONFIG_PATH" node -e "
  const c = JSON.parse(require('fs').readFileSync(process.env.CONFIG_PATH, 'utf8'));
  const exists = (c.agents?.list || []).some(a => a.id === process.env.AGENT_ID);
  process.exit(exists ? 0 : 1);
" 2>/dev/null; then
  echo "❌ Agent '$AGENT_ID' already exists in openclaw.json"
  exit 1
fi

echo "📦 Adding agent: $AGENT_ID (crew-type: $CREW_TYPE)"

# 更新 openclaw.json
AGENT_ID="$AGENT_ID" CREW_TYPE="$CREW_TYPE" BIND_CHANNEL="$BIND_CHANNEL" BIND_ACCOUNT="$BIND_ACCOUNT" CONFIG_PATH="$CONFIG_PATH" SKILLS_JSON="$SKILLS_JSON" OPENCLAW_HOME="$OPENCLAW_HOME" node -e "
  const fs = require('fs');
  const c = JSON.parse(fs.readFileSync(process.env.CONFIG_PATH, 'utf8'));
  const agentSkills = JSON.parse(process.env.SKILLS_JSON || '[]');
  const agentId = process.env.AGENT_ID;
  const crewType = process.env.CREW_TYPE || 'external';
  const openclawHome = process.env.OPENCLAW_HOME || (process.env.HOME + '/.openclaw');

  // 1. 添加到 agents.list
  if (!c.agents) c.agents = {};
  if (!c.agents.list) c.agents.list = [];
  const newAgent = {
    id: agentId,
    name: agentId,
    workspace: openclawHome + '/workspace-' + agentId,
    skills: agentSkills,
  };
  c.agents.list.push(newAgent);

  // 2. 仅对内 Crew 加入 Main Agent 的 allowAgents
  if (crewType === 'internal') {
    const main = c.agents.list.find(a => a.id === 'main');
    if (main) {
      if (!main.subagents) main.subagents = {};
      if (!main.subagents.allowAgents) main.subagents.allowAgents = [];
      if (!main.subagents.allowAgents.includes(agentId)) {
        main.subagents.allowAgents.push(agentId);
      }
    }
  }
  // 对外 Crew 不加入 allowAgents（bind-only，不可通过 Main Agent spawn）

  // 3. 如果需要绑定渠道
  const bindChannel = process.env.BIND_CHANNEL || '';
  const bindAccount = process.env.BIND_ACCOUNT || '';
  if (bindChannel) {
    if (!c.bindings) c.bindings = [];
    c.bindings.push({
      agentId,
      match: { channel: bindChannel, accountId: bindAccount },
      comment: agentId + ' direct channel binding (' + crewType + ')'
    });
  }

  fs.writeFileSync(process.env.CONFIG_PATH, JSON.stringify(c, null, 2) + '\n');
"

echo "  ✅ Added to agents.list"
if [ "$CREW_TYPE" = "internal" ]; then
  echo "  ✅ Added to Main Agent allowAgents (spawn mode enabled)"
else
  echo "  ✅ Skipped allowAgents (external crew is bind-only)"
fi
echo "  ✅ Skill scope: $SKILLS_MODE"

if [ -n "$BIND_CHANNEL" ]; then
  echo "  ✅ Added binding: $BIND_CHANNEL:$BIND_ACCOUNT"
fi

# 更新 HRBP 的 EXTERNAL_CREW_REGISTRY.md（对外 Crew）
# 对内 Crew 更新 Main Agent 的 MEMORY.md
if [ "$CREW_TYPE" = "external" ]; then
  HRBP_WORKSPACE="$OPENCLAW_HOME/workspace-hrbp"
  EXTERNAL_REGISTRY="$HRBP_WORKSPACE/EXTERNAL_CREW_REGISTRY.md"
  if [ -f "$EXTERNAL_REGISTRY" ]; then
    ROUTE_MODE="binding"
    [ -n "$BIND_CHANNEL" ] && BOUND_CH="$BIND_CHANNEL:$BIND_ACCOUNT" || BOUND_CH="—"
    REGISTRY_ROW="| $AGENT_ID | $TEMPLATE_ID_SANITIZED | external | $BOUND_CH | $TODAY_DATE | active | $RECRUIT_NOTE_SANITIZED |"
    HISTORY_LINE="- $TODAY_DATE: 招募对外 Crew $AGENT_ID ($TEMPLATE_ID_SANITIZED) - $RECRUIT_NOTE_SANITIZED"

    if grep -Fq "| $AGENT_ID |" "$EXTERNAL_REGISTRY" 2>/dev/null; then
      echo "  ⚠️  Agent already in EXTERNAL_CREW_REGISTRY, skipping"
    else
      TMP_REG="$(mktemp "${EXTERNAL_REGISTRY}.tmp.XXXXXX")"
      awk -v row="$REGISTRY_ROW" '
        BEGIN { inserted = 0 }
        /^## Operation History/ && inserted == 0 { print row; inserted = 1 }
        { print }
        END { if (inserted == 0) print row }
      ' "$EXTERNAL_REGISTRY" > "$TMP_REG"
      mv "$TMP_REG" "$EXTERNAL_REGISTRY"
      echo "  ✅ Updated EXTERNAL_CREW_REGISTRY.md"
    fi

    TMP_HIST="$(mktemp "${EXTERNAL_REGISTRY}.tmp.XXXXXX")"
    awk -v line="$HISTORY_LINE" '
      BEGIN { inserted = 0 }
      /^## Operation History/ {
        print; print ""; print line; inserted = 1; next
      }
      { print }
      END { if (inserted == 0) { print ""; print "## Operation History"; print ""; print line } }
    ' "$EXTERNAL_REGISTRY" > "$TMP_HIST"
    mv "$TMP_HIST" "$EXTERNAL_REGISTRY"
    echo "  ✅ Updated EXTERNAL_CREW_REGISTRY operation history"
  fi

  # 更新 HRBP MEMORY.md（operation history）
  HRBP_MEMORY="$HRBP_WORKSPACE/MEMORY.md"
  if [ -f "$HRBP_MEMORY" ]; then
    HISTORY_LINE_MEM="- $TODAY_DATE: 招募对外 Crew $AGENT_ID ($TEMPLATE_ID_SANITIZED) - $RECRUIT_NOTE_SANITIZED"
    if ! grep -Fqx "$HISTORY_LINE_MEM" "$HRBP_MEMORY" 2>/dev/null; then
      TMP_HRBP_MEM="$(mktemp "${HRBP_MEMORY}.tmp.XXXXXX")"
      awk -v line="$HISTORY_LINE_MEM" '
        BEGIN { inserted = 0 }
        /^## Operation History/ {
          print; print ""; print line; inserted = 1; next
        }
        { print }
        END { if (inserted == 0) { print ""; print "## Operation History"; print ""; print line } }
      ' "$HRBP_MEMORY" > "$TMP_HRBP_MEM"
      mv "$TMP_HRBP_MEM" "$HRBP_MEMORY"
      echo "  ✅ Updated HRBP MEMORY operation history"
    fi
  fi

else
  # 内部 Crew：注入技术故障派发协议到 AGENTS.md（幂等，第三方模板可能未包含）
  AGENTS_MD="$WORKSPACE/AGENTS.md"
  if [ -f "$AGENTS_MD" ] && ! grep -q "## Technical Issue Dispatch Protocol" "$AGENTS_MD"; then
    cat >> "$AGENTS_MD" << 'PROTOCOL'

## Technical Issue Dispatch Protocol

当任务执行中遭遇技术性故障（脚本报错、配置异常、spawn 失败等）：

```
1. 立即告知用户：
   "遇到了技术问题，正在呼唤 IT Engineer 处理，请稍作等待，任务执行时间会稍长。"
2. sessions_spawn it-engineer（必须 `runtime=subagent`，且**禁止传入 `streamTo`**），传入：
   - 具体错误信息
   - 当前正在执行的操作
   - 相关文件路径或配置
3. IT Engineer 修复后 → 继续执行原任务
```

**绝对禁止**：因技术问题停止工作，或引导用户自行解决。
PROTOCOL
    echo "  ✅ Injected Technical Issue Dispatch Protocol into AGENTS.md"
  fi

  # 内部 Crew：更新 Main Agent 的 MEMORY.md
  MAIN_MEMORY="$OPENCLAW_HOME/workspace-main/MEMORY.md"
  if [ -f "$MAIN_MEMORY" ]; then
    ROUTE_MODE="spawn"
    [ -n "$BIND_CHANNEL" ] && ROUTE_MODE="both"
    BOUND_CHANNELS="—"
    [ -n "$BIND_CHANNEL" ] && BOUND_CHANNELS="$BIND_CHANNEL"

    if grep -q "^| $AGENT_ID " "$MAIN_MEMORY" 2>/dev/null; then
      echo "  ⚠️  Agent already in MEMORY.md roster, skipping"
    else
      ROSTER_ROW="| $AGENT_ID | $AGENT_ID | $TEMPLATE_ID_SANITIZED | internal | $ROUTE_MODE | $BOUND_CHANNELS | active |"
      TMP_MEMORY="$(mktemp "${MAIN_MEMORY}.tmp.XXXXXX")"
      awk -v row="$ROSTER_ROW" '
        BEGIN { inserted = 0 }
        /^## External Crew Note/ && inserted == 0 { print row; inserted = 1 }
        { print }
        END { if (inserted == 0) print row }
      ' "$MAIN_MEMORY" > "$TMP_MEMORY"
      mv "$TMP_MEMORY" "$MAIN_MEMORY"
      echo "  ✅ Updated Main Agent MEMORY.md roster (internal crew)"
    fi
  fi
fi

# 同步 TEAM_DIRECTORY（内部 crew 变化时）
if [ "$CREW_TYPE" = "internal" ]; then
  if [ -f "$SYNC_TEAM_DIRECTORY_SCRIPT" ]; then
    OPENCLAW_HOME="$OPENCLAW_HOME" CONFIG_PATH="$CONFIG_PATH" bash "$SYNC_TEAM_DIRECTORY_SCRIPT" >/dev/null 2>&1 || {
      echo "  ⚠️  Failed to sync TEAM_DIRECTORY.md"
    }
  fi
fi

echo ""
# 向 TOOLS.md 注入文件操作规范（幂等）
inject_file_edit_guide "$WORKSPACE/TOOLS.md"

echo "✅ Agent '$AGENT_ID' registered successfully! (type: $CREW_TYPE)"
echo ""
echo "⚠️  Restart Gateway to apply changes: ./scripts/dev.sh gateway"
