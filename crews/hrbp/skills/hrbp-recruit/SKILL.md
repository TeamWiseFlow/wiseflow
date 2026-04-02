# HRBP Skill — Recruit (招聘 / 实例化)

## Trigger
User requests a new external agent/role/assistant.

> Scope: **external crews only**. Internal crew lifecycle is managed by Main Agent.

## Procedure

### Step 1: Understand Requirements (L1)
- Ask the user about the new agent's purpose, specialty, and responsibilities
- Ask if the new agent needs a direct channel binding (Mode B; external crews are bind-only)
- Clarify the instance's name and desired ID (lowercase, hyphenated, e.g., `cs-product-a`)

### Step 2: Match Template (L1)
- Browse template library: `~/.openclaw/hrbp_templates/index.md`
- If a matching template exists → use it as the base, proceed to Step 3
- If no match → create a new template first:
  1. Use `~/.openclaw/hrbp_templates/_template/` as scaffold (or closest existing template)
  2. Generate 8 workspace files for the new template
  3. Write to `~/.openclaw/hrbp_templates/<template-id>/`
  4. Update `~/.openclaw/hrbp_templates/index.md`
  5. Then proceed to Step 3

### Step 3: Configure Instance (L1)
Present an instantiation proposal to the user:
- **Instance ID**: unique, lowercase, hyphenated (e.g., `cs-product-a`)
- **Instance Name**: human-readable (e.g., "产品A客服")
- **Source Template**: which template this instance is based on
- **Channel Binding**: optional — which channel and account
- **Skill Customization**: optional — additional or denied skills
- **Role Tuning**: optional — SOUL.md adjustments for this specific instance

### Step 4: Generate Workspace (L2)
After user confirms the proposal:

1. Create workspace directory: `~/.openclaw/workspace-<instance-id>/`
2. Copy template files as starting point
3. Apply instance-specific customizations (name, role tuning, etc.)
4. Create optional skill config file:
   - `BUILTIN_SKILLS` — one bundled skill per line（表示”在 wiseflow 基线技能之外追加”）
5. Copy shared protocols (`RULES.md`, `TEMPLATES.md`) into the workspace
6. **[If template uses `customer-db` skill]** Initialize the customer database:
   - Ask the user to define the database schema (tables, fields, types)
   - Write the schema to `~/.openclaw/workspace-<instance-id>/db/schema.sql`
   - Run the initialization script from the workspace directory:
     ```
     cd ~/.openclaw/workspace-<instance-id>
     bash ./skills/customer-db/scripts/db.sh init
     ```
   - Confirm tables were created successfully:
     ```
     bash ./skills/customer-db/scripts/db.sh tables
     ```
   - Record the schema summary in the instance's `MEMORY.md` under a `## Database Schema` section

   **Schema example** (adapt to the user's business needs):
   ```sql
   -- db/schema.sql
   CREATE TABLE IF NOT EXISTS customers (
     id          INTEGER PRIMARY KEY AUTOINCREMENT,
     channel_id  TEXT NOT NULL UNIQUE,   -- 渠道用户标识（如飞书 open_id）
     name        TEXT,
     phone       TEXT,
     status      TEXT DEFAULT 'active',  -- active / vip / blocked
     created_at  TEXT DEFAULT (date('now')),
     last_seen   TEXT DEFAULT (date('now'))
   );
   ```

   **Schema design guidelines**:
   - Always include a `channel_id` column to link records to the user's channel identity
   - Use `TEXT DEFAULT (date('now'))` for date fields (SQLite has no native DATE type)
   - Avoid storing PII beyond what's operationally necessary
   - Keep schema simple — the agent performs DML only; complex joins should be avoided

### Step 5: Register Instance (L3 — requires user confirmation)
1. Run:
   - `bash ./skills/hrbp-recruit/scripts/add-agent.sh <instance-id> --crew-type external`
   - Optional bind: `--bind <channel>:<accountId>`
   - Optional bundled skills add-on: `--builtin-skills <skill1,skill2|all>`
   - Optional template metadata: `--template-id <template-id> --note <text>`
2. This will:
   - Add instance to `agents.list` in openclaw.json
   - Keep Main Agent `subagents.allowAgents` untouched（external bind-only）
   - Add binding if specified
   - Write `skills` allowlist from `DECLARED_SKILLS` + workspace skills only（declare-mode）
   - Enforce external constraints: create `feedback/` directory
   - Update HRBP Agent's MEMORY.md（Instance Registry + Operation History）

### Step 6: Update HRBP Memory
- No manual text edit required if Step 5 script succeeded.
- Only verify HRBP MEMORY has registry/history entry; if missing, rerun add-agent.sh with:
  - `--template-id <template-id>`
  - `--note <text>`

### Step 7: Closeout
Report to the user:
- Instance ID and name
- Source template
- Workspace location
- Route mode: binding（外部 crew 仅支持 bind-only，无 spawn 模式）
- Remind: restart Gateway to activate (`./scripts/dev.sh gateway`)

## Notes
- Always present the proposal before generating files
- Use existing templates when possible — avoid creating unnecessary new templates
- Instance IDs must be unique, lowercase, hyphenated
- The workspace directory must exist before running add-agent.sh
- Same template can be instantiated multiple times with different IDs
