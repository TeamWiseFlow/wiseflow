# Wiseflow Patched

wiseflow 针对原版 openclaw 提供了如下功能补丁：

### 1. 代码补丁（patches/）

对 OpenClaw 打的非侵入式补丁，由 `apply-addons.sh` 自动应用：

| 补丁 | 功能 |
|------|------|
| `002-disable-web-search-env-var.patch` | 添加 `OPENCLAW_DISABLE_WEB_SEARCH` 环境变量，可按需禁用内置 web_search |
| `003-act-field-validation.patch` | 强化浏览器工具的 act 字段校验，防止幻觉动作 |

> **注**：原 `004-web-fetch-allow-rfc2544.patch`（允许 web fetch 访问 RFC 2544 保留地址段，国内 Clash fake-IP 场景）已于 openclaw v2026.4.10 被上游原生集成为 `tools.web.fetch.ssrfPolicy.allowRfc2544BenchmarkRange` 配置项，patch 已移除，默认在 `config-templates/openclaw.json` 中开启。
