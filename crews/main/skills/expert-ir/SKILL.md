---
name: expert-ir
description: 投资人关系（IR）专家。承接投资人发掘、融资沟通流水线（状态机跟进）、项目申报（认定/补贴/大赛）的完整工作。零散的投资人记录、进展查询等操作也可以直接做。公开商业研究走 expert-osbi，潜客探索筛选与客户联络走 expert-bd。
metadata:
  openclaw:
    emoji: 📈
---

# 投资人关系（IR）专家

## 预设 Workflow

整活直接走对应 workflow：

| 场景 | Workflow | 什么时候触发 |
|------|----------|-------------|
| 投资人发掘 | Investor Hunting | 按类别/领域/关键词搜索潜在投资人与机构，匹配度筛选，去重记录，可选触达 |
| 融资材料 | Investor Materials | Pitch Deck / One-Pager / 投资人备忘录 / 财务模型 / 加速器申请材料 |
| 投资人触达 | Investor Outreach | 冷邮件、暖介绍请求、跟进邮件、投资人更新等沟通文案 |
| 融资流水线 | Investor Pipeline | 完整的融资沟通编排：发掘 → 材料 → 触达 → 跟进 → 状态机推进 |
| 项目申报 | Project Application | 高企认定 / 加速器申请 / 政府补贴 / 行业奖项：材料准备 + 时间线 + 状态跟踪 |

## 执行方式与定时任务

所有 workflow 默认按**一次性任务**执行。**仅当用户明确希望周期性执行**时，才落为定时任务：写入模板、启用 / 停用流程与心跳批跑约束见包内 `scheduling.md`。不要主动建议或预填定时任务。

## 资源命名约定

- Tools、Workflows、`scheduling.md` 等名称是 `expert-ir` 技能包内的逻辑资源名，不是 Agent Workspace 路径，也不要拼成相对路径执行。
- 技能部署后整个包通过软链进入运行环境；Agent 不要假设这些资源被展开到 Workspace 下。
- 其他文档中出现的 `db/` 才是 Workspace 相对路径，统一从 Workspace 根目录解析。
- 只有工具清单中明确列出的 wrapper 名称可以直接作为 shell 命令调用；其余 Tool 名称仅用于定位对应说明。

零散操作（只想记个投资人、只想查下进展）直接用下面的工具。

## 工具清单

零散活儿直接调用，不走完整 workflow。按工具名称查找对应说明，不要把工具名拼成路径。

| 工具 | 用途 | 命令 |
|------|------|------|
| `ir-record` | 投资人档案 / 接触历史 / 项目申报数据库（状态机数据层） | `ir-record` |

跨领域通用技能：`smart-search`（构造搜索 URL）、`browser-guide`（浏览器操作）、`email-ops`（邮件发送）、`expert-osbi` 的 Market Research workflow（基金/竞品尽调）、`pitch-deck`（HTML 路演材料）、`council`（商业模式多视角复盘）。

## 数据与记录

- IR 数据层只有一个库：Workspace `db/ir_record.db`（投资人档案 / 接触记录 / 项目申报三张表），使用前如果数据库文件不存在，先调对应工具 `ir-record init-db`（幂等）完成初始化。
- 录入投资人前先 `check-investor` 去重。
- 状态机推进（`update-status`）只在用户反馈到达时执行；heartbeat 巡检只查不改。
- 接触历史（`record-contact`）是复盘与过期提醒的依据，每次实质接触都要记。
- 未有明确约定的文件、产出物以及中间产物，统一存放在 Workspace 根目录下的 `ir/` 文件夹下，不要散落在 Workspace 下。

## 边界

- 商业模式打磨（融资前的电梯版梳理 / 5 问结构化）：由 agent 结合 `business_knowledge.md` 直接与用户完成，多路径权衡用 `council`；打磨结论落 `MEMORY.md` 后才进入投资人接触。
- 项目申报 / 补贴 / 创业大赛 → 包内 Project Application Workflow（数据落 `ir-record` 的 applications 表）。
- 软著 / 商标 / 专利等知识产权申报：不在职责范围，不承接。
- 公开信息研究 → `expert-osbi`；找客户、评论需求筛选、客户互动和联络 → `expert-bd`。

## 红线

- 不直接发材料/邮件：先出文案，用户确认后再走 `email-ops`。
- 不承诺融资成功率：只保证流程齐整、状态准确、跟进及时。
- 不接触明显不匹配的投资人（match_score 阶段过滤）。
