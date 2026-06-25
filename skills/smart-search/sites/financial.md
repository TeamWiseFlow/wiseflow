# 金融

> last_verified: 2026-06-15

## 雪球 (Xueqiu)

股票/代码搜索：
```
https://xueqiu.com/search?q={keyword}
```

股票详情页：`https://xueqiu.com/S/{symbol}`（如 `/S/SH600519`）

### Cookie Warmup

1. Navigate `https://xueqiu.com`
2. 等待 3 秒
3. Navigate 到搜索 URL

示例查询：`茅台`、`AAPL`、`腾讯`、`SH600519`

## Pitfalls

### pitfall: login_for_advanced_data

- **触发**：访问详细财务数据
- **症状**：部分数据需登录查看
- **workaround**：Cookie Warmup 后访问

## Fallback

1. 搜索无结果 → 检查登录态
2. 仍不足 → Bing 搜 `site:xueqiu.com {keyword}`
