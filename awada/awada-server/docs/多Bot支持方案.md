# 多 Bot 支持方案

## 概述

基于 Bot ID 的多实例管理方案，支持在单个进程中运行多个 Bot 实例，每个 Bot 有独立的配置（token、deviceGuid、lanes）。

## 架构设计

### 核心组件

1. **Bot 配置管理器** (`config/bots.ts`)
   - 从环境变量加载 Bot 配置
   - 支持多个 Bot 实例配置

2. **Bot 管理器** (`src/services/bot/manager.ts`)
   - 管理所有 Bot 实例
   - 通过 GUID 或 Bot ID 查找 Bot 配置
   - 单例模式，全局唯一

3. **Webhook 路由** (`src/routes/webhook.ts`)
   - 通过回调消息中的 `guid` 识别 Bot
   - 将消息路由到对应的 Bot 处理

4. **消息处理** (`src/services/message/index.ts`)
   - 接收 `botConfig` 参数
   - 使用 Bot 特定的配置处理消息
   - 在 InboundEvent 中添加 `bot_id` 字段

5. **消息发送** (`src/services/outbound/index.ts`)
   - 从 `OutboundEvent.target.bot_id` 获取 Bot 配置
   - 使用对应的 token 和 deviceGuid 发送消息

6. **QiweAPI Client** (`services/qiweapi/client.ts`)
   - 支持动态 token（通过 `call` 方法的第三个参数）

## 配置方式

### 环境变量

在 `.env` 或环境变量中配置每个 Bot 的信息：

```bash
# Bot 1: linfen
LINFEN_TOKEN=your_linfen_token
LINFEN_DEVICE_GUID=your_linfen_guid

# Bot 2: wiseflow
WISEFLOW_TOKEN=your_wiseflow_token
WISEFLOW_DEVICE_GUID=your_wiseflow_guid

# 共享配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

### Bot 配置结构

```typescript
interface BotConfig {
  botId: string;           // Bot 唯一标识
  token: string;          // QiweAPI Token
  deviceGuid: string;     // 设备 GUID
  lanes: Lane[];         // 该 Bot 监听的 lanes
  platform: Platform;    // 平台标识（如 'qiwe:linfen'）
  name?: string;         // Bot 名称（可选）
}
```

## 工作流程

### 1. 初始化

```typescript
// src/index.ts
import { initializeBotManager } from './services/bot/manager';
import { BOT_CONFIGS } from '@/config/bots';

// 初始化 Bot 管理器
initializeBotManager(BOT_CONFIGS);
```

### 2. 接收消息（Webhook）

```typescript
// src/routes/webhook.ts
async function handleRawMessage(rawMsg: CallbackMessageRaw): Promise<void> {
  // 通过 guid 识别 Bot
  const botManager = getBotManager();
  const botConfig = botManager.getBotByGuid(rawMsg.guid);
  
  if (!botConfig) {
    // 未知 Bot，忽略
    return;
  }
  
  // 使用 botConfig 处理消息
  await handleNormalMessage(rawMsg, botConfig);
}
```

### 3. 处理消息（Inbound）

```typescript
// src/services/message/index.ts
export async function handleMessage(
  message: CallbackMessage, 
  botConfig: BotConfig
): Promise<{...}> {
  // 使用 botConfig 的 platform 和 lanes
  const lane = determineLane(message, botConfig);
  const PLATFORM = botConfig.platform;
  
  // 发布到 Redis，包含 bot_id
  await producer.createAndPublishInbound({
    meta: {
      platform: PLATFORM,
      lane,
      bot_id: botConfig.botId,  // 添加 bot_id
      // ...
    },
    payload: payload
  });
}
```

### 4. 发送消息（Outbound）

```typescript
// src/services/outbound/index.ts
async function dispatchToPlatform(event: OutboundEvent): Promise<void> {
  const { bot_id, platform } = event.target;
  
  // 获取 Bot 配置
  const botManager = getBotManager();
  let botConfig = botManager.getBotById(bot_id);
  
  // 如果没有指定 bot_id，从 platform 推断
  if (!botConfig && platform) {
    const platformBotId = platform.replace('qiwe:', '');
    botConfig = botManager.getBotById(platformBotId);
  }
  
  // 使用 botConfig 发送消息
  await handlePayload(payload, toId, channelId, botConfig);
}
```

### 5. 发送消息（使用 Bot 配置）

```typescript
// src/services/outbound/index.ts
async function handlePayload(
  payload: Payload, 
  toId: string, 
  channelId: string, 
  botConfig: BotConfig
): Promise<void> {
  // 使用 botConfig 的 token 和 deviceGuid
  await sendMessage(toId, content, undefined, botConfig.deviceGuid, botConfig.token);
}
```

## 关键改进

### 1. 类型定义扩展

- `InboundMeta` 添加 `bot_id?: string`
- `OutboundTarget` 添加 `bot_id?: string`
- `Platform` 类型扩展：`'qiwe:linfen' | 'qiwe:wiseflow'`

### 2. QiweAPI Client 支持动态 Token

```typescript
// services/qiweapi/client.ts
public async call<T, P>(
  method: string,
  params: P,
  token: string  
): Promise<ApiResponse<T>> {
  const requestToken = token || qiweapiConfig.token;
  // 使用 requestToken 发送请求
}
```

### 3. 所有发送函数支持 Token

所有消息发送函数都添加了 `token: string` 参数：
- `sendTextMsg`
- `sendHyperTextMsg`
- `sendMixTextMsg`
- `sendImageMsg`
- `sendFileMsg`
- `sendVoiceMsg`
- `sendMessage`
- `uploadFileByUrl`

## 使用示例

### 配置多个 Bot

```typescript
// config/bots.ts
export const BOT_CONFIGS: BotConfig[] = [
  {
    botId: 'linfen',
    token: process.env.LINFEN_TOKEN || '',
    deviceGuid: process.env.LINFEN_DEVICE_GUID || '',
    lanes: ['linfen'],
    platform: 'qiwe:linfen',
    name: 'linfen',
  },
  {
    botId: 'wiseflow',
    token: process.env.WISEFLOW_TOKEN || '',
    deviceGuid: process.env.WISEFLOW_DEVICE_GUID || '',
    lanes: ['user', 'admin'],
    platform: 'qiwe:wiseflow',
    name: 'wiseflow',
  },
];
```

### 在代码中使用

```typescript
// 获取 Bot 管理器
const botManager = getBotManager();

// 通过 GUID 查找 Bot
const botConfig = botManager.getBotByGuid('some-guid');

// 通过 Bot ID 查找 Bot
const botConfig = botManager.getBotById('linfen');

// 获取所有 Bot
const allBots = botManager.getAllBots();

// 根据 lane 查找 Bot
const bots = botManager.getBotsByLane('linfen');
```

## 向后兼容

- 如果没有指定 `bot_id`，系统会尝试从 `platform` 推断
- 如果找不到对应的 Bot，会使用第一个可用的 Bot（向后兼容）
- 如果所有 Bot 都不可用，会回退到全局配置（如果存在）

## 注意事项

1. **Webhook 回调**：确保 QiweAPI 的回调地址正确配置，所有 Bot 的回调都会发送到同一个地址
2. **Redis Streams**：不同 Bot 的消息通过 `bot_id` 和 `lane` 区分，但共享同一个 Redis Stream
3. **Token 管理**：每个 Bot 使用独立的 token，确保 token 不会混淆
4. **GUID 唯一性**：每个 Bot 的 `deviceGuid` 必须唯一，用于识别消息来源

## 优势

1. **单进程运行**：所有 Bot 在同一个进程中运行，资源占用更少
2. **配置灵活**：通过环境变量配置，易于部署和管理
3. **代码复用**：共享大部分代码逻辑，只需区分配置
4. **易于扩展**：添加新 Bot 只需添加配置，无需修改代码

## 与 PM2 方案对比

| 特性 | 基于 Bot ID 方案 | PM2 方案 |
|------|----------------|----------|
| 进程数 | 1 个 | N 个（每个 Bot 一个进程） |
| 资源占用 | 低 | 高 |
| 配置管理 | 环境变量 | PM2 配置文件 |
| 代码复杂度 | 中等 | 低 |
| 隔离性 | 逻辑隔离 | 进程隔离 |
| 扩展性 | 高 | 中等 |

## 故障排查

### Bot 未识别

- 检查环境变量是否正确配置
- 检查 `BOT_CONFIGS` 是否正确加载
- 检查回调消息中的 `guid` 是否匹配

### 消息发送失败

- 检查 `botConfig.token` 是否正确
- 检查 `botConfig.deviceGuid` 是否存在
- 检查 `OutboundEvent.target.bot_id` 是否正确设置

### Token 混淆

- 确保每个 Bot 使用独立的 token
- 检查 `apiClient.call` 是否正确传递 token 参数

