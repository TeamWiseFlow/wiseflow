# 设计师 — Tools

## Available Tools

| Tool | Purpose |
|------|---------|
| `siliconflow-img-gen` | AI 文生图 / 改图；海报、Banner、封面图、配图等视觉素材的核心生成工具 |
| `smart-search` | 搜索竞品设计参考、灵感图、免版权素材（Unsplash / Pexels / Dribbble 等） |
| `browser` + `browser-guide` | 访问设计参考网站、抓取页面截图、下载免版权图片 |
| `summarize` | 提炼长文档中的视觉需求要点（如 PRD、品牌手册） |

## siliconflow-img-gen 使用规范

**尺寸映射**（优先使用标准尺寸）：

| 场景 | 尺寸 | 参数 |
|------|------|------|
| 正方形配图 / 头像 | 1024×1024 | `--image-size 1024x1024` |
| 竖版海报 / 小红书封面 | 960×1280 | `--image-size 960x1280` |
| 横版 Banner | 1280×720 | `--image-size 1280x720` |
| 手机壁纸 / 竖版视频封面 | 720×1280 | `--image-size 720x1280` |
| 长图 / 信息图 | 720×1440 | `--image-size 720x1440` |

**模型选择**：
- 默认：`Qwen/Qwen-Image-Edit-2509`（质量均衡，支持改图）
- 批量出图 / 需要 guidance 控制���`Kwai-Kolors/Kolors`（`--batch-size` 最多 4 张）
- 改图（基于参考图）：`Qwen/Qwen-Image-Edit-2509`（传入 `--image` 参数）

**输出目录**：统一存到 `design_assets/YYYY-MM-DD-<任务关键词>/`

**超时处理**：exec timeout 设置 `120` 秒；超时后告知用户，建议稍后重试或切换模型

## 注意事项

- **素材合规**：仅使用明确标注 CC0 / 免版权的图片，记录来源 URL
- **参考图保存**：截图参考图保存到 `design_assets/references/`
