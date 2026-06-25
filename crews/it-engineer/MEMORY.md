# IT Engineer Agent — Memory

## 关于 wiseflow 项目

项目背景、功能介绍和目录结构详见工作区中的**项目背景.md**（由部署脚本自动同步，每次升级均为最新版）。

---

## Crew 通讯录（只读参考）
- 对内 Crew 通讯录：`~/.openclaw/crew_templates/TEAM_DIRECTORY.md`（由 Main Agent 维护，IT Engineer 只读）
- 对外 Crew 注册表：`~/.openclaw/workspace-hrbp/EXTERNAL_CREW_REGISTRY.md`（由 HRBP 维护，IT Engineer 只读）
- Crew 的增删改**不属于 IT Engineer 职责**；遇到 crew 相关配置��题，IT Engineer 可读取以上文件辅助排查，但不主动修改 crew 配置

---

## 安装路径（由 setup-crew.sh 自动维护）

> 实际项目路径记录在 `OFB_ENV.md`（同目录），每次运行 `setup-crew.sh` 自动更新。
> 执行任何脚本前，先读取该文件确认路径，再 `cd <PROJECT_ROOT>` 后调用 `./scripts/xxx.sh`。
>
> **禁止直接运行 `openclaw` 命令**，只能通过项目脚本或在 `openclaw/` 子目录内用 `pnpm openclaw` 调用。

---

## AWADA Extension 知识（运维必备）

### AWADA 是什么（定义与适用场景）
- `awada-server` 是部署在公网服务器的中转服务，解决"本地 OpenClaw 无固定公网 IP"但仍需接入第三方消息平台 webhook 的问题。
- `awada-extension` 是本地 OpenClaw 的 channel 插件，通过 Redis Streams 与 awada-server 双向通信。
- 典型场景：
  - WorkTool / QiweAPI 等要求固定公网回调地址
  - 多渠道统一接入后分发给不同 OpenClaw 实例
  - 企业希望 remote→local 全链路 self-host

### AWADA 架构要点
- 上行链路：
  - 用户消息 -> WorkTool/QiweAPI webhook -> awada-server -> `awada:events:inbound:<lane>` -> awada-extension -> OpenClaw agent
- 下行链路：
  - OpenClaw agent 回复 -> `awada:events:outbound:<lane>` -> awada-server -> 用户侧平台
- 核心组件职责：
  - `awada-server`：接 webhook、写 inbound stream、消费 outbound 并回发
  - `Redis`：事件总线（按 lane 分流）
  - `awada-extension`：订阅 inbound、提交 outbound

### 本地 channel 配置（openclaw.json）
- 配置入口：`channels.awada`
- 最小必填项：
  - `enabled: true`
  - `redisUrl`
  - `lane`（单实例只绑定一个 lane，通常 `user` 或 `admin`）
  - `platform`（需与 awada-server 端 `BOT_N_PLATFORM` 对齐）
- 常用可选项：
  - `consumerGroup`（默认 `openclaw`）
  - `consumerName`（多实例需唯一）
  - `dmPolicy` / `allowFrom`
  - `maxRetries` / `blockTimeMs` / `batchSize`
  - `perMsgMaxLen`：单条消息最大字符数，超长回���自动拆分多条发送（微信等平台有单消息长度限制时必设）
- Redis URL 示例：
  - `redis://HOST:PORT/DB`
  - `redis://:PASSWORD@HOST:PORT/DB`

### 客服场景配置要点

1. **`channels.awada.perMsgMaxLen`**(如 `1800`):微信对单条消息有长度限制,超长回复会被截断。设置此项后,awada-extension 会在发送层自动将长回复拆分为多条,不影响 LLM 生成。

```json
{
  "channels": {
    "awada": { "perMsgMaxLen": 500, "...": "其他配置" }
  }
}
```

2. 如需启动 customerDB hook（自动记录客户来访、更新状态等），需要在`plugins`字段下参考如下配置：

```json
"plugins": [
  {
    "path": "{wiseflow 项目路径}/awada/awada-extension",
    "config": {
      "customerdb": {
        "agentId": "sales-cs",
        "workspaceDir": "/home/wukong/.openclaw/workspace-sales-cs"
      }
    }
  }
]
```

---

### AWADA 排障检查单
0. 若日志出现 `Cannot find module 'ioredis'`（plugin=awada）：
   - 进入 awada-extension 目录安装依赖：
     ```bash
     cd <PROJECT_ROOT>/awada/awada-extension
     pnpm install --prod
     ```
   - 该命令不是每次都要跑，仅在首次启用、`node_modules` 被清理、或 `package.json` 变更后执行
0.1 若日志出现 ioredis 连接重试异常（如 `MaxRetriesPerRequestError`）：
   - 先检查 `channels.awada.redisUrl` 是否是合法 URL
   - 密码中如含 `@`、`#`、`!`、`%`，必须 URL 编码（如 `#` -> `%23`）
   - 常见误配症状：URL 被解析后 host 异常（例如变成 `R3d1s`），导致探测连接持续失败
1. awada-server 进程是否存活（pm2 / systemd）
2. Redis 连通性是否正常（公网访问、密码、db）
3. webhook 回调地址是否与平台后台配置一致
4. openclaw `channels.awada` 的 `lane/platform` 是否与服务端 bot 配置匹配
5. Channel 状态是否显示 connected，消息是否能完成收发闭环

---

## 如何更新 wiseflow 系统

### 升级命令
```bash
cd <PROJECT_ROOT>
./scripts/upgrade.sh
```

`upgrade.sh` 会依次：
1. 拉取最新代码（`git reset --hard origin/main`）
2. 读取 `openclaw.version`，按锚定 commit 检出 openclaw 引擎
   - 若已是目标 commit，跳过 install/build
3. 安装 / 更新依赖（`pnpm install`）并重新构建（`pnpm build`）
4. 重新应用 addons + 同步 crew 配置（`apply-addons.sh` 内含 `setup-crew.sh`）

升级完成后通常需要重启服务（详见 AGENTS.md **服务重启流程**）。

---

## 定时任务（Cron）维护方案

> **v2026.6.6 起**：cron 存储已从 JSON 文件迁移至 SQLite，**禁止再编辑任何 JSON 文件**。

### 存储变更

| 项目 | 旧方案（已废弃） | 新方案（当前） |
|------|------------------|----------------|
| Job 定义 | `~/.openclaw/cron/jobs.json` | SQLite 表 `cron_jobs` |
| 运行时状态 | `~/.openclaw/cron/jobs-state.json` | SQLite 同表内字段 |
| 运行日志 | `~/.openclaw/cron/runs/*.jsonl` | SQLite 表 `cron_run_logs` |
| 数据库位置 | — | `~/.openclaw/state/openclaw.sqlite` |

旧文件已被 `openclaw doctor --fix` 重命名为 `.migrated` 后缀，数据已导入 SQLite。`.migrated` 文件可安全删除。

### 日常管理命令

> ⚠️ **禁止直接运行 `openclaw` 命令**（不在系统 PATH 中）。
> 必须先 `cd` 到 openclaw 子目录，通过 `pnpm openclaw` 调用。
> 项目路径见同目录 `OFB_ENV.md`，以下用 `<OC>` 代指 `<WISEFLOW_PROJECT_ROOT>/openclaw`。

```bash
# 查看所有定时任务
cd <OC> && pnpm openclaw cron list

# 查看某个任务详情（含投递路由预览）
cd <OC> && pnpm openclaw cron show <job-id>

# 新增定时任务
cd <OC> && pnpm openclaw cron add "0 8 * * *" "任务描述" --name "任务名" --agent <agent-id>

# 编辑任务（修改调度/投递/模型等）
cd <OC> && pnpm openclaw cron edit <job-id> --announce --channel feishu --to "user:ou_xxx"
cd <OC> && pnpm openclaw cron edit <job-id> --model "provider/model"

# 启用/禁用任务
cd <OC> && pnpm openclaw cron edit <job-id> --enabled    # 启用
cd <OC> && pnpm openclaw cron edit <job-id> --no-enabled # 禁用

# 删除任务
cd <OC> && pnpm openclaw cron remove <job-id>

# 手动触发一次
cd <OC> && pnpm openclaw cron run <job-id>

# 查看运行历史
cd <OC> && pnpm openclaw cron runs --id <job-id> --limit 20
```

### 直接查询 SQLite（排查用）

```bash
# 列出所有 job 及关键字段
sqlite3 ~/.openclaw/state/openclaw.sqlite \
  "SELECT job_id, name, schedule_expr, enabled, delivery_mode, delivery_channel, delivery_to FROM cron_jobs;"

# 查看最近运行记录
sqlite3 ~/.openclaw/state/openclaw.sqlite \
  "SELECT job_id, seq, datetime(ts/1000, 'unixepoch', 'localtime') as time, status, error FROM cron_run_logs ORDER BY ts DESC LIMIT 20;"

# 修改投递目标（紧急调整时使用，正常应走 openclaw cron edit）
sqlite3 ~/.openclaw/state/openclaw.sqlite \
  "UPDATE cron_jobs SET delivery_to = 'user:ou_新ID' WHERE job_id = '目标job-id';"
```

### 迁移操作（仅升级后首次需要）

```bash
cd <OC> && pnpm openclaw doctor --fix
```

该命令会将 `jobs.json`、`jobs-state.json`、`runs/*.jsonl` 导入 SQLite，并将原文件重命名为 `.migrated`。**已迁移过则无需再执行**。

### 重要提醒

1. **禁止手动编辑** `~/.openclaw/cron/` 下的任何 JSON 文件，它们已不再被运行时读取
2. **禁止直接修改** SQLite 中 `job_json` 列（它是完整 job 定义的冗余快照），应通过 `openclaw cron edit` 修改，CLI 会同时更新结构化列和 `job_json`
3. `delivery_to` 等结构化列的紧急修改可直接 UPDATE，但后续应通过 CLI 确认一致性
4. cron 运行在 Gateway 进程内，修改后立即生效，无需重启

---

## 常见故障与解决方案

（在排查故障后将解决方案记录在此，方便复用）

---

## 部署记录

（首次部署和重要变更记录）
