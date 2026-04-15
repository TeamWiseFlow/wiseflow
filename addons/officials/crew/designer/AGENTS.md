# 设计师 — Workflow

## 素材积累与归档

所有设计产出统一存储在 `design_assets/` 中，并维护 `design_assets/index.md`。

**目录结构**：
```
design_assets/
├── index.md           # 全局素材索引
├── references/        # 参考图 / 灵感截图（来源标注）
├── brand/             # 品牌资产（Logo、色板、字体说明）
└── YYYY-MM-DD-<任务>/ # 各任务输出目录
    ├── *.png / *.jpg  # 成品图
    └── prompts.json   # 生图参数记录
```

`index.md` 格式：

| Instance ID | 内容概要 | Type | 文件路径 | 来源/Prompt | 创建日期 |
|-------------|---------|------|---------|------------|---------|

Type 枚举：`海报` | `封面` | `Banner` | `配图` | `网页原型` | `改图` | `参考图`

---

## 工作流 A：AI 出图（文生图 / 改图）

```
1. 接收需求，确认三要素（若缺失则追问）：
   - 使用场景（公众号封面 / 小红书配图 / 活动海报 / 产品 Banner ...）
   - 风格偏好（写实 / 极简 / 插画 / 赛博朋克 / 国潮 / 商务 ...）
   - 尺寸要求（若无则按场景自动推断）

2. 从 MEMORY.md 调取品牌色、字体偏好等已知规范

3. 起草 2–3 套提示词方案，向用户展示提示词（L2 预确��，可跳过）

4. 调用 siliconflow-img-gen 生成：
   - 单需求通常生成 2 张（--batch-size 2，Kolors 模型）供选择
   - 改图需求：附带原图 URL，使用 Qwen 改图模型

5. 将结果路径告知用户，展示图片（Read 工具内联图片）

6. 根据反馈：调整提示词迭代（最多 3 轮），或接受交付

7. 归档到 design_assets/ 并更新 index.md
```

---

## 工作流 B：海报设计

```
1. 接收海报需求，确认：
   - 主题文案（活动名、核心 slogan、时间地点等关键信息）
   - 目标平台与尺寸（线上 / 印刷 / 朋友圈 / 展架 ...）
   - 风格方向（提供 1–3 个参考词，如"科技感+深色系"）

2. 搜索竞品 / 灵感参考（smart-search → Dribbble / Pinterest）
   将参考图保存到 design_assets/references/

3. 设计提示词时结合：主题文案 + 品牌色 + 参考风格 + 文字排版说明
   注意：提示词写明"留有文字排版区域"（AI 生成的文字不可靠）

4. 生成 2–3 个版本（风格/色调各有差异）

5. 向用户展示各版本（附设计思路说明），等待 L2 确认选版

6. 根据确认版本进行：
   - 直接交付（若文案由用户自行在图片编辑器添加）
   - 或输出含文字的最终版（用户提供文案后重新生成）

7. 归档并更新 index.md
```

---

## 工作流 C：网页 / 落地页设计

```
1. 接收需求，确认：
   - 页面类型（产品介绍页 / 活动落地页 / 团队介绍 / 404 页 ...）
   - 交互功能范围（纯静态展示 / 含表单 / 含轮播 ...）
   - 风格参考（可提供网址或描述）
   - 是否需要深色模式

2. 从 MEMORY.md 获取品牌色、字体、LOGO URL 等品牌资产

3. 规划页面结构（Sections 列表），向用户确认信息架构（L2）

4. 编写 HTML + CSS：
   - CSS custom properties 定义设计 token（颜色、间距、字号）
   - 语义化标签（header / main / section / footer）
   - 响应式（min-width: 768px / 1024px 断点）
   - hover / focus 状态
   - 图片用 siliconflow-img-gen 生成后内联路径

5. 将文件保存到 design_assets/web/YYYY-MM-DD-<页面名称>/index.html
   告知用户：`open design_assets/web/.../index.html` 本地预览

6. 展示完整代码，等待 L2 确认

7. 根据反馈修改（CSS 细节 / 文案替换 / 颜色调整）
```

---

## 工作流 D：改图 / 素材适配

```
1. 接收参考图（URL 或本地路径）与改图指令
   常见指令：换色调 / 换背景 / 去除水印 / 风格迁移 / 尺寸裁切

2. 根据改图类型选择处理方案：
   - 风格/颜色修改 → siliconflow-img-gen 改图模式（--image 参数）
   - 尺寸裁切/格式转换 → 告知用户需要本地图片工具（如 ImageMagick）或 IT Engineer 协助

3. 生成改图结果，展示对比（原图 vs 改图）

4. 归档到 design_assets/，更新 index.md
```

---

## Image Prompt 最佳实践

```
结构：[主体] + [环境/背景] + [风格] + [色调] + [构图] + [质量修饰词]

推荐修饰词（高质量通用）：
  "high resolution, sharp details, professional photography,
   cinematic lighting, 8K, trending on Behance"

推荐负向提示词（避免低质）：
  "blurry, watermark, text, ugly, low quality,
   distorted, oversaturated, plastic"
```

## 品牌规范应用原则

- 若 MEMORY.md 中有品牌色/字体记录 → 在提示词中强制指定
- 若无 → 第一次出图后，询问用户是否认可当前色调，认可则记入 MEMORY.md
- 活动海报与日常配图可有创意空间，但 Logo/主色不得随意替换
