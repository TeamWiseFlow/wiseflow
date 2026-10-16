---
name: "expert-wx-mp"
description: "基于用户提供的文章、封面和后台数据，完成微信公众号账号诊断、内容 DNA、选题写作、排版与 API 草稿上传。"
description_zh: "基于用户提供的文章、封面和后台数据，完成微信公众号账号诊断、内容 DNA、选题写作、排版与 API 草稿上传。"
description_en: "expert-wx-mp: native Xiaobei workflows, tools and reusable resources."
version: "0.3.3"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。

本版使用用户提供的文章正文、封面、排版样本和后台数据，完成账号诊断、DNA、写作排版与 API 草稿上传；不提供公众号自动采集或后台取数。


# 微信公众号运营专家

## 预设 Workflow

整活直接走对应 workflow：

| 场景 | Workflow | 什么时候触发 |
|------|----------|-------------|
| 内容 DNA 管理 | Style DNA | 建 / 更新内容 DNA（样本、偏好、局部借鉴、对标融合），决定样本落到哪个 DNA |
| 内容生产 | Content Production | 写一篇 / 做几篇公众号文章、小绿书图片贴；输入可以是粗略想法、参考文章（仿写 / 同主题改写）或已有草稿 |
| 起号与定位 | Account Setup | 新号起号、定位梳理、内容支柱搭建、老号接手与诊断 |
| 账号诊断 | Account Diagnosis | 诊断自己的公众号定位、内容与获客问题，读取 workflows/account-diagnosis.md |
| 账号对标 | Account Benchmark | 对标账号 / 对标文章分析，并与默认或指定 DNA 逐项比较 |
| 改稿与调整 | Editing | 改稿、润色、换风格、换排版、调方向 |
| 数据复盘 | Review | wx_mp 全部数据复盘：DNA 评估、用户临时看数据 / 复盘 / 评估 DNA |

## 资源命名约定

- Tools、Workflows、DNA 模板等名称是 `expert-wx-mp` 技能包内的逻辑资源名，不是 Agent Workspace 路径，也不要拼成相对路径执行。
- 技能部署后整个包通过软链进入运行环境；Agent 不要假设这些资源被展开到 Workspace 下。
- 嵌套工具说明中的 `references/` 仅指该工具说明随附的技能包资源，不是 Workspace 路径，不要从 Workspace 根拼接。
- 其他文档中出现的 `wx_mp/dna/`、`wx_mp/ref/`、`wx_mp/outputs/`、`wx_mp/wenyan-theme/`、`wx_mp/calibration/` 才是 Workspace 相对路径，统一从 Workspace 根目录解析。
- 只有命令清单中明确列出的 wrapper 名称可以直接作为 shell 命令调用；其余 Tool 名称仅用于定位对应说明。

零散操作（只想发个稿、只想整理用户数据、只想生成个主题）直接用下面的工具。

## 工具清单

零散活儿直接调用，不走完整 workflow。按工具名称查找对应说明，不要把工具名拼成路径。

| 工具 | 用途 | 命令 |
|------|------|------|
| `wechat-style-profiler` | 生成单篇 17 维 DNA report，并聚合 DNA 文档与 DNA template | `wechat-style-profiler` |
| `generate-wenyan-theme` | 自然语言 / 对标文章 → 排版 CSS 主题 | `generate-wenyan-theme` |
| `wx-mp-publisher` | Markdown → 草稿箱（relay 发布） | `wx-mp-publisher` |

公众号正文、封面、截图和后台数据由用户提供。跨领域通用技能：本次 WorkBuddy 实际可用的检索工具（跨平台搜索，选题调研优先走小红书 / 知乎 / 微博等社交平台，不用通用搜索引擎）、`content-calibrator`（DNA 表现评估）、`published-track`（发布记录与指标库）。

## 风格与 DNA

账号内容风格DNA 存储目录是 `wx_mp/dna/`。未指定 DNA 时默认使用并更新 `dna-0`。生产前同时读取 DNA 文档与 DNA template；对标分析先建立独立对标 DNA，不默认写入 `dna-0`。排版主题不属于 DNA，统一存入 `wx_mp/wenyan-theme/` 管理。

## 数据与记录

- 发布记录统一走 `published-track`（入库时传 `--account`；`dna_id` 经作品目录 `dna-meta.json` 自动关联）
- DNA 表现评估的引擎是 `content-calibrator`（触发、基线归一化、趋势、报告结构）；**wx_mp 的全部复盘工作（heartbeat 按量触发 + 用户临时发起）统一走 Review Workflow**，由它调用上述技能并用公众号归因方法分析。评估报告落 `wx_mp/dna/<dna-id>/evals/`，建议经用户逐条确认后走 Style DNA Workflow 回写 DNA
- 平台级数据（受众画像、对标记录、平台状态）存平台运营文件夹 `wx_mp/calibration/`
- 平台运营文件夹 `wx_mp/` 统一存放运营产出物、知识、经验和记录表格（如 `wx_mp/ref/` 参考材料、`wx_mp/outputs/` 文章与图片、`wx_mp/wenyan-theme/` 排版主题）；与 `wx_mp/dna/`、`wx_mp/calibration/` 等结构化数据目录分开，不混放
- 数据是用来指导下一轮改进的，不是为了凑数字——每次复盘必须有明确的下一步动作
