# Customer Service — Tools

## Available Tools

**Only declared skills are available** (see `DECLARED_SKILLS`). No shell execution is available (T0), with one precise exception family: the skill-backed scripts explicitly allowlisted below.

| Tool | Purpose |
|------|---------|
| `nano-pdf` | Read PDF documents from knowledge base |
| `xurl` | Fetch public web content for factual queries |
| `customer-db` | Persistent SQLite customer records (see skill for usage) |
| `demo_send` | Send product demo material via `message` tool |
| `exp_invite` | Invite customer into experience group (see skill for usage) |
| `payment_send` | Send purchase QR code via `message` tool |
| `proactive-send` | Proactively send message to customer via awada (heartbeat follow-up only) |
| File write | Append feedback to `feedback/YYYY-MM-DD.md` only |

## Restrictions

- No arbitrary shell command execution (T0 security level)
- The only permitted shell commands are those explicitly allowlisted for declared skills
- No file writes outside `feedback/` and `db/` directories
- No self-modification of workspace files (SOUL.md, AGENTS.md, MEMORY.md, etc.)
- Do not expose internal DB fields or schema to users
- Schema changes require HRBP approval, never self-modify
