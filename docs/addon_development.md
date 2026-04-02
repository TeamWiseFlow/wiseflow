# Addon Development Guide

This guide explains how to develop addons for **OpenClaw for Business (OFB)**.

An addon is an independent Git repository installed to the `addons/` directory. It can extend OFB in up to four ways, applied in this order by `scripts/apply-addons.sh`:

1. **`overrides.sh`** — pnpm dependency overrides (most stable, no line-number coupling)
2. **`patches/*.patch`** — git patches for precise source changes (may need updating after upstream upgrades)
3. **`skills/`** — global skills visible to all agents
4. **`crew/`** — Crew templates installed to `crews/` and managed by HRBP

---

## Addon Directory Layout

```
<addon-name>/
├── addon.json              # Required: addon metadata
├── overrides.sh            # Optional: dependency replacement script
├── patches/
│   └── *.patch             # Optional: git patches against openclaw/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md        # Skill definition (required)
│       └── scripts/        # Supporting scripts (optional)
└── crew/
    └── <template-id>/
        ├── SOUL.md         # Required — role definition (must declare command-tier)
        ├── AGENTS.md       # Workflows and procedures
        ├── MEMORY.md       # Initial memory / background context
        ├── USER.md         # Assumptions about the user
        ├── IDENTITY.md     # Name and persona
        ├── TOOLS.md        # Tool guidance
        ├── HEARTBEAT.md    # Health-check template
        ├── BOOTSTRAP.md    # Onboarding intro (shown on first boot only)
        ├── DENIED_SKILLS   # Optional: built-in skills to block
        └── skills/
            └── <skill-name>/   # Template-scoped skills (only this crew sees them)
                └── SKILL.md
```

---

## `addon.json` Format

```jsonc
{
  "name": "my-addon",
  "version": "1.0.0",
  "description": "What this addon does",
  "internal_crews": ["my-ops-bot"],       // crew templates that are internal (managed by Main Agent)
  "external_crews": ["my-customer-bot"],  // crew templates that are external (managed by HRBP)
  "auto-activate": false                  // set true to auto-instantiate crew templates on apply
}
```

### Crew Type Declaration

The `internal_crews` and `external_crews` arrays in `addon.json` are the **sole authority** for crew-type assignment:

- Templates listed in `internal_crews` → **internal** (inherits all global skills, Main Agent manages lifecycle)
- Templates listed in `external_crews` → **external** (uses DECLARED_SKILLS only, HRBP manages lifecycle)
- Templates in neither array → defaults to **external** with a warning
- A template listed in **both** arrays → error, `apply-addons.sh` will abort

The `crew-type:` field in `SOUL.md` is **not required** for addon templates. If present, it will be overwritten by `apply-addons.sh` to match the `addon.json` declaration.

---

## Layer 1 — `overrides.sh`

Receives two environment variables: `ADDON_DIR` and `OPENCLAW_DIR`.
Use it to inject pnpm overrides or replace packages before the build:

```bash
#!/bin/bash
# Example: replace a transitive dependency
cd "$OPENCLAW_DIR"
node -e "
  const pkg = JSON.parse(require('fs').readFileSync('package.json','utf8'));
  if (!pkg.pnpm) pkg.pnpm = {};
  if (!pkg.pnpm.overrides) pkg.pnpm.overrides = {};
  pkg.pnpm.overrides['some-package'] = '^2.0.0';
  require('fs').writeFileSync('package.json', JSON.stringify(pkg, null, 2));
"
```

---

## Layer 2 — `patches/*.patch`

Generate with `git diff` or `git format-patch` against the upstream `openclaw/` source.
Patches are applied with `--3way --ignore-whitespace --whitespace=fix`.

> **Warning:** Patches are fragile across upstream upgrades. Prefer `overrides.sh` for dependency changes.

---

## Layer 3 — Global Skills (`skills/`)

Skills placed here are installed to `openclaw/skills/` and made available to all agents.
Each skill requires a `SKILL.md` file at the skill root.

Global skills are listed in `~/.openclaw/GLOBAL_SHARED_SKILLS` after `apply-addons.sh` runs.

---

## Layer 4 — Crew Templates (`crew/`)

### Required: Declare a Command Tier

Every crew template **must** declare a command tier in its `SOUL.md`. `setup-crew.sh` reads this declaration and automatically generates:
1. `agents.list[].tools.exec` in `openclaw.json` (per-agent security/ask policy)
2. `~/.openclaw/exec-approvals.json` entries (per-agent command allowlists with resolved binary paths)

Add this section to `SOUL.md` (before or after `## Communication Style`):

```markdown
## 权限级别
command-tier: T1
```

**The four tiers** (see `crews/shared/COMMAND_TIERS.md` for the full command lists):

| Tier | Name | Exec Policy | Typical Crew Type |
|------|------|-------------|-------------------|
| `T0` | read-only | `security: deny` — no shell execution | Customer service, content creation, research |
| `T1` | basic-shell | `security: allowlist` — read-only commands: `cat`, `ls`, `grep`, `ps`, `curl` (GET only), … | Coordination, operations |
| `T2` | dev-tools | `security: allowlist` — T1 + `git`, `npm`, `pnpm`, `node`, `python`, `cp`, `mv`, `mkdir`, `rm`, … | Development, automation |
| `T3` | admin | `security: full` — unrestricted shell access | Infrastructure, sysops |

Choose the **minimum tier** that the role genuinely needs. When in doubt, go lower — HRBP or the user can grant additional permissions after deployment.

### Fine-Grained Adjustments with `ALLOWED_COMMANDS`

To add or remove commands relative to the base tier, create an `ALLOWED_COMMANDS` file in the template directory:

```
# Prefix + to allow, - to deny
+./scripts/setup-crew.sh
-rm
```

These adjustments are applied on top of the tier's base allowlist and reflected in `exec-approvals.json` automatically.

### Skills Behavior by Crew Type

**Internal crews** (`internal_crews`):
- Inherit **all global skills** — every skill installed in `openclaw/skills/` (both built-in and addon-provided) is visible by default
- Use `DENIED_SKILLS` to exclude specific skills that the crew should not access
- `BUILTIN_SKILLS` file is still supported for backward compatibility but rarely needed since the default is already "all"

**External crews** (`external_crews`):
- Use **declaration mode** — only skills explicitly listed in `DECLARED_SKILLS` are visible
- `DECLARED_SKILLS` can reference both global skills (from `openclaw/skills/`) and template-scoped skills (from `crew/<template>/skills/`)
- Template-scoped skills are automatically appended (no need to list them in `DECLARED_SKILLS`)
- `self-improving` skill is always blocked for external crews

### Instantiation Behavior

By default, installed templates are **not auto-instantiated** — they become available in the HRBP/Main Agent template library and the user can instantiate them on demand.

To auto-instantiate on `apply-addons.sh`, set `"auto-activate": true` in `addon.json`. This creates `workspace-<template-id>` and registers the agent immediately. Use with caution: the instance ID will equal the template ID, and existing workspaces will be skipped (not overwritten).

### `DENIED_SKILLS` (internal crews only)

If your internal crew template should not have access to certain skills, list them one per line in `DENIED_SKILLS`:

```
github
gh-issues
coding-agent
```

### `DECLARED_SKILLS` (external crews only)

External crew templates must declare which skills they need in `DECLARED_SKILLS`:

```
customer-db
smart-search
rss-reader
```

---

## Testing Your Addon Locally

1. Clone your addon into `addons/<addon-name>/`
2. Run `./scripts/apply-addons.sh` — it is fully idempotent
3. Restart the gateway: `./scripts/dev.sh gateway`
4. For crew templates: ask HRBP to instantiate the new template

To force re-apply (e.g., after updating a crew template that already exists in `crews/`):

```bash
./scripts/apply-addons.sh --force
```

---

## Upgrade Compatibility

When the upstream `openclaw` version changes:

- **`overrides.sh`** — usually unaffected (package-level override)
- **`patches/*.patch`** — re-generate against the new upstream commit if they fail to apply
- **`skills/`** — rarely affected unless openclaw's skill API changes
- **`crew/` templates** — update if `SOUL.md` references upstream-specific behaviors that changed

Check `openclaw.version` for the pinned upstream commit. When submitting your addon to the community, document which OFB version range it supports.
