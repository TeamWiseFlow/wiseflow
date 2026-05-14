---
name: ppt-maker
description: 从文稿内容生成专业 PPTX 演示文稿，支持用户提供的模板/参考图风格提取、AI 配图（siliconflow-img-gen）和素材图库（pexels/pixabay）。纯 Python 生成，无需 Google/ChatGPT API。
metadata:
  openclaw:
    emoji: 📊
    requires:
      bins:
      - python3
    primaryEnv: SILICONFLOW_API_KEY
    install:
    - id: brew
      kind: brew
      formula: libreoffice
      bins:
      - libreoffice
      label: Install LibreOffice (brew)
---

# PPT Maker

从文稿内容生成专业 `.pptx` 演示文稿。支持：

- **模板风格提取**：上传参考 PPTX 或截图，自动提取配色与布局
- **AI 配图**：通过 `siliconflow-img-gen` 生成封面及内容页配图（替换 Google/ChatGPT API）
- **素材图库**：可扩展接入 pexels-footage / pixabay-footage 获取免版税图片
- **纯 Python 生成**：JSON → python-pptx，无需 Node.js 或外部 API（除图片生成外）

## 依赖

```bash
pip install python-pptx
```

本脚本依赖 `python-pptx`。若未安装，脚本会提示安装命令。

## 工作流

```
用户提供文稿 + 可选模板
        │
        ▼
┌───────────────────┐
│ Step 1: 风格分析   │  ← 若有模板 PPTX：运行 extract 命令提取主题
│                   │  ← 若有参考截图：LLM 分析配色/布局
│                   │  ← 若无模板：使用默认主题或与用户确认风格
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Step 2: 大纲生成   │  ← LLM 分析文稿结构，规划每页内容与布局
│                   │  ← 确定哪些页面需要配图
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Step 3: 配图准备   │  ← AI 图：siliconflow-img-gen（16:9 封面/内容插图）
│                   │  ← 素材图：pexels-footage / pixabay-footage（可选）
│                   │  ← 用户图：直接引用用户提供的图片路径
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Step 4: PPTX 生成  │  ← 组装 JSON 配置，运行 generate_pptx.py
│                   │  ← 输出 .pptx 文件
└────────┬──────────┘
         │
         ▼
┌───────────────────────┐
│ Step 5: 视觉校验       │  ← 逐页转 PNG，LLM 视觉模型审阅排版
│  （必须执行）          │  ← 检查字体大小、布局偏移、元素重叠等
│                       │  ← 发现问题 → 修复 JSON → 重新生成 → 再校验
└────────┬──────────────┘
         │
         ▼
    交付 PPTX 文件
```

### Step 1: 风格分析

#### 1a. 用户提供了模板 PPTX

```bash
python3 {baseDir}/scripts/generate_pptx.py \
  --extract-style \
  --template /path/to/template.pptx
```

输出模板的主题信息（配色、字体、布局）。将提取的颜色映射到 JSON 配置的 `theme` 字段。

若 `python-pptx` 未安装，脚本返回 error 提示。此时询问用户是否安装，或改用 LLM 分析模式（见 1c）。

#### 1b. 用户提供了参考截图

使用 LLM 分析截图的视觉风格，提取：

```json
{
  "colors": {
    "primary": "#1E3A8A",
    "accent": "#E94560",
    "background": "#FFFFFF",
    "text": "#1F2937"
  },
  "layout": "标题左上 + 内容居中",
  "typography": "标题加粗 36px + 正文 18px"
}
```

将提取的配色映射到 config JSON 的 `theme` 字段。

#### 1c. 无模板（默认主题）

向用户确认风格方向：
- **商务专业**：深蓝主色 + 白底（`primary_color: "1A3C6E"`）
- **科技活力**：深海军蓝 + 电光蓝强调（`primary_color: "0F172A"`, `accent_color: "38BDF8"`）
- **极简白**：白底 + 单色强调（`primary_color: "1A1A1A"`, `background_color: "FFFFFF"`）
- 或用户自定义

### Step 2: 大纲生成

LLM 分析文稿内容，输出每页的结构规划：

```
1. 封面页（cover）
   - 标题：{主标题}
   - 副标题：{副标题}
   - 配图：AI 生成抽象科技背景

2. 目录页（toc）
   - 章节：{3-5 个章节}

3. 章节分隔页（section）
   - "01 市场概览"

4-N. 内容页（content / two_column / image_full）
   - 标题 + 要点 + 配图位置

N+1. 结束页（ending）
```

将大纲展示给用户确认后再继续。

### Step 3: 配图准备

#### 优先级策略

| 图片类型 | 首选方案 | 备选方案 |
|---------|---------|---------|
| 封面背景图 | siliconflow-img-gen | 纯色背景 |
| 概念插图 | siliconflow-img-gen | pexels/pixabay 素材 |
| 数据图表 | 用户提供 | pexels/pixabay 素材 |
| 产品截图 | 用户提供 | — |
| Logo / 二维码 | 用户提供 | — |

#### 使用 siliconflow-img-gen 生成配图

```bash
# 封面背景（16:9）
python3 {baseDir}/../siliconflow-img-gen/scripts/gen.py \
  --prompt "抽象科技背景，{主题描述}，{主色调}渐变，现代简洁，适合PPT封面，16:9横幅" \
  --image-size 1664x928 \
  --out-dir ./tmp/ppt-images

# 内容页插图（16:9）
python3 {baseDir}/../siliconflow-img-gen/scripts/gen.py \
  --prompt "{页面主题}概念插图，扁平化设计风格，{主色调}主色调，简洁专业" \
  --image-size 1664x928 \
  --out-dir ./tmp/ppt-images
```

**生成后必须验证**：检查图片不是纯色白板（siliconflow 偶发异常），异常则重试（最多 3 次）。

#### 使用素材图库（可选，后续集成）

```
# pexels-footage（计划中）
python3 {baseDir}/../pexels-footage/scripts/search.py --query "business meeting" --orientation landscape

# pixabay-footage（计划中）
python3 {baseDir}/../pixabay-footage/scripts/search.py --query "technology abstract" --orientation horizontal
```

### Step 4: PPTX 生成

#### 组装 JSON 配置

参考 `references/slide-layouts.md` 了解每种 slide type 的 JSON 格式。

将 Step 1 的主题 + Step 2 的大纲 + Step 3 的图片路径组装为完整 JSON：

```json
{
  "theme": {
    "primary_color": "1A3C6E",
    "secondary_color": "16213E",
    "accent_color": "E94560",
    "background_color": "FFFFFF",
    "text_color": "333333",
    "heading_font": "Microsoft YaHei",
    "body_font": "Microsoft YaHei"
  },
  "slides": [
    {
      "type": "cover",
      "title": "季度业务汇报",
      "subtitle": "Q1 2026 工作总结",
      "author": "业务拓展部",
      "background_image": "./tmp/ppt-images/00.png",
      "background_color": "1A3C6E"
    },
    {
      "type": "toc",
      "title": "目录",
      "items": ["市场概览", "业绩亮点", "问题与挑战", "下季度规划"]
    }
  ]
}
```

将 JSON 写入文件（如 `./tmp/slides-config.json`）。

#### 运行生成脚本

```bash
python3 {baseDir}/scripts/generate_pptx.py \
  --config ./tmp/slides-config.json \
  --output ./output/presentation.pptx

# 若有模板 PPTX 需要继承母版/布局
python3 {baseDir}/scripts/generate_pptx.py \
  --config ./tmp/slides-config.json \
  --output ./output/presentation.pptx \
  --template /path/to/template.pptx
```

### Step 5: 视觉校验（必须执行）

PPTX 生成后，**必须逐页转为 PNG 图片**，用视觉模型审阅排版是否正确。这是自动化流程无法保证排版质量的关键环节。

#### 5a. 逐页转 PNG

```bash
python3 {baseDir}/scripts/pptx_to_png.py \
  --input ./output/presentation.pptx \
  --outdir ./tmp/ppt-pngs
```

此脚本依赖系统安装 LibreOffice（`libreoffice-impress`）。若未安装，脚本会给出安装提示。

转换完成后，`./tmp/ppt-pngs/` 目录下会生成 `Slide1.png`、`Slide2.png`... 每个文件对应一页幻灯片。

#### 5b. 逐页视觉审阅

**用 Read 工具打开每一张 PNG 图片**，逐页检查以下项目：

| 检查项 | 关注点 | 判定标准 |
|--------|--------|---------|
| **整体偏移** | 所有内容是否整体偏上/偏下/偏左/偏右 | 页边距均匀，内容居中 |
| **字体大小** | 标题/正文是否过大（撑爆）或过小（看不清） | 标题约 28-44pt，正文约 16-20pt，视觉比例协调 |
| **文字截断** | 长文本是否超出幻灯片边界被截断 | 文字完整显示，左右留白充足 |
| **元素重叠** | 文本框/图片/装饰条是否互相遮挡 | 各元素有清晰边界，不重叠 |
| **图片质量** | 配图是否正常显示、比例是否变形 | 图片清晰，横纵比正确，无占位符裸露 |
| **配色可读性** | 文字与背景对比度是否足够 | 深底浅字或浅底深字，能轻松阅读 |
| **整体感** | 各页风格是否统一，排版是否专业 | 风格一致，无突兀差异 |

**审阅流程**：

1. 用 `Read` 工具打开第一张 `Slide1.png`（封面），检查标题位置、背景图、强调线
2. 依次打开后续每张 PNG，逐页检查
3. 对每页记录：`PASS` 或 `FAIL（原因：xxx）`
4. 所有页面 `PASS` 才可进入交付步骤

#### 5c. 发现问题时

若任意页面 `FAIL`，按以下流程修复：

1. **分析根因**：定位是 JSON 配置的问题（字号/位置参数不对）还是脚本渲染逻辑问题
2. **修复 JSON 配置**：调整对应 slide 的配置参数（字号、位置、颜色等）
3. **重新生成**：运行 `generate_pptx.py` 重新生成 .pptx
4. **重新校验**：再次执行 5a → 5b，直到所有页面 `PASS`
5. **最多重试 3 轮**：若 3 轮后仍有问题，记录具体问题告知用户，不可无限循环

#### 5d. 常见问题速查

| 现象 | 可能原因 | 修复方法 |
|------|---------|---------|
| 所有内容整体偏下 | 幻灯片高度设置问题或模板母版偏移 | 检查 slide_height，或在 JSON 中统一调整各元素的 top 值 |
| 字体超大撑爆页面 | 字号参数过大 | 降低 `font_size`，封面标题不超过 44，正文不超过 20 |
| 中文显示方框 | 字体不支持中文 | 将 `heading_font`/`body_font` 改为 `"Microsoft YaHei"` 或 `"SimHei"` |
| 图片遮挡文字 | image_position 与实际布局冲突 | 改用 `"bottom"` 位置或将图片缩小 |
| 长列表溢出底部 | bullets 条数过多 | 拆分为多页，或缩小字号/行距 |

### Step 6: 交付

1. 确认 `.pptx` 文件已生成，视觉校验全部通过
2. 告知用户文件路径、幻灯片数量、使用的风格
3. 清理临时文件（`./tmp/ppt-images/`、`./tmp/ppt-pngs/` 和 `./tmp/slides-config.json`），除非用户要求保留

## 幻灯片类型速查

| type | 用途 | 关键字段 |
|------|------|---------|
| `cover` | 封面 | title, subtitle, author, background_image |
| `toc` | 目录 | title, items[] |
| `section` | 章节分隔 | number, title, subtitle |
| `content` | 标准内容 | title, body, bullets[], image, image_position |
| `two_column` | 双栏对比 | left_title, left_body[], right_title, right_body[] |
| `image_full` | 全图展示 | image, title, caption |
| `ending` | 感谢页 | title, subtitle, contact, qr_image |

详细 JSON 格式与示例见 `references/slide-layouts.md`。

## 反模式

- 不要在生成 PPTX 后跳过视觉校验（Step 5），这是最常见的排版质量问题来源
- 不要在用 `siliconflow-img-gen` 生成图片时设置 inline env var（`SILICONFLOW_API_KEY=... python3 ...`），API key 已在系统环境中
- 不要跳过图片生成后的验证步骤（纯色白板检查）
- 每页 slides JSON 必须包含 `type` 字段
- 颜色值不要带 `#` 前缀（python-pptx 要求）
- 图片路径使用绝对路径或相对于脚本执行目录的正确相对路径

## 交付清单

- [ ] 风格已确认（模板提取 / LLM 分析 / 默认主题）
- [ ] 大纲已与用户确认
- [ ] 配图已生成并验证（非纯色白板）
- [ ] JSON 配置已写为临时文件
- [ ] PPTX 已成功生成且文件非空
- [ ] **视觉校验已通过（逐页 PNG 审阅，所有页面 PASS）**
- [ ] 临时文件已清理（除非用户要求保留）
- [ ] 交付时说明文件路径、幻灯片数量、使用的模板/风格
