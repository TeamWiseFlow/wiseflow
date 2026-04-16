---
name: wenyan-publisher
description: Render Markdown to platform-optimized HTML and publish to Zhihu, Toutiao/Juejin, or Medium via browser automation. Uses browser-guide skill for the publishing step.
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["node"] },
      },
  }
---

# Wenyan Publisher — 多平台发布

将 Markdown 渲染为目标平台格式，再通过浏览器自动化完成发布。

**支持平台**: `zhihu`（知乎）| `toutiao`（今日头条，含 juejin 掘金）| `medium`


---

## Step 1：Render Markdown → 平台 HTML

> **重要**：必须使用绝对路径调用 node，**禁止** `cd {baseDir} && node scripts/render.mjs` 这种模式（`cd` 不在权限白名单中会报 exec denied）。

```bash
node {baseDir}/scripts/render.mjs -f article.md --platform <platform> -o /tmp/output.html
```

| 平台 | 命令示例 |
|------|---------|
| 知乎 | `node {baseDir}/scripts/render.mjs -f article.md --platform zhihu -o /tmp/zhihu.html` |
| 今日头条 / 掘金 | `node {baseDir}/scripts/render.mjs -f article.md --platform toutiao -o /tmp/toutiao.html` |
| Medium | `node {baseDir}/scripts/render.mjs -f article.md --platform medium -o /tmp/medium.html` |

---

## Step 2：通过 browser-guide 发布

使用 **browser-guide** skill 打开目标平台编辑器，将 Step 1 输出的 HTML 粘贴后发布：

| 平台 | 编辑器入口 | 操作要点 |
|------|-----------|---------|
| `zhihu` | `zhihu.com/p/new` | 切换到富文本模式，粘贴 HTML |
| `toutiao` | `mp.toutiao.com` | 选择图文发布，粘贴 HTML |
| `juejin` | `juejin.cn/editor/drafts/new` | 切换富文本模式，粘贴 HTML（与 toutiao 用同一渲染结果）|
| `medium` | `medium.com/new-story` | 切换 HTML 模式，粘贴内容 |

---

## Render 参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `-f, --file <path>` | 必填 | Markdown 文件路径 |
| `--platform <name>` | `wechat` | `zhihu` \| `toutiao`（juejin 同此）\| `medium` |
| `-t, --theme <id>` | `default` | 排版主题 ID |
| `-h, --highlight <id>` | `solarized-light` | 代码高亮主题 |
| `-c, --custom-theme <path>` | — | 自定义主题 CSS |
| `--no-mac-style` | — | 禁用代码块 Mac 风格 |
| `--no-footnote` | — | 禁用链接转脚注 |
| `-o, --output <path>` | stdout | 输出到文件（推荐指定，便于浏览器读取） |

---

## 平台差异说明

| 平台 | 特殊处理 |
|------|---------|
| `zhihu` | MathJax 公式 → `<img data-eeimg="true" alt="formula">` |
| `toutiao` / `juejin` | MathJax SVG → inline data:image/svg+xml（掘金与今日头条共用此处理逻辑）|
| `medium` | 引用/代码块/表格/数学公式标准化为纯文本 |

> 文章不含数学公式时，三个平台输出的 HTML 差异很小。

---

## Error Handling

| 错误 | 处理方式 |
|------|---------|
| `Cannot find module '@wenyan-md/core'` | 在 `{baseDir}` 运行 `npm install` |
| `--file (-f) is required` | 提供 Markdown 文件路径 |
| `unsupported platform` | 使用 `zhihu`、`toutiao`、`medium` 之一（juejin 请用 `toutiao`）|
