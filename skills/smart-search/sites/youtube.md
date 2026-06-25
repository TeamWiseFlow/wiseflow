# YouTube

> last_verified: 2026-06-15

## 搜索

### URL

```
https://www.youtube.com/results?search_query={keyword}
```

### 时间过滤（追加 `&sp=`）

- 一小时内：`EgIIAQ%3D%3D`
- 今天：`EgIIAg%3D%3D`
- 本周：`EgIIAw%3D%3D`
- 本月：`EgIIBA%3D%3D`
- 本年：`EgIIBQ%3D%3D`

### 类型过滤（追加 `&sp=`，与时间/排序互斥）

- 仅视频：`EgIQAQ%3D%3D`
- 仅 Shorts：`EgIQCQ%3D%3D`
- 仅频道：`EgIQAg%3D%3D`
- 仅播放列表：`EgIQAw%3D%3D`

### 排序（追加 `&sp=`，与类型互斥）

- 按上传日期：`CAI%3D`
- 按观看次数：`CAM%3D`
- 按评分：`CAE%3D`

### Cookie Warmup

1. Navigate `https://www.youtube.com`
2. 等待 3 秒
3. Navigate 到搜索 URL

### 多关键词

用 `+` 连接

## Pitfalls

### pitfall: heavy_client_rendering

- **触发**：导航到搜索结果页后立即提取
- **症状**：内容未加载
- **workaround**：等待 5 秒以上再 snapshot

### pitfall: video_tab_fallback

- **触发**：搜索结果中某些视频格式
- **症状**：`lockupViewModel` 格式的视频卡片被遗漏
- **workaround**：DOM 提取时同时匹配 `ytd-video-renderer` 和 `lockup-view-model` 两种格式

## Fallback

1. 搜索无结果 → 换关键词
2. 仍不足 → Bing 搜 `site:youtube.com {keyword}`
