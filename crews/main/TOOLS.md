# Main Agent — Tools

## 工具与脚本

- `sessions_spawn`: Dispatch tasks to allowed sub-agents, especially IT Engineer for system work.
- `./skills/crew-list/scripts/list-internal-crews.sh`: List internal team roster.
- `./skills/crew-recruit/scripts/recruit-internal-crew.sh`: Recruit non-protected internal crew.
- `./skills/crew-dismiss/scripts/dismiss-internal-crew.sh`: Dismiss non-protected internal crew.
- `./skills/work-channel-binding/scripts/check-work-channel-bindings.py`: Inspect current work channel bindings.
- `./skills/work-channel-binding/scripts/prepare-work-channel-binding.py`: Build a dry-run binding plan.
- `./skills/work-channel-binding/scripts/apply-work-channel-binding.py`: Apply confirmed binding changes.
- `./skills/work-channel-binding/scripts/record-pending-followup.py`: Record restart followup before Gateway restart.
- `./skills/work-channel-binding/scripts/complete-pending-followup.py`: Complete restart followup after recovery.
- `./skills/reminder/scripts/update-reminders.py`: Refresh reminder state.

## System Environment Notes

- OpenClaw config: `~/.openclaw/openclaw.json`
- Main workspace: `~/.openclaw/workspace-main`
- IT Engineer workspace: `~/.openclaw/workspace-it-engineer`
- HRBP workspace template may exist, but HRBP is not enabled by default.
- Gateway restart command: `WISEFLOW_CONFIRM_GATEWAY_RESTART=confirmed ./skills/work-channel-binding/scripts/restart-gateway-confirmed.sh <reason>`
- Gateway status command: `systemctl --user status openclaw-gateway --no-pager`
- Weixin login command: `openclaw channels login --channel openclaw-weixin`
- Weixin pairing check: `openclaw pairing list openclaw-weixin`
- Weixin pairing approve: `openclaw pairing approve openclaw-weixin <id>`

## OFV_ENV

Main Agent should know the same operating environment that IT Engineer uses, but should delegate risky or detailed system work to IT Engineer.

Use this knowledge for guidance and orchestration only:

- Project root is the wiseflow-pro checkout.
- OpenClaw runtime state lives under `~/.openclaw`.
- Model keys are collected into daemon env during install; Main Agent should not ask users for LLM keys unless explicitly troubleshooting install.
- Default main model is `deepseek/deepseek-v4-pro` with high thinking.

## Work Channel Notes

Main Agent supports onboarding for these work channels:

- Feishu
- WeCom

Tutorial placeholders:

- `./skills/work-channel-binding/docs/feishu.md`
- `./skills/work-channel-binding/docs/wecom.md`

Do not configure awada as a default work channel. Awada is reserved for external crew service scenarios.

## Tool Usage Rules

### sessions_spawn 规范

- Spawn only agents in `allowAgents`.
- IT Engineer is the default system subagent.
- HRBP is enabled only when external crew is needed.
- External crew are bind-only and not spawned by Main Agent.

### 团队管理操作

- 查看团队 → `crew-list`
- 招募成员 → `crew-recruit`
- 下线成员 → `crew-dismiss`
- 工作 channel 绑定 → `work-channel-binding`
- reminder 更新 → `reminder`

Do not hand-edit `openclaw.json`; use skill scripts.

### L3 Confirmation Required

Ask the user before:

- modifying `openclaw.json`;
- saving channel secrets;
- enabling HRBP;
- creating or deleting crew;
- restarting Gateway.
