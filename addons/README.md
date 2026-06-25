Place addon directories here to auto-load them via `scripts/apply-addons.sh`.

Each subdirectory is treated as one addon (identified by its `addon.json` manifest).
This directory's subdirectories are **git-ignored** — third-party addons are not tracked by this repo.

## Addon vs. Base wiseflow

wiseflow 采用两级扩展机制：

- **Base wiseflow**（`patches/` + `skills/`）：每次 `apply-addons.sh` 运行时无条件应用，对所有 addon 和 crew 生效。包括代码补丁（`patches/*.patch`）、插件（`patches/suppress-stale-reply`）和默认全局技能（`skills/`）。
- **Addon**（`addons/*/`）：在 base 之上叠加，提供额外全局技能（`skills/`）和 Crew 模板（`crew/`）。

> **注意**：addon 不包含 patches 层。如需对 openclaw 打补丁，请将 patch 放到项目根目录的 `patches/` 下，而非 addon 内部。

## Install an addon

```bash
git clone https://github.com/some-org/some-addon.git addons/some-addon
./scripts/apply-addons.sh
```

## Develop your own addon

See **[addon_development.md](../docs/addon_development.md)** for the full guide, including:

- Pinning to the correct OpenClaw version (`openclaw.version`)
- Addon directory structure and `addon.json` schema
- Two-layer loading mechanism (skills → crew)
- Local dev & test workflow
- How to publish and get listed in the marketplace
