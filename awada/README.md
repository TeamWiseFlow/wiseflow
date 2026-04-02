# awada

## 为什么需要 awada？

部分第三方消息服务提供商（比如企微 bot、个微 bot）要求有固定公网 IP 作为接收端，而 openclaw 更多的应用场景是本地部署，没有公网 IP，或者需要从多个渠道接收消息分发给不同的 openclaw 实例处理——这都需要一个放置于公网的集中中转站。

对于企业级用户，如果私密要求特别高，希望自己掌控完整的 remote 端到 openclaw workstation 通信（即中间所有通信都是 self-host），awada 也是一个"开箱即用"的方案。

## 架构

```
微信用户
   │  (消息)
   ▼
WorkTool / QiweAPI  ──webhook──►  awada-server（公网服务器）
                                        │
                                     Redis Streams
                                  (awada:events:inbound:<lane>)
                                        │
                                        ▼
                              awada-extension（本地 openclaw）
                                        │
                                    openclaw agent
                                        │
                              awada:events:outbound:<lane>
                                        │
                                        ▼
                                    awada-server  ──►  微信用户（回复）
```

**核心组件：**
- **awada-server**：部署在公网服务器，负责接收 webhook 推送、写入 Redis Streams、消费 outbound 事件并回复用户
- **Redis**：消息中转，两侧通过 `awada:events:inbound:<lane>` 和 `awada:events:outbound:<lane>` 通信
- **awada-extension**：openclaw 的 channel 插件，订阅 Redis Streams 接收消息、回写回复

---

## 一、服务器端：部署 awada-server

### 前置条件

- 公网服务器（固定 IP 或域名）
- Node.js 18+
- Redis（可与 awada-server 同机或独立部署）
- WorkTool 账号（个微/企微 bot）或 QiweAPI 账号

### 安装

```bash
cd awada/awada-server
npm install
```

### 配置 .env

在 `awada/awada-server/` 目录下创建 `.env` 文件：

```bash
# ── 服务器 ──────────────────────────────────────────
PORT=8088

# ── Redis ────────────────────────────────────────────
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
# REDIS_DB=0   # 可选，默认 0

# ── Bot 配置（以 BOT_N_ 为前缀，N 从 1 开始） ────────
# WorkTool 个微/企微 bot 示例：
BOT_1_TYPE=worktool
BOT_1_ID=mybot
BOT_1_DEVICE_GUID=<worktool robotId>
BOT_1_LANES=user,admin
BOT_1_PLATFORM=worktool:mybot
BOT_1_NAME=My Bot

# QiweAPI 企微 bot 示例：
# BOT_1_TYPE=qiwe
# BOT_1_ID=qiwebot
# BOT_1_TOKEN=<qiweapi token>
# BOT_1_DEVICE_GUID=<qiweapi device guid>
# BOT_1_LANES=user
# BOT_1_PLATFORM=qiwe:qiwebot

# ── WorkTool 回调地址（worktool 类型必填） ────────────
WORKTOOL_CALLBACK_URL=https://your-domain.com/webhook/worktool
```

**Bot 配置说明：**

| 环境变量 | 说明 | 必填 |
|---------|------|------|
| `BOT_N_TYPE` | bot 类型：`worktool` 或 `qiwe` | 是 |
| `BOT_N_ID` | bot 唯一标识（自定义字符串） | 是 |
| `BOT_N_DEVICE_GUID` | WorkTool 填 robotId，QiweAPI 填 device guid | 是 |
| `BOT_N_LANES` | 该 bot 监听的 lane，逗号分隔（默认 `user,admin`） | 否 |
| `BOT_N_PLATFORM` | 平台标识，会写入消息事件（默认 `type:id`） | 否 |
| `BOT_N_TOKEN` | QiweAPI token（worktool 留空） | qiwe 必填 |
| `BOT_N_NAME` | bot 名称（可选） | 否 |

**Lane 与路由：**
- 每个 lane 对应一条 Redis Stream：`awada:events:inbound:<lane>`
- 通常用 `user` 代表普通用户消息，`admin` 代表管理员消息
- 多个 bot 可监听不同 lane，实现流量分流

### 启动

```bash
# 开发模式
npm run dev

# 使用 PM2（生产推荐）
pm2 start pm2.config.js
pm2 save
pm2 startup  # 按提示配置开机自启
```

### 设置 Webhook 回调

启动后，在 WorkTool 或 QiweAPI 后台将 webhook 地址配置为：

- WorkTool：`https://your-domain.com/webhook/worktool`
- QiweAPI：`https://your-domain.com/webhook/qiwe`

---

## 二、本地端：启用 awada-extension

### 安装插件

在 openclaw 的配置目录下执行：

```bash
# 进入 openclaw 项目
cd /path/to/openclaw

# 安装 awada-extension
# （具体安装方式参考 openclaw 插件文档）
```

### 安装 awada-extension 依赖（必做一次）

`awada-extension` 使用独立 `package.json` 管理依赖。首次在某个代码路径启用时，先安装依赖：

```bash
cd /path/to/openclaw_for_business/awada/awada-extension
pnpm install --prod
```

如果你使用本仓默认目录，可直接执行：

```bash
cd ~/openclaw_for_business/awada/awada-extension
pnpm install --prod
```

说明：
- 不需要每次启动都执行，只在以下情况需要重新执行：
- 首次在该目录启用 awada-extension
- `awada-extension/node_modules` 被清理（例如 `git clean -fdx` 或手动删除）
- `awada-extension/package.json` 依赖发生变更
- 典型报错信号：`Cannot find module 'ioredis'`

### 配置

在 openclaw 的配置文件（`~/.openclaw/openclaw.json` 或对应路径）中，添加 `channels.awada` 节点：

```json
{
  "channels": {
    "awada": {
      "enabled": true,
      "redisUrl": "redis://:YOUR_REDIS_PASSWORD@YOUR_SERVER_IP:6379/0",
      "lane": "user",
      "platform": "worktool:mybot"
    }
  }
}
```

**awada-extension 配置项：**

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | `true` | 是否启用该 channel |
| `redisUrl` | string | — | Redis 连接 URL，**必填** |
| `lane` | string | `"user"` | 订阅的 lane（每个 openclaw 实例只绑定一个 lane） |
| `platform` | string | — | 平台标识（如 `worktool:mybot`），主动发消息时必填 |
| `consumerGroup` | string | `"openclaw"` | Redis Consumer Group 名称 |
| `consumerName` | string | `"openclaw_bot"` | 消费者名称（多实例时需唯一） |
| `dmPolicy` | string | `"open"` | 消息接入策略：`open`/`pairing`/`allowlist` |
| `allowFrom` | string[] | `[]` | `allowlist` 模式下允许的用户 ID 列表 |
| `maxRetries` | number | `5` | 消息处理失败最大重试次数 |
| `blockTimeMs` | number | `5000` | Redis XREADGROUP 阻塞超时（毫秒） |
| `batchSize` | number | `10` | 每批拉取消息数量 |
| `perMsgMaxLen` | number | — | 单条消息最大字符数。设置后，超长回复会自动拆分为多条发送，每条不超过该值。适用于微信等对单消息长度有限制的平台。 |

> **设计约定：** awada-server 的 Bot 可监听多个 lane（`BOT_N_LANES=user,admin`），但 awada-extension 每个实例只绑定一个 lane，通过 lane 实现流量隔离与路由。`platform` 值须与 awada-server 端对应 Bot 的 `BOT_N_PLATFORM` 保持一致。

**Redis URL 格式：**
```
redis://HOST:PORT/DB                     # 无密码
redis://:PASSWORD@HOST:PORT/DB           # 有密码
redis://USERNAME:PASSWORD@HOST:PORT/DB   # 有用户名和密码
```

> 注意：如果密码包含 `@`、`#`、`!`、`%` 等特殊字符，必须先做 URL 编码再写入 `redisUrl`。  
> 例如原密码为 `Aw4d@R3d1s#2025!Sec`，应写为 `Aw4d%40R3d1s%232025%21Sec`。

**典型配置示例：**
```json
{
  "channels": {
    "awada": {
      "enabled": true,
      "redisUrl": "redis://:MyRedisPass@121.4.44.143:7601/0",
      "lane": "user",
      "platform": "worktool:mybot",
      "dmPolicy": "open"
    }
  }
}
```

**客服场景推荐配置（含消息长度限制 + 用户会话隔离）：**
```json
{
  "channels": {
    "awada": {
      "enabled": true,
      "redisUrl": "redis://:MyRedisPass@121.4.44.143:7601/0",
      "lane": "user",
      "platform": "worktool:mybot",
      "dmPolicy": "open",
      "perMsgMaxLen": 500
    }
  },
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

> **说明：**
> - `perMsgMaxLen: 500`：将超长回复自动拆分，每条不超过 500 字符。微信单消息有长度限制，建议设置此项。拆分在发送层进行，不影响 LLM 生成过程。
> - `session.dmScope: "per-channel-peer"`：每个微信用户（`user_id_external`）独享独立 session，用户 A 的对话上下文完全隔离于用户 B。`session` 是顶层配置，与 `channels` 平级。

### 通过向导配置

openclaw 支持交互式配置向导，启动后选择 "Configure channel → Awada"，按提示输入 Redis URL、lane 和 platform 即可。

---

## 三、验证连接

1. 确认 awada-server 已启动，Redis 可访问
2. 在 openclaw 状态面板查看 Awada channel 状态，显示 "connected to Redis" 即成功
3. 通过微信向 bot 发送测试消息，确认 openclaw agent 能收到并回复

---

## 四、多 Bot / 多 openclaw 实例

- **多 bot**：在 `.env` 中增加 `BOT_2_*`、`BOT_3_*` 等配置，每个 bot 分配不同 lane
- **多 openclaw 实例**：不同实例订阅不同 lane（`lane` 配置不同），或使用不同 `consumerGroup`
- **同一 Redis 多租户**：可通过不同 `db` 编号隔离（`redisUrl` 末尾 `/1`、`/2`…）
