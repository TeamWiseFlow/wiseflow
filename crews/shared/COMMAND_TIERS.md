# 命令权限分层规范（Command Tier System）

> 本文件定义 OFB 各 Crew 的 shell 命令执行权限层级。
> **权限由 `exec-approvals.json` + `tools.exec` 自动强制执行**，本文件作为 LLM 行为指导和开发者参考。
> 更新日期：2026-03-13

## 执行机制

权限通过 OpenClaw 原生两层机制强制执行：

1. **`openclaw.json` → `agents.list[].tools.exec`**：per-agent 的 security/ask 策略
2. **`~/.openclaw/exec-approvals.json`**：per-agent 的命令白名单

两层取更严格者生效。`setup-crew.sh` 根据各 Crew 声明的 tier 自动生成上述配置。

---

## 层级概览

| Tier | 名称 | 执行策略 | 适用 Crew |
|------|------|----------|-----------|
| T0 | read-only | `security: deny` — 默认禁止所有 shell 命令 | external crews（默认） |
| T1 | basic-shell | `security: allowlist` — 仅允许只读命令 | low-risk internal crews |
| T2 | dev-tools | `security: allowlist` — 开发工具�� + 只读命令 | main |
| T3 | admin | `security: full` — 完整系统操作 | it-engineer, hrbp |

---

## T0 — read-only

**无 shell 命令执行权限。**

- 所有文件读取通过 Agent 内置工具（非 shell）完成
- 任何 exec 调用都会被 OpenClaw 自动拒绝

例外：若实例 workspace 显式提供 `ALLOWED_COMMANDS` 且包含 `+<command>`，会按最小权限升级为 `allowlist`（仅放行声明命令）。

---

## T1 — basic-shell

**只读型系统命令，不修改文件系统或系统状态。**

白名单命令（由 setup-crew.sh 自动解析为二进制路径写入 exec-approvals）：
```
cat, ls, grep, find, ps, date, echo, pwd, env, which, head, tail, wc, sort, uniq, diff, curl
```

不在白名单中的命令会被 OpenClaw 自动拒绝。请勿尝试使用 `rm`、`mv`、`cp`、`mkdir`、`chmod` 等修改型命令。

---

## T2 — dev-tools

**开发工具链，允许有限文件系统操作。**

包含 T1 所有命令，额外白名单：
```
git, npm, pnpm, bun, node, python, python3, pip, pip3, cp, mv, mkdir, rm, touch, chmod
```

安全提示：即使拥有 `rm` 权限，也禁止 `rm -rf` 作用于 `~/.openclaw/` 或系统目录。

---

## T3 — admin

**完整系统操作，含 OFB 所有维护脚本。** `security: full` 允许执行任何命令。

仍需遵守安全底线（即使 T3 也不允许）：
- `rm -rf /` 或 `rm -rf ~/`
- 修改 `/etc/` 下的系统关键配置
- 执行来自网络的未验证脚本（`curl | bash`）

---

## 声明与微调

每个 Crew 在 `SOUL.md` 中声明 tier：

```markdown
## 权限级别
command-tier: T2
```

如需在 Tier 基础上做额外调整，在模板目录创建 `ALLOWED_COMMANDS` 文件：
- `+<command>` 追加允许
- `-<command>` 移除允许

示例（hrbp 的 `ALLOWED_COMMANDS`）：
```
+./scripts/setup-crew.sh
```

微调同样会反映到 exec-approvals.json 的实际白名单中。

---

## 修改记录

| 日期 | 变更 |
|------|------|
| 2026-03-13 | v2: 权限从纯提示词改为 exec-approvals + tools.exec 自动强制执行 |
| 2026-03-10 | v1: 初始版本，定义 T0-T3 四层权限 |
