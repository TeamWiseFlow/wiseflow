---
name: youtube-publish
description: Upload videos to YouTube via YouTube Data API v3. Supports video upload
  (resumable), title, description, tags, and visibility settings. Requires Google
  OAuth2 credentials.
metadata:
  openclaw:
    emoji: ▶️
    requires:
      bins:
      - python3
---

# YouTube 视频发布（youtube-publish）

通过 YouTube Data API v3 上传视频，支持断点续传、标题/描述/标签、可见性设置。使用 Google OAuth2 认证。

---

## 前置条件

1. Google Cloud Console 创建项目，启用 YouTube Data API v3
2. 配置 OAuth2 凭据（`client_secret.json`），设置重定向 URI
3. 首次运行需浏览器授权，后续自动使用 refresh token
4. 安装依赖：`pip install google-auth-oauthlib google-api-python-client`

---

## 配置

将 OAuth2 凭据文件保存为 `~/.openclaw/credentials/youtube_client_secret.json`

首次授权后 refresh token 自动保存到 `~/.openclaw/credentials/youtube_token.json`

---

## 使用方式

```bash
python3 ./skills/youtube-publish/scripts/publish_youtube.py \
  --title "视频标题" \
  --video video.mp4 \
  --description "视频描述" \
  --tags AI,科技,工具 \
  --visibility public
```

Shorts 发布：

```bash
python3 ./skills/youtube-publish/scripts/publish_youtube.py \
  --title "#shorts 标题" \
  --video shorts.mp4 \
  --visibility public
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | 是 | 视频标题，最多 100 字 |
| `--video` | 是 | 视频文件路径，支持 mp4/mov/avi |
| `--description` | 否 | 视频描述，最多 5000 字 |
| `--tags` | 否 | 逗号分隔的标签 |
| `--visibility` | 否 | `public`/`unlisted`/`private`，默认 `private` |
| `--category-id` | 否 | YouTube 分类 ID，默认 28（科技） |
| `--made-for-kids` | 否 | 是否为儿童内容，默认否 |

---

## Agent 工作流

1. 检查 OAuth2 凭据文件是否存在
2. 准备视频 + 标题 + 可见性
3. 运行 `publish_youtube.py` 脚本
4. 首次运行会输出授权 URL，用户需在浏览器中完成授权
5. 检查 stdout JSON 输出：
   - `{"ok": true, "video_id": "xxx", "url": "https://youtu.be/xxx"}` → 成功
   - `{"ok": false, "error": "AUTH_REQUIRED"}` → 需要用户完成 OAuth2 授权
   - `{"ok": false, "error": "..."}` → 其他错误

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| AUTH_REQUIRED | 无有效 OAuth2 token | 提示用户完成浏览器授权 |
| UPLOAD_FAILED | 上传失败 | 重试一次（resumable upload 支持断点续传） |
| TITLE_TOO_LONG | 标题超 100 字 | 截断后重试 |
| QUOTA_EXCEEDED | API 配额用尽 | 等待次日配额重置 |
