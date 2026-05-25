# Media Operator Bootstrap

This one-time bootstrap collects the operating context before content work starts. If this crew is being enabled through Main Agent and has no direct work channel yet, Main Agent may ask these questions on behalf of this crew and write the answers into the crew workspace.

## Step 1: Platform Scope

Ask which platforms the user wants to operate:

- WeChat Official Account
- WeCom Moments
- Xiaohongshu
- Douyin
- Kuaishou
- Bilibili
- YouTube
- TikTok
- Instagram
- Facebook
- Threads
- Pinterest
- Other platforms

Clarify:

- first-launch platforms;
- later/backlog platforms;
- draft-only vs automatic publishing;
- whether human approval is required before publishing.

## Step 2: WeChat / WeCom Publishing Readiness

If the user chooses WeChat Official Account or WeCom Moments, remind them:

> These publishing APIs commonly require an IP allowlist. If this machine has no fixed public IP, use a relay/transit mode before enabling automatic publishing.

Ask:

- Does this machine have a fixed public IP?
- Is the platform IP allowlist already configured?
- Do they need relay/transit mode?
- Should this crew only generate drafts until publishing credentials are ready?

## Step 3: Brand and Business Context

Collect:

- brand/company name;
- product/service introduction;
- target audience;
- key selling points;
- brand tone;
- forbidden claims or sensitive topics;
- competitors or differentiation;
- common CTA;
- source material locations;
- approval owner and workflow.

## Step 4: Content Operating Rhythm

Ask:

- publishing frequency by platform;
- daily/weekly topic planning cadence;
- whether heartbeat should generate topics, drafts, or status reports;
- failure handling preference: notify immediately or summarize later.

## Completion

After bootstrap is complete:

1. Update `MEMORY.md` with platform strategy, brand context, and constraints.
2. Update `USER.md` with approval preferences and service recipient information.
3. Update `TOOLS.md` with publishing environment notes, but never write secrets into Markdown.
4. Update `HEARTBEAT.md` only if the user wants periodic tasks.
5. Delete `BOOTSTRAP.md` from the runtime workspace.
6. Suggest the next step, such as creating the first WeChat Official Account draft.
