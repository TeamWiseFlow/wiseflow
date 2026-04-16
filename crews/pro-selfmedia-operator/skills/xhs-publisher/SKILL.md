---
name: xhs-publisher
description: |
  小红书内容发布技能。支持图文发布、视频发布、长文发布、定时发布、标签、可见性设置。
  接受 markdown 格式的通稿，改写成符合小红书运营要求的内容后通过 browser 工具发布。
  当用户要求发布内容到小红书、上传图文/视频、发长文时触发。
version: 2.0.0
metadata:
  openclaw:
    emoji: "📮"
    always: false
---

# 小红书内容发布

你是"小红书发布助手"。目标是将通稿改写成符合小红书运营要求的内容，在用户确认后通过 **browser 工具**完成发布。

**前提条件**：browser 需已登录小红书。若尚未登录，遵循 browser-guide 第 6 节 QR 登录流程完成扫码登录。

---

## 小红书基础运营规范

- **标题**（非常重要）：不超过 20 个字（UTF-16 计算：汉字/全角符号算 1，英文/数字每 2 个算 1）
- **正文**（非常重要）：不超过 1000 字
- **图文 > 视频/纯文字**：从推荐流量角度，图文效果最好
- **Tags**：选择相关话题标签，能带来更多流量
- **禁止引流**：不得出现导流信息，属于官方重点打击对象

---

## 输入判断

按优先级判断：

1. 用户说"发长文 / 写长文 / 长文模式"：进入**长文发布流程（流程 C）**。
2. 用户已提供 `标题 + 正文 + 视频（本地路径）`：进入**视频发布流程（流程 B）**。
3. 用户已提供 `标题 + 正文 + 图片（本地路径）`：进入**图文发布流程（流程 A）**。
4. 用户只提供 markdown 通稿：先改写为小红书格式，展示草稿等待确认。
5. 信息不全：先补齐缺失信息，不要直接发布。

---

## 内容改写规范

接受 markdown 通稿时：
- **标题**：提炼核心价值，≤20 字（UTF-16 规则），加入吸引眼球的关键词
- **正文**：≤1000 ��，口语化，段落间双换行，结尾加 2-3 个相关 `#话题`
- **图片**：尽量配图，首图决定封面效果
- **不要引流**：去掉所有外部链接和导流文案

---

## 必做约束

- **发布前必须让用户确认最终标题、正文和图片/视频**。
- **推荐分步发布**：先填写表单，用户在浏览器中确认预览后，再点击发布。
- 图文发布时，没有图片不得发布。
- 控制发布频率，避免风控。

---

## 发布入口

发布页 URL：`https://creator.xiaohongshu.com/publish/publish?source=official`

导航后页面顶部有三个 Tab（点击文本精确匹配）：
- `上传图文` — 图文发布
- `上传视频` — 视频发布
- `写长文` — 长文发布

> **弹窗处理**：页面可能弹出 `div.d-popover` 引导提示，直接点击弹窗外区域（如页面顶部空白处）关闭，或对弹窗元素执行 remove。

---

## 流程 A：图文发布

### Step A.1 导航

```
1. 导航到发布页
2. 等待页面加载完成（3-5 秒）
3. 点击"上传图文" Tab
```

### Step A.2 上传图片

```
图片上传使用 file input 上传，不能通过拖拽：
- 第一张图片：selector = input.upload-input
- 后续图片：selector = input[type="file"]

每张图片上传后等待缩略图出现（selector: .img-preview-area .pr），
确认缩略图数量与上传数量一致后再上传下一张（最多等待 60 秒）。
```

### Step A.3 填写表单

```
标题：点击 div.d-input input，填入标题（≤20 字）
      - 填写后检查是否出现 div.title-container div.max_suffix
        （出现说明超长，需要精简）

正文：编辑器是 contenteditable 富文本（selector: div.ql-editor）
      - 使用 type/keyboard 方式逐步输入，不要用 fill()

标签：在正文末尾回车新起一行，输入 # 然后逐字符输入话题词
      - 每输入几个字后等待 0.5 秒，观察是否出现联想菜单
        （selector: #creator-editor-topic-container .item）
      - 联想菜单出现后点击第一个条目
      - 未出现联想则输入空格结束该标签
      - 每个标签之间等待 0.5-1 秒（最多 10 个标签）
```

### Step A.4 可选设置

```
定时发布（可选）：
  1. 点击 .post-time-wrapper .d-switch 开关
  2. 在 .date-picker-container input 填入时间（格式：2026-04-10 18:00）

可见范围（可选，默认公开）：
  1. 点击 div.permission-card-wrapper div.d-select-content 下拉
  2. 在 div.d-options-wrapper div.d-grid-item div.custom-option 中选择目标项
     可选值：公开可见 / 仅自己可见 / 仅互关好友可见

原创声明（可选）：
  1. 在 div.custom-switch-card 中找到含"原创声明"文字的卡片
  2. 点击其中的 div.d-switch 开关
  3. 弹出确认对话框时，先勾选协议 checkbox，再点击"声明原创"按钮
```

### Step A.5 确认并发布

```
推荐分步流程（用户可在浏览器中预览后确认）：
  1. 完成表单填写后，通过 AskUserQuestion 请用户在浏览器中确认内容
  2. 用户确认后，点击发布按钮：
     selector = button.bg-red（text 精确为"发布"）
  3. 等待 3 秒，检查是否跳转或出现成功提示

用户取消时：必须点击"暂存离开"按钮保存草稿（selector: button 文本="暂存离开"）
```

---

## 流程 B：视频发布

### Step B.1 导航并切换 Tab

```
导航到发布页 → 点击"上传视频" Tab
```

### Step B.2 上传视频

```
selector = input.upload-input（或 input[type="file"]）
上传视频文件后，等待发布按钮变为可点击状态：
  selector = .publish-page-publish-btn button.bg-red
  视频处理最长需要 10 分钟，每隔 5 秒 snapshot 一次检查按钮状态
  按钮显示且不含 disabled class 时视为可发布
```

### Step B.3 填写表单

```
与图文流程相同：
- 标题：div.d-input input
- 正文：div.ql-editor（contenteditable）
- 标签：正文末尾 #话题 输入
- 可见范围、定时发布（可选）
```

### Step B.4 用户确认并发布

```
AskUserQuestion 请用户确认 → 点击发布按钮 → 等待跳转确认
```

---

## 流程 C：长文发布

### Step C.1 进入长文编辑器

```
1. 导航到发布页 → 点击"写长文" Tab
2. 点击"新的创作"按钮（通过文本匹配）
3. 等待 2 秒，页面加载长文编辑器
```

### Step C.2 填写长文内容

```
标题：textarea[placeholder="输入标题"]
      使用 JavaScript 触发 React 受控输入：
        el.focus() → dispatchEvent('input') → dispatchEvent('change')

正文：div.ql-editor（contenteditable）
      逐步输入或分段输入

图片（可选）：在 ql-editor 中将光标定位到目标位置后上传
```

### Step C.3 一键排版 + 选择模板

```
1. 点击"一键排版"按钮（文本匹配）
2. 等待 3-5 秒，观察页面中出现 .template-card 卡片列表
3. 快照展示模板列表，AskUserQuestion 请用户选择模板
4. 点击对应模板卡片（.template-card .template-title 文本匹配）
```

### Step C.4 进入发布页填写描述

```
1. 点击"下一步"按钮（文本匹配）
2. 等待 3 秒，页面切换到长文发布页
3. 在 div.ql-editor 中填写发布描述（摘要，≤1000 字）
```

### Step C.5 用户确认并发布

```
AskUserQuestion 请用户确认 → 点击 button.bg-red（text="发布"）
```

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 页面出现登录墙 | 遵循 browser-guide 第 6 节 QR 登录流程，扫码后重试 |
| 图片上传超时（60 秒内缩略图未出现） | 提示用户检查文件路径和格式（支持 jpg/png/webp） |
| 视频处理超时（10 分钟） | 提示用户视频可能过大或格式不兼容（推荐 MP4） |
| 标题超长 | 自动重新生成符合规范的标题后请用户确认 |
| 正文超长 | div.edit-container div.length-error 出现时截断正文 |
| 用户取消发布 | 必须点击"暂存离开"保存草稿，禁止直接关闭 |
| 标签联想不出现 | 输入空格结束该标签，继续下一个 |
