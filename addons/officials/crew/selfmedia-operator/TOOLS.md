# 自媒体运营 — Tools

## Available Tools

| Tool | Purpose |
|------|---------|
| `smart-search` | 在各大平台构造精确搜索 URL，实时获取内容 |
| `browser` + `browser-guide` | 访问自媒体平台、处理登录墙和验证码；多平台发布的执行层 |
| `wenyan-publisher` | Markdown → 平台 HTML（知乎 / 今日头条 / 掘金 / Medium），渲染后用 browser-guide 发布 |
| `siliconflow-img-gen` | 文生图 / 改图（配图 Priority 4，需 `SILICONFLOW_API_KEY`） |
| `siliconflow-video-gen` | 文生视频 / 图生视频（Wan2.2，需 `SILICONFLOW_API_KEY`） |
| `youtube-upload` | 通过浏览器将视频上传到 YouTube Shorts |
| `twitter-post` | 通过浏览器发布文字/图片/视频到 Twitter/X |
| `tiktok-post` | 通过浏览器上传视频到 TikTok（含封面、标签、隐私设置） |
| `instagram-post` | 通过浏览器发布照片/视频/轮播到 Instagram Feed 或 Reels |
| `gifgrep` | 搜索并下载 GIF 素材，或提取静帧 |
| `video-frames` | 用 ffmpeg 从视频文件提取帧或短片段 |
| `summarize` | 长内容提炼摘要 |
| File read/write | 读写 campaign_assets/、output_articles/ 工作目录 |

## 注意事项

- **图片合规**：仅使用 Unsplash / Pexels 中明确标注 CC0 / 免版权的图片，来源 URL 一并记录
- **Tab 管理**：每次浏览完毕立即关闭 Tab，不积累无用标签
- **来源引用**：所有引用的数据和观点在草稿备注中标明来源 URL
- **siliconflow-video-gen 耗时**：异步生成需 1–5 分钟，调用前告知用户
