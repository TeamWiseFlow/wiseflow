---
name: ir-record
description: 维护 IR（投资人关系专员）的 SQLite 追踪数据库，记录投资人档案和接触历史，避免重复接触，跟踪进展状态。
---

# IR Record 技能

在 `./db/ir_record.db` 中维护持久化 SQLite 数据库，供 IR 的三种工作模式使用。

## 数据库位置

```
./db/ir_record.db
```

首次使用需先初始化：`bash ./skills/ir-record/scripts/init-db.sh`

---

## 表结构

### investors（投资人档案）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| name | TEXT NOT NULL | 投资人姓名 |
| type | TEXT NOT NULL | 投资人类别（angel/vc/pe/cvc/fo/other） |
| firm | TEXT | 所属机构（如红杉、高瓴） |
| title | TEXT | 职位（如合伙人、VP） |
| email | TEXT | 邮箱 |
| phone | TEXT | 电话 |
| wechat | TEXT | 微信号 |
| linkedin | TEXT | LinkedIn URL |
| source | TEXT | 来源（如何找到的） |
| focus_areas | TEXT | 关注领域（逗号分隔） |
| match_score | TEXT | 匹配度（high/medium/low） |
| status | TEXT NOT NULL DEFAULT 'new' | 进展状态（new/contacted/bp_sent/meeting/dd/ts/invested/passed） |
| notes | TEXT | 备注 |
| created_at | TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')) | 记录创建时间 |
| updated_at | TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')) | 最后更新时间 |

**状态机**：
```
new → contacted → bp_sent → meeting → dd → ts → invested
  ↓        ↓         ↓         ↓       ↓     ↓
passed   passed    passed    passed  passed passed
```
- `new`：新发现，尚未接触
- `contacted`：已发出首次接触（邮件/私信/引荐请求）
- `bp_sent`：已发送 BP/材料
- `meeting`：已安排或完成会议
- `dd`：尽调中
- `ts`：Term Sheet 谈判中
- `invested`：已完成投资
- `passed`：放弃/被拒

### contacts（接触记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| investor_id | INTEGER NOT NULL | 关联 investors.id |
| contact_type | TEXT NOT NULL | 接触方式（email/phone/meeting/intro/pitch/other） |
| direction | TEXT NOT NULL | 方向（outbound=我方主动, inbound=对方主动） |
| summary | TEXT NOT NULL | 接触内容摘要 |
| result | TEXT | 结果/对方反馈 |
| next_step | TEXT | 下一步行动 |
| contact_date | TEXT NOT NULL | 接触日期（YYYY-MM-DD） |
| created_at | TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now','localtime')) | 记录时间 |

---

## 脚本命令

所有脚本均需在 workspace 根目录下执行。

### 初始化数据库

```bash
bash ./skills/ir-record/scripts/init-db.sh
```

### 投资人档案管理

**检查投资人是否已记录**（按姓名+机构去重）：
```bash
bash ./skills/ir-record/scripts/check-investor.sh --name <姓名> --firm <机构名>
```
返回 JSON：`{"exists": true/false, "id": <记录ID或null>}`

**记录新投资人**：
```bash
bash ./skills/ir-record/scripts/record-investor.sh \
  --name <姓名> \
  --type <angel|vc|pe|cvc|fo|other> \
  --firm <机构名> \
  --title <职位> \
  --email <邮箱> \
  --phone <电话> \
  --wechat <微信号> \
  --linkedin <LinkedIn> \
  --source <来源> \
  --focus-areas <关注领域> \
  --match-score <high|medium|low> \
  --status <new|contacted|...> \
  --notes <备注>
```
必填：`--name`、`--type`、`--firm`。
返回 JSON：`{"ok": true, "id": <记录ID>}` 或 `{"ok": false, "error": "..."}`

**更新投资人状态**：
```bash
bash ./skills/ir-record/scripts/update-status.sh \
  --id <投资人ID> \
  --status <新状态> \
  --notes <备注（可选）>
```
返回 JSON：`{"ok": true}` 或 `{"ok": false, "error": "..."}`

### 接触记录管理

**检查近期接触**（同一投资人，过去 N 天内）：
```bash
bash ./skills/ir-record/scripts/check-contact.sh --investor-id <ID> --days <天数>
```
返回 JSON：`{"has_recent": true/false, "last_contact_date": "<日期或null>"}`

**记录接触**：
```bash
bash ./skills/ir-record/scripts/record-contact.sh \
  --investor-id <投资人ID> \
  --contact-type <email|phone|meeting|intro|pitch|other> \
  --direction <outbound|inbound> \
  --summary <接触内容摘要> \
  --result <结果> \
  --next-step <下一步行动> \
  --contact-date <YYYY-MM-DD>
```
必填：`--investor-id`、`--contact-type`、`--direction`、`--summary`、`--contact-date`。
返回 JSON：`{"ok": true, "id": <记录ID>}` 或 `{"ok": false, "error": "..."}`

### 进展查询

**查询投资人 Pipeline 摘要**（按状态分组）：
```bash
bash ./skills/ir-record/scripts/query-progress.sh
```
返回 JSON 数组，每个投资人的基本信息、当前状态、最近接触日期。

**查询待跟进投资人**（超过 N 天未跟进）：
```bash
bash ./skills/ir-record/scripts/query-stale.sh --days <天数>
```
返回 JSON 数组，列出超过指定天数未跟进的活跃状态投资人。

---

## 使用规则

1. **模式一（Deal Crafting）**：不直接使用数据库，仅通过用户对话和 MEMORY.md 记录材料版本。
2. **模式二（Investor Hunting）**：
   - 搜索到投资人后，先用 `check-investor.sh` 判断是否已记录
   - 已在数据库中则跳过，除非有新的联系方式或信息需要更新
   - 新投资人立即用 `record-investor.sh` 记录（status=new）
   - 首次接触后，用 `update-status.sh` 更新状态，用 `record-contact.sh` 记录接触
3. **模式三（Relationship Tracking）**：
   - HEARTBEAT 触发时运行 `query-stale.sh --days 7` 检查超期未跟进的
   - 用户告知新进展时，立即更新状态和记录接触
   - 每周运行 `query-progress.sh` 获取全局 Pipeline 视图
