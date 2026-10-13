---
name: "tiktok-live"
description: "TikTok公开直播互动：已授权文字发送与点赞；公开房间和事件读取使用 tiktok-hunter live。"
description_zh: "TikTok公开直播互动：已授权文字发送与点赞；公开房间和事件读取使用 tiktok-hunter live。"
description_en: "tiktok-live: native Xiaobei workflows, tools and reusable resources."
version: "0.3.2"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# TikTok 直播互动

```bash
tiktok-live send '<直播间>' '弹幕文案'
tiktok-live like '<直播间>'
tiktok-live methods
```

默认预览，已有动作授权时加 --confirm。通过 --account 指定同一真实账号，使用完整字符串 ID。登录与同次 ticket-guard 写入材料按 tiktok-hunter 说明准备，缺失时在请求前停止。

房间查询、搜索、分类、进房历史、榜单、礼物列表、流地址与有界监听全部使用 `tiktok-hunter live`；本工具仅支持 send/like，竞争调研由 当前实际可用的公开资料检索能力 编排。没有商品、赠礼支付或主播后台能力。超时/断连先核对，不自动重发或换通道补发；写入仍需实号验证。
