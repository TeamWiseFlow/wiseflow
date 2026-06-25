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
