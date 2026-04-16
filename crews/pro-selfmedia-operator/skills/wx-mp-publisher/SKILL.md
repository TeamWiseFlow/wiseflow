---
name: wx-mp-publisher
description: Render and publish Markdown articles to WeChat Official Account (公众号) draft box. Supports local mode (IP whitelisted) and server relay mode via Wenyan Server.
metadata:
  {
    "openclaw":
      {
        "emoji": "📤",
        "requires": { "bins": ["node", "npx"] },
        "optionalEnv": ["WECHAT_APP_ID", "WECHAT_APP_SECRET"],
      },
  }
---

# WeChat MP Publisher

将 Markdown 稿件排版并推送到微信公众号草稿箱。

---

## Frontmatter 要求

文章 Markdown 开头必须包含 YAML 块，否则微信 API 会拒绝：

```yaml
---
title: 文章标题
cover: ./cover.jpg       # 可选，缺省自动取正文第一张图
author: 作者名称          # 可选
source_url: https://...  # 可选，原文链接
---
```

---

## 本地直发（IP 已在白名单）

```bash
# 基础发布
npx --yes @wenyan-md/cli publish -f article.md

# 指定主题和高亮
npx --yes @wenyan-md/cli publish -f article.md -t grace -h solarized-light
```

> 若收到 `invalid ip` 错误，说明本机出口 IP 未在公众号后台白名单，改用 Server 中转模式。

---

## Server 中转模式（若本地没有公网 IP，需要使用此模式）

```bash
npx --yes @wenyan-md/cli publish \
  -f article.md \
  -t grace \
  --server https://your-wenyan-server.example.com \
  --api-key YOUR_SERVER_KEY
```

---

## 参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `-f, --file <path>` | 必填 | Markdown 文件路径 |
| `-t, --theme <id>` | `default` | 视觉主题 ID（见下方列表） |
| `-h, --highlight <id>` | `solarized-light` | 代码高亮主题 |
| `--no-mac-style` | — | 禁用代码块 Mac 风格 |
| `--no-footnote` | — | 禁用链接转脚注 |
| `--server <url>` | — | Wenyan Server URL |
| `--api-key <key>` | — | Wenyan Server API Key |

---

## 主题列表与智能选择

| 主题 ID | 适用场景 |
|---------|---------|
| `default` | 资讯、通知、简讯 |
| `grace` | 深度长文、书评、文化艺术 |
| `tech` | 技术教程、代码分析 |
| `fresh` | 健康生活、美食、户外 |
| `warm` | 情感、故事、节日 |
| `elegant` | 品牌、商务、精品内容 |
| `cute` | 亲子、宠物、娱乐 |

**智能选择决策树**（用户未指定主题时按此匹配）：

```
含大量代码/技术术语 → tech
年轻女性/亲子/萌宠  → cute
情感/故事/节日      → warm
健康/美食/户外      → fresh
品牌/商务/精品      → elegant
深度长文/文化/书评  → grace
其他（资讯/通知）   → default
```

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `WECHAT_APP_ID` | 微信公众号 AppID（必填） |
| `WECHAT_APP_SECRET` | 微信公众号 AppSecret（必填） |

---

## Error Handling

| 错误 | 处理方式 |
|------|---------|
| `invalid ip` | 将本机出口 IP 加入公众号后台 IP 白名单，或改用 `--server` 中转 |
| `invalid appid` | 检查 `WECHAT_APP_ID` 环境变量是否正确 |
| 图片上传失败 | 确认 Markdown 中图片路径在当前工作目录中真实存在 |
| 样式冲突/排版错乱 | 加 `--no-mac-style` 重试 |
| `缺少 title` | 在 Markdown 开头添加 frontmatter `title:` 字段 |

---

## Notes

- 第一次运行 `npx @wenyan-md/cli` 会自动下载包，约 10–30 秒，之后有缓存
- publish 成功后会输出草稿 `media_id`，可在公众号后台找到对应草稿
- 本 skill 只负责推送草稿，正式发布仍需在公众号后台手动操作
