# Reddit

> 参数参考 [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/reddit/search.js)。固定 session/profile `default`，带 --persistent。

## 搜索

### URL

```
https://www.reddit.com/search/?q={keyword}
```

排序：`&sort=relevance` | `hot` | `top` | `new` | `comments`

时间过滤（页面实际支持时，以当前筛选状态为准）：`&t=hour` | `day` | `week` | `month` | `year` | `all`

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

## 结果与翻页

保留 subreddit、作者、帖子标题、permalink、页面时间与实际计数；跨帖、引用/转发和评论数量分别识别。向下滚动或下一页按实际页面继续，不能把接口 after 游标直接拼成未验证的网页页码。上游 /search.json 是 API 入口，本技能不通过 eval fetch 复制该路径。

## Fallback

1. 搜索无结果 → 换关键词或换 subreddit
2. 仍不足 → Bing 搜 `site:reddit.com {keyword}`
