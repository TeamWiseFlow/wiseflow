---
name: rss-reader
description: 发现网站的 RSS/Atom feed URL，然后抓取并解析 feed 中的文章。
---

# rss-reader — 工具说明

> 本文是 `expert-osbi` 专家包内的工具说明书，不独立出现在技能列表中。由相关 Workflow 指引调用。

解析公开网站的 RSS/Atom 订阅。平台原始内容由 `douyin-hunter` / `xhs-hunter` / `tiktok-hunter` / `kuaishou-hunter` / `x-hunter` / `weibo-hunter` / `wx-mp-hunter` 获取；不要用本工具替代这些技能。发现网站的 RSS/Atom feed URL，抓取并解析 feed 中的文章。适合监控网站更新、批量采集同一信源的多篇文章（无需逐页访问）。

**输入**：feed URL（未知时先按下方「发现 feed URL」找到）；可选 `--limit` / `--skip`。
**输出**：markdown，分两段——全文文章（可直接处理，无需访问原文 URL）与摘要链接（需访问原文取全文）。

## 调用方式

通过 PATH 调用 wrapper，无需拼接脚本路径：

```bash
rss-reader <feed_url> [--limit N] [--skip url1,url2,...]
```

| Option | Description |
|--------|-------------|
| `--limit N` | Max entries to return (default: 20) |
| `--skip url1,url2,...` | Skip entries whose URLs are already processed (deduplication) |

输出两段的处理：

- **Full-content articles**（正文 >200 字符）：直接提取 title / author / date / content，**无需访问文章 URL**。
- **Summary-only links**（仅短摘要）：逐条访问 URL 获取全文（按 browser-guide 浏览原文）。

---

## 发现 feed URL

已有 RSS/Atom URL 时跳过本节。

**方法 A — 页面源码**：导航到网站 snapshot，找 `<head>` 里的 `<link rel="alternate">`：

```html
<link rel="alternate" type="application/rss+xml" href="/feed">
<link rel="alternate" type="application/atom+xml" href="/atom.xml">
```

**方法 B — 常见路径**（逐个试，直到返回 XML）：

```
/feed  /feed.xml  /rss  /rss.xml  /atom.xml  /index.xml
/?feed=rss2  /feeds/posts/default
```

**方法 C** — 找页面上的 RSS 图标 🟠 或 "RSS" / "Subscribe" / "Feed" 链接。

有效 feed URL 返回以 `<rss`、`<feed` 或 `<rdf:RDF` 开头的 XML。

---

## Edge cases

| Situation | Action |
|-----------|--------|
| Feed returns 404 | Try alternative paths from 「发现 feed URL」 |
| Feed requires login | Use browser-guide to read accessible pages; do not pass platform Cookie to this feed parser |
| Script error "Failed to parse feed" | Feed XML may be malformed; report the URL to the user |
| Empty feed | Report: "This RSS feed has no entries." |
