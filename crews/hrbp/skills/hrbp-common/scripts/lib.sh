#!/bin/bash
# lib.sh - Shared helpers for HRBP lifecycle scripts
# Source this file: source "$(dirname "$0")/../../hrbp-common/scripts/lib.sh"

# Validate agent-id format: lowercase alphanumeric + hyphens, no leading/trailing hyphens, max 63 chars (DNS label).
validate_agent_id() {
  local id="$1"
  if ! printf '%s\n' "$id" | grep -Eq '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'; then
    echo "❌ Invalid agent-id: $id"
    echo "   Expected: lowercase letters, numbers, hyphens; no leading/trailing hyphens; max 63 chars"
    echo "   Example: customer-service-a"
    exit 1
  fi
}

# 向 workspace 的 TOOLS.md 追加通用工具调用规范（幂等）
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
GUIDE
}

inject_exec_guide() {
  local tools_md="$1"
  [ -f "$tools_md" ] || return 0
  grep -q "## exec 命令规范" "$tools_md" && return 0
  cat >> "$tools_md" << 'GUIDE'

## exec 命令规范

exec allowlist 不支持 shell 重定向符（`>`、`<`、`2>`、`&>`），使用时会导致整条命令被 deny，即使其中每个命令都已在白名单中。

**避免**：
```
ls -la /tmp/file.txt 2>/dev/null && echo "EXISTS" || echo "NOT"
some-cmd > /tmp/out.txt
```

**改用**：
```bash
# 判断文件是否存在
[ -f /tmp/file.txt ] && echo "EXISTS" || echo "NOT"
test -f /tmp/file.txt && echo "EXISTS" || echo "NOT"

# 写文件用 write 工具；读文件用 read 工具
```

如果确实需要重定向，请改用 `bash -c "..."` 方式，并确保 `bash` 已在 exec allowlist 中（T2 及以上 tier 默认包含）。
GUIDE
}

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

inject_feishu_media_guide() {
  local user_md="$1"
  [ -f "$user_md" ] || return 0
  grep -qF "## 发送图片/文件/视频等富媒体（自动注入）" "$user_md" && return 0
  cat >> "$user_md" << 'GUIDE'

## 发送图片/文件/视频等富媒体（自动注入）

向用户发送图片、文件、视频或其他富媒体内容时，不要在本地打开媒体文件，**必须将文件本体通过对话所在的 channel 直接发送到聊天中**，且不得直接输出文件路径或 base64 内容作为回复。
GUIDE
}
