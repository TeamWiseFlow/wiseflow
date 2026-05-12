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

### Step 5: 交付

1. 确认 `.pptx` 文件已生成且大小合理（非空）
2. 告知用户文件路径
3. 清理临时文件（`./tmp/ppt-images/` 和 `./tmp/slides-config.json`），除非用户要求保留

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
- [ ] 临时文件已清理（除非用户要求保留）
- [ ] 交付时说明文件路径、幻灯片数量、使用的模板/风格
