---
name: smart-search
description: Construct optimized search URLs for major platforms and navigate to results with the browser. Replaces the built-in web_search tool for targeted, platform-specific searches.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "always": true,
      }
  }
---

# Smart Search Guide

Use this skill whenever the user asks you to search for information on the web or a specific platform. **Construct the search URL directly and navigate to it** instead of using the built-in `web_search` tool.

## Keyword Encoding

- **Spaces**: use `+` for Bing, GitHub, Bilibili; use `%20` for Douyin, Twitter, Facebook, Zhihu; either works for Baidu, Quark, YouTube
- **Special characters**: URL-encode them (e.g., `#` → `%23`, `&` → `%26`, `?` → `%3F`)
- **Chinese characters**: URL-encode (browsers handle this automatically when you navigate)

---

## Cookie Warmup — CRITICAL for Authenticated Platforms

Many platforms will return empty results or redirect to login if you navigate **directly** to a search URL without first visiting the home page. Always warm up the session in two steps:

| Platform | Step 1 (warmup) | Step 2 (search) |
|----------|-----------------|-----------------|
| 知乎 | Navigate `https://www.zhihu.com` | Navigate to search URL |
| Reddit | Navigate `https://www.reddit.com` | Navigate to search URL |
| 微博 | Navigate `https://weibo.com` | Navigate to search URL |
| YouTube | Navigate `https://www.youtube.com` | Navigate to search URL |
| 雪球 | Navigate `https://xueqiu.com` | Navigate to search URL |
| 路透社 | Navigate `https://www.reuters.com` | Navigate to search URL |
| Bilibili | Navigate `https://www.bilibili.com` | Navigate to search URL |
| 小红书 | Navigate `https://www.xiaohongshu.com` | Navigate to search URL |
| TikTok | Navigate `https://www.tiktok.com` | Navigate to search URL |

**Platforms that do NOT need warmup** (public APIs / no auth required):
- Google, Bing, Baidu, Quark, GitHub, arXiv, Wikipedia, BBC, HackerNews, V2EX, Tieba, Amazon

---

## General Web Search

### Bing (recommended)

```
https://www.bing.com/search?q={keyword}
```

Time filters (append to URL):
- Last 24 hours: `&filters=ex1:"ez1"`
- Last week: `&filters=ex1:"ez2"`
- Last month: `&filters=ex1:"ez3"`

Pagination: `&first={offset}` where offset = (page − 1) × 10 + 1

### Bing News

```
https://www.bing.com/news/search?q={keyword}
```

### Bing Images

```
https://www.bing.com/images/search?q={keyword}
```

Time filters for images: `&qft=filterui:age-lt{minutes}` where minutes = 1440 (day) / 10080 (week) / 44640 (month) / 525600 (year)

### Baidu (backup)

General web search:
```
https://www.baidu.com/s?wd={keyword}
```

Baidu Images:
```
https://image.baidu.com/search/index?tn=baiduimage&fm=result&ie=utf-8&word={keyword}
```

### Quark / 夸克 (fallback)

```
https://quark.sm.cn/s?q={keyword}
```

---

## Academic & Reference

### arXiv (preprints: CS, Physics, Math, Biology, Economics, etc.)

Browser search:
```
https://arxiv.org/search/?searchtype=all&query={keyword}
```

Search by specific field:
- Title: `?searchtype=ti&query={keyword}`
- Author: `?searchtype=au&query={keyword}`
- Abstract: `?searchtype=abs&query={keyword}`
- Category (e.g., cs.AI): `?searchtype=all&query={keyword}&searchtype=all&start=0`

Sort by most recent: append `&order=-announced_date_first`

arXiv API (returns structured XML — useful for programmatic access):
```
https://export.arxiv.org/api/query?search_query=all:{keyword}&max_results=10
```

### Wikipedia

English:
```
https://en.wikipedia.org/w/index.php?search={keyword}
```

Chinese (中文):
```
https://zh.wikipedia.org/w/index.php?search={keyword}
```

Other languages: replace the language code prefix (e.g., `de`, `fr`, `ja`, `ko`, `es`).

---

## Video Platforms

### YouTube

```
https://www.youtube.com/results?search_query={keyword}
```

Time filters (append to URL):
- Last hour: `&sp=EgIIAQ%3D%3D`
- Today: `&sp=EgIIAg%3D%3D`
- This week: `&sp=EgIIAw%3D%3D`
- This month: `&sp=EgIIBA%3D%3D`
- This year: `&sp=EgIIBQ%3D%3D`

Type filters (append to URL, cannot combine with time/sort):
- Videos only: `&sp=EgIQAQ%3D%3D`
- Shorts only: `&sp=EgIQCQ%3D%3D`
- Channels only: `&sp=EgIQAg%3D%3D`
- Playlists only: `&sp=EgIQAw%3D%3D`

Sort options (append to URL, cannot combine with type filters):
- By upload date: `&sp=CAI%3D`
- By view count: `&sp=CAM%3D`
- By rating: `&sp=CAE%3D`

> **Note**: `sp=` only accepts one value — type, time, and sort filters are mutually exclusive. Use whichever is most relevant.

Multi-keyword: join with `+` (e.g., `wiseflow+AI+搜索`)

---

## Chinese Social Media

### 哔哩哔哩 (Bilibili / B站)

```
https://search.bilibili.com/{channel}?keyword={keyword}
```

Channels: `all` (综合) | `video` (视频) | `bangumi` (番剧) | `pgc` (影视) | `live` (直播) | `article` (专栏) | `upuser` (UP主)

Sort options for `all` and `video`:
- Most views: `&order=click`
- Newest: `&order=pubdate`
- Most danmaku: `&order=dm`
- Most favorites: `&order=stow`

Sort options for `live`:
- Search anchors only: `&search_type=live_user`
- Search live rooms only: `&search_type=live_room`
- Live rooms by start time: `&search_type=live_room&order=live_time`

Sort options for `upuser`:
- Most fans (desc): `&order=fans`
- Fewest fans (asc): `&order=fans&order_sort=1`
- Highest level: `&order=level`

Sort options for `article`:
- Newest: `&order=pubdate`
- Most clicks: `&order=click`
- Most popular: `&order=attention`
- Most comments: `&order=scores`

Multi-keyword: join with `+`

### 抖音 (Douyin / TikTok China)

```
https://www.douyin.com/search/{keyword}?type={type}
```

Types: `general` (综合，default) | `video` (视频) | `user` (用户) | `live` (直播)

Multi-keyword: join with `%20` (e.g., `wiseflow%20AI`)

For sort and filter options: interact with the page UI after navigating.

### 微博 (Weibo)

- Comprehensive: `https://s.weibo.com/weibo/{keyword}`
- Real-time / Latest: `https://s.weibo.com/realtime?q={keyword}`
- Users: `https://s.weibo.com/user?q={keyword}`
- Topics: `https://s.weibo.com/topic?q={keyword}`

### 小红书 (Xiaohongshu / RED / 红薯)

```
https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes
```

> **Note**: Use `source=web_search_result_notes` (not `web_explore_feed`) to get search results instead of explore feed.
> After navigating, wait ~3 seconds and scroll down twice — results use lazy loading.

For channel selection, filter, and sort: interact with the page UI after navigating.

### 知乎 (Zhihu)

```
https://www.zhihu.com/search?type=content&q={keyword}
```

Content types: `content` (综合) | `people` (用户) | `scholar` (论文) | `column` (专栏) | `publication` (电子书) | `ring` (圈子) | `topic` (话题) | `zvideo` (视频)

Filters for comprehensive search (`type=content`):
- Answers only: `&vertical=answer`
- Articles only: `&vertical=article`
- Videos only: `&vertical=zvideo`

Sort:
- Most upvotes: `&sort=upvoted_count`
- Newest: `&sort=created_time`

Time range:
- Last day: `&time_interval=a_day`
- Last week: `&time_interval=a_week`
- Last month: `&time_interval=a_month`
- Last 3 months: `&time_interval=three_months`
- Last 6 months: `&time_interval=half_a_year`
- Last year: `&time_interval=a_year`

Example — newest articles from the last month:
```
https://www.zhihu.com/search?type=content&q={keyword}&vertical=article&sort=created_time&time_interval=a_month
```

Multi-keyword: join with `%20`

---

### 百度贴吧 (Tieba)

```
https://tieba.baidu.com/f/search/res?qw={keyword}&ie=utf-8
```

Search within a specific forum (吧):
```
https://tieba.baidu.com/f/search/res?qw={keyword}&kw={forum_name}&ie=utf-8
```

> **Note**: Public content, no warmup needed. Only the first page of results is reliably available. Multi-keyword: URL-encode spaces as `%20`.

---

## International Social Media

### Twitter / X

- Top results: `https://x.com/search?q={keyword}`
- Latest: `https://x.com/search?q={keyword}&f=live`
- People: `https://x.com/search?q={keyword}&f=user`
- Media: `https://x.com/search?q={keyword}&f=media`
- Lists: `https://x.com/search?q={keyword}&f=list`

Add "Near You" filter: append `&lf=on`

> **Note**: Twitter/X uses heavy client-side rendering. After navigating, wait at least **5 seconds** before taking a snapshot to ensure tweet content has loaded.

Multi-keyword: join with `%20`

### Facebook

- All: `https://www.facebook.com/search/top/?q={keyword}`
- People: `https://www.facebook.com/search/people/?q={keyword}`
- Pages: `https://www.facebook.com/search/pages?q={keyword}`
- Groups: `https://www.facebook.com/search/groups?q={keyword}`
- Events: `https://www.facebook.com/search/events?q={keyword}`

For filter and sort options: interact with the page UI after navigating.

Multi-keyword: join with `%20`

### Reddit

```
https://www.reddit.com/search/?q={keyword}
```

Sort options: `&sort=relevance` | `hot` | `top` | `new` | `comments`

Time filter (for `sort=top`): `&t=hour` | `day` | `week` | `month` | `year` | `all`

Search within a specific subreddit:
```
https://www.reddit.com/r/{subreddit}/search/?q={keyword}&restrict_sr=on&sort=relevance&t=all
```

Multi-keyword: join with `+`

### TikTok (international)

```
https://www.tiktok.com/search?q={keyword}
```

> **Note**: Cookie warmup required — navigate `https://www.tiktok.com` first. Wait ~3 seconds after navigating to search results for content to load.

Multi-keyword: join with `%20`

---

## Developer Platforms

### GitHub

```
https://github.com/search?q={keyword}&type={type}
```

Types: `repositories` | `users` | `code` | `issues` | `pullrequests` | `discussions` | `topics` | `wikis`

Sort options for **repositories**:
- Most stars: `&s=stars&o=desc`
- Fewest stars: `&s=stars&o=asc`
- Most forks: `&s=forks&o=desc`
- Recently updated: `&s=updated&o=desc`

Sort options for **users**:
- Most followers: `&s=followers&o=desc`
- Most repositories: `&s=repositories&o=desc`
- Recently joined: `&s=joined&o=desc`

Language filter (for `repositories` and `users`): `&l={language}` (e.g., `&l=Python`, `&l=TypeScript`, `&l=Go`)

Multi-keyword: join with `+`

Example:
```
https://github.com/search?q=wiseflow+addon&type=repositories&s=stars&o=desc&l=Python
```

### LinkedIn

Job search (cookie warmup required — navigate `https://www.linkedin.com` first):
```
https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}
```

People search:
```
https://www.linkedin.com/search/results/people/?keywords={keyword}
```

Company search:
```
https://www.linkedin.com/search/results/companies/?keywords={keyword}
```

Multi-keyword: join with `%20`

---

## After Navigating

1. Take a snapshot to confirm results have loaded.
2. If a CAPTCHA, login wall, or verification challenge appears, follow the **browser-guide** skill.
3. Extract the relevant information from the visible results.
4. If more results are needed, paginate by:
   - Modifying the URL's pagination parameter, or
   - Clicking the "Next page" button on the page.
5. Close the tab immediately after extracting all needed information.

---

## Financial Platforms

### 雪球 (Xueqiu) — Stocks & Finance

Stock/symbol search (cookie warmup required — navigate `https://xueqiu.com` first):
```
https://xueqiu.com/search?q={keyword}
```

Example queries: `茅台`, `AAPL`, `腾讯`, `SH600519`

For stock detail page: `https://xueqiu.com/S/{symbol}` (e.g., `/S/SH600519`)

---

## Tech Communities

### Hacker News (public, no login required)

```
https://news.ycombinator.com/
```

Search via Algolia (unofficial but reliable):
```
https://hn.algolia.com/?q={keyword}
```

Sort by date: `&dateRange=pastWeek` | `pastMonth` | `pastYear`

### V2EX (public, no login required)

Search (Google site search approach, most reliable):
```
https://www.google.com/search?q=site:v2ex.com+{keyword}
```

Or navigate directly to V2EX and use the built-in search:
```
https://www.v2ex.com/?q={keyword}
```

---

## News

### Reuters

News search (cookie warmup required — navigate `https://www.reuters.com` first):
```
https://www.reuters.com/search/news?blob={keyword}
```

Multi-keyword: join with `+`

---

## Shopping

### Amazon

```
https://www.amazon.com/s?k={keyword}
```

Department filter (append to URL): `&i={department}` — common values: `electronics`, `books`, `clothing-shoes-jewelry`, `grocery`, `toys-and-games`

Sort options (append to URL):
- Relevance (default): `&s=relevance-rank`
- Price low to high: `&s=price-asc-rank`
- Price high to low: `&s=price-desc-rank`
- Avg customer review: `&s=review-rank`
- Newest arrivals: `&s=date-desc-rank`

> **Anti-bot protection**: Navigate and wait at least 2–3 seconds before taking a snapshot. If you encounter a robot verification page, do not retry immediately — follow the **browser-guide** skill.

Multi-keyword: join with `+`
