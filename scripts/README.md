# scripts/ 脚本说明

## 脚本总览

| 脚本 | 用途 | 拉取代码 | apply addons | pnpm build | 安装 daemon | 重启 gateway |
|------|------|:---:|:---:|:---:|:---:|:---:|
| `install.sh` | 新安装 / 升级 | ✅ | ✅ | ✅ | ✅ | ✅ |
| `apply-addons.sh` | 本地测试改动 | — | ✅ | ✅ | — | ✅ |
| `dev.sh` | 开发模式（前台） | — | ✅ | — | — | — |
| `setup-crew.sh` | 仅同步 crew markdown | — | — | — | — | — |

---

## install.sh

**一键安装 / 升级**。新用户首次部署和老用户升级都用这一个脚本。

```bash
./scripts/install.sh              # 标准安装/升级
./scripts/install.sh --skip-crew  # 跳过 crew workspace 同步
./scripts/install.sh --force      # 强制覆盖已有 workspace 文件（含 MEMORY.md）
```

执行流程：
1. git fetch + reset（拉取最新 wiseflow 代码）
2. checkout openclaw 到 `openclaw.version` 锚定的版本
3. `pnpm install`（安装/更新依赖）
4. `apply-addons.sh --no-build --no-restart`（应用 patches + skills + crew 模板）
5. `pnpm build` + `pnpm ui:build`（编译 dist + Control UI）
6. 写入 `daemon.env`（收集 openclaw.json 引用的环境变量）
7. `daemon uninstall` + `daemon install`（重装 systemd service）
8. systemd drop-in + restart（注入 daemon.env 并重启 gateway）

> ⚠️ 升级前请确保系统空闲（无 agent 会话正在处理任务）。

---

## apply-addons.sh

**应用 addon 改动后一步到位**。用于新增/修改了 patch、skill 或 crew 模板后的本地测试。不拉取远程代码，不升级 openclaw 版本——直接用本地已有的源码。

```bash
./scripts/apply-addons.sh              # 应用 addons + build + restart gateway
./scripts/apply-addons.sh --skip-crew  # 跳过 crew workspace 同步
./scripts/apply-addons.sh --no-build   # 不执行 pnpm build（调用方自行处理）
./scripts/apply-addons.sh --no-restart # 不重启 gateway service
./scripts/apply-addons.sh --force      # 强制覆盖已有 workspace 文件
```

执行流程：
1. 恢复 `openclaw/` 到干净状态（`git reset --hard`）
2. 同步 `config-templates/` 中的配置项到运行时 `openclaw.json`
3. 安装全局 skills（`skills/` → `openclaw/skills/`）
4. 依次加载各 addon：overrides → patches → skills → crew 模板
5. `pnpm install`（仅有 overrides/patches 时）
6. `setup-crew.sh`（同步 crew workspace，可 `--skip-crew` 跳过）
7. `pnpm build`（编译 dist，可 `--no-build` 跳过）
8. `systemctl restart`（重启 gateway，可 `--no-restart` 跳过）

---

## dev.sh

**开发模式前台运行**。自动 apply addons，但**不 build**——需要用户自行 `cd openclaw && pnpm build`。

```bash
cd openclaw && pnpm build && cd ..   # 首次或修改源码后手动 build
./scripts/dev.sh gateway             # 前台启动 gateway
./scripts/dev.sh cli config set ...  # 运行 openclaw CLI 命令
```

---

## setup-crew.sh

**仅同步 crew workspace 的 markdown 文件**。不碰源码，不 build，不重启。适合只更新了 crew 模板内容（SOUL.md、AGENTS.md 等）的场景。

```bash
./scripts/setup-crew.sh          # 幂等同步（不覆盖已有文件）
./scripts/setup-crew.sh --force  # 强制覆盖（含 MEMORY.md 等个性化文件）
```

---

## 已废弃脚本

以下脚本仍然保留在仓库中但不再推荐使用：

| 脚本 | 替代方案 |
|------|---------|
| `upgrade.sh` | 使用 `install.sh` |
| `reinstall-daemon.sh` | 使用 `install.sh --skip-crew`（仅重装 daemon）或 `apply-addons.sh`（应用改动后重启） |

---

## 典型场景速查

| 场景 | 命令 |
|------|------|
| 新用户首次安装 | `./scripts/install.sh` |
| 老用户升级到最新版 | `./scripts/install.sh` |
| 修改了 patch 后测试 | `./scripts/apply-addons.sh` |
| 修改了 crew markdown 后同步 | `./scripts/setup-crew.sh` |
| 开发调试（前台运行） | `cd openclaw && pnpm build && cd .. && ./scripts/dev.sh gateway` |
