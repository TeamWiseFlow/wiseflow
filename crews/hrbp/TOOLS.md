# HRBP Agent — Tools

## Available Tools (T2 — Dev Toolchain)

### Crew Lifecycle Scripts
- `./skills/hrbp-recruit/scripts/add-agent.sh`: Register new external agent in openclaw.json
- `./skills/hrbp-modify/scripts/modify-agent.sh`: Update agent bindings in openclaw.json
- `./skills/hrbp-remove/scripts/remove-agent.sh`: Unregister external agent and archive workspace
- `./skills/hrbp-list/scripts/list-agents.sh`: View external agent roster (from EXTERNAL_CREW_REGISTRY)
- `./skills/hrbp-usage/scripts/agent-usage.sh`: Query agent model usage and cost data
- `./skills/hrbp-feedback-review/scripts/scan-feedback.sh`: Scan external crew feedback directories

### File Read/Write
- For generating and editing workspace files
- For reading feedback entries from `~/.openclaw/workspace-*/feedback/`
- For maintaining `EXTERNAL_CREW_REGISTRY.md` in this workspace
- For reading `~/.openclaw/crew_templates/TEAM_DIRECTORY.md` (internal crew status, read-only)

### Shell Execution (T2)
- T2 白名单命令（cat/ls/grep/find/ps + git/node/pnpm/cp/mv/mkdir/rm/touch + bash/sh）
- Use OFB scripts via paths in `OFB_ENV.md`

### 查阅其他 Agent 的 Session 历史

> ⚠️ **禁止使用 `sessions_send`/`sessions_list`/`sessions_history`/`sessions_status` 等技能命令查询其他 agent 的 session**——这些命令仅限当前自身 agent 使用。

如需查阅外部 Crew 的对话历史（例如审查 feedback、分析对话质量），直接读取本地文件：

```bash
# 查看某 agent 的 session 索引（含所有 session 的元数据）
cat ~/.openclaw/agents/<agentId>/sessions/sessions.json

# 查看某条 session 的完整对话记录（JSONL 格式，每行一条消息）
cat ~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl
```

- `sessions.json`：JSON 对象，key = session key（如 `agent:cs-001:awada:direct:user123`），value = session 元数据
- `<sessionId>.jsonl`：完整对话内容，逐条 JSON 行，包含 role/content/timestamp 等字段

## Tool Usage Rules
- Use `~/.openclaw/hrbp_templates/` as starting points for new agents
- Never modify `main`, `hrbp`, or `it-engineer` lifecycle — they are internal, managed by Main Agent
- All openclaw.json modifications are L3 (require user confirmation)
- Feedback files are read-only for analysis — never modify a crew's feedback entries
