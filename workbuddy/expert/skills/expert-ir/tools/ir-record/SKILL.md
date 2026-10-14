---
name: "ir-record"
description: "IR 投资人关系数据库（SQLite）：投资人档案、接触历史、项目申报三张表，含状态机推进与过期查询。"
description_zh: "IR 投资人关系数据库（SQLite）：投资人档案、接触历史、项目申报三张表，含状态机推进与过期查询。"
description_en: "ir-record: native Xiaobei workflows, tools and reusable resources."
version: "0.3.3"
author: "TeamWiseFlow"
---

## WorkBuddy 执行入口

本文的 wrapper 名称表示本包逻辑命令。执行前读取 `xiaobei-runtime`，通过其统一入口运行命令；不假设全局 PATH 已安装小贝。业务数据写用户当前工作空间，登录态和依赖由该运行层隔离管理。能力以运行层 `list` 返回为准；未包含的浏览器发布/取数步骤使用用户资料或当前 WorkBuddy 实际可用工具，不调用原 OpenClaw 安装或 crew。


# ir-record — IR 记录数据库工具

在 Workspace `db/ir_record.db` 中维护持久化 SQLite 数据库，供投资人发掘与跟进、项目申报使用。

## 数据库位置

```
<Workspace 根>/db/ir_record.db
```

所有命令通过 PATH wrapper `ir-record <子命令>` 调用，不要拼接脚本路径。初始化（幂等，可重复执行）：`ir-record init-db`。

---

## 表结构

### investors（投资人档案）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| name | TEXT NOT NULL | 投资人姓名 |
| type | TEXT NOT NULL | 投资人类别（angel/vc/pe/cvc/fo/other） |
| firm | TEXT | 所属机构 |
| title | TEXT | 职位 |
| email | TEXT | 邮箱 |
| phone | TEXT | 电话 |
| wechat | TEXT | 微信号 |
| linkedin | TEXT | LinkedIn URL |
| source | TEXT | 来源 |
| focus_areas | TEXT | 关注领域（逗号分隔） |
| match_score | TEXT | 匹配度（high/medium/low） |
| status | TEXT NOT NULL DEFAULT 'new' | 进展状态 |
| notes | TEXT | 备注 |
| created_at | TEXT | 记录创建时间 |
| updated_at | TEXT | 最后更新时间 |

**状态机**：
```
new → contacted → bp_sent → meeting → dd → ts → invested
  ↓        ↓         ↓         ↓       ↓     ↓
passed   passed    passed    passed  passed passed
```

### contacts（接触记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| investor_id | INTEGER NOT NULL | 关联 investors.id |
| contact_type | TEXT NOT NULL | 接触方式（email/phone/meeting/intro/pitch/other） |
| direction | TEXT NOT NULL | 方向（outbound/inbound） |
| summary | TEXT NOT NULL | 接触内容摘要 |
| result | TEXT | 结果/对方反馈 |
| next_step | TEXT | 下一步行动 |
| contact_date | TEXT NOT NULL | 接触日期（YYYY-MM-DD） |
| created_at | TEXT | 记录时间 |

### applications（项目申报）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| name | TEXT NOT NULL | 申报项目名称 |
| type | TEXT NOT NULL | 申报类别（competition/grant/subsidy/incubator/other） |
| organizer | TEXT | 主办方/组织方 |
| platform_url | TEXT | 申报平台 URL |
| deadline | TEXT | 截止日期（YYYY-MM-DD） |
| status | TEXT NOT NULL DEFAULT 'planning' | 申报状态 |
| submitted_date | TEXT | 实际提交日期 |
| result | TEXT | 结果/获奖情况 |
| notes | TEXT | 备注 |
| created_at | TEXT | 记录创建时间 |
| updated_at | TEXT | 最后更新时间 |

**申报状态**：
```
planning → drafting → submitted → shortlisted → awarded
                ↓          ↓           ↓
             passed     rejected    rejected
```
- `planning`：计划申报
- `drafting`：材料准备中
- `submitted`：已提交
- `shortlisted`：入围/初筛通过
- `awarded`：获奖/获批
- `rejected`：未通过
- `passed`：放弃申报

---

## 命令

### 初始化

```bash
ir-record init-db
```

### 投资人档案管理

**检查投资人是否已记录**（按姓名+机构去重）：
```bash
ir-record check-investor --name <姓名> --firm <机构名>
```
返回 JSON：`{"exists": true/false, "id": <记录ID或null>}`

**记录新投资人**：
```bash
ir-record record-investor \
  --name <姓名> --type <angel|vc|pe|cvc|fo|other> --firm <机构名> \
  [--title <职位>] [--email <邮箱>] [--phone <电话>] [--wechat <微信号>] \
  [--linkedin <LinkedIn>] [--source <来源>] [--focus-areas <关注领域>] \
  [--match-score <high|medium|low>] [--status <new|contacted|...>] [--notes <备注>]
```
必填：`--name`、`--type`、`--firm`。

**更新投资人状态**：
```bash
ir-record update-status --id <投资人ID> --status <新状态> [--notes <备注>]
```

### 接触记录管理

**检查近期接触**：
```bash
ir-record check-contact --investor-id <ID> --days <天数>
```

**记录接触**：
```bash
ir-record record-contact \
  --investor-id <投资人ID> --contact-type <email|phone|meeting|intro|pitch|other> \
  --direction <outbound|inbound> --summary <接触内容摘要> \
  --contact-date <YYYY-MM-DD> [--result <结果>] [--next-step <下一步行动>]
```
必填：`--investor-id`、`--contact-type`、`--direction`、`--summary`、`--contact-date`。

### 进展查询

**查询投资人 Pipeline 摘要**：
```bash
ir-record query-progress
```

**查询待跟进投资人**（N 天无 contact 进展）：
```bash
ir-record query-stale --days <天数>
```

### 项目申报管理

**检查申报是否已记录**（按项目名+主办方去重）：
```bash
ir-record check-application --name <项目名> [--organizer <主办方>]
```
返回 JSON：`{"exists": true/false, "id": <记录ID或null>}`

**记录新申报**：
```bash
ir-record record-application \
  --name <项目名> --type <competition|grant|subsidy|incubator|other> \
  [--organizer <主办方>] [--platform-url <申报平台URL>] [--deadline <YYYY-MM-DD>] \
  [--status <planning|drafting|submitted|shortlisted|awarded|rejected|passed>] \
  [--submitted-date <YYYY-MM-DD>] [--result <结果>] [--notes <备注>]
```
必填：`--name`、`--type`。

**更新申报状态**：
```bash
ir-record update-application --id <申报ID> --status <新状态> [--notes <备注>] [--result <结果>]
```

**查询申报记录**：
```bash
ir-record query-applications [--status <状态>] [--upcoming <天数>]
```
- 无参数：返回所有申报，按状态排序
- `--status`：按状态过滤
- `--upcoming`：查询未来 N 天内截止的申报

---

## 使用规则

1. **投资人发掘与跟进**：
   - 搜索到投资人后，先用 `check-investor` 判断是否已记录
   - 已在数据库中则跳过，除非有新信息需要更新
   - 新投资人立即用 `record-investor` 记录（status=new）
   - 首次接触后，用 `update-status` 更新状态，用 `record-contact` 记录接触
   - 可随时运行 `query-stale --days 7` 检查超期未跟进；用户启用定时模式后（见 `expert-ir` 包内 `scheduling.md`），由心跳定期运行
   - `query-progress` 获取全局 Pipeline 视图（按需或按用户约定周期运行）
2. **项目申报**（配合 `expert-ir` 包内 Project Application workflow）：
   - 发现申报机会后，先用 `check-application` 判断是否已记录
   - 已在数据库中则跳过，避免重复申报
   - 确认申报后用 `record-application` 记录（status=planning）
   - 提交后更新 status 为 submitted
   - 可随时运行 `query-applications --upcoming 7` 查即将截止的申报；用户启用定时模式后由心跳定期提醒
