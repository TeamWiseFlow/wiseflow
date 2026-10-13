---
name: "generate-wenyan-theme"
description: "从自然语言描述或用户提供的排版样本生成自定义排版 CSS 主题，产出可直接给 wx-mp-publisher 使用的 wenyan 格式主题。"
description_zh: "从自然语言描述或用户提供的排版样本生成自定义排版 CSS 主题，产出可直接给 wx-mp-publisher 使用的 wenyan 格式主题。"
description_en: "generate-wenyan-theme: native Xiaobei workflows, tools and reusable resources."
version: "0.3.2"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# generate-wenyan-theme - 工具说明

> 本文是 `expert-wx-mp` 专家包内的工具说明书，不独立出现在技能列表中。由相关 Workflow 指引调用。

根据用户的自然语言需求，生成符合微信公众号排版规范的自定义 CSS 样式表，保存为本地文件。

本工具只管理排版主题，不参与内容 DNA 采样、组合或评分。主题资产统一保存在 `wx_mp/wenyan-theme/`，不写入 `wx_mp/dna/`。

---

## 核心能力

- **自然语言转 CSS**：理解视觉需求（如"赛博朋克风"、"深色代码块"、"带装饰的引用块"），转换为精确的 CSS 代码
- **样式参考生成**：分析用户提供的本地 HTML、封面或排版截图，生成 wenyan CSS；只有链接时请补充材料
- **多篇排版归纳**：读取用户提供的多篇 HTML 或截图，提炼真实出现的排版共性；不自动按账号采集
- **主题注册到 index.json**：生成自定义 CSS 后，把主题信息写入工作区 `wx_mp/wenyan-theme/index.json`，`wx-mp-publisher` 会从这里读自定义主题
- **微信排版规范适配**：严格遵循 `#wenyan` 命名空间约束，确保样式能完美注入微信公众号 DOM 结构
- **高级排版特效**：支持伪元素 (`::before`/`::after`)、渐变背景 (`linear-gradient`)、内联 SVG/Base64 图片等高级 CSS 特性

---

## 输入模式识别

1. 用户提供本地 HTML：运行本地整理入口，将内容保存为样本 JSON 后分析。
2. 用户提供多篇 HTML 或排版截图：逐篇分析，提炼共性；截图不能证明未显示的字号或 CSS 实现。
3. 用户只描述视觉需求：按自然语言模式生成。
4. 只有公众号名或文章链接：先请用户提供 HTML 或截图；链接只记出处。

## 用户 HTML 整理脚本

通过 xiaobei-runtime 调用逻辑命令 generate-wenyan-theme；脚本只读用户本地文件，不访问网络。

```bash
generate-wenyan-theme --input-html wx_mp/ref/article.html --output wx_mp/wenyan-theme/sources.json
generate-wenyan-theme --input-html wx_mp/ref/one.html --input-html wx_mp/ref/two.html --output wx_mp/wenyan-theme/sources.json
```

输入路径可为用户授权的绝对路径或工作空间相对路径；输出必须是工作空间内的相对 .json 路径。结果 articles[].content_html 为实际文件内容，source_file 标明出处。工具不支持 URL 或账号采集参数。用户仅提供截图时直接使用当前可用的视觉能力分析，不伪造 HTML。

## HTML 样式分析要点

从 `content_html` 中抽取共性时，只分析可迁移到 wenyan CSS 的视觉规律，不复制微信原文中不可控或依赖原始 DOM 的实现细节：

- 颜色：正文色、标题色、强调色、引用/代码/分割线背景色
- 字号与层级：h1/h2/h3、正文、注释、小字之间的相对比例
- 间距节奏：段落间距、标题上下留白、列表缩进、引用块 padding
- 装饰语言：标题前后缀、底纹、边框、圆角、分割线、卡片感
- 内容类型：是否频繁使用图片、引用、列表、代码、表格
- 共同约束：多篇账号样本中重复出现的风格才作为模板核心；单篇偶发元素只作为可选细节

---


### 1. 强制命名空间约束（最重要）

所有 CSS 选择器 **必须** 以 `#wenyan` 开头，中间用空格隔开。缺少 `#wenyan` 前缀的样式将失效。

- ✅ `#wenyan h1 { color: red; }`
- ❌ `h1 { color: red; }`

### 2. 字体与字号

- **font-family**：严禁主动设置，保持默认以适配微信公众号编辑器的系统字体
- **font-size**：建议 12px - 18px 范围，避免排版溢出或阅读困难

### 3. 支持的 CSS 选择器字典

| 目标元素 | CSS 选择器 | 常用定制属性 |
|---------|-----------|------------|
| 全局默认 | `#wenyan` | `background-image`, `line-height`, `color` |
| 各级标题 | `#wenyan h1` ~ `#wenyan h6` | `font-size`, `text-align`, `border-bottom`, `margin` |
| 标题文字 | `#wenyan h1 span` | `color`, `font-weight`, `background` |
| 标题装饰 | `#wenyan h1::before` | `content`, `display`, `width`, `height`, `background-image` |
| 段落文本 | `#wenyan p` | `text-indent`, `letter-spacing`, `color` |
| 引用块 | `#wenyan blockquote` | `border-left`, `background-color`, `padding` |
| 代码块外层 | `#wenyan pre` | `background-color`, `border-radius`, `padding`, `overflow-x: auto` |
| 代码块内容 | `#wenyan pre code` | `color` |
| 分割线 | `#wenyan hr` | `border`, `border-top-style`, `border-color` |
| 超链接 | `#wenyan a` | `color`, `text-decoration`, `border-bottom` |

### 4. 外部资源引用限制

- **禁止本地路径**：严禁 `url("./bg.png")` 等本地路径
- **合法引入方式**：
  - Data URI（推荐）：`url("data:image/svg+xml;utf8,<svg>...</svg>")`
  - HTTPS 地址：`url(https://example.com/bg.jpg)`
- **禁止 Web 字体**：不支持 `@font-face`，只能使用系统字体

### 5. 输出文件路径约束

**所有产物（用户样本 JSON + 生成的 CSS）统一放工作区下专用子目录 `wx_mp/wenyan-theme/`，不要散落工作区根。** 脚本会自动 `mkdir -p` 该子目录。

- 样本输出 JSON：工作区内相对 `.json` 路径，可含子目录（如 `wx_mp/wenyan-theme/sources.json`）；禁止绝对路径和 `..` 上跳。
- 生成的 CSS：写入同一 `wx_mp/wenyan-theme/` 子目录下的相对 `.css` 路径（如 `wx_mp/wenyan-theme/custom-theme.css`）；禁止绝对路径、`..` 上跳、隐藏目录和非 `.css` 后缀。

---

## 参考模板（default.css 结构）

```css
/* 全局属性 */
#wenyan {
    line-height: 1.75;
    font-size: 16px;
}

/* 标题与段落间距 */
#wenyan h1,
#wenyan h2,
#wenyan h3,
#wenyan h4,
#wenyan h5,
#wenyan h6,
#wenyan p {
    margin: 1em 0;
}

/* 一级标题 */
#wenyan h1 {
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    font-size: 1.5em;
}

/* 二级标题 */
#wenyan h2 {
    text-align: center;
    font-size: 1.2em;
    border-bottom: 1px solid #f7f7f7;
    font-weight: bold;
}

/* 列表 */
#wenyan > ul,
#wenyan > ol {
    padding-left: 1rem;
}

#wenyan ul,
#wenyan ol {
    margin-left: 1rem;
    font-size: 0.9rem;
}

/* 图片 */
#wenyan img {
    max-width: 100%;
    height: auto;
    margin: 0 auto;
    display: block;
}

/* 表格 */
#wenyan table {
    border-collapse: collapse;
    margin: 1.4em auto;
    max-width: 100%;
    table-layout: fixed;
    text-align: left;
    overflow: auto;
    display: table;
}

/* 引用块 */
#wenyan blockquote {
    background: #afb8c133;
    border-left: 0.5em solid #ccc;
    margin: 1.5em 0;
    padding: 0.5em 10px;
    font-style: italic;
    font-size: 0.9em;
}

/* 行内代码 */
#wenyan p code {
    color: #ff502c;
    padding: 4px 6px;
    font-size: 0.78em;
}

/* 代码块外围 */
#wenyan pre {
    border-radius: 5px;
    line-height: 2;
    margin: 1em 0.5em;
    padding: .5em;
    box-shadow: rgba(0, 0, 0, 0.55) 0px 1px 5px;
    font-size: 12px;
}

/* 代码块 */
#wenyan pre code {
    display: block;
    overflow-x: auto;
    margin: .5em;
    padding: 0;
}

/* 分割线 */
#wenyan hr {
    border: none;
    border-top: 1px solid #ddd;
    margin-top: 2em;
    margin-bottom: 2em;
}

/* 链接 */
#wenyan a {
    word-wrap: break-word;
    color: #0069c2;
}
```

---

## Agent 执行步骤

### A. 自然语言模式

1. **分析需求**：提取关键词（如：深色、科技风、可爱），确定主色调和风格方向
2. **生成 CSS**：严格按照命名空间约束和上述规范，生成完整的 CSS 代码
3. **保存文件**：将 CSS 写入 `wx_mp/wenyan-theme/` 子目录（如 `wx_mp/wenyan-theme/custom-theme.css`）
4. **注册主题**：按「生成主题注册规则」更新工作区 `wx_mp/wenyan-theme/index.json`
5. **后续引导**：提示使用 `wx-mp-publisher` 技能的第二个位置参数传入注册的 `theme-id` 发布

### B. 用户提供单篇样本

1. 读取用户提供的 HTML 或排版截图；只有链接时请补充材料。
2. HTML 运行 generate-wenyan-theme --input-html <本地文件> --output wx_mp/wenyan-theme/sources.json，读取真实样本 JSON。
3. 分析实际可见的标题、段落、引用、分割线、强调与图片布局；截图不支持的细节明确标注。
4. 按 #wenyan 命名空间把可迁移特征生成 CSS，不复制无效 class。
5. 按原主题规则保存、注册，再交 wx-mp-publisher 使用。

### C. 用户提供多篇样本

1. 核对用户提供的样本、账号标识和筛选要求；多个 HTML 以重复 --input-html 参数整理。
2. 逐篇阅读真实内容，列出实际参考的标题或文件路径；不宣称读取了未提供的账号文章。
3. 用户已指定样本并要求生成时直接执行；需要自行取舍样本或有风格冲突时，先展示拟采用的样本与取舍。
4. 优先抽取多篇共同的视觉规则，单篇偶发特征作可选细节。
5. 生成 CSS，保存并注册主题。

## 生成前确认要求

仅在需要用户选择样本或解决冲突时补问；说明样本数量、标题或文件名、筛选依据和主题方向。用户已明确提供样本与生成要求时沿用授权，不重复索取确认。

## 生成主题注册规则

每次成功生成自定义 CSS 后，必须更新工作区主题注册表：

```text
wx_mp/wenyan-theme/index.json
```

结构固定为：

```json
{
  "version": 1,
  "themes": [
    {
      "id": "<theme-id>",
      "name": "<主题名称>",
      "css": "wx_mp/wenyan-theme/<theme-id>.css",
      "source": "<natural-language | url | account>",
      "createdAt": "<ISO-8601 时间>"
    }
  ]
}
```

**登记表是 client 侧 id → 本地 CSS 路径映射，relay 不存主题。** CSS 内容随发布请求上传（`custom_theme` 字段）。

注册要求：

- `theme-id` 使用 CSS 文件名去掉 `.css` 后缀，例如 `wx_mp/wenyan-theme/custom-theme.css` → `custom-theme`。
- CSS 文件路径写相对路径（含 `wx_mp/wenyan-theme/` 子目录），优先使用当前 crew workspace 内路径。
- 如果同名 `theme-id` 已存在，更新原记录，不重复追加。
- 保留可追溯字段：`name`、`source`、`createdAt`；更新主题时刷新 `createdAt`。
- 不要修改内置主题 ID 的含义。

注册后，`wx-mp-publisher` 发布时通过第二个位置参数引用自定义主题：

```bash
wx-mp-publisher article.md custom-theme
```

临时未登记的 CSS 文件也可直接传路径：

```bash
wx-mp-publisher article.md wx_mp/wenyan-theme/custom-theme.css
```

---

## 与 wx-mp-publisher 配合使用

生成 CSS 文件后，用 `wx-mp-publisher` 发布，第二个位置参数优先传登记的 `theme-id`：

```bash
wx-mp-publisher article.md custom-theme
```

> 注：发布统一走 `publish_wx_mp.py`，当 theme 参数指向本地 `.css` 文件路径、或为 `wx_mp/wenyan-theme/index.json` 登记的自定义 id 时，脚本读出 CSS 内容作 `custom_theme` 字段随 multipart 上传 relay；relay 侧请求结束即清理，不持久化、不落盘、不按用户存主题。
