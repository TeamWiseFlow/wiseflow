# Wiseflow Patches

wiseflow 针对原版 openclaw 提供的非侵入式补丁与插件，作为 wiseflow 的共性基础能力，由 `apply-addons.sh` 自动应用。

### 1. 代码补丁（*.patch）

对 OpenClaw 打的 git patch，按序号命名，顺序应用：

| 补丁 | 功能 |
|------|------|
| `001-suppress-stale-reply-context.patch` | 为 suppress-stale-reply 插件提供上下文支持，确保被抑制的回复仍写入对话历史 |
| `002-disable-web-search-env-var.patch` | 添加 `OPENCLAW_DISABLE_WEB_SEARCH` 环境变量，可按需禁用内置 web_search |
| `003-act-field-validation.patch` | 强化浏览器工具的 act 字段校验，防止幻觉动作 |
| `004-no-fallback-sticky.patch` | 添加 `OPENCLAW_NO_FALLBACK_STICKY=1` 环境变量，每轮始终从默认模型重试，避免 fallback 跨轮累积成本 |

> **注**：原 `004-web-fetch-allow-rfc2544.patch`（允许 web fetch 访问 RFC 2544 保留地址段，国内 Clash fake-IP 场景）已于 openclaw v2026.4.10 被上游原生集成为 `tools.web.fetch.ssrfPolicy.allowRfc2544BenchmarkRange` 配置项，patch 已移除，默认在 `config-templates/openclaw.json` 中开启。

### 2. 插件（suppress-stale-reply/）

| 插件目录 | 功能 |
|---------|------|
| `suppress-stale-reply/` | 用户连续快速发送多条消息时，agent 对被超越消息的回复不发送给用户（仍写入历史）；`/`-前缀指令型回复放行；可通过 `OPENCLAW_SUPPRESS_STALE_REPLY=0` 关闭 |

### 3. 依赖覆盖（overrides.sh）

`overrides.sh` 在 openclaw 恢复干净状态后最先执行，用于注入 pnpm 依赖覆盖（如 patchright 替换 playwright）。

### 辅助工具

- `generate-patch.sh`：从当前 openclaw 工作区生成 patch 文件的辅助脚本，在项目根目录运行。
