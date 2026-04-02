---
name: proactive-send
description: >
  向 awada 客户主动发送消息，用于 heartbeat 跟进场景。
  在 openclaw 消息处理循环之外直接写入 Redis outbound stream，
  无需等待客户发起对话。
---

# 主动发送（proactive-send）

本技能让 `sales-cs` 在 heartbeat 中主动向已表达购买意向但延迟的客户发送跟进消息。

---

## 使用方法

```bash
bash ./skills/proactive-send/scripts/send.sh \
  --user-id-external "<user_id_external>" \
  --text "<跟进消息内容>"
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--user-id-external` | 是 | 客户的 awada 用户标识，来自对话上下文 Sender 块的 `id` 字段，也是 `follow_up.user_id_external` 列的值 |
| `--text` | 是 | 发送给客户的消息文本 |

`platform` 和 `lane` 自动从 `~/.openclaw/openclaw.json` 的 `channels.awada` 读取，`channel_id` 和 `tenant_id` 固定为 `"0"`。

### 返回值

- 成功：打印 Redis stream message ID（如 `1712345678901-0`），exit 0
- 失败：打印错误描述到 stderr，exit 1

---

## 典型用法（heartbeat 跟进流程）

```
1. 用 customer-db 查询到期的跟进任务：
   bash ./skills/customer-db/scripts/db.sh sql \
     "SELECT id, peer, awada_customer_id, reason, context_summary, status
      FROM follow_up
      WHERE status IN ('pending', 'sent_once')
        AND follow_up_at <= strftime('%Y-%m-%d %H:%M', 'now', 'localtime')
      ORDER BY follow_up_at ASC"

2. 对每条任务，根据 context_summary 生成跟进话术，然后调用：
   bash ./skills/proactive-send/scripts/send.sh \
     --user-id-external "<user_id_external>" \
     --text "<生成的跟进消息>"

3. 根据发送结果更新 follow_up 状态：
   - status='pending' 时首次发送 → 更新为 'sent_once'，记录 sent_text：
     bash ./skills/customer-db/scripts/db.sh sql \
       "UPDATE follow_up SET status='sent_once', sent_text='<消息内容>', retry_count=retry_count+1 WHERE id=<id>"

   - status='sent_once' 时二次发送 → 直接标记完成：
     bash ./skills/customer-db/scripts/db.sh sql \
       "UPDATE follow_up SET status='completed', sent_text='<消息内容>', completed_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime') WHERE id=<id>"

4. 若发送失败（exit 1），跳过本条，下次 heartbeat 自动重试
```

---

## 注意事项

- **每位客户最多主动发送两次**：第一次发送后状态改为 `sent_once`；第二次发送后状态改为 `completed`，不再继续跟进，避免骚扰
- **客户主动回复后自动停止**：hook 会在客户下次发消息时将 `pending`/`sent_once` 任务标记为 `completed`
- **不要在非 heartbeat 场景主动调用**：本技能仅用于 heartbeat 触发的定时跟进，不应在正常对话中调用
- **消息内容应自然克制**：基于 `context_summary` 生成，不要施压，给客户留空间
