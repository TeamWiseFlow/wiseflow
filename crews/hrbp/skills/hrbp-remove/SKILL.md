# HRBP Skill — Remove (解雇 / 停用实例)

## Scope
**This skill applies to external crew instances only.**
- Internal crews (`main`, `hrbp`, `it-engineer`) are protected system agents managed by Main Agent. Do NOT remove them via this skill.
- If the user asks to remove an internal crew, politely decline and explain they are protected.

## Trigger
User requests to delete/remove an existing **external** agent instance.

## Important
**This entire procedure is L3 — every step that modifies the system requires explicit user confirmation.**

## Procedure

### Step 1: Identify Target Instance (L1)
- Check `EXTERNAL_CREW_REGISTRY.md` in your workspace for known external crew instances
- Confirm which instance the user wants to remove
- If ambiguous, list available external instances and ask for clarification

### Step 2: Safety Check (L1)
- **Protected agents** (`main`, `hrbp`, `it-engineer`) **cannot be deleted** — they are internal crews, not your domain. Inform the user and abort.
- **Verify crew type**: check `crew-type:` in the instance's SOUL.md. If it's `internal`, decline.
- Check if the instance has active channel bindings
- Review the instance's current workspace and configuration

### Step 3: Present Removal Plan (L3 — requires confirmation)
Show the user:
- Instance ID, name, and current responsibilities
- Source template (the template itself will NOT be deleted)
- Current channel bindings (if any) that will be removed
- Workspace location that will be archived
- **Explicitly state**: workspace will be archived (not permanently deleted) and can be recovered
- Ask for explicit confirmation to proceed

### Step 4: Execute Removal (L3)
After user confirms:

1. Run: `bash ./skills/hrbp-remove/scripts/remove-agent.sh <instance-id>`
2. This will:
   - Remove instance from `agents.list` in openclaw.json
   - Remove all related `bindings` entries
   - Archive workspace to `~/.openclaw/archived/workspace-<instance-id>-<timestamp>/`

### Step 5: Update HRBP Registry
- Remove entry from `EXTERNAL_CREW_REGISTRY.md` in your workspace
- Note in Operation History

### Step 6: Closeout
Report to the user:
- Instance removed successfully
- Source template still available for future instantiation
- Workspace archived location (for recovery if needed)
- Bindings removed (if any)
- Remind: restart Gateway to apply changes (`./scripts/dev.sh gateway`)

## Notes
- **External crew only**: Never remove `main`, `hrbp`, or `it-engineer` — these are internal crews not in your domain
- Removing an instance does NOT delete the template — template remains available in `~/.openclaw/hrbp_templates/` for future use
- Workspace is archived, not permanently deleted — user can recover it
- All steps that modify the system require explicit user confirmation
- If the user asks to "undo" a removal, the workspace can be restored from the archive
