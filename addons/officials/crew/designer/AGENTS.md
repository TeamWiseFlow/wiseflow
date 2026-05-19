# 设计师 — Workflow

## 通用规则

### 任务文件夹

**每项设计任务必须先创建独立文件夹**，所有产出归档其中：

```bash
bash ./skills/init-workspace/scripts/init.sh <任务名>
```

产出目录结构：

```
design_assets/YYYY-MM-DD-<任务名>/
├── brief.md        # 设计需求文档（必须填写，确认后不可跳过）
├── prompts.json    # 生图参数记录
├── source/         # 原始素材（参考图、品牌资产）
└── output/         # 成品输出
```

### Brief 确认机制

1. 接到需求后，将需求整理写入 `brief.md`
2. **将 brief 发给父 Agent / 用户确认**，等待明确同意
3. 确认前不得进入后续步骤
4. 后续视觉 review 以 brief 为基准对照

### 视觉 Review 机制

生成图片后**必须**调用视觉模型 review，不得跳过：

1. 用 `image` 工具查看生成结果
2. 对照 `brief.md` 逐项检查：主题文案是否体现、风格是否匹配、尺寸是否正确、品牌色是否准确
3. 发现偏差 → 调整提示词重新生成（最多 3 轮）
4. Review 通过 → 发送给用户/父 Agent

> 注：AI 生图偶尔返回纯色背景（无主体内容），也在此步骤排除——纯色图直接重试。

---

## 工作流 A：复杂图文设计（海报、邀请函、品牌 logo 等）

```
1. 接收需求 → 调用 init-workspace 创建任务文件夹
2. 将需求整理为 brief.md，包含：
   - 主题文案（活动名、slogan、时间地点等关键信息）
   - 目标平台与尺寸（线上/印刷/朋友圈/展架...）
   - 风格方向（1–3 个参考词，如"科技感+深色系"）
   - 品牌约束（品牌色、字体、LOGO — 从 MEMORY.md 获取）
3. 搜索竞品 / 灵感参考以丰富 brief.md：
   - 使用 smart-search 搜索竞品或相关设计灵感
   - 可以调用 image 工具获得素材的视觉描述作为参考
   - 综合搜索结果完善/丰富 brief.md
4. 将 brief 发给父 Agent / 用户确认，等待明确同意
5. 素材获取（按优先级）：
   a. pexels-footage / pixabay-footage 搜索下载免版权素材 → 保存到 source/
   b. 无合适素材时，使用 siliconflow-img-gen 生成底图 → 保存到 output/
      - 提示词必须结合：主题文案 + 品牌色 + 参考风格 + 文字排版说明
      - 提示词中写明"留有文字排版区域"（AI 生成的文字不可靠）
6. 合成产出
   按 brief.md 要求排版拼接原始素材，增加相关文字等，最终产出成稿
7. 视觉 Review（对照 brief.md）— 此步骤必须 `sessions_spawn` 独立的 subagent 完成：
   - 创建subagent(`designer`)按如下步骤进行 review
      - 用 image 工具查看产出成稿
      - 逐项检查：主题、风格、尺寸、品牌色是否与 brief.md 一致
      - 反馈待改动点
   - 按 subagent 返回重复 5～6 步骤，再次提交审核，直至没有待改动点或往复超过 3 轮。
8. 发给用户/父 Agent，根据反馈迭代修改
9. 最终确认后归档，更新 design_assets/index.md
```

---

## 工作流 B：网页 / 落地页设计

```
1. 接收需求 → 调用 init-workspace 创建任务文件夹
2. 将需求整理为 brief.md，包含：
   - 页面类型（产品介绍页/活动落地页/团队介绍/404 页...）
   - 交互功能范围（纯静态展示/含表单/含轮播...）
   - 风格参考（可提供网址或描述）
   - 是否需要深色模式
   - 品牌约束（品牌色、字体、LOGO — 从 MEMORY.md 获取）
3. 搜索竞品 / 灵感参考以丰富 brief.md：
   - 规划页面结构（Sections 列表），向用户确认信息架构
   - 使用 smart-search 搜索竞品或相关设计灵感
   - 可以调用 image 工具获得素材的视觉描述作为参考
   - 综合搜索结果完善/丰富 brief.md
4. 将 brief 发给父 Agent / 用户确认，等待明确同意
5. 素材获取：
   - 页面所需配图/背景图 → pexels-footage / pixabay-footage 优先，siliconflow-img-gen 备选
   - 下载/生成的图片保存到 source/ 目录
6. 编写 HTML + CSS：
   - CSS custom properties 定义设计 token（颜色、间距、字号）
   - 语义化标签（header / main / section / footer）
   - 响应式（min-width: 768px / 1024px 断点）
   - hover / focus 状态
   - 图片引用 source/ 中的素材
7. 视觉 Review（对照 brief.md）— 此步骤必须 `sessions_spawn` 独立的 subagent 完成：
   - 创建subagent(`designer`)按如下步骤进行 review
      - 用 image 工具对页面截图进行审查
      - 逐项检查：页面类型、交互元素、风格、深色模式、品牌色是否与 brief 一致
      - 按 subagent 返回重复 5～6 步骤，再次提交审核，直至没有待改动点或往复超过 3 轮。
8. 发给用户/父 Agent，根据反馈迭代修改
9. 最终确认后将文件保存到任务文件夹 output/ 目录，归档并更新 index.md
```

---

## 工作流 C：改图 / 素材适配

```
1. 接收需求 → 调用 init-workspace 创建任务文件夹
2. 将需求整理为 brief.md，包含：
   - 原始素材（URL 或本地路径）
   - 改图指令（换色调/换背景/去除水印/风格迁移/尺寸裁切...）
   - 期望效果描述
   - 品牌约束（如涉及色调修改，需注明品牌色）
3. 搜索竞品 / 灵感参考以丰富 brief.md：
   - 使用 smart-search 搜索竞品或相关设计灵感
   - 可以调用 image 工具获得素材的视觉描述作为参考
   - 综合搜索结果完善/丰富 brief.md
4. 将 brief 发给父 Agent / 用户确认，等待明确同意
5. 根据改图类型选择处理方案：
   a. 风格/颜色修改 → siliconflow-img-gen 改图模式（--image 参数）
      - --image 指向 source/ 中的原始素材
      - --out-dir 指向 output/ 目录
   b. 尺寸裁切/格式转换 → 告知用户需要本地图片工具（如 ImageMagick）或 IT Engineer 协助
6. 视觉 Review（对照 brief.md）— 此步骤必须 `sessions_spawn` 独立的 subagent 完成：
   - 创建subagent(`designer`)按如下步骤进行 review：
      - 用 image 工具对比原图与改图结果
      - 检查：改图指令是否准确执行、色调/风格是否符合 brief、是否引入不期望的变形
      - 按 subagent 返回重复 4～5 步骤，再次提交审核，直至没有待改动点或往复超过 3 轮。
7. Review 通过 → 展示对比（原图 vs 改图），发给用户/父 Agent 确认
8. 最终确认后归档，更新 design_assets/index.md
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
