# Reddit

> last_verified: 2026-06-15

## 搜索

### URL

```
https://www.reddit.com/search/?q={keyword}
```

排序：`&sort=relevance` | `hot` | `top` | `new` | `comments`

时间过滤（sort=top 时）：`&t=hour` | `day` | `week` | `month` | `year` | `all`

### 子版块内搜索

```
https://www.reddit.com/r/{subreddit}/search/?q={keyword}&restrict_sr=on&sort=relevance&t=all
```

### Cookie Warmup

1. Navigate `https://www.reddit.com`
2. 等待 3 秒
3. Navigate 到搜索 URL

### 多关键词

用 `+` 连接

## Pitfalls

### pitfall: login_wall_for_subscribed

- **触发**：访问订阅列表等需登录的内容
- **症状**：返回登录墙
- **workaround**：Cookie Warmup 后访问，或 browser-guide 处理登录

## Fallback

1. 搜索无结果 → 换关键词或换 subreddit
2. 仍不足 → Bing 搜 `site:reddit.com {keyword}`
