---
name: wxwork-moments
description: Publish content (text + images/video/link) to WeChat Work (企业微信) customer
  moments via a single bash script. Supports local mode (IP whitelisted) and relay
  mode via tx-relay proxy.
metadata:
  openclaw:
    emoji: 📱
    requires:
      bins:
      - python3
---

# WeChat Work Moments Publisher（企业微信朋友圈发布）

---

## 发布命令

所有发布操作均通过同一脚本完成，脚本路径：`./skills/wxwork-moments/scripts/post_moments.py`

### 纯文字

```bash
python3 ./skills/wxwork-moments/scripts/post_moments.py "正文内容"
```

### 图文（最多 9 张图）

```bash
python3 ./skills/wxwork-moments/scripts/post_moments.py "正文内容" /path/to/img1.jpg /path/to/img2.png
```

### 视频（1 个，≤ 30 秒，≤ 10MB）

```bash
python3 ./skills/wxwork-moments/scripts/post_moments.py "正文内容" /path/to/video.mp4
```

### 图文链接（必须传封面图）

> ⚠️ **重要**：链接模式**必须**附封面图，否则发布失败。不存在不传封面图的模式。

```bash
python3 ./skills/wxwork-moments/scripts/post_moments.py "推荐阅读" --link https://example.com/article "文章标题" /path/to/cover.jpg
```

---

## Agent 行为约束

> 以下规则**严格执行**，不得跳过。

1. **等待脚本完整返回后**再进行下一步，脚本包含上传和发布两个网络请求，耗时可能超过 10 秒，期间告知用户"正在上传素材 / 正在发布……"，**禁止**在脚本结束前自行拼接其他 curl 命令。
2. 脚本已处理模式判断、token 获取、素材上传、media_id 记录、发布等全部步骤，**无需**手动执行任何中间步骤。
3. 脚本输出最后一行若以 `✓` 开头表示成功；以 `✗` 开头表示失败，需将错误信息完整告知用户。
4. 正文中不要包含换行“\n”, wxwork api 不能解析“\n”

---

## 附件限制速查

| 附件类型 | 限制 |
|---------|------|
| 图片（jpg/png/gif） | 最多 9 个 |
| 视频（mp4/mov）     | 最多 1 个，时长 ≤ 30 秒，大小 ≤ 10MB |
| 图文链接            | 最多 1 个，可附 1 张封面图 |
| 图片与视频/链接      | 不可同时存在 |

---

## Error Handling

| 错误信息 | 原因 | 处理 |
|---------|------|------|
| `请配置环境变量` | 两组环境变量均未配置 | 在系统环境或 crew 配置中添加对应变量 |
| `invalid ip` | 本机 IP 未加入企业微信可信 IP | 后台添加 IP；或改用 relay 模式（配置 `WXWORK_PROXY_URL`） |
| `401 Unauthorized` | relay 模式 api_key 错误 | 检查 `WENYAN_API_KEY` |
| `no privilege` | 应用未开通客户联系权限 | 企业微信后台为应用开通权限 |
| `图片最多 9 张` | 超出数量限制 | 减少传入文件数量 |

---

## Notes

- 朋友圈任务创建成功后，指定员工会在企业微信中收到一键发布提醒
- `moment_id` 可用于后续在企业微信管理后台（客户联系 → 客户朋友圈）查询发布状态
- 临时素材（media_id）有效期 **3 天**，脚本每次发布时重新上传，无需手动管理

---

企业微信朋友圈分发无需执行 `published-track` 相关操作。
