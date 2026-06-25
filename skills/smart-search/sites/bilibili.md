# 哔哩哔哩 (Bilibili / B站)

> last_verified: 2026-06-15

## 概览

- 域名：`search.bilibili.com`（搜索）、`www.bilibili.com`（主站）
- 登录要求：搜索可免登录，但部分内容需登录
- Auth 策略：Cookie Warmup（推荐先访问首页）

## 搜索

### URL

```
https://search.bilibili.com/{channel}?keyword={keyword}
```

频道（`{channel}`）：
- `all`（综合）
- `video`（视频）
- `bangumi`（番剧）
- `pgc`（影视）
- `live`（直播）
- `article`（专栏）
- `upuser`（UP主）

### 排序

综合/视频：
- 最多播放：`&order=click`
- 最新：`&order=pubdate`
- 最多弹幕：`&order=dm`
- 最多收藏：`&order=stow`

直播：
- 搜索主播：`&search_type=live_user`
- 搜索直播间：`&search_type=live_room`

UP主：
- 粉丝最多：`&order=fans`
- 等级最高：`&order=level`

专栏：
- 最新：`&order=pubdate`
- 最多点击：`&order=click`
- 最多评论：`&order=scores`

### 分页

URL 分页：`&page={n}`（从 1 开始）

### Cookie Warmup

1. Navigate `https://www.bilibili.com`
2. 等待 3 秒
3. Navigate 到搜索 URL

### 多关键词

用 `+` 连接

## Pitfalls

### pitfall: bangumi_bvid_subtitle

- **触发**：对番剧/纪录片/电影/综艺的 bvid 获取字幕
- **症状**：普通视频字幕接口对 PGC 内容返回不同结构
- **workaround**：PGC 内容的字幕需走 `https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}` 接口，`cid` 从 `https://api.bilibili.com/x/web-interface/view?bvid={bvid}` 获取

## Fallback

1. 搜索无结果 → 换关键词或换频道
2. 仍不足 → Bing 搜 `site:bilibili.com {keyword}`

## Re-entry

- 在搜索结果页 → 从当前 page 继续翻页
- 在视频详情页 → 继续提取内容
