---
name: siliconflow-img-gen
description: Generate or edit images via SiliconFlow Images API. Text-to-image uses
  Qwen/Qwen-Image; image-edit uses Qwen/Qwen-Image-Edit-2509.
metadata:
  openclaw:
    emoji: 🖼️
    requires:
      bins:
      - python3
      env:
      - SILICONFLOW_API_KEY
    primaryEnv: SILICONFLOW_API_KEY
    homepage: https://docs.siliconflow.cn/cn/api-reference/images/images-generations
---

# SiliconFlow Image Gen

Generate or edit images using the SiliconFlow Images API.

Two modes:
- **Text-to-image** — default model `Qwen/Qwen-Image`（if rate limit exceeded, falls back to `baidu/ERNIE-Image-Turbo`）
- **Image-edit** — default model `Qwen/Qwen-Image-Edit-2509`，由 `--image` 参数触发

## Run

Note: Image generation can take 10–60 seconds. Set a higher timeout when invoking via exec (e.g., `exec timeout=120`).

**Do NOT set env vars inline** (e.g., `SILICONFLOW_API_KEY=... python3 ...`). The env var is already in the system environment; inline assignments break the exec permission check.

```bash
# Text-to-image (default model: Qwen/Qwen-Image)
python3 {baseDir}/scripts/gen.py --prompt "your prompt here"

# if rate limit exceeded, falls back to `baidu/ERNIE-Image-Turbo`
python3 {baseDir}/scripts/gen.py --prompt "your prompt here" --model "baidu/ERNIE-Image-Turbo"

# Image-edit (default model: Qwen/Qwen-Image-Edit-2509)
python3 {baseDir}/scripts/gen.py --prompt "add a lighthouse" --image "https://example.com/source.jpg"
```

### Text-to-image examples

```bash
# Square output (default)
python3 {baseDir}/scripts/gen.py --prompt "a futuristic city at dusk"

# Landscape 16:9
python3 {baseDir}/scripts/gen.py --prompt "mountain lake" --image-size 1664x928

# Portrait 9:16
python3 {baseDir}/scripts/gen.py --prompt "mountain lake" --image-size 928x1664

# Enable CFG (useful when prompt contains text to render)
python3 {baseDir}/scripts/gen.py --prompt "a sign saying HELLO" --cfg 4.0 --steps 50

# Save to specific directory
python3 {baseDir}/scripts/gen.py --prompt "sunset" --out-dir ./out/images
```

### Image-edit examples

```bash
# Edit with a single source image
python3 {baseDir}/scripts/gen.py \
  --prompt "make it night time" \
  --image "https://example.com/photo.jpg"

# Edit with up to three source images
python3 {baseDir}/scripts/gen.py \
  --prompt "blend these photos" \
  --image  "https://example.com/a.jpg" \
  --image2 "https://example.com/b.jpg" \
  --image3 "https://example.com/c.jpg"
```

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--prompt` | required | Text description for the image |
| `--model` | auto | Model ID; auto-selected by mode if omitted |
| `--image-size` | `1328x1328` | Resolution (text-to-image only, see valid values below) |
| `--steps` | `20` | Inference steps (1–100) |
| `--cfg` | — | CFG scale (0.1–20). Qwen recommends 4.0 when generating text in image; must be >1 for text generation |
| `--seed` | — | Random seed (0–9999999999) |
| `--image` | — | Source image URL — **enables image-edit mode** |
| `--image2` | — | Second source image URL (edit mode only) |
| `--image3` | — | Third source image URL (edit mode only) |
| `--out-dir` | `./tmp/sf-img-<ts>` | Output directory |

### Valid `--image-size` values (Qwen/Qwen-Image)

| Value | Ratio |
|-------|-------|
| `1328x1328` | 1:1 (default) |
| `1664x928` | 16:9 |
| `928x1664` | 9:16 |
| `1472x1140` | 4:3 |
| `1140x1472` | 3:4 |
| `1584x1056` | 3:2 |
| `1056x1584` | 2:3 |

## Output

- `*.png` images named by index
- `prompts.json` mapping index → prompt + URL
- `index.html` thumbnail gallery

## ⚠️ 生成后必须验证

SiliconFlow 图片生成经常出现异常：返回一张**纯色背景图**（单色无内容），而非 prompt 要求的图像。

**每张图生成后必须执行验证，不得跳过。**

### 验证流程

1. 图片生成后，立即用 `image` 工具查看刚生成的图片
2. 判断图片是否正常：
   - ❌ **异常**：整张图是纯色背景（全黑/全白/全灰/全蓝等），没有任何主体内容 → **重新生成**
   - ✅ **正常**：图片有明确的主体内容，符合 prompt 描述 → 继续下一步
3. 如果重新生成，最多重试 3 次，仍异常则标记失败并继续后续任务
