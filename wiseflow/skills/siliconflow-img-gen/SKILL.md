---
name: siliconflow-img-gen
description: Generate images via SiliconFlow Images API (Kolors, Qwen-Image, etc.). Supports text-to-image and image editing.
homepage: https://docs.siliconflow.cn/cn/api-reference/images/images-generations
metadata:
  {
    "openclaw":
      {
        "emoji": "🖼️",
        "requires": { "bins": ["python3"], "env": ["SILICONFLOW_API_KEY"] },
        "primaryEnv": "SILICONFLOW_API_KEY",
      },
  }
---

# SiliconFlow Image Gen

Generate images using the SiliconFlow Images API.

## Run

Note: Image generation can take 10–60 seconds depending on the model and steps.
When invoking via OpenClaw's exec tool, set a higher timeout (e.g., `exec timeout=120`).

```bash
python3 {baseDir}/scripts/gen.py --prompt "your prompt here"
```

Useful flags:

```bash
# Default model (Kwai-Kolors/Kolors), square output
python3 {baseDir}/scripts/gen.py --prompt "a futuristic city at dusk"

# Portrait / landscape sizes
python3 {baseDir}/scripts/gen.py --prompt "mountain lake" --image-size 720x1280
python3 {baseDir}/scripts/gen.py --prompt "mountain lake" --image-size 1280x720

# Batch generation (Kolors only, max 4)
python3 {baseDir}/scripts/gen.py --prompt "flower field" --batch-size 3

# Control quality vs speed
python3 {baseDir}/scripts/gen.py --prompt "portrait" --steps 30 --guidance 7.5

# Use Qwen image model
python3 {baseDir}/scripts/gen.py --prompt "a serene lake" --model "Qwen/Qwen2.5-VL-72B-Instruct"

# Save to specific directory
python3 {baseDir}/scripts/gen.py --prompt "sunset" --out-dir ./out/images
```

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--prompt` | required | Text description for the image |
| `--model` | `Kwai-Kolors/Kolors` | Model ID |
| `--image-size` | `1024x1024` | Resolution: `1024x1024`, `960x1280`, `768x1024`, `720x1440`, `720x1280` |
| `--batch-size` | `1` | Number of images (1–4, Kolors only) |
| `--steps` | `20` | Inference steps (1–100) |
| `--guidance` | `7.5` | Guidance scale (0–20, Kolors only) |
| `--negative-prompt` | — | What to avoid in the image |
| `--seed` | — | Random seed for reproducibility (0–9999999999) |
| `--out-dir` | `./tmp/sf-img-<ts>` | Output directory |

## Output

- `*.png` images named by index
- `prompts.json` mapping index → prompt + URL
- `index.html` thumbnail gallery

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SILICONFLOW_API_KEY` | Your SiliconFlow API key (required) |
