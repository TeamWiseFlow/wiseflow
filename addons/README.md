Place addon directories here to auto-load them via `scripts/apply-addons.sh`.

Each subdirectory is treated as one addon (identified by its `addon.json` manifest).
This directory's subdirectories are **git-ignored** — third-party addons are not tracked by this repo.

## Install an addon

```bash
git clone https://github.com/some-org/some-addon.git addons/some-addon
./scripts/apply-addons.sh
```

## Develop your own addon

See **[addon_development.md](../docs/addon_development.md)** for the full guide, including:

- Pinning to the correct OpenClaw version (`openclaw.version`)
- Addon directory structure and `addon.json` schema
- Four-layer loading mechanism (overrides → patches → skills → crew)
- Local dev & test workflow
- How to publish and get listed in the marketplace
