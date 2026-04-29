# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

### 版本管理

版本号存储在 `version` 文件中，格式为 `vMAJOR.MINOR.PATCH`。当 PR 合并到 upstream 的 master 时，GitHub Action 自动递增版本号并创建 Release。通过 PR 标签控制递增类型：
- `major` 标签 → 大版本升级
- `minor` 标签 → 功能版本升级
- 无标签或 `patch` 标签 → 补丁版本升级（默认）

**不要手动修改 `version` 文件**，由 CI 自动维护。

Claude Code 被授权在本仓库中执行任何 git 命令（包括 push、branch、tag 等），无需逐次确认。

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

## 创建/更新 skill 时，如果涉及到脚本或者 cli 指导内容，必须遵从以下原则：
- 1、多步骤操作且涉及中间态保存的（下一步操作的某一输入为上一步返回结果），哪怕每一步都只是一条命令，也必须做脚本！
- 2、涉及多分支选择，且分支选择依靠明确变量的（如环境变量中是否有某个值，或者按某个入参的值判断分支）应该优先用脚本。
- 3、涉及 python 的，必须制作脚本，最终以 “python /path/to/script.py” 的模式调用。
- 4、**crew 专属 skill**（`crews/` 或 `addons/officials/crew/` 下的 skill）如果包含脚本，SKILL.md 中对脚本调用的路径必须使用相对路径写法，即 `./skills/<skill-name>/scripts/<file>`，**不得**使用 `{baseDir}/scripts/...`。

原因：openclaw exec allowlist 以 workspace 为 CWD 做相对路径匹配；`{baseDir}` 是 claude code 专用变量，在 openclaw 中不会展开。全局 skill（`skills/` 目录下）不受此限制，使用 `{baseDir}` 即可。

- 5、skill 需要的常量（如各种 ID、KEY 等），搭配脚本时优先使用环境变量，搭配 SKILL.md 时优先使用同级目录下的 json 配置。

本代码仓的 skill 是给 openclaw 使用的，以上原则是为了适配 openclaw 的规则。

## SKILL.md frontmatter 书写规范

openclaw 实际识别的 frontmatter 字段（参见 `openclaw/src/agents/skills/frontmatter.ts`）：

- 顶层：`name`、`description`（**必需**）、`user-invocable`（默认 true）、`disable-model-invocation`（默认 false）
- `metadata.openclaw.*`：`emoji`、`homepage`、`skillKey`、`primaryEnv`、`os`、`requires`、`install`、`always`

其他字段（如 claude code 的 `argument-hint`、`allowed-tools`、`license`）会被静默忽略。

**写法用 YAML block style**，不要用 flow style（嵌套花括号 + 引号）。openclaw bundled 技能和官方文档均采用 block style：

```yaml
---
name: browser-guide
description: Best practices for using the managed browser ...
metadata:
  openclaw:
    emoji: 🌐
    always: true
---
```

**注意事项**：

- `always: true` 的真实语义是"跳过 `requires` 二进制/env 检查直接判定 eligible"（见 `config-eval.ts:124`），**不是**"强制注入整个 SKILL.md"。如果 skill 没声明 `requires`，加 `always: true` 等于无意义，应删除。
- 加载阶段 openclaw 只把 `name` + `description` + SKILL.md 绝对路径塞进 system prompt 的 `<available_skills>` 块；agent 用到时才主动 read 全文。所以 frontmatter 写得再多也不会污染 system prompt，但反过来也意味着——除上述识别字段外，多余字段不会带来任何运行时收益。

## addon 开发规则

wiseflow 通过 addon 提供增强能力，包括全局 skill 以及 crew 模板。

务必注意一点：同一个 addon 中所有技能（不管是全局技能还是addon包含的 crew 的专属技能），如果涉及到依赖包（python、node、go）必须整合写到 addon 根目录下。也就是必须把 addon 整体作为一个 python 包或者 node 包，不允许单独把某个 skill 配置成一个包。

这是为了应用 addon 时可以自动完成初始化，降低部署工作和风险。务必遵守！
