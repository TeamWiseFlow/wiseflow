---
name: rss-reader
description: Discover, fetch, and parse RSS/Atom feeds to efficiently retrieve multiple articles from a single source without visiting each article page individually.
metadata:
  {
    "openclaw":
      {
        "emoji": "📡",
        "always": false,
      },
  }
---

# RSS / Atom Feed Reader

Use this skill when:
- The user provides an RSS or Atom feed URL directly
- The user wants to monitor or retrieve updates from a website
- You need to efficiently collect multiple articles from one source
- A website's content can be accessed more reliably through its feed than by scraping individual pages

---

## 1. Discovering the Feed URL

When given a website URL (not an RSS URL), find the feed URL first:

**Method A — check page source**
Navigate to the website, take a snapshot, then look for `<link>` tags in the page `<head>`:
```html
<link rel="alternate" type="application/rss+xml" href="/feed" title="RSS Feed">
<link rel="alternate" type="application/atom+xml" href="/atom.xml" title="Atom Feed">
```

**Method B — try common patterns**
Append these paths to the website's base URL one at a time until one returns XML:
- `/feed`
- `/feed.xml`
- `/rss`
- `/rss.xml`
- `/atom.xml`
- `/index.xml`
- `/?feed=rss2` (WordPress)
- `/feed/rss2` (WordPress alternate)
- `/feeds/posts/default` (Blogger)

**Method C — look for feed links on the page**
Search for RSS icons (🟠), or links labelled "RSS", "Subscribe", "Feed", "Atom".

---

## 2. Recognising a Valid Feed URL

A valid feed URL, when opened in the browser, returns XML containing one of:
- `<rss version="2.0">` — RSS 2.0
- `<feed xmlns="http://www.w3.org/2005/Atom">` — Atom
- `<rdf:RDF>` — RSS 1.0 / RDF

If the browser shows a rendered "Feed Preview" page instead of raw XML, that is fine — the content is the same.

---

## 3. Fetching the Feed

Navigate to the feed URL:
```
browser.navigate(url="{rss_feed_url}")
```

Take a snapshot to inspect the content. The feed XML will contain a list of items/entries.

---

## 4. Parsing RSS 2.0

Each article appears as an `<item>` element:

```xml
<item>
  <title>Article Title</title>
  <link>https://example.com/article-slug</link>
  <description>Short summary or full HTML content</description>
  <content:encoded><![CDATA[Full HTML content (higher priority than description)]]></content:encoded>
  <author>author@example.com (Author Name)</author>
  <dc:creator>Author Name</dc:creator>
  <pubDate>Mon, 01 Jan 2024 12:00:00 +0000</pubDate>
  <guid>https://example.com/article-slug</guid>
</item>
```

**Content priority (highest → lowest):**
1. `<content:encoded>` — full HTML, use if present
2. `<description>` — may be a summary or full content depending on the publisher

---

## 5. Parsing Atom

Each article appears as an `<entry>` element:

```xml
<entry>
  <title>Article Title</title>
  <link href="https://example.com/article-slug" rel="alternate"/>
  <content type="html"><![CDATA[Full HTML content]]></content>
  <summary>Short summary (lower priority than content)</summary>
  <author><name>Author Name</name><email>author@example.com</email></author>
  <published>2024-01-01T12:00:00Z</published>
  <updated>2024-01-02T08:00:00Z</updated>
  <id>https://example.com/article-slug</id>
</entry>
```

**Content priority (highest → lowest):**
1. `<content>` — full content, use if present
2. `<summary>` — usually a short excerpt

---

## 6. Information to Extract

For each entry, record:

| Field | Source (RSS) | Source (Atom) |
|-------|-------------|---------------|
| Title | `<title>` | `<title>` |
| Article URL | `<link>` | `<link href="...">` |
| Content / HTML | `<content:encoded>` or `<description>` | `<content>` or `<summary>` |
| Author | `<author>` or `<dc:creator>` | `<author><name>` |
| Publish date | `<pubDate>` | `<published>` (or `<updated>`) |

Also capture the feed-level metadata:
- Feed title: `<channel><title>` (RSS) / `<feed><title>` (Atom)
- Feed description: `<channel><description>` / `<feed><subtitle>`
- Website URL: `<channel><link>` / `<feed><link rel="alternate">`
- Last updated: `<lastBuildDate>` (RSS) / `<feed><updated>` (Atom)

---

## 7. Deciding Whether to Visit the Article URL

- **Full content in feed** (`<content:encoded>` or `<content>` has substantial HTML, > 200 characters): process it directly — **no need to visit the article URL**.
- **Summary only** (content is short, truncated, or `<description>` ends with "…"): navigate to the article URL to retrieve the full content.
- **No content field at all**: navigate to the article URL.

---

## 8. Deduplication

Skip any entry whose article URL is already in the set of previously processed URLs. Do not re-process duplicates.

---

## 9. Feed Pagination

Some feeds support multiple pages of older entries:

- Check for `<link rel="next">` in Atom feeds:
  ```xml
  <link rel="next" href="https://example.com/feed?page=2"/>
  ```
- For feeds with a `?page=N` pattern, increment `N` to get older entries.
- Stop paginating when the feed returns no new items or the page returns an error.

---

## 10. Edge Cases

| Situation | Action |
|-----------|--------|
| Feed URL returns 404 | Try the alternative patterns from Section 1 |
| Feed requires login | Follow the **browser-guide** skill for login handling |
| Feed returns garbled characters | The encoding may be non-UTF-8; try appending `?charset=utf-8` or report to the user |
| Empty feed (`<channel>` has no `<item>`) | Report: "该 RSS 信源目前没有条目" |
| XML parse error / malformed feed | Report: "无法解析该 RSS 信源，格式可能有误：{url}" |
| Feed redirects to a login page | Follow the **browser-guide** skill |
