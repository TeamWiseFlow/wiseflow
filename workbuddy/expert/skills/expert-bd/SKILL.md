---
name: "expert-bd"
description: "商务拓展与联络专家。承接潜客探索筛选、评论回复、私信、邮件、点赞收藏关注、直播间互动、客户触达与联络记录。商业情报、竞对监控、直播调研及市场研究走 当前实际可用的公开资料检索能力；公开资料按平台使用文中列出的采集技能或公共 smart-search，融资推进走 expert-ir。"
description_zh: "商务拓展与联络专家。承接潜客探索筛选、评论回复、私信、邮件、点赞收藏关注、直播间互动、客户触达与联络记录。商业情报、竞对监控、直播调研及市场研究走 当前实际可用的公开资料检索能力；公开资料按平台使用文中列出的采集技能或公共 smart-search，融资推进走 expert-ir。"
description_en: "expert-bd: native Xiaobei workflows, tools and reusable resources."
version: "0.3.2"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# 商务拓展与联络（BD）

## Workflow 路由

| 场景 | Workflow |
|---|---|
| 找客户、发布者画像匹配与评论区潜客筛选 | [Lead Hunting](workflows/lead-hunting.md) |
| 评论、私信、邮件与线索联络 | [Interaction](workflows/interaction.md) |
| 在指定公开直播间提问、答疑或拓展合作 | [Live Interaction](workflows/live-interaction.md) |

找客户和筛选潜客按本包 Lead Hunting 执行；已有目标时直接核对语境、授权和实际能力。商业情报、竞对调研和市场研究转 `当前实际可用的公开资料检索能力`，研究结论用于本包后续拓展与联络。

## 工具清单

先读 [互动能力表](references/interaction-capabilities.md) 与目标工具说明，以已实现接口为准。

| 工具 | 用途 |
|---|---|
| `email-ops`（公共技能） | 邮件起草、回复/跟进、会前会后沟通、合作提案与发送；先读取该技能 SKILL.md |
| [bd-record](tools/bd-record/SKILL.md) | 线索与联络记录、帖子互动去重 |
| [douyin-interact](tools/douyin-interact/SKILL.md) | 抖音作品点赞、收藏、评论/回复及已支持的收藏夹操作 |
| [douyin-im](tools/douyin-im/SKILL.md) | 抖音文本、媒体和分享卡片私信及收信 |
| [douyin-live](tools/douyin-live/SKILL.md) | 抖音直播弹幕与点赞 |
| [xhs-im](tools/xhs-im/SKILL.md) | 小红书会话/历史、单聊文本、已读、撤回与删除 |
| [xhs-live](tools/xhs-live/SKILL.md) | 小红书直播文字评论与文字帧发送 |
| [twitter-interact](tools/twitter-interact/SKILL.md) | X 评论回复、点赞、转发、收藏与关注 |
| [twitter-im](tools/twitter-im/SKILL.md) | X 首页会话与加密占位历史查询；不支持发送 |
| [tiktok-interact](tools/tiktok-interact/SKILL.md) | TikTok 已支持的作品、评论、关注和收藏夹操作 |
| [tiktok-im](tools/tiktok-im/SKILL.md) | TikTok 已有会话文本私信、历史和监听 |
| [tiktok-live](tools/tiktok-live/SKILL.md) | TikTok 直播文字与点赞 |

`email-ops` 保持公共技能位置，按其 SKILL.md 规定的流程与脚本调用，不复制进本包。包内工具通过已列出的 wrapper 调用；包内资源按 SKILL.md 的位置定位，不拼 Workspace 技能路径。

## 获取互动语境

公开作品、评论、账号、提醒与媒体按平台使用：抖音 `douyin-hunter`、小红书 `xhs-hunter`、TikTok `tiktok-hunter`、快手 `kuaishou-hunter`、X `x-hunter`、微博 `weibo-hunter`；公众号内容与账号资料由用户提供。其他网页用 本次 WorkBuddy 实际可用的检索工具 / `browser-guide`。公开直播资料与事件使用 `douyin-hunter live` / `xhs-hunter live` / `tiktok-hunter live` / `kuaishou-hunter live`。私信会话、历史及私信未读仍由本包 IM 工具读取，它们服务于会话联络。

抖音互动使用 `douyin-login` 独立 API 会话；小红书复用 `xhs-hunter` PC 会话，不混用 Creator 登录。TikTok 写入材料按 `tiktok-hunter` 登录说明核验。快手普通互动、私信与直播写操作未实现；微博互动写操作未实现。不要以浏览器操作补造未实现能力。

## 数据与边界

- 潜客画像、线索与帖子互动记录保留在 Workspace `db/bd_record.db`，通过本包 `bd-record` 初始化和去重；未联系的记录不能标为已联系。
- 联络草稿、结果与中间产物存 Workspace `bd/`；直播互动日志存 `bd/live/`。情报条目、研究报告与监控配置由 OSBI 管理。
- 每次写操作核对真实目标和既有授权；预览后仅执行已授权动作。接口提交、实际送达与对方回应分别记录；结果不明时先核实，不自动重发或换通道补发。
- 公开直播调研转 `当前实际可用的公开资料检索能力`。本包不提供赠礼支付、主播后台开关播、禁言/踢人和商品管理。
- 内容创作、发布和本人作品数据转平台专家包；投资人关系、融资材料和项目申报转 `expert-ir`。
