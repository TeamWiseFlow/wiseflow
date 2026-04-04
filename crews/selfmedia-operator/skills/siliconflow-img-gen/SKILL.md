---
name: siliconflow-img-gen
description: Generate or edit images via SiliconFlow Images API. Use for text-to-image and image-edit tasks. Defaults: generation model Qwen/Qwen-Image; edit model Qwen/Qwen-Image-Edit-2509. Output defaults to workspace campaign_assets with migration-friendly relative path resolution.
homepage: https://docs.siliconflow.cn/cn/api-reference/images/images-generations
metadata:
  {
    "openclaw":
      {
        "emoji": "🖼️",
        "requires": { "bins": ["python3"] },
      },
  }
---

# SiliconFlow Image Gen

支持两种模式：
- 文生图（text-to-image）
- 改图（基于已有网络图片 URL 做修改）

## 默认输出位置

默认输出到当前 agent workspace 下的 `campaign_assets/sf-img-<timestamp>/`。

> 实现方式是基于脚本自身相对位置反推 workspace 根目录，不写死绝对路径，便于后续迁移。

## 用法

```bash
# 1) 文生图（默认模型：Qwen/Qwen-Image）
python3 {baseDir}/scripts/gen.py --prompt "一只戴墨镜的柯基在海边"

# 2) 文生图，输出 JPG 格式
python3 {baseDir}/scripts/gen.py --prompt "一只戴墨镜的柯基在海边" --format jpg

# 3) 改图（默认模型：Qwen/Qwen-Image-Edit-2509）
python3 {baseDir}/scripts/gen.py \
  --prompt "把这张图改成夜景霓虹风" \
  --image "https://example.com/original.jpg"

# 4) 多参考图改图（按 API 支持可选传 image2/image3）
python3 {baseDir}/scripts/gen.py \
  --prompt "改成赛博朋克风格" \
  --image "https://example.com/a.jpg" \
  --image2 "https://example.com/b.jpg" \
  --image3 "https://example.com/c.jpg"

# 5) 指定输出目录（可选）
python3 {baseDir}/scripts/gen.py --prompt "海报封面" --out-dir ./campaign_assets
```

## 参数

| Flag | 默认值 | 说明 |
|------|--------|------|
| `--prompt` | 必填 | 文本描述 |
| `--model` | 自动选择 | 未传时：文生图=`Qwen/Qwen-Image`，改图=`Qwen/Qwen-Image-Edit-2509` |
| `--image` | — | 改图输入原图 URL；传入即进入改图模式 |
| `--image2` | — | 可选第二张参考图 URL |
| `--image3` | — | 可选第三张参考图 URL |
| `--image-size` | `1024x1024` | 图像分辨率 |
| `--steps` | `20` | 推理步数（`num_inference_steps`） |
| `--cfg` | `4` | 采样配置（`cfg`） |
| `--batch-size` | `1` | 批量生成数 |
| `--negative-prompt` | — | 负面提示词 |
| `--seed` | — | 随机种子 |
| `--format` | `jpg` | 输出格式：`png` / `jpg` / `jpeg` |
| `--out-dir` | `campaign_assets` | 输出根目录 |

## 改图请求格式对齐说明

脚本已对齐以下字段：
- `model`
- `prompt`
- `num_inference_steps`
- `cfg`
- `image`
- `image2`
- `image3`

等价于你提供的 SiliconFlow Images API 请求格式。

## 输出内容

每次执行会生成：
- `00.png`, `01.png`...（下载后的图片）
- `prompts.json`（prompt、模型、源图 URL、结果 URL）
- `index.html`（本地缩略图预览）
