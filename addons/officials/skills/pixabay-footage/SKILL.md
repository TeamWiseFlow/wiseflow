---
name: pixabay-footage
description: Search and download copyright-free images and video clips from Pixabay
  API. Alternative to pexels-footage when Pexels has no suitable results. Supports
  both photo search (--type image) and video search (--type video, default).
metadata:
  openclaw:
    emoji: 🎬
    requires:
      bins:
      - python3
      env:
      - PIXABAY_API_KEY
---

# Pixabay Footage — Pexels 之外的备选图片/视频素材

Use this skill when:
- Pexels results are not suitable or quota is exhausted
- You need alternative copyright-free images or video clips
- Preparing visual assets for content creation

**Prerequisites**: `PIXABAY_API_KEY` must be set. Register free at https://pixabay.com/api/docs/

---

## Usage

### 下载图片

```bash
python3 {baseDir}/scripts/pixabay_search.py \
  --type image \
  --terms "sunset,ocean,forest" \
  --aspect 16:9 \
  --output-dir ./assets/images \
  [--max-clips 15]
```

### 下载视频

```bash
python3 {baseDir}/scripts/pixabay_search.py \
  --type video \
  --terms "sunset,ocean,forest" \
  --aspect 9:16 \
  --output-dir ./video_assets/footage \
  [--min-duration 5] \
  [--max-clips 15]
```

Same interface as `pexels-footage`. Output format identical.

---

## When to Choose Pixabay vs Pexels

| | Pexels | Pixabay |
|-|--------|---------|
| Photo quality | High | Good |
| Photo count | 3M+ | 4M+ |
| Video quality | Higher (HD/4K) | Good (HD) |
| Video count | 1M+ | 2M+ |
| Rate limits | 200 req/hour (free) | 100 req/min (free) |
| Best for | People, nature, lifestyle | Objects, abstract, concepts |

Use Pexels first; fall back to Pixabay if results are insufficient.

---

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--terms` | required | Comma-separated search keywords (one per scene) |
| `--type` | `video` | `image` or `video` |
| `--aspect` | `9:16` | `9:16` (portrait) \| `16:9` (landscape) \| `1:1` (square) |
| `--output-dir` | required | Directory to save downloaded files |
| `--min-duration` | `5` | Minimum clip duration in seconds (video only) |
| `--max-clips` | `15` | Maximum total files to download |

---

## Output

Same JSON structure as pexels-footage:
- `--type image` → `{"ok": true, "images": [...], "total": N, "output_dir": "..."}`
- `--type video` → `{"ok": true, "clips": [...], "total": N, "output_dir": "..."}`

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PIXABAY_API_KEY` | Pixabay API key (required) |
