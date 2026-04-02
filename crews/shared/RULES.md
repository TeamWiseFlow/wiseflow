# System Rules

## User's Role
Ideas, direction, taste, key questions, final validation. System does everything else.

## Autonomy Ladder
- L1 (trivial, reversible): Proceed directly
- L2 (non-trivial, reversible): Proceed, produce structured output
- L3 (irreversible): Must get user confirmation. No exceptions.

## Task Types (QAPS)
- Q: Direct answer, no closeout
- A: Deliverable → closeout mandatory
- P: Project → task card + checkpoints + closeout
- S: System change → needs review + closeout + rollback plan

## Closeout
Every A/P/S task ends with closeout (see TEMPLATES.md). Mark "值得沉淀" if insight is reusable.

## Routing

### Internal Crew Routing
- Default: Messages route through Main Agent, who dispatches via `sessions_spawn`
- Internal crews with `bindings` entries can also handle channel messages directly
- Same internal agent can serve both spawn + bind modes simultaneously
- Force route syntax: `[Route: @<agent-id>] <message>` or `@<agent-id> <message>`
  - Example: `[Route: @it-engineer] 帮我检查 gateway 日志`

### External Crew Routing
- **External Crews are BIND-ONLY** — they are never spawned by Main Agent
- External Crews handle messages directly via their bound channel
- Main Agent does not route to external crews; inform users to use the dedicated channel

### Crew Lifecycle Ownership
- **Internal Crew lifecycle**: recruit/modify/dismiss are Main Agent responsibilities
  (Main Agent uses crew-recruit / crew-dismiss skills)
- **External Crew lifecycle**: recruit/modify/dismiss/upgrade are HRBP-only
  (HRBP uses hrbp-recruit / hrbp-modify / hrbp-remove / hrbp-upgrade skills)
- Internal crews (main/hrbp/it-engineer) are protected — neither Main Agent nor HRBP can delete them

## Inter-Agent Communication
- Spawn preferred for internal crews (parallel, isolated)
- Sub-agent results announce back to spawner
- Requesting agent syncs results to its own channel

## Crew Upgrades
- **Internal Crew**: upgrades initiated by the managing agent or human user.
  Record what changed, why, how to rollback. S-class changes need user review.
- **External Crew**: upgrades are managed exclusively by HRBP.

## Crew Types
See `CREW_TYPES.md` for the authoritative definition of internal vs external crews.
