# 新闻浏览器搜索

## Reuters

使用固定持久化 session/profile `default`。先打开 `https://www.reuters.com/`，从当前页面的搜索按钮或搜索框进入实际结果页，按真实 URL 与控件读取结果。旧 `/search/news?blob=` 不再作为固定可靠入口。

[OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/reuters/search.js) 和 [SearXNG](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/reuters.py) 当前都参考 articles-by-search-v2 读取方案；它是接口，不是可直接用于浏览器导航的搜索页。不要照抄接口 URL、Cookie fetch 或签名到 Camoufox eval。smart-search 仅操作页面；当前页面无可用搜索入口时，用 Bing 搜 `site:reuters.com {keyword}` 再打开原文。

登录、Datadome 防护或付费墙按 browser-guide 处理。首页初始化不等于解除验证，未访问的全文不能用搜索摘要补造。

## BBC

固定 session/profile `default`，带 --persistent：

```
https://www.bbc.co.uk/search?q={keyword}
```

等待结果区出现后提取标题、链接、摘要与日期。区域重定向以实际页面为准，复制原文链接，不保存 edgeauth 等短期访问票据为固定搜索规则。
