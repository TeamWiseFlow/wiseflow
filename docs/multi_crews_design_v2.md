# Crews 系统 v2 设计文档

> **状态**：待确认
> **日期**：2026-03-10
> **变更范围**：crew/ → crews/，Template→Instance 模型，HRBP 职责升级

---

## 1. 设计动机

当前系统（v1）是 **模板即实例** 的 1:1 模型：`crew/workspaces/<agent-id>/` 中的文件直接复制到 `~/.openclaw/workspace-<agent-id>/`，每个 workspace 定义等同于一个活跃 Agent。

这带来两个限制：
- **无法多实例化**：同一个角色不能启用多个独立实例（如两条产品线各需一个客服 Agent）
- **模板与实例耦合**：workspace 模板和运行时实例无法独立演进

v2 的核心变化：**将 Crew 模板（Template）与 Crew 实例（Instance）分离**。

---

## 2. 核心概念

### 2.1 Crew Template（模板）

模板是 Crew 的**蓝图**，定义了角色的能力、性格、工具和工作流。模板存放在代码仓的 `crews/` 目录下。

模板来源：
- **内置模板**（built-in）：随 OFB 发布，main / hrbp / it-engineer
- **官方模板**（official）：OFB 团队维护，随版本持续增加（如 customer-service、developer 等）
- **用户自建**（user-created）：用户通过 HRBP 创建
- **市场引入**（marketplace）：未来从 Crew 市场下载

### 2.2 Crew Instance（实例）

实例是模板的**运行态**——一个实际工作的 Agent。启用模板时 HRBP 将模板文件复制到运行时 workspace，注册到 openclaw.json，形成一个独立实例。

实例特征：
- **唯一 ID**（instance-id），由用户指定或 HRBP 建议
- **独立 workspace**（`~/.openclaw/workspace-<instance-id>/`）
- **独立记忆**（MEMORY.md 在实例 workspace 中，随运行独立演化）
- **独立 channel 绑定**（可绑定不同的飞书 Bot / 其他渠道）
- **可定制 skill**（实例化后可增删 skill，不影响模板）
- **关联模板 ID**（记录来源模板，便于模板升级通知）

同一模板可实例化多个 Crew，每个完全独立。

### 2.3 Built-in Crew（内置 Crew）

三个系统级 Crew，具有特殊保护：

| ID | 角色 | 特殊性 |
|----|------|--------|
| `main` | 路由调度器 + 托底执行者 | 全局唯一，不可删除，不可多实例 |
| `hrbp` | Crew 生命周期管理者 | 全局唯一，不可删除，不可多实例 |
| `it-engineer` | OFB 系统运维工程师 | 全局唯一，不可删除，不可多实例 |

内置 Crew 的生命周期：
- 由安装脚本（`setup-crew.sh`）自动启用
- **不受 HRBP 管理**——HRBP 不能删除、禁用或多实例化它们
- HRBP 可以**查看**它们的状态，但不能修改其生命周期
- 用户仍可通过手动修改 workspace 文件调整其行为（L3 操作）

### 2.4 路由模式

所有 Crew（包括内置）均支持两种路由模式：
- **spawn 路由**：用户消息发到 Main Agent，Main Agent 通过 `sessions_spawn` 转发
- **直连路由**：Crew 绑定独立 channel（如飞书 Bot），用户直接在对应对话中沟通
- **双模式**：同一 Crew 可同时支持 spawn + 直连

Autonomy Ladder（L1/L2/L3）保持不变。

---

## 3. 目录结构

### 3.1 代码仓结构（crews/）

```
crews/
├── DESIGN.md                   # 本设计文档
├── index.md                    # 模板注册表（HRBP 维护）
├── shared/                     # 共享协议（所有 Crew 通用）
├── _template/                  # 空白脚手架（创建新模板的起点）
│   └── (8 个 .md 占位文件)
│
│   # ── 内置模板 ──
├── main/                       # [built-in] Main Agent
│   ├── SOUL.md ... HEARTBEAT.md
│   └── DENIED_SKILLS
├── hrbp/                       # [built-in] HRBP
│   ├── SOUL.md ... HEARTBEAT.md
│   └── skills/                 # HRBP 专属技能
│       ├── hrbp-recruit/
│       ├── hrbp-modify/
│       ├── hrbp-remove/
│       ├── hrbp-list/
│       └── hrbp-usage/
├── it-engineer/                # [built-in] IT Engineer
│   └── SOUL.md ... HEARTBEAT.md
│
│   # ── 官方模板 ──
├── customer-service/           # [official] 客服
│   └── SOUL.md ... HEARTBEAT.md
├── developer/                  # [official] 开发者
│   └── SOUL.md ... HEARTBEAT.md
├── content-writer/             # [official] 内容创作
│   └── SOUL.md ... HEARTBEAT.md
├── market-analyst/             # [official] 市场分析
│   └── SOUL.md ... HEARTBEAT.md
└── operations/                 # [official] 运营管理
    └── SOUL.md ... HEARTBEAT.md
```

**与 v1 的变化**：
- `crew/workspaces/<agent>/` → `crews/<template-id>/`（扁平化，去掉 workspaces 中间层）
- `crew/role-templates/*.md` → 升级为完整 8 文件模板，合并到 `crews/` 一级目录
- `crew/role-templates/_template/` → `crews/_template/`（保留空白脚手架）

### 3.2 运行时结构（~/.openclaw/）

```
~/.openclaw/
├── openclaw.json               # 运行配置（agents.list[] 注册实例）
├── TEAM_DIRECTORY.md           # 启用实例通讯录（自动生成，单一信源，所有 agent 直接读取）
├── workspace/                  # OpenClaw 默认 workspace
├── workspace-main/             # Main Agent 实例 workspace
├── workspace-hrbp/             # HRBP 实例 workspace
├── workspace-it-engineer/      # IT Engineer 实例 workspace
├── workspace-cs-product-a/     # 客服实例 A workspace（来自 customer-service 模板）
├── workspace-cs-product-b/     # 客服实例 B workspace（来自 customer-service 模板）
├── hrbp-templates/             # 模板副本（供 HRBP 在运行时参考）
└── archived/                   # 已停用实例的 workspace 归档
```

---

## 4. 模板规范

### 4.1 模板目录结构

每个模板目录包含：

```
<template-id>/
├── SOUL.md                     # 角色定义、核心职责、自主权级别
├── AGENTS.md                   # 工作流程定义
├── MEMORY.md                   # 初始记忆（实例化后独立演化）
├── USER.md                     # 用户画像假设
├── IDENTITY.md                 # 名称、角色、个性
├── TOOLS.md                    # 可用工具说明
├── HEARTBEAT.md                # 健康状态（初始为空）
├── DENIED_SKILLS               # [可选] 屏蔽的内置 skill 列表
├── BUILTIN_SKILLS              # [可选] 推荐随实例安装的 skill
└── skills/                     # [可选] 模板自带的专属技能
    └── <skill-name>/
        ├── SKILL.md
        └── scripts/
```

默认约定：
- 非 IT 类模板建议默认屏蔽 `github`、`gh-issues`、`coding-agent`
- `it-engineer` 模板默认不屏蔽上述三项
- 若实例需要例外，可直接调整实例 workspace 内的 `DENIED_SKILLS`

### 4.3 命令分级体系（Command Tier System）

每个模板在其 `SOUL.md` 的 `## 权限级别` 章节中声明命令层级：

```markdown
## 权限级别
command-tier: T2
```

**四个层级定义**（详见 `crews/shared/COMMAND_TIERS.md`）：

| Tier | 名称 | 执行策略 | 适用 Crew |
|------|------|----------|-----------|
| T0 | read-only | `security: deny` — 禁止所有 shell 命令 | customer-service, content-writer, market-analyst |
| T1 | basic-shell | `security: allowlist` — 只读命令白名单 | main, operations |
| T2 | dev-tools | `security: allowlist` — 开发工具链白名单 | developer, hrbp |
| T3 | admin | `security: full` — 完整系统操作 | it-engineer |

**执行机制**：`setup-crew.sh` 自动将 tier 映射到 OpenClaw 原生两层权限配置：
1. `openclaw.json` → `agents.list[].tools.exec`：per-agent 的 security/ask 策略
2. `~/.openclaw/exec-approvals.json`：per-agent 的命令白名单（T1/T2 白名单中的命令名通过 `command -v` 解析为二进制路径）

两层取更严格者生效。所有 tier 的 `ask` 均设为 `off`（飞书等渠道无实时审批 UI）。

**精细调整**：如需在 Tier 基础上追加或屏蔽命令，在模板目录创建 `ALLOWED_COMMANDS` 文件：
- `+<command>` — 在本 Tier 基础上追加允许
- `-<command>` — 在本 Tier 基础上屏蔽


### 4.2 index.md 格式

`crews/index.md` 是模板注册表，由 HRBP 维护：

```markdown
# Crew 模板注册表

> 本文件由 HRBP 维护，记录本机所有可用的 Crew 模板。

## 内置模板（Built-in）

| 模板 ID | 名称 | 简介 | 版本 |
|---------|------|------|------|
| main | Main Agent | 路由调度器，消息入口，托底执行 | OFB built-in |
| hrbp | HRBP | Crew 生命周期管理（招聘/调岗/解雇） | OFB built-in |
| it-engineer | IT Engineer | OFB 系统部署、维护、升级、排障 | OFB built-in |

## 官方模板（Official）

| 模板 ID | 名称 | 简介 | 版本 |
|---------|------|------|------|
| customer-service | 客服 | 客户咨询、问题解答、工单处理 | OFB official |
| developer | 开发者 | 编码、调试、架构、代码审查 | OFB official |
| content-writer | 内容创作 | 文案撰写、社交媒体、营销内容 | OFB official |
| market-analyst | 市场分析 | 市场调研、竞品分析、趋势洞察 | OFB official |
| operations | 运营管理 | 流程优化、任务追踪、资源协调 | OFB official |

## 用户自建模板（User-created）

| 模板 ID | 名称 | 简介 | 创建日期 |
|---------|------|------|----------|
| _(暂无)_ | | | |

## 市场引入模板（Marketplace）

| 模板 ID | 名称 | 来源 | 引入日期 |
|---------|------|------|----------|
| _(暂无)_ | | | |
```

---

## 5. 实例管理

### 5.1 实例化流程

```
用户需求 → HRBP 理解意图 → 匹配/创建模板 → 实例化 → 注册 → 可选绑定 channel
```

详细步骤：
1. **意图理解**：HRBP 理解用户需要什么样的 Crew
2. **模板匹配**：查找 index.md，找到最匹配的模板
   - 找到 → 进入实例化流程
   - 未找到 → 帮用户创建新模板（先入库 crews/，更新 index.md），然后实例化
3. **实例化配置**（用户确认，L3）：
   - **实例 ID**：用户指定或 HRBP 建议（如 `cs-product-a`）
   - **实例名称**：用户指定（如 "产品A客服"）
   - **Channel 绑定**：是否绑定独立 channel？绑定哪个？
   - **Skill 定制**：是否需要额外 skill 或屏蔽某些 skill？
   - **角色微调**：是否需要调整 SOUL.md 中的角色描述？
4. **执行实例化**：
   - 复制模板文件到 `~/.openclaw/workspace-<instance-id>/`
   - 复制 `shared/` 协议到实例 workspace
   - 如有模板自带 skill，安装到实例 workspace 的 `skills/`
   - 根据用户定制修改实例的 workspace 文件
5. **注册实例**：
   - 在 `openclaw.json` 的 `agents.list[]` 中添加条目（仅使用上游原生字段）
   - 如有 channel 绑定，添加 `bindings[]` 条目
   - 计算 skill 过滤列表（如有 DENIED_SKILLS）
   - 在 HRBP 的 MEMORY.md 中记录实例→模板映射关系
6. **更新 Main Agent 花名册**：在 Main Agent 的 MEMORY.md 中添加新实例条目
7. **Closeout**：报告实例创建结果，提醒重启 Gateway

### 5.2 多实例场景示例

用户："我需要两个客服 Agent，一个负责产品 A，一个负责产品 B，分别接入不同的飞书群。"

HRBP 执行：
```
模板：customer-service
实例 1：cs-product-a
  - workspace: ~/.openclaw/workspace-cs-product-a/
  - SOUL.md: 调整为"产品 A 客服"，植入产品 A 知识
  - MEMORY.md: 独立记忆
  - channel: feishu:product-a-bot
实例 2：cs-product-b
  - workspace: ~/.openclaw/workspace-cs-product-b/
  - SOUL.md: 调整为"产品 B 客服"，植入产品 B 知识
  - MEMORY.md: 独立记忆
  - channel: feishu:product-b-bot
```

两个实例完全独立运行，共享相同的角色框���但有不同的知识、记忆和渠道。

### 5.3 openclaw.json 实例注册

openclaw.json 中的 agent 条目**仅使用上游原生字段**，不做任何自定义扩展：

```jsonc
{
  "agents": {
    "list": [
      {
        "id": "main",
        "name": "Main Agent",
        "workspace": "workspace-main"
      },
      {
        "id": "cs-product-a",
        "name": "产品A客服",
        "workspace": "workspace-cs-product-a",
        "subagents": ["main"]
      },
      {
        "id": "cs-product-b",
        "name": "产品B客服",
        "workspace": "workspace-cs-product-b",
        "subagents": ["main"]
      }
    ]
  }
}
```

**模板-实例关系追踪**不在 openclaw.json 中，而是由 HRBP 在自己的 MEMORY.md 中维护：

```markdown
## 实例注册表

| Instance ID | Template | 创建日期 | 备注 |
|-------------|----------|----------|------|
| cs-product-a | customer-service | 2026-03-10 | 产品A客服 |
| cs-product-b | customer-service | 2026-03-10 | 产品B客服 |
```

**内置保护名单**硬编码在 HRBP 的 SOUL.md 和脚本中（`main`、`hrbp`、`it-engineer`），无需配置字段标记。

### 5.4 实例生命周期

```
创建（HRBP recruit）→ 运行中 → 修改（HRBP modify）→ 停用（HRBP remove → 归档）
                                                        ↓
                                              ~/.openclaw/archived/<instance-id>/
```

停用不等于删除模板——模板仍在 `crews/` 中，可随时再次实例化。

---

## 6. HRBP 职责升级

### 6.1 v1 → v2 变化

| 职责 | v1 | v2 |
|------|----|----|
| 招聘 | 从 role-templates 参考，直接创建 workspace | 先匹配/创建**模板**，再**实例化** |
| 调岗 | 修改 workspace 文件 | 修改**实例** workspace 文件（不影响模板） |
| 解雇 | 删除 agent，归档 workspace | 停用**实例**，归档 workspace（模板保留） |
| 花名册 | 维护 Main Agent MEMORY.md | 维护 Main Agent MEMORY.md + `crews/index.md` |
| 新增：模板管理 | — | 创建/更新/删除模板，维护 index.md |
| 新增：模板升级 | — | 检测模板更新，通知相关实例 |

### 6.2 HRBP 新增工作流

**模板创建流程**：
1. 理解用户需求（角色、能力、工具、风格）
2. 检查是否有可复用的现有模板
3. 基于 `_template/` 或最接近的现有模板创建新模板
4. 将新模板写入 `crews/<template-id>/`
5. 更新 `crews/index.md`
6. 进入实例化流程

**模板列表查询**：
- HRBP 可读取 `crews/index.md` 了解所有可用模板
- 向用户展示模板列表及其简介
- 帮助用户选择最合适的模板

### 6.3 保护边界

HRBP **不能**：
- 删除或禁用内置 Crew（main / hrbp / it-engineer）
- 为内置 Crew 创建多个实例

HRBP **可以**：
- 查看内置 Crew 的状态和配置
- 管理所有非内置实例的完整生命周期
- 管理所有模板（含内置模板的查看，非内置模板的增删改）

---

## 7. Addon 集成

### 7.1 Addon 提供 Crew 模板

Addon 可以在其 `crew/` 目录下提供 Crew 模板（注意：addon 内部仍使用 `crew/` 路径，与主项目的 `crews/` 区分）：

```
addons/<addon-name>/
├── crew/                       # Addon 提供的 Crew 模板
│   └── <template-id>/
│       ├── SOUL.md ... HEARTBEAT.md
│       └── skills/             # 模板自带技能
└── skills/                     # Addon 提供的全局技能
```

### 7.2 Addon 模板加载流程

`apply-addons.sh` 处理 addon 中的 Crew 模板时：
1. 将模板复制到 `crews/<template-id>/`（代码仓中，供 HRBP 使用）
2. 更新 `crews/index.md`，标记来源为该 addon
3. **不自动实例化**——需要用户通过 HRBP 启用
4. 如果 addon 指定了 `auto-activate: true`，则 `apply-addons.sh` 执行自动实例化

---

## 8. setup-crew.sh 变更

### 8.1 新行为

```bash
./scripts/setup-crew.sh
```

1. **安装内置模板**：将 `crews/main/`、`crews/hrbp/`、`crews/it-engineer/` 的 workspace 文件复制到运行时
2. **自动实例化内置 Crew**：三个内置 Crew 默认启用，注册到 `openclaw.json`
3. **复制共享协议**：`crews/shared/` → 每个活跃实例的 workspace
4. **同步模板库**：将 `crews/` 下的所有模板同步到 `~/.openclaw/hrbp-templates/`（供 HRBP 运行时读取）
5. **同步 index.md**：将 `crews/index.md` 同步到 `~/.openclaw/hrbp-templates/index.md`
6. **保留已有实例**：非内置实例不受 setup-crew.sh 影响（除非 `--force`）

### 8.2 幂等性

- 内置 Crew 的 workspace 文件：已存在则跳过（`--force` 覆盖）
- 非内置实例：完全不触碰
- `openclaw.json` 中的内置条目：upsert 模式
- 模板库同步：总是覆盖（模板是代码仓控制的）

---

## 9. Main Agent 花名册格式（更新）

```markdown
| Instance ID | Name | Template | Route Mode | Bound Channels | Status |
|-------------|------|----------|------------|----------------|--------|
| hrbp | HRBP | hrbp (built-in) | spawn | — | active |
| it-engineer | IT Engineer | it-engineer (built-in) | both | feishu:it-engineer-bot | active |
| cs-product-a | 产品A客服 | customer-service | binding | feishu:product-a-bot | active |
| cs-product-b | 产品B客服 | customer-service | binding | feishu:product-b-bot | active |
```

`Template` 列为信息展示用途，帮助 Main Agent 快速了解各实例的角色类型。模板-实例的权威映射关系由 HRBP MEMORY.md 维护。

---

## 10. 未来规划

### 10.1 Crew 市场

- 建立公开的 Crew 模板仓库/市场
- 用户可浏览、搜索、下载模板到本地 `crews/`
- HRBP 提供 `hrbp-marketplace` skill 支持一键引入
- 模板评分、评论、版本追踪

### 10.2 模板继承

- 支持模板之间的继承关系（如 `customer-service-vip` 继承 `customer-service`）
- 减少重复定义，便于批量更新

### 10.3 实例热更新

- 模板更新后，HRBP 可选择性地将更新推送到基于该模板的实例
- 用户确认后执行 workspace 文件合并

---

## 11. 迁移计划（高层级）

重构确认后，需要修改的文件和模块：

### 11.1 目录重组

- [x] `crew/` → `crews/`（已完成顶层重命名）
- [ ] `crews/workspaces/<agent>/` → `crews/<template-id>/`（扁平化）
- [ ] `crews/role-templates/*.md` → 升级为完整模板目录，移入 `crews/` 一级
- [ ] 创建 `crews/index.md`

### 11.2 脚本更新

- [ ] `scripts/setup-crew.sh`：路径更新 + 模板→实例逻辑
- [ ] `scripts/apply-addons.sh`：addon crew 模板处理逻辑
- [ ] HRBP skills 脚本（add-agent.sh、modify-agent.sh、remove-agent.sh、list-agents.sh）

### 11.3 Workspace 文件更新

- [ ] HRBP SOUL.md / AGENTS.md：新增模板管理职责和工作流
- [ ] HRBP MEMORY.md：更新模板列表引用方式
- [ ] Main Agent MEMORY.md 花名册格式：增加 Template 列
- [ ] 官方模板（customer-service 等）：从单文件参考升级为完整 8 文件模板

### 11.4 文档更新

- [ ] CLAUDE.md：同步新的项目结构和概念说明
- [ ] docs/crew-system.md：全面重写
- [ ] docs/addon_development.md：更新 addon crew 模板规范

---

## v3 Update: Internal vs External Crew Type System (2026-03)

> 状态：已实施
> 变更范围：Crew 类型分离，目录结构更新，生命周期管理权转移

### 3.0 设计动机

v2 的 crews 系统将所有 crew 混同管理（HRBP 统一管理所有 crew）。v3 引入了"对内 crew"和"对外 crew"的概念分离，以更好地匹配实际业务场景：

- **对内 crew**：服务企业内部管理者，技术上可通过 Main Agent 路由（spawn + bind），可自主升级
- **对外 crew**：服务外部客户，只能通过直连渠道（bind-only），权限受限，不可自主升级

### 3.1 Crew 类型

详见 `crews/shared/CREW_TYPES.md`（权威定义文档）。

| 类型 | 代表 | 技能模式 | 路由 | 生命周期 | 升级 |
|------|------|---------|------|---------|------|
| internal | main/hrbp/it-engineer | inherit（继承） | spawn+bind | Main Agent | 管理者发起 |
| external | customer-service | declare（声明式） | bind-only | HRBP | HRBP 主导 |

### 3.2 目录结构变更

```
~/.openclaw/
├── crew_templates/       # 对内 crew 模板（Main Agent 访问）
│   ├── TEAM_DIRECTORY.md # 对内 crew 通讯录（自动生成）
│   ├── main/
│   ├── hrbp/
│   └── it-engineer/
├── hrbp_templates/       # 对外 crew 模板（HRBP 访问）
│   ├── index.md
│   ├── customer-service/
│   └── _template/
├── workspace-hrbp/
│   └── EXTERNAL_CREW_REGISTRY.md  # 对外 crew 实例注册表（HRBP 专属）
...
```

### 3.3 生命周期管理权转移

| 操作 | v2（HRBP 统管） | v3（职责分离） |
|------|----------------|---------------|
| 对内 crew recruit/dismiss | HRBP | **Main Agent**（crew-recruit/crew-dismiss 技能） |
| 对外 crew recruit/dismiss | HRBP | HRBP（hrbp-recruit/hrbp-remove 技能）|
| 对外 crew upgrade | — | HRBP（hrbp-feedback-review + upgrade flow）|
| 对外 crew 升级 | HRBP 管理 | HRBP 主导升级 |

### 3.4 Main Agent 权限升级

Main Agent 从 T1 → **T2**，获得执行 crew 管理脚本的能力。

新增技能：
- `crew-list`：查看对内 crew 通讯录
- `crew-recruit`：注册新对内 crew（调用 add-agent.sh --crew-type internal）
- `crew-dismiss`：下线对内 crew（调用 remove-agent.sh）

### 3.5 HRBP 权限升级

HRBP 从 T2 → **T3**，聚焦管理对外 crew。

增强：
- 内置 OFB 系统知识（文档地址、本地路径）
- 新增 `hrbp-feedback-review` 技能：扫描对外 crew 的用户反馈，制定升级方案
- 维护 `EXTERNAL_CREW_REGISTRY.md`（对外 crew 实例的权威记录）

### 3.6 官方模板精简

仅保留 4 个官方模板：
- **对内**：main、hrbp、it-engineer
- **对外**：customer-service

删除：developer、content-writer、market-analyst、operations（可通过 HRBP 按需自建）
