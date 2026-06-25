---
name: published-track
description: 发布记录追踪。使用 SQLite 数据库记录所有平台发布内容及其互动数据，按平台分表管理。三大块：与发布技能结合（发布记录 1B；打分评估 1A 由 content-calibrator 负责）、数据更新、查询与平台设置。
metadata:
  openclaw:
    emoji: "📊"
    requires:
      bins:
      - bash
      - sqlite3
---

# published-track — 发布记录追踪

统一管理所有平台（微信公众号、微信视频号、知乎、B站、抖音、快手、小红书、今日头条、掘金、Twitter/X、Facebook、Instagram、TikTok、YouTube、Pinterest、Threads）的发布记录与互动数据。

> 企业微信朋友圈不纳入追踪记录（无公开 URL、互动数据无法自动获取、运营复盘价值低），发布后不调 `record.sh`。

---

## 数据库位置

`./db/published_track.db`（相对于工作区根目录）。初始化（幂等）：

```bash
./skills/published-track/scripts/init-db.sh
```

---

## 平台与表对应关系

| 平台 | 表名 | 内容类型 | 特有指标 |
|------|------|---------|---------|
| 微信公众号 | `pub_wx_mp` | article | reads, shares, favorites, likes, comments |
| 微信视频号 | `pub_wx_channel` | video | plays, likes, comments, shares, favorites |
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

`--platform` 取「表名」去掉 `pub_` 前缀，如 `wx_mp`、`wx_channel`、`xhs`、`bilibili`。

---

## 表结构

每张表共享通用字段：`id`（自增主键）、`title`、`content_type`（article/video/post）、`source_folder`（原始文件夹，如 `output_articles/xxx`，**不做唯一约束，同内容可同平台多次发布**）、`publish_url`、`publish_date`（YYYY-MM-DD）、`distribute_status`（0=待分发，1=无需分发，2=已分发）、`notes`、`created_at`、`updated_at`。各平台特有互动指标默认 0，另有 `top_comment`（主要留言摘要）。

### content-calibrator 打分字段

| 字段 | 说明 |
|------|------|
| `cal_enabled` | 该记录是否参与 content-calibrator 复盘（0/1） |
| `cal_score_er/hp/sr/ql/na/ab/pv` | 7 维分（0-5）：情感共鸣/钩子强度/社会议题/金句密度/叙事性/受众广度/实用价值 |
| `cal_composite` | 综合分（0-10） |
| `cal_rubric_version` | 打分时 rubric 版本 |
| `cal_scored_at` | 打分时间 |

---

# 三大使用方式

## 块一·与发布技能结合

本块描述发布记录脚本的用法与编排意图。**实际编排由 `AGENTS.md`（"按需写作 / 发布记录管理与复盘"）与执行流类技能（`gaoqian-article`、`video-product`）承担**；各发布技能本身只管发布，不提及打分与记录。流程顺序为 **打分 → 发布 → 记录**。

### 流程 1A·打分评估（发布前自检）

**打分由 `content-calibrator` 技能负责**（blind sub-agent + `score-only.sh` + 阈值门 + 最多 2 轮改稿重打 + 平台未启用跳过；视频内容打分锚在脚本定稿前）。完整流程见 `content-calibrator/SKILL.md` 的"流程 1A·打分评估（发布前自检）"，本技能不重复描述。

### 流程 1B·发布记录（发布后）

发布成功后调用合并入口 `record.sh`：

- **提供 `--cal-*` 分数** → 自动置 `cal_enabled=1` + 算 composite + 记 `cal_rubric_version`（从 `.cheat-state.json` 读）
- **不提供分数** → `cal_enabled=0`（不参与复盘）
- 显式 `--cal-enabled 0/1` → 覆盖自动判定

```bash
# 正常发布后（1A 已打过分的平台，把分一并传入）
./skills/published-track/scripts/record.sh \
  --platform wx_mp \
  --title "标题" \
  --content-type article \
  --source-folder "output_articles/xxx" \
  --publish-url "https://mp.weixin.qq.com/s/xxx" \
  --cal-er 3 --cal-hp 4 --cal-sr 3 --cal-ql 4 --cal-na 3 --cal-ab 4 --cal-pv 2

# 平台未启用 calibration，或补发/补登记历史作品（不打分）
./skills/published-track/scripts/record.sh \
  --platform xhs \
  --title "标题" \
  --content-type post \
  --source-folder "output_articles/xxx" \
  --publish-url "https://www.xiaohongshu.com/xxx"
```

参数说明：
- `--distribute-status`：0=待分发（默认），1=无需分发，2=已分发。
- `--publish-date`：**省略即默认当日**。❌ 勿传 `"$(date +%Y-%m-%d)"`（exec 沙箱不展开 `$()`）；仅补登记非当日作品时传字面量如 `2026-06-14`。
- `--publish-url`：发布失败时留空并在 `--notes` 注明原因。
- `score-and-record.sh` 已合并为 `record.sh` 的薄 wrapper，兼容保留，新调用直接用 `record.sh`。

> **设计依据**：有分数说明 1A 已通过、`calibration/<platform>/` 必存在；无分则 1A 阶段就该报错了。故"有分即追踪、无分即不追踪"。

---

## 块二·数据更新

### 流程 2A·自动更新（定时任务用）

`fetch-and-update-metrics.sh` 封装 login-manager 探活 → API 抓取 → DB 写入，凌晨复盘心跳调用：

```bash
# 通过 source-folder 从 DB 查 publish_url → 抓取 → 写入
./skills/published-track/scripts/fetch-and-update-metrics.sh \
  --platform <platform> --source-folder "output_articles/xxx"

# 按 id 逐条抓（同 folder 多条记录各自独立统计，推荐）
./skills/published-track/scripts/fetch-and-update-metrics.sh \
  --platform xhs --id <rowid> --xsec-token <tok> --xsec-source pc_feed
```

返回 JSON 统一格式：

| 场景 | 返回示例 |
|------|---------|
| 脚本获取成功 | `{"ok":true,"method":"script","platform":"bilibili","content_id":"BVxxx","metrics_params":"..."}` |
| Cookie 失效 | `{"ok":false,"error":"SESSION_EXPIRED","platform":"xhs","method":"script","hint":"..."}` |
| 需浏览器获取 | `{"ok":false,"method":"browser","platform":"twitter","hint":"使用 twitter-interact 技能..."}` |
| 需手动提供 | `{"ok":false,"method":"manual","platform":"wx_mp","hint":"该平台互动数据无法自动获取..."}` |

Exit codes：0=成功/浏览器/手动（非错误），1=一般错误，2=SESSION_EXPIRED。

- **脚本支持**：xhs、bilibili、douyin、kuaishou
- **浏览器获取**：zhihu、toutiao、juejin、twitter、youtube、facebook、instagram、tiktok、pinterest、threads
- **手动提供**：wx_mp、wx_channel

### 流程 2B·用户提供数据（Agent 补录）

用户主动告知已发布内容的信息，Agent 用 `record.sh` 录入基础信息，再用 `update-metrics.sh` 补录互动数据：

```bash
# 1) 录入基础信息
./skills/published-track/scripts/record.sh \
  --platform wx_mp --title "用户提供的标题" --content-type article \
  --source-folder "output_articles/xxx" \
  --publish-url "https://mp.weixin.qq.com/s/xxx" \
  --publish-date "2026-06-14" --distribute-status 1 --notes "用户手动录入"

# 2) 补录互动数据（只传用户提供的字段，其余保持不变）
./skills/published-track/scripts/update-metrics.sh \
  --platform wx_mp --source-folder "output_articles/xxx" \
  --reads 1234 --likes 56 --shares 12
```

各平台可传指标字段见上方「平台与表对应关系」"特有指标"列。

---

## 块三·查询与平台设置

### 流程 3A·查询待分发内容（白天 heartbeat 用）

```bash
./skills/published-track/scripts/query-pending.sh                # 所有平台待分发
./skills/published-track/scripts/query-pending.sh --platform wx_mp # 单平台
```

返回 JSON 数组，每项含 `platform`、`source_folder`、`title`、`publish_url`。

### 流程 3B·设置

**分发状态**：

```bash
./skills/published-track/scripts/set-distribute-status.sh \
  --platform wx_mp --source-folder "output_articles/xxx" --status 2
./skills/published-track/scripts/set-distribute-status.sh \
  --platform wx_mp --id 3 --status 2
./skills/published-track/scripts/set-distribute-status.sh \
  --platform wx_mp --mark-all-distributed
```

**平台打分开关 + 阈值**：

```bash
./skills/content-calibrator/scripts/cal-toggle.sh --list                       # 全平台开关+阈值
./skills/content-calibrator/scripts/cal-toggle.sh --platform wx_mp --status    # 单平台开关
./skills/content-calibrator/scripts/cal-toggle.sh --platform wx_mp --enable    # 启用
./skills/content-calibrator/scripts/cal-toggle.sh --platform wx_mp --disable   # 停用（需确认）
./skills/content-calibrator/scripts/cal-toggle.sh --platform wx_mp --threshold          # 查看阈值
./skills/content-calibrator/scripts/cal-toggle.sh --platform wx_mp --set-threshold 2    # 设阈值
```

阈值语义：每维 0-5，需 **> 阈值**才放行发布；阈值 0 = 不拦截（起步默认）。Agent 不得自动启用某平台打分，必须告知用户由用户决定。阈值可由 Agent 在 content-calibrator 复盘后根据累积数据推荐并经用户确认后设置（见 `content-calibrator/SKILL.md` 复盘段）。

### 流程 3C·通用查询（Agent 按需调用）

```bash
./skills/published-track/scripts/query.sh --platform zhihu            # 某平台全部记录
./skills/published-track/scripts/query.sh --platform zhihu --limit 10 # 最近 N 条
./skills/published-track/scripts/check-published.sh \
  --platform zhihu --source-folder "output_articles/xxx"              # 是否已发布
```

---

## 与发布技能的配合

所有发布技能（wx-mp-publisher、xhs-publish、gaoqian-article、wechat-channels-publish、bilibili-publish 等）的流程统一为 **打分(1A) → 发布 → 记录(1B)**。各技能 SKILL.md 的"打分评估 / 发布记录"段标注此要求，主 agent 无需额外提醒。

**平台代号对照**：`wx-mp-publisher`/`sync-from-mp` → `wx_mp`；`wechat-channels-publish` → `wx_channel`；`xhs-publish` → `xhs`。
