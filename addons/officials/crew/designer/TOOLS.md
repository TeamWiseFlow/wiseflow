# 设计师 — Tools

## design-system-picker 使用规范

调用 `design-system-picker` 技能从内置设计系统库中选取匹配的设计系统：

```
./skills/design-system-picker/scripts/pick.sh "<风格描述>"
```

返回匹配的设计系统列表，包含风格名称、色彩主调、适用场景。选取后将其 DESIGN.md 内容作为本任务的设计规范基础。

## siliconflow-img-gen 使用规范

仅在需要为网页/界面生成配图素材时使用（非核心工作，备选方案）。

**尺寸映射**（网页/界面场景优先）：

| 场景 | 尺寸 | 参数 |
|------|------|------|
| 网页 Banner / Hero 背景 | 1280×720 | `--image-size 1280x720` |
| 正方形图标 / 头像 | 1024×1024 | `--image-size 1024x1024` |
| 竖版手机端配图 | 720×1280 | `--image-size 720x1280` |

**模型选择**：
- 默认：`Qwen/Qwen-Image`（质量均衡）

**输出目录**：统一存到 `design_assets/YYYY-MM-DD-<任务关键词>/source/`

**超时处理**：exec timeout 设置 `120` 秒

## 素材获取优先级

1. `pexels-footage` / `pixabay-footage` 搜索免版权素材
2. `siliconflow-img-gen` 生成配图
3. 所有素材保存到任务 `source/` 目录，记录来源
