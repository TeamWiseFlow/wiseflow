# Twitter / X

> last_verified: 2026-06-15

## 搜索

### URL

| 类型 | URL |
|------|-----|
| 热门 | `https://x.com/search?q={keyword}` |
| 最新 | `https://x.com/search?q={keyword}&f=live` |
| 用户 | `https://x.com/search?q={keyword}&f=user` |
| 媒体 | `https://x.com/search?q={keyword}&f=media` |
| 列表 | `https://x.com/search?q={keyword}&f=list` |

"Near You" 过滤：追加 `&lf=on`

### Cookie Warmup

1. Navigate `https://x.com`
2. 等待 5 秒
3. Navigate 到搜索 URL

### 多关键词

用 `%20` 连接

## Pitfalls

### pitfall: heavy_client_rendering

- **触发**：导航后立即提取
- **症状**：推文内容未加载
- **workaround**：等待 **5 秒以上**再 snapshot

### pitfall: private_likes_empty_timeline

- **触发**：查看私密账号的点赞/关注列表
- **症状**：返回空时间线，但不是错误
- **workaround**：识别为私密状态，不当作"无结果"

### pitfall: graphql_cursor_pagination

- **触发**：翻页获取更多推文
- **症状**：URL 不变，需 cursor 参数
- **workaround**：滚动加载（无限滚动模式），或从页面底部"显示更多"按钮获取 cursor

## Fallback

1. 搜索无结果 → 检查登录态
2. 仍不足 → Bing 搜 `site:x.com {keyword}`
