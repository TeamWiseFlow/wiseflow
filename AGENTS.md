# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

### 版本管理

版本号存储在 `version` 文件中，格式为 `vMAJOR.MINOR.PATCH`。当 PR 合并到 upstream 的 master 时，GitHub Action 自动递增版本号并创建 Release。通过 PR 标签控制递增类型：
- `major` 标签 → 大版本升级
- `minor` 标签 → 功能版本升级
- 无标签或 `patch` 标签 → 补丁版本升级（默认）

**不要手动修改 `version` 文件**，由 CI 自动维护。

## Crew Template 开发规范

创建或修改 crew template（`crews/` 或 `addons/officials/crew/` 下的任何 crew）时，必须遵循 `docs/workspace-bootstrap-files.md` 中定义的文件职责划分：

- **AGENTS.md**：工作流程、决策树、操作步骤
- **SOUL.md**：角色定义、价值观、自主权等级（L1/L2/L3）、行为边界
- **IDENTITY.md**：名字、形象类型、性格基调、emoji、头像——仅此四项，不写工作职责或能力清单
- **TOOLS.md**：本机环境备忘（脚本路径、环境变量、工具别名）——不写工作流程，不重复 SKILL.md 内容
- **MEMORY.md**：跨会话需保留的背景知识（产品手册、用户偏好、历史记录）——不写工具使用规范
- **HEARTBEAT.md**：周期性巡检任务清单，保持短小
- **BOOTSTRAP.md**：一次性首次运行引导，完成后删除
- **USER.md**：服务对象信息



Codex 被授权在本仓库中执行任何 git 命令（包括 push、branch、tag 等），无需逐次确认。
