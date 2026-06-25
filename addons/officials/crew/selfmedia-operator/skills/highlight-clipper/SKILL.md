---
name: highlight-clipper
description: 自动从本地视频中提取高光片段。通过 ASR 转录 + 文本分析识别高光时刻，剪辑输出多段短视频。
metadata:
  openclaw:
    emoji: "✂️"
    requires:
      bins:
      - python3
      - ffmpeg
      - ffprobe
      env:
      - SILICONFLOW_API_KEY
    primaryEnv: SILICONFLOW_API_KEY
---

# highlight-clipper — 视频高光剪辑

Use this skill when:
- 用户提供一个本地视频文件，希望自动剪辑出高光片段
- 需要从长视频中提取精彩片段用于二次分发（抖音/小红书/B站短视频等）

**不适用场景**：纯音乐或无声视频（依赖语音内容识别高光）、画面精彩但无语音的片段。

---

## 工作流程

### Step 1 — 创建输出目录

在 `output_videos/` 下创建项目目录：

```bash
mkdir -p output_videos/<video-name>
```

### Step 2 — 运行高光剪辑

```bash
python3 ./skills/highlight-clipper/scripts/clip.py <video_path> --out-dir output_videos/<video-name>
```

参数说明：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `<video_path>` | — | 源视频文件路径（必需） |
| `--out-dir` | — | 输出目录，必须在 `output_videos/` 或 `tmp/` 下（必需） |
| `--count` | 3 | 提取高光片段数量 |
| `--min-duration` | 15 | 最短片段时长（秒） |
| `--max-duration` | 58 | 最长片段时长（秒），默认 58 留余量防超 60s 平台限制 |
| `--buffer` | 3 | 片段前后缓冲（秒） |

示例 — 从一段 5 分钟视频提取 5 个高光：

```bash
python3 ./skills/highlight-clipper/scripts/clip.py output_videos/my-video/video.mp4 --out-dir output_videos/my-video --count 5
```

### Step 3 — 查看结果

脚本产出：

```
output_videos/<video-name>/
├── highlight_01.mp4       # 高光片段 1
├── highlight_02.mp4       # 高光片段 2
├── highlight_03.mp4       # 高光片段 3
└── highlights.json        # 高光分析报告
```

`highlights.json` 包含完整转录文本、每个片段的时间戳、评分和文案：

```json
{
  "source_video": "video.mp4",
  "video_duration": 180.5,
  "highlight_count": 3,
  "full_transcript": "...",
  "highlights": [
    {
      "index": 1,
      "file": "highlight_01.mp4",
      "start": 12.0,
      "end": 45.0,
      "duration": 33.0,
      "text": "这才是最关键的一步...",
      "score": 8.5
    }
  ]
}
```

查看报告：

```bash
cat output_videos/<video-name>/highlights.json
```

### Step 4 — 后续处理（可选）

对高光片段做进一步加工：
- 使用 `t2video` 为片段添加配音或封面
- 使用各平台发布技能（`douyin-publish`、`xhs-publish` 等）发布

---

## 技术原理

1. **音频提取**：ffmpeg 从视频中提取 16kHz 单声道 WAV
2. **ASR 转录**：SiliconFlow SenseVoiceSmall 模型，获取带时间戳的语音片段
3. **高光评分**：对每个转录片段综合打分，考量：
   - 情感强度词（"最"、"超"、"非常"等）— 权重 2.0
   - 转折/惊喜词（"但是"、"没想到"、"原来"等）— 权重 3.0
   - 行动号召词（"赶紧"、"收藏"、"关注"等）— 权重 2.5
   - 疑问句和感叹号 — 权重 1.5
   - 数据/数字出现 — 权重 1.0
   - 信息密度（单位时长文字量）— 权重最高 3.0
4. **多样性选择**：贪婪选取得分最高的 N 个片段，保证片段间至少间隔 3 秒（仅去重）
5. **相邻合并**：间隔 ≤ 10 秒的高光片段自动合并为一段长片段，**不限时长**——挨着的高光连成完整段落
6. **锚点扩展**：短片段（< max-duration）以片段为中心向前后扩展填满 max-duration；已合并的长片段不截断，保留完整内容
7. **视频剪辑**：ffmpeg 精确裁剪

---

## 长视频处理

视频超过 5 分钟时，脚本自动分块转录（每块 5 分钟），合并时间戳后统一分析。无需手动干预。

---

## 注意事项

- 源视频必须有语音内容，纯音乐或无声视频无法识别高光
- 转录质量取决于语音清晰度，建议使用语音清晰的视频
- 高光评分基于文本语义分析，非视觉分析——画面精彩但无语音的片段可能被遗漏
- 片段时长受 `--min-duration` 和 `--max-duration` 控制，可根据目标平台要求调整（如抖音 15–60 秒、小红书 15–45 秒）
- 相邻高光片段（间隔 ≤ 10 秒）会自动合并，合并后不限时长——适合会议中连续精彩讨论的场景
- 短片段会以片段为中心向前后扩展至 max-duration（默认 58 秒），确保每段内容充实
