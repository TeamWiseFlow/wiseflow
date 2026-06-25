---
name: weibo-publish
description: 通过浏览器自动化在微博发布图文内容。微博 API 对个人开发者不友好，浏览器方案更实用。
metadata:
  openclaw:
    emoji: 📢
---

# 微博发布

通过浏览器工具在微博上发布内容（文字、图片、视频）。微博 API 对个人开发者申请门槛高，浏览器自动化是更实用的方案。

**前提条件**：浏览器已登录微博（Cookie Warmup 或 QR 登录）。

---

## 发布文字微博

### 流程

1. **Cookie Warmup**：Navigate `https://weibo.com`，等待 3 秒
2. **定位输入框**：
   - 主页输入框：`textarea.W_input` 或 `[node-type="textEl"]` 或 `textarea[placeholder*="有什么新鲜事"]`
   - 如果找不到，Navigate `https://weibo.com` 刷新后重试
3. **输入文字内容**：
   - 点击输入框使其获得焦点
   - 用 `browser act kind=type` + `slowly: true` 输入内容
   - **最长 2000 字符**
4. **发布**：
   - 点击"发布"按钮：`a[node-type="submit"]` 或 `button[action-type="post"]` 或文本为"发布"的按钮
   - 等待 3 秒确认发布成功（输入框清空或出现"发布成功"提示）

---

## 发布图文微博

### 流程

1. **Cookie Warmup**：Navigate `https://weibo.com`
2. **定位输入框**（同文字微博）
3. **上传图片**：
   - 点击图片上传按钮：`a[node-type="uploadImg"]` 或 `.W_icon_pic` 图标
   - 等待文件选择对话框
   - 用 CDP `DOM.setFileInputFiles` 注入图片文件到 `input[type="file"]`
   - 等待上传完成（图片缩略图出现在编辑区）
   - **最多 9 张图片**，单张不超过 5MB
4. **输入文字内容**（同文字微博）
5. **发布**（同文字微博）

---

## 发布视频微博

### 流程

1. **Cookie Warmup**：Navigate `https://weibo.com`
2. **点击视频上传入口**：
   - 在发布框中点击视频图标：`a[node-type="uploadVideo"]`
   - 或直接 Navigate `https://weibo.com/p/103495:home`（视频发布页）
3. **上传视频文件**：
   - 用 CDP `DOM.setFileInputFiles` 注入视频文件
   - 等待上传完成（进度条到 100%）
   - **视频限制**：mp4 格式，最长 15 分钟，不超过 2GB
4. **填写描述文字**
5. **发布**

---

## Pitfalls

### pitfall: css_module_hash_drift

- **触发**：用 CSS module hash 选择器（如 `.publishBtn_1a2b3c`）
- **症状**：下次部署后选择器失效
- **workaround**：用 `node-type` 属性或 placeholder 文本定位，不用 hash class

### pitfall: input_box_collapsed

- **触发**：微博首页输入框默认折叠
- **症状**：输入框高度很小，无法直接输入
- **workaround**：先点击输入框使其展开，等待 1 秒后再输入

### pitfall: image_upload_via_cdp

- **触发**：用 `browser act` 上传图片
- **症状**：文件选择对话框无法通过 browser act 操作
- **workaround**：用 CDP `DOM.setFileInputFiles` 直接注入文件到 `input[type="file"]` 元素
- **Patchright 1.60+ 替代**：`locator.drop()` 可直接拖拽图片到输入区域，无需定位 file input

### pitfall: anti_spam_on_rapid_post

- **触发**：短时间内连续发布多条微博
- **症状**：出现验证码或"操作过于频繁"
- **workaround**：每次发布间隔 60 秒以上

### pitfall: weibo_url_shortener

- **触发**：微博内容中包含 URL
- **症状**：URL 被自动缩短为 t.cn 格式
- **workaround**：这是正常行为，不影响发布

---

## 错误处理

| 情况 | 处理 |
|------|------|
| 未登录 / 登录墙 | browser-guide QR 登录后重试 |
| 输入框找不到 | 刷新页面后重试，或用 placeholder 文本定位 |
| 图片上传失败 | 检查文件大小（<5MB），重试一次 |
| 视频上传超时 | 检查文件大小和网络，等待更长时间 |
| 验证码 / 频率限制 | 等待 60 秒后重试 |

## 发布后

**必须**调用 `published-track` 技能记录本次发布。
