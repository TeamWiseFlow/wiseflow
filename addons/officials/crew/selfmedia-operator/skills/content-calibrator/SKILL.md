---
name: content-calibrator
description: 内容校准预测循环——打分 → 盲预测 → T+3d复盘 → 进化 rubric。按平台独立迭代，每个平台拥有自己的 rubric、校准池、预测日志、受众画像。本技能负责打分（blind sub-agent + score-only.sh + 阈值门 + 流程 1A）与校准闭环；发布记录与数据采集由 published-track 统一管理。
metadata:
  openclaw:
    emoji: 🎯
    requires:
      bins:
      - bash
      - sqlite3
      - node
---

# Content Calibrator — 内容校准预测循环

> 方法论源自 cheat-on-content，适配 openclaw + selfmedia-operator 工作流。
> **三条不可妥协原则**：
> 1. **盲预测**：预测必须在看到实际数据之前写完，写完即 immutable
> 2. **升级 = 全量重打**：rubric 升级时校准池所有样本必须重打分
> 3. **rubric 是工作台不是博物馆**：被推翻/吸收的观察删掉，git history 是档案

---

## 核心设计：按平台独立迭代

**一套程序逻辑，N 套校准实例。** 每个平台拥有完全独立的：

| 组件 | 说明 | 为什么必须分开 |
|------|------|---------------|
| rubric | 评分维度 + 权重 | 不同内容形态的预测维度不同；即使维度相同，权重会分化 |
| calibration pool | 校准样本池 | 不同平台的 baseline 量级不同（公众号 1w 阅读 ≠ 小红书 1w 浏览） |
| predictions | 预测日志 | 同一篇内容发到两个平台，预测是两条独立 immutable 日志 |
| baseline | 基线播放/阅读量 | 平台间量级差异巨大 |
| bucket | 流量档位边界 | 绝对桶完全不同，比率桶的 baseline 也不同 |
| benchmark | 对标账号 | 公众号对标和小红书对标的 pattern 完全不同 |
| audience | 受众画像 | 两个平台受众画像差异很大 |

---

## 核心闭环

```
📊 打分 → 🎯 盲预测 → 🚀 发布 → 📈 T+3d复盘 → 🧬 进化 rubric
```

每个平台独立走这个闭环。公众号的 rubric 升级不影响小红书的 rubric。

---

## 与 published-track 的集成

发布流程为 **打分(1A) → 发布 → 记录(1B)**。**打分（1A）由本技能负责，发布记录（1B）由 published-track 负责。**

### 流程 1A·打分评估（发布前自检）

发布前对稿件做盲打分 + 阈值门，**避免主 agent 自创自评**。

1. **主 agent `sessions_spawn` 一个 blind sub-agent**，只喂 `script_path`（稿件/视频定稿）+ `calibration/<platform>/rubric_notes.md`。sub-agent 硬禁读 `.cheat-state.json`/`predictions/`/`rubric-memo.md`/`audience.md`/对话历史，输出严格 JSON 7 维分（ER/HP/SR/QL/NA/AB/PV，各 0-5）+ per-dim confidence。
2. 主 agent 拿分调 `score-only.sh` 校验 + 算 composite + 判阈值门：
   ```bash
   ./skills/content-calibrator/scripts/score-only.sh \
     --platform wx_mp --content-path "output_articles/xxx/article.md" \
     --cal-er 3 --cal-hp 4 --cal-sr 3 --cal-ql 4 --cal-na 3 --cal-ab 4 --cal-pv 2
   ```
   返回 JSON 含 `passed` 与 `failing_dims`。阈值取自 `calibration/<platform>/.cheat-state.json` 的 `score_threshold`（默认 0=不拦截），**每维需 > 阈值**才算通过。
3. **阈值门**：`passed=false` → 主 agent 据 `failing_dims` 改稿 → 重新 spawn blind sub-agent 打分 → 再判门。**最多 2 轮**，仍不达标 → 暂停发布、上报用户裁定。
4. `passed=true` → 放行，进入发布技能。
5. **平台未启用 calibration**（`calibration/<platform>/` 不存在）→ 跳过 1A，直接发布。

> **视频内容**：打分对象是**脚本定稿**（storyboard/口播稿），不是成片。视频技能流程 = 打分(定稿) → 制作 → 发布 → 记录。成片后不再打分。

### 流程 1B·发布记录（由 published-track 承接）

打分通过并发布成功后，由 `published-track/scripts/record.sh` 落库（提供 `--cal-*` 分数 → `cal_enabled=1` + 算 composite；不提供 → `cal_enabled=0`）。详见 `published-track/SKILL.md`。

### 平台打分开关 + 阈值

`content-calibrator/scripts/cal-toggle.sh`（`--enable/--disable/--set-threshold N/--threshold/--list`）。

### 数据采集由 published-track 统一管理

**content-calibrator 不再直接抓取平台数据。** 数据采集流程：

1. **一键获取**：使用 `published-track/scripts/fetch-and-update-metrics.sh`（封装 login-manager 探活 → API 抓取 → DB 写入）
2. **复盘时**：直接从 published-track DB 读取数据，不另行抓取
3. **深度数据**（完播率、转粉率、评论内容等）：仍需 browser tool + CDP 拦截，但由 published-track 的心跳任务负责采集和更新

### wx-mp-hunter 数据获取说明

⚠️ **wx-mp-hunter 无法获取微信公众号文章的阅读数、点赞数等互动数据。** 微信公众号的互动数据需要登录微信公众号后台查看，wx-mp-hunter 只能获取文章标题、正文和链接。

因此：
- 微信公众号的复盘数据只能从 published-track DB 中读取（由心跳巡检手动更新）
- 如需精确数据，用户需手动提供或通过微信公众号后台截图

---

## 路由表（触发词 → 操作）

| 用户说 | 操作 | 前置条件 |
|--------|------|----------|
| "初始化校准 [--platform xxx]" | Init | 首次使用 |
| "打分这篇 [path] --platform xxx" | Score | 该平台 rubric_notes.md 存在 |
| "预测这篇 [path] --platform xxx" / "启动预测" | Predict | 已 init + 有最终稿 |
| "复盘 [path] --platform xxx" / "T+3d 数据来了" | Retro | 有预测 + 已发布 + 过时间窗口 |
| "升级公式 --platform xxx" / "bump rubric" | Bump | 校准池 ≥ MIN_SAMPLES |
| "导入对标 --platform xxx" / "learn from" | LearnFrom | 有 viral-chaser 报告或用户提供对标数据 |
| "校准状态 [--platform xxx]" / "calibration status" | Status | 任意时刻 |
| "加维度 XX --platform xxx" | 维度变更 | **必须用户确认** |
| "改权重 XX --platform xxx" | 权重变更 | **必须用户确认** |

### 平台启用控制

**是否启用某个平台的 calibration，必须由用户决定。** Agent 不得自动启用。

- 启用：`./skills/content-calibrator/scripts/cal-toggle.sh --platform <platform> --enable`
- 停用：`./skills/content-calibrator/scripts/cal-toggle.sh --platform <platform> --disable`
- 查看状态：`./skills/content-calibrator/scripts/cal-toggle.sh --list`

Agent 在复盘或发布时，发现对应平台未启用 calibration，**不得自动启用**，应告知用户"该平台未启用 content-calibrator，如需启用请确认"。

`--platform` 为必填参数（Init 除外，Init 时交互询问或 Agent 自主判断）。支持的平台 ID：

| 平台 ID | 平台 | 内容形态 |
|---------|------|---------|
| `wx_mp` | 微信公众号 | 长文 |
| `wx_channel` | 微信视频号 | 短视频 |
| `xhs` | 小红书 | 图文/视频笔记 |
| `zhihu` | 知乎 | 文章/回答 |
| `bilibili` | B站 | 视频 |
| `douyin` | 抖音 | 短视频 |
| `kuaishou` | 快手 | 短视频 |
| `toutiao` | 今日头条 | 文章 |
| `youtube` | YouTube | 视频 |

---

## 文件结构

```
<workspace>/
├── calibration/                     # 校准系统根目录
│   ├── wx_mp/                       # 公众号独立体系
│   │   ├── rubric_notes.md          # 评分公式（blind sub-agent 可读）
│   │   ├── rubric-memo.md           # 观察记录（含实绩数据，blind 不可读）
│   │   ├── .cheat-state.json        # 该平台状态文件
│   │   ├── predictions/             # immutable 预测日志
│   │   │   └── YYYY-MM-DD_<id>_<short>.md
│   │   ├── benchmark.md             # 对标账号信息
│   │   └── audience.md              # 受众画像
│   ├── wx_channel/                  # 视频号独立体系
│   │   ├── rubric_notes.md
│   │   ├── rubric-memo.md
│   │   ├── .cheat-state.json
│   │   ├── predictions/
│   │   ├── benchmark.md
│   │   └── audience.md
│   ├── xhs/                         # 小红书独立体系
│   │   ├── rubric_notes.md
│   │   ├── rubric-memo.md
│   │   ├── .cheat-state.json
│   │   ├── predictions/
│   │   ├── benchmark.md
│   │   └── audience.md
│   └── ...                          # 更多平台
```

---

## Init — 初始化

为指定平台创建 `calibration/<platform>/` 目录和初始文件。

**两种触发方式**：
- **用户主动**：用户说"初始化校准"或"我要做 XX 平台" → 交互式问答
- **Agent 不得自主初始化**：必须用户明确要求

### 用户主动触发流程

1. 询问或从 `--platform` 参数获取平台 ID
2. 创建目录结构 `calibration/<platform>/`
3. 写入 `rubric_notes.md`（根据平台选择默认 rubric）
4. 写入 `.cheat-state.json`（cold-start 模式）
5. 询问用户 5 个问题：内容形态、典型篇幅、发布频率、对标账号（可选）、该平台 baseline
6. 如有对标账号 → 触发 LearnFrom

### 默认 Rubric 按平台分发

| 平台 | 默认 rubric | 说明 |
|------|------------|------|
| wx_mp | 长文 rubric（ER/HP/SR×1.5 + QL/NA/AB/PV×1.0） | 公众号核心驱动力：情感 + 钩子 + 社会议题 |
| wx_channel | 视频 rubric（ER/HP/SR×1.5 + QL/NA/AB/PV×1.0） | 视频号核心驱动力：情感 + 钩子 + 社会议题 |
| xhs | 图文笔记 rubric（ER/HP/SR×1.5 + QL/NA/AB/PV×1.0） | 起步同维度，bump 后会分化 |
| bilibili/douyin/kuaishou | 视频 rubric（ER/HP/SR×1.5 + QL/NA/AB/PV×1.0） | 起步同维度，bump 后会分化 |
| 其他 | 同上 | 起步同维度，bump 后会分化 |

---

## Score — 打分

给单篇稿子打 rubric 分。**脚本不做 LLM 打分**；打分由主 agent `sessions_spawn` 的 blind sub-agent 完成，在发布前作为自检门（流程见上方"流程 1A·打分评估"）。

**blind sub-agent 隔离规则**（主对话已看过用户对话/实绩/复盘历史，inline 打分会被污染，故必须 delegate）：

- **白名单只读**：稿件（`script.md`/`article.md`/`post.md`）+ `calibration/<platform>/rubric_notes.md`
- **硬禁读**：`rubric-memo.md`、`.cheat-state.json`、`predictions/`、`audience.md`、`benchmark.md`、对话历史
- **输出**：严格 JSON 7 维分（ER/HP/SR/QL/NA/AB/PV，各 0-5）+ per-dim confidence
- Bump Phase 2 校准池重打分**强制** blind sub-agent，不接受任何 fallback
- Predict Phase 2.5 做 disagreement detection：blind 与主 Claude 自估 |delta| ≥ 2 → 弹用户裁定

### 当前默认 rubric（所有平台起步版 v0）

7 个维度，每维 0-5 整数分：

| 维度 | 代号 | 含义 | 权重 |
|------|------|------|------|
| 情感共鸣 | ER | 读者能否产生"说的就是我"的代入感 | ×1.5 |
| 钩子强度 | HP | 标题/开头是否锁定注意力 | ×1.5 |
| 社会议题共振 | SR | 是否触及社会讨论 | ×1.5 |
| 金句密度 | QL | 是否有独立可传播的表达 | ×1.0 |
| 叙事性 | NA | 是否有清晰的故事弧线 | ×1.0 |
| 受众广度 | AB | 话题的普适程度 | ×1.0 |
| 实用价值 | PV | 读者能否获得可操作的信息 | ×1.0 |

**composite = (ER×1.5 + HP×1.5 + SR×1.5 + QL + NA + AB + PV) / 8.5 × 2.0**

---

## Predict — 盲预测

在看到任何实际数据之前写 immutable 预测日志。

### 流程

1. **Blind check**：确认用户未看过后续数据
2. 读最终稿 + `calibration/<platform>/rubric_notes.md` + state
3. **Blind sub-agent 盲打分**（只看稿子 + rubric，不看对话历史）
4. 锚点对比（从 `calibration/<platform>/predictions/` 找历史相近 composite 的样本）
5. 给 bucket（流量档位）+ 概率分布 + 中枢
6. 写反事实场景 + 关键校准假设
7. **用户 review**：展示完整草拟版，等 "ok" 或挑刺
8. 落盘到 `calibration/<platform>/predictions/`，预测段 immutable

### Cold-start 简化

前 5 篇不要求完整 bucket 数字，只给 7 维分 + 一句话 bet。第 5 篇复盘后解锁完整预测。

---

## Retro — 复盘

T+N 天后从 published-track DB 读实际数据 → 对比预测 → 提炼观察。

### 两个入口

#### 入口 1：凌晨 HEARTBEAT 自动复盘

心跳巡检时，检查每个已启用 calibration 的平台：
- 从 published-track DB 读取该平台所有 `cal_enabled=1` 且有预测但未复盘的记录
- 检查是否积累了 **5 个新数据点**（有实际互动数据但尚未复盘）
- 如有 ≥5 个 → 自动执行复盘流程

#### 入口 2：用户导入对标

用户主动提供对标账号/爆款内容数据，触发 LearnFrom 流程。这是**校准 rubric 本身**的入口——通过分析对标内容，提炼该平台高流量内容的 pattern，调整 rubric 维度和权重。

> **复盘的本质**：复盘是"拿实际数据验证预测，提炼观察，可能触发 rubric 升级"。导入对标是"从外部信号校准 rubric 的初始假设"。两者互补：复盘是内源校准，对标是外源校准。

### 数据来源（全部从 published-track DB）

复盘时**只从 published-track DB 读取数据**，不另行抓取：

```bash
# 读取某平台某篇内容的互动指标
./skills/published-track/scripts/query.sh --platform wx_mp --limit 10

# 或直接 SQL
sqlite3 db/published_track.db "SELECT * FROM pub_wx_mp WHERE source_folder='output_articles/xxx'"
```

### 阈值推荐（复盘副产物）

复盘积累数据后，Agent 可评估"发布前自检阈值门"的 `score_threshold` 是否合理：观察各维度分与实际互动的相关性，若某维度低分内容普遍表现差，可建议提高该平台阈值。**Agent 不得自动改阈值**，需向用户给出建议值与依据，经用户确认后执行：

```bash
./skills/content-calibrator/scripts/cal-toggle.sh --platform <platform> --set-threshold <N>
```

起步期阈值默认 0（不拦截），待累积足够复盘样本后再收紧。

**各平台数据获取能力**（由 `published-track/scripts/fetch-and-update-metrics.sh` 统一调度）：

| 平台 | 方案 | 心跳可自动更新 | 需手动补充 | 说明 |
|------|------|--------------|-----------|------|
| 小红书 | 脚本 | ✅ likes/favorites/comments/shares | 完播率/转粉率 | xhshow 签名 + cookie |
| B站 | 脚本 | ✅ plays/likes/coins/favorites/danmaku/comments | 完播率 | 公开 API，无需 cookie |
| 抖音 | 脚本 | ⚠️ plays/likes/comments/shares/favorites | 完播率 | a_bogus 签名 + cookie |
| 快手 | 脚本 | ⚠️ plays/likes/comments | — | GraphQL + cookie |
| 知乎 | 浏览器 | ⚠️ views/upvotes/comments/favorites | — | browser snapshot |
| 今日头条 | 浏览器 | ⚠️ impressions/reads/comments/likes | — | browser snapshot |
| 掘金 | 浏览器 | ✅ views/likes/comments/favorites | — | browser snapshot（无需 cookie） |
| Twitter/X | 浏览器 | ⚠️ views/likes/retweets/replies/bookmarks | — | twitter-interact 技能 |
| YouTube | 浏览器 | ✅ views/likes/comments/shares | — | browser snapshot（无需 cookie） |
| 微信公众号 | 跳过 | ❌ 无法自动获取 | reads/likes/shares 等 | 需用户手动提供 |
| 微信视频号 | 跳过 | ❌ 无法自动获取 | plays/likes/comments/shares/favorites | 需用户手动提供 |

### 流程

1. 校验时间窗口（默认 T+3d）
2. 从 published-track DB 读互动数据
3. 写实绩段 + top 评论关键词聚类（如有评论数据）
4. 验证/推翻预测的各假设
5. 提炼新观察 → 写入 `calibration/<platform>/rubric-memo.md`
6. 检测是否触发 bump（≥3 次同向偏差）

---

## Bump — Rubric 升级

系统性偏差信号 → 校准池全量重打 → 排序一致性校验 → 落地新公式。

**只影响当前平台的 rubric**，其他平台不受影响。

### 流程

1. 前置门槛检查（校准池样本数 + 观察强度）
2. 写出新公式完整方程
3. 校准池全量重打分（blind sub-agent 隔离）
4. 计算排序一致性（新公式排序 vs 实际排序，阈值 4/5）
5. 落地 + cleanup pass（删被推翻/吸收的观察）
6. 更新所有校准样本的 Re-scored 标记
7. 更新 `calibration/<platform>/rubric_notes.md` 版本速查

---

## 维度与权重变更规则

**维度和权重可以被修改，但必须满足以下条件之一**：
1. **用户主动要求** — "给公众号加个 XX 维度" / "把小红书的 SR 权重调到 2.0"
2. **Agent 提议 + 用户确认** — Agent 在 Bump 流程中检测到系统性偏差后提议变更，**必须等待用户明确同意才生效**

变更流程：
- 变更维度（增/删/替换）→ 走 Bump 全量重打 + 排序一致性校验
- 变更权重 → 走 Bump 流程
- 变更被拒绝 → rubric 不动，观察记入 `rubric-memo.md`

---

## LearnFrom — 导入对标

从对标账号/爆款内容中提取 pattern，作为该平台 rubric 初始校准信号。

### 数据来源

1. **viral-chaser 追爆报告**：已下载的爆款视频分析 → 提取结构 pattern
2. **用户提供的数据**：手动粘贴对标账号数据
3. **published-track DB 中的历史数据**：该平台已发布内容的互动数据

> ⚠️ wx-mp-hunter **无法获取**公众号互动数据，不能作为对标数据来源。

### 流程

1. 确认对标来源（viral-chaser 报告 / 用户提供数据 / 历史数据）
2. 分析 pattern：哪些维度在高流量内容中一致偏高/偏低
3. 派生 rubric 信号（调整权重/维度）
4. 写入 `calibration/<platform>/benchmark.md` + 更新 `rubric-memo.md`

---

## Status — 校准状态看板

显示指定平台（或所有平台）的校准循环状态：

```
📊 Content Calibrator 状态

平台: wx_mp（微信公众号）
模式: calibration（已过 cold-start）
Rubric: v0（长文）
校准池: 8 篇（5 篇有实绩）
上次预测: 2026-06-08
待复盘: 2 篇
Buffer: 0

最近 5 篇偏差:
  ✅ AI团队运营  预测 30-100w  实际 45w   +13%
  ❌ 一人公司    预测 30-100w  实际 8w    -73%
  ✅ 搞钱思维    预测 5-30w   实际 22w   +10%
  ...

系统性偏差: 无（连续同向 < 3）

---

平台: xhs（小红书）
模式: cold-start
Rubric: v0（图文笔记）
校准池: 0 篇
（尚未开始校准循环）
```

---

## 脚本

### 发布记录（合并入口 record.sh）

Agent 发布后调用 `record.sh`，行为：提供任意 `--cal-*` 分数 → 置 `cal_enabled=1` + 算 composite + 记 `cal_rubric_version`；不提供 → `cal_enabled=0`。`score-and-record.sh` 已合并为 `record.sh` 的薄 wrapper。

```bash
# 打分通过的平台 — 把 blind sub-agent 打的分一并传入
./skills/published-track/scripts/record.sh \
  --platform wx_mp \
  --title "AI 时代的一人公司" \
  --content-type article \
  --source-folder "output_articles/ai-one-person-company" \
  --publish-url "https://mp.weixin.qq.com/s/xxx" \
  --cal-er 3 --cal-hp 4 --cal-sr 4 --cal-ql 3 --cal-na 2 --cal-ab 4 --cal-pv 3

# 未启用 calibration 或补发 — 不传 --cal-* 即可
./skills/published-track/scripts/record.sh \
  --platform xhs \
  --title "标题" \
  --content-type post \
  --source-folder "output_articles/xxx" \
  --publish-url "https://www.xiaohongshu.com/xxx"
```

### 打分结果校验（不写入数据库）

Agent 按 rubric 打完 7 维分后，可用 `score-only.sh` 校验分数合法性、计算 composite 并输出结构化 JSON，不写入 DB。此脚本不做 LLM 打分，仅校验并格式化 Agent 已打好的分数。

```bash
./skills/content-calibrator/scripts/score-only.sh \
  --platform wx_mp \
  --content-path "output_articles/xxx/article.md" \
  --cal-er 3 --cal-hp 4 --cal-sr 4 --cal-ql 3 --cal-na 2 --cal-ab 4 --cal-pv 3
```

### 平台打分开关管理

```bash
# 查看所有平台
./skills/content-calibrator/scripts/cal-toggle.sh --list

# 启用/停用
./skills/content-calibrator/scripts/cal-toggle.sh --platform wx_mp --enable
./skills/content-calibrator/scripts/cal-toggle.sh --platform wx_mp --disable
```

### 初始化平台

```bash
./skills/content-calibrator/scripts/init.sh --platform <platform_id>
```

创建 `calibration/<platform_id>/` 目录和初始文件。幂等——已存在则跳过。

### 查询 published-track 数据

```bash
./skills/content-calibrator/scripts/query-metrics.sh --platform <platform> --source-folder <folder>
```

从 published-track DB 查询某篇内容的互动指标。

### 构建校准池

```bash
./skills/content-calibrator/scripts/build-calibration-pool.sh --platform <platform>
```

从 published-track DB 构建指定平台的校准池。

### 导入追爆报告

```bash
./skills/content-calibrator/scripts/import-viral-chaser.sh --platform <platform> <report-path>
```

将 viral-chaser 追爆报告导入为指定平台的对标信号。
