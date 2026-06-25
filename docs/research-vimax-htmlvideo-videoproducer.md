# ViMax vs html-video vs video-producer 对比调研

> 调研日期：2026-06-12
> 调研对象：
> - ViMax: https://github.com/bigbrother666sh/ViMax (commit: 229e749, main 分支)
> - html-video: https://github.com/bigbrother666sh/html-video (main 分支)
> - video-producer: 本项目 `addons/official-plus/crew/video-producer/` 及已部署实例 `~/.openclaw/workspace-video-producer/`

---

## 1. 能够实现的视频类型

| 维度 | ViMax | html-video | video-producer (ours) |
|------|-------|------------|----------------------|
| **叙事长视频** | ✅ 核心能力。Idea2Video / Novel2Video / Script2Video，支持多场景叙事、角色追踪、时间连贯性 | ❌ 不擅长。content-graph 做多帧分镜但本质是信息可视化/解说，非叙事 | ❌ 不擅长。片段拼接为主，无角色追踪/叙事引擎 |
| **数据可视化动画** | ❌ 无专门支持 | ✅ 核心能力。NYT 风格折线图、Swiss/Vignelli 数据卡片、决策树 | ⚠️ 有限。Manim 可做数学动画，但非开箱即用 |
| **标题/片头动画** | ❌ 无专门支持 | ✅ 21 模板覆盖。Glitch title、kinetic type、typewriter cursor、liquid hero、light-leak cinema、logo outro | ⚠️ 有限。HyperFrames 可做但需手写 HTML+GSAP，无模板库 |
| **产品宣传片** | ❌ 无专门支持 | ✅ 15s/30s 多场景产品 promo 模板 | ⚠️ 有限。需手动编排片段 |
| **解说/教程视频** | ⚠️ 可做但非专长 | ✅ 决策树 explainer、多帧 storyboard | ✅ 可做。TTS 旁白 + HyperFrames/Manim + 素材拼接 |
| **AI 生成视频素材** | ✅ 核心能力。Google Veo / 豆包 Seedance 文生视频/图生视频，多镜头并行生成 | ❌ 无 AI 视频生成 | ✅ SiliconFlow Wan2.2 文生视频/图生视频（5s 片段） |
| **真人出镜/口播** | ✅ AutoCameo（用户上传照片嵌入故事） | ❌ 无 | ✅ de-mouth 去口误/填充词，保留口播视频 |
| **UI 演示/录屏** | ❌ 无 | ❌ 无 | ✅ patchright 浏览器自动化录制 |
| **文章/链接→视频** | ❌ 无 | ✅ 核心能力。粘贴 URL/GitHub repo，自动抓取内容生成视频 | ❌ 无自动内容抓取 |
| **数学/公式动画** | ❌ 无 | 🗺️ 计划中（Manim adapter） | ✅ Manim explainer skill |
| **视频后处理** | ⚠️ moviepy 基础拼接 | ⚠️ ffmpeg 拼接+音频混合 | ✅ 完整。content-check 质检 → de-mouth 去口误 → fragment-assembly 拼接 → ffmpeg 编码 → SRT 字幕 |

**小结**：
- **ViMax** 是叙事长视频专家（AI 生成画面+多镜头+角色连贯），但动画/数据可视化/后处理弱
- **html-video** 是动画/信息视频专家（模板库+HTML 原生渲染），但无 AI 视频生成、无口播、无后处理
- **video-producer** 是实用型生产流水线（TTS+素材+质检+拼接+去口误），覆盖面广但每个方向深度有限

---

## 2. 技术依赖

### ViMax

| 类别 | 依赖 | 说明 |
|------|------|------|
| **Python** | 3.12+（硬性要求） | |
| **包管理** | `uv` | |
| **ML/AI 框架** | `langchain` + `langchain-openai` + `langchain-community` | Agent 编排 + LLM 调用 |
| **向量检索** | `faiss-cpu` | **仅 Novel2Video 管线使用（该管线未完成），Idea2Video/Script2Video 不用** |
| **视频处理** | `moviepy` | 视频拼接（concatenate_videoclips） |
| **图像处理** | `opencv-python`, `pillow` | 图片 I/O 辅助（下载、base64 转换） |
| **场景检测** | `scenedetect[opencv]` | 声明依赖，管线代码未直接使用 |
| **HTTP** | `aiohttp`, `requests` | |
| **重试** | `tenacity` | |
| **LLM SDK** | `openai`, `google-genai` | OpenAI 兼容接口 + Google GenAI |
| **torch / torchaudio** | pyproject.toml 声明（CUDA 12.8） | **死依赖，源码中无任何 import。安装时下载约 2GB，运行时不使用** |

### html-video

| 类别 | 依赖 | 说明 |
|------|------|------|
| **Node.js** | 20+（硬性要求） | |
| **包管理** | `pnpm` 9+ | monorepo workspace |
| **渲染引擎** | `@remotion/bundler` + `@remotion/renderer` + `remotion` v4 | Remotion 在 dependencies（adapter 未完成） |
| **前端框架** | `react` 18 + `react-dom` | Studio UI |
| **CLI 工具** | `ffmpeg`（系统安装） | MP4 编码 |
| **浏览器** | Chromium（Playwright 安装） | Headless 录制 HTML 动画 |
| **构建** | `typescript` 5.7+, `@biomejs/biome` | 类型检查 + lint |
| **运行时下载** | `hyperframes`（npx） | 默认渲染引擎 |

### video-producer (ours)

| 类别 | 依赖 | 说明 |
|------|------|------|
| **Python** | 3.x（无硬性版本要求） | 脚本仅用标准库 |
| **Node.js** | 需要（npx 调用） | HyperFrames CLI |
| **CLI 工具** | `ffmpeg`/`ffprobe`（系统安装） | 核心：编码/质检/拼接 |
| **浏览器** | Chromium（Playwright/Patchright） | HyperFrames 渲染 + UI demo 录制 |
| **数学动画** | `manim`（可选） | manim-explainer skill |
| **Python 包** | **零外部 pip 依赖** | 全部使用 stdlib（urllib, json, subprocess 等） |
| **运行时下载** | `hyperframes`（npx）, `patchright`（npx） | |

**小结**：
- **ViMax 依赖中等偏重**：langchain 全家桶 + opencv + moviepy + faiss，但 torch 是死依赖可剔除
- **html-video 中等**：Node.js monorepo + Remotion + Chromium，无 Python/ML 依赖
- **video-producer 最轻**：零 pip 依赖，核心只靠 ffmpeg + 系统 Python，按需 npx 拉取

---

## 3. 技术复杂度

| 维度 | ViMax | html-video | video-producer |
|------|-------|------------|----------------|
| **架构复杂度** | 🔴 高。多 Agent 流水线（Director→Screenwriter→Producer→Generator），RAG 分段检索，角色/场景追踪，一致性检查 | 🟡 中。monorepo 6 包 + 21 模板 + 可插拔引擎适配器 + content-graph IR + Studio UI | 🟢 低。线性流水线（需求→TTS→质检→制作→质检→拼接），每个 skill 独立脚本 |
| **代码量** | 🔴 大。完整 Agent 框架 + 多模式入口 | 🟡 中。TypeScript monorepo + 模板库 | 🟢 小。每个 skill 一个 Python 脚本 + SKILL.md |
| **编排方式** | 自研多 Agent 调度器 | Agent 循环（14 种 coding agent 可选） | openclaw crew 编排（SOUL/AGENTS/TOOLS.md） |
| **渲染管线** | API 生成→moviepy 拼接 | HTML→Chromium 录制→ffmpeg 编码→拼接 | 多模式：HyperFrames/Manim/patchright/素材下载→ffmpeg 拼接 |
| **质量保障** | MLLM/VLM 一致性检查 | 无自动质检 | ✅ content-check 自动质检（黑帧/时长/ASR 回查） |
| **上手门槛** | 🔴 高。需理解 4 种模式 + YAML 配置 + Agent 调度 | 🟡 中。Studio UI 降低门槛，但模板定制需懂 HTML/CSS/GSAP | 🟢 低。crew 自主运行，人工只需写 requirement.md |

---

## 4. 对硬件资源的需求程度

### 重要纠正：ViMax 不需要 GPU

`pyproject.toml` 声明了 `torch` + `torchaudio`（CUDA 12.8），但**源码中无任何文件 import torch 或 torchaudio**。这是死依赖/占位依赖。所有图片和视频生成走云端 API，零本地推理。

| 维度 | ViMax | html-video | video-producer |
|------|-------|------------|----------------|
| **CPU** | 🟡 中。多 Agent 并行 + opencv 图片 I/O + moviepy 拼接 | 🟡 中。Chromium 录制是 CPU 密集型，但单帧渲染 | 🟢 低。`taskset -c 0` + `nice -n 10` 强制单核低优先级 |
| **GPU** | 🟢 **不需要**。torch 是死依赖，所有生成走云端 API | 🟢 不需要。`--no-browser-gpu` 禁用 GPU 渲染 | 🟢 不需要。AI 视频生成走云端 API，本地渲染禁用 GPU |
| **内存** | 🟡 中。langchain Agent 上下文 + opencv 帧缓存，预估 4-8GB | 🟡 中。Chromium headless 约 1-2GB/worker | 🟢 低。批量限 3 并发 + gc.collect()，4GB 可运行 |
| **磁盘** | 🟡 中。uv 缓存 + 中间帧（torch 死依赖占 ~2GB） | 🟡 中。node_modules + Chromium + 中间 webm | 🟢 低。无本地模型，中间文件按项目隔离 |
| **网络** | 🔴 高。LLM API + 图片生成 API + 视频生成 API，每次生成多轮调用 | 🟢 低。仅可选 MiniMax 音频 + 源抓取 | 🟡 中。SiliconFlow TTS/ASR/视频 + Pexels/Pixabay 下载 |

**硬件需求总评**：

| | ViMax | html-video | video-producer |
|--|-------|------------|----------------|
| **最低配置** | 4C8G + 稳定网络 | 4C8G + 20GB 磁盘 | 2C4G + 10GB 磁盘 |
| **推荐配置** | 8C16G | 8C16G | 4C8G |
| **GPU** | 不需要 | 不需要 | 不需要 |

---

## 5. 所需第三方服务（API Key 等）

### ViMax

| 服务 | 必需？ | 用途 | 获取方式 |
|------|--------|------|----------|
| **LLM API Key**（OpenRouter/Google/OpenAI/MiniMax） | ✅ 必需 | Agent 编排、脚本生成、一致性检查 | 注册对应平台 |
| **图片生成 API Key**（Google Imagen / 豆包 Seedream） | ✅ 必需 | 场景画面生成 | Google AI Studio 或云雾代理 |
| **视频生成 API Key**（Google Veo / 豆包 Seedance / OpenRouter） | ✅ 必需 | AI 视频片段生成 | Google AI Studio 或云雾代理 |
| **云雾（YunWu）代理** | ❌ 可选 | 国内访问 Google API 的代理 | 注册云雾 |
| **Silicon Reranker** | ❌ 可选 | BGE reranker（仅 Novel2Video RAG） | 注册 Silicon |

> ViMax 已内置云雾代理适配器（`video_generator_veo_yunwu_api.py`、`image_generator_nanobanana_yunwu_api.py`、`video_generator_doubao_seedance_yunwu_api.py`、`image_generator_doubao_seedream_yunwu_api.py`），国内用户可通过云雾+豆包绕过 Google API 直连问题。

### html-video

| 服务 | 必需？ | 用途 | 获取方式 |
|------|--------|------|----------|
| **MiniMax API Key** | ❌ 可选 | AI 背景音乐 + TTS 旁白 | 注册 MiniMax |
| **Anthropic API Key** | ❌ 可选 | 无 CLI agent 时的 fallback | 注册 Anthropic |
| **Coding Agent** | ⚠️ 实质必需 | 生成 content-graph + HTML | 安装 14 种之一（Claude Code / Cursor 等） |

> 核心渲染完全本地，API Key 仅用于可选音频。但**必须有一个 coding agent**，否则无法生成内容。

### video-producer (ours)

| 服务 | 必需？ | 用途 | 获取方式 |
|------|--------|------|----------|
| **SILICONFLOW_API_KEY** | ✅ 必需 | TTS、ASR、视频生成 | 注册硅基流动（国内服务，免费额度） |
| **PEXELS_API_KEY** | ❌ 可选 | 素材库下载 | 注册 Pexels（免费） |
| **PIXABAY_API_KEY** | ❌ 可选 | 素材库下载 | 注册 Pixabay（免费） |
| **VOLCENGINE_API_KEY** | ❌ 可选 | de-mouth 高精度 ASR（词级时间戳） | 注册火山引擎 |

> 所有必需/推荐服务均为**国内可直连**，无 GFW 问题。

---

## 6. 配音/音频能力（专项对比）

| | ViMax | html-video | video-producer (ours) |
|--|-------|------------|----------------------|
| **TTS 引擎** | ❌ 无 | MiniMax TTS（可选） | SiliconFlow MOSS-TTSD-v0.5 |
| **配音方式** | 依赖视频生成 API 的音频能力 | 独立 TTS → ffmpeg 混入 MP4 | 独立 TTS → ASR 自检 → ffmpeg 混入 |
| **旁白控制** | ❌ 无法控制音色/语速/情感 | ✅ 可输入旁白脚本 | ✅ 5 种音色可选，可调语速 |
| **背景音乐** | ❌ 无 | MiniMax 生成（可选） | ❌ 无（可手动混入） |
| **ASR 回查** | ❌ 无 | ❌ 无 | ✅ Jaccard 相似度 ≥ 0.5 自检 |
| **去口误/后处理** | ❌ 无 | ❌ 无 | ✅ de-mouth skill |
| **字幕** | ❌ 无 | ❌ 无 | ✅ SRT 生成 |

### ViMax 配音机制详解

ViMax 没有独立的 TTS 实现。其 `ShotDescription` 中有 `audio_desc` 字段，但仅作为视频生成 API prompt 的一部分：

```python
# script2video_pipeline.py
video_output = await self.video_generator.generate_single_video(
    prompt=shot_description.motion_desc + "\n" + shot_description.audio_desc,
    ...
)
```

`audio_desc` 示例：
```
[Sound Effect] Ambient sound (supermarket background noise, shopping cart wheels rolling)
[Speaker] Alice (Happy): Hello, how are you?
```

源码中还有被注释掉的结构化音频字段（`speaker`、`line`、`emotion`、`is_speaker_lip_visible`），说明曾计划更细粒度的音频控制，但最终简化为自由文本。

**影响**：
1. 质量不可控——Veo/Seedance 的音频生成质量远不如专业 TTS
2. 无法后期修正——没有独立音轨，不能调速、去口误、换音色
3. 无法做旁白型视频——没有"先出音频再配画面"的能力
4. 对话/台词场景勉强可用——Veo 端到端音视频生成可能比 TTS+对口型更自然，但仅适合叙事类

---

## 7. ViMax 依赖纠正记录

| 项目 | 之前结论 | 实际情况 | 证据 |
|------|---------|---------|------|
| GPU 需求 | 🔴 必需 CUDA 12.8 | 🟢 不需要 | 源码无任何 `import torch`，所有生成走云端 API |
| faiss 使用 | 🔴 每次生成都用 | 🟢 仅 Novel2Video（未完成） | `novel2movie_pipeline.py` 头部标注 `# TODO: NOT IMPLEMENTED YET`，Idea2Video/Script2Video 无 faiss |
| opencv 角色 | 🔴 重处理 | 🟢 仅图片 I/O 辅助 | `utils/image.py` 中 cv2 仅用于下载和 base64 转换 |
| 配音能力 | 未深入 | ❌ 无独立 TTS | `audio_desc` 仅拼入视频生成 prompt，无 TTS API 调用 |
| 国内可用性 | 🔴 Google API 难获取 | 🟡 有云雾代理+豆包备选 | 内置 `*_yunwu_api.py` 和 `*_doubao_*_api.py` 适配器 |

---

## 8. 综合评价

| | ViMax | html-video | video-producer |
|--|-------|------------|----------------|
| **定位** | AI 叙事长视频工作室 | HTML 动画视频 meta-layer | 实用型视频生产流水线 |
| **核心优势** | AI 画面生成 + 角色连贯 + 多镜头 | 21 模板 + 本地渲染 + 零 API 费用 | TTS+质检+去口误+全流程自动化 |
| **核心劣势** | 无配音/TTS、无模板、无后处理 | 无 AI 视频生成、无口播/后处理 | 每个方向深度有限、无模板库 |
| **适合场景** | AI 生成叙事短片（故事/奇幻/角色） | 数据可视化/产品宣传/标题动画 | 口播解说/教程/素材拼接/去口误 |
| **与我们的互补性** | 🟡 中。AI 画面生成能力可借鉴 | 🟢 高。HyperFrames 我们已用，模板库+Studio UI+content-graph 可直接增强 | — 基准 |

### 整合方向建议

1. **html-video 与 video-producer 互补性最强**——我们已用 HyperFrames 作为渲染引擎，html-video 的 21 模板库、content-graph 多帧分镜 IR、Studio UI 正好补足我们"无模板、无可视化编排"的短板。整合路径清晰：模板→HyperFrames 适配→我们的质检/拼接流水线。

2. **ViMax 的 AI 视频生成思路可借鉴**，但直接整合代价大（langchain 全家桶+多 Agent 框架）。其多 Agent 编排和角色一致性方案值得研究。云雾代理+豆包适配器说明国内可用性比预期好。

3. **三者覆盖的视频类型几乎互不重叠**——ViMax 擅长 AI 生成叙事、html-video 擅长 HTML 动画信息视频、我们擅长 TTS 口播+后处理。理想方案是取 html-video 的模板/分镜 + ViMax 的 AI 画面生成思路 + 我们的质检/拼接/去口误，形成完整链路。
