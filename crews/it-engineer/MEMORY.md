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

## 常见故障与解决方案

（在排查故障后将解决方案记录在此，方便复用）

---

## 部署记录

（首次部署和重要变更记录）
