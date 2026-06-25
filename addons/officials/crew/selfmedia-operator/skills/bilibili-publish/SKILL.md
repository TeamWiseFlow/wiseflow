---
name: bilibili-publish
description: Publish videos to Bilibili (B站) via Open Platform API (OAuth2).
  Supports chunked video upload, cover image, tags, and partition selection.
  Requires BILIBILI_APP_ID and BILIBILI_APP_SECRET environment variables.
metadata:
  openclaw:
    emoji: 📺
    requires:
      bins:
      - python3
---

# B站视频发布（bilibili-publish）

通过 B站开放平台 API（OAuth2 + HMAC-SHA256 签名）上传发布视频，支持分块上传、封面、分区和标签。

> ⚠️ 本技能使用 B站开放平台 OAuth2 API（`member.bilibili.com/arcopen/`），非 Web 创作中心 API。
> 需要在 [B站开放平台](https://open.bilibili.com/) 申请 app_key/app_secret。

---

## 前置条件

1. 环境变量 `BILIBILI_APP_ID` 和 `BILIBILI_APP_SECRET` 已配置（B站开放平台凭据）
2. OAuth2 授权已完成（`~/.openclaw/logins/bilibili-oauth.json` 存在且有效）
3. 若 token 过期，脚本会自动尝试 refresh；若 refresh 也失败，需重新授权

---

## OAuth2 授权流程（首次使用）

1. 获取授权页面 URL：
   ```
   https://account.bilibili.com/pc/account-pc/auth/oauth?client_id=${BILIBILI_APP_ID}&gourl=${REDIRECT_URL}&state=random
   ```
2. 用户在浏览器中打开该 URL，扫码登录并授权
3. 授权后回调 URL 中获取 `code` 参数
4. 交换 token：
   ```bash
   python3 ./skills/bilibili-publish/scripts/publish_bilibili.py --exchange-token <code>
   ```
5. Token 保存在 `~/.openclaw/logins/bilibili-oauth.json`

---

## 使用方式

```bash
python3 ./skills/bilibili-publish/scripts/publish_bilibili.py \
  --title "视频标题" \
  --video video.mp4 \
  --tid 122 \
  --tags AI,科技,工具
```

带封面和描述：

```bash
python3 ./skills/bilibili-publish/scripts/publish_bilibili.py \
  --title "视频标题" \
  --video video.mp4 \
  --cover cover.jpg \
  --desc "视频描述" \
  --tid 122 \
  --tags AI,科技
```

---

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | 是 | 视频标题，最多 80 字 |
| `--video` | 是 | 视频文件路径，支持 mp4 |
| `--cover` | 否 | 封面图路径；不提供则 B站自动截取 |
| `--desc` | 否 | 视频描述 |
| `--tid` | 否 | 分区 ID，默认 122（野生技术协会） |
| `--tags` | 是 | 逗号分隔的标签，最多 10 个，每个最多 20 字 |
| `--copyright` | 否 | 1=自制（默认），2=转载 |
| `--exchange-token` | 否 | OAuth2 授权码交换模式 |

---

## 常用分区 ID

| tid | 分区 |
|-----|------|
| 122 | 野生技术协会 |
| 36 | 知识 · 科技 |
| 95 | 数码 |
| 207 | 资讯 |
| 21 | 日常 |
| 76 | 美食制作 |

---

## Agent 工作流

1. 确认 `BILIBILI_APP_ID` 和 `BILIBILI_APP_SECRET` 环境变量已设置
2. 准备视频文件 + 标题 + 分区 + 标签
3. 运行 `publish_bilibili.py` 脚本（自动完成上传+提交）
4. 检查 stdout JSON 输出：
   - `{"ok": true, "bvid": "BVxxx", "url": "..."}` → 成功
   - `{"ok": false, "error": "CREDENTIALS_MISSING"}` → 需配置环境变量
   - `{"ok": false, "error": "AUTH_REQUIRED"}` → 需完成 OAuth2 授权流程
   - `{"ok": false, "error": "AUTH_EXPIRED"}` → 需重新授权
   - `{"ok": false, "error": "..."}` → 其他错误，反馈用户

---

## 错误处理

| 错误 | 原因 | 处理 |
|------|------|------|
| CREDENTIALS_MISSING | 环境变量未配置 | 设置 BILIBILI_APP_ID 和 BILIBILI_APP_SECRET |
| AUTH_REQUIRED | 无 OAuth token | 完成 OAuth2 授权流程 |
| AUTH_EXPIRED | token 过期且刷新失败 | 重新走授权流程获取新 code |
| UPLOAD_FAILED | 上传失败 | 检查网络和文件大小，重试一次 |
| SUBMIT_FAILED | 提交失败 | 检查分区和标签是否合法 |
