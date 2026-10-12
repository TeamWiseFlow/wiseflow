# 技术社区浏览器搜索

使用固定 session/profile `default`，全部 Camoufox 命令带 --persistent。

## Hacker News

```
https://hn.algolia.com/?q={keyword}
```

[OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/hackernews/search.js) 和 [SearXNG](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/hackernews.py) 使用 Algolia 检索，浏览器入口保持 hn.algolia.com。按页面的 Stories/Comments、排序和时间控件筛选，并复核当前筛选状态；旧 dateRange 字符串不作为已确认的通用参数。

帖子标题与文章原文链接分别记录，HN 讨论页为 `https://news.ycombinator.com/item?id={id}`。评论不等于文章正文，也不代表独立用户数量。

## V2EX

本站首页 `https://www.v2ex.com/?q={keyword}` 不作为搜索入口。使用 Bing 的公开索引：

```
https://www.bing.com/search?q=site%3Av2ex.com%20{keyword}
```

找到主题后打开 `https://www.v2ex.com/t/{id}` 核实；索引可能不覆盖新主题和不可见内容。不要把首页正常返回当作关键词搜索已执行。

## 百度贴吧

[OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/tieba/search.js) 的浏览器搜索参数：

```
https://tieba.baidu.com/f/search/res?qw={keyword}&ie=utf-8&pn=1
```

pn 为页码，从 1 开始，不是乘以 10 的偏移量。吧内搜索可按页面“吧内”控件限定，只有当前页面实际采用 kw 时才沿用；结果量与后续页以真实页面为准。

先看列表中的主题标题、正文片段、吧名和链接，再按需要打开主题。已删除、不可见或验证页分别记录，不宣称只有第一页有效或翻完了全部结果。
