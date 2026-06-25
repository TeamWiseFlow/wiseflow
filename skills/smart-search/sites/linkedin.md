# LinkedIn

> last_verified: 2026-06-15

## 搜索

### 职位搜索

```
https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}
```

### 人员搜索

```
https://www.linkedin.com/search/results/people/?keywords={keyword}
```

### 公司搜索

```
https://www.linkedin.com/search/results/companies/?keywords={keyword}
```

### Cookie Warmup

1. Navigate `https://www.linkedin.com`
2. 等待 5 秒
3. Navigate 到搜索 URL

### 多关键词

用 `%20` 连接

## Pitfalls

### pitfall: login_wall_strict

- **触发**：几乎所有 LinkedIn 内容需登录
- **症状**：未登录时显示登录墙或截断内容
- **workaround**：必须 Cookie Warmup + 已登录态

### pitfall: people_search_aggressive

- **触发**：人员搜索翻页过多
- **症状**：触发 LinkedIn 频率限制
- **workaround**：人员搜索建议不超过 3 页

## Fallback

1. 搜索无结果 → 检查登录态
2. 仍不足 → Bing 搜 `site:linkedin.com {keyword}`
