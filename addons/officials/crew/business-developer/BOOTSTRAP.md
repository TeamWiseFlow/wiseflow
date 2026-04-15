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
1. Check `SILICONFLOW_API_KEY` is set → required for LLM content generation
2. For Cold Outreach: check SMTP env vars are set (`SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`)
3. Verify `send_email.py` dependency: `python3 -c "import smtplib; print('ok')"` (built-in, always ok)
4. Create output directories: `mkdir -p outreach_data`

If SMTP is not configured, affiliate marketing mode still works fully.
