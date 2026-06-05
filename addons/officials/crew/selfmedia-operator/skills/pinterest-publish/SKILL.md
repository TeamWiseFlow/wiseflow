---
name: pinterest-publish
description: Create pins on Pinterest via Pinterest API v5. Supports image pins
  and video pins with board selection. Requires Pinterest OAuth2 token.
metadata:
  openclaw:
    emoji: 📌
    requires:
      bins:
      - python3
---

# Pinterest 发布（pinterest-publish）

通过 Pinterest API v5 创建 Pin，支持图片 Pin 和视频 Pin。使用 OAuth2 认证。

---

## 前置条件

1. Pinterest Developer Portal 创建应用，获取 App ID / App Secret
2. 申请 `pins:write` 和 `boards:read` 权限
3. 获取 OAuth2 Access Token

---

## 配置

保存到 `~/.openclaw/credentials/pinterest_config.json`：

```json
{
  "access_token": "your_access_token",
  "board_id": "your_default_board_id"
}
```

---

## 使用方式

图片 Pin：

```bash
python3 ./skills/pinterest-publish/scripts/publish_pinterest.py \
  --title "Pin 标题" \
  --description "描述" \
  --image https://example.com/image.jpg \
  --board-id 123456789
```

视频 Pin：

```bash
python3 ./skills/pinterest-publish/scripts/publish_pinterest.py \
  --title "Pin 标题" \
  --description "描述" \
  --video https://example.com/video.mp4 \
  --board-id 123456789
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | 是 | Pin 标题 |
| `--description` | 否 | Pin 描述 |
| `--image` | 图片必填 | 图片 URL |
| `--video` | 视频必填 | 视频 URL |
| `--board-id` | 是 | 看板 ID |
| `--link` | 否 | 关联链接 URL |

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| AUTH_REQUIRED | Token 失效 | 更新 Access Token |
| UPLOAD_FAILED | 上传失败 | 检查 URL 可访问性 |
| INVALID_BOARD | 看板 ID 无效 | 检查看板是否存在 |

注意：Pinterest API 仅支持 URL 形式的媒体，不支持本地文件上传。

---

## 发布记录（强制）

发布成功后，**必须**立即调用 `published-track` 技能记录发布信息：

```bash
./skills/published-track/scripts/record.sh \
  --platform pinterest \
  --title "标题" \
  --content-type post \
  --source-folder "<原始文件夹路径>" \
  --publish-url "<发布URL>" \
  --publish-date "$(date +%Y-%m-%d)"
```

`--source-folder` 为原始内容所在的相对路径（如 `output_articles/xxx` 或 `output_videos/xxx`）。
`--publish-url` 为发布后获得的 URL，若发布失败则留空并在 `--notes` 中注明原因。

执行 `./skills/published-track/scripts/init-db.sh`（幂等，重复执行无副作用）。
