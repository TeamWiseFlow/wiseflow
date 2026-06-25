---
name: threads-publish
description: Publish posts to Threads via Meta Graph API. Supports text, image, video,
  and carousel posts. Requires Meta OAuth2 token with threads_basic and threads_content_publish
  permissions.
metadata:
  openclaw:
    emoji: 🧵
    requires:
      bins:
      - python3
---

# Threads 发布（threads-publish）

通过 Meta Graph API 发布内容到 Threads，支持文字、图片、视频和轮播帖子。使用 Content Container 模式。

---

## 前置条件

1. Meta Developer 应用，获取 `threads_basic` + `threads_content_publish` 权限
2. Threads 账户关联到应用
3. 长效 Token

---

## 配置

保存到 `~/.openclaw/credentials/threads_config.json`：

```json
{
  "access_token": "your_long_lived_token",
  "threads_user_id": "your_threads_user_id"
}
```

---

## 使用方式

文字帖：

```bash
python3 ./skills/threads-publish/scripts/publish_threads.py \
  --text "帖子内容 #hashtag"
```

图片帖：

```bash
python3 ./skills/threads-publish/scripts/publish_threads.py \
  --text "描述" \
  --images https://example.com/image.jpg
```

视频帖：

```bash
python3 ./skills/threads-publish/scripts/publish_threads.py \
  --text "描述" \
  --video https://example.com/video.mp4
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--text` | 是 | 帖子文本内容 |
| `--images` | 否 | 图片 URL（逗号分隔，最多 10 张） |
| `--video` | 否 | 视频 URL |

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| AUTH_REQUIRED | Token 失效 | 更新 Token |
| UPLOAD_FAILED | 容器创建失败 | 检查 URL 可访问性 |
| MEDIA_PROCESSING | 媒体处理中 | 轮询状态等待 |

注意：Threads API 同 Instagram，仅支持 URL 形式的媒体。
