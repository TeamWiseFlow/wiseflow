---
name: smart-search
description: Construct optimized search URLs for major platforms and navigate to results with the browser. Replaces the built-in web_search tool for targeted, platform-specific searches.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "always": false,
      },
  }
---

# Smart Search Guide

Use this skill whenever the user asks you to search for information on the web or a specific platform. **Construct the search URL directly and navigate to it** instead of using the built-in `web_search` tool.

## Keyword Encoding

- **Spaces**: use `+` for Bing, GitHub, Bilibili; use `%20` for Douyin, Twitter, Facebook, Zhihu; either works for Baidu, Quark, YouTube
- **Special characters**: URL-encode them (e.g., `#` → `%23`, `&` → `%26`, `?` → `%3F`)
- **Chinese characters**: URL-encode (browsers handle this automatically when you navigate)

---

## General Web Search

### Bing (recommended for English and international content)

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

### Baidu (recommended for Chinese content)

General web search:
```
https://www.baidu.com/s?wd={keyword}
```

Baidu Images:
```
https://image.baidu.com/search/index?wd={keyword}
```

Baidu IT / Developer (开发者搜索):
```
https://kaifa.baidu.com/search?wd={keyword}
```

### Quark / 夸克 (recommended for Chinese news and mobile content)

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
- Today: `&sp=EgIIAg%3D%3D`
- This week: `&sp=EgIIAw%3D%3D`
- This month: `&sp=EgIIBA%3D%3D`
- This year: `&sp=EgIIBQ%3D%3D`

Sort options:
- By upload date: `&sp=CAISAhAB`
- By view count: `&sp=CAMSAhAB`
- By rating: `&sp=CAESAhAB`

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
https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_explore_feed
```

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

## International Social Media

### Twitter / X

- Top results: `https://x.com/search?q={keyword}`
- Latest: `https://x.com/search?q={keyword}&f=live`
- People: `https://x.com/search?q={keyword}&f=user`
- Media: `https://x.com/search?q={keyword}&f=media`
- Lists: `https://x.com/search?q={keyword}&f=list`

Add "Near You" filter: append `&lf=on`

Multi-keyword: join with `%20`

### Facebook

- All: `https://www.facebook.com/search/top/?q={keyword}`
- People: `https://www.facebook.com/search/people/?q={keyword}`
- Pages: `https://www.facebook.com/search/pages?q={keyword}`
- Groups: `https://www.facebook.com/search/groups?q={keyword}`
- Events: `https://www.facebook.com/search/events?q={keyword}`

For filter and sort options: interact with the page UI after navigating.

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

---

## After Navigating

1. Take a snapshot to confirm results have loaded.
2. If a CAPTCHA, login wall, or verification challenge appears, follow the **browser-guide** skill.
3. Extract the relevant information from the visible results.
4. If more results are needed, paginate by:
   - Modifying the URL's pagination parameter, or
   - Clicking the "Next page" button on the page.
5. Close the tab immediately after extracting all needed information.
