# Injected Instructions — 注入指令说明

本文档记录所有通过脚本自动注入到 Agent workspace 的指令内容，便于追踪和排查。

---

## 注入机制

注入由两处脚本触发，均幂等（���测标记行是否已存在）：

| 触发场景 | 脚本 | 注入目标 |
|----------|------|----------|
| 内置 Crew 首次安装 / 配置文件同步 | `scripts/setup-crew.sh` | `~/.openclaw/workspace-{main,hrbp,it-engineer}/TOOLS.md` |
| 新 Crew 注册（HRBP 招募 / Main Agent 招募对内 crew） | `crews/hrbp/skills/hrbp-recruit/scripts/add-agent.sh` | `~/.openclaw/workspace-{agentId}/TOOLS.md` |

注入函数实现：
- `scripts/lib/agent-skills.sh` → `inject_file_edit_guide()`（供 `setup-crew.sh` 使用）
- `crews/hrbp/skills/hrbp-common/scripts/lib.sh` → `inject_file_edit_guide()`（供 `add-agent.sh` 使用）

幂等标记：`## 本地文件操作规范`（首次检测，若已存在则跳过）

---

## 注入内容（TOOLS.md 末尾追加）

```markdown
## 本地文件操作规范

1. **小改动优先**：read 最新文件内容后，复制原文精确片段再 edit
2. **大改动直接**：整文件重写走 write（先基于最新内容生成）
3. **避免一次改太大**：拆成多个小 patch，减少 mismatch
4. **以 read 结果为准**：别依赖聊天里渲染后的文本（如超链接形式的文件名），要以 read 工具的返回结果为准

## sessions_spawn 规范

> ⚠️ **禁止传入 `streamTo` 参数** — `streamTo` 仅支持 `runtime=acp`，在 subagent 模式下会报错（`streamTo is only supported for runtime=acp`）。spawn 时只传 agentId 和 task 内容即可。
```

---

## 注入位置：TOOLS.md（不是 AGENTS.md）

**选择 TOOLS.md 的原因**：

- 本地文件操作（read/edit/write）和 `sessions_spawn` 均属于**工具调用规范**
- AGENTS.md 记录工作流程和业务协议（如 Technical Issue Dispatch Protocol），不承载工具操作规则

**职责分工**：

| 文件 | 内容定位 |
|------|----------|
| `SOUL.md` | 身份、角色、核心原则、自主等级 |
| `AGENTS.md` | 工作流程、调度协议、业务规则（含 Technical Issue Dispatch Protocol） |
| `TOOLS.md` | 工具列表 + 工具调用规范（含注入的通用规范） |

---

## 各模板手写内容与注入内容的边界

以下规则**不应**在模板 TOOLS.md 中手写（由注入统一提供）：

- `streamTo` 禁止传入的警告
- "先读后改"、"read 最新文件"类文件操作规范

以下规则**仍在**模板 TOOLS.md 中手写（agent 专属，注入无法覆盖）：

- `sessions_spawn` 的专属约束（如 main 的 HRBP 不可 spawn、external crew 不可 spawn）
- 特定工具的使用方式（如 hrbp 的 crew lifecycle scripts、it-engineer 的系统命令）

以下内容**只放在 AGENTS.md**，不放 TOOLS.md：

- **Technical Issue Dispatch Protocol**（内置 Crew 专属，描述遇到技术故障时调用 IT Engineer 的工作流）

---

## 历史变更

| 日期 | 变更内容 |
|------|----------|
| 2026-03-25 | 初始注入：本地文件操作规范（4条） |
| 2026-03-25 | 增加注入：sessions_spawn 通用规范（streamTo 禁止） |
| 2026-03-25 | 清理模板中与注入重复的内容（main/hrbp/it-engineer TOOLS.md） |
