---
name: youtube-upload
description: Upload a video to YouTube Shorts using the browser. Handles file selection,
  title/description/tags, visibility settings, and post-upload URL retrieval.
metadata:
  openclaw:
    emoji: ▶️
---

# YouTube Shorts 上传

## 通用约束

- 视频文件上传前必须先复制到 `/tmp/openclaw/uploads/`（browser 工具沙箱限制）
- `browser upload` 工具可能返回「超时错误」，但这**不代表上传失败**！上传后用 snapshot 检查页面状态（进度条、处理状态文字）
- **不要通过检查 `input.files.length` 是否为 0 判定上传是否失败！** `input.files.length == 0` 不代表上传失败。
- 遇到 `browser failed: timed out. Restart the OpenClaw gateway ...` 错误时，**不需要重启、不需要报错**！等待 30 秒后在原页面继续操作即可。若仍无法操作，再等 30 秒；若还不行，尝试关闭浏览器后重开；只有关闭重开后仍报错才是真的出错，需停止并反馈用户。
- 标题和描述输入使用 `type` + `slowly: true`，不要用 `fill()`
- 上传进度轮询用 snapshot，不重试 click

## Workflow

```
1. cp <video_file> /tmp/openclaw/uploads/video.mp4

2. Navigate to https://studio.youtube.com
   Confirm channel dashboard loads (not login page)

3. Navigate to https://www.youtube.com/upload
   Wait for the upload dialog (timeout: 15s)

4. Upload /tmp/openclaw/uploads/video.mp4
   Poll with snapshot every 15s until progress bar disappears or shows "Processing"
   (timeout: 300s — large videos can take several minutes)

5. Fill in Title (max 100 characters)
   Fill in Description + hashtags

6. Select "No, it's not made for kids"

7. Click "Next" — wait 3s
   Click "Next" — wait 3s
   Click "Next" — wait 3s (now on Visibility page)

8. Select visibility: Public / Unlisted / Scheduled

9. Click "Publish" (or "Save")
   Wait for confirmation dialog or "Your video has been published" (timeout: 30s)

10. Navigate to https://studio.youtube.com
    Extract the video URL from the first video row
    Report the URL
```

## Metadata Source

Use the `.json` file from `shorts-compose` for title, description, and tags:

- `title` → trim to 100 characters
- `description` + `tags` → append tags as `#tag1 #tag2` at end of description

## Error Handling

| 问题 | 处理方式 |
|------|---------|
| 出现登录页 | 通知用户重新登录浏览器 |
| 视频未识别为 Shorts | 检查时长（≤60s）和比例（9:16）是否符合要求 |
