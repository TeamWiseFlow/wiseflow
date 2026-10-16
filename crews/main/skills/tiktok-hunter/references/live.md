# TikTok 公开直播读取

```bash
tiktok-hunter live get '<直播间>'
tiktok-hunter live list --limit 20
tiktok-hunter live search '关键词' --limit 20
tiktok-hunter live history '<直播间>'
tiktok-hunter live media '<直播间>'
tiktok-hunter live listen '<直播间>' --duration 1m
tiktok-hunter live --help
```

get/list/search/categories/history/rank/gifts/media 与有界 listen 归 hunter；通过 --account 使用同一真实账号。list 只含关注账号中在播的；history 只覆盖进房快照；流地址不保证每场都有。没有商品接口或主播后台能力。列表最多 100 条，监听时长 1s–10m，输出 JSONL。

hunter 不允许 live send/like 或礼物支付。文字与点赞由 expert-bd 的 tiktok-live 执行，调研分析由 expert-osbi 编排。只有实际取得的事件、流地址与字段能作为证据；监听不是口播转写，不代表完整历史。登录和只读会话验证按 hunter 主说明执行，仍需真实账号验收。
