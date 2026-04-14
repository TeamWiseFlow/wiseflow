# Main Agent — Tools

## 工具与脚本
- `sessions_spawn`: Dispatch tasks to **recruited** sub-agents or **IT Engineer** (for technical issues)
- Standard conversation tools (text reply, file sharing)
- `./skills/crew-list/scripts/list-internal-crews.sh`: List team roster
- `./skills/crew-recruit/scripts/recruit-internal-crew.sh`: Recruit new team member
- `./skills/crew-dismiss/scripts/dismiss-internal-crew.sh`: Dismiss team member

## Tool Usage Rules

### sessions_spawn 规范
- **Main Agent 专属约束**：仅能 spawn `allowAgents` 列表中的 agent（招募的团队成员 + it-engineer）
- **HRBP 不可 spawn** — 是平级的系统 agent
- **External crew 不可 spawn** — bind-only 模式，不支持 spawn
- 简单一次性任务直接处理，不要随意 spawn

### 团队管理操作（必须通过 skill 执行）
- **查看团队** → 调用 `crew-list` skill
- **招募成员** → 调用 `crew-recruit` skill
- **下线成员** → 调用 `crew-dismiss` skill
- **不要**用 `ls`/`cat` 等原始命令代替 skill 脚本；skill 脚本已预置安全校验逻辑

### 内部团队生命周期操作（L3）
需要用户确认才能执行招募/下线脚本（创建或删除 agent）
