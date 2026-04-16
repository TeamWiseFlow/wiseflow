# HEARTBEAT — sales-cs 定时任务

## 主动跟进流程

当前时间已由系统注入（见上方 `[cron]` 行）。

**执行步骤（每次心跳触发时）：**

1. 先清理过期任务（超过 48 小时仍为 pending，客户已失联）：

```bash
bash ./skills/customer-db/scripts/follow-up-expire.sh
```

2. 查询当前到期的跟进任务：

```bash
bash ./skills/customer-db/scripts/follow-up-due.sh
```

输出为 tab 分隔表格（含 header），字段：`id / peer / user_id_external / follow_up_at / reason / context_summary / status`。

3. 若无到期任务（仅输出 header 或空），回复 `HEARTBEAT_OK` 并结束。

4. 对每条到期任务，依次执行：

   a. 阅读 `context_summary`，生成自然的跟进话术（简短、克制、不施压）

   b. 调用 `proactive-send` 发送消息

   c. 根据当前 `status` 更新记录：

      - `status='pending'`（首次发送）→ 标记为 sent_once：
        ```bash
        bash ./skills/customer-db/scripts/follow-up-mark-sent.sh \
          --id <id> \
          --sent-text "<发送的消息内容>"
        ```

      - `status='sent_once'`（二次发送）→ 标记为 completed：
        ```bash
        bash ./skills/customer-db/scripts/follow-up-complete.sh \
          --id <id> \
          --sent-text "<发送的消息内容>"
        ```

   d. 若发送失败（exit 1），跳过本条，不更新状态��下次心跳自动重试

**跟进话术原则：**
- 基于 `context_summary` 中的客户兴趣点和建议角度生成
- 一句话开场，不超过三句话
- 不要催促，给客户留空间
- 例："您好，之前聊到专业版的事，不知道今天方便看看吗？"
