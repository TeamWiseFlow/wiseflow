---
name: wechat-channels-publish
description: 通过浏览器自动化发布视频到微信视频号。处理 wujie shadow DOM，支持视频上传、标题描述填写、即时发布。
metadata:
  openclaw:
    emoji: 📺
---

# 微信视频号发布

通过浏览器工具在微信视频号创作者中心发布视频。视频号创作者中心使用 **wujie 微前端**，所有表单元素在 `<wujie-app>::shadow-root` 内，需要特殊处理。

**前提条件**：浏览器已登录 `channels.weixin.qq.com`（微信扫码登录）。

---

## 发布流程

### Step 1: 导航到发布页

```
Navigate https://channels.weixin.qq.com/platform/post/create
```

等待 **5 秒**（wujie 需要额外时间初始化 shadow DOM）。

### Step 2: 检查登录态

如果页面 URL 包含 `login` 或出现登录二维码：
- 按`browser-guide`技能的 1-B QR Code 登录流程处理

### Step 3: 上传视频

**方式 A：CDP setFileInputFiles（推荐）**

```bash
python ./skills/wechat-channels-publish/scripts/upload_video.py --video <video_path> --cdp-port <port>
```

脚本会：
1. 找到上传触发按钮（shadow DOM 内的 `span.add-icon` 或 `div.upload-content`）
2. 点击触发按钮激活隐藏的 `<input type="file">`
3. 用 CDP `DOM.setFileInputFiles` 注入视频文件
4. 如果 setFileInput 失败（shadow DOM 限制），fallback 到方式 B

**方式 B：DataTransfer base64 分块注入**

当 CDP setFileInput 在 shadow DOM 内失败时使用：
```bash
python ./skills/wechat-channels-publish/scripts/upload_video.py --video <video_path> --cdp-port <port> --method base64
```

脚本会：
1. 读取视频文件，转为 base64
2. 分 50KB 块通过 `Runtime.evaluate` 注入页面 `window.__oc_chunks` 数组
3. 在页面内组装 `DataTransfer` + `File` 对象，设置到 `<input type="file">` 的 `files` 属性
4. 触发 `change` + `input` 事件

**支持的视频格式**：`.mp4`、`.mov`、`.avi`、`.webm`

### Step 4: 等待上传+转码完成

上传后视频需要转码处理，等待方式：
- 每 3 秒检查一次页面状态
- 上传中：shadow DOM 内存在 `[class*="uploading"]` 或 `[class*="progress"]`
- 转码中：`[class*="transcoding"]`
- 完成：出现 `<video>` 预览或 `[class*="preview-video"]` 或文本"上传成功"/"转码完成"
- 失败：`[class*="upload-fail"]` 或文本"上传失败"
- **最长等待 3 分钟**（大视频转码可能较慢）

### Step 5: 填写标题

```bash
python ./skills/wechat-channels-publish/scripts/fill_form.py --title "<标题>" --cdp-port <port>
```

- 标题输入框在 shadow DOM 内：`input[placeholder*="短标题"]`
- **建议 6-16 字**，最长约 30 字
- 脚本通过 `Runtime.evaluate` 在 shadow root 内查找并填写

### Step 6: 填写描述

```bash
python ./skills/wechat-channels-publish/scripts/fill_form.py --caption "<描述内容>" --cdp-port <port>
```

- 描述输入框：`div[contenteditable][data-placeholder="添加描述"]`
- **话题标签**直接写在描述中，如：`日常生活 #搞笑 #生活`
- 最长约 300 字

### Step 7: 发布

> 视频号发布不必勾选"原创声明"，发布后用户会在手机端补充。

点击"发表"按钮：
- 按钮在 shadow DOM 内，文本为"发表"或"发布"
- 按钮不能是 disabled 状态

```bash
python ./skills/wechat-channels-publish/scripts/fill_form.py --publish --cdp-port <port>
```

- 发布时如果弹出“原创声明弹窗”，直接点击 “直接发表” 即可。

### Step 8: 确认发布成功

等待 4 秒后检查：
- 页面会自动跳转到视频管理的视频列表页面
- 或 URL 变为 `https://channels.weixin.qq.com/platform/post/list`
- 刚发表的作品通常在第一个。但是它可能处于转码之中，表现为封面缩略图为灰色，转圈。此时需要等待，每隔五秒看一下转码是否已经完成（封面缩略图出现），此时才能进行下一步。

### Step 9: 获取已发布视频链接

发布成功后，在视频号管理后台的视频列表页获取视频公开链接：

1. 找到刚发布的视频（列表第一条，或按标题匹配）
3. 点击该视频的 **"分享"** 按钮
4. 在弹出的分享面板中，点击 **"复制视频链接"**
5. 链接格式通常为 `https://weixin.qq.com/sph/xxxxxx`（`sph` 即视频号拼音缩写）

> **注意**：如果刚发布的视频还在审核中，"分享"按钮可能不可用。此时可先完成发布记录（publish_url 留空），待审核通过后再补充链接。

**自动化脚本方式**（推荐）：

```bash
python ./skills/wechat-channels-publish/scripts/get_video_link.py --cdp-port <port> [--title "<视频标题>"]
```

脚本会自动：
1. 在视频列表页找到刚发布的视频
2. 点击"分享"按钮
3. 点击"复制链接"
4. 从剪贴板读取链接并输出

链接将用于数据记录流程（不在本技能流程中，通常是执行完本技能之后执行）

---

## 保存草稿

在 Step 7 中点击"存草稿"按钮而非"发表"。

---

## 手动模式

如果需要人工检查表单后再发布：
1. 完成到 Step 6（所有字段已填写）
2. **不自动点击发表**，告知用户在浏览器中手动检查并点击
3. 注意：不操作时标签页约 30 秒后可能被重置为空白页

---

## Pitfalls

### pitfall: wujie_shadow_dom

- **触发**：访问创作者中心任何页面
- **症状**：常规 DOM 选择器找不到表单元素
- **workaround**：所有操作必须穿透 shadow DOM：
  - Python CDP 脚本中使用 `document.querySelector('wujie-app').shadowRoot.querySelector(selector)`
  - 或 CDP `DOM.querySelector` 带 `pierce:` 模式（如果 Patchright 支持）

### pitfall: cdp_setfileinput_in_shadow_dom

- **触发**：CDP `DOM.setFileInputFiles` 对 shadow DOM 内的 `<input type="file">` 操作
- **症状**：返回 `Not allowed` 错误
- **workaround**：fallback 到 DataTransfer base64 分块注入方式
- **Patchright 1.60+ 替代**：`locator.drop()` 可模拟拖拽文件到上传区域，绕过 shadow DOM 内 file input 的限制：
  ```javascript
  const videoBuffer = fs.readFileSync(videoPath);
  await page.locator('.upload-content').drop({
    files: { name: 'video.mp4', mimeType: 'video/mp4', buffer: videoBuffer }
  });
  ```
  需验证视频号上传区域是否响应 drop 事件（部分自定义组件可能不处理 drag/drop）。

### pitfall: video_transcode_timeout

- **触发**：大视频文件上传后转码
- **症状**：等待超过 3 分钟仍未完成
- **workaround**：增加等待时间（`--timeout 600`），或检查视频格式是否兼容

### pitfall: login_qr_only

- **触发**：访问视频号页面未登录
- **症状**：跳转到扫码登录页，无用户名/密码选项
- **workaround**：等待用户在手机微信扫码确认

### pitfall: form_reset_on_idle

- **触发**：填写完表单后长时间不操作
- **症状**：标签页被重置为空白页（约 30 秒空闲超时）
- **workaround**：填完表单后立即发布，或使用手动模式让用户快速操作

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 未登录 | 等待用户扫码登录，最长 2 分钟 |
| 上传失败 | 检查视频格式（mp4/mov/avi/webm），重试一次 |
| setFileInput Not allowed | 自动 fallback 到 base64 注入方式 |
| 转码超时 | 增加超时时间，或告知用户稍后在创作者中心检查 |
| 发表按钮 disabled | 检查必填字段是否已填写（视频是否上传完成） |
| shadow DOM 元素找不到 | 等待更长时间让 wujie 初始化，或刷新页面 |
