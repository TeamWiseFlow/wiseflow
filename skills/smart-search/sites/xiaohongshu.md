# 小红书 (Xiaohongshu / XHS / 红薯)

> last_verified: 2026-06-15 | 来源：OpenCLI sitemaps/xiaohongshu/ + search.js

## 概览

- 域名：`www.xiaohongshu.com`，海外品牌 `rednote.com`
- 登录要求：**几乎所有操作需登录**（`web_session` cookie）
- Auth 策略：Cookie Warmup（必须先访问首页）

## 搜索

### URL

```
https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes
```

- `source=web_search_result_notes`（不是 `web_explore_feed`）
- 关键词用 URL-encode，空格用 `%20`

### Cookie Warmup

1. Navigate `https://www.xiaohongshu.com`
2. 等待 3 秒
3. Navigate 到搜索 URL

### 分页

小红书搜索使用**无限滚动**加载，无 URL 分页参数：
- 每次向下滚动加载更多结果
- 每屏约 20 条，建议最多滚动 3-5 次
- 滚动后等待 2-3 秒让新内容渲染

### DOM 提取提示

搜索结果卡片的选择器（**会漂移，需要 fallback 链**）：

```
主选择器：  section.note-item
Fallback：  section:has(a[href*="/search_result/"]) 或 section:has(a[href*="/explore/"])
```

卡片内字段：
- 标题：`.title` 或 `.note-title` 或 `a.title` 或 `a[href*="/search_result/"] span`
- 作者：`a.author .name` 或 `.author-name` 或 `.nick-name`
- 点赞数：`.count` 或 `.like-count` 或 `.like-wrapper .count`
- 笔记链接：`a.cover.mask` 或 `a[href*="/search_result/"]` 或 `a[href*="/explore/"]`

**点赞数压缩格式**：`2.1w` = 2.1万，`1.5万` = 15000，`1.2k` = 1200。解析时需处理这些中文缩写。

### 笔记详情 URL

笔记详情 URL 格式：`https://www.xiaohongshu.com/explore/{note_id}?xsec_token={token}&xsec_source=pc_search`

**⚠️ xsec_token 必须从搜索结果/笔记列表的链接中提取，不能手拼！** 裸访问 `/explore/{note_id}` 会 403。

### 笔记发布时间估算

小红书 note ID 遵循 MongoDB ObjectID 格式，前 8 位 hex 编码 Unix 时间戳：
- 例：`697f6c74...` → `0x697f6c74` = 1769958516 → 2026-02-01
- 偏移 UTC+8（中国标准时间）

## Pitfalls

### pitfall: search_api_returns_empty

- **触发**：走 `/api/sns/web/v1/search/notes` XHR
- **症状**：关键词在网页搜得到结果但 API 返空
- **workaround**：直接导航到搜索结果页做 DOM 提取，不走 API

### pitfall: login_wall_on_search

- **触发**：未登录访问搜索页
- **症状**：页面显示"登录后查看搜索结果"或 redirect 到 `/login`
- **workaround**：先 Cookie Warmup，若仍遇登录墙 → browser-guide QR 登录

### pitfall: dom_class_drift

- **触发**：搜索结果 `section.note-item` class 被替换或移除
- **症状**：DOM 提取返回 0 条结果，但页面可见内容
- **workaround**：fallback 到 `section:has(a[href*="/search_result/"])` 或 `section:has(a[href*="/explore/"])`

### pitfall: security_block_on_repeated_access

- **触发**：短时间高频访问同一笔记 URL / 高频搜索
- **症状**：页面显示"安全限制"/"访问链接异常"，URL 含 `website-login/error`
- **workaround**：触发后 60s 内不重试同 URL；连续请求间用 1-2s wait 隔开

### pitfall: note_url_requires_xsec_token

- **触发**：手拼 `/explore/{note_id}` 裸路径，没带 `xsec_token`
- **症状**：页面 403 或 redirect 到错误页
- **workaround**：笔记 URL 必须从搜索结果/笔记列表的链接中提取（已含 signed token）

## Fallback

当搜索结果页 DOM 提取失败时：

1. 检查是否登录墙 → browser-guide 登录后重试
2. 等待更长时间（5-10s）后重新 snapshot
3. 尝试 fallback 选择器（`section:has(a[href*="/explore/"])`）
4. 若仍失败，换 Bing 搜 `site:xiaohongshu.com {keyword}`

## Re-entry

中断后醒来根据 URL 判断：

- 在 `/search_result/?keyword=<X>` 且结果已渲染 → 从 DOM 提取步骤继续
- 在 `/login` 或命中登录墙 → browser-guide 登录后重新搜索
- 在 `/` 或其他页面 → 重新执行搜索流程
