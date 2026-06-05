# BusinessDeveloper Bootstrap

This one-time bootstrap collects the business context before BD work starts. If this crew is being enabled through Main Agent and has no direct work channel yet, Main Agent may ask these questions on behalf of this crew and write the answers into the crew workspace.

## Step 1: Company & Business Context

Collect:

- company/brand name;
- product or service introduction (one-line positioning);
- target customer profile;
- key selling points / differentiators;
- brand tone for outreach communications;
- forbidden claims or sensitive topics to avoid;
- competitors or differentiation notes.

## Step 2: Outreach Readiness

Ask:

- Is SMTP configured for cold email outreach? If not, explain that email outreach mode will be unavailable until SMTP is set up.
- Should the crew start in draft-only mode (collect leads but not contact them) or is direct outreach approved?
- For direct outreach: does the user have existing outreach templates/talking points, or should the crew draft them for review?

## Step 3: Environment Verification

On first startup, check and report:

1. `SILICONFLOW_API_KEY` is set → required for LLM content generation
2. For Cold Outreach: check SMTP env vars (`SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`)
3. Verify `send_email.py` dependency: `python3 -c "import smtplib; print('ok')"` (built-in, always ok)
4. Create output directories: `mkdir -p outreach_data`

If SMTP is not configured, affiliate marketing mode still works fully.

## Completion

After bootstrap is complete:

1. Update `MEMORY.md` with company/business background and SMTP status.
2. Update `USER.md` with organization info (replace `<待填充>` placeholder).
3. Delete `BOOTSTRAP.md` from the runtime workspace.
4. Suggest the next step, such as setting up the first Lead Hunting task.
