---
name: pexels-footage
description: Search and download copyright-free images and video clips from Pexels
  API. Supports both photo search (--type image) and video search (--type video, default).
metadata:
  openclaw:
    emoji: 🎞️
    requires:
      bins:
      - python3
      env:
      - PEXELS_API_KEY
---

# Pexels Footage — 版权免费图片/视频素材下载

Use this skill when:
- You need real photos or video clips (not AI-generated) as source material
- User wants professional-looking footage or images from Pexels
- Preparing visual assets for content creation

**Prerequisites**: `PEXELS_API_KEY` must be set. Register free at https://www.pexels.com/api/

---

## Usage

### 下载图片

```bash
python3 {baseDir}/scripts/pexels_search.py \
  --type image \
  --terms "sunset ocean,mountain landscape,forest path" \
  --aspect 16:9 \
  --output-dir ./assets/images \
  [--max-clips 15]
```

### 下载视频

```bash
python3 {baseDir}/scripts/pexels_search.py \
  --type video \
  --terms "sunset ocean,mountain landscape,forest path" \
  --aspect 9:16 \
  --output-dir ./video_assets/footage \
  [--min-duration 5] \
  [--max-clips 15]
```

### Options

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

### 图片输出

```
✅ Downloaded 12 images to ./assets/images/
   pexels-sunset-ocean-abc123.jpg  (1920x1280)
   pexels-mountain-def456.jpg      (2048x1365)
   ...
```

Returns JSON to stdout:
```json
{
  "ok": true,
  "images": ["path1.jpg", "path2.jpg"],
  "total": 12,
  "output_dir": "./assets/images"
}
```

### 视频输出

```json
{
  "ok": true,
  "clips": ["path1.mp4", "path2.mp4"],
  "total": 12,
  "output_dir": "./video_assets/footage"
}
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PEXELS_API_KEY` | Pexels API key (required) |

---

## Error Handling

| Error | Action |
|-------|--------|
| `PEXELS_API_KEY not set` | Check environment variables |
| No results found for term | Try broader/simpler keywords (English works best) |
| Download fails | Retry once; skip if fails again |
| Rate limit (HTTP 429) | Wait 60s, then retry |
