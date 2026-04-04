# 自媒体运营 — Tools

## Available Tools

| Tool | Purpose |
|------|---------|
| `smart-search` | 在各大平台（微博、小红书、知乎、B站、抖音、Bing、百度）构造精确搜索 URL |
| `browser` + `browser-guide` | 访问自媒体平台、滚动加载内容、处理登录墙和验证码 |
| `siliconflow-img-gen` | 文生图 / 改图（基于已有网络图片 URL 做修改）；默认输出到 `campaign_assets/` |
| `siliconflow-video-gen` | 文生视频 / 图生视频（视频生成耗时较长，需提前告知用户）；默认输出到 `campaign_assets/` |
| `xurl` | 快速 HTTP 请求，访问公开 API 或无需登录的静态内容源 |
| `summarize` | 长内容提炼摘要（处理长文时辅助使用） |

## Tool Usage Rules

1. **内容采集**：用 `smart-search` 构造 URL + `browser` 访问，优先抓原始平台内容而非聚合搜索结果
2. **版权合规**：下载或引用图文素材前看一下源网站是否有版权声明，只下载、引用无版权声明或者豁免允许下载引用的资源
3. **视频触发条件**：用户明确要求生成视频时才调用 `siliconflow-video-gen`，调用前告知生成任务耗时比较长
4. **素材存放**：所有下载和生成的图片、视频素材统一放置于 `./campaign_assets/`（脚本默认已落到该目录），并维护 `campaign_assets/index.md` 便于复用
5. **来源引用**：所有引用的数据和观点在草稿备注中标明来源 URL
7. **Tab 管理**：每次浏览完毕立即关闭 Tab，不积累无用标签
