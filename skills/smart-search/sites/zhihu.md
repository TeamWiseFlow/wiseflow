# 知乎浏览器搜索

固定 session/profile `default`，每条 Camoufox 操作带 --persistent。登录和验证按 browser-guide 执行。

```
https://www.zhihu.com/search?type=content&q={keyword}
```

这是浏览器搜索页；关键词在 q 中编码一次。类型、排序、时间筛选优先用当前页面可见的控件，并复核实际结果，不默认保证旧 vertical、sort、time_interval 参数仍生效。需要人员等分类时用页面菜单确认生成的 URL。

[OpenCLI 当前搜索](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/zhihu/search.js) 使用 search_v3 API，每页 20 条、按服务端 paging.next 续读。**这些接口页码/offset 不是浏览器分页保证**，不要将 API 的 all/answer/article/question 类型值、limit 或 offset 直接套到网页 URL。浏览器按页面“下一页”或实际懒加载续看，仍遵守默认两次搜索导航预算。

提取真实标题、类型、作者、原文链接和可见赞同数；去掉广告/推荐位，HTML 实体按实际 Unicode 文本读取。回答链接形如 `https://www.zhihu.com/question/{question_id}/answer/{answer_id}`，文章为 `https://zhuanlan.zhihu.com/p/{article_id}`。保留完整 ID，打开对应原文后核实全文，不将被截断的搜索摘要当正文。

首页访问不能保证已登录。登录墙、验证码和看不到全文分别记录；可换关键词或用 Bing 搜 `site:zhihu.com {keyword}`，索引不代表完整结果。
