# HEARTBEAT_TEMPLATE

此文件为 HEARTBEAT.md 的写入模板。当用户确认某个工作模式的配置后，参照以下格式将对应模式写入 HEARTBEAT.md。

**原则**：只写入用户实际启用的模式，不要预填未启用的模式。

---

## 模式一：Lead Hunting（潜在客户探索）

```markdown
### 模式一：Lead Hunting（潜在客户探索）

**状态**：已启用

**目标平台**：
- xhs：<关键词1>、<关键词2>、<关键词3>
- dy：<关键词1>、<关键词2>
- web：<站点URL>：<搜索关键词>

**潜在客户判定标准**：
- 符合特征：
  - <特征描述1>
  - <特征描述2>
- 排除特征（同行/竞对）：
  - <特征描述1>

**执行参数**：
- 频率：<每天N次 / 每N小时>
- 每次最大探索量：<N个创作者>
- 反馈形式：<列表报告 / Cold Touch 私信 / Email 联系>
- Cold Touch 话术：<话术内容>
- Email 话术：<话术内容>

**执行**：调用 `lead-hunting` 技能
```

---

## 模式二：Comment Engagement（评论区拓展）

```markdown
### 模式二：Comment Engagement（评论区拓展）

**状态**：已启用

**目标平台**：
- xhs：<关键词1>、<关键词2>
- dy：<关键词1>

**互动策略**：<direct_comment / reply_dm / direct_dm>

**互动话术**：
- <话术内容>

**执行参数**：
- 频率：<描述>

**执行**：调用 `comment-engagement` 技能
```

---

## 模式三：Intel Gathering（商业情报采集）

```markdown
### 模式三：Intel Gathering（商业情报采集）

**状态**：已启用

**监控信源**：
- xhs - <账号名/ID>：<监控说明>
- <网站URL>：<监控说明>

**提取标准**：
- <要提取的信息描述>

**交付形式**：<简报 / 报告 / 监控表格>

**执行时间**：<cron 表达式，如 "0 8 * * *">

**执行**：调用 `intel-gathering` 技能
```

---

## 多模式并存

如用户启用了多个模式，HEARTBEAT.md 中按顺序排列已启用的模式，各模式之间用 `---` 分隔。

## 模式禁用

如用户要求停用某个模式，从 HEARTBEAT.md 中删除对应配置段落，并 spawn IT Engineer 移除对应的定时任务配置。
