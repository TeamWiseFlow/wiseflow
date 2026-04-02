# PM2 多 Bot 部署指南

## 概述

本项目支持通过 PM2 同时运行多个 Bot 实例，每个 Bot 使用不同的 Token 和 Device GUID，完全隔离运行。

## 配置说明

### 1. 环境变量配置

在项目根目录创建 `.env` 文件（或使用系统环境变量）：

```bash
# Bot 1 - linfen
LINFEN_TOKEN=your_linfen_token_here
LINFEN_DEVICE_GUID=your_linfen_guid_here

# Bot 2 - wiseflow
WISEFLOW_TOKEN=your_wiseflow_token_here
WISEFLOW_DEVICE_GUID=your_wiseflow_guid_here

# Redis 配置（所有 Bot 共享）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

### 2. PM2 配置

配置文件：`pm2.config.js`

当前配置了两个 Bot：
- **awada-linfen**: 监听 `linfen` lane，端口 8088
- **awada-wiseflow**: 监听 `user,admin` lanes，端口 8089

### 3. Lane 分配

- **linfen bot**: 只监听 `linfen` lane
- **wiseflow bot**: 监听 `user` 和 `admin` lanes

## 使用方法

### 启动所有 Bot

```bash
# 启动所有 Bot
pm2 start pm2.config.js

# 或指定环境
pm2 start pm2.config.js --env production
```

### 管理单个 Bot

```bash
# 查看所有 Bot 状态
pm2 status

# 查看特定 Bot 日志
pm2 logs awada-linfen
pm2 logs awada-wiseflow

# 重启特定 Bot
pm2 restart awada-linfen

# 停止特定 Bot
pm2 stop awada-linfen

# 删除特定 Bot
pm2 delete awada-linfen
```

### 查看日志

```bash
# 查看所有 Bot 日志
pm2 logs

# 查看特定 Bot 日志
pm2 logs awada-linfen --lines 100

# 实时查看日志
pm2 logs --lines 0
```

### 监控

```bash
# 查看监控面板
pm2 monit

# 查看详细信息
pm2 describe awada-linfen
```

### 开机自启

```bash
# 保存当前 PM2 进程列表
pm2 save

# 生成开机自启脚本
pm2 startup

# 按照提示执行生成的命令
```

## 工作原理

### 1. Webhook 路由

所有 Bot 实例共享同一个 Webhook 地址（`/webhook`）。当收到回调时：

1. 每个实例检查回调中的 `guid` 字段
2. 如果 `guid` 匹配当前实例的 `QIWEAPI_DEVICE_GUID`，则处理消息
3. 如果不匹配，则静默忽略（不报错）

### 2. Lane 隔离

- 每个 Bot 只监听配置的 lanes
- 消息根据 `determineLane()` 函数分配到对应的 lane
- Outbound 消费者只处理属于自己 lanes 的消息

### 3. Redis 共享

- 所有 Bot 实例共享同一个 Redis
- 通过 `guid` 和 `lane` 区分消息
- 幂等性检查确保消息不重复处理

## 添加新 Bot

### 步骤 1: 添加环境变量

在 `.env` 文件中添加：

```bash
NEWBOT_TOKEN=your_token
NEWBOT_DEVICE_GUID=your_guid
```

### 步骤 2: 修改 pm2.config.js

在 `apps` 数组中添加新配置：

```javascript
{
  name: 'awada-newbot',
  script: './src/index.ts',
  interpreter: 'ts-node',
  interpreter_args: '-r tsconfig-paths/register',
  instances: 1,
  exec_mode: 'fork',
  env: {
    NODE_ENV: 'development',
    PORT: 8090,  // 使用不同的端口
    QIWEAPI_TOKEN: process.env.NEWBOT_TOKEN || '',
    QIWEAPI_DEVICE_GUID: process.env.NEWBOT_DEVICE_GUID || '',
    OUTBOUND_LANES: 'marketing_1',  // 指定 lanes
    PLATFORM: 'qiwe:newbot',
    BOT_NAME: 'newbot',
    REDIS_HOST: process.env.REDIS_HOST || 'localhost',
    REDIS_PORT: process.env.REDIS_PORT || '6379',
  },
  error_file: './logs/newbot-error.log',
  out_file: './logs/newbot-out.log',
}
```

### 步骤 3: 重启 PM2

```bash
pm2 reload pm2.config.js
```

## 注意事项

1. **Webhook 地址**: 所有 Bot 使用同一个 Webhook URL，QiweAPI 会推送所有 Bot 的回调
2. **端口**: 虽然每个 Bot 配置了不同端口，但实际只需要一个端口对外暴露（Webhook）
3. **日志**: 每个 Bot 有独立的日志文件，便于排查问题
4. **内存**: 每个 Bot 实例独立运行，注意总内存使用
5. **Redis**: 确保 Redis 连接数足够支持多个 Bot 实例

## 故障排查

### Bot 没有收到消息

1. 检查 Bot 的 `guid` 是否正确配置
2. 检查 Webhook 日志，确认消息是否被正确路由
3. 检查 Redis 连接是否正常

### 消息重复处理

1. 检查幂等性检查是否正常工作
2. 确认不同 Bot 的 lanes 没有重叠（除非业务需要）

### 性能问题

1. 使用 `pm2 monit` 查看各 Bot 的资源使用
2. 检查 Redis 连接数和性能
3. 考虑增加 Redis 连接池大小

