---
name: wenyan-formatter
description: Format Markdown drafts into styled HTML for preview, or publish directly to WeChat Official Account (GZH) draft box. Supports multiple visual themes with smart topic-based theme selection.
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "requires": { "bins": ["node", "npx"] },
        "optionalEnv": ["WECHAT_APP_ID", "WECHAT_APP_SECRET"],
      },
  }
---

# Wenyan Formatter

将 Markdown 草稿渲染为微信公众号风格的 HTML，或一键推送到公众号草稿箱。

## Run

### 预览（render）

```bash
# 渲染本地 Markdown 文件
bash {baseDir}/scripts/format.sh --file ./draft.md

# 渲染内联 Markdown，指定主题
bash {baseDir}/scripts/format.sh --content "## 标题\n\n正文内容..." --theme grace

# 指定代码高亮主题
bash {baseDir}/scripts/format.sh --file ./draft.md --theme tech --highlight github-dark

# 自定义 CSS 主题
bash {baseDir}/scripts/format.sh --file ./draft.md --custom-theme ./my-theme.css
```

### 发布到公众号草稿箱（publish）

> 需要预先设置 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`。

```bash
# 本机 IP 已在公众号 IP 白名单时，直接发布
bash {baseDir}/scripts/format.sh --action publish --file ./draft.md --theme grace

# 通过 Wenyan Server 绕过 IP 白名单限制（推荐）
bash {baseDir}/scripts/format.sh \
  --action publish \
  --file ./draft.md \
  --theme grace \
  --server https://your-wenyan-server.example.com \
  --api-key YOUR_SERVER_KEY
```

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--action` | `render` | `render`（仅输出 HTML）或 `publish`（推送草稿） |
| `--file` | — | 本地 Markdown 文件路径（与 `--content` 二选一） |
| `--content` | — | 直接传入 Markdown 字符串 |
| `--theme` | `default` | 视觉主题 ID（见下方主题列表） |
| `--highlight` | `solarized-light` | 代码块高亮主题 |
| `--custom-theme` | — | 自定义 CSS 文件路径 |
| `--no-mac-style` | — | 关闭 Mac 风格代码块头部 |
| `--no-footnote` | — | 禁用链接转脚注 |
| `--out-dir` | `./tmp/wenyan-<ts>` | 渲染输出���录（仅 render 模式） |
| `--server` | — | Wenyan Server URL（publish 模式，绕过 IP 白名单） |
| `--api-key` | — | Wenyan Server API Key（配合 `--server` 使用） |

## Output

**render 模式**

- `<out-dir>/output.html` — 可在浏览器预览的完整 HTML 页面
- `<out-dir>/source.md` — 原始 Markdown 备份

**publish 模式**

- 控制台打印推送结果（草稿 media_id 或错误信息）

## Theme List & 智能主题匹配

> Agent 应根据文章内容自动选择最贴切的主题，避免每次都使用默认主题。

| 主题 ID | 视觉风格 | 适用内容场景 |
|---------|---------|------------|
| `default` | 简洁黑白，标准微信排版 | 通知、简讯、时效性资讯 |
| `grace` | 优雅衬线，米白底色 | 深度长文、读书笔记、文化艺术 |
| `tech` | 深色背景，等宽字体强调 | 技术教程、代码分析、产品评测 |
| `fresh` | 清新绿色调，轻量感 | 健康生活、美食、户外、轻量资讯 |
| `warm` | 暖橙/土黄，温暖感 | 情感、故事、节日、生活感悟 |
| `elegant` | 极简留白，高对比标题 | 品牌内容、商务、高端产品推介 |
| `cute` | 粉色圆角，活泼插画感 | 亲子、宠物、娱乐、年轻用户 |

### 智能主题匹配决策树

```
内容含大量代码 / 技术术语？
  └─ 是 → tech

主要受众是年轻女性 / 亲子 / 萌宠？
  └─ 是 → cute

情感/故事/节日/生活类内容？
  └─ 是 → warm

健康 / 美食 / 户外 / 轻量生活？
  └─ 是 → fresh

品牌推广 / 商务 / 精品内容？
  └─ 是 → elegant

深度长文 / 文化 / 书评？
  └─ 是 → grace

以上均不符合（资讯/通知/简讯）
  └─ → default
```

> 用户明确指定主题时，遵从用户选择；不确定时按决策树匹配，并在消息中告知已选主题及原因。

## Environment Variables

| 变量 | 说明 |
|------|------|
| `WECHAT_APP_ID` | 微信公众号 AppID（publish 模式必填） |
| `WECHAT_APP_SECRET` | 微信公众号 AppSecret（publish 模式必填） |

## Notes

- 第一次运行 `npx @wenyan-md/cli` 时会自动下载包，耗时约 10–30 秒，之后有缓存
- **publish 模式**默认要求本机 IP 在公众号后台 IP 白名单中；生产环境建议配置 Wenyan Server 绕过限制
- Markdown 文件应包含 YAML frontmatter（至少含 `title:` 字段），否则 publish 时可能被微信 API 拒绝
- 渲染 HTML 仅供预览，最终排版以公众号后台实际效果为准
