---
name: "wx-mp-hunter"
description: "根据微信公众号文章链接，通过 HTTP 获取全文、正文图片与封面，供账号诊断、DNA 提取与内容创作使用。"
description_zh: "根据微信公众号文章链接，通过 HTTP 获取全文、正文图片与封面，供账号诊断、DNA 提取与内容创作使用。"
description_en: "wx-mp-hunter: native Xiaobei workflows, tools and reusable resources."
version: "0.3.1"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# 微信公众号文章获取

用户提供 mp.weixin.qq.com 文章链接时，用本技能获取正文、图片和封面；不读取本机客户端或账号后台。

以用户提供的文章链接为输入，批量先验证一篇，成功后再处理其他链接。返回失败时保留实际错误，不把风控、删除或缺少正文当作成功。

## fetch — 获取文章全文

```bash
wx-mp-hunter fetch <url> [--html] [--download-images] [--download-cover] [--output-dir <dir>]
```

| Option | Description |
|--------|-------------|
| `url` | 文章链接（`mp.weixin.qq.com`，长链或短链均可） |
| `--html` | 同时返回正文原始 HTML |
| `--download-images` | 把正文图片下载到本地，`content_markdown` 中的图片 URL 替换为本地相对路径 |
| `--download-cover` | 下载文章分享封面到 `<output-dir>/covers/<hash>.<ext>`，输出 `cover_url` 与 `cover_local_path` |
| `--output-dir <dir>` | 图片下载目标目录（配合 `--download-images`；默认当前目录） |

输出示例：
```json
{
  "ok": true,
  "url": "https://mp.weixin.qq.com/s/xxxxx",
  "title": "文章标题",
  "author": "公众号名称",
  "publish_time": "2024-03-10",
  "content_text": "正文纯文本内容...",
  "content_markdown": "段落文字……\n\n![](https://mmbiz.qpic.cn/mmbiz_jpg/xxxxx/0?wx_fmt=jpeg)\n\n继续文字……**加粗**……",
  "images": [
    "https://mmbiz.qpic.cn/mmbiz_jpg/xxxxx/0?wx_fmt=jpeg",
    "https://mmbiz.qpic.cn/mmbiz_png/xxxxx/0?wx_fmt=png"
  ],
  "cover_url": "https://mmbiz.qpic.cn/mmbiz_jpg/xxxxx/0?wx_fmt=jpeg",
  "cover_local_path": ""
}
```

| 字段 | 说明 |
|------|------|
| `content_text` | 纯文本正文（去除所有 HTML 标签） |
| `content_markdown` | Markdown 格式正文，图片以内联 `![](url)` 放在原文位置，保留加粗/斜体/链接；`--download-images` 时 URL 替换为 `images/<hash>.<ext>` 本地相对路径 |
| `images` | 正文所有图片 CDN 链接（从 `data-src` 解析） |
| `cover_url` | 文章分享封面 URL，优先来自 `og:image`，兜底 `twitter:image` / `msg_cdn_url` |
| `cover_local_path` | 仅使用 `--download-cover` 且下载成功时存在，指向本地封面文件 |

`fetch` 优先读取分享卡片的 `og:title`；对应字段为空时才回退到页面中的 `h1`。`publish_time` 依次从页面日期、JS 时间戳、`og:article:published_time` / `article:published_time` 和正文日期提取；页面未提供时可能为空。

### 图片本地化

加 `--download-images --output-dir <dir>` 后，脚本并发下载（默认 4 并发、单图 ≤5MB、总量 ≤100MB）到 `<dir>/images/<hash>.<ext>`，并把 `content_markdown` 里的图片 URL 替换为本地相对路径，便于离线阅读 / 二次加工 / 转存。

```
wx-mp-hunter fetch <url> --html --download-images --output-dir ./article-out
```

### 封面下载

加 `--download-cover --output-dir <dir>` 后，脚本下载分享封面到 `<dir>/covers/<hash>.<ext>`，并在 JSON 中输出 `cover_url`、`cover_local_path`、`cover_download_ok`。该路径可传给 `wechat-style-profiler report --cover-image` 做视觉 DNA 分析。

```
wx-mp-hunter fetch <url> --download-cover --output-dir ./article-out
```

---
