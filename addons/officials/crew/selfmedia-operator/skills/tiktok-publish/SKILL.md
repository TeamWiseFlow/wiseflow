---
name: tiktok-publish
description: Upload videos to TikTok via Content Posting API. Supports direct upload
  and URL-based publish, hashtags, and privacy settings. Requires TikTok OAuth2 credentials.
metadata:
  openclaw:
    emoji: 🎵
    requires:
      bins:
      - python3
---

# TikTok 视频发布（tiktok-publish）

通过 TikTok Content Posting API 上传视频，支持直接上传和 URL 拉取两种模式。使用 TikTok OAuth2 认证。

---

## 前置条件

1. TikTok Developer Portal 创建应用，获取 client_key / client_secret
2. 配置 OAuth2 重定向 URI
3. 首次运行需浏览器授权，后续自动使用 refresh token

---

## 配置

环境变量或配置文件：

```json
{
  "client_key": "your_client_key",
  "client_secret": "your_client_secret",
  "redirect_uri": "https://localhost:8080/callback"
}
```

保存到 `~/.openclaw/credentials/tiktok_config.json`

首次授权后 token 保存到 `~/.openclaw/credentials/tiktok_token.json`

---

## 使用方式

```bash
python3 ./skills/tiktok-publish/scripts/publish_tiktok.py \
  --title "视频标题" \
  --video video.mp4 \
  --description "描述 #hashtag1 #hashtag2" \
  --privacy public
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | 是 | 视频标题，最多 150 字 |
| `--video` | 是 | 视频文件路径，支持 mp4/mov/webm |
| `--description` | 否 | 视频描述，最多 2200 字 |
| `--privacy` | 否 | `public`/`mutual_follow`/`follower`/`private`，默认 `public` |
| `--disable-comment` | 否 | 禁用评论 |
| `--disable-duet` | 否 | 禁用合拍 |
| `--disable-stitch` | 否 | 禁止拼接 |

---

## Agent 工作流

1. 检查 TikTok 配置和 token 是否存在
2. 准备视频 + 标题 + 描述
3. 运行 `publish_tiktok.py` 脚本
4. 检查 stdout JSON 输出：
   - `{"ok": true, "publish_id": "xxx"}` → 上传成功（发布可能需要几分钟处理）
   - `{"ok": false, "error": "AUTH_REQUIRED"}` → 需要用户完成 OAuth2 授权
   - `{"ok": false, "error": "..."}` → 其他错误

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| AUTH_REQUIRED | 无有效 OAuth2 token | 提示用户完成浏览器授权 |
| UPLOAD_FAILED | 上传失败 | 检查文件格式和大小，重试一次 |
| PUBLISH_PENDING | 视频处理中 | 正常现象，TikTok 服务器处理视频需要时间 |
| QUOTA_EXCEEDED | API 配额用尽 | 等待配额重置 |
