# Redis Infrastructure 文档

本文档介绍 awada-server 中 Redis Streams 基础设施的实现，供工程师检查和参考。

## 文件结构

```
src/
├── index.ts                           # 主入口
├── infrastructure/redis/
│   ├── types.ts                       # 类型定义（事件协议、配置等）
│   ├── connection.ts                  # Redis 连接管理（单例、连接池）
│   ├── producer.ts                    # EventProducer（XADD 写入）
│   ├── consumer.ts                    # EventConsumer（XREADGROUP 消费）
│   ├── idempotency.ts                 # 幂等/去重管理
│   ├── session.ts                     # Session 锁和序号管理
│   ├── conversation.ts                # Conversation ID 映射管理
│   └── index.ts                       # 统一导出
└── examples/
    ├── server-example.ts              # Server 端使用示例
    └── bot-example.ts                 # Bot 端使用示例
```

## 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| **EventProducer** | `producer.ts` | `XADD` 写入 Inbound/Outbound Stream，自动管理 session_seq |
| **EventConsumer** | `consumer.ts` | `XREADGROUP` 消费，自动 ACK、Pending 回收、DLQ 处理 |
| **IdempotencyManager** | `idempotency.ts` | `SETNX` 幂等检查，防止重复处理 |
| **SessionManager** | `session.ts` | 分布式锁 + 序号控制，确保同 session 按序串行处理 |
| **ConversationManager** | `conversation.ts` | 维护 (platform, user, channel) -> conversation_id 映射 |
| **RedisConnection** | `connection.ts` | 单例连接管理，支持多客户端 |

## 依赖安装

```bash
# 生产依赖
npm install ioredis uuid

# 开发依赖
npm install -D typescript @types/node @types/uuid tsx
```

## Payload 格式规范

### Payload 结构

`payload` 是一个数组，每个元素代表一条消息内容。数组中的元素按顺序发送。

```json
[{
  "type": "text",
  "text": "你好"
},
{
  "type": "image",
  "file_url": "https://example.com/image.png"
},
{
  "type": "audio",
  "file_path": "/path/to/audio.mp3"
},
{
  "type": "file",
  "file_id": "dddddxxxxxxxxx"
}]
```

### 消息类型定义

| type | 字段 | 说明 |
|------|------|------|
| `text` | `text` | 文本内容（字符串），允许放入表情符（前后用 `[]` 包裹），允许放入 URL |
| `image` | `file_url` 或 `file_path` 或 `file_id` | 图片（三选一） |
| `audio` | `file_url` 或 `file_path` 或 `file_id` | 音频（三选一） |
| `file` | `file_url` 或 `file_path` 或 `file_id` | 文件（三选一） |

**字段说明：**
- `file_url`：可访问的 URL
- `file_path`：本地绝对路径
- `file_id`：上传后获得的文件 ID

### 约束规则

1. `type` 仅允许 `text`、`image`、`audio`、`file` 四种
2. 一个 payload 数组中最多包含 **1 条** `text` 类型消息，但可以包含多个 `file`、`image`、`audio` 类型的消息
3. 当 payload 数组中存在 `text` 类型消息时，必须同时存在至少 1 条 `file` 或 `image` 消息
4. 纯文本消息可以直接使用单个 `text` 类型元素，例如：`[{"type": "text", "text": "你好"}]`
5. 支持发送纯图片或纯文件消息，但每条纯图片或纯文件消息的前一条或后一条消息中，必须包含一条 `text` 类型的消息，作为用户查询的上下文

**重要**：存入 Redis 时，整个事件会被序列化为 JSON；读取时，一次 `json.loads()` / `JSON.parse()` 即可

## Redis Key 命名规范

定义在 `types.ts` 的 `STREAM_KEYS` 中：

| Key 模式 | 用途 |
|----------|------|
| `awada:events:inbound:{lane}` | Inbound 事件流（Server -> Bot） |
| `awada:events:outbound:{lane}` | Outbound 事件流（Bot -> Server） |
| `awada:events:inbound:dlq` | Inbound 死信队列 |
| `awada:events:outbound:dlq` | Outbound 死信队列 |
| `awada:session_seq:{sessionId}` | Session 序号计数器 |
| `awada:session_next_seq:{sessionId}` | Session 下一个期望序号 |
| `awada:lock:session:{sessionId}` | Session 分布式锁 |
| `awada:processed:{eventId}` | 幂等标记 |
| `awada:conversation:{platform}:{userId}:{channelId}` | Conversation 映射 |

## Consumer Group 命名规范

| Group 模式 | 用途 |
|------------|------|
| `bot_workers_{lane}` | Bot 消费 Inbound |
| `server_dispatchers_{lane}` | Server 消费 Outbound |

## 可靠性机制

### 1. At-least-once 投递

- Redis Streams Consumer Group 提供 at-least-once 语义
- 消息处理成功后才 ACK
- 处理失败的消息留在 Pending 中等待重试

### 2. 幂等保证

- 使用 `IdempotencyManager` 对每个 event_id 做去重
- `SETNX` + TTL 原子操作
- 处理失败时移除幂等标记，允许重试

### 3. 顺序保证

- `session_seq`：Server 为每个 session 生成递增序号
- `session_next_seq`：Bot 维护期望的下一个序号
- 乱序消息不处理，等待重试

### 4. 并发控制

- `SessionManager` 使用分布式锁确保同一 session 串行处理
- 锁带有自动续租机制，防止处理时间过长导致锁过期

### 5. DLQ 处理

- 超过 `maxRetries` 次重试的消息自动进入 DLQ
- DLQ 消息包含原始事件、错误信息、重试次数等

## 配置参数

### StreamConfig（消费者配置）

```typescript
interface StreamConfig {
  consumerGroup: string;        // Consumer Group 名称
  consumerName: string;         // Consumer 名称（建议包含 PID）
  maxRetries: number;           // 最大重试次数，默认 5
  minIdleTimeMs: number;        // Pending 消息空闲超时（ms），默认 30000
  blockTimeMs: number;          // XREADGROUP BLOCK 时间（ms），默认 5000
  batchSize: number;            // 每次拉取消息数量，默认 10
  idempotencyTtlSeconds: number; // 幂等 key 过期时间（秒），默认 86400
}
```

### SessionLockOptions（Session 锁配置）

```typescript
interface SessionLockOptions {
  lockTimeoutMs: number;    // 锁超时时间（ms），默认 60000
  renewIntervalMs: number;  // 续租间隔（ms），默认 20000
}
```

## 参考文档

- [awada_top_architecture.md](../references/awada_top_architecture.md) - 顶层架构设计
- [PYTHON_INTEGRATION.md](./PYTHON_INTEGRATION.md) - Python 端对接手册
- [README.md](../../README.md) - 项目说明
