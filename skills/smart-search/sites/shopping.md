# 购物

> 搜索入口参考 [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/amazon/search.js)。固定 session/profile `default`，带 --persistent。

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

商品价格、库存、配送与评价数以本次页面实际显示为准，记录币种、地区和采集时间；广告位单独标记，不把推荐区或变体重复列成独立结果。搜索不包含购物车、下单或登录购买操作。

## Pitfalls

### pitfall: anti_bot_protection

- **触发**：导航后立即 snapshot
- **症状**：遇到机器人验证页面
- **workaround**：导航后等 2-3 秒再 snapshot；遇到验证页不要立即重试 → browser-guide
