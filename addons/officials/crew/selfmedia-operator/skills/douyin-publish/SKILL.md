---
name: douyin-publish
description: Publish content to Douyin (抖音) via open platform H5 Schema.
  Generates a schema URL to open Douyin app's publish page. Supports video,
  images, album, hashtags, privacy, note mode, and forward-to-daily. Requires
  Douyin open platform web app credentials.
metadata:
  openclaw:
    emoji: 🎤
    requires:
      bins:
      - python3
---

# 抖音内容发布（douyin-publish）

通过抖音开放平台 H5 Schema 发布内容（视频/图片/图集），生成 schema URL 唤起抖音 App 完成发布。

---

## 前置条件

1. 在 [抖音开放平台](https://open.douyin.com) 创建**网页应用**，获取 `client_key` / `client_secret`
2. 申请 `h5.share` 能力权限（H5 场景分享/发布）
3. 投稿能力（抖音 30.5.0+）：额外申请 `aweme.share` 权限
4. 转发到日常能力（抖音 30.5.0+）：额外申请 `aweme.forward` 权限

> **H5 Schema 方式不需要用户 OAuth2 授权**，使用 client_token（client_credential 授予）即可生成 schema。用户在手机端打开 schema 后由抖音 App 处理发布。

---

## 配置

保存到 `~/.openclaw/credentials/douyin_config.json`：

```json
{
  "client_key": "your_client_key",
  "client_secret": "your_client_secret"
}
```

---

## 使用方式

```bash
python3 ./skills/douyin-publish/scripts/publish_douyin.py \
  --title "视频标题" \
  --video "https://example.com/video.mp4" \
  --tags 话题1,话题2
```

图集模式：

```bash
python3 ./skills/douyin-publish/scripts/publish_douyin.py \
  --title "图文标题" \
  --images "https://example.com/img1.jpg,https://example.com/img2.jpg" \
  --tags 话题1
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | 是 | 内容标题 |
| `--video` | 否* | 视频 URL（公网可访问，mp4/mov，≤128M） |
| `--image` | 否* | 单张图片 URL（png/jpg/gif，≤20M） |
| `--images` | 否* | 逗号分隔的图片 URL（图集模式，png/jpg，抖音 22.2.0+） |
| `--tags` | 否 | 逗号分隔的话题标签 |
| `--short-title` | 否 | 短标题（抖音 30.0.0+） |
| `--private-status` | 否 | 可见范围：0=公开，1=仅自己，2=好友可见（抖音 30.0.0+） |
| `--download-type` | 否 | 下载控制：1=允许，2=不允许（抖音 30.0.0+） |
| `--share-to-type` | 否 | 发布类型：0=投稿，1=转发到日常（抖音 25.4.0+） |
| `--poi-id` | 否 | 地理位置 POI ID（抖音 22.2.0+） |
| `--feature` | 否 | 设为 `note` 启用笔记模式（抖音 30.3.0+，仅多图） |

*\*`--video`、`--image`、`--images` 至少提供一个。`--video` 优先于图片参数。*

> **重要**：`--video` / `--image` / `--images` 均为**公网可访问的 URL**，不是本地文件路径。需先将媒体文件上传到可公网访问的位置。

---

## Agent 工作流

1. 检查抖音配置（`douyin_config.json`）
2. 确保视频/图片已上传到公网可访问的 URL
3. 运行 `publish_douyin.py` 脚本
4. 检查 stdout JSON 输出：
   - `{"ok": true, "schema_url": "snssdk1128://...", "share_id": "xxx"}` → 成功生成 schema
   - `{"ok": false, "error": "CONFIG_MISSING"}` → 需要配置凭据
   - `{"ok": false, "error": "..."}` → 其他错误
5. 将 `schema_url` 提供给用户，用户在手机上打开（扫码或点击链接）
6. 用户在抖音 App 中确认发布
7. 可通过 `share_id` 调用「查询视频分享结果」API 获取发布状态

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| CONFIG_MISSING | 无 douyin_config.json | 创建配置文件 |
| CONFIG_INVALID | 缺少 client_key 或 client_secret | 补全配置 |
| CLIENT_TOKEN_FAILED | 获取 client_token 失败 | 检查凭据是否正确、应用是否审核通过 |
| TICKET_FAILED | 获取 ticket 失败 | 检查应用是否审核通过、h5.share 权限是否已申请 |
| SHARE_ID_FAILED | 获取 share_id 失败 | 检查 h5.share 权限 |
| MISSING_MEDIA | 未提供视频或图片 | 至少提供一种媒体内容 |
