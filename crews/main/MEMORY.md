# Main Agent — Memory

## Default Runtime State

Fresh install is intentionally minimal:

- User entry channel: `openclaw-weixin` direct chat to `main`.
- IT Engineer is available as Main Agent's subagent only.
- HRBP is not enabled by default.
- Feishu and WeCom are configured later as work channels.
- Awada is reserved for external crew scenarios and is not part of Main Agent's default work-channel flow.

## Internal Crew Roster

> Authoritative source: `~/.openclaw/crew_templates/TEAM_DIRECTORY.md` and live `openclaw.json`.
> This file is supplementary memory for onboarding and lifecycle decisions.

| Instance ID | Name | Template | Type | Route Mode | Bound Channels | Status |
|-------------|------|----------|------|------------|----------------|--------|
| it-engineer | IT Engineer | it-engineer (built-in) | internal | spawn via main | — | active |
| hrbp | HRBP | hrbp (built-in) | internal/system | direct/work-channel after enablement | — | not enabled |

## wiseflow 系统知识

项目背景、功能介绍和目录结构详见工作区中的**项目背景.md**（由部署脚本自动同步，每次升级均为最新版）。

实际项目路径、OpenClaw 配置路径、gateway 运维命令、环境变量文件位置记录在工作区中的 `OFB_ENV.md`（由 `setup-crew.sh` 自动同步）。

## Lifecycle Ownership Rule

Main Agent owns lifecycle management for non-protected internal crew.

Protected agents:

- `main`
- `it-engineer`
- `hrbp` when enabled

External crew are managed by HRBP and require direct channel binding.

## Work Channel State

Initial state:

- workChannel.enabled: false
- workChannel.recommended: false
- itEngineerHasDirectBinding: false
- hrbpEnabled: false
- hrbpHasDirectBinding: false

Recommend work channel when:

- internal crew count excluding `main` is greater than 3;
- first external crew is requested;
- user repeatedly needs direct access to a specialist.

Supported work channels in Main Agent onboarding:

- Feishu
- WeCom

## State Files

Runtime files maintained in Main Agent workspace:

- `reminder.json`: active reminders and cooldown state.
- `pending-followup.json`: pending Gateway restart/config followup.
- `business-context/`: stable company, brand, product, audience, channel, and operating context collected during onboarding. Internal crew workspaces receive a symlink to this folder when recruited.
- `channel-bindings.json`: optional summary of work channel binding decisions.
- `feishu.md`: user-maintained Feishu setup notes.
- `wecom.md`: user-maintained WeCom setup notes.

## Notes

- Do not store secrets in Markdown memory files.
- Bot/app secrets belong in `openclaw.json` or the OpenClaw credential mechanism used by the selected channel.
- The Weixin channel id is `openclaw-weixin`.
- Weixin supports direct chats and media; group chats are not part of the current advertised capability metadata.
