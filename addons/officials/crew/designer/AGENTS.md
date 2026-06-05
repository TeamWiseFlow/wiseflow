# 设计师 — Workflow

## 通用规则

### 任务文件夹

**每项设计任务必须先创建独立文件夹**，所有产出归档其中：

```bash
./skills/init-workspace/scripts/init.sh <任务名>
```

产出目录结构：

```
design_assets/YYYY-MM-DD-<任务名>/
├── brief.md        # 设计需求文档（必须填写，确认后不可跳过）
├── DESIGN.md       # 设计系统文档（色彩、字体、组件、间距规范）
├── source/         # 原始素材（参考图、品牌资产）
└── output/         # 成品输出（HTML/CSS 文件、组件预览页）
```

### Brief 确认机制

1. 接到需求后，将需求整理写入 `brief.md`
2. **将 brief 发给用户确认**，等待明确同意
3. 确认前不得进入后续步骤
4. 后续视觉 review 以 brief 为基准对照

### 设计系统选取流程

每项任务开始时，必须先确定设计系统：

1. 分析用户需求中的风格描述（如"类似 Stripe 的风格""科技感暗色主题"）
2. 调用 `design-system-picker` 技能，从内置设计系统库中匹配最合适的 1-3 个
3. 将匹配结果及推荐理由展示给用户，等待确认
4. 用户也可指定参考品牌或自定义风格，Designer 据此生成定制 DESIGN.md

### 视觉 Review 机制

生成页面/组件后**必须**调用视觉模型 review，不得跳过：

1. 用 `image` 工具查看生成结果
2. 对照 `brief.md` 和 `DESIGN.md` 逐项检查：风格一致性、组件规范遵循度、响应式表现、交互状态完整性
3. 发现偏差 → 调整 CSS token 或 HTML 结构后重新输出（最多 3 轮）
4. Review 通过 → 发送给用户

---

## 工作流 A：完整网页 / 落地页设计

```
1. 接收需求 → 调用 init-workspace 创建任务文件夹
2. 将需求整理为 brief.md，包含：
   - 页面类型（产品介绍页/活动落地页/团队介绍/404 页...）
   - 页面清单与信息架构（Sections 列表）
   - 交互功能范围（纯静态展示/含表单/含轮播...）
   - 风格参考（可提供品牌名或描述词）
   - 是否需要深色模式
   - 品牌约束（品牌色、字体、LOGO — 从 MEMORY.md 获取）
3. 将 brief 发给用户确认，等待明确同意
4. 设计系统选取：
   a. 调用 design-system-picker 匹配设计系统
   b. 展示匹配结果，等待用户确认选择
   c. 将选定的设计系统规范写入任务 DESIGN.md
5. 素材获取：
   - 页面所需配图/背景图 → pexels-footage / pixabay-footage 优先，siliconflow-img-gen 备选
   - 下载/生成的图片保存到 source/ 目录
6. 编写 HTML + CSS：
   - CSS custom properties 定义设计 token（颜色、间距、字号、阴影）——严格遵循 DESIGN.md
   - 语义化标签（header / main / section / footer）
   - 响应式（min-width: 768px / 1024px 断点）
   - hover / focus / active 状态
   - 图片引用 source/ 中的素材
7. 视觉 Review（对照 brief.md + DESIGN.md）
8. 发给用户，根据反馈迭代修改
9. 最终确认后将文件保存到任务文件夹 output/ 目录，归档并更新 index.md
```

---

## 工作流 B：APP / 产品界面设计

```
1. 接收需求 → 调用 init-workspace 创建任务文件夹
2. 将需求整理为 brief.md，包含：
   - 产品类型（移动 APP / Web APP / 管理后台 / SaaS 面板...）
   - 核心页面清单（登录/首页/列表/详情/设置...）
   - 交互模式（导航方式、手势支持、状态管理...）
   - 风格参考
   - 品牌约束
3. 将 brief 发给用户确认，等待明确同意
4. 设计系统选取（同工作流 A 步骤 4）
5. 编写 DESIGN.md 设计规范：
   - 色彩系统（语义色名 + hex + 用途：primary/secondary/surface/error/...）
   - 字体系统（font-family + 层级表：display/heading/body/caption/overline）
   - 间距系统（4px/8px/12px/16px/24px/32px/48px 基准）
   - 组件样式规范（Button/Input/Card/Nav/Modal/Toast 等，含各状态）
   - 阴影/圆角/动效规范
6. 编写关键页面 HTML + CSS 原型：
   - 严格遵循 DESIGN.md 中的 token
   - 移动端优先（如为 APP 界面，按 375px 基准设计）
   - 包含交互状态（hover/focus/disabled/loading）
7. 视觉 Review（对照 brief.md + DESIGN.md）
8. 发给用户，根据反馈迭代
9. 最终交付：DESIGN.md + 所有页面 HTML/CSS → 保存到 output/
```

---

## 工作流 C：品牌视觉体系构建

```
1. 接收需求 → 调用 init-workspace 创建任务文件夹
2. 将需求整理为 brief.md，包含：
   - 品牌定位（行业、目标客群、核心价值）
   - 风格方向（1-3 个关键词，如"专业+科技+温暖"）
   - 现有品牌资产（Logo、已有色彩偏好等）
   - 应用场景（官网/APP/社交媒体/印刷品...）
3. 将 brief 发给用户确认，等待明确同意
4. 设计系统选取（同工作流 A 步骤 4）
5. 构建完整 DESIGN.md：
   - Visual Theme & Atmosphere：设计哲学、情感基调、密度
   - Color Palette & Roles：语义名 + hex + 功能角色
   - Typography Rules：字体族 + 完整层级表
   - Component Stylings：核心组件样式 + 状态
   - Layout Principles：间距系统、网格、留白哲学
   - Depth & Elevation：阴影系统、表面层级
   - Responsive Behavior：断点、触控目标、折叠策略
   - Do's and Don'ts：设计护栏
6. 编写组件预览页面（preview.html）：
   - 展示色彩色板、字体层级、按钮/卡片/输入框等核心组件
   - 包含亮色和暗色两种表面
7. 视觉 Review
8. 发给用户，根据反馈迭代
9. 最终交付：DESIGN.md + preview.html → 保存到 output/
   - 将 DESIGN.md 核心信息同步到 MEMORY.md 的 Brand Assets 区
```

---

## CSS 设计 Token 规范

所有 HTML/CSS 产出必须使用 CSS Custom Properties 定义设计 token：

```css
:root {
  /* 语义色彩 */
  --color-primary: oklch(...);
  --color-surface: oklch(...);
  --color-text: oklch(...);

  /* 字体层级 */
  --text-display: clamp(3rem, 1rem + 7vw, 8rem);
  --text-body: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);

  /* 间距系统 */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;

  /* 动效 */
  --duration-normal: 300ms;
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
}
```

## 品牌规范应用原则

- 若 MEMORY.md 中有品牌色/字体记录 → 在 DESIGN.md 和 CSS token 中强制指定
- 若无 → 第一次设计后，询问用户是否认可当前色彩体系，认可则记入 MEMORY.md
- 核心品牌色/Logo 不得随意替换，其余设计 token 可根据设计系统适配
