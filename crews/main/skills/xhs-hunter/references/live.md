# 小红书公开直播读取

使用 `xhs-hunter live`，复用 hunter 的 PC 登录态。不要用 Creator Cookie 拼接。调研分析交 `expert-osbi`，直播文字发送交 `expert-bd` 的 `xhs-live`。

```bash
xhs-hunter live methods
xhs-hunter live call list_categories
xhs-hunter live call square_feed --kwargs '{"size":20}'
xhs-hunter live call current_room_info --args '["真实room_id"]'
xhs-hunter live listen --room-id '真实room_id' --seconds 60 --max-events 100
```

`methods` 只列房间、商品和观看相关方法。`call` 的 --args 是 JSON 数组，--kwargs 是 JSON 对象；`send_comment`、send、room-text 和 send-captured-frame 不允许通过 hunter 执行。join_room/viewer_heart 会上报观看状态，仅在实际进房或维持观看时调用；gift_panel/charge_panel 只读面板，不支付或赠礼。

监听逐行输出 JSON，最后报告事件数；时长 1–3600 秒、最多 1000 条。保留 decoded.room 中实际返回的事件，未知帧如实标记，不从空事件推断没有观众。没有完整直播历史接口。

host_id 为目标主播 ID，不要求登录账号为主播；目标可为自己或其他人的公开房间，按实际访问权限执行。监听不是口播转写，评论样本不等于整场表现。原始资料保存到调用方指定目录，直播研究默认 `osbi/live/`。仍须真实账号验收，不把离线通过当作现场成功。
