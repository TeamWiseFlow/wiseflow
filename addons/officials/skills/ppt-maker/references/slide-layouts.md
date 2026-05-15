# Slide Layouts Reference

ppt-maker 支持的幻灯片布局类型与 JSON 配置示例。

## 全局配置结构

```json
{
  "theme": {
    "primary_color": "1A1A2E",
    "secondary_color": "16213E",
    "accent_color": "E94560",
    "background_color": "FFFFFF",
    "text_color": "333333",
    "heading_font": "Microsoft YaHei",
    "body_font": "Microsoft YaHei"
  },
  "slides": [...]
}
```

## 幻灯片类型

### 1. cover — 封面

```json
{
  "type": "cover",
  "title": "季度业务汇报",
  "subtitle": "Q1 2026 工作总结与展望",
  "author": "业务拓展部",
  "background_color": "1A1A2E",
  "background_image": "/path/to/ai_cover_bg.png"
}
```

- `background_image`：可选，AI 生成的封面底图（16:9，建议 1664x928）
- `background_color`：用于纯色背景或图片叠加蒙版

### 2. toc — 目录页

```json
{
  "type": "toc",
  "title": "目录",
  "items": ["市场概览", "业绩亮点", "问题与挑战", "下季度规划"]
}
```

### 3. content — 标准内容页

最常用的幻灯片类型，支持文字+可选配图。

```json
{
  "type": "content",
  "title": "市场概览",
  "body": "2026 年 Q1，行业整体规模达到...",
  "bullets": [
    "市场份额增长 15%，超出预期",
    "新增客户 42 家，其中企业级客户占比 60%",
    "客户留存率维持在 92%，高于行业平均"
  ],
  "image": "/path/to/chart.png",
  "image_position": "right"
}
```

- `image_position`：`"right"`（默认）、`"left"`、`"bottom"`
- `body` 与 `bullets` 可同时使用，body 在前，bullets 在后

### 4. two_column — 双栏对比

```json
{
  "type": "two_column",
  "title": "竞品对比分析",
  "left_title": "我们",
  "left_body": ["AI 驱动推荐引擎", "7×24 自动运营", "数据安全保障"],
  "right_title": "竞品",
  "right_body": ["人工规则匹配", "工作时间运营", "基础安全措施"]
}
```

`left_body` / `right_body` 支持字符串数组（每条一个 bullet）或纯文本。

### 5. section — 章节分隔页

```json
{
  "type": "section",
  "number": "01",
  "title": "市场概览",
  "subtitle": "行业趋势、竞争格局与机会分析",
  "background_color": "1A1A2E"
}
```

### 6. image_full — 全图页

```json
{
  "type": "image_full",
  "title": "产品演示",
  "caption": "核心功能界面展示",
  "image": "/path/to/screenshot.png"
}
```

### 7. ending — 结束页

```json
{
  "type": "ending",
  "title": "感谢聆听",
  "subtitle": "期待与您进一步交流",
  "contact": "邮箱：team@company.com | 电话：138-0000-0000",
  "qr_image": "/path/to/qrcode.png",
  "background_color": "1A1A2E"
}
```

## 配图策略

| 页面类型 | 配图建议 | 推荐 API |
|---------|---------|---------|
| 封面 | 抽象科技/行业背景，16:9 横幅 | siliconflow-img-gen（`--image-size 1664x928`） |
| 内容页 | 概念插图、数据图表、场景图 | siliconflow-img-gen + pexels-footage / pixabay-footage |
| 全图页 | 高清产品截图 / 实景照片 | 用户提供 |
| 结束页 | 品牌 Logo / 二维码 | 用户提供 |

## AI 配图注意事项

1. 生成封面/内容页配图前，将主题色名称（如"深蓝色"）融入 prompt
2. siliconflow-img-gen 16:9 尺寸为 `1664x928`
3. 生成后必须验证图片不是纯色白板（siliconflow 偶发异常）
4. 图片文件名与幻灯片索引对应（如 `slide_01_bg.png`）
