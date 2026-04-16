---
name: pexels-footage
description: Search and download copyright-free video clips from Pexels API. Clips are downloaded to a local directory for use by shorts-compose (--footage-dir mode).
metadata:
  {
    "openclaw":
      {
        "emoji": "🎞️",
        "always": false,
        "requires": { "bins": ["python3"] },
        "requiredEnv": ["PEXELS_API_KEY"],
      },
  }
---

# Pexels Footage — 版权免费视频素材下载

Use this skill when:
- You need real video clips (not AI images) as source material for a video
- User wants professional-looking footage from Pexels
- You are preparing clips for `shorts-compose --footage-dir`

**Prerequisites**: `PEXELS_API_KEY` must be set. Register free at https://www.pexels.com/api/

---

## Usage

```bash
python3 {baseDir}/scripts/pexels_search.py \
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
| `--aspect` | `9:16` | `9:16` (portrait) \| `16:9` (landscape) \| `1:1` (square) |
| `--output-dir` | required | Directory to save downloaded clips |
| `--min-duration` | `5` | Minimum clip duration in seconds |
| `--max-clips` | `15` | Maximum total clips to download |

---

## Output

```
✅ Downloaded 12 clips to ./video_assets/footage/
   pexels-sunset-ocean-abc123.mp4  (8s)
   pexels-mountain-def456.mp4      (12s)
   ...
```

Returns JSON to stdout:
```json
{
  "ok": true,
  "clips": ["path1.mp4", "path2.mp4"],
  "total": 12,
  "output_dir": "./video_assets/footage"
}
```

---

## After Downloading

Use with `shorts-compose`:
```bash
python3 {shorts_compose_baseDir}/scripts/compose.py \
  --topic "主题" \
  --footage-dir ./video_assets/footage \
  --aspect 9:16 \
  --output-dir ./output_videos
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
| No clips found for term | Try broader/simpler keywords (English works best) |
| Download fails | Retry once; skip if fails again |
| Rate limit (HTTP 429) | Wait 60s, then retry |
