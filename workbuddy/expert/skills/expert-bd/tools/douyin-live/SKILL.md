---
name: "douyin-live"
description: "抖音公开直播间互动：已授权的弹幕与点赞。房间读取和事件监听使用 douyin-hunter live。"
description_zh: "抖音公开直播间互动：已授权的弹幕与点赞。房间读取和事件监听使用 douyin-hunter live。"
description_en: "douyin-live: native Xiaobei workflows, tools and reusable resources."
version: "0.3.2"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# 抖音直播互动

复用 douyin-login 独立 API 会话，按本包 Live Interaction workflow 执行。目标可以是自己或他人的公开直播间，实际发言权限由平台决定。

```bash
douyin-live chat --room-id 实际room_id --text '弹幕内容'
douyin-live like --room-id 实际room_id --count 1
```

默认只预览；已有授权后加 --confirm。弹幕 ≤200 字，单次点赞 1–20 次。call 只暴露 live_chat/live_like，不提供房间资料和监听。room_id 从 `douyin-hunter live room` 实际响应取得，不把网页房间号 web_rid 当 room_id。

房间、商品、PK/榜单、最近消息、流地址和事件监听使用 `douyin-hunter live`，调研分析走 当前实际可用的公开资料检索能力。会话或同次安全材料缺失停止；风控立即停止。结果未知先核实，不能自动重发；不送礼、不操作主播后台，不将离线通过当作现场送达。
