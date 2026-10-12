# 金融

> 来源参考 [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/xueqiu/search.js)。固定 session/profile `default`，带 --persistent。

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

上游股票 search 使用 stock/search.json，其结果不等于全站讨论。smart-search 使用浏览器搜索页，按当前页面区分股票、用户或讨论，不能把上游 JSON 端点当网页 URL。保留计数/价格的时间和币种，缺项不补零。

## Pitfalls

### pitfall: login_for_advanced_data

- **触发**：访问详细财务数据
- **症状**：部分数据需登录查看
- **workaround**：在共享 `default` profile 核对真实登录状态；访问首页不能替代登录，受限数据按 browser-guide 处理

## Fallback

1. 搜索无结果 → 检查登录态
2. 仍不足 → Bing 搜 `site:xueqiu.com {keyword}`
