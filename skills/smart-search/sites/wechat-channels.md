# 微信视频号 (WeChat Channels)

> last_verified: 2026-06-15 | 来源：OpenCLI clis/wechat-channels/publish.js + sitemaps

## 概览

- 域名：`channels.weixin.qq.com`
- 登录要求：**所有操作需登录**（微信扫码）
- Auth 策略：Cookie Warmup + 扫码登录

## 搜索

微信视频号**没有独立的搜索 URL**，搜索入口在微信客户端内。Web 端只能访问创作者中心。

### 可访问的 Web 内容

- 创作者中心：`https://channels.weixin.qq.com/platform/home`
- 视频管理：`https://channels.weixin.qq.com/platform/post/list`

### 替代搜索方式

1. **Bing 搜视频号内容**：`site:channels.weixin.qq.com {keyword}`
2. **微信内搜索**：需在微信客户端操作，Web 无法替代

## Pitfalls

### pitfall: wujie_shadow_dom

- **触发**：访问创作者中心页面
- **症状**：所有表单元素在 `<wujie-app>::shadow-root` 内，常规 DOM 选择器找不到
- **workaround**：CDP 操作需使用 shadow DOM 穿透（`DOM.querySelector` 带 pierce 模式），或 `browser evaluate` 中用 `document.querySelector('wujie-app').shadowRoot.querySelector(selector)`

### pitfall: login_via_qr_only

- **触发**：访问视频号页面未登录
- **症状**：跳转到扫码登录页，无用户名/密码选项
- **workaround**：等待用户在手机微信扫码确认，最长等 2 分钟

### pitfall: video_upload_via_cdp

- **触发**：上传视频文件到发布页
- **症状**：普通 `browser act` 无法触发 `<input type="file">`（在 shadow DOM 内）
- **workaround**：需用 CDP `DOM.setFileInputFiles` 注入文件，或 DataTransfer base64 分块注入（大文件分 50KB 块避免超出 bridge 限制）

## Fallback

视频号搜索无法在 Web 端完成 → 用 Bing `site:channels.weixin.qq.com` 替代

## Re-entry

- 在创作者中心页面 → 继续操作
- 在扫码登录页 → 等待用户扫码后继续
