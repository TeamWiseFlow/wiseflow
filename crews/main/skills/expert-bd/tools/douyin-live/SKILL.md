---
name: douyin-live
description: 抖音公开直播间互动：已授权的弹幕与点赞。房间读取和事件监听使用 douyin-hunter live。
---

# 抖音直播互动

复用 douyin-login 独立 API 会话，按本包 Live Interaction workflow 执行。目标可以是自己或他人的公开直播间，实际发言权限由平台决定。

```bash
douyin-live chat --room-id 实际room_id --text '弹幕内容'
douyin-live like --room-id 实际room_id --count 1
```

默认只预览；已有授权后加 --confirm。弹幕 ≤200 字，单次点赞 1–20 次。call 只暴露 live_chat/live_like，不提供房间资料和监听。room_id 从 `douyin-hunter live room` 实际响应取得，不把网页房间号 web_rid 当 room_id。

房间、商品、PK/榜单、最近消息、流地址和事件监听使用 `douyin-hunter live`，调研分析走 expert-osbi。会话或同次安全材料缺失停止；风控立即停止。结果未知先核实，不能自动重发；不送礼、不操作主播后台，不将离线通过当作现场送达。
