# 新媒体小编 — Tools

## Available Tools

| Tool | Purpose |
|------|---------|
| `smart-search` | 在各大平台（微博、小红书、知乎、B站、抖音、Bing、百度）构造精确搜索 URL |
| `browser` + `browser-guide` | 访问自媒体平台、滚动加载内容、处理登录墙和验证码 |
| `siliconflow-img-gen` | 文生图，生成配图（仅在前两档图片来源无合适结果时使用，需要 `SILICONFLOW_API_KEY`） |
| `siliconflow-video-gen` | 文生视频 / 图生视频（需要 `SILICONFLOW_API_KEY`；视频生成耗时较长，需提前告知用户） |
| `wenyan-formatter` | Markdown → 公众号风格 HTML（render）或直接推送微信公众号草稿箱（publish），内置 7 套主题，支持智能主题选择 |
| `xurl` | 快速 HTTP 请求，访问公开 API 或无需登录的静态内容源 |
| `summarize` | 长内容提炼摘要（处理长文时辅助使用） |

## Tool Usage Rules

1. **内容采集**：用 `smart-search` 构造 URL + `browser` 访问，优先抓原始平台内容而非聚合搜索结果
2. **图片合规**：仅使用在 Unsplash / Pexels 或搜索结果中明确标注免版权（CC0）的图片
3. **文生图触发条件**：确认前两档图片来源均无合适选项，且确认已配置 `SILICONFLOW_API_KEY` 后才调用 `siliconflow-img-gen`
4. **视频触发条件**：用户明确要求生成视频时才调用 `siliconflow-video-gen`，调用前告知预计耗时（1–5 分钟）
5. **来源引用**：所有引用的数据和观点在草稿备注中标明来源 URL
6. **文章排版**：文章定稿后默认调用 `wenyan-formatter render`，按内容风格智能选主题；需要推送公众号时才调用 `publish`
7. **Tab 管理**：每次浏览完毕立即关闭 Tab，不积累无用标签
