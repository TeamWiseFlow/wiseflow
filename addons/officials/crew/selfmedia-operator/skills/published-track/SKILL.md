---
name: published-track
description: 发布记录追踪。使用 SQLite 数据库记录所有平台发布内容及其互动数据，按平台分表管理。发布后必须调用本技能记录，心跳巡检时更新数据。
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins:
      - bash
      - sqlite3
---

# published-track — 发布记录追踪

统一管理所有平台（微信公众号、知乎、B站、抖音、快手、小红书、今日头条、掘金、Twitter/X、Facebook、Instagram、TikTok、YouTube、Pinterest、Threads、企业微信朋友圈）的发布记录与互动数据。

---

## 数据库位置

`./db/published_track.db`（相对于工作区根目录）

初始化（幂等，可重复执行）：

```bash
./skills/published-track/scripts/init-db.sh
```

---

## 平台与表对应关系

| 平台 | 表名 | 内容类型 | 特有指标 |
|------|------|---------|---------|
| 微信公众号 | `pub_wx_mp` | article/video/post | reads, shares, favorites, likes, comments |
| 知乎 | `pub_zhihu` | article/post | views, upvotes, comments, favorites |
| B站 | `pub_bilibili` | video | plays, danmaku, likes, coins, favorites, shares, comments |
| 抖音 | `pub_douyin` | video | plays, likes, comments, shares, favorites |
| 快手 | `pub_kuaishou` | video | plays, likes, comments, shares |
| 小红书 | `pub_xhs` | article/video/post | views, likes, favorites, comments, shares |
| 今日头条 | `pub_toutiao` | article | impressions, reads, comments, likes |
| 掘金 | `pub_juejin` | article | views, likes, comments, favorites |
| Twitter/X | `pub_twitter` | post/video | views, likes, retweets, replies, bookmarks |
| Facebook | `pub_facebook` | post/video | reach, likes, comments, shares |
| Instagram | `pub_instagram` | post/video | reach, likes, comments, shares, saves |
| TikTok | `pub_tiktok` | video | plays, likes, comments, shares, favorites |
| YouTube | `pub_youtube` | video | views, likes, comments, shares |
| Pinterest | `pub_pinterest` | post | impressions, saves, comments |
| Threads | `pub_threads` | post | views, likes, reposts, replies |
| 企业微信朋友圈 | `pub_wxwork_moments` | post | likes, comments |

---

## 表结构

每张表共享以下通用字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| title | TEXT NOT NULL | 标题 |
| content_type | TEXT NOT NULL | article / video / post |
| source_folder | TEXT NOT NULL | 原始文件夹（如 output_articles/xxx 或 output_videos/xxx） |
| publish_url | TEXT | 发布后 URL |
| publish_date | TEXT NOT NULL | 发布日期（YYYY-MM-DD） |
| notes | TEXT | 备注 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

去重键：`source_folder`（同一篇内容在同一平台只记录一次）

各平台特有的互动指标字段默认值为 0，另有 `top_comment`（主要留言摘要，TEXT）字段。

---

## 使用方式

### 1. 发布后立即记录（强制）

每完成一个平台的发布，**必须**立即调用 `record.sh` 记录：

```bash
./skills/published-track/scripts/record.sh \
  --platform <platform_id> \
  --title "标题" \
  --content-type <article|video|post> \
  --source-folder "output_articles/xxx" \
  --publish-url "https://..." \
  --publish-date "$(date +%Y-%m-%d)" \
  [--notes "备注"]
```

`--platform` 值对应上表「表名」去掉 `pub_` 前缀，如 `wx_mp`、`zhihu`、`bilibili` 等。

若发布失败（如平台拒绝、超时），仍需记录，`publish_url` 留空，`notes` 中注明失败原因。

### 2. 数据更新（心跳巡检）

使用 `update-metrics.sh` 更新互动数据：

```bash
./skills/published-track/scripts/update-metrics.sh \
  --platform <platform_id> \
  --source-folder "output_articles/xxx" \
  --reads 1234 \
  --likes 56 \
  ...
```

只需传入要更新的指标字段，未传入的字段保持不变。

### 3. 查询

```bash
# 查询某平台全部记录
./skills/published-track/scripts/query.sh --platform zhihu

# 查询某平台最近 N 条
./skills/published-track/scripts/query.sh --platform zhihu --limit 10

# 查询特定内容是否已发布到某平台
./skills/published-track/scripts/check-published.sh \
  --platform zhihu \
  --source-folder "output_articles/xxx"

# 查询所有平台中未发布的原始文件夹
./skills/published-track/scripts/query.sh --unpublished
```

### 4. 清理低数据记录

发布超过 7 天、互动指标低于 300 的记录，使用 `query.sh` 查出后可删除：

```bash
./skills/published-track/scripts/query.sh --platform zhihu --stale-days 7 --below 300
```

---

## 与发布技能的配合

所有发布技能（wx-mp-publisher、sync-from-mp、bilibili-publish 等）在发布成功后必须调用 `record.sh` 记录。各技能 SKILL.md 中已标注此要求，主 agent 无需额外提醒。
