---
name: pixabay-footage
description: Search and download copyright-free video clips from Pixabay API. Alternative to pexels-footage when Pexels has no suitable results.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "always": false,
        "requires": { "bins": ["python3"] },
        "requiredEnv": ["PIXABAY_API_KEY"],
      },
  }
---

# Pixabay Footage — Pexels 之外的备选视频素材

Use this skill when:
- Pexels clips are not suitable or quota is exhausted
- You need alternative copyright-free video clips
- Preparing clips for `shorts-compose --footage-dir`

**Prerequisites**: `PIXABAY_API_KEY` must be set. Register free at https://pixabay.com/api/docs/

---

## Usage

```bash
python3 {baseDir}/scripts/pixabay_search.py \
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
| Video quality | Higher (HD/4K) | Good (HD) |
| Content variety | 1M+ videos | 2M+ videos |
| Rate limits | 200 req/hour (free) | 100 req/min (free) |
| Best for | People, nature, lifestyle | Objects, abstract, concepts |

Use Pexels first; fall back to Pixabay if results are insufficient.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PIXABAY_API_KEY` | Pixabay API key (required) |
