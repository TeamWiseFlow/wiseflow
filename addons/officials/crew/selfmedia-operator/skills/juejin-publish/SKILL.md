---
name: juejin-publish
description: 发布文章到掘金平台。使用浏览器自动化完成发布流程，包括在线编辑器输入内容、选择分类、添加标签、上传封面图、发布。当用户要求发布内容到掘金时触发。
---

# 掘金文章发布

- **必须使用在线编辑器（bytemd + CodeMirror 5）**。
- **始终**先进掘金首页再进编辑器，不直接跳 `drafts/new`。
- 掘金编辑器使用 localStorage / SPA 路由记住上次打开的 draft。发布后直接 navigate 到 `drafts/new` 会被重定向回上一个草稿 URL（`drafts/xxxxxxx`），导致第二篇内容注入到错误位置。

## 通用约束

- 🔴 **正文配图手动上传**：掘金编辑器不会从本地路径 `![...](img1.jpg)` 加载图片。注入正文后，需检查 article.md 中的图片标记位置，在对应位置通过编辑器的「图片」按钮逐一上传 `output_articles/<name>/` 中的配图文件到正文中。
- 文件上传前必须先将文件复制到 `/tmp/openclaw/uploads/`（browser 工具沙箱限制）
- `browser upload` 工具可能返回「超时错误」，但这**不代表上传失败**！上传后用 snapshot 检查页面状态
- **不要通过检查 `input.files.length` 是否为 0 判定上传是否失败！**
- 遇到 `browser failed: timed out` 错误时，**不需要重启浏览器**！等待 30 秒后在原页面继续操作
- **标题**用 `type` + `slowly: true`；**正文**根据 CM 状态选 setValue 或 textarea dispatch
- 发布对话框中操作优先用 `evaluate` 直接操作 DOM

## Workflow（在线编辑器方式）

### Step 1: 准备文件

```
cp <cover_image> /tmp/openclaw/uploads/cover.jpg

# 同时生成 JS 转义后的正文（用于 evaluate 注入）
python3 /tmp/escape_md.py <article.md路径>
```

正文转义脚本（保存为 `/tmp/escape_md.py`）：
```python
#!/usr/bin/env python3
import sys
def escape_for_js(text):
    lines = text.split('\n')
    if lines[0].strip() == '---':
        end_idx = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
        if end_idx is not None: lines = lines[end_idx+1:]
    text = '\n'.join(lines).strip()
    text = text.replace('\\', '\\\\').replace('"', '\\"')
    text = text.replace('\n', '\\n').replace('\r', '')
    return text

for path in sys.argv[1:]:
    with open(path) as f: content = f.read()
    escaped = escape_for_js(content)
    with open(path + '.escaped.txt', 'w') as f: f.write(escaped)
    print(f'Escaped: {path} -> {path}.escaped.txt ({len(escaped)} chars)')
```

### Step 2: 断开旧草稿 → 打开编辑器

> 🔴 **核心原则**：每次发布都走这个路径，无论第几篇。

```
① Navigate to https://juejin.cn/
② 等待 2 秒
③ Navigate to https://juejin.cn/editor/drafts/new
④ evaluate 验证：
   browser evaluate fn="window.location.href.includes('drafts/new')"
   返回 false → 回到 ①
```

### Step 3: 输入标题

```
Snapshot 获取页面元素
找到标题输入框（通常是第一个 textbox，placeholder="输入文章标题..."）
使用 act + type + slowly:true 输入标题
```

### Step 4: 等待 CodeMirror 初始化（最多重试 5 次）

```
evaluate fn="!!(document.querySelector('.CodeMirror') && document.querySelector('.CodeMirror').CodeMirror)"

返回 true → 进入 Step 5A（优先路径）
返回 false → 等待 2 秒重试，最多 5 次
5 次后仍 false → 进入 Step 5B（兜底路径）
```

### Step 5A: 注入正文 — 优先路径（CM.setValue）

```js
browser evaluate fn="document.querySelector('.CodeMirror').CodeMirror.setValue(\"<escaped_markdown>\")"
```

成功标志：字符数 > 0、预览渲染、摘要自动填充、右上角"保存成功"。

### Step 5B: 注入正文 — 兜底路径（textarea dispatch）

```js
browser evaluate fn="(() => { const ta = document.querySelector('.CodeMirror textarea'); ta.value = '<escaped_markdown>'; ta.dispatchEvent(new Event('input', { bubbles: true })); return 'ok'; })()"
```

> ⚠️ 兜底路径的代价：摘要不会自动填充，需在 Step 7 手动填写。

### Step 6: 等待自动保存

```
等待 2~3 秒，确认右上角出现"保存成功"，URL 从 drafts/new 变为 drafts/xxxxxxx
```

### Step 7: 点击发布 → 填写发布信息

点击「发布」按钮后，在弹出对话框中：

```
1. 选择分类（必填 *）：
   evaluate 找到文字为「人工智能」的元素并 click
   或根据文章内容选择合适分类

2. 添加标签（必填 *）：
   a. 用 evaluate click 标签搜索框（.byte-select__input）
   b. 输入关键词（如 "AI"），等待下拉出现
   c. evaluate 从 .byte-select-option 列表中 click 目标标签

3. 上传封面图：
   a. evaluate click 「上传封面」按钮
   b. browser upload /tmp/openclaw/uploads/cover.jpg
   c. 忽略可能的超时提示

4. 填写摘要（必填 *，仅兜底路径需要手动填）：
   evaluate 找到摘要 textarea 并 fill
   摘要内容取文章前 100 字左右的核心描述
```

### Step 8: 确认发布

```
evaluate 找到「确定并发布」按钮并 click
等待 3~5 秒，检查 URL：
  → 跳转到 /published → 发布成功，获取文章 URL
  → 仍在 draft 页面 → snapshot 检查是否有错误提示
```

## 发布选项参考

See `references/publish-options.md` for category list, tag suggestions, and cover image specs.

## 常见问题处理

| 问题 | 处理方式 |
|------|---------|
| 元素引用失效（Element not found） | 重新 snapshot 获取最新元素引用；发布对话框中操作改用 evaluate |
| `.CodeMirror.CodeMirror` 为 undefined | 最多重试 5 次；仍不可用则走 textarea dispatch 兜底路径 |
| 正文注入后字符数为 0 | 重新注入；检查是否命中了正确的 textarea |
| 兜底路径摘要未自动填充 | 手动 evaluate 填写摘要 textarea（必填字段） |
| 分类/标签下拉无响应 | 用 evaluate 直接操作 DOM 代替 snapshot+click |
| 发布后无跳转/URL | 等待 30s；若无响应，截图检查是否有违禁词提示 |
| 标签添加失败 | evaluate 从 .byte-select-option 列表直接 click 目标标签 |
| 第二篇 navigated 到旧草稿 URL | 回到首页 → 等 2 秒 → 重新进 drafts/new → 验证 URL |

## 错误示范

```
❌ 直接 navigate 到 drafts/new（不先进首页）：
→ SPA 可能重定向到旧草稿 URL，第二篇失败

❌ 用 textarea.value= 但不 dispatchEvent：
→ CM 不认，字符数为 0

❌ 用 fill() / Clipboard + Ctrl+V：
→ 无效

❌ 用 type 逐字输入正文：
→ 依赖 ref 动态变化，容易失败；已废弃

❌ 兜底路径忘记填摘要（*必填）：
→ 发布按钮无响应，因为摘要为空
```
