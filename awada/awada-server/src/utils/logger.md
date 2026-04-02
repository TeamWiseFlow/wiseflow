# 日志工具使用说明

## 概述

`logger.ts` 提供统一的日志工具，所有日志时间统一为**北京时间（UTC+8）**，格式为 `YYYY-MM-DD HH:mm:ss.SSS`。

## 特性

- ✅ 统一的时间格式（北京时间 UTC+8）
- ✅ 支持日志级别：`DEBUG`、`INFO`、`WARN`、`ERROR`
- ✅ 支持模块前缀，便于区分不同模块的日志
- ✅ 自动格式化对象为 JSON
- ✅ 兼容 emoji 和特殊字符

## 快速开始

### 方式一：使用默认 logger（无前缀）

```typescript
import { logger } from '@/utils/logger';

logger.info('这是一条信息');
logger.warn('这是一条警告');
logger.error('这是一条错误');
logger.debug('这是一条调试信息');
```

**输出示例：**
```
[2025-12-22 14:56:55.285] [INFO] 这是一条信息
[2025-12-22 14:56:55.286] [WARN] 这是一条警告
[2025-12-22 14:56:55.287] [ERROR] 这是一条错误
[2025-12-22 14:56:55.288] [DEBUG] 这是一条调试信息
```

### 方式二：创建带前缀的 logger（推荐）

```typescript
import { createLogger } from '@/utils/logger';

const logger = createLogger('Webhook');
logger.info('收到回调');
logger.error('处理失败', error);
```

**输出示例：**
```
[2025-12-22 14:56:55.285] [Webhook] [INFO] 收到回调
[2025-12-22 14:56:55.286] [Webhook] [ERROR] 处理失败
```

### 方式三：使用便捷方法

```typescript
import { log, info, warn, error, debug } from '@/utils/logger';

info('这是一条信息');
warn('这是一条警告');
error('这是一条错误');
debug('这是一条调试信息');
```

## API 参考

### Logger 类

#### 创建 Logger 实例

```typescript
import { Logger, createLogger } from '@/utils/logger';

// 方式1：使用 createLogger 工厂函数（推荐）
const logger = createLogger('ModuleName');

// 方式2：直接实例化
const logger = new Logger('ModuleName');
```

#### 方法

##### `logger.debug(...args: any[]): void`
输出调试级别日志，用于开发调试。

```typescript
logger.debug('调试信息', { key: 'value' });
// 输出: [2025-12-22 14:56:55.285] [ModuleName] [DEBUG] 调试信息 {"key":"value"}
```

##### `logger.info(...args: any[]): void`
输出信息级别日志，用于一般信息记录。

```typescript
logger.info('操作成功');
logger.info('✅ 消息已发送');
// 输出: [2025-12-22 14:56:55.285] [ModuleName] [INFO] 操作成功
// 输出: [2025-12-22 14:56:55.286] [ModuleName] [INFO] ✅ 消息已发送
```

##### `logger.warn(...args: any[]): void`
输出警告级别日志，用于警告信息。

```typescript
logger.warn('⚠️ 配置缺失，使用默认值');
// 输出: [2025-12-22 14:56:55.285] [ModuleName] [WARN] ⚠️ 配置缺失，使用默认值
```

##### `logger.error(...args: any[]): void`
输出错误级别日志，用于错误信息。

```typescript
logger.error('处理失败', error);
// 输出: [2025-12-22 14:56:55.285] [ModuleName] [ERROR] 处理失败 [错误堆栈]
```

##### `logger.log(...args: any[]): void`
`logger.info()` 的别名，兼容 `console.log`。

```typescript
logger.log('这是一条日志');
// 等同于 logger.info('这是一条日志');
```

### 便捷方法

```typescript
import { log, info, warn, error, debug } from '@/utils/logger';

// 这些方法使用默认 logger（无前缀）
log('日志');      // 等同于 logger.info()
info('信息');     // 等同于 logger.info()
warn('警告');     // 等同于 logger.warn()
error('错误');    // 等同于 logger.error()
debug('调试');    // 等同于 logger.debug()
```

## 使用示例

### 示例 1：在服务模块中使用

```typescript
// src/services/message/index.ts
import { createLogger } from '@/utils/logger';

const logger = createLogger('Message');

export async function handleMessage(message: CallbackMessage) {
  logger.info('开始处理消息');
  
  try {
    // 处理逻辑
    logger.debug('消息详情:', { msgType: message.msgType, senderId: message.senderId });
    logger.info('✅ 消息处理成功');
  } catch (error) {
    logger.error('❌ 消息处理失败:', error);
    throw error;
  }
}
```

**输出：**
```
[2025-12-22 14:56:55.285] [Message] [INFO] 开始处理消息
[2025-12-22 14:56:55.286] [Message] [DEBUG] 消息详情: {"msgType":2,"senderId":"7881302994934588"}
[2025-12-22 14:56:55.287] [Message] [INFO] ✅ 消息处理成功
```

### 示例 2：在路由中使用

```typescript
// src/routes/webhook.ts
import { createLogger } from '@/utils/logger';

const logger = createLogger('Webhook');

router.post('/', async (ctx) => {
  logger.info('🚀🚀🚀 -【收到回调】- 🚀🚀🚀');
  logger.debug('原始数据:', ctx.request.body);
  
  try {
    // 处理逻辑
    logger.info('✅ 回调处理完成');
  } catch (error) {
    logger.error('❌ 回调处理失败:', error);
  }
});
```

### 示例 3：记录对象数据

```typescript
const logger = createLogger('API');

const response = {
  code: 0,
  data: { userId: '123', name: 'John' }
};

logger.info('API 响应:', response);
// 输出: [2025-12-22 14:56:55.285] [API] [INFO] API 响应: {
//   "code": 0,
//   "data": {
//     "userId": "123",
//     "name": "John"
//   }
// }
```

### 示例 4：错误处理

```typescript
const logger = createLogger('Service');

try {
  await someOperation();
} catch (error: any) {
  logger.error('操作失败:', error);
  logger.error('错误详情:', {
    message: error.message,
    stack: error.stack,
    code: error.code
  });
}
```

## 日志级别说明

| 级别 | 方法 | 用途 | 示例场景 |
|------|------|------|----------|
| `DEBUG` | `logger.debug()` | 调试信息 | 变量值、函数调用、详细流程 |
| `INFO` | `logger.info()` | 一般信息 | 操作成功、状态变化、重要事件 |
| `WARN` | `logger.warn()` | 警告信息 | 配置缺失、降级处理、潜在问题 |
| `ERROR` | `logger.error()` | 错误信息 | 异常捕获、操作失败、系统错误 |

## 最佳实践

### 1. 使用模块前缀

为每个模块创建独立的 logger 实例，便于日志过滤和查找：

```typescript
// ✅ 推荐
const messageLogger = createLogger('Message');
const webhookLogger = createLogger('Webhook');
const outboundLogger = createLogger('Outbound');

// ❌ 不推荐（所有日志混在一起）
import { logger } from '@/utils/logger';
logger.info('消息'); // 无法区分是哪个模块
```

### 2. 合理使用日志级别

```typescript
// ✅ 推荐
logger.debug('内部变量值:', { userId, sessionId }); // 调试信息
logger.info('✅ 消息已发送'); // 重要操作
logger.warn('⚠️ 使用默认配置'); // 警告
logger.error('❌ 发送失败:', error); // 错误

// ❌ 不推荐
logger.info('userId:', userId); // 应该用 debug
logger.error('这是一条普通信息'); // 应该用 info
```

### 3. 错误日志包含上下文

```typescript
// ✅ 推荐
logger.error('发送消息失败:', {
  error: error.message,
  userId: message.senderId,
  msgType: message.msgType,
  stack: error.stack
});

// ❌ 不推荐
logger.error('发送失败'); // 缺少上下文信息
```

### 4. 使用 emoji 增强可读性

```typescript
// ✅ 推荐（清晰直观）
logger.info('✅ 消息已发送');
logger.warn('⚠️ 配置缺失');
logger.error('❌ 处理失败');

// ❌ 不推荐（不够直观）
logger.info('消息已发送');
logger.warn('配置缺失');
logger.error('处理失败');
```

## 迁移指南

### 从 console.log 迁移

**替换规则：**
- `console.log()` → `logger.info()` 或 `logger.log()`
- `console.warn()` → `logger.warn()`
- `console.error()` → `logger.error()`
- `console.info()` → `logger.info()`
- `console.debug()` → `logger.debug()`

**示例：**

```typescript
// 迁移前
console.log('[Webhook] 收到回调');
console.error('[Webhook] 处理失败:', error);

// 迁移后
import { createLogger } from '@/utils/logger';
const logger = createLogger('Webhook');

logger.info('收到回调');
logger.error('处理失败:', error);
```

## 时间格式说明

所有日志时间统一为**北京时间（UTC+8）**，格式为：

```
YYYY-MM-DD HH:mm:ss.SSS
```

**示例：**
```
2025-12-22 14:56:55.285
```

- `YYYY-MM-DD`：年-月-日
- `HH:mm:ss`：时:分:秒（24小时制）
- `SSS`：毫秒（3位数字）

## 注意事项

1. **对象格式化**：对象会自动格式化为 JSON，但如果对象包含循环引用，会抛出错误
2. **Emoji 支持**：支持 emoji 和特殊字符，会自动识别并正确输出
3. **性能**：日志输出是同步的，大量日志可能影响性能，生产环境建议使用日志级别过滤
4. **时区**：所有时间都是北京时间（UTC+8），不受系统时区影响

## 常见问题

### Q: 如何禁用某个级别的日志？

A: 目前不支持动态配置日志级别，所有级别的日志都会输出。如需过滤，可以在日志收集系统中进行过滤。

### Q: 如何输出到文件？

A: 当前实现只输出到控制台（console）。如需输出到文件，可以使用日志收集工具（如 PM2、Winston）或重定向输出。

### Q: 时间不准确怎么办？

A: 日志工具会自动将时间转换为北京时间（UTC+8）。如果时间仍不准确，请检查系统时间设置。

### Q: 如何自定义日志格式？

A: 可以修改 `src/utils/logger.ts` 中的 `format` 方法来自定义格式。

## 相关文件

- `src/utils/logger.ts` - 日志工具实现
- `src/services/message/index.ts` - 使用示例
- `src/routes/webhook.ts` - 使用示例

