---
name: facebook-publish
description: Publish posts, videos, and reels to Facebook via Meta Graph API v23.0.
  Supports feed posts, video posts, photo posts, reels, and stories. Requires Meta
  OAuth2 page access token.
metadata:
  openclaw:
    emoji: 📘
    requires:
      bins:
      - python3
---

# Facebook 发布（facebook-publish）

通过 Meta Graph API v23.0 发布内容到 Facebook，支持帖子、视频、Reels 和 Stories。使用 Meta OAuth2 Page Access Token 认证。

---

## 前置条件

1. Meta Developer Portal 创建应用，获取 App ID / App Secret
2. 申请 `pages_manage_posts` 和 `pages_read_engagement` 权限
3. 获取长效 Page Access Token

---

## 配置

保存到 `~/.openclaw/credentials/facebook_config.json`：

```json
{
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "page_access_token": "your_long_lived_page_token",
  "page_id": "your_page_id"
}
```

---

## 使用方式

文字帖子：

```bash
python3 ./skills/facebook-publish/scripts/publish_facebook.py \
  --message "帖子内容" \
  --mode feed
```

视频/Reel：

```bash
python3 ./skills/facebook-publish/scripts/publish_facebook.py \
  --message "描述" \
  --video video.mp4 \
  --mode reel
```

图片帖子：

```bash
python3 ./skills/facebook-publish/scripts/publish_facebook.py \
  --message "描述" \
  --images img1.jpg img2.jpg \
  --mode feed
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--message` | 是 | 帖子内容 |
| `--mode` | 是 | `feed`/`video`/`reel`/`story` |
| `--video` | 视频模式必填 | 视频文件路径 |
| `--images` | 图片模式必填 | 图片路径列表 |
| `--title` | 否 | 视频标题（video 模式） |

---

## Agent 工作流

1. 检查 Facebook 配置是否存在
2. 准备内容 + 媒体文件
3. 运行 `publish_facebook.py` 脚本
4. 检查 stdout JSON 输出：
   - `{"ok": true, "post_id": "xxx", "url": "https://facebook.com/xxx"}` → 成功
   - `{"ok": false, "error": "AUTH_REQUIRED"}` → 更新 Page Token
   - `{"ok": false, "error": "..."}` → 其他错误

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| AUTH_REQUIRED | Token 失效 | 更新 Page Access Token |
| UPLOAD_FAILED | 上传失败 | 检查文件格式，重试 |
| MEDIA_PROCESSING | 视频处理中 | 轮询状态等待完成 |
| RATE_LIMIT | 频率限制 | 等待后重试 |
