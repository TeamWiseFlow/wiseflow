# IR Bootstrap

This one-time bootstrap collects the business and financing context before IR work starts. If this crew is being enabled through Main Agent and has no direct work channel yet, Main Agent may ask these questions on behalf of this crew and write the answers into the crew workspace.

## Step 1: Company & Financing Context

Collect (skip items the user already has clear answers for):

1. **Company basics**: company name, one-line positioning, core product/service
2. **Financing status**: current round, target amount, existing progress
3. **Material status**: does the user already have a BP/PPT? Need to create new or update existing?
4. **Style preferences**: any reference templates or benchmark cases for investor materials?

## Step 2: Investor Outreach Readiness

Ask:

- Is SMTP configured for investor email outreach? If not, explain that email contact mode will be unavailable until SMTP is set up.
- Does the user want to start with just商业模式打磨 (no outreach yet), or jump straight to investor search?

## Step 3: Environment Verification

On first startup, check and report:

1. `SILICONFLOW_API_KEY` is set → required for PPT AI image generation
2. For investor email outreach: check SMTP env vars (`SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`)
3. Verify `sqlite3` is available: `which sqlite3`
4. Create output directories: `mkdir -p db output`
5. Initialize the investor database: `./skills/ir-record/scripts/init-db.sh`

If SMTP is not configured, investor email contact mode is unavailable but all other modes work fully.

## Completion

After bootstrap is complete:

1. Update `MEMORY.md` with company/financing background and SMTP status.
2. Update `USER.md` with organization info (replace `<待填充>` placeholder).
3. Delete `BOOTSTRAP.md` from the runtime workspace.
4. Suggest the next step, such as starting a商业模式梳理 session or setting up investor search criteria.
