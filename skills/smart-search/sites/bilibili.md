# 哔哩哔哩 (Bilibili / B站)

> 搜索类别参考 [OpenCLI](https://github.com/jackwener/OpenCLI/blob/b06ab7780e73d3021e12e0f170086c2d55675776/clis/bilibili/search.js) 与 [SearXNG](https://github.com/searxng/searxng/blob/ad46ebd7d87666edb5f116c5b274b47f689ac6cd/searx/engines/bilibili.py)。固定 session/profile `default`，带 --persistent。

## 概览

- 域名：`search.bilibili.com`（搜索）、`www.bilibili.com`（主站）
- 登录要求：搜索可免登录，但部分内容需登录
- 可先访问首页核对当前页面与登录状态，不能以首页访问成功认定已登录

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

### 页面结果与媒体内容

普通视频、番剧、用户和直播类别以当前搜索页菜单为准；列表中的标题、作者和可见计数先记录实际值，不补零。OpenCLI 当前普通视频搜索使用带签名的 WBI 接口；不要将接口 search_type=bili_user 直接当作浏览器频道名，也不在本技能中构造 WBI 请求。

本技能搜索和阅读页面，不调用字幕/播放接口或拼接 bvid/cid。需要视频或字幕处理时核对现有对应技能能力，不能仅凭浏览器搜索结果承诺下载或转写。

## Fallback

1. 搜索无结果 → 换关键词或换频道
2. 仍不足 → Bing 搜 `site:bilibili.com {keyword}`

## Re-entry

- 在搜索结果页 → 从当前 page 继续翻页
- 在视频详情页 → 继续提取内容
