# HRBP Skill — Usage Monitor (用量监控)

## Trigger
User asks about agent usage, costs, token consumption, or resource monitoring. Examples:
- "各 Agent 用了多少？"
- "看一下本周的用量"
- "哪个 Agent 花费最多？"
- "给我看月度使用报告"

## Procedure

### Step 1: Clarify Query Scope (L1)
Determine what the user wants to see:
- **Which agents**: All agents, or specific agent(s)?
- **Time range**: Today, this week, this month, or cumulative?
- **Metrics focus**: Token usage, cost, or both?

If unclear, default to: all agents, cumulative, both tokens and cost.

### Step 2: Run Usage Query (L1)
Execute the appropriate command:

```bash
# All agents, cumulative (default)
bash ./skills/hrbp-usage/scripts/agent-usage.sh

# Specific agent
bash ./skills/hrbp-usage/scripts/agent-usage.sh --agent <agent-id>

# Daily breakdown (last 7 days)
bash ./skills/hrbp-usage/scripts/agent-usage.sh --period daily

# Daily breakdown (last N days)
bash ./skills/hrbp-usage/scripts/agent-usage.sh --period daily --days 14

# Weekly breakdown
bash ./skills/hrbp-usage/scripts/agent-usage.sh --period weekly --days 28

# Monthly breakdown
bash ./skills/hrbp-usage/scripts/agent-usage.sh --period monthly --days 90
```

### Step 3: Interpret Results (L1)
Present the data to the user with insights:

1. **Overview**: Total calls, total tokens, total cost across all agents
2. **Per-agent breakdown**: Which agents are most/least active
3. **Trends**: If using daily/weekly/monthly, note any patterns (increasing, decreasing, spikes)
4. **Anomalies**: Flag any agent with unexpectedly high usage
5. **Cost efficiency**: Compare input vs output tokens, cache hit ratio

### Step 4: Recommendations (L1)
Based on the data, optionally suggest:
- If an agent has zero usage → ask if it should be removed
- If an agent has very high cost → suggest reviewing its model configuration
- If cache read ratio is low → the agent may benefit from prompt optimization
- If an agent hasn't been used in a long time → flag for review

## Output Format

Present results in a clear, structured format:

```
📊 Agent 用量报告

| Agent | 调用次数 | 总 Token | 成本 |
|-------|---------|---------|------|
| main  | 150     | 500K    | $2.50|
| hrbp  | 30      | 100K    | $0.80|
| dev   | 200     | 800K    | $4.20|

总计: 380 次调用, 1.4M tokens, $7.50

趋势: 本周用量较上周增长 15%
建议: developer agent 用量最高，建议检查其模型配置
```

## Notes
- This skill is read-only (L1) — no system modifications
- Data comes from OpenClaw session transcript files (`~/.openclaw/agents/<id>/sessions/*.jsonl`)
- If no usage data exists, inform the user that agents start recording after their first interaction
- Cost data depends on model pricing configuration in openclaw.json; if pricing not configured, cost will show as "—"
