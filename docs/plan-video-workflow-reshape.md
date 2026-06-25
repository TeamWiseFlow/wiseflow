# Video Production Workflow 重塑方案 v4

> 基于 html-video (https://github.com/bigbrother666sh/html-video) 深度调研
> 调研日期：2026-06-12
> 状态：**方案设计 v4，待确认**

---

## 0. 核心架构：Video Producer 三工作流 × 双模式

```
Video Producer
├── 模式 A: subagent（被 Media Operator spawn）
├── 模式 B: binding（用户直接交互）
│
├── 工作流 1: html-video（主力）
│   └── 脚本 → content-graph → 全帧统一走 html-video → exportMp4 → 封面
│
├── 工作流 2: ui-demo（浏览器录制）
│   └── URL + 交互脚本 → Patchright (Node.js) 录制 → MP4
│
└── 工作流 3: de-mouth（后处理）
    └── 视频 → ASR 词级时间戳 → 检测口误/填充词 → 切割重编码 → MP4
```

**Media Operator 彻底解耦**：只负责出 `script.md`，不再介入制作细节。Video Producer 全权负责从脚本到成品。

**集成方式**：html-video CLI 调用。Agent 独立完成工作，不需要 UI，中间过程不让用户过多干预。

---

## 1. 核心设计决策：video-clip 模板统一所有帧

### 1.1 问题

html-video 的 `FrameRecord.htmlPath` 是必需字段——每帧必须从 HTML 渲染。用户提供的 MP4 素材、AI 生成的视频片段不能直接作为帧。

### 1.2 解决方案：video-clip 模板

创建 `video-clip-916` 模板，将视频素材包装为 HTML 帧，统一走 html-video 渲染管线：

```html
<!-- templates/video-clip-916/source/index.html -->
<div id="scene"
     data-width="1080" data-height="1920"
     data-duration="PLACEHOLDER_DURATION">
  <video id="bg-video"
         src="PLACEHOLDER_VIDEO_SRC"
         autoplay muted playsinline
         style="width:100%;height:100%;object-fit:cover;
                position:absolute;top:0;left:0;">
  </video>
  <!-- 可选文字叠加层 -->
  <div id="overlay" style="position:absolute;bottom:10%;left:5%;right:5%;
           opacity:0; transform:translateY(20px);">
    <h1 class="title">PLACEHOLDER_TITLE</h1>
    <p class="subtitle">PLACEHOLDER_SUBTITLE</p>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
  window.__timelines = {};
  const tl = gsap.timeline({ paused: true });
  tl.to("#overlay", { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }, 0.5);
  window.__timelines["video-clip"] = tl;
</script>
```

### 1.3 统一后的 content-graph

**所有节点都是 HTML 帧**，不再有 dynamic/stock 两条路径：

| 节点类型 | 模板 | 变量来源 |
|---------|------|---------|
| 标题动画 | `glitch-title-916` | agent 填充文案 |
| 文字动效 | `kinetic-type-916` | agent 填充文案 |
| 数据图表 | `data-chart-916` | agent 填充数据 |
| **素材片段** | **`video-clip-916`** | **video_generate / siliconflow-video-gen / pixabay / pexels → MP4 路径** |
| **用户提供片段** | **`video-clip-916`** | **用户提供的 MP4 路径** |
| **AI 生成片段** | **`video-clip-916`** | **siliconflow-video-gen 产出的 MP4 路径** |
| 结尾 CTA | `logo-outro-916` | agent 填充文案 |

### 1.4 素材获取流程（统一纳入 html-video）

```
content-graph 中 productionMode: "stock" 的节点:
  │
  ▼
① 获取素材 MP4
   优先级: video_generate → siliconflow-video-gen → pixabay-footage → pexels-footage
   产出: clip.mp4
      │
      ▼
② 注入 video-clip-916 模板
   PLACEHOLDER_VIDEO_SRC → clip.mp4 路径
   PLACEHOLDER_DURATION → ffprobe 获取时长
   PLACEHOLDER_TITLE / SUBTITLE → 可选文字叠加
      │
      ▼
③ html-video 正常渲染该帧（Chromium 加载 HTML → <video> 播放 → 录制 → MP4）
```

### 1.5 代价与收益

**代价**：
- 素材 MP4 经过 Chromium 重编码（录制→webm→mp4），有轻微质量损失
- 额外耗时：10 秒素材 ≈ 15 秒渲染（Chromium 实时录制）

**收益**：
- **fragment-assembly 完全移除**——html-video 的 `exportMp4` 处理全部帧的拼接 + 音频混合
- **content-graph 完全统一**——所有节点都是 HTML 帧，无 dynamic/stock 分叉
- **组装逻辑零自定义**——全走 html-video 标准管线
- **用户提供素材自然融入**——和 AI 生成素材完全同构处理

**判断**：对于 5-15 秒的短视频片段，重编码代价完全可接受。统一管线的收益远大于代价。

---

## 2. html-video 关键能力边界（调研确认）

### 2.1 html-video 能做什么

| 能力 | 说明 |
|------|------|
| **模板渲染** | HTML+CSS+GSAP → Chromium 录制 → MP4，含 animation freeze + font loading + duration probe |
| **逐帧渲染 + 全项目导出** | `exportMp4`：逐帧渲染 → `concatFramesWithFfmpeg` → `applySoundtrack` |
| **帧拼接** | stream copy（同引擎）或 re-encode（混合引擎） |
| **音频混合** | TTS + BGM + ducking(-18dB) + fade-in/out + AAC 192k |
| **MiniMax TTS** | speech-02-turbo，多音色/语速/情感 |
| **MiniMax Music** | music-1.5 BGM 生成 |
| **外部音频注入** | `applySoundtrack` 接受任意音频文件 |
| **Content-Graph IR** | nodes + edges + topo-sort 结构化分镜 schema |
| **21 模板库** | 含 manifest (JSON Schema inputs) + provenance + license |
| **模板注册表** | intent 驱动搜索 + 评分 + license 过滤 |

### 2.2 html-video 不能做什么（需要我们补充）

| 缺失 | 我们的补充 |
|------|-----------|
| **无内置分段** | agent 自行分析脚本 → 生成 content-graph（分段智能在 agent） |
| **无 AI 视频生成** | video_generate / siliconflow-video-gen 获取素材 → video-clip 模板包装 |
| **无素材库** | pixabay-footage / pexels-footage 获取素材 → video-clip 模板包装 |
| **无质量验证** | 模板渲染比手写 HTML 稳定得多，暂不需要 |
| **Remotion 适配器** | 代码存在但可能未 production-ready，首批只用 HyperFrames |

---

## 3. 技能去留决策（最终版）

### 3.1 移除

| 技能 | 原因 |
|------|------|
| `hyperframes-video-creation` | html-video HyperFrames 适配器完全覆盖，且更健壮 |
| `fragment-assembly` | html-video `exportMp4` 统一处理帧拼接 + 音频混合 |
| `content-check` | TDD 循环范式不匹配 html-video 的"时长预确定"范式 |
| `video-frames` | html-video 渲染管线内置帧处理 |
| `summarize` | 非视频核心能力，agent 自身能力覆盖 |

### 3.2 保留

| 技能 | 角色 |
|------|------|
| `siliconflow-tts` | TTS fallback（MiniMax 主力后） |
| `siliconflow-video-gen` | AI 视频生成（获取素材后走 video-clip 模板） |
| `pexels-footage` | 素材库（获取素材后走 video-clip 模板） |
| `pixabay-footage` | 素材库（获取素材后走 video-clip 模板） |
| `manim-explainer` | 公式/数学动画补充（frameIntent: "formula" 时可选） |
| `ui-demo` | 工作流 2（Node.js patchright） |
| `de-mouth` | 工作流 3 |

### 3.3 不碰

| 技能 | 原因 |
|------|------|
| `siliconflow-img-gen` | 全局公共技能，不属于 video-producer |

### 3.4 新增（来自 html-video + 自建）

| 能力 | 说明 |
|------|------|
| html-video CLI | 全管线渲染引擎 + 模板系统 + content-graph + 帧拼接 + 音频混合 |
| MiniMax TTS | 主力 TTS（speech-02-turbo） |
| MiniMax Music | BGM 生成（music-1.5） |
| 9:16 模板库 | 首批 5 个模板（4 个动画 + 1 个 video-clip） |

---

## 4. 工作流 1: html-video — 详细设计

### 4.1 端到端流程

```
输入: script.md（来自 Media Operator 或用户直接提供）
      │
      ▼
① Content-Graph 生成（agent 自行分段）
   - 分析 script.md 内容结构
   - 生成 content-graph.json（nodes + edges）
   - 每节点标注: frameIntent, templateRef, variables, hasTts
   - 分段智能在 agent，html-video 不参与
      │
      ▼
② 素材预获取（productionMode: "stock" 的节点）
   - 按优先级获取素材: video_generate → siliconflow-video-gen → pixabay → pexels
   - 用户提供的素材直接使用
   - 产出: clip.mp4 → 放入项目资产目录
      │
      ▼
③ 模板变量注入（所有节点）
   - animation 节点: 填充文案/数据变量
   - stock 节点: 填充 videoSrc + duration + 可选 overlay 文字
   - formula 节点: manim-explainer 渲染 → 产出 MP4 → video-clip 模板包装
   - 替换 HTML PLACEHOLDER → 写入帧目录
      │
      ▼
④ TTS 生成
   - 主力: MiniMax TTS (speech-02-turbo)
   - Fallback: SiliconFlow TTS (MOSS-TTSD-v0.5)
   - 可选: MiniMax Music 生成 BGM
   - 音频写入项目资产目录
      │
      ▼
⑤ html-video exportMp4（全项目渲染）
   - 逐帧渲染（HyperFrames 适配器）
   - 帧拼接（concatFramesWithFfmpeg）
   - 音频混合（applySoundtrack: TTS + BGM + ducking + fades）
   - 输出: video.mp4
      │
      ▼
⑥ 封面制作
   - 生成 1080x1920 封面图（必须包含标题文字）
      │
      ▼
   输出: final/video.mp4 + final/cover.jpg
```

### 4.2 Content-Graph 规范（统一版）

```json
{
  "schemaVersion": 1,
  "intent": "promo | explainer | data-viz | comparison | other",
  "synopsis": "视频概要描述",
  "nodes": [
    {
      "id": "hook-title",
      "kind": "text",
      "label": "开篇标题",
      "frameIntent": "intro",
      "durationSec": 4,
      "templateRef": "glitch-title-916",
      "variables": { "title": "99%的人都不知道", "subtitle": "这个赚钱方法" },
      "hasTts": true,
      "ttsText": "99%的人都不知道这个赚钱方法",
      "ttsVoice": "MiniMax:voice-1"
    },
    {
      "id": "product-demo",
      "kind": "entity",
      "label": "产品展示",
      "frameIntent": "image-pan",
      "durationSec": 8,
      "templateRef": "video-clip-916",
      "variables": { "videoSrc": "assets/product-clip.mp4", "title": "一键搞定" },
      "stockSource": "video_generate | siliconflow-video-gen | pixabay | pexels | user-provided",
      "hasTts": true,
      "ttsText": "有了它，一键搞定",
      "ttsVoice": "MiniMax:voice-1"
    },
    {
      "id": "cta-outro",
      "kind": "text",
      "label": "结尾 CTA",
      "frameIntent": "outro",
      "durationSec": 4,
      "templateRef": "logo-outro-916",
      "variables": { "title": "立即体验", "subtitle": "链接在简介" },
      "hasTts": true,
      "ttsText": "立即体验，链接在简介",
      "ttsVoice": "MiniMax:voice-1"
    }
  ],
  "edges": [
    { "from": "hook-title", "to": "product-demo", "kind": "dependency", "reason": "先建立吸引再展示产品" },
    { "from": "product-demo", "to": "cta-outro", "kind": "sequence", "reason": "展示后接 CTA" }
  ]
}
```

**关键变化**：不再有 `productionMode` 字段。所有节点统一通过 `templateRef` 区分——动画模板 or video-clip 模板。

### 4.3 模板库

**P0（首批 5 个）**：

| 模板 | 原版 | 场景 | 改造要点 |
|------|------|------|---------|
| `glitch-title-916` | frame-glitch-title | 开篇 hook 标题动画 | 9:16 布局，中文标题 |
| `kinetic-type-916` | frame-kinetic-type | 中段卖点文字动效 | 9:16 布局，中文多行排版 |
| `data-chart-916` | frame-data-chart-nyt | 数据佐证可视化 | 9:16 竖向条形图 |
| `logo-outro-916` | frame-logo-outro | 结尾 CTA | 9:16 布局，品牌元素 |
| **`video-clip-916`** | **自建** | **素材/用户提供/AI 生成片段** | **`<video>` 播放 + 可选文字叠加** |

**P1（第二批 3 个）**：

| 模板 | 原版 | 场景 |
|------|------|------|
| `product-promo-916` | frame-product-promo | 产品展示 |
| `decision-tree-916` | frame-decision-tree | 决策/流程解说 |
| `bold-poster-916` | frame-bold-poster | 大字报/引言 |

**P2（第三批 3 个）**：

| 模板 | 原版 | 场景 |
|------|------|------|
| `liquid-hero-916` | frame-liquid-bg-hero | 液态背景英雄区 |
| `light-leak-916` | frame-light-leak-cinema | 电影感光效过渡 |
| `warm-grain-916` | frame-warm-grain | 温暖胶片质感 |

### 4.4 TTS 策略

```
TTS 优先级:
1. MiniMax TTS (speech-02-turbo) — 主力
2. SiliconFlow TTS (MOSS-TTSD-v0.5) — fallback

BGM:
1. MiniMax Music (music-1.5) — 主力
2. 用户提供的音频文件 — 直接注入

音频混合（html-video applySoundtrack 处理）:
- TTS narration 音轨
- BGM 音轨（自动 ducking，TTS 时 BGM 降 -18dB）
- Fade-in/out（自动计算）
- AAC 192kbps 编码
```

### 4.5 素材获取优先级

```
video_generate（openclaw 原生，14+ 供应商自动 fallback）
  → siliconflow-video-gen（Wan2.2 T2V/I2V）
    → pixabay-footage
      → pexels-footage
```

获取后统一走 `video-clip-916` 模板注入 html-video 管线。

### 4.6 html-video CLI 集成

```bash
# 安装（addon 根目录 package.json 声明依赖）
pnpm install

# 全项目渲染（核心用法）
html-video render <project-dir> --format mp4 --resolution 1080x1920 --fps 30

# 模板搜索（agent 用来选模板）
html-video templates search --intent "title animation"
```

**关键**：用 html-video 的 `exportMp4` 做全项目端到端渲染（逐帧渲染 + 拼接 + 音频混合），不再自己写组装逻辑。

**addon 依赖管理**（遵循 CLAUDE.md 规范）：
- video-producer addon 根目录添加 `package.json`
- html-video + pnpm 作为 Node.js 依赖
- Python 脚本（TTS fallback、素材获取）保持不变
- 整个 addon 作为一个混合包（Node.js 渲染 + Python 辅助）

---

## 5. 工作流 2: ui-demo — 保持现有

```
输入: 目标 URL + 交互脚本
      │
      ▼
① Patchright (Node.js) 启动目标页面
② 按交互脚本执行操作（点击/输入/滚动/等待）
③ CDP recordVideo → WebM
④ ffmpeg 转码 → MP4 (9:16)
      │
      ▼
   输出: demo video.mp4
```

**技术栈**：Node.js patchright（`const { chromium } = require('patchright')`，`.cjs` 脚本，`node demo-script.cjs` 执行）。**不使用 Python patchright。**

**无改动**，保留现有 `ui-demo` 技能。

---

## 6. 工作流 3: de-mouth — 保持现有

```
输入: 视频文件
      │
      ▼
① ASR 词级时间戳（火山引擎优先 / SiliconFlow fallback）
② 检测填充词（嗯/啊/那个/就是/然后…）和口误
③ 标记切割点 → ffmpeg 精确切割
④ 重编码拼接 → MP4
      │
      ▼
   输出: cleaned video.mp4
```

**无改动**，保留现有 `de-mouth` 技能。

---

## 7. Media Operator 解耦设计

### 7.1 当前：Media Operator 深度介入

```
Media Operator:
  → 获取文章
  → 创作脚本
  → 拆分片段（决定生产模式、技能选择）
  → 初始化片段目录
  → 补齐需求文档
  → 预置素材
  → spawn video-producer × N
  → 最终组装
  → 封面制作
  → 用户确认
```

### 7.2 重塑后：Media Operator 只出脚本

```
Media Operator:
  → 获取文章
  → 创作脚本 → script.md
  → 用户确认脚本
  → spawn video-producer（传入 script.md + 风格偏好 + 业务约束）
  → 等待成品
  → 用户确认成品

Video Producer (全权负责):
  → 读取 script.md
  → 生成 content-graph（自行分段）
  → 素材预获取（stock 节点）
  → 模板变量注入（所有节点）
  → TTS 生成
  → html-video exportMp4（全项目渲染）
  → 封面制作
  → 返回成品
```

**Media Operator 的 video-product SKILL.md 大幅精简**：只保留：
- Step 0: 准备工作（获取文章）
- Step 1: 脚本创作 + 评估
- Step 2: 定稿 + 用户确认
- Step 3: spawn video-producer（传入脚本 + 约束）
- Step 4: 用户确认成品

---

## 8. Video Producer AGENTS.md 重写要点

### 8.1 三工作流入口

```markdown
## 工作流选择

收到任务后，首先判断工作流：

| 条件 | 工作流 |
|------|--------|
| 任务是"根据脚本/文章生成视频" | → 工作流 1: html-video |
| 任务是"录制产品 Demo / 操作教程" | → 工作流 2: ui-demo |
| 任务是"去除口误/填充词" | → 工作流 3: de-mouth |
| 任务是"HD 导出 / 格式转换" | → 工作流 3: de-mouth（复用其 ffmpeg 能力） |
```

### 8.2 工作流 1 详细步骤

```markdown
## 工作流 1: html-video

### Step 1 — Content-Graph 生成
分析 script.md，自行决定分段，生成 content-graph.json：
- 每个语义段落 → 一个 node
- 标注 frameIntent（intro/data-bar/quote/outro/formula/image-pan）
- 选择模板：animation 场景 → 动画模板; 素材场景 → video-clip-916
- 帧间关系 → edges（sequence/dependency/contrast）

### Step 2 — 素材预获取
需要素材的节点（templateRef: "video-clip-916"）：
  → 按优先级获取: video_generate → siliconflow-video-gen → pixabay → pexels
  → 用户提供的素材直接使用
  → 产出 clip.mp4 → 放入项目资产目录

### Step 3 — 模板变量注入
所有节点：
  → 替换 HTML PLACEHOLDER → 写入帧目录
  → stock 节点: videoSrc → clip.mp4 路径, duration → ffprobe 获取

### Step 4 — TTS 生成
有 hasTts 的节点：
  → MiniMax TTS 生成（主力）
  → 失败时 SiliconFlow TTS（fallback）
可选：MiniMax Music 生成 BGM

### Step 5 — html-video 全项目渲染
html-video render <project-dir>：
  → 逐帧渲染（HyperFrames 适配器）
  → 帧拼接（concatFramesWithFfmpeg）
  → 音频混合（applySoundtrack）

### Step 6 — 封面制作
生成 1080x1920 封面图（必须包含标题文字）
```

---

## 9. html-video 最长视频限制

**无总时长硬限制。** 逐帧独立渲染再 concat：

| 视频时长 | 帧数估算 | 渲染时间估算 | 可行性 |
|---------|---------|------------|--------|
| 30 秒 | 5-10 帧 | 1-2 分钟 | ✅ 毫无压力 |
| 1 分钟 | 10-20 帧 | 2-5 分钟 | ✅ 很轻松 |
| 3 分钟 | 20-40 帧 | 5-15 分钟 | ✅ 可行 |
| 5 分钟 | 30-60 帧 | 10-25 分钟 | ⚠️ 可行但需耐心 |
| 10 分钟 | 60-120 帧 | 20-50 分钟 | ⚠️ 建议分段 |

---

## 10. 实施计划

### Phase 1: html-video 集成基础（2-3 天）

1. 在 video-producer addon 根目录创建 `package.json`，添加 html-video 依赖
2. 安装并验证 html-video CLI 可用
3. 测试全项目渲染：创建项目 → 写 content-graph → 写帧 HTML → render → MP4
4. 配置 MiniMax API Key（MINIMAX_API_KEY 环境变量）
5. 测试 MiniMax TTS + Music 生成

**交付物**：html-video CLI 可用 + MiniMax 音频可用

### Phase 2: 模板库建设（2-3 天）

1. 创建模板目录结构 `templates/`
2. 定义 `template.yaml` manifest 规范
3. 从 html-video 提炼 4 个 P0 动画模板，改造为 9:16：
   - `glitch-title-916`
   - `kinetic-type-916`
   - `data-chart-916`
   - `logo-outro-916`
4. **自建 `video-clip-916` 模板**（`<video>` 播放 + 可选文字叠加）
5. 每个模板测试渲染
6. 写模板注册表脚本

**交付物**：5 个 P0 模板 + 注册表脚本

### Phase 3: Content-Graph + 工作流重写（2-3 天）

1. 定义 content-graph.json 规范（统一版，无 productionMode）
2. 写 `content_graph.py`（validate + topo_sort）
3. 重写 video-producer AGENTS.md：三工作流入口 + 工作流 1 详细步骤
4. 精简 video-product SKILL.md：只保留脚本创作 + spawn + 确认
5. 端到端测试：script.md → content-graph → 素材获取 → 模板注入 → html-video render → 成品

**交付物**：重写后的 AGENTS.md + SKILL.md + content_graph.py

### Phase 4: 技能清理 + BUILTIN_SKILLS 更新（0.5 天）

1. 移除 `hyperframes-video-creation`、`fragment-assembly`、`content-check`、`video-frames`、`summarize` 技能目录
2. 更新 BUILTIN_SKILLS 列表
3. 更新 ALLOWED_COMMANDS（添加 html-video CLI 命令）
4. 验证两种模式（subagent + binding）均可用

**交付物**：清理后的技能清单

### Phase 5: 模板库扩展 + 迭代（持续）

- P1 模板：product-promo-916、decision-tree-916、bold-poster-916
- P2 模板：liquid-hero-916、light-leak-916、warm-grain-916
- 根据使用反馈迭代模板质量和变量设计

---

## 11. 风险评估

| 风险 | 等级 | 缓解 |
|------|------|------|
| html-video 是 Node.js monorepo，集成到 Python addon 需混合包管理 | 🟡 中 | addon 根目录加 package.json，Python 脚本通过 subprocess 调用 CLI |
| 模板从 16:9 改 9:16 布局工作量大 | 🟡 中 | GSAP 动画逻辑不变，只改 CSS 布局 + 分辨率；先做 4 个 P0 验证 |
| video-clip 模板重编码素材导致质量损失 | 🟢 低 | 5-15 秒片段的重编码损失可忽略；如未来不可接受可加 passthrough 适配器 |
| MiniMax API 国内可用性 | 🟢 低 | MiniMax 本身国内服务（api.minimaxi.com），SiliconFlow 作 fallback |
| 去掉 content-check 后无质量验证 | 🟢 低 | 模板渲染比手写 HTML 稳定得多；素材帧是下载/生成的成品无需验证 |
| Remotion 适配器可能未 production-ready | 🟢 低 | 首批只用 HyperFrames 适配器 |
| Media Operator 解耦后 video-producer 自主权变大 | 🟡 中 | script.md 中可含风格/约束/禁用项；video-producer 必须遵守 |

---

## 12. 预期收益

| 维度 | 改造前 | 改造后 |
|------|--------|--------|
| **动态片段生产** | 5-10 分钟/片段（手写 HTML + 调试） | 1-2 分钟/片段（填模板变量 + 渲染） |
| **动画质量** | 不稳定（依赖 agent 生成质量） | 稳定（模板预验证 + animation freeze + font loading） |
| **音频能力** | TTS only，无 BGM | TTS + BGM 生成 + ducking + fades |
| **素材处理** | 独立路径，与模板帧分叉 | 统一 video-clip 模板，全走 html-video |
| **模板复用** | 0% | 60-80%（常见场景走模板） |
| **编排结构** | 扁平数组 | 结构化 content-graph + 依赖关系 |
| **组装逻辑** | 自写脚本（fragment-assembly） | 零自定义（html-video exportMp4） |
| **Media Operator 复杂度** | 高（深度介入制作） | 低（只出脚本） |
| **Video Producer 自主性** | 低（按 media-operator 指令执行） | 高（全权负责从脚本到成品） |
| **工作流覆盖** | 1 个（视频生产） | 3 个（html-video + ui-demo + de-mouth） |

---

## 13. 待确认

1. **整体方向**：Video Producer 三工作流 × 双模式 + Media Operator 只出脚本 + video-clip 模板统一所有帧？
2. **MiniMax API Key**：是否已有？还是需要注册？
3. **P0 模板选择**：5 个（glitch-title / kinetic-type / data-chart / logo-outro / **video-clip**）是否合适？
4. **实施顺序**：Phase 1→2→3→4 是否可接受？还是希望先做 POC？
5. **已部署实例同步**：改造完成后是否立即同步到 `~/.openclaw/workspace-video-producer/`？
