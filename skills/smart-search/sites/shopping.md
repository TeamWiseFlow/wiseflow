# 购物

> last_verified: 2026-06-15

## Amazon

```
https://www.amazon.com/s?k={keyword}
```

部门过滤：`&i={department}`（`electronics`、`books`、`clothing-shoes-jewelry`、`grocery`、`toys-and-games`）

排序：
- 相关性（默认）：`&s=relevance-rank`
- 价格低→高：`&s=price-asc-rank`
- 价格高→低：`&s=price-desc-rank`
- 评价最高：`&s=review-rank`
- 最新上架：`&s=date-desc-rank`

多关键词用 `+` 连接

## Pitfalls

### pitfall: anti_bot_protection

- **触发**：导航后立即 snapshot
- **症状**：遇到机器人验证页面
- **workaround**：导航后等 2-3 秒再 snapshot；遇到验证页不要立即重试 → browser-guide
