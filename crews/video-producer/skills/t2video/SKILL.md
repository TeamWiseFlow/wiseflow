---
name: t2video
description: Full text-to-video pipeline (MoneyPrinterTurbo style). Accepts a topic or script, generates narration via SiliconFlow TTS, assembles video from local footage, local images, or AI-generated clips, and outputs an MP4. Designed to be called directly by users or spawned by pro-selfmedia-operator.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎥",
        "always": false,
        "requires": { "bins": ["python3"], "env": ["SILICONFLOW_API_KEY"] },
        "primaryEnv": "SILICONFLOW_API_KEY",
      },
  }
---

# t2video — 文字转视频全流水线

Use this skill when:
- The user provides a topic or script and wants a complete short video output
- pro-selfmedia-operator spawns video-producer to produce content for a specific platform
- You need finer control over materials than `shorts-compose` provides (local files, AI clips)

**Pipeline**:
```
Topic / Script
  → LLM Script (if topic given)
  → SiliconFlow TTS (audio narration)
  → Video Materials (local video / local images / AI-generated via SiliconFlow)
  → MoviePy Composition
  → MP4 + metadata.json
```

> **t2video vs shorts-compose**
> - `t2video` uses **SiliconFlow TTS** (Chinese-optimized, no external process needed)
> - `t2video` natively handles **local video/image files** as material input
> - `shorts-compose` uses edge-tts and focuses on Pexels/AI-image modes

---

## 视频剧本结构（LLM 生成脚本时必须遵循）

用 `--topic` 触发 LLM 生成脚本时，prompt 中须明确要求以下三段式结构：

| 段落 | 时长占比 | 目标 | 示例套路 |
|------|---------|------|---------|
| **开篇抓眼球** | 前 15–20% | 3 秒内让人停止划走 | "99% 的人都不知道…" / "我花了 XX 才搞明白" / 强反差开场 |
| **中段讲卖点** | 60–70% | 展示核心价值，每个卖点一句 | 场景化痛点 → 产品/方法解决 → 数据/案例佐证 |
| **结尾促下单** | 后 15–20% | 明确 CTA，降低决策门槛 | "链接在简介" / "点击立即领取" / "限时优惠只剩 XX 件" |

> 若调用方已提供完整剧本（`--script`），跳过此结构，直接使用传入内容。

---

## Prerequisites (one-time install)

```bash
pip install openai moviepy requests pillow
```

---

## Usage

### 1 — From Topic (auto-generate everything)

```bash
# default: SiliconFlow generates images as background frames
python3 {baseDir}/scripts/t2video.py \
  --topic "为什么AI正在改变每一个行业" \
  --language zh \
  --output-dir ./output_videos
```

### 2 — From Script (skip LLM step)

```bash
python3 {baseDir}/scripts/t2video.py \
  --script "人工智能正以前所未有的速度渗透到每一个行业..." \
  --language zh \
  --output-dir ./output_videos
```

### 3 — With Local Video Footage

```bash
# Use pre-downloaded .mp4 / .mov files from a directory
python3 {baseDir}/scripts/t2video.py \
  --topic "城市夜景之美" \
  --footage-dir ./assets/city_night \
  --aspect 9:16 \
  --output-dir ./output_videos
```

### 4 — With Local Images

```bash
# Slideshow from a directory of .jpg / .png files
python3 {baseDir}/scripts/t2video.py \
  --topic "春天的花朵" \
  --images-dir ./assets/spring_photos \
  --aspect 16:9 \
  --output-dir ./output_videos
```

### 5 — AI-Generated Video Clips (siliconflow-video-gen mode)

```bash
# Generates video clips via SiliconFlow Wan2.2 API for each scene
# WARNING: each clip takes 1-5 minutes — total may be 10-30 min for full video
python3 {baseDir}/scripts/t2video.py \
  --topic "深海生物的神秘世界" \
  --auto-gen-video \
  --aspect 9:16 \
  --output-dir ./output_videos
```

### 6 — Batch Generation

```bash
python3 {baseDir}/scripts/t2video.py \
  --topic "10个提升效率的方法" \
  --batch 3 \
  --output-dir ./output_videos
```

---

## All Options

```
--topic <text>          Video topic (LLM generates script from this)
--script <text>         Direct script text (skips LLM)
--language zh|en        Language for TTS (default: zh)
--aspect 9:16|16:9|1:1  Output aspect ratio (default: 9:16)

Material source (choose one; default = SiliconFlow image generation):
--footage-dir <dir>     Directory of local video clips (.mp4/.mov/.avi)
--images-dir <dir>      Directory of local image files (.jpg/.png)
--auto-gen-video        Generate video clips via SiliconFlow Video API (slow)

TTS options:
--voice <name>          SiliconFlow TTS voice name (default: FishAudio/speech-01-hd)
                        Leave empty string "" for dynamic voice

Composition:
--clip-duration <sec>   Max seconds per footage/image clip (default: 5)
--transition none|fade  Clip transitions in footage/images mode (default: none)
--n-images <N>          Number of AI images in default image mode (default: 5)
--batch <N>             Generate N versions (default: 1)
--output-dir <dir>      Output directory (required)
```

---

## Output

```
output_videos/
  2026-04-05-AI行业-1.mp4       ← final video
  2026-04-05-AI行业-1.json      ← metadata (script, terms, duration, voice, aspect)
  assets/
    audio.mp3                   ← TTS narration
    scene_*.png / clip_*.mp4    ← intermediate frames/clips
```

---

## Material Mode Decision Guide

| Situation | Recommended mode |
|-----------|-----------------|
| Have real-life footage for topic | `--footage-dir` |
| Have themed photos | `--images-dir` |
| Want highest quality AI visuals (slow) | `--auto-gen-video` |
| Quick draft / no materials | default (AI images, fast) |

---

## SiliconFlow TTS Voices (recommended)

| Voice ID | Style | Best for |
|----------|-------|---------|
| `FishAudio/speech-01-hd` | Natural, HD | General Chinese narration (default) |
| `FishAudio/speech-01-turbo` | Fast | High-volume batch generation |
| `""` (empty string) | Dynamic | Auto-selected by platform |

> **Note on TTS API**: SiliconFlow TTS uses `/v1/audio/speech` (OpenAI-compatible).
> The user-facing docs at `/audio/create-audio-transcriptions` cover speech-to-text, not TTS.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SILICONFLOW_API_KEY` | API key for LLM + TTS + image/video generation (required) |
| `LLM_API_BASE` | Override LLM endpoint (default: `https://api.siliconflow.cn/v1`) |
| `LLM_API_KEY` | Override LLM key (defaults to `SILICONFLOW_API_KEY`) |
| `LLM_MODEL` | Model name (default: `Qwen/Qwen2.5-7B-Instruct`) |

---

## Error Handling

| Error | Action |
|-------|--------|
| `SILICONFLOW_API_KEY not set` | Check environment variables |
| TTS request fails | Verify API key; try `--voice ""` for dynamic voice |
| `moviepy` not installed | `pip install moviepy` |
| `--auto-gen-video` timeout | Each clip may take up to 10 min; consider reducing scene count or using `--footage-dir` |
| No material found in directory | Check path; ensure files have correct extensions |
