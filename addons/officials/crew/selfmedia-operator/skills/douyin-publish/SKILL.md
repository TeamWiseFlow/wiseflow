---
name: douyin-publish
description: Publish videos to Douyin (抖音) via open platform API with OAuth2 authentication.
  Supports video upload, cover image, hashtags, and privacy settings. Requires Douyin
  open platform OAuth2 credentials.
metadata:
  openclaw:
    emoji: 🎤
    requires:
      bins:
      - python3
---

# 抖音视频发布（douyin-publish）

通过抖音开放平台 API 发布视频，支持视频上传、封面、话题标签。使用 OAuth2 认证。

---

## 前置条件

1. 抖音开放平台创建应用，获取 client_key / client_secret
2. 申请「视频管理」权限范围
3. 首次运行需浏览器授权，后续自动使用 refresh token

---

## 配置

保存到 `~/.openclaw/credentials/douyin_config.json`：

```json
{
  "client_key": "your_client_key",
  "client_secret": "your_client_secret",
  "redirect_uri": "https://localhost:8080/callback"
}
```

首次授权后 token 保存到 `~/.openclaw/credentials/douyin_token.json`

---

## 使用方式

```bash
python3 ./skills/douyin-publish/scripts/publish_douyin.py \
  --title "视频标题" \
  --video video.mp4 \
  --cover cover.jpg \
  --tags 话题1,话题2
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | 是 | 视频标题，最多 55 字 |
| `--video` | 是 | 视频文件路径，支持 mp4，建议 9:16 |
| `--cover` | 否 | 封面图 URL 或本地路径 |
| `--tags` | 否 | 逗号分隔的话题标签 |
| `--private` | 否 | 设为仅自己可见 |

---

## Agent 工作流

1. 检查抖音配置和 token
2. 准备视频 + 标题
3. 运行 `publish_douyin.py` 脚本
4. 检查 stdout JSON 输出：
   - `{"ok": true, "item_id": "xxx", "url": "https://www.douyin.com/video/xxx"}` → 成功
   - `{"ok": false, "error": "AUTH_REQUIRED"}` → 需要完成 OAuth2 授权
   - `{"ok": false, "error": "..."}` → 其他错误

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| AUTH_REQUIRED | 无有效 OAuth2 token | 提示用户完成授权 |
| UPLOAD_FAILED | 上传失败 | 检查文件格式，重试一次 |
| PUBLISH_FAILED | 发布失败 | 检查权限和内容合规性 |
| QUOTA_EXCEEDED | API 调用频率限制 | 等待后重试 |

## 发布记录（强制）

发布成功后，**必须**立即调用 `published-track` 技能记录发布信息：

```bash
./skills/published-track/scripts/record.sh \
  --platform douyin \
  --title "标题" \
  --content-type video \
  --source-folder "<原始文件夹路径>" \
  --publish-url "<发布URL>" \
  --publish-date "$(date +%Y-%m-%d)"
```

`--source-folder` 为原始内容所在的相对路径（如 `output_articles/xxx` 或 `output_videos/xxx`）。
`--publish-url` 为发布后获得的 URL，若发布失败则留空并在 `--notes` 中注明原因。

执行 `./skills/published-track/scripts/init-db.sh`（幂等，重复执行无副作用）。
