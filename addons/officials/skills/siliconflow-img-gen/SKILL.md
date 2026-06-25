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
- **Text-to-image** — default model `Qwen/Qwen-Image`; on HTTP 403/404/429/500/503/504, automatically retries with `baidu/ERNIE-Image-Turbo`
- **Image-edit** — default model `Qwen/Qwen-Image-Edit-2509`，由 `--image` 参数触发

> 📍 **全局技能路径提示**：文中所有 `./scripts/` 路径均相对于本技能所在目录（即 `<skill>` 标签 `location` 属性所指目录），**不是**工作区目录。执行时按本技能实际安装路径拼接。

## Run

Note: Image generation can take 10–60 seconds. Set a higher timeout when invoking via exec (e.g., `exec timeout=120`).

**Do NOT set env vars inline** (e.g., `SILICONFLOW_API_KEY=... python3 ...`). The env var is already in the system environment; inline assignments break the exec permission check.

```bash
# Text-to-image (default model: Qwen/Qwen-Image)
python3 ./scripts/gen.py --prompt "your prompt here"

# Manually specify ERNIE-Image-Turbo (also used as auto-fallback on 403/404/429/500/503/504)
python3 ./scripts/gen.py --prompt "your prompt here" --model "baidu/ERNIE-Image-Turbo"

# Image-edit (default model: Qwen/Qwen-Image-Edit-2509)
python3 ./scripts/gen.py --prompt "add a lighthouse" --image "https://example.com/source.jpg"
```

### Text-to-image examples

```bash
# Square output (default)
python3 ./scripts/gen.py --prompt "a futuristic city at dusk"

# Landscape 16:9
python3 ./scripts/gen.py --prompt "mountain lake" --image-size 1664x928

# Portrait 9:16
python3 ./scripts/gen.py --prompt "mountain lake" --image-size 928x1664

# Enable CFG (useful when prompt contains text to render)
python3 ./scripts/gen.py --prompt "a sign saying HELLO" --cfg 4.0 --steps 50

# Save to specific directory
python3 ./scripts/gen.py --prompt "sunset" --out-dir ./out/images
```

### Image-edit examples

```bash
# Edit with a single source image
python3 ./scripts/gen.py \
  --prompt "make it night time" \
  --image "https://example.com/photo.jpg"

# Edit with up to three source images
python3 ./scripts/gen.py \
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
| `--image-size` | `1328x1328` | Resolution (text-to-image only, **must be one of the valid values below** — invalid values will cause an error with the closest valid suggestion) |
| `--steps` | `20` | Inference steps (1–100) |
| `--cfg` | — | CFG scale (0.1–20). Qwen recommends 4.0 when generating text in image; must be >1 for text generation |
| `--seed` | — | Random seed (0–9999999999) |
| `--negative-prompt` | — | Concepts to exclude, not necessary|
| `--image` | — | Source image URL — **enables image-edit mode** |
| `--image2` | — | Second source image URL (edit mode only) |
| `--image3` | — | Third source image URL (edit mode only) |
| `--out-dir` | `./tmp/sf-img-<ts>` | Output directory |

### Valid `--image-size` values (Qwen/Qwen-Image)

> **Invalid sizes are rejected** — the script exits with an error listing all valid options and suggesting the closest match by aspect ratio. Re-run with a valid `--image-size`.

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

## 视频封面/海报最佳实践

适用于**图文混合素材**（短视频封面、社媒海报、信息图配图等）——需要模型一次性渲染文字与画面，而不是后期合成。

### 1. 参数推荐

| 参数 | 推荐值 | 原因 |
|------|--------|------|
| `--cfg` | **4.0** | Qwen 官方建议：只要 prompt 里有要渲染的文字，CFG 必须 ≥4，否则文字会糊、错位、出现乱码字符 |
| `--steps` | **50** | 默认 20 文字边缘发虚；提高到 50 文字锐利可读 |
| `--image-size` | 按平台选 | 9:16 竖屏 `928x1664`、16:9 横屏 `1664x928`、1:1 方图 `1328x1328`（必须在合法值列表内） |
| `--negative-prompt` | 可选 | 大部分时候并不需要 |

### 2. Prompt 写法（关键）

**❌ 反例**（泛泛描述）：
> "Generate an attractive short-video cover with a title about AI"

**✅ 正例**（按视觉布局分段写，明确写出要渲染的文字）：
> "A dramatic vertical 9:16 short-video cover. Background: bold red-to-black gradient. Top: glowing AI chip icons with text 'DeepSeek'. Middle: large bold Chinese text '前几周 DeepSeek 还是神一般的存在' in white and gold gradient with sharp shadows. Bottom: dramatic red glowing Chinese text '为什么热度消散得这么快？' with lightning effects. Style: high contrast, modern tech poster, dramatic lighting, professional Chinese typography, sharp text rendering, cinematic, no watermarks."

要点：
- **要写的字直接写完整句子**，不要"加个标题"这种空指令
- **按布局分段**描述（top/middle/bottom 或左/中/右），让模型知道字放哪
- **指定字体特性**：颜色、渐变、阴影、发光、风格
- **明确要求**："sharp text rendering"、"professional Chinese typography"
- 末尾加 "no watermarks" 排除水印

### 3. 可选设置 `--negative-prompt`

> 并不是必须的，大部分时候现代模型并不需要特别指定负面提示。

### 4. 生成后必须验证

1. 用 `image` 工具分析图片，**逐项确认**：
   - ✅ 文字内容是否完全正确（不能错字、漏字、出现乱码字符）
   - ✅ 文字位置/对齐/排版是否符合预期
   - ✅ **没有意外的 logo/水印/UI 元素**（如有，重新生成，并使用 `--negative-prompt` 防止）
   - ✅ 主体内容符合 prompt
2. 异常则重新生成（最多 3 次），仍异常则标记失败继续

### 5. 输出格式

- 脚本默认输出 **PNG**（无损）
- 如果目标平台只支持 **JPG**（如企业微信朋友圈），用 PIL 二次转码：
  ```python
  from PIL import Image
  img = Image.open("00.png").convert("RGB")
  img.save("cover.jpg", "JPEG", quality=92)
  ```
  **不做任何像素修改**，只是格式转换。

### 6. 完整示例

```bash
python3 ./scripts/gen.py \
  --prompt "A dramatic vertical 9:16 short-video cover with bold red and black gradient background, glowing AI chip icons floating in the upper area, and large bold Chinese text '前几周 DeepSeek 还是神一般的存在' in the middle in white and gold gradient with sharp shadows. At the bottom, dramatic glowing red Chinese text '为什么热度消散得这么快？' with lightning-like effects. Visual style: high contrast, modern tech poster, dramatic lighting, professional Chinese typography, sharp text rendering, cinematic, no watermarks" \
  --image-size 928x1664 \
  --cfg 4.0 \
  --steps 50 \
  --out-dir /path/to/output
```

---

## ⚠️ 生成后必须验证

SiliconFlow 图片生成经常出现异常：返回一张**纯色背景图**（单色无内容），而非 prompt 要求的图像。

**每张图生成后必须执行验证，不得跳过。**

### 验证流程

1. 图片生成后，立即用 `image` 工具查看刚生成的图片
2. 判断图片是否正常：
   - ❌ **异常**：整张图是纯色背景（全黑/全白/全灰/全蓝等），没有任何主体内容 → **重新生成**
   - ✅ **正常**：图片有明确的主体内容，符合 prompt 描述 → 继续下一步
3. 如果重新生成，最多重试 3 次，仍异常则标记失败并继续后续任务
