# 数据复盘 Workflow（wx_mp）

**wx_mp 的所有数据复盘工作都走这个 workflow**——heartbeat 按量触发的 DNA 评估、用户临时发起的"看看数据 / 复盘一下 / 评估这个 DNA"，统一从这里进。复盘一律**根据数据针对 DNA 做**，没有单篇复盘；复盘过程调用跨平台技能 `content-calibrator`（评估引擎：触发规则、账号基线归一化、趋势计算、证据聚合、报告结构）

本 workflow 提供引擎没有的东西：**wx_mp 平台的归因方法**（指标语义、互动路径映射、DNA 维度回溯、平台混杂因素）。

## 入口判断

走本 workflow：
- heartbeat 凌晨任务 Step 3：wx_mp 有 DNA 触发评估时
- 用户："看看数据怎么样" / "最近复盘一下" / "评估一下 dna-X" / "这个 DNA 最近表现如何"

不走本 workflow：
- 对标账号 / 对标文章分析 → `account-benchmark.md`
- 建 / 更新 DNA → `style-dna.md`
- 单篇数据疑问（"这篇阅读怎么低"）→ 不是复盘，agent 直接取数在账号与 DNA 上下文里回答；若发现指向 DNA 层面的系统性问题，引导用户发起本 workflow 的评估

## wx_mp 归因方法（平台特有，引擎不包含）

### 指标语义

| 指标 | 含义与解读 |
|------|-----------|
| reads | 阅读数，第一层转化结果；标题/选题/推荐流量共同决定 |
| shares | 转发，最强认可信号；与选题社交货币属性相关 |
| favorites | 收藏，实用价值信号；"可带走资产"类内容高 |
| likes | 点赞（在看），轻认可；受文末引导影响大 |
| comments | 评论，互动设计 + 身份张力决定 |

公众号无曝光量接口数据，漏斗第一层（推荐/送达 → 打开）只能从 reads 相对变化推断，不直接观测。

### 互动漏斗 → template 七部分 → 17 维映射

| 漏斗卡点 | 先怀疑的 template 部分 | 可回溯的 DNA 维度 |
|---------|----------------------|------------------|
| 打开率低（reads 比值走低） | 选题、标题 | topic-angle、title-style、cover-image |
| 完读低（读完率低 / 阅读时长短） | 起、承、转 | sentence-rhythm、paragraph-structure、narrative-micro-operations、rhythm |
| 收藏低 | 承、合（实用价值） | argument-logic、professionalism |
| 评论低 | 情感触点、互动设计 | emotion、rhetoric、signature |
| 关注/转化低 | 合、CTA | tone、thinking |

### 平台混杂因素（归因前必排）

1. **账号成熟度**：新号数据天然低、老号天然高；跨账号绝对值不可比，只看同账号比值与走向。
2. **推荐流量波动**：公众号推荐机制放量或收紧造成整体水位漂移——同账号全部作品同步涨跌 → 平台因素，不是 DNA 因素。
3. **选题热度**：热点选题自带流量；单篇突增先查选题是否踩中时效话题。
4. **发布时间与节假日**：发布时段、长假期间阅读习惯变化。
5. **常读用户比例变化**：粉丝结构变化（涨粉/掉粉期）整体抬升或压低水位。

排不掉混杂的写「观察」，不写「结论」。

## 评估流程

### Step 0 - 确定评估对象

```bash
content-calibrator eval --platform wx_mp --check
```

- **heartbeat 路径**：全部 `triggered=false` → 在 Step 5 汇总里报各 DNA 待评估进度（n/5），本 workflow 结束；有 `triggered=true` → 对每个触发 DNA 走 Step 1。
- **用户路径**：用户点名某 DNA → 该 DNA 未达阈值时用 `--dna-id <id> --force`；未点名 → 先看 `--check`，优先评估已触发 DNA，都未触发时问用户是否强制评估某个 DNA。

### Step 1 - 聚合证据

```bash
content-calibrator eval --platform wx_mp                    # 全部触发 DNA
content-calibrator eval --platform wx_mp --dna-id <id>      # 指定 DNA
```

输出逐篇绝对值 + 同账号基线比值 + 每指标趋势走向；`baseline_insufficient` 的记录只作绝对观察。

### Step 2 - 归因分析

按上方「wx_mp 归因方法」执行，同时遵守 `content-calibrator` 的共性归因原则（趋势优先 / 证据可追溯 / 先排混杂）：

1. 判定只看比值与走向，绝对值只作上下文。
2. 逐条排除平台混杂因素。
3. 回读 `wx_mp/dna/<dna-id>/<dna-id>.dna.md` / `.template.md` 与待评估作品原文（`source_folder`），把趋势变化落到 template 七部分与 17 维。

### Step 3 - 报告与标记

1. 写评估报告到 `wx_mp/dna/<dna-id>/evals/{YYYY-MM-DD}.eval.md`，结构按 `content-calibrator` 的评估产物要求（整体判定 / 趋势表 / template 归因 / 逐条建议 / 观察区）。
2. 标记覆盖的记录，防下轮重复评估：

```bash
content-calibrator eval --platform wx_mp --mark-evaluated --ids <本轮记录 id，逗号分隔>
```

### Step 4 - 出口

- 向用户呈现：整体判定 + 逐条优化建议（每条注明目标维度/template 部分与证据篇目）。heartbeat 场景在凌晨汇总里上报，**不唤醒用户**。
- 用户逐条确认后，采纳的建议走 `style-dna.md`「表现反馈」转译进 DNA；**Agent 不得自动更新 DNA**。
- 不涉及风格规则的业务动作（选题方向、栏目增减）直接给行动项，不进 DNA。

## 执行纪律

- heartbeat isolated 会话中本流程由**主 agent inline 执行**，不 调用当前环境提供的专家或子任务工具、不 当前环境的子任务等待工具（评估需连续回读多文件，隔离会话本就无上下文污染）。
