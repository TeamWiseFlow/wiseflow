---
name: tiktok-live
description: TikTok公开直播互动：已授权文字发送与点赞；公开房间和事件读取使用 tiktok-hunter live。
---

# TikTok 直播互动

```bash
tiktok-live send '<直播间>' '弹幕文案'
tiktok-live like '<直播间>'
tiktok-live methods
```

默认预览，已有动作授权时加 --confirm。通过 --account 指定同一真实账号，使用完整字符串 ID。登录与同次 ticket-guard 写入材料按 tiktok-hunter 说明准备，缺失时在请求前停止。

房间查询、搜索、分类、进房历史、榜单、礼物列表、流地址与有界监听全部使用 `tiktok-hunter live`；本工具仅支持 send/like，竞争调研由 expert-osbi 编排。没有商品、赠礼支付或主播后台能力。超时/断连先核对，不自动重发或换通道补发；写入仍需实号验证。
