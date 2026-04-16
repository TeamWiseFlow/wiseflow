---
name: wxwork-moments
description: Publish content (text + images/video/link) to WeChat Work (企业微信) customer moments. Supports local mode (IP whitelisted) and relay mode via tx-relay proxy.
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
        "requires": { "bins": ["curl"] },
        "optionalEnv": ["WXWORK_CORP_ID", "WXWORK_CORP_SECRET", "WXWORK_PROXY_URL", "WENYAN_API_KEY"],
      },
  }
---

# WeChat Work Moments Publisher（企业微信朋友圈发布）

支持两种发布模式，根据环境变量自动选择：

| 模式 | 条件 | 数据流 |
|------|------|--------|
| **本地直连** | 设置了 `WXWORK_CORP_ID` + `WXWORK_CORP_SECRET`，且本机 IP 已加入企业微信可信 IP | Agent → 企业微信 API |
| **Relay 中转** | 设置了 `WXWORK_PROXY_URL`（固定 IP 服务器） | Agent → tx-relay → 企业微信 API |

---

## 环境变量

| 变量 | 模式 | 说明 |
|------|------|------|
| `WXWORK_CORP_ID` | 本地直连 | 企业 ID |
| `WXWORK_CORP_SECRET` | 本地直连 | 应用 Secret |
| `WXWORK_PROXY_URL` | Relay 中转 | tx-relay 地址，如 `http://123.60.11.251:3001` |
| `WENYAN_API_KEY` | Relay 中转 | 代理服务鉴权 Key |

---

## 模式选择逻辑

```bash
if [ -n "$WXWORK_CORP_ID" ] && [ -n "$WXWORK_CORP_SECRET" ]; then
  MODE=local   # 本地直连
elif [ -n "$WXWORK_PROXY_URL" ]; then
  MODE=relay   # Relay 中转
else
  echo "ERROR: 需要设置 (WXWORK_CORP_ID + WXWORK_CORP_SECRET) 或 WXWORK_PROXY_URL"
  exit 1
fi
```

---

## 发布流程

### 步骤 1：上传图片/视频，获取 media_id

#### 本地直连模式

```bash
# 获取 access_token
TOKEN=$(curl -sf "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=${WXWORK_CORP_ID}&corpsecret=${WXWORK_CORP_SECRET}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 上传图片
MEDIA=$(curl -sf -X POST \
  "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=${TOKEN}&type=image" \
  -F "media=@/path/to/image.jpg")
MEDIA_ID=$(echo $MEDIA | python3 -c "import sys,json; print(json.load(sys.stdin)['media_id'])")
```

#### Relay 中转模式

```bash
# 上传图片（支持 jpg/png，最大 10MB）
MEDIA=$(curl -sf -X POST "${WXWORK_PROXY_URL}/wxwork/media/upload" \
  -H "x-api-key: ${WENYAN_API_KEY}" \
  -F "media=@/path/to/image.jpg" \
  -F "type=image")
MEDIA_ID=$(echo $MEDIA | python3 -c "import sys,json; print(json.load(sys.stdin)['media_id'])")

# 上传视频（最大 10MB，时长 ≤ 30 秒）
MEDIA=$(curl -sf -X POST "${WXWORK_PROXY_URL}/wxwork/media/upload" \
  -H "x-api-key: ${WENYAN_API_KEY}" \
  -F "media=@/path/to/video.mp4" \
  -F "type=video")
MEDIA_ID=$(echo $MEDIA | python3 -c "import sys,json; print(json.load(sys.stdin)['media_id'])")
```

### 步骤 2：发布朋友圈

#### 本地直连模式

```bash
# 纯文字
curl -sf -X POST \
  "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_moment_task?access_token=${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"text": {"content": "正文内容"}}'

# 图文（最多 9 张图）
curl -sf -X POST \
  "https://qyapi.weixin.qq.com/cgi-bin/externalcontact/add_moment_task?access_token=${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": {\"content\": \"正文内容\"},
    \"attachments\": [
      {\"msgtype\": \"image\", \"image\": {\"media_id\": \"$MEDIA_ID\"}}
    ]
  }"
```

#### Relay 中转模式

```bash
# 纯文字
curl -sf -X POST "${WXWORK_PROXY_URL}/wxwork/moments/add" \
  -H "x-api-key: ${WENYAN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"text": {"content": "正文内容"}}'

# 图文（最多 9 张图）
curl -sf -X POST "${WXWORK_PROXY_URL}/wxwork/moments/add" \
  -H "x-api-key: ${WENYAN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": {\"content\": \"正文内容\"},
    \"attachments\": [
      {\"msgtype\": \"image\", \"image\": {\"media_id\": \"$MEDIA_ID\"}}
    ]
  }"

# 图文链接
curl -sf -X POST "${WXWORK_PROXY_URL}/wxwork/moments/add" \
  -H "x-api-key: ${WENYAN_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": {\"content\": \"推荐阅读\"},
    \"attachments\": [{
      \"msgtype\": \"link\",
      \"link\": {
        \"title\": \"文章标题\",
        \"url\": \"https://example.com/article\",
        \"media_id\": \"$COVER_MEDIA_ID\"
      }
    }]
  }"
```

---

## 附件限制

| 附件类型 | 限制 |
|---------|------|
| `image`（图片） | 最多 9 个 |
| `video`（视频） | 最多 1 个，时长 ≤ 30 秒，大小 ≤ 10MB |
| `link`（图文链接） | 最多 1 个 |
| 图片与视频/链接 | 不可同时存在 |

---

## 可见范围（可选）

```bash
# 仅向指定员工的客户可见，并按标签筛选（两种模式均支持此 body 结构）
-d '{
  "text": {"content": "内容"},
  "visible_range": {
    "sender_list": { "user_list": ["zhangsan", "lisi"] },
    "external_contact_list": { "tag_list": ["etXXXXXXXX"] }
  }
}'
```

---

## 返回值

```json
{ "ok": true, "moment_id": "xxxxxxxxxxxxxxxx", "detail": { "errcode": 0, "errmsg": "ok" } }
```

Relay 模式返回上述结构；本地直连模式直接返回企业微信原始响应（含 `errcode`/`errmsg`）。

---

## Error Handling

| 错误 | 原因 | 处理 |
|------|------|------|
| `invalid ip` | 本机/服务器 IP 未加入企业微信可信 IP | 在企业微信后台添加 IP；或改用 Relay 模式 |
| `401 Unauthorized` | `x-api-key` 不正确（Relay 模式） | 检查 `WENYAN_API_KEY` |
| `no privilege` | 应用未开通客户联系权限 | ��企业微信后台为应用开通权限 |
| `invalid attachments size` | 图片超过 9 张 | 减少图片数量 |

---

## Notes

- 朋友圈任务创建成功后，指定员工会在企业微信中收到一键发布提醒
- `moment_id` 可用于后续查询发布状态（企业微信管理后台 → 客户联系 → 客户朋友圈）
- 临时素材（media_id）有效期 **3 天**，过期需重新上传
