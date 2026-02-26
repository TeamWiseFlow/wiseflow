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

## Development Workflow

### 远程仓库

- **origin** → `git@github.com:bigbrother666sh/wiseflow.git`（个人开发仓库）
- **upstream** → `git@github.com:TeamWiseFlow/wiseflow.git`（TeamWiseflow 正式发布仓库）

### 开发流程

1. 默认在 `master` 分支上开发，按需创建功能分支
2. 开发完成后推送到 **origin**（个人仓库���
3. 阶段性成果通过 GitHub PR 从 origin 合并到 **upstream**（TeamWiseflow 正式仓库）

### 本地归档分支

- **`4.x`** — 仅本地保留，归档 v4.30 及之前的代码

### 版本管理

版本号存储在 `version` 文件中，格式为 `vMAJOR.MINOR.PATCH`。当 PR 合并到 upstream 的 master 时，GitHub Action 自动递增版本号并创建 Release。通过 PR 标签控制递增类型：
- `major` 标签 → 大版本升级
- `minor` 标签 → 功能版本升级
- 无标签或 `patch` 标签 → 补丁版本升级（默认）

**不要手动修改 `version` 文件**，由 CI 自动维护。

## Permissions

Claude Code 被授权在本仓库中执行任何 git 命令（包括 push、branch、tag 等），无需逐次确认。
