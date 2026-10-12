---
name: xhs-live
description: 小红书公开直播文字评论与文字帧发送；房间、商品和事件监听使用 xhs-hunter live。
---

# 小红书直播互动

使用 xhs-hunter login 建立的 PC 会话，先按本包 Live Interaction workflow 核对目标、文案与既有授权。不混用 Creator Cookie。host_id 是目标主播 ID，目标可为自己或他人的公开直播间。

```bash
xhs-live send '真实room_id' '评论文本' --host-id '主播user_id'
xhs-live methods
```

send、room-text、send-captured-frame room 和 call send_comment 默认预览，实际执行加 --confirm。room-text 的完整 payload 必须来自当前房间真实字段，不猜测身份、昵称或优先级；send-captured-frame 仅用于当前房间已捕获的文字帧。不支持直播点赞，不用赠礼接口代替。

房间与商品信息、观看状态及有界事件监听通过 `xhs-hunter live`，竞争调研转 expert-osbi。methods 只列发送方法，call 不允许查询方法。提交异常或结果不明先核实，不自动重发；发送仍需真实账号验收。
