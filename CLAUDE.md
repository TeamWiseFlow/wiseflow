# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wiseflow v5.x is an **OpenClaw add-on** that enhances browser automation with anti-detection capabilities. It replaces Playwright with Patchright (undetected fork) and adds tab recovery, agent skills, and anti-bot strategies. The distributable unit is the `addon/` directory, which gets copied into an OpenClaw installation.

Requires: OpenClaw >= 2026.2

## Architecture

### Three-Layer Add-on Loading

OpenClaw's `apply-addons.sh` processes add-ons in this order:

1. **`overrides.sh`** — pnpm overrides that swap `playwright-core` → `patchright-core` at the package manager level. Controlled by `PATCHRIGHT_VERSION` env var (default: 1.57.0). Also patches documentation references.

2. **`patches/*.patch`** — Git patches applied to OpenClaw source. Currently `001-browser-tab-recovery.patch` adds snapshot-based tab recovery when the target tab disappears mid-session.

3. **`skills/*/SKILL.md`** — Agent skill definitions installed into OpenClaw's skill system. `browser-guide/SKILL.md` teaches the agent login wall handling, CAPTCHA strategies, lazy-load scrolling, paywall detection, and tab cleanup.

### Key Files

| Path | Purpose |
|------|---------|
| `addon/addon.json` | Package manifest (name, version, openclaw dependency) |
| `addon/overrides.sh` | pnpm override script, receives `$ADDON_DIR` and `$OPENCLAW_DIR` |
| `addon/patches/001-browser-tab-recovery.patch` | Tab resilience patch for browser tool |
| `addon/skills/browser-guide/SKILL.md` | Agent browser best practices |
| `tests/run-managed-tests.mjs` | Automated test suite (Node.js ESM) |
| `patchright/` | Browser anti-detection patches (gitignored, built separately) |
| `reference/` | Archived v4.x code (search engines, RSS parser, GitHub search) |
| `docs/anti-detection-research.md` | Technical analysis of detection mechanisms |
| `version` | Current version string (v5.0) |

### Deployment Model

```
openclaw_for_business/
  addons/
    wiseflow/          ← copy of addon/ directory
      addon.json
      overrides.sh
      patches/
      skills/
```

Install: copy `addon/` → `<openclaw>/addons/wiseflow`, then restart OpenClaw.
