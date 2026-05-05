---
name: xhs-publisher
description: '小红书内容发布技能。支持图文发布、视频发布、长文发布、定时发布、标签、可见性设置。

  当用户要求发布内容到小红书、上传图文/视频、发长文时触发。

  '
metadata:
  openclaw:
    emoji: 📮
---

# 小红书内容发布

通过 **browser工具**完成给定内容在小红书平台上的发布。

**前提条件**:browser 需已登录小红书。若尚未登录,遵循 browser-guide 第 6 节 QR 登录流程完成扫码登录。

---

## 小红书基础运营规范

- **标题**(非常重要):不超过 20 个字(UTF-16 计算:汉字/全角符号算 1,英文/数字每 2 个算 1)
- **正文**(非常重要):不超过 1000 字
- **图文 > 视频/纯文字**:从推荐流量角度,图文效果最好
- **Tags**:选择相关话题标签,能带来更多流量
- **禁止引流**:不得出现导流信息,属于官方重点打击对象

如果用户提供的是 文字内容/markdown通稿，按上述规范审查，修改不符合规范的部分，并在正文末尾添加 2-3 个相关话题标签和小红书平台的 hook 模板（见 AGENTS.md 严格平台策略 - 小红书）。

如果用户提供的是 视频/图片 等纯媒体素材或者简单的文字大意，需要按上述运营规范生成符合规范的标题和正文，并在正文末尾添加 2-3 个相关话题标签和小红书平台的 hook 模板（见 AGENTS.md 严格平台策略 - 小红书）。生成的标题和正文必须与用户提供的内容相关且符合小红书运营规范。

---

## 浏览器操作通用约束

- 视频文件上传前必须先复制到 `/tmp/openclaw/uploads/`(browser 工具沙箱限制)
- `browser upload` 工具可能返回「超时错误」,但这**不代表上传失败**!上传后用 snapshot 检查页面状态(进度条、处理状态文字)
- **不要通过检查 `input.files.length` 是否为 0 判定上传是否失败!** `input.files.length == 0` 不代表上传失败。
- 遇到 `browser failed: timed out. Restart the OpenClaw gateway ...` 错误时,**不需要重启、不需要报错**!等待 30 秒后在原页面继续操作即可。若仍无法操作,再等 30 秒;若还不行,尝试关闭浏览器后重开;只有关闭重开后仍报错才是真的出错,需停止并反馈用户。
- 标题和描述输入使用 `type` + `slowly: true`,不要用 `fill()`
- 浏览器超时只汇报,不执行 `browser stop/start`
- 上传进度轮询用 snapshot,不重试 click

---

## 根据输入判断执行流程

按优先级判断:

1. 用户说"发长文 / 写长文 / 长文模式":进入**长文发布流程(流程 C)**。
2. 已有 `标题 + 正文 + 视频(本地路径)`:进入**视频发布流程(流程 B)**。
3. 已有 `标题 + 正文 + 图片(本地路径)`:进入**图文发布流程(流程 A)**。
4. 每日 HEARTBEAT 任务,进入**图文发布流程(流程 A)**。
5. 默认走**图文发布流程(流程 A)**。

---

## 发布入口

发布页 URL:`https://creator.xiaohongshu.com/publish/publish?source=official`

导航后页面顶部有三个 Tab(点击文本精确匹配):
- `上传图文` - 图文发布
- `上传视频` - 视频发布
- `写长文` - 长文发布

> **弹窗处理**:页面可能弹出 `div.d-popover` 引导提示,直接点击弹窗外区域(如页面顶部空白处)关闭。

---

## 流程 A:图文发布

### Step A.1 导航

```
1. 导航到发布页
2. 等待页面加载完成(3-5 秒)
3. 点击"上传图文" Tab
```

### Step A.2 上传图片

**重要:文件路径处理**

browser upload 工具只能操作 `/tmp/openclaw/uploads/` 目录下的文件。如果图片在其他位置,必须先复制到该目录:

```bash
cp /path/to/your/image.jpg /tmp/openclaw/uploads/
```

**上传操作**

```
1. 点击上传按钮(或 file input)
2. 使用 browser upload 上传图片:
   - selector = input.upload-input
   - paths = ["/tmp/openclaw/uploads/img1.jpg", "/tmp/openclaw/uploads/img2.jpg", ...]
3. 执行 browser upload 后,等待 30 秒
4. 使用 snapshot 检查页面状态:
   - 是否出现图片预览/缩略图
   - 页面是否显示「图片编辑」字样
   - 是否显示图片数量(如 "2/18")
5. 如果第一次 snapshot 未看到缩略图,再等 60 秒后重新 snapshot
6. 重复检查最多 3 次,全部失败才判断上传失败
```

### Step A.3 填写表单

**重要:必须区分标题和正文,分别输入**

小红书的标题和正文是两个独立的输入框,必须分别操作。

**标题输入**:
```
1. 点击标题输入框:div.d-input input 或 textbox[placeholder*="标题"]
2. 使用  `type` + `slowly: true` 输入标题:
3. 检查是否超长,超长则需精简
```

**正文输入**:
```
1. 点击正文编辑器:div.ql-editor(contenteditable 富文本编辑器)
2. 使用  `type` + `slowly: true` 输入正文:
3. 不要使用 fill(),会导致编辑器无法识别内容
```

**标签输入**:
```
在正文末尾回车新起一行,输入 # 然后逐字符输入话题词:
- 每输入几个字后等待 0.5 秒,观察是否出现联想菜单
  (selector: #creator-editor-topic-container .item)
- 联想菜单出现后点击第一个条目
- 未出现联想则输入空格结束该标签
- 每个标签之间等待 0.5-1 秒(最多 10 个标签)
```

### Step A.4 可选设置

```
定时发布(可选,用户未说,则默认立即发布):
  1. 点击 .post-time-wrapper .d-switch 开关
  2. 在 .date-picker-container input 填入时间(格式:2026-04-10 18:00)

可见范围(可选,默认公开,用户未说则默认公开):
  1. 点击 div.permission-card-wrapper div.d-select-content 下拉
  2. 在 div.d-options-wrapper div.d-grid-item div.custom-option 中选择目标项
     可选值:公开可见 / 仅自己可见 / 仅互关好友可见

原创声明(可选,用户未说则默认声明):
  1. 在 div.custom-switch-card 中找到含"原创声明"文字的卡片
  2. 点击其中的 div.d-switch 开关
  3. 弹出确认对话框时,先勾选协议 checkbox,再点击"声明原创"按钮
```

### Step A.5 确认并发布

直接发布,不要问用户。

---

## 流程 B:视频发布

### Step B.1 导航并切换 Tab

```
导航到发布页 → 点击"上传视频" Tab
```

### Step B.2 上传视频

```
selector = input.upload-input(或 input[type="file"])
上传视频文件后,等待发布按钮变为可点击状态:
  selector = .publish-page-publish-btn button.bg-red
  视频处理最长需要 10 分钟,每隔 5 秒 snapshot 一次检查按钮状态
  按钮显示且不含 disabled class 时视为可发布
```

### Step B.3 填写表单

```
与图文流程相同:
- 标题:div.d-input input
- 正文:div.ql-editor(contenteditable)
- 标签:正文末尾 #话题 输入
- 可见范围、定时发布(可选,用户未说则都按默认)
```

### Step B.4 确认并发布

直接发布,不要问用户。

---

## 流程 C:长文发布

### Step C.1 进入长文编辑器

```
1. 导航到发布页 → 点击"写长文" Tab
2. 点击"新的创作"按钮(通过文本匹配)
3. 等待 2 秒,页面加载长文编辑器
```

### Step C.2 填写长文内容

```
标题:textarea[placeholder="输入标题"],click 后 `type` + `slowly: true` 输入标题

正文:div.ql-editor(contenteditable),`type` + `slowly: true` 分段输入正文内容

图片(可选):在 ql-editor 中将光标定位到目标位置后上传
```

### Step C.3 一键排版 + 选择模板

```
1. 点击"一键排版"按钮(文本匹配)
2. 等待 3-5 秒,观察页面中出现 .template-card 卡片列表
3. 根据内容自动选择合适的模板卡片
   - 通过 snapshot 获取每个卡片的标题(.template-title)和简介(.template-desc)
   - 根据标题和简介内容判断适合的模板类型(如图文、视频、长图等)
4. 点击对应模板卡片(.template-card .template-title 文本匹配)
```

### Step C.4 进入发布页填写描述

```
1. 点击"下一步"按钮(文本匹配)
2. 等待 3 秒,页面切换到长文发布页
3. 在 div.ql-editor 中填写发布描述(摘要,≤1000 字)
```

### Step C.5 确认并发布

直接发布,不要问用户.


---

## 错误处理

| 情况 | 处理 |
|------|------|
| 页面出现登录墙 | 遵循 browser-guide 第 6 节 QR 登录流程,扫码后重试 |
| 图片上传超时(browser upload 返回超时错误) | **忽略此错误**,等待 60 秒后 snapshot 检查页面是否有缩略图 |
| 图片上传验证失败(3 次检查均无缩略图) | 提示用户检查文件路径和格式(支持 jpg/png/webp) |
| 视频处理超时(10 分钟) | 提示用户视频可能过大或格式不兼容(推荐 MP4) |
| 标题超长 | 自动重新生成符合规范的标题 |
| 正文超长 | div.edit-container div.length-error 出现时截断正文 |
| 用户取消发布 | 必须点击"暂存离开"保存草稿,禁止直接关闭 |
| 标签联想不出现 | 输入空格结束该标签,继续下一个 |
