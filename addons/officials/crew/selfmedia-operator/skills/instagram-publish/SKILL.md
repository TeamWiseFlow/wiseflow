---
name: instagram-publish
description: Publish posts and reels to Instagram via Meta Graph API. Supports single
  images, carousels (up to 10), and reels. Uses content container pattern. Requires
  Meta OAuth2 token with instagram_basic and instagram_content_publish permissions.
metadata:
  openclaw:
    emoji: 📸
    requires:
      bins:
      - python3
---

# Instagram 发布（instagram-publish）

通过 Meta Graph API 发布内容到 Instagram，支持单图、轮播（最多 10 张）和 Reels。使用 Content Container 模式。需要 Instagram Professional 账户关联到 Facebook Page。

---

## 前置条件

1. Instagram Professional 账户（Business 或 Creator）
2. 关联 Facebook Page
3. Meta Developer 应用，获取 `instagram_basic` + `instagram_content_publish` 权限
4. 长效 Page Access Token

---

## 配置

保存到 `~/.openclaw/credentials/instagram_config.json`：

```json
{
  "page_access_token": "your_long_lived_page_token",
  "ig_user_id": "your_ig_business_account_id"
}
```

---

## 使用方式

单图帖子：

```bash
python3 ./skills/instagram-publish/scripts/publish_instagram.py \
  --caption "描述 #hashtag1 #hashtag2" \
  --images photo.jpg \
  --mode feed
```

轮播帖子：

```bash
python3 ./skills/instagram-publish/scripts/publish_instagram.py \
  --caption "描述" \
  --images img1.jpg img2.jpg img3.jpg \
  --mode carousel
```

Reel：

```bash
python3 ./skills/instagram-publish/scripts/publish_instagram.py \
  --caption "描述" \
  --video reel.mp4 \
  --mode reel
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--caption` | 是 | 描述，最多 2200 字，最多 30 个 hashtag |
| `--mode` | 是 | `feed`/`carousel`/`reel` |
| `--images` | feed/carousel必填 | 图片 URL 列表，carousel 最多 10 张 |
| `--video` | reel必填 | 视频 URL，Reels 建议 9:16，≤90s |

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| AUTH_REQUIRED | Token 失效 | 更新 Token |
| UPLOAD_FAILED | 容器创建失败 | 检查图片 URL 可访问性 |
| MEDIA_PROCESSING | 媒体处理中 | 轮询状态等待 |
| RATE_LIMIT | API 限制 | 等待后重试 |

注意：Instagram API 发布只支持 **URL** 形式的媒体，不支持本地文件上传。需要先将图片/视频上传到可公开访问的 URL。

---

## 发布记录（强制）

发布成功后，**必须**立即调用 `published-track` 技能记录发布信息：

```bash
./skills/published-track/scripts/record.sh \
  --platform instagram \
  --title "标题" \
  --content-type post \
  --source-folder "<原始文件夹路径>" \
  --publish-url "<发布URL>" \
  --publish-date "$(date +%Y-%m-%d)"
```

`--source-folder` 为原始内容所在的相对路径（如 `output_articles/xxx` 或 `output_videos/xxx`）。
`--publish-url` 为发布后获得的 URL，若发布失败则留空并在 `--notes` 中注明原因。

执行 `./skills/published-track/scripts/init-db.sh`（幂等，重复执行无副作用）。
