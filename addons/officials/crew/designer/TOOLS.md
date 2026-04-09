# 设计师 — Tools

## Available Tools

| Tool | Purpose |
|------|---------|
| `siliconflow-img-gen` | AI 文生图 / 改图；海报、Banner、封面图、配图等视觉素材的核心生成工具 |
| `smart-search` | 搜索竞品设计参考、灵感图、免版权素材（Unsplash / Pexels / Dribbble 等） |
| `browser` + `browser-guide` | 访问设计参考网站、抓取页面截图、下载免版权图片 |
| `summarize` | 提炼长文档中的视觉需求要点（如 PRD、品牌手册） |
| `xurl` | 快速访问公开图片 CDN / API，获取素材 URL |

## Tool Usage Rules

### siliconflow-img-gen 使用规范

1. **尺寸映射**（优先使用标准尺寸）：

   | 场景 | 尺寸 | 参数 |
   |------|------|------|
   | 正方形配图 / 头像 | 1024×1024 | `--image-size 1024x1024` |
   | 竖版海报 / 小红书封面 | 960×1280 | `--image-size 960x1280` |
   | 横版 Banner / 公众号封面 | 1280×720 | `--image-size 1280x720` |
   | 手机壁纸 / 竖版视频封面 | 720×1280 | `--image-size 720x1280` |
   | 长图 / 信息图 | 720×1440 | `--image-size 720x1440` |

2. **模型选择**：
   - 默认：`Qwen/Qwen-Image-Edit-2509`（质量均衡，支持改图）
   - 批量出图 / 需要 guidance 控制：`Kwai-Kolors/Kolors`（`--batch-size` 最多 4 张）
   - 改图（基于参考图）：`Qwen/Qwen-Image-Edit-2509`（传入 `--image` 参数）

3. **提示词规范（中英文均可，推荐英文更稳定）**：
   ```
   [主体描述] + [风格关键词] + [色调] + [构图] + [细节修饰]
   示例：
   "A modern tech company poster, minimalist flat design,
   deep blue and white color palette, centered composition,
   clean typography placeholder, professional, high resolution"
   ```

4. **输出目录**：统一存到 `design_assets/YYYY-MM-DD-<任务关键词>/`

5. **超时处理**：exec timeout 设置 `120` 秒；超时后告知用户，建议稍后重试或切换模型

### smart-search / browser 搜索规范

- 搜索灵感时，优先访问：Dribbble、Behance、Pinterest、Unsplash、Pexels
- 只使用明确标注 **CC0 / 免版权** 的图片，记录来源 URL
- 截图参考图保存到 `design_assets/references/`

### 网页设计输出规范

- 使用语义化 HTML5 + 原生 CSS（不依赖任何外部框架，可选引用 CDN Tailwind）
- 文件保存为 `design_assets/web/YYYY-MM-DD-<页面名称>/index.html`
- 必须包含：响应式断点（768px / 1024px）、hover 状态、合理的 CSS custom properties（颜色/字号变量）
- 输出后告知用户：在浏览器用 `open index.html` 即可本地预览
