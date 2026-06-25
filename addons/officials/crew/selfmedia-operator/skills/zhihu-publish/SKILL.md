---
name: zhihu-publish
description: 通过浏览器自动化在知乎发布文章或回答。知乎无可用公开 API，需通过浏览器操作完成发布。
metadata:
  openclaw:
    emoji: 📝
---

# 知乎发布

通过浏览器工具在知乎上发布文章或回答。知乎没有对个人开发者开放的发布 API，只能通过浏览器自动化。

**前提条件**：浏览器已登录知乎（Cookie Warmup 或 QR 登录）。

---

## 发布文章

### 流程

1. **Cookie Warmup**：Navigate `https://www.zhihu.com`，等待 3 秒
2. **进入创作页**：Navigate `https://www.zhihu.com/column/c_000000000/edit` 或点击右上角"写文章"
   - 直接 URL：`https://zhuanlan.zhihu.com/write`
3. **等待编辑器加载**：3-5 秒，确认 `.WriteIndex-page` 或 `.PostEditor` 出现
4. **填写标题**：
   - 找到标题输入框：`input[placeholder*="标题"]` 或 `.WriteIndex-titleInput input`
   - 用 `browser act kind=type` + `slowly: true` 输入标题
5. **填写正文**：
   - 知乎使用富文本编辑器（ProseMirror / Draft.js）
   - 点击正文区域：`.ProseMirror` 或 `.public-DraftEditor-root`
   - 用 `browser act kind=type` + `slowly: true` 输入内容
   - **Markdown 内容**需先转换为纯文本或手动分段输入（知乎编辑器不支持直接输入 Markdown）
6. **添加话题**（可选）：
   - 点击"添加话题"按钮
   - 输入话题名称，从下拉列表选择
7. **发布**：
   - 点击"发布"按钮
   - 等待 3 秒确认发布成功（URL 变为文章详情页）

### 标题限制

- 最长 100 字符

### 正文格式

知乎编辑器支持：
- 标题（H1/H2）
- 粗体 / 斜体
- 链接
- 图片（需先上传）
- 代码块
- 引用
- 有序/无序列表

**不支持直接输入 Markdown**，需通过编辑器工具栏或快捷键操作。

---

## 发布回答

### 流程

1. **Cookie Warmup**：Navigate `https://www.zhihu.com`
2. **导航到问题页**：Navigate `https://www.zhihu.com/question/{question_id}`
3. **等待页面加载**：3-5 秒
4. **点击"写回答"**：
   - 找到"写回答"按钮：`button.Button--blue` 或文本为"写回答"的按钮
   - 点击后等待编辑器出现
5. **填写回答内容**：
   - 同文章正文填写方式
6. **发布回答**：
   - 点击"发布"按钮
   - 等待 3 秒确认

---

## Pitfalls

### pitfall: editor_not_prosemirror

- **触发**：知乎编辑器 DOM 结构变更
- **症状**：`.ProseMirror` 选择器找不到编辑器
- **workaround**：fallback 到 `.public-DraftEditor-root` 或 `[contenteditable="true"]`

### pitfall: markdown_not_supported

- **触发**：直接粘贴 Markdown 文本到编辑器
- **症状**：Markdown 标记原样显示，不被渲染
- **workaround**：用编辑器工具栏格式化，或分段输入（先输入纯文本，再用快捷键加粗/设标题等）

### pitfall: image_upload_timeout

- **触发**：上传大图片
- **症状**：上传进度卡住
- **workaround**：图片压缩到 2MB 以内再上传；超时后重试一次
- **Patchright 1.60+ 替代**：`locator.drop()` 可拖拽图片到编辑器区域，绕过 file input 超时问题

### pitfall: anti_spam_check

- **触发**：短时间内发布多篇内容
- **症状**：出现验证码或"操作过于频繁"提示
- **workaround**：每次发布间隔 60 秒以上

### pitfall: numeric_html_entities

- **触发**：从知乎复制内容时
- **症状**：文本含 `&#x4F60;` 等编码
- **workaround**：解码 HTML 实体后再使用

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 未登录 / 登录墙 | browser-guide QR 登录后重试 |
| 编辑器未加载 | 等待 5 秒后重试，检查选择器 |
| 发布按钮灰色 | 检查标题/正文是否已填写 |
| 验证码 / 频率限制 | 等待 60 秒后重试 |

## 发布后

**必须**调用 `published-track` 技能记录本次发布。
