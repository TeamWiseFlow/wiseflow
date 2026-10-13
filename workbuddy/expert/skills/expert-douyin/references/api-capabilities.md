# 抖音能力路由

| 业务 | 入口 |
| --- | --- |
| 内容 DNA、定位、创作、对标、图文分析 | 本包对应 workflow 与 douyin-style-profiler |
| 账号、作品、评论、搜索、媒体下载 | douyin-hunter |
| 视频转写与关键帧 | 先 douyin-hunter 下载，再 viral-chaser 分析本地视频 |
| 已有视频素材加工 | video-edit / talking-head-cut / video-review |
| 已实现的互动、私信、直播写操作 | expert-bd 的对应工具 |
| 发布 | 交付完整材料，由用户原平台发布；本次有真实 WorkBuddy 发布能力时按其说明执行 |
| 本人后台数据与复盘 | 用户导出数据 → published-track update-metrics → content-calibrator 与 review workflow |

采集和 BD 使用 douyin-login 的独立 API 会话。没有发布或本人后台取数的本地入口，不借用宿主浏览器 profile。
