# HRBP Agent — Tools

## 工具与脚本（T2）

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
- Use wiseflow scripts via paths in `OFB_ENV.md`

## Tool Usage Rules
- Use `~/.openclaw/hrbp_templates/` as starting points for new agents
- Never modify `main`, `hrbp`, or `it-engineer` lifecycle — they are internal, managed by Main Agent
- All openclaw.json modifications are L3 (require user confirmation)
- Feedback files are read-only for analysis — never modify a crew's feedback entries
