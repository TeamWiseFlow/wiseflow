---
name: shorts-compose
description: Full pipeline to generate short-form videos from topic or script. Supports AI image mode (SiliconFlow) and real footage mode (Pexels/Pixabay clips). Multiple aspect ratios, transitions, and batch generation.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "always": false,
        "requires": { "bins": ["python3"] },
        "requiredEnv": ["SILICONFLOW_API_KEY"],
        "optionalEnv": ["LLM_API_BASE", "LLM_MODEL", "EDGE_TTS_VOICE", "PEXELS_API_KEY"],
      },
  }
---

# Shorts Compose — 短视频全流水线

Use this skill when generating any short-form video. Two operating modes:

| Mode | When to use | Visual material |
|------|-------------|-----------------|
| **Image mode** (default) | No footage clips available | AI-generated images via SiliconFlow |
| **Footage mode** (`--footage-dir`) | After running `pexels-footage` or `pixabay-footage` | Real copyright-free video clips |

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
pip install edge-tts moviepy openai requests pillow
```

---

## Usage

### Image Mode (AI 图片)

```bash
python3 {baseDir}/scripts/compose.py \
  --topic "AI工具如何改变工作方式" \
  --language zh \
  --output-dir ./output_videos
```

### Footage Mode (真实视频素材)

```bash
# Step 1: Download footage
python3 {pexels_baseDir}/scripts/pexels_search.py \
  --terms "technology,office,innovation" \
  --aspect 9:16 \
  --output-dir ./video_assets/footage

# Step 2: Compose with footage
python3 {baseDir}/scripts/compose.py \
  --topic "AI工具如何改变工作方式" \
  --footage-dir ./video_assets/footage \
  --aspect 9:16 \
  --transition fade \
  --output-dir ./output_videos
```

### 16:9 Horizontal Video

```bash
python3 {baseDir}/scripts/compose.py \
  --topic "大自然风光" \
  --footage-dir ./video_assets/footage \
  --aspect 16:9 \
  --output-dir ./output_videos
```

### Batch Generation (生成多个版本，挑最佳)

```bash
python3 {baseDir}/scripts/compose.py \
  --topic "AI工具推荐" \
  --batch 3 \
  --output-dir ./output_videos
```

### All Options

```
--topic <text>          Video topic (LLM generates script)
--script <text>         Direct script (skip LLM step)
--language zh|en        Language (default: zh)
--aspect 9:16|16:9|1:1  Aspect ratio (default: 9:16)
--footage-dir <dir>     Directory of pre-downloaded video clips (enables footage mode)
--clip-duration <sec>   Max seconds per clip in footage mode (default: 5)
--transition none|fade  Clip transitions (default: none)
--n-images <N>          Number of AI images in image mode (default: 5)
--duration-hint <sec>   Target video duration hint (default: 45)
--batch <N>             Generate N videos (default: 1)
--output-dir <dir>      Output directory (required)
--assets-dir <dir>      Intermediate files dir (default: output-dir/assets)
```

---

## Output

```
output_videos/
  2026-04-05-AI工具.mp4        ← final video
  2026-04-05-AI工具.json       ← metadata

# Batch mode:
  2026-04-05-AI工具-1.mp4
  2026-04-05-AI工具-2.mp4
  2026-04-05-AI工具-3.mp4
```

Metadata JSON includes: `title`, `description`, `tags`, `duration`, `aspect`, `script`, `footage_mode`.

---

## Recommended Workflow (Footage Mode)

```
1. Choose aspect ratio based on target platform:
   - 9:16  → YouTube Shorts, TikTok, Instagram Reels, Douyin
   - 16:9  → YouTube standard, Bilibili, WeChat Video
   - 1:1   → Instagram Feed, WeChat Moments

2. Generate footage search terms from topic keywords (in English, simple nouns work best)
   e.g., topic "AI工具推荐" → terms "technology,computer,work,office"

3. Run pexels-footage (or pixabay-footage if Pexels has no results)

4. Run shorts-compose with --footage-dir

5. If batch mode: show user all N videos, ask which to keep/publish
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SILICONFLOW_API_KEY` | API key for LLM + image gen | **Required** |
| `LLM_API_BASE` | Override LLM endpoint | `https://api.siliconflow.cn/v1` |
| `LLM_API_KEY` | Override LLM key | `SILICONFLOW_API_KEY` |
| `LLM_MODEL` | Model name | `Qwen/Qwen2.5-7B-Instruct` |
| `EDGE_TTS_VOICE` | TTS voice | auto by language |

**Default TTS voices**: `zh-CN-YunxiNeural` (Chinese) · `en-US-GuyNeural` (English)

---

## Error Handling

| Error | Action |
|-------|--------|
| `SILICONFLOW_API_KEY not set` | Check environment |
| `edge-tts` / `moviepy` not found | `pip install edge-tts moviepy` |
| No clips in footage-dir | Falls back to placeholder image, continues |
| Image generation fails | Uses placeholder image, continues |
| Batch: some videos fail | Reports per-video status, exits 1 only if all fail |
