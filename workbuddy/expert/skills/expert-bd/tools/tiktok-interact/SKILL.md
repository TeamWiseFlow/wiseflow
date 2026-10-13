---
name: "tiktok-interact"
description: "TikTok作品互动，支持范围以工具能力表为准。"
description_zh: "TikTok作品互动，支持范围以工具能力表为准。"
description_en: "tiktok-interact: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# TikTok interact

点赞/取消、收藏/取消、关注/取消、评论发布；用 call folder create/update/add 管理收藏夹（add 只能加入已收藏作品）。没有评论点赞、删除或转发写接口。

```bash
tiktok-interact like "<作品链接>"
tiktok-interact comment "<作品链接>" --text "真实讨论内容"
tiktok-interact reply "<作品链接>" --reply-to "<真实评论ID>" --text "回复内容"
tiktok-interact follow "<账号>" --confirm
tiktok-interact call <resource> <action> [平台选项]
tiktok-interact --help
```

写操作默认预览，已有授权时加 --confirm。查询通过 --account 指定同一个真实账号，完整ID作为字符串传递。列表默认20条、最多100条；监听 --duration 为1s–10m，默认1m，输出JSONL。不无限监听，不把样本当完整历史。

登录使用 `tiktok-hunter login/export`，写材料准备按 `tiktok-hunter` 说明执行。TikTok 写操作缺少同次 ticket-guard 材料时脚本在请求前阻止。只执行真实接口已支持的动作，仍须本地实号验证响应、送达与权限。超时/断连先核对结果，不换通道重发；风控不当作登出。

内容搜索、作品、用户和评论采集使用 `tiktok-hunter`。公开资料使用 `tiktok-hunter`，直播读取使用 `tiktok-hunter live`，调研分析交 当前实际可用的公开资料检索能力；已授权互动按 expert-bd 的 Interaction/Live Interaction workflow 执行。记录真实目标、动作、时间和结果，不将预览当作已送达。
