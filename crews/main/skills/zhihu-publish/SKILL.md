---
name: zhihu-publish
description: 通过 forked camoufox-cli 持久化 session zhihu 在知乎发布文章或回答。知乎无可用公开 API，需通过浏览器操作完成发布。
metadata:
  openclaw:
    emoji: 📝
---

# 知乎发布

通过 **camoufox-cli** 持久化 session `zhihu`（一个且只有一个持久化 session，fail-first 队列：同 session 已有命令在跑时新命令直接 fail）在知乎上发布文章或回答。知乎没有对个人开发者开放的发布 API，只能通过浏览器自动化。

> **主力后端 = `target=camoufox`**。下方命令 / 示例只针对 `target=camoufox`。
> **`target=host` / `target=node`**：只按本 skill 的「流程 + 提示事项」走--何时有头 / 何时无头 / 频率限制 / 错误处理约定是**后端无关**的，照本 skill 执行。不要照搬 `camoufox-cli ...` 命令，用你当前后端自带的浏览器工具语义调用即可。

---

正文先保存为 UTF-8 纯文本 `body.txt`，通过 `zhihu-publish fill --ref @<编辑器-ref> --body @/绝对路径/body.txt` 填写。wrapper 只负责读取文件、清空当前正文、填入和读回核验；文件读取失败时不操作浏览器。不要把多行正文拼进 shell，不用 `$(cat ...)`；标题仍用页面输入框填写。路径含空格时给整个 `@路径` 参数加引号。

## 前置条件

1. 持久化 session `zhihu` 已登录（登录态存 session profile 里）。本 skill 与 login-manager **完全无关**--自管探活 + 登录，**不导出 cookie/UA 落中央存储**。
2. 首次使用 / 登录态失效时，走自管**有头手动**登录流：
   - `camoufox-cli --session zhihu --persistent --headed --json open "https://www.zhihu.com"`
   - 告知用户「**知乎** 浏览器已打开，请在窗口里手动登录，完成后告诉我」
   - 等用户回复后 `snapshot` 零登录态就位
   - 登录后**close session**--登录态落磁盘 profile，不留进程占内存；本 skill 下次 `--session zhihu --persistent` 重起无头即恢复，用完再 close。

> **不导出 cookie/UA**--登录态只在 session profile 里闭环，不落 `~/.openclaw/logins/`。本 skill 不调用 `cookies export` / `identity export`。

---

## 发布文章

```
1. 启持久化 session + 打开创作页：
   camoufox-cli --session zhihu --persistent --json open "https://zhuanlan.zhihu.com/write"
2. sleep 3-5 加载编辑器，snapshot 确认 .WriteIndex-page 或 .PostEditor 出现
3. snapshot 拿到标题输入框 ref：input[placeholder*="标题"] 或 .WriteIndex-titleInput input
4. camoufox-cli --session zhihu --persistent --json type <标题-ref> "文章标题"
   - 最长 100 字符
5. snapshot 拿到正文编辑器 ref：.ProseMirror 或 .public-DraftEditor-root 或 [contenteditable="true"]
6. camoufox-cli --session zhihu --persistent --json click <正文-ref> 聚焦编辑器
7. zhihu-publish fill --ref @<正文-ref> --body @/绝对路径/body.txt
   - 知乎使用富文本编辑器（ProseMirror / Draft.js），不支持直接输入 Markdown
   - 正文文件只放待发布纯文本；Markdown 内容先转换为纯文本
8. （可选）添加话题：snapshot 找"添加话题"按钮 ref -> click -> type 话题名称 -> 从下拉选
9. snapshot 找"发布"按钮 ref -> camoufox-cli --session zhihu --persistent --json click <发布-ref>
10. sleep 3，snapshot 确认发布成功（URL 变为文章详情页）
```

### 正文格式

知乎编辑器支持：标题（H1/H2）/ 粗体 / 斜体 / 链接 / 图片（需先上传）/ 代码块 / 引用 / 有序无序列表。**不支持直接输入 Markdown**--需通过编辑器工具栏或快捷键操作。

---

## 发布回答

```
1. 启持久化 session + 打开问题页：
   camoufox-cli --session zhihu --persistent --json open "https://www.zhihu.com/question/{question_id}"
2. sleep 3-5 加载
3. 找"写回答"按钮并点击。两种方式：
   - snapshot 找 button ref（文本为"写回答"）后 camoufox-cli click @<ref>
   - 若 click 卡死/无响应，改用 eval 绕过：
     camoufox-cli --session zhihu --persistent --json eval "var b=Array.from(document.querySelectorAll('button')).find(function(x){return x.textContent.trim()==='写回答'}); if(b){b.click();'CLICKED'}else{'NOT_FOUND'}"
4. sleep 3-5 等编辑器出现，snapshot 拿到编辑器 ref（textbox 或 contenteditable）
5. 填写回答内容（见下方"填写正文"段）
6. ⚠️ 发布前必做：设置「创作声明」（见下方"创作声明"段）
7. snapshot 找"发布回答"按钮 ref -> click
8. sleep 3，确认发布成功（URL 变为 /question/.../answer/... 详情页）
```

### 填写正文

知乎编辑器是 Draft.js（`[contenteditable=true]`），正文用文件填写 wrapper：

```
zhihu-publish fill --ref @<编辑器-ref> --body @/绝对路径/body.txt
```

wrapper 聚焦指定编辑器，先清空旧正文再填入文件，并读回完整正文核对。返回 `ok: true` 才继续设置声明和发布；清空、填写或核验失败时停留在编辑页，不点击发布。

### 导入公众号文章（可选）

知乎编辑器工具栏有"导入链接"功能，支持导入微信公众号文章：

1. snapshot 找"导入"按钮 -> click -> 切换到"导入链接"tab
2. 在 textbox 中填入公众号文章 URL -> 点"开始导入"
3. 导入可能失败（知乎规范过滤：含导流二维码、广告外链、违禁词等会拦截；内容重复/敏感词会导入失败）
4. 导入失败时，改用直接 fill 正文的方式

### 创作声明（发布前必做）

⚠️ **发布回答前必须设置创作声明**，否则需要发布后重新编辑补设。

编辑器底部有「发布设置」区域，其中包含「创作声明」下拉框（combobox），默认值为"无声明"。

对于 AI 辅助创作的内容，必须选择"包含 AI 辅助创作 作者对内容负责"：

```
1. snapshot 找「创作声明」combobox ref
2. click 展开 combobox -> snapshot 找 option "包含 AI 辅助创作 作者对内容负责" -> click 该 option
3. 确认 combobox 文本变为"包含 AI 辅助创作 作者对内容负责"
```

可选值：无声明 / 包含剧透 / 包含医疗建议 / 虚构创作 / 包含理财内容 / 包含 AI 辅助创作 作者对内容负责

### 编辑已发布的回答

若发布时遗漏了创作声明，可通过编辑补设：

1. 打开回答详情页，找"编辑回答"按钮 -> click
2. 编辑器打开后，滚动到底部找「创作声明」combobox
3. 设置声明后，找"提交修改"按钮 -> click
4. sleep 3 确认保存成功

---

## 图片上传

知乎编辑器插入图片需先上传：

```
1. snapshot 找编辑器工具栏的"图片"按钮 ref -> click 触发文件选择
2. snapshot 拿到弹出的 <input type="file"> ref
3. camoufox-cli --session zhihu --persistent --json upload <图片-input-ref> <image.jpg>
   - forked cli upload 命令底层走 Playwright setInputFiles，无需 CDP setFileInput hack
4. sleep 等待上传完成（snapshot 看图片出现在编辑器）
```

---

## 必做约束

- **用完即 close 持久化 session `zhihu`**--登录态 + 指纹冻结在磁盘 profile，不留进程占内存；下次发布 `--session zhihu --persistent` 重起无头即恢复。只在 session 卡死时 `camoufox-cli --session zhihu --json close` teardown。
- 同 session 已有命令在跑时，新命令 fail-first（返回 `session zhihu 正忙，请等待当前操作完成后再试`）--读到这条文本就等当前操作完成再重试，不要盲试。
- 每次发布间隔 60 秒以上，避免触发反垃圾。

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

### pitfall: anti_spam_check

- **触发**：短时间内发布多篇内容
- **症状**：出现验证码或"操作过于频繁"提示
- **workaround**：每次发布间隔 60 秒以上

### pitfall: numeric_html_entities

- **触发**：从知乎复制内容时
- **症状**：文本含 `&#x4F60;` 等编码
- **workaround**：解码 HTML 实体后再使用

### pitfall: click_timeout

- **触发**：`camoufox-cli click @<ref>` 命令卡死或被 SIGKILL
- **症状**：click 命令无响应，进程被杀
- **workaround**：改用 `eval` 里调 `element.click()` 绕过：先 `querySelectorAll` 找到目标按钮，直接 `.click()`

### pitfall: fill_not_clearing

- **触发**：绕过正文 wrapper，在已有正文上直接输入
- **症状**：新旧内容拼接在一起
- **workaround**：使用 `zhihu-publish fill --ref @<编辑器-ref> --body @/绝对路径/body.txt`，由脚本清空、填入和核验

### pitfall: import_link_blocked

- **触发**：使用知乎"导入链接"功能导入公众号文章
- **症状**：导入后编辑器为空，无报错提示
- **workaround**：知乎规范会过滤含导流二维码、广告外链、违禁词的内容。导入失败后改用 `fill` 直接填入纯文本

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 未登录 / 登录墙 | 走前置条件的有头手动登录流，重试一次 |
| 编辑器未加载 | 等待 5 秒后重试，检查选择器 |
| 发布按钮灰色 | 检查标题/正文是否已填写 |
| 验证码 / 频率限制 | 等待 60 秒后重试 |
| session 正忙（fail-first） | 等当前操作完成再重试，不要盲试 |
| click 命令卡死 | 改用 eval + element.click() 绕过 |

## 发布后

**必须**调用 `published-track` 技能记录本次发布。
