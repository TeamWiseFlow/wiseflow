# HRBP Skill — External Crew Roster (对外 Crew 花名册)

## Trigger
User asks to list external crew instances, check current external agents, or inspect their bindings/status. Examples:
- "现在有哪些对外 crew？"
- "列一下当前的客服 agent"
- "看下外部 crew 花名册"
- "哪些 agent 是绑定飞书的？"

> **Scope: external crews only.** Internal crews (main / hrbp / it-engineer) are managed by Main Agent — not listed here.

## Procedure

### Step 1: Query Roster
Run:

```bash
# List all registered external agents with binding/workspace status
bash ./skills/hrbp-list/scripts/list-agents.sh
```

### Step 2: Summarize for User
Present concise takeaways:
1. Total external crew count
2. Each instance: ID, name, source template, channel bindings
3. Missing workspace or abnormal status (if any)

## Notes
- This skill is read-only — no system modifications
- Data source: `EXTERNAL_CREW_REGISTRY.md`（本 workspace 权威记录）+ `~/.openclaw/openclaw.json`（bindings/status）
- External crews are **bind-only** — no spawn mode
- If registry is empty or missing, check if any external crews have been recruited yet
