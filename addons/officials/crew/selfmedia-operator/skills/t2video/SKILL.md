---
name: t2video
description: 一站式短视频制作工具。整合 SiliconFlow TTS 语音合成、素材搜集（Pexels/Pixabay/AI 生成）和 FFmpeg 组装，从脚本到成品视频一步完成。无 subagent 模式，适合短小视频。
metadata:
  openclaw:
    emoji: "🎥"
    requires:
      bins:
      - python3
      - ffmpeg
      - ffprobe
      env:
      - SILICONFLOW_API_KEY
    primaryEnv: SILICONFLOW_API_KEY
---

# t2video — 一站式短视频制作

Use this skill when:
- 需要从脚本生成完整短视频（TTS + 素材 + 组装）
- 用户指定主题和已有素材，生成短视频

**本技能是 video-producer 的简化版**：适合短小视频制作，且只生成9:16的竖屏视频。

**不烧录字幕**：大部分平台支持自动生成字幕，无需手动烧录。

---

## ⚙️ 执行方式（强制）

本技能涉及多步骤生产流程，你应该 self-spawn 一个 subagent 来执行，原因：subagent 独立上下文，不会因对话历史积累而降低输出质量。

你只负责跟进subagent的执行，避免它们长时间卡在某个步骤，必要时可以提供提示或调整执行策略。另外在关键节点要求它向你汇报，你检查后再让它继续执行下一步。

---

## 工作流程

### Step 1 — 工作区目录准备

在 `output_videos/` 下创建项目文件夹，如 `output_videos/<video-name>/`，作为 project-dir。

工作区结构：

```
<project-dir>/
├── script.md              # 三段式脚本
├── tts_requirement.md     # 配音需求（由 Step 3 创建）
├── artifacts/             # 产出素材（TTS音频+视频素材）
│   ├── speech.mp3         # TTS 配音
│   ├── speech.json        # TTS 元数据（含 duration）
│   └── <video>.mp4        # 视频素材
└── video.mp4              # 最终成品
```

### Step 2 — 写三段式脚本

基于用户要求按「开篇抓眼球 → 中段讲卖点 → 结尾促下单」结构撰写脚本，保存为 `script.md`。

| 段落 | 时长占比 | 目标 | 示例 |
|------|---------|------|------|
| **开篇抓眼球** | 前 15–20% | 3 秒内让人停止划走 | "99% 的人都不知道…" / 强反差开场 |
| **中段讲卖点** | 60–70% | 展示核心价值 | 痛点 → 解决 → 数据佐证 |
| **结尾促下单** | 后 15–20% | 明确 CTA | "链接在简介" / "限时优惠" |

脚本完成后保存到工作区（如 `<project-dir>/script.md`）。

！检查点：subagent 必须在此步骤完成后向主agent汇报。主agent应在此先自检脚本质量（如是否符合三段式结构、是否预留了用户指定素材的使用位置、是否有明确 CTA），确认无误后提交用户确认。

如果用户有意见，则需要重复执行Step2，直到用户确认后才能让subagent进入 Step 3。

### Step 3 — 生成配音

创建 `tts_requirement.md`，写入配音文案、音色和语速：

```markdown
# 配音需求

## 配音文案
<!-- 需要朗读的纯文本，不含 markdown 标题、注释或镜头说明 -->

## 语音要求
- 音色：fnlp/MOSS-TTSD-v0.5:benjamin
- 语速：1.0
- 语气：自然、有吸引力
```

**配音文案书写要求**：
- `## 配音文案` 段内只写需要朗读的**纯文本**，不得使用任何 Markdown 格式（标题、加粗、列表等）
- 如需分段，用空行分隔，不要用 `###` 等标题
- tts.py 会自动过滤 Markdown 标题行（`#`/`##`/`###` 等）和 HTML 注释，但最好从源头就写纯文本

！检查点：subagent 必须在此步骤完成后向主agent汇报。主agent应在此对 `tts_requirement.md` 进行评估，通过后再让subagent继续执行下去。

然后调用 tts.py 生成配音：

```bash
python3 ./skills/t2video/scripts/tts.py <project-dir>/ --overwrite
```

脚本会自动读取 `tts_requirement.md`，只抽取「配音文案」中的纯文本，并读取其中的音色和语速设置。产出 `artifacts/speech.mp3` 和 `artifacts/speech.json`（含 `duration` 字段）。

ASR 自检由 tts.py 自动完成（Jaccard 相似度阈值 0.5），无需额外操作。

### Step 4 — TDD 式素材生产与自检

把 content-check 作为素材生产的测试循环，严格按以下流程执行：

#### 4.1 初检

在搜集任何新素材之前，先运行 content-check 检查已有素材：

```bash
python3 ./skills/t2video/scripts/check.py <project-dir>/
```

根据输出执行：
- `verdict: "accepted"` 且 `duration_gap.status: "sufficient"` → 素材满足要求，进入 Step 5 合成
- `verdict: "needs_rework"` 或 `duration_gap.status: "deficit"` → 记录问题和 `duration_gap.gap`，进入 4.2 补充/修正
- `duration_gap.status: "excess"` → 素材总时长超出目标 3s 以上（会产生明显无声段），删除过长素材后重新下载匹配的

content-check 自动确定目标时长：读取 `artifacts/speech.json`，按 `duration + 1s` 计算缺口（前后各 0.5s）。

#### 4.2 搜集/补充素材

按以下优先级搜集/补充素材：

1. **用户素材**：如果用户指定了素材，则必须优先使用，不足部分再用如下的方案补全
2. **`video_generate` 工具**：使用 openclaw 原生的 `video_generate` 工具生成视频片段（注意必须为9:16竖屏）
3. **`pexels-footage`**：`video_generate` 不可用时，从 Pexels 免费素材库搜索下载（注意必须为9:16竖屏）
4. **`pixabay-footage`**：`pexels-footage` 不可用时，或未搜索到合适素材时，从 Pixabay 免费素材库搜索下载（注意必须为9:16竖屏）
5. **AI 视频生成**：仅在上述方案均不可用或时长仍不足时使用

**素材下载规则**（必须严格遵守）：

- **一次只下载一个视频**：pixabay-footage 和 pexels-footage 脚本已强制视频类型 `--max-clips=1`，禁止批量下载
- **时长精准匹配**：根据 content-check 报告的 `duration_gap`，设置 `--min-duration` 和 `--max-duration` 让下载的素材贴近缺口时长。例如缺口 20s，则 `--min-duration 17 --max-duration 23`，不要下载远超需求的素材
- **超出检测**：如果 content-check 报告 `duration_gap.status: "excess"`（实际时长超出目标 3s 以上），必须删除过长的素材后重新下载匹配的

```bash
# 使用 AI 视频生成（仅在其他方案不可用时）
python3 ./skills/t2video/scripts/gen.py \
  --prompt "描述画面内容" \
  --out-dir <project-dir>/artifacts
```

#### 4.3 回归自检

每生成、下载或修正一段素材后，立即重新运行 content-check：

```bash
python3 ./skills/t2video/scripts/check.py <project-dir>/
```

1. 如果有质量问题（如空画面、低分辨率），先修复问题素材
2. 如果有时长缺口，按 4.2 的优先级补充缺口
3. 补充或修复后再次运行 content-check
4. 只有 `verdict: "accepted"` 且时长满足目标时，才能进入 Step 5 合成

### Step 5 — 合成视频

content-check 通过后，调用 fragment-assembly 将视频和音频合成为最终成品：

```bash
python3 ./skills/t2video/scripts/assemble.py <project-dir>/artifacts/ --output <project-dir>/video.mp4
```

合成规则：
- 有 `speech.mp3` → 使用 TTS 音频替换视频音轨（AAC 192k）
- 无配音 → 保留视频原音轨
- 不烧录字幕

合成后确认 `video.mp4` 存在且非空。

### Step 6 — 制作封面

每个视频都必须配封面图。封面要求：
- **必须包含视频标题文字**，不允许纯图片封面
- 标题文字必须有设计感（字体选择、排版布局、颜色搭配）
- 竖屏封面 1080x1920，横屏 1920x1080
- 可以使用视频关键画面作为背景，但文字是必须元素

使用 `siliconflow-img-gen` 制作封面，保存为 `<project-dir>/cover.jpg`。

---

## 可用语音

| Voice ID | 说明 |
|----------|------|
| `fnlp/MOSS-TTSD-v0.5:benjamin` | 幽默男声，语速较慢，推荐 |
| `fnlp/MOSS-TTSD-v0.5:charles` | 激昂男声，适合广告 |
| `fnlp/MOSS-TTSD-v0.5:claire` | 清澈女声，推荐 |
| `fnlp/MOSS-TTSD-v0.5:david` | 清脆男声 |
| `fnlp/MOSS-TTSD-v0.5:diana` | 可爱女声，娃娃音 |

---

## 脚本清单

| 脚本 | 文件名 | 用途 |
|------|--------|------|
| TTS 语音合成 | `./skills/t2video/scripts/tts.py` | 读取 tts_requirement.md，生成 speech.mp3 + speech.json |
| 素材自检 | `./skills/t2video/scripts/check.py` | 检查素材质量与时长缺口 |
| 片段合成 | `./skills/t2video/scripts/assemble.py` | 视频+音频合成 MP4 |
| AI 视频生成 | `./skills/t2video/scripts/gen.py` | SiliconFlow 文生视频/图生视频 |

---

## 注意事项

- **TTS ASR 自检已内置**：tts.py 生成音频后自动执行 ASR 自检（阈值 50%），无需单独操作
- **素材搜集仅支持素材合成模式**：不支持动态制作（hyperframes、manim 等），这是本技能与 video-producer 的关键区别
- **不拆分片段**：整部视频作为单一片段生产，适合 1–3 分钟的短小视频
- **配音语速不得为匹配视频时长而调整**：默认 1.0，只能按用户明确要求修改
