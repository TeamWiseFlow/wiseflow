# Bootstrap

This is a pre-configured crew workspace. Review these files at startup:

- **SOUL.md** — Role definition, core responsibilities, and autonomy level
- **AGENTS.md** — Workflows and operating procedures
- **MEMORY.md** — Background context and historical records
- **IDENTITY.md** — Name and persona
- **USER.md** — Assumptions about who you are serving
- **TOOLS.md** — Available tools, usage rules, and required environment variables

## First-Run Checklist

On first startup:
1. Check `SILICONFLOW_API_KEY` is set → required for PPT AI image generation
2. For investor email outreach: check SMTP env vars are set (`SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`)
3. Verify `sqlite3` is available: `which sqlite3`
4. Create output directories: `mkdir -p db output`
5. Initialize the investor database: `bash ./skills/ir-record/scripts/init-db.sh`

If SMTP is not configured, investor email contact mode is unavailable but all other modes work fully.
