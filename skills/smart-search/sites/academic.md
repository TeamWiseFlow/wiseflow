# 学术与百科

> last_verified: 2026-06-15

## arXiv（预印本）

### 浏览器搜索

```
https://arxiv.org/search/?searchtype=all&query={keyword}
```

按字段搜索：
- 标题：`?searchtype=ti&query={keyword}`
- 作者：`?searchtype=au&query={keyword}`
- 摘要：`?searchtype=abs&query={keyword}`

按最新排序：追加 `&order=-announced_date_first`

### API（结构化 XML）

```
https://export.arxiv.org/api/query?search_query=all:{keyword}&max_results=10
```

分页：`&start={offset}`

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

无特殊 pitfalls。学术平台均为公开访问，不需要 Cookie Warmup。
