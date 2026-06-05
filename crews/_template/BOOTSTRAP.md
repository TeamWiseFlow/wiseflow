# Bootstrap

This one-time bootstrap collects the operating context the crew needs before work starts. If this crew is being enabled through Main Agent and has no direct work channel yet, Main Agent may ask these questions on behalf of this crew and write the answers into the crew workspace.

## When to Include Bootstrap Steps

Add bootstrap collection steps when the crew needs **user-specific context** that cannot be derived from the system or environment — for example:

- Company/brand/business background
- Platform choices and publishing strategy
- Product/service handbook details
- User preferences (language, style, frequency)
- Operational links and escalation contacts

**Do NOT add bootstrap steps** when the crew only needs system-level knowledge (paths, tool locations, architecture) — that belongs in `MEMORY.md` or `TOOLS.md` directly.

## Pattern

Structure the bootstrap as numbered steps, each collecting a coherent category of information:

```
## Step 1: <Category Name>

Collect:
- item 1;
- item 2;
- ...

## Step N: Environment Verification

On first startup, check and report:
1. Required env vars / dependencies
2. Create output directories
```

## Completion

Every bootstrap must end with a Completion section that:

1. Updates `MEMORY.md` with collected context (replacing placeholders).
2. Updates `USER.md` with relevant user/organization info.
3. Deletes `BOOTSTRAP.md` from the runtime workspace.
4. Suggests a concrete next step.

## Minimal Bootstrap (No Collection Needed)

If a crew does not need to collect user-specific info, **omit BOOTSTRAP.md entirely**. Do not keep a placeholder file — its absence signals that no bootstrap is needed.

---

## Review Files at Startup

Regardless of whether bootstrap steps exist, review these files at startup:

- **SOUL.md** — Role definition, core responsibilities, and autonomy level
- **AGENTS.md** — Workflows and operating procedures
- **MEMORY.md** — Background context and ongoing task state
- **IDENTITY.md** — Name and persona
- **USER.md** — Assumptions about who you are serving
- **TOOLS.md** — Available tools and usage guidelines
