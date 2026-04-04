---
name: siliconflow-video-gen
description: Generate videos via SiliconFlow Video API. Supports text-to-video (T2V) and image-to-video (I2V) using Wan2.2 models. Async flow: submit job, poll status, then download. Default output path resolves to workspace campaign_assets via relative path logic for portability.
homepage: https://docs.siliconflow.cn/cn/userguide/capabilities/video
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "bins": ["python3"] },
      },
  }
---

# SiliconFlow Video Gen

通过 SiliconFlow Video API 生成视频（Wan2.2 系列）。

## 默认输出位置

默认输出到当前 agent workspace 下的 `campaign_assets/sf-video-<timestamp>/`。

> 脚本通过相对路径推导 workspace 根目录，不写死绝对路径，便于后续迁移。

## 运行示例

```bash
# 文生视频（T2V）
python3 {baseDir}/scripts/gen.py --prompt "海边日落延时摄影"

# 图生视频（I2V）
python3 {baseDir}/scripts/gen.py \
  --model "Wan-AI/Wan2.2-I2V-A14B" \
  --prompt "镜头缓慢拉远" \
  --image "https://example.com/my-photo.jpg"

# 指定分辨率与输出目录
python3 {baseDir}/scripts/gen.py \
  --prompt "城市夜景" \
  --image-size 720x1280 \
  --out-dir ./campaign_assets
```

## 参数

| Flag | 默认值 | 说明 |
|------|---------|-------------|
| `--prompt` | 必填 | 视频描述 |
| `--model` | `Wan-AI/Wan2.2-T2V-A14B` | 模型：T2V 或 I2V |
| `--image` | — | I2V 模式必填：图片 URL 或 base64 data URI |
| `--image-size` | `1280x720` | 分辨率：`1280x720` / `720x1280` / `960x960` |
| `--negative-prompt` | — | 负面提示词 |
| `--seed` | — | 随机种子 |
| `--poll-interval` | `10` | 轮询间隔（秒） |
| `--timeout` | `600` | 最长等待时长（秒） |
| `--out-dir` | `campaign_assets` | 输出根目录 |

## 输出

- `video_<requestId>.mp4`
- `result.json`（完整 API 返回）
