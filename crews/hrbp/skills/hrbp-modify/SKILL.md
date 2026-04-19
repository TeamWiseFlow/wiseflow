# HRBP Skill — Modify (调岗)

## Scope
**This skill applies to external crew instances only.**
- Internal crews (`main`, `hrbp`, `it-engineer`) are managed by Main Agent via setup-crew.sh. Do NOT modify their workspace via this skill.
- If the user asks to modify an internal crew, politely explain this and redirect.

## Trigger
User requests to change/update an existing **external** agent instance.

## Procedure

### Step 1: Identify Target Instance
- Check `EXTERNAL_CREW_REGISTRY.md` in your workspace for known external crew instances
- Confirm which instance the user wants to modify
- **Verify crew type**: confirm the target is an external crew (`crew-type: external` in SOUL.md). If it's an internal crew, decline and redirect.
- If ambiguous, list available external instances and ask for clarification

### Step 2: Understand Changes
- Read the target instance's current workspace files (SOUL.md, AGENTS.md, TOOLS.md, etc.)
- Ask the user what needs to change:
  - Role/responsibilities (SOUL.md)
  - Workflow/procedures (AGENTS.md)
  - Tools and permissions (TOOLS.md)
  - Identity/voice (IDENTITY.md)
  - Channel bindings (add/remove direct channel access)
- Present a summary of proposed changes

### Step 3: User Confirmation
- Present the modification plan clearly:
  - Which files will be changed
  - What the changes are (before → after summary)
  - Any binding changes
- **Wait for explicit user confirmation before proceeding**

### Step 4: Apply Changes
After user confirms:

1. **Workspace files**: Edit the relevant .md files in `~/.openclaw/workspace-<instance-id>/`
2. **Channel bindings**: If binding changes are needed, run:
   - Add binding: `bash ./skills/hrbp-modify/scripts/modify-agent.sh <instance-id> --bind <channel>:<accountId>`
   - Remove binding: `bash ./skills/hrbp-modify/scripts/modify-agent.sh <instance-id> --unbind <channel>`
3. **DECLARED_SKILLS**: If skill access changes are needed, edit `~/.openclaw/workspace-<instance-id>/DECLARED_SKILLS`
4. Update `EXTERNAL_CREW_REGISTRY.md` if specialty or route mode changed

### Step 5: Closeout
Report to the user:
- Summary of changes made
- Files modified
- Any binding changes
- Remind: restart Gateway to activate changes (`./scripts/dev.sh gateway`)

## Notes
- Always read current config before proposing changes
- 所有系统配置和渠道绑定操作都需要用户明确确认
- Workspace file edits can proceed after user approves the plan
- **External crew only**: Protected agents (`main`, `hrbp`, `it-engineer`) are internal crews — they are NOT managed by this skill
- Modifications affect the instance only — the source template is not changed
- External crew SOUL.md must retain `crew-type: external` and `command-tier: T0` (or declared tier) — do not remove these
- External crews cannot upgrade themselves; all upgrades must go through HRBP (this skill)
