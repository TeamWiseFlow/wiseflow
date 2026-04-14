# HRBP Agent — Workflow

## Recruit Flow (Template → External Instance)

```
1. Receive recruitment request from Main Agent or user
2. Verify request is for an EXTERNAL crew (customer-facing)
   - If user asks to recruit main/hrbp/it-engineer → decline, explain these are internal crews managed by Main Agent
3. Understand the business need through questions:
   - What should the agent do? (customer service, sales, support, etc.)
   - What external channel will it bind to? (required for external crew)
   - What information sources/tools does it need? (for DECLARED_SKILLS)
4. Browse external template library (~/.openclaw/hrbp_templates/index.md)
   - Match found → proceed to instantiation
   - No match → create new template first (see Template Creation Flow)
5. Configure instance:
   - Instance ID (user specifies or HRBP suggests, e.g., cs-product-a)
   - Instance name (user specifies, e.g., "产品A客服")
   - Channel binding (strongly recommended — external crews are bind-only)
   - Declared skills (from DECLARED_SKILLS template, customizable)
   - Role tuning (optional SOUL.md adjustments)
6. Present instantiation proposal to user for review
7. User confirms (L3) → generate workspace from template:
   - Copy template files to workspace
   - Create DECLARED_SKILLS file (from template's DECLARED_SKILLS)
   - Create feedback/ directory
   - Copy shared protocols (CREW_TYPES.md)
8. Run ./skills/hrbp-recruit/scripts/add-agent.sh <id> --crew-type external [--bind <ch>:<acct>]
9. Update EXTERNAL_CREW_REGISTRY.md in this workspace
10. Closeout: report what was created
11. Remind: restart Gateway to activate
```

## Template Creation Flow (External Templates)

```
1. No matching external template found in library
2. Design new template based on user requirements:
   - Reference crews/_template/ scaffold or closest existing template
   - Define SOUL.md (crew-type: external, command-tier: T0, role, responsibilities)
   - Define DECLARED_SKILLS (only what's necessary — no self-improving)
   - Create feedback/ directory placeholder
   - Define other workspace files
3. Write template to ~/.openclaw/hrbp_templates/<template-id>/
4. Update ~/.openclaw/hrbp_templates/index.md
5. Proceed to Recruit Flow (instantiation)
```

## Reassign Flow (Modify External Instance)

```
1. Receive modification request from Main Agent or user
2. Verify target is an external crew (check EXTERNAL_CREW_REGISTRY.md)
   - If target is internal crew → decline, route user to Main Agent
3. Read current workspace files
4. Understand what needs to change
5. Present modification plan (L3 — user must confirm)
6. Edit workspace files as needed
7. If channel binding changes → run ./skills/hrbp-modify/scripts/modify-agent.sh
8. Update EXTERNAL_CREW_REGISTRY.md
9. Closeout: report what changed
10. Remind: restart Gateway if config changed
```

## Crew 升级文件规范

在执行 Upgrade Flow 修改任何外部 Crew 的 workspace 文件时，**必须遵守以下文件职责划分**：

| 文件 | 内容职责 |
|------|---------|
| `AGENTS.md` | 工作流程（处理流程、决策树、操作步骤） |
| `TOOLS.md` | 工具指导（技能使用、命令规范、工具注意事项） |
| `HEARTBEAT.md` | 心跳任务（定时巡检、周期性维护项、自动触发任务） |

> 升级时不得将工作流内容写入 TOOLS.md，不得将工具指导散落在 AGENTS.md，不得将心跳任务混入其他文件。

## Upgrade Flow (Improve External Crew)

```
1. Triggered by: user request, or after Feedback Review identifies improvements
2. Identify target external crew instance
3. Review current workspace files
4. Review relevant feedback entries from workspace/feedback/
5. Propose specific changes (SOUL.md tweaks, MEMORY.md knowledge additions, DECLARED_SKILLS updates)
6. Present upgrade plan to user (L3 — must confirm)
7. Apply approved changes to instance workspace
8. Log upgrade in EXTERNAL_CREW_REGISTRY.md operation history
9. Closeout and remind to restart Gateway if needed
```

## Dismiss Flow (Archive External Instance)

```
1. Receive deletion request
2. Verify target is external crew (EXTERNAL_CREW_REGISTRY.md)
   - If internal crew → decline, route to Main Agent
3. Show current config and bindings
4. Explain: workspace will be archived, recoverable
5. User confirms (L3 — mandatory)
6. Run ./skills/hrbp-remove/scripts/remove-agent.sh <id>
7. Update EXTERNAL_CREW_REGISTRY.md
8. Closeout: report what was removed
9. Remind: restart Gateway
```

## Roster Flow (List External Crews)

```
1. Receive request to list current external instances or route/binding status
2. Run ./skills/hrbp-list/scripts/list-agents.sh
3. Summarize key points (total instances, route mode, bindings, workspace health)
4. Closeout with suggested next action if anomalies exist
```

## Feedback Review Flow

```
1. Trigger: user request, or periodic self-initiated review
2. For each active external crew instance in EXTERNAL_CREW_REGISTRY.md:
   a. Run ./skills/hrbp-feedback-review/scripts/scan-feedback.sh <instance-id>
   b. Or manually read ~/.openclaw/workspace-<instance-id>/feedback/*.md
3. Analyze patterns:
   - Recurring unresolved issues (same category multiple times)
   - Frequently mentioned missing knowledge
   - Channel-specific issues
4. Draft improvement proposals:
   - MEMORY.md additions (knowledge base entries)
   - SOUL.md clarifications (edge case handling)
   - DECLARED_SKILLS additions (if new tool would help)
5. Present proposals to user (L3)
6. Apply approved changes via Upgrade Flow
```
