# 多 Agent 系统架构（Crews v2）

## 概述

多 Agent 系统是 openclaw-for-business 的核心组件，定义在项目根目录的 `crews/` 中。

核心理念：**Template → Instance 分离**。`crews/` 存放 Crew 模板蓝图，通过 HRBP 实例化为独立运行的 Agent。同一模板可实例化多个 Crew 实例。

设计目标：
1. **任务专业性** — 每个 Crew 聚焦特定领域
2. **多实例化** — 同一角色模板可创建多个独立实例（如两条产品线各配一个客服）
3. **并行处理** — 利用 OpenClaw 的 `sessions_spawn` 把任务拆到子进程完成

采用**混合路由模式**：
- **模式 A（统一入口）**：用户通过飞书 Bot 与 Main Agent 对话，Main Agent 通过 `sessions_spawn` 分发给子 Agent
- **模式 B（渠道直连）**：子 Agent 通过 OpenClaw 原生 `bindings` 直接绑定到特定渠道
- 同一个子 Agent 可以同时被两种方式使用

## 核心概念

### Template（模板）
模板是 Crew 的**蓝图**，定义角色的能力、性格、工具和工作流。存放在 `crews/` 目录下。

模板来源：
- **内置模板**（built-in）：main / hrbp / it-engineer — 系统级，由 `setup-crew.sh` 自动安装
- **官方模板**（official）：customer-service / developer / content-writer / market-analyst / operations
- **用户自建**（user-created）：通过 HRBP 创建
- **市场引入**（marketplace）：未来从 Crew 市场下载

### Instance（实例）
实例是模板的**运行态**——一个实际工作的 Agent。特征：
- 唯一 ID（如 `cs-product-a`）
- 独立 workspace（`~/.openclaw/workspace-<instance-id>/`）
- 独立记忆（MEMORY.md 随运行独立演化）
- 独立 channel 绑定

### Built-in Crew（内置 Crew）
三个系统级 Crew，全局唯一，不可删除，不可多实例：

| ID | 角色 | 特殊性 |
|----|------|--------|
| `main` | 路由调度器 + 托底执行者 | 消息入口 |
| `hrbp` | Crew 生命周期管理 | 招聘/调岗/解雇 |
| `it-engineer` | OFB 系统运维 | 部署/升级/排障 |

## 架构

```
模式 A: 飞书用户 → Bridge → Gateway → Main Agent → spawn 子 Agent
模式 B: 渠道用户 → OpenClaw channel → Gateway bindings → 子 Agent（直接响应）
```

**进程类型**：Gateway 单进程，所有 Agent 在内部以子进程模式运行（逻辑隔离）。

## 源码结构（crews/）

```
crews/
├── DESIGN.md              # 设计文档
├── index.md               # 模板注册表（HRBP 维护）
├── shared/                # 共享协议（所有 Crew 通用）
├── _template/             # 空白脚手架（创建新模板的起点）
│
│   # ── 内置模板 ──
├── main/                  # [built-in] Main Agent
├── hrbp/                  # [built-in] HRBP
│   └── skills/            # HRBP 专属技能
│       ├── hrbp-recruit/  # 招聘（实例化）
│       ├── hrbp-modify/   # 调岗（修改实例）
│       ├── hrbp-remove/   # 解雇（停用实例）
│       ├── hrbp-list/     # 花名册/路由状态查询
│       └── hrbp-usage/    # 用量与成本统计
├── it-engineer/           # [built-in] IT Engineer
│
│   # ── 官方模板 ──
├── customer-service/      # [official] 客服
├── developer/             # [official] 开发者
├── content-writer/        # [official] 内容创作
├── market-analyst/        # [official] 市场分析
└── operations/            # [official] 运营管理

skills/                    # 全局共享技能（项目根目录，所有 Agent 可见）
```

### 运行时结构（~/.openclaw/）

```
~/.openclaw/
├── openclaw.json               # 运行配置（agents.list[] 注册实例）
├── TEAM_DIRECTORY.md           # 启用 crew 通讯录（由脚本自动同步）
├── workspace-main/             # Main Agent 实例 workspace
├── workspace-hrbp/             # HRBP 实例 workspace
├── workspace-it-engineer/      # IT Engineer 实例 workspace
├── workspace-<instance-id>/    # 用户创建的实例 workspace
├── hrbp-templates/             # 模板副本（供 HRBP 运行时参考）
│   ├── index.md                # 模板注册表
│   ├── _template/              # 空白脚手架
│   ├── customer-service/       # 官方模板...
│   └── ...
└── archived/                   # 已停用实例的 workspace 归档
```

### 技能两级体系

与 OpenClaw 原生 skill 加载机制对齐：

| 级别 | 位置 | 安装到 | 可见范围 |
|------|------|--------|----------|
| 全局共享 | `skills/`（项目根目录） | `openclaw/skills/` | 所有 Agent |
| 模板专属 | `crews/<template>/skills/` | `~/.openclaw/workspace-<instance>/skills/` | 仅该实例 |

默认策略（OFB）：
- 每个 Agent 默认使用固定基线 bundled skills：
  `1password`、`healthcheck`、`model-usage`、`nano-pdf`、`skill-creator`、`ordercli`、`session-logs`、`tmux`、`weather`、`xurl`、`video-frames`
- addon 根目录 `skills/` 安装的全局 skills，默认对所有 Agent 开放
- addon `crew/<template>/skills/` 只安装到该实例 workspace，不会开放给其他 Agent
- `BUILTIN_SKILLS` 用于在基线上追加额外 bundled skills（例如 `github` / `gh-issues` / `coding-agent`）
- `DENIED_SKILLS` 作为最终裁剪层（从“基线 + 追加”里减掉指定 skills）

## 核心组件

### Main Agent（路由器/调度员）
- 接收用户消息，判断意图
- 优先通过 `sessions_spawn` 分发给对应子 Agent
- 汇报子 Agent 结果
- 没有匹配 crew 时才自己处理
- 如无匹配且暗示缺少能力 → 建议通过 HRBP 招聘

### HRBP Agent（Crew 生命周期管理）
- 管理 Crew 模板库（浏览、创建新模板）
- 管理实例完整生命周期：招聘（实例化）、调岗（修改）、解雇（归档）
- 受保护，不可删除
- 五个 Skill：`hrbp-recruit`、`hrbp-modify`、`hrbp-remove`、`hrbp-list`、`hrbp-usage`

### IT Engineer Agent（系统运维）
- 负责 OFB 系统的部署、维护、升级和故障排除
- 面向非技术用户，用简明语言解释技术问题
- 受保护，不可删除

## 实例来源

Crew 实例有三种创建方式：

1. **内置自动安装**：`crews/main/`、`crews/hrbp/`、`crews/it-engineer/` — 由 `setup-crew.sh` 自动实例化，不受 HRBP 管理
2. **HRBP 实例化**：用户通过与 HRBP 对话，从模板库中选择模板并实例化为运行态 Agent（默认方式）
3. **Addon 模板引入**：第三方 addon 通过 `crew/` 目录贡献模板，由 `apply-addons.sh` 安装到模板库，再由 HRBP 实例化（或 addon 指定 auto-activate）

## Workspace 结构

每个模板/实例的 workspace 包含 8 个核心文件：

| 文件 | 用途 |
|------|------|
| SOUL.md | 角色定位、身份边界 |
| AGENTS.md | 工作流和流程 |
| MEMORY.md | 长期记忆和上下文 |
| USER.md | 用户偏好 |
| IDENTITY.md | 名称、个性、声音 |
| TOOLS.md | 可用工具和使用规则 |
| HEARTBEAT.md | 健康状态 |

可选文件：
- `DENIED_SKILLS` — 屏蔽的内置 skill 列表
- `BUILTIN_SKILLS` — 在 OFB 基线之上追加的 bundled skills
- `skills/` — 模板/实例专属技能目录

## 共享协议

- **
## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/setup-crew.sh` | 安装多 Agent 系统（部署内置 Crew、同步模板库、更新配置，幂等） |
| `crews/hrbp/skills/hrbp-common/scripts/sync-team-directory.sh` | 生成 `~/.openclaw/TEAM_DIRECTORY.md`（单一信源，所有 agent 直接读取） |
| `crews/hrbp/skills/hrbp-recruit/scripts/add-agent.sh` | HRBP 内部：注册新实例 |
| `crews/hrbp/skills/hrbp-modify/scripts/modify-agent.sh` | HRBP 内部：修改实例渠道绑定 |
| `crews/hrbp/skills/hrbp-remove/scripts/remove-agent.sh` | HRBP 内部：移除实例（workspace 归档） |
| `crews/hrbp/skills/hrbp-list/scripts/list-agents.sh` | HRBP 内部：列出所有实例及状态 |
| `crews/hrbp/skills/hrbp-usage/scripts/agent-usage.sh` | HRBP 内部：统计实例用量与成本 |

## 配置

Agent 实例配置在 `~/.openclaw/openclaw.json` 中（仅使用上游原生字段）：

- `agents.list[]` — 实例列表（id、name、workspace、subagents）
- `agents.list[].skills` — 实例 skill 白名单（始终写入：基线 + 追加 - denied + workspace skills）
- `bindings[]` — 渠道绑定（模式 B 直连）
- `TEAM_DIRECTORY.md` — 基于 `agents.list[]` + `bindings[]` 的实时通讯录

模板-实例映射关系由 HRBP 的 MEMORY.md 维护，不侵入 openclaw.json。

## 路由模式

| 模式 | 说明 | 配置 |
|------|------|------|
| spawn | 通过 Main Agent 路由 | `allowAgents` 列表 |
| binding | 渠道直连 | `bindings[]` 条目 |
| both | 两种方式共存 | 同时配置 |

强制路由写法：
- `[Route: @it-engineer] 帮我看下系统日志`
- `@it-engineer 帮我看下系统日志`

生命周期权限：
- 仅 `hrbp` 可以执行 recruit/modify/remove
- `main` 只能识别并路由到 `hrbp`
