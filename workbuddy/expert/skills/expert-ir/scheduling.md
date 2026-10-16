# 定时执行（可选）

> 本文件是 `expert-ir` 专家包附属说明：IR 各 workflow 如何落为定时任务。

**原则**：`expert-ir` 的所有 workflow 默认按**一次性任务**执行。**仅当用户明确希望周期性执行**（如每天搜一次投资人、每周生成 Pipeline 摘要）时，才将配置写入 workspace 的 `HEARTBEAT.md` 并配 cron。不要主动建议或预填定时任务。

## 启用流程

1. 先按对应 workflow 跑通一次，与用户确认全部配置要素（目标类别/领域 / 渠道与关键词 / 筛选标准 / 跟进规则 / 执行参数）。
2. 参照下方模板，把**用户实际启用的模式**写入 `HEARTBEAT.md`（不要预填未启用的模式；多模式并存时按顺序排列，模式之间用 `---` 分隔）。
3. 使用当前真实可用的 WorkBuddy 工具 按段内执行时间 / 频率配置 cron。
4. 在 `MEMORY.md`「已启用的定时任务」段登记任务名、cron 表达式与启用日期。

## 停用流程

从 `HEARTBEAT.md` 删除对应配置段落，使用当前真实可用的 WorkBuddy 工具 移除对应 cron，并从 `MEMORY.md` 登记段移除。

---

## HEARTBEAT.md 写入模板

### Investor Hunting（投资人搜索 - 定时执行）

```markdown
### Investor Hunting（投资人搜索）

**状态**：已启用

**搜索目标**：
- 投资人类别：<天使/VC/PE/CVC/不限>
- 偏好领域：<行业/赛道>
- 地域：<国内/海外/不限>

**搜索渠道**：
- <渠道1>：<搜索关键词>
- <渠道2>：<搜索关键词>

**筛选标准**：
- 匹配特征：
  - <特征描述1>
  - <特征描述2>
- 排除特征：
  - <特征描述1>

**执行参数**：
- 频率：<每天N次 / 每N小时>
- 每次最大搜索量：<N个>
- 自动触达：<是/否>
- 触达话术：<话术内容（如启用自动触达）>

**执行**：按 `expert-ir` 的 Investor Hunting Workflow 执行
```

### Relationship Tracking（投资人关系维护 - 定时跟进）

```markdown
### Relationship Tracking（关系跟踪）

**状态**：已启用

**跟进规则**：
- 超过 <N> 天未跟进的活跃投资人 → 提醒用户
- 尽调中的投资人 → 每天检查是否有更新
- 每周一生成 Pipeline 摘要

**执行**：
1. 运行 `ir-record query-progress`（进度查询）
2. 检查是否有超期未跟进的投资人
3. 如有新进展，更新 MEMORY.md 中的 Pipeline 表
4. 如有需要关注的事项，汇总后推送给用户
```

---

## 定时巡检规则（心跳批跑时）

### 投资人过期巡检

> 投资人跟进状态机：`new → contacted → bp_sent → meeting → dd → ts → invested/passed`

**触发条件**：凌晨复盘心跳数据抓完后、用户咨询回复之前插入一个巡检步骤。

```bash
# 查 7 天无 contact 进展的投资人
ir-record query-stale --days 7
```

输出 JSON list（按 `days_since_last` 降序），每条含 `id` / `name` / `firm` / `status` / `match_score` / `last_contact_date` / `next_step` / `days_since_last`。

**处理规则**：

- `status` ∈ {`new`, `contacted`, `bp_sent`, `meeting`, `dd`, `ts`} 且 `days_since_last > 7` → **STALE**，加入"待跟进"列表
- `status` ∈ {`invested`, `passed`} → **跳过**（已完结）
- `match_score` = `low` → **跳过**（非重点关注）

### 申报截止巡检

```bash
# 查 7 天内截止的申报
ir-record query-applications --upcoming 7
```

有即将截止的申报 → 在汇报中提醒用户（附申报名称与截止日期）。

### 汇报格式（心跳总报告加一段）

```
## IR 巡检
共 N 个投资人超过 7 天无进展，重点跟进：
- 张三 @ 红杉（status=meeting, 13 天无进展, last next_step=5/20 约下轮 meeting）
- 李四 @ 真格（status=bp_sent, 9 天无进展, last next_step=5/24 follow up BP）
（其他 N-K 个已完结 / 非重点，已自动跳过）
申报提醒：X 个项目将在 7 天内截止（列名称 + 截止日期）
（无内容的段跳过）
```

### 约束

- 7 天阈值是**默认值**，用户可在 `ir-record/.config.json` 改（待实现）
- 凌晨不主动发起新接触（用现有 `next_step` 提醒用户白天处理）
- 不在心跳里改 `status`（用户白天自己决定推进 / 标记 passed）
- 只批跑用户已配置的模式，不发起配置外的接触
