# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wiseflow v5.x is an **OpenClaw_for_business add-on** that enhances browser automation with anti-detection capabilities for [openclaw](https://github.com/openclaw/openclaw). It replaces Playwright with Patchright (undetected fork) and adds tab recovery, agent skills, and anti-bot strategies. In future, it may add some extension/plugin to openclaw.

The distributable unit is the `wiseflow/` directory, which would be applied to OpenClaw by a script developed by another team: https://github.com/bigbrother666sh/openclaw_for_business/blob/main/scripts/apply-addons.sh.

we must keep working with both the latest openclaw project and openclaw_for_business project.

**OpenClaw_for_business is also called "OFB" for short.**

## OpenClaw_for_business Add-on Architecture

### Three-Layer Add-on Loading

OpenClaw_for_business's `apply-addons.sh` processes our add-ons in this order:

1. **`overrides.sh`** — pnpm overrides that swap `playwright-core` → `patchright-core` at the package manager level. Controlled by `PATCHRIGHT_VERSION` env var (default: 1.57.0). Also patches documentation references.

2. **`patches/*.patch`** — Git patches applied to OpenClaw source. Currently `001-browser-tab-recovery.patch` adds snapshot-based tab recovery when the target tab disappears mid-session.

**must use scripts/generate-patch.sh to generate the final patch file**

3. **`skills/*/SKILL.md`** — Agent skill definitions installed into OpenClaw's skill system. `browser-guide/SKILL.md` teaches the agent login wall handling, CAPTCHA strategies, lazy-load scrolling, paywall detection, and tab cleanup.

### Key Files

| Path | Purpose |
|------|---------|
| `wiseflow/addon.json` | Package manifest (name, version, openclaw dependency) |
| `wiseflow/overrides.sh` | pnpm override script, receives `$ADDON_DIR` and `$OPENCLAW_DIR` |
| `wiseflow/patches/001-browser-tab-recovery.patch` | Tab resilience patch for browser tool |
| `wiseflow/skills/browser-guide/SKILL.md` | Agent browser best practices |
| `tests/run-managed-tests.mjs` | Automated test suite (Node.js ESM) |
| `docs/anti-detection-research.md` | Technical analysis of detection mechanisms |
| `version` | Current version string (v5.0) |

### Deployment Model

```
openclaw_for_business/
  addons/
    wiseflow/          ← copy of wiseflow/ directory
      addon.json
      overrides.sh
      patches/
      skills/
```

Install: copy `wiseflow/` → `<openclaw>/addons/wiseflow`, then restart OpenClaw.

## Development Workflow

### 远程仓库

- **origin** → `git@github.com:bigbrother666sh/wiseflow.git`（个人开发仓库）
- **upstream** → `git@github.com:TeamWiseFlow/wiseflow.git`（TeamWiseflow 正式发布仓库）

### 开发流程与注意事项

1. 默认在 `master` 分支上开发，按需创建功能分支
2. 本项目是基于 openclaw 进行 patch，同时必须遵循 openclaw_for_business(OFB)的 add-on 加载机制。因此你应该保证在 tests/ 下面始终克隆一份来自 https://github.com/openclaw/openclaw 的代码，同时克隆一份 https://github.com/bigbrother666sh/openclaw_for_business/blob/main/scripts/apply-addons.sh 
每次开发前都应该进行一次拉取，然后基于最新的 openclaw 代码进行开发，并保证最后的产出适配 apply-addons.sh
3. 遵循 tdd（测试驱动开发）流程，每次开发之后必须进行完整测试
4. 本项目建立在其他一些开源项目基础上，比如[patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright), 随着项目发展，你需要记录一份我们的依赖清单，对于每一个你都可以 clone 一份代码到项目根目录下，以便随时查看我们是否有必要跟着升级，但记得同步更新 .gitignore 文件, 避免混入提交，同时 tests/ 下的openclaw_for_business 代码仓也永远不要提交
5. 开发完成后推送到 **origin**（个人仓库)
6. 阶段性成果通过 GitHub PR 从 origin 合并到 **upstream**（TeamWiseflow 正式仓库）
7. **upstream**（TeamWiseflow 正式仓库）每次合并 PR 后自动更新版本号并触发 release 打包发布

注：有时我会通过在 .claude/ 中留下 TODO.md 的方式下发开发任务，这些任务你完成后需要把 TODO.md 改名为 {date}_done.md

### 版本管理

版本号存储在 `version` 文件中，格式为 `vMAJOR.MINOR.PATCH`。当 PR 合并到 upstream 的 master 时，GitHub Action 自动递增版本号并创建 Release。通过 PR 标签控制递增类型：
- `major` 标签 → 大版本升级
- `minor` 标签 → 功能版本升级
- 无标签或 `patch` 标签 → 补丁版本升级（默认）

**不要手动修改 `version` 文件**，由 CI 自动维护。

## Permissions

Claude Code 被授权在本仓库中执行任何 git 命令（包括 push、branch、tag 等），无需逐次确认。
