---
name: t2video
description: 一站式短视频制作工具。整合 Edge TTS（免费）/ SiliconFlow TTS 语音合成、SiliconFlow 文生视频/图生视频和 FFmpeg 组装，从脚本到成品视频一步完成。支持用户指定素材的位置编排。
metadata:
  openclaw:
    emoji: "🎥"
    requires:
      bins:
      - python3
      env:
      - SILICONFLOW_API_KEY
    primaryEnv: SILICONFLOW_API_KEY
---

# t2video — 一站式短视频制作

Use this skill when:
- 需要从脚本生成完整短视频（TTS + 素材 + 组装）
- 需要生成 TTS 语音旁白（Edge TTS 免费 / SiliconFlow 备选）
- 需要生成 AI 视频片段
- 需要将用户提供的素材（视频/图片）按指定位置编入视频
- 需要将已有素材 + 音频组装成最终视频

**三种模式**：

| 模式 | 用途 | 输入 | 输出 |
|------|------|------|------|
| `tts` | 语音合成 | 文本 | 音频文件 |
| `gen` | AI 视频生成 | 文本描述/图片 | MP4 视频片段 |
| `compose` | 视频组装 | 素材 + 音频 + 编排计划 | 最终 MP4 |

**不烧录字幕**：大部分平台支持自动生成字幕，无需手动烧录。

---

## tts — 语音合成

**默认使用 Edge TTS**（完全免费，无需 API Key）。SiliconFlow 为备选（需要 API Key，音质更好）。

```bash
# 默认 edge-tts（免费）
python3 ./skills/t2video/scripts/t2video.py tts \
  --text "大家好，欢迎来到今天的视频。"

# 指定语音
python3 ./skills/t2video/scripts/t2video.py tts \
  --text "99%的人都不知道这个技巧" \
  --voice zh-CN-YunxiNeural

# 从文件读取长文本
python3 ./skills/t2video/scripts/t2video.py tts \
  --text-file ./output_video/my-video/script.txt \
  --out-dir ./output_video/my-video/fragments

# SiliconFlow TTS（备选，需要 SILICONFLOW_API_KEY）
python3 ./skills/t2video/scripts/t2video.py tts \
  --provider siliconflow \
  --text "这是演示旁白。" \
  --voice "FunAudioLLM/CosyVoice2-0.5B:anna" \
  --format wav
```

### tts 参数

| Flag | Default | Description |
|------|---------|-------------|
| `--text` | — | 要合成的文本（与 --text-file 二选一） |
| `--text-file` | — | UTF-8 文本文件路径 |
| `--provider` | `edge` | TTS 提供者：edge（免费）/ siliconflow（备选） |
| `--voice` | provider 默认 | 语音 ID（见下方语音列表） |
| `--speed` | — | 语速。Edge: -50~50（百分比）；SF: 0.25~4.0 |
| `--format` | `mp3` | 音频格式（siliconflow：mp3/opus/wav/pcm） |
| `--sample-rate` | — | 采样率（siliconflow only） |
| `--output` | — | 精确输出路径 |
| `--out-dir` | `./tmp/tts-<ts>` | 输出目录 |

### Edge TTS 可用语音（免费，无需 Key）

| Voice ID | 说明 |
|----------|------|
| `zh-CN-XiaoxiaoNeural` | 女声（默认） |
| `zh-CN-XiaoyiNeural` | 女声 |
| `zh-CN-YunjianNeural` | 男声 |
| `zh-CN-YunxiNeural` | 男声 |
| `zh-CN-YunxiaNeural` | 男声 |
| `zh-CN-YunyangNeural` | 男声（新闻播报风格） |
| `zh-CN-liaoning-XiaobeiNeural` | 东北话女声 |
| `zh-CN-shaanxi-XiaoniNeural` | 陕西话女声 |
| `en-US-JennyNeural` | English Female |
| `en-US-GuyNeural` | English Male |
| `en-US-AriaNeural` | English Female |
| `en-US-DavisNeural` | English Male |
| `ja-JP-NanamiNeural` | 日本語 Female |
| `ja-JP-KeitaNeural` | 日本語 Male |
| `ko-KR-SunHiNeural` | 한국어 Female |
| `ko-KR-InJoonNeural` | 한국어 Male |

### SiliconFlow TTS 可用语音（需要 API Key）

| Voice ID | 说明 |
|----------|------|
| `FunAudioLLM/CosyVoice2-0.5B:alex` | 男声 |
| `FunAudioLLM/CosyVoice2-0.5B:anna` | 女声 |
| `FunAudioLLM/CosyVoice2-0.5B:bella` | 女声 |
| `FunAudioLLM/CosyVoice2-0.5B:benjamin` | 男声 |
| `FunAudioLLM/CosyVoice2-0.5B:charles` | 男声 |
| `FunAudioLLM/CosyVoice2-0.5B:claire` | 女声 |
| `FunAudioLLM/CosyVoice2-0.5B:david` | 男声 |
| `FunAudioLLM/CosyVoice2-0.5B:diana` | 女声 |

---

## gen — AI 视频生成

直接调用 SiliconFlow Video API 生成视频片段。异步模式：提交任务 → 轮询状态 → 下载结果。

> 生成视频通常需要 1–5 分钟，建议设置 exec timeout=600。
> **每次最多生成 5 秒视频**。需要更长视频时，拆成多段顺序生成。

```bash
# 文生视频
python3 ./skills/t2video/scripts/t2video.py gen \
  --prompt "海豚在夕阳下跃出海面"

# 图生视频
python3 ./skills/t2video/scripts/t2video.py gen \
  --model "Wan-AI/Wan2.2-I2V-A14B" \
  --prompt "镜头缓慢拉远" \
  --image "https://example.com/photo.jpg"

# 指定分辨率和输出目录
python3 ./skills/t2video/scripts/t2video.py gen \
  --prompt "延时摄影：花朵绽放" \
  --image-size 720x1280 \
  --out-dir ./output_video/my-video/fragments
```

### gen 参数

| Flag | Default | Description |
|------|---------|-------------|
| `--prompt` | required | 视频描述 |
| `--model` | `Wan-AI/Wan2.2-T2V-A14B` | 模型：T2V 或 I2V |
| `--image` | — | 图片 URL 或 base64（I2V 必需） |
| `--image-size` | `1280x720` | 分辨率：1280x720/720x1280/960x960 |
| `--negative-prompt` | — | 负面提示 |
| `--seed` | — | 随机种子 |
| `--poll-interval` | `10` | 轮询间隔（秒） |
| `--timeout` | `600` | 最大等待时间（秒） |
| `--out-dir` | `./tmp/sf-video-<ts>` | 输出目录 |

---

## compose — 视频组装

将预准备的视觉素材（视频片段/图片）与旁白音频组装成最终 MP4。

### 素材编排计划

支持通过 `--plan` 参数指定素材的位置编排。编排计划为 JSON 文件，格式如下：

```json
{
  "audio": "./output_video/my-video/fragments/speech.mp3",
  "aspect": "9:16",
  "tracks": [
    {
      "position": "0%",
      "material": "./output_video/my-video/fragments/video_01.mp4"
    },
    {
      "position": "30%",
      "material": "./output_video/my-video/fragments/user_clip.mp4"
    },
    {
      "position": "70%",
      "material": "./output_video/my-video/fragments/photo.jpg",
      "duration": 8
    }
  ]
}
```

**position 说明**：
- `"0%"` = 视频开头
- `"50%"` = 视频中部
- `"100%"` = 视频末尾
- 也可以用秒数：`"5.0"` 表示第 5 秒
- 图片必须指定 `duration`（显示秒数），视频则按原时长（不超过剩余空间）

**编排逻辑**：
1. 根据音频时长确定视频总时长
2. 按 position 排序，将用户指定素材插入对应时间点
3. 未被用户素材覆盖的时间段，由 `--materials-dir` 中的素材按顺序填充
4. 如果某段时间没有素材，使用占位符（深色纯色）

### compose 参数

| Flag | Default | Description |
|------|---------|-------------|
| `--audio` | required | 旁白音频路径（mp3/wav） |
| `--materials-dir` | required | 素材目录（视频/图片），用于填充非指定位置 |
| `--plan` | — | 素材编排计划 JSON 文件路径（可选） |
| `--aspect` | `9:16` | 画面比例：9:16/16:9/1:1 |
| `--clip-duration` | `5` | 每段素材最大秒数 |
| `--transition` | `none` | 转场：none/fade |
| `--output` | required | 输出 MP4 路径 |

### 基础用法（无编排计划）

```bash
# 按素材目录顺序自动组装
python3 ./skills/t2video/scripts/t2video.py compose \
  --audio ./output_video/my-video/fragments/speech.mp3 \
  --materials-dir ./output_video/my-video/fragments \
  --aspect 9:16 \
  --output ./output_video/my-video/video.mp4
```

### 带编排计划的用法

```bash
# 在视频中部插入用户指定的片段
python3 ./skills/t2video/scripts/t2video.py compose \
  --audio ./output_video/my-video/fragments/speech.mp3 \
  --materials-dir ./output_video/my-video/fragments \
  --plan ./output_video/my-video/plan.json \
  --aspect 9:16 \
  --output ./output_video/my-video/video.mp4
```

---

## 完整工作流示例

```bash
WORKDIR="./output_video/my-video/fragments"
mkdir -p "$WORKDIR"

# 1. 生成旁白
python3 ./skills/t2video/scripts/t2video.py tts \
  --text "99%的人都不知道这个技巧..." \
  --voice zh-CN-YunxiNeural \
  --out-dir "$WORKDIR"

# 2. 生成 AI 视频片段（每段 5s）
python3 ./skills/t2video/scripts/t2video.py gen \
  --prompt "科技感办公室场景" \
  --image-size 720x1280 \
  --out-dir "$WORKDIR"

# 3. 编写编排计划（可选，如需指定素材位置）
cat > ./output_video/my-video/plan.json << 'EOF'
{
  "audio": "./output_video/my-video/fragments/speech.mp3",
  "aspect": "9:16",
  "tracks": [
    {"position": "0%", "material": "./output_video/my-video/fragments/video_01.mp4"},
    {"position": "50%", "material": "./output_video/my-video/fragments/user_product_demo.mp4"},
    {"position": "85%", "material": "./output_video/my-video/fragments/campaign_cover.jpg", "duration": 5}
  ]
}
EOF

# 4. 组装成品
python3 ./skills/t2video/scripts/t2video.py compose \
  --audio "$WORKDIR/speech.mp3" \
  --materials-dir "$WORKDIR" \
  --plan ./output_video/my-video/plan.json \
  --aspect 9:16 \
  --output ./output_video/my-video/video.mp4
```

---

## 视频剧本结构

生成脚本时遵循三幕结构：

| 段落 | 时长占比 | 目标 | 示例 |
|------|---------|------|------|
| **开篇抓眼球** | 前 15–20% | 3 秒内让人停止划走 | "99% 的人都不知道…" / 强反差开场 |
| **中段讲卖点** | 60–70% | 展示核心价值 | 痛点 → 解决 → 数据佐证 |
| **结尾促下单** | 后 15–20% | 明确 CTA | "链接在简介" / "限时优惠" |

**用户指定素材的编排**：当用户提出要在视频的某个位置加入其指定的视频片段、素材或图片时，应在编写剧本阶段就规划好该素材的位置和时长，并在编排计划中明确写出。用户的位置描述可能是模糊的（如"视频中部"、"末尾"），编写剧本时需转换为具体的 position 百分比或秒数。

---

## 素材优先级

materials-dir 中同时有视频和图片时，优先使用视频片段。无素材时使用占位符。

## 错误处理

| 错误 | 处理 |
|------|------|
| 音频文件不存在 | 检查路径，确保 tts 步骤完成 |
| 无素材文件 | 使用占位符（深色纯色） |
| MoviePy 导入失败 | `pip install moviepy` |
| edge-tts 导入失败 | `pip install edge-tts>=7.0` |
| SiliconFlow API 错误 | 检查 SILICONFLOW_API_KEY |
| 视频生成超时 | 增加 --timeout 或拆分更短的片段 |
