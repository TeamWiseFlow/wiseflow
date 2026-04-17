---
name: viral-chaser
description: Download and analyze viral videos from Douyin/Bilibili/Kuaishou. Generates a trend-chasing report (viral element breakdown, visual style analysis) and a ready-to-use script outline compatible with shorts-compose and t2video.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎯",
        "always": false,
        "requires": { "bins": ["node", "ffmpeg"] },
        "requiredEnv": ["SILICONFLOW_API_KEY"],
      },
  }
---

# Viral Chaser（追爆分析）

Use this skill when:
- A user provides a Douyin / Bilibili / Kuaishou video link and wants to create a similar viral video
- You need to analyze the structure and formula of a trending video
- You need a script outline based on a reference video

**Supported platforms:** 抖音（Douyin）、B 站（Bilibili）、快手（Kuaishou）

**Not supported:** 小红书（XHS）、微信视频号、TikTok

---

## Workflow

### Step 1 — Check login (skip for public Bilibili videos)

```
Run: login-manager check <platform>
```

- `platform`: `douyin` | `bilibili` | `kuaishou`
- If the result is `SESSION_EXPIRED` (exit code 2), run `login-manager login <platform>` first

### Step 2 — Run the analyzer

```bash
node {baseDir}/scripts/viral_chaser.ts <url> [--no-frames]
```

- `<url>`: Full or short-link URL of the video
- `--no-frames`: Skip key frame extraction (faster, audio-only analysis)

The script outputs a **JSON object to stdout**. Read it and proceed with analysis.

**Output JSON structure:**
```json
{
  "ok": true,
  "platform": "douyin",
  "metadata": {
    "contentId": "...",
    "title": "...",
    "desc": "...",
    "author": "...",
    "durationSeconds": 89,
    "coverUrl": "...",
    "stats": { "playCount": 0, "likeCount": 0, "commentCount": 0 }
  },
  "transcript": {
    "text": "全文转录...",
    "segments": [{ "start": 0.0, "end": 5.2, "text": "开场文案" }]
  },
  "frames": ["/tmp/viral_chaser/{id}/frames/frame_00_0s.jpg", "..."],
  "localPaths": {
    "video": "/tmp/viral_chaser/{id}/video.mp4",
    "audio": "/tmp/viral_chaser/{id}/audio.wav",
    "tmpDir": "/tmp/viral_chaser/{id}"
  }
}
```

**Exit codes:**
- `0` = Success
- `1` = Error (URL invalid, download failed, etc.) — report to user
- `2` = Cookie expired — run `login-manager login <platform>`, then retry once

### Step 3 — Read key frames (if available)

For each path in `frames`, use the `Read` tool to load the image and analyze it visually.

```
Read: /tmp/viral_chaser/{id}/frames/frame_00_0s.jpg
Read: /tmp/viral_chaser/{id}/frames/frame_01_3s.jpg
...
```

---

## Analysis Framework

After receiving the JSON output and reading the frames, generate a **追爆报告** in Markdown.

### 1. 内容摘要
1–2 sentences: what core value does this video deliver to viewers?

### 2. 开头钩子分析（前 0–10 秒）
Based on `transcript.segments` where `start < 10`:
- **钩子类型**: 提问型 / 冲突型 / 反转型 / 数字型 / 悬念型 / 痛点型 / 利益型
- **具体文案**: quote the exact opening line(s)
- **效果评估**: why this hook works (or doesn't)

### 3. 内容结构拆解
Based on transcript segments, divide into logical sections:

| 段落 | 时间区间 | 功能 | 核心内容 |
|------|---------|------|---------|
| 开场 | 0–Xs | 钩子/引入 | ... |
| 主体一 | X–Ys | 价值/信息传递 | ... |
| 主体二 | Y–Zs | 深化/转折 | ... |
| 收尾 | Z–结束 | CTA/情绪收尾 | ... |

### 4. 爆款元素评估
Rate each element as **强 / 中 / 弱** with a one-line explanation:

| 元素 | 评级 | 说明 |
|------|:----:|------|
| 前 3 秒吸引力 | | |
| 痛点共鸣度 | | |
| 悬念设置 | | |
| 情绪触发 | | |
| 价值清晰度 | | |
| CTA 效果 | | |
| 视觉冲击（基于关键帧） | | |
| 节奏把控 | | |

### 5. 视觉风格分析（基于关键帧图片）
After reading the frame images:
- **色调风格**: 暖色系/冷色系/高饱和/低饱和/黑白
- **构图类型**: 人脸近景 / 产品展示 / 场景空镜 / 文字卡片 / 混合
- **字幕/文字覆盖**: 字体粗细、位置、是否有背景框、动画感
- **整体视觉标签**: 3–5 个关键词（如：「真实感」「强对比」「高信息密度」）

If `--no-frames` was used or frames is empty, note: "（跳过视觉分析，请重新运行不带 --no-frames 参数）"

### 6. 可借鉴点
3–5 concise, directly actionable techniques. One sentence each.

### 7. 目标受众
One sentence describing the primary audience persona.

---

## Script Generation

After completing the 追爆报告, ask the user:

> "追爆报告已完成。接下来，我可以基于此视频的公式为您生成新脚本大纲。请告诉我：
> 1. 新视频的主题/产品/角度（或直接回复"按原主题"）
> 2. 风格偏好：仿写（保留框架换内容）/ 改写（重组表达）/ 创新（仅借鉴钩子类型）"

Then generate the script outline in this format:

```
【追爆脚本大纲】
来源参考：{platform} - {title}

▍标题备选（5 个，风格各异）
1. ...
2. ...
3. ...
4. ...
5. ...

▍开场钩子（0–8s）
文案：...
画面建议：...

▍主体段一（8–40s）
文案：...
画面素材关键词（用于 pexels-footage 搜索）：...

▍主体段二（40–70s）
文案：...
画面素材关键词：...

▍收尾/CTA（70–90s）
文案：...
画面建议：...

▍制作建议
BGM 风格：...
字幕风格：...
视觉色调：...
```

After generating the outline, ask:
> "脚本大纲已就绪。要直接用 `shorts-compose` 制作，还是先调整脚本？"

If the user confirms, pass the script to `shorts-compose --script "<outline>"` or `t2video --script "<outline>"`.

---

## Notes

- **Temporary files** are stored in `/tmp/viral_chaser/{contentId}/` — they are NOT automatically cleaned up so you can re-read frames without re-downloading. Clean up manually with `rm -rf /tmp/viral_chaser/` when done.
- **Bilibili DASH format**: if `mediaFormat` is `DASH`, the video and audio streams are separate. The downloaded `video.mp4` contains the video stream only; audio is in `audio.wav` after extraction. This is transparent to the analysis workflow.
- **Cookie refresh**: if the script exits with code 2 mid-workflow, run `login-manager login <platform>` and retry. Do not retry more than once.
