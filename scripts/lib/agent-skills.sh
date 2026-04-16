#!/bin/bash
# agent-skills.sh - 统一计算 Agent 的技能过滤配置
#
# 设计理念（wiseflow）：
#   两种技能解析模式，由 SOUL.md 中的 crew-type 决定：
#
#   inherit 模式（对内 Crew，crew-type: internal）：
#   - 基线：list_default_global_skill_names 中 11 个指定的上游内置技能
#   - 自动追加：apply-addons.sh 写入 GLOBAL_SHARED_SKILLS 的 addon/项目全局技能
#   - 可通过 BUILTIN_SKILLS（或显式参数）在此之上追加 Agent 专属技能
#     （如 it-engineer 的 github / gh-issues / coding-agent）
#   - 可通过 DENIED_SKILLS（或显式参数）从最终列表中排除技能
#
#   declare 模式（对外 Crew，crew-type: external）：
#   - 仅使用 DECLARED_SKILLS 文件中明确声明的技能
#   - 不继承基线技能，不继承全局共享技能
#   - 不支持 DENIED_SKILLS（无需排除，因为只包含声明的技能）
#   - workspace 专属技能仍然可用（追加到声明列表末尾）
#
#   最终总是写入 agents.list[].skills，避免"空 skills 字段 => 全量技能泄露"
#   resolve_agent_skills_json 返回：
#       JSON 数组   → Agent 最终可见 skills

set -e

split_skill_tokens() {
  local raw="$1"
  printf '%s\n' "$raw" \
    | sed 's/#.*$//' \
    | tr ',' '\n' \
    | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' \
    | awk 'NF'
}

# 从 SOUL.md 读取 crew-type 声明
# 返回: "internal" 或 "external"（未声明时默认 "external"，更安全）
# 此函数是 crew-type 解析的唯一权威实现，exec-tiers.sh 和 setup-crew.sh 均引用此处。
resolve_crew_type() {
  local soul_file="$1"

  if [ ! -f "$soul_file" ]; then
    printf 'external'
    return
  fi

  local crew_type
  crew_type="$(grep -im1 '^crew-type:' "$soul_file" 2>/dev/null \
    | sed 's/^[Cc]rew-[Tt]ype:[[:space:]]*//' \
    | tr -d '[:space:]' \
    | tr '[:upper:]' '[:lower:]')"

  case "$crew_type" in
    internal) printf 'internal' ;;
    external) printf 'external' ;;
    *) printf 'external' ;;  # 未声明或未知类型，默认 external（安全兜底）
  esac
}

list_builtin_skill_names() {
  local project_root="$1"
  local bundled_root="$project_root/openclaw/skills"

  if [ ! -d "$bundled_root" ]; then
    return
  fi

  for skill_dir in "$bundled_root"/*/; do
    [ -d "$skill_dir" ] || continue
    if [ -f "${skill_dir}SKILL.md" ]; then
      basename "$skill_dir"
    fi
  done | sort
}

# wiseflow 指定的全局基线技能（对所有对内 Crew 统一开放的 8 个上游内置技能）
# 变更须同步更新 config-templates/openclaw.json 的 skills.entries 确保这些技能处于 enabled 状态
#
# 不在此基线的说明：
#   1password / video-frames / bluebubbles / peekaboo — 全局可用，但各 crew 须自行在 BUILTIN_SKILLS 中声明
#   healthcheck  — 仅 it-engineer（在其 BUILTIN_SKILLS 中单独配置）
#   model-usage  — 仅 hrbp（在其 BUILTIN_SKILLS 中单独配置）
#   ordercli     — 仅 sales-cs（对外 Crew，通过 DECLARED_SKILLS 声明，不进内置基线）
#   xurl / camsnap / clawhub / discord / alipay-mcp-config / canvas — 全局禁用
list_default_global_skill_names() {
  cat <<'EOF'
nano-pdf
skill-creator
session-logs
tmux
weather
summarize
gifgrep
self-improving
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

# 读取对外 Crew 的声明式技能列表（DECLARED_SKILLS 文件）
list_declared_skill_names() {
  local declared_file="$1"

  if [ ! -f "$declared_file" ]; then
    return
  fi

  split_skill_tokens "$(cat "$declared_file")" \
    | grep -Ev '^(self-improving|self-improve)$' \
    | sort -u
}

# 读取额外 bundled skills（来自 BUILTIN_SKILLS 文件或命令行参数）
# 返回：每行一个 skill 名称，空字符串表示无额外追加
resolve_additional_builtin_skill_names() {
  local explicit_tokens="$1"
  local builtin_file="$2"
  local project_root="$3"

  local raw=""
  if [ -n "$explicit_tokens" ]; then
    raw="$explicit_tokens"
  elif [ -f "$builtin_file" ]; then
    raw="$(cat "$builtin_file")"
  fi

  [ -n "$raw" ] || return 0

  local tokens=""
  tokens="$(split_skill_tokens "$raw")"
  [ -n "$tokens" ] || return 0

  # 支持 all/*：扩展为当前可发现的 bundled skills
  if printf '%s\n' "$tokens" | grep -Eiq '^(all|\*)$'; then
    local all_builtins=""
    all_builtins="$(list_builtin_skill_names "$project_root")"
    if [ -n "$all_builtins" ]; then
      printf '%s\n' "$all_builtins"
      return 0
    fi
    echo "  ⚠️  Cannot resolve bundled skills for 'all' (openclaw/skills not found)." >&2
    return 0
  fi

  # 额外技能不做强校验，允许先声明后安装
  printf '%s\n' "$tokens"
}

# 读取需要屏蔽的 skill 列表（来自 DENIED_SKILLS 文件或命令行参数）
# 返回：每行一个 skill 名称，空字符串表示无屏蔽
resolve_denied_skill_names() {
  local agent_id="$1"
  local explicit_tokens="$2"
  local denied_file="$3"

  local raw=""
  if [ -n "$explicit_tokens" ]; then
    raw="$explicit_tokens"
  elif [ -f "$denied_file" ]; then
    raw="$(cat "$denied_file")"
  fi

  [ -n "$raw" ] || return 0

  split_skill_tokens "$raw"
}

# 计算 Agent 的技能过滤配置（内部使用）
# 模式由 crew-type 决定：
#   internal → inherit 模式（基线 + 额外 - 拒绝 + workspace）
#   external → declare 模式（仅 DECLARED_SKILLS + workspace）
resolve_agent_skills_json() {
  local agent_id="$1"
  local workspace_dir="$2"
  local explicit_builtin_tokens="$3"
  local builtin_file="$4"
  local explicit_denied_tokens="$5"
  local denied_file="$6"
  local project_root="$7"
  local openclaw_home="${8:-$HOME/.openclaw}"

  # 读取 crew 类型
  local soul_file="$workspace_dir/SOUL.md"
  local crew_type
  crew_type="$(resolve_crew_type "$soul_file")"

  local workspace_skills
  workspace_skills="$(list_workspace_skill_names "$workspace_dir")"

  if [ "$crew_type" = "external" ]; then
    # ── declare 模式（对外 Crew）──
    # 仅使用 DECLARED_SKILLS 文件中的技能 + workspace 专属技能
    local declared_file="$workspace_dir/DECLARED_SKILLS"
    local declared_skills
    declared_skills="$(list_declared_skill_names "$declared_file")"

    printf '%s\n%s\n' "$declared_skills" "$workspace_skills" \
      | grep -Ev '^(self-improving|self-improve)$' \
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

  # ── inherit 模式（对内 Crew）──
  # 层次：① 11 个基线上游技能  ② addon/项目全局技能  ③ Agent 专属技能（BUILTIN_SKILLS）  ④ -DENIED  ⑤ +workspace

  # ① wiseflow 指定的 11 个基线技能
  local default_builtins=""
  default_builtins="$(list_default_global_skill_names)"

  # ② addon / 项目安装的全局技能（apply-addons.sh 写入 GLOBAL_SHARED_SKILLS 文件）
  local addon_global_skills=""
  local global_shared_file="$openclaw_home/GLOBAL_SHARED_SKILLS"
  if [ -f "$global_shared_file" ]; then
    addon_global_skills="$(awk 'NF' "$global_shared_file")"
  fi

  # ③ Agent 专属额外技能（来自 BUILTIN_SKILLS 文件或命令行参数）
  local additional_builtins=""
  additional_builtins="$(resolve_additional_builtin_skill_names \
    "$explicit_builtin_tokens" \
    "$builtin_file" \
    "$project_root")"

  local merged_global_skills=""
  merged_global_skills="$(printf '%s\n%s\n%s\n' "$default_builtins" "$addon_global_skills" "$additional_builtins" \
    | awk 'NF && !seen[$0]++')"

  local denied_names
  denied_names="$(resolve_denied_skill_names \
    "$agent_id" \
    "$explicit_denied_tokens" \
    "$denied_file")"

  local allowed_builtins=""
  if [ -n "$denied_names" ]; then
    while IFS= read -r skill; do
      [ -n "$skill" ] || continue
      if ! printf '%s\n' "$denied_names" | grep -Fxq "$skill"; then
        allowed_builtins="$allowed_builtins"$'\n'"$skill"
      fi
    done <<< "$merged_global_skills"
  else
    allowed_builtins="$merged_global_skills"
  fi

  printf '%s\n%s\n' "$allowed_builtins" "$workspace_skills" \
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

# 收集某 agent 所有 skill 的脚本路径，供自动注入 ALLOWED_COMMANDS
#
# 输出格式（每行一条）:
#   +./skills/<skill>/scripts/<file>     — workspace-local skill 脚本（相对路径）
#   +<abs_path>                          — 全局 skill 脚本（绝对路径）
#
# 参数:
#   $1  workspace_dir   agent 的 workspace 目录
#   $2  skills_json     JSON 数组字符串（resolve_agent_skills_json 的输出）
#   $3  project_root    wiseflow 项目根目录
#
# 设计：只处理有执行权限（可执行位）或以 .sh 结尾的文件，跳过 .py/.json 等。
collect_skill_script_commands() {
  local workspace_dir="$1"
  local skills_json="$2"
  local project_root="$3"

  [ -n "$workspace_dir" ] || return 0
  [ -n "$skills_json" ] || return 0

  # 从 JSON 数组解析 skill 名称列表
  local skill_names
  skill_names="$(printf '%s\n' "$skills_json" \
    | node -e '
const fs = require("fs");
const raw = fs.readFileSync(0, "utf8").trim();
let arr;
try { arr = JSON.parse(raw); } catch(_) { arr = []; }
if (Array.isArray(arr)) arr.forEach((s) => { if (s && typeof s === "string") console.log(s); });
' 2>/dev/null)"

  [ -n "$skill_names" ] || return 0

  while IFS= read -r skill; do
    [ -n "$skill" ] || continue

    # ── workspace-local skill ──────────────────────────────
    local ws_scripts_dir="$workspace_dir/skills/$skill/scripts"
    if [ -d "$ws_scripts_dir" ]; then
      while IFS= read -r -d '' f; do
        local fname
        fname="$(basename "$f")"
        # 只允许 .sh 文件或有可执行位的文件（排除 .py .json .txt 等）
        case "$fname" in
          *.py|*.json|*.txt|*.md|*.yaml|*.yml) continue ;;
        esac
        [ -x "$f" ] || [[ "$fname" == *.sh ]] || continue
        printf '+./skills/%s/scripts/%s\n' "$skill" "$fname"
      done < <(find "$ws_scripts_dir" -maxdepth 1 -type f -print0 2>/dev/null)
    fi

    # ── 全局 skill（openclaw/skills/）──────────────────────
    local global_scripts_dir="$project_root/openclaw/skills/$skill/scripts"
    if [ -d "$global_scripts_dir" ]; then
      while IFS= read -r -d '' f; do
        local fname
        fname="$(basename "$f")"
        case "$fname" in
          *.py|*.json|*.txt|*.md|*.yaml|*.yml) continue ;;
        esac
        [ -x "$f" ] || [[ "$fname" == *.sh ]] || continue
        printf '+%s\n' "$f"
      done < <(find "$global_scripts_dir" -maxdepth 1 -type f -print0 2>/dev/null)
    fi

  done <<< "$skill_names"
}

# 向 external crew 的 AGENTS.md 追加渠道回复规则（幂等）
# 规则：调用工具的 turn 不得包含面向客户的文本，所有文本在最后一个 turn 统一输出
inject_channel_reply_rules() {
  local agents_md="$1"
  [ -f "$agents_md" ] || return 0
  grep -qF "## 渠道回复规则（自动注入）" "$agents_md" && return 0
  cat >> "$agents_md" << 'RULES'

---

## 渠道回复规则（自动注入）

调用任何工具（exec / message / read 等）的 turn 中，不得包含任何面向客户的文本。面向客户的完整回复必须在所有工具执行完成后，在最后一个 turn 中统一输出。违反此规则会导致客户收到多条内容相近的消息。
RULES
}

# 向 workspace 的 TOOLS.md 追加通用工具调用规范（幂等）
# 注入内容见 docs/injected_instruction.md
# 向 AGENTS.md 追加通用标准 section（幂等）
# 1. Technical Issue Dispatch Protocol
# 2. sessions_spawn 规范
inject_agents_md_sections() {
  local agents_md="$1"
  [ -f "$agents_md" ] || return 0

  if ! grep -qF "## Technical Issue Dispatch Protocol" "$agents_md"; then
    cat >> "$agents_md" << 'TIDP'

## Technical Issue Dispatch Protocol

**当任务执行过程中遭遇技术问题或系统故障（exec 失败、配置异常、spawn 报错、脚本异常等），必须严格按以下步骤处理：**

1. **立即告知用户**：主动说明遇到了技术问题，正在呼唤 IT Engineer 处理，请耐心等待，任务执行时间会稍长
2. **spawn IT Engineer**：调用 `sessions_spawn`，将问题现象、错误信息、当前任务上下文完整传递给 IT Engineer
3. **等待修复完成**，然后继续执行原任务

**绝对禁止**：因技术问题停止工作，或要求用户自行解决系统故障。技术问题由 IT Engineer 负责，你的职责是保证用户任务顺利完成。
TIDP
  fi

  if ! grep -qF "## sessions_spawn 规范" "$agents_md"; then
    cat >> "$agents_md" << 'SSP'

## sessions_spawn 规范

> ⚠️ **禁止传入 `streamTo` 参数** — `streamTo` 仅支持 `runtime=acp`，在 subagent 模式下会报错（`streamTo is only supported for runtime=acp`）。spawn 时只传 agentId 和 task 内容即可。
SSP
  fi
}

inject_file_edit_guide() {
  local tools_md="$1"
  [ -f "$tools_md" ] || return 0
  grep -q "## 本地文件操作规范" "$tools_md" && return 0
  cat >> "$tools_md" << 'GUIDE'

## 本地文件操作规范

1. **小改动优先**：read 最新文件内容后，复制原文精确片段再 edit
2. **大改动直接**：整文件重写走 write（先基于最新内容生成）
3. **避免一次改太大**：拆成多个小 patch，减少 mismatch
4. **以 read 结果为准**：别依赖聊天里渲染后的文本（如超链接形式的文件名），要以 read 工具的返回结果为准

## sessions_spawn 规范

> ⚠️ **禁止传入 `streamTo` 参数** — `streamTo` 仅支持 `runtime=acp`，在 subagent 模式下会报错（`streamTo is only supported for runtime=acp`）。spawn 时只传 agentId 和 task 内容即可。
GUIDE
}
