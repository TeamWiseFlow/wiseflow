# Wiseflow Patches

wiseflow 针对原版 openclaw 提供的非侵入式补丁与依赖覆盖，作为 wiseflow 的共性基础能力，由 `apply-addons.sh` 自动应用。

### 1. 代码补丁（*.patch）

对 OpenClaw 打的 git patch，按序号命名，顺序应用：

| 补丁 | 功能 |
|------|------|
| `002-disable-web-search-env-var.patch` | 添加 `OPENCLAW_DISABLE_WEB_SEARCH` 环境变量，可按需禁用内置 web_search |
| `003-act-field-validation.patch` | 强化浏览器工具的 act 字段校验，防止幻觉动作 |
| `005-browser-timeout-env-var.patch` | 添加 `OPENCLAW_BROWSER_TIMEOUT` 环境变量，支持自定义浏览器超时 |

> **注**：原 `001-suppress-stale-reply-context.patch` 已于 2026-04-25 移除，awada channel 改用 per-peer inbound debouncer 在入口层合并连发消息，无需 openclaw 核心补丁即可解决历史污染问题。

### 2. 依赖覆盖（overrides.sh）

`overrides.sh` 在 openclaw 恢复干净状态后最先执行，用于注入 pnpm 依赖覆盖（如 patchright 替换 playwright）。

### 辅助工具

- `generate-patch.sh`：从当前 openclaw 工作区生成 patch 文件的辅助脚本，在项目根目录运行。
