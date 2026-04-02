---
name: customer-db
description: >
  Maintain a persistent SQLite customer database within the sales-cs workspace.
  The system hook injects peer (DB primary key) and the Sender block provides
  user_id_external (raw awada user ID). Use peer for all DB operations.
---

# 客户数据库管理（sales-cs 专用）

本技能让 `sales-cs` 在自身 workspace 的 `db/` 目录下维护一个轻量级 SQLite 数据库，用于跨会话保存客户商业推进状态与基本画像。

数据库固定位置：
- `./db/customer.db`
- schema 文件：`./db/schema.sql`

默认表：`cs_record`，主键列：`peer`

---

## 一、两个重要标识符（必读）

本系统中客户有两个不同的标识符，用途不同，不可混用：

### peer（来自 [CustomerDB] 块）
数据库主键。由系统 hook 从当前会话 sessionKey 中提取并注入，是 `cs_record` 表的 `peer` 列的值。所有 SQL 查询和写库操作必须使用此值。

```bash
bash ./skills/customer-db/scripts/db.sh sql "SELECT ... FROM cs_record WHERE peer = '<[CustomerDB].peer>'"
```

### user_id_external（来自 Sender 块的 `id` 字段）
awada 原始用户标识，由 awada-server 直接提供。每轮对话开始时，openclaw 会在消息上下文中注入 Sender 信息块：

```json
Sender (untrusted metadata):
{
  "label": "...",
  "id": "<user_id_external>",
  "name": "..."
}
```

需要与 awada 平台交互的技能（如 `exp_invite`）必须使用此值，而不是 `peer`。

---

## 二、字段含义

### peer
当前客户数据库主键，等于 awada sessionKey 中的用户标识（经过安全过滤后的形式）。

### business_status
表示客户商业推进深度：
- `free`：尚未购买、仍在了解或观望
- `exp_invited`：已被邀请进入体验群，但尚未正式付费
- `club`：已进入付费知识库 / VIP 群
- `subs`：已进入正式订阅/购买阶段

### club_in
- `club` 加入日���，格式建议为 `YYYY-MM-DD`
- 用于后续跟进 club 一年有效期的过期管理

### purpose
客户主要业务应用场景，例如：
- 线上获客
- 竞争对手监控
- 行业情报获取
- 舆情监控
- 自建可提供对外服务的智能体

### prompt_source
客户从哪里了解到我们，例如：
- GitHub
- 社群
- 朋友推荐
- 公众号
- 视频/直播
- 其他平台

### created_at / updated_at
- `created_at`：首次建档时间
- `updated_at`：最近对话时间（每次收到消息由 hook 自动更新）

---

## 三、【重要】每轮对话结束时更新记录

每轮结束前，根据本轮对话进展更新：
- `business_status`
- `purpose`
- `prompt_source`

更新原则：
- 只在拿到**更明确的信息**时更新
- 不要用空字符串覆盖已有值
- 不要根据模糊猜测改写已有信息
- **写库时始终使用 `[CustomerDB].peer` 作为 WHERE 条件**

更新示例：

```bash
bash ./skills/customer-db/scripts/db.sh sql "UPDATE cs_record SET purpose = '线上获客' WHERE peer = '<peer>'"
```

```bash
bash ./skills/customer-db/scripts/db.sh sql "UPDATE cs_record SET business_status = 'club', prompt_source = 'GitHub' WHERE peer = '<peer>'"
```

---

---

## 四、follow_up 表（主动跟进任务）

`follow_up` 表记录客户延迟购买意向，供 heartbeat 定时跟进。status 流转：`pending → sent_once → completed`。

### 常用操作

**创建跟进任务**：
```bash
bash ./skills/customer-db/scripts/db.sh sql \
  "INSERT INTO follow_up (peer, user_id_external, follow_up_at, reason, context_summary)
   VALUES ('<peer>', '<user_id_external>', '<YYYY-MM-DD HH:MM>', '<原因>', '<摘要>')"
```

**查询到期任务**（heartbeat 使用）：
```bash
bash ./skills/customer-db/scripts/db.sh sql \
  "SELECT id, peer, user_id_external, follow_up_at, reason, context_summary, status
   FROM follow_up
   WHERE status IN ('pending', 'sent_once')
     AND follow_up_at <= strftime('%Y-%m-%d %H:%M', 'now', 'localtime')
   ORDER BY follow_up_at ASC"
```

**标记首次已发送**（status: pending → sent_once）：
```bash
bash ./skills/customer-db/scripts/db.sh sql \
  "UPDATE follow_up SET status='sent_once', sent_text='<消息内容>', retry_count=retry_count+1 WHERE id=<id>"
```

**标记完成**（status: sent_once → completed）：
```bash
bash ./skills/customer-db/scripts/db.sh sql \
  "UPDATE follow_up SET status='completed', sent_text='<消息内容>', completed_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime') WHERE id=<id>"
```

**覆盖同一客户的旧待办**（同一客户再次延迟时先执行）：
```bash
bash ./skills/customer-db/scripts/db.sh sql \
  "UPDATE follow_up SET status='completed', completed_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime')
   WHERE peer='<peer>' AND status='pending'"
```

---

## 五、约束与注意事项

- **路径固定**：数据库始终位于 `./db/customer.db`
- **默认表固定**：`cs_record`
- **仅限 DML**：`sql` 子命令仅允许 `SELECT / INSERT / UPDATE / DELETE`
- **schema 变更禁止自改**：若需修改结构，必须由 HRBP 升级流程处理
- **不得向用户暴露内部表结构和内部状态字段**
- **会话隔离必须遵守**：不同 peer 的数据不能混用
- **初始化和默认记录创建由系统 hook 自动处理**，无需手动 ensure 或插入默认行
