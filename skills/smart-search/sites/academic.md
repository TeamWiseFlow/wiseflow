# 学术与百科

> 网页字段参考 [arXiv 搜索页](https://arxiv.org/search/)；其他入口参考 [OpenCLI 万方](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/wanfang/search.js)。浏览器操作使用固定 profile `default`，带 --persistent。

## arXiv（预印本）

### 浏览器搜索

```
https://arxiv.org/search/?searchtype=all&query={keyword}
```

按字段搜索：
- 标题：`?searchtype=title&query={keyword}`
- 作者：`?searchtype=author&query={keyword}`
- 摘要：`?searchtype=abstract&query={keyword}`

按最新排序：追加 `&order=-announced_date_first`

网页分页可使用页面下一页链接；arXiv 网页 start 是条目偏移量，size 和 start 以当前结果页的实际链接为准。不要把 API 的 ti/au/abs、search_query 或 Atom/XML 端点用于本浏览器搜索流程。最新排序指初次公告日期，不能据此断言是论文最后更新日期。

## 百度学术

```
https://xueshu.baidu.com/s?wd={keyword}
```

多关键词用 `+` 连接。不需要 Warmup。

## 万方数据

```
https://s.wanfangdata.com.cn/paper?q={keyword}
```

中文学术论文、学位论文、会议论文。不需要 Warmup。

## Wikipedia

英文：
```
https://en.wikipedia.org/w/index.php?search={keyword}
```

中文：
```
https://zh.wikipedia.org/w/index.php?search={keyword}
```

其他语言：替换语言代码前缀（`de`、`fr`、`ja`、`ko`、`es`）。

## Pitfalls

arXiv/Wikipedia 公开搜索通常不需登录；万方等数据库的全文可能付费或不可得。只交付实际看到的摘要/全文，访问限制按 browser-guide 处理。
