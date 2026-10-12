---
name: sales-cs-manager
description: 对外销售客服（sales-cs crew）管理专家。承接 sales-cs 的启用（channel 选择、配置、workspace 文件初始化、业务知识接入）与启用后的复盘升级（客户反馈扫描、话术/客服手册/IDENTITY 调整）。sales-cs 是对外 crew，被设定为不根据客户反馈自主调整升级，所有调整经本包由 main agent 落地。零散的 channel 检查、反馈扫描也可以直接做。不涉及商务获客（走 expert-bd）、投资人关系（走 expert-ir）、content-producer 启用（走 AGENTS.md crew 管理段）。
metadata:
  openclaw:
    emoji: ☎️
---

# sales-cs 管理（sales-cs-manager）

## 预设 Workflow

| 场景 | Workflow | 什么时候触发 |
|------|----------|-------------|
| sales-cs 启用 | Enablement | 用户想要对外客服 / 销售客服 / 公开接待客户的 agent；从零到可用的一次性完整流程 |
| sales-cs 复盘与升级 | Review | 用户想复盘 sales-cs / 调整客服话术 / 改客服手册 / 改对外称呼 / 增减客服可用技能；或 main agent 定期检查客户反馈 |

## 资源命名约定

- Tools、Workflows 等名称是 `sales-cs-manager` 技能包内的逻辑资源名，不是 Agent Workspace 路径，也不要拼成相对路径执行。
- 技能部署后整个包通过软链进入运行环境；Agent 不要假设这些资源被展开到 Workspace 下。
- 其他文档中出现的 `~/.openclaw/workspace-sales-cs/` 等路径是实例真实路径，按字面解析；本包自身不落任何运行期数据，无 Workspace 数据目录。
- 只有工具清单中明确列出的 wrapper 名称可以直接作为 shell 命令调用；其余 Tool 名称仅用于定位对应说明。

零散操作（只想查下 channel 状态、只想扫下反馈）直接用下面的工具。

## 工具清单

| 工具 | 用途 | 命令 |
|------|------|------|
| `sales-cs-enablement` | awada channel 配置检查 + business_knowledge 软链建立 | `sales-cs-enablement check-channel` / `sales-cs-enablement link` |
| `sales-cs-review` | 扫描 sales-cs workspace 的客户反馈，输出结构化摘要 | `sales-cs-review [--since YYYY-MM-DD]` |

配置类操作（channel 绑定、`openclaw.json` 合入、Gateway 重启、daemon.env、customer-db schema）不在本包工具内，一律 spawn IT engineer 执行（其技能：`awada-channel-setup` / `work-channel-binding`）。

## 核心治理边界

- **sales-cs 不自行升级**：它被设定为不根据客户反馈自主调整自己的 workspace 文件。对它的任何调整（记忆 / 话术 / IDENTITY / 客服手册 / 可用技能）都是 main agent 的责任，一律经 Review workflow 由用户确认后落地。
- **业务知识单点维护**：`business_knowledge.md` + `business_knowledge/` 只在 main agent workspace 维护，sales-cs workspace 通过软链只读访问（Enablement workflow 建链）。改业务知识在 main workspace 改，不要在 sales-cs 侧改软链目标。
- **反馈只读**：sales-cs workspace 的 `feedback/` 是客户反馈历史，只用于复盘，不修改、不删除。

## 边界

- 商业情报 / 市场研究 -> `expert-osbi`；潜客探索筛选 / 评论区互动 / 客户联络 -> `expert-bd`。
- 投资人发掘 / 融资跟进 -> `expert-ir`。
- content-producer 启用与调整 -> AGENTS.md「crew 管理」段（不走本包）。
