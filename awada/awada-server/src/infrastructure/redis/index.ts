/**
 * Redis Infrastructure 统一导出
 */

// 类型定义
export * from './types';

// 连接管理
export { RedisConnection, getRedisClient, createRedisClient } from './connection';

// 事件生产者
export { EventProducer } from './producer';

// 事件消费者
export {
  EventConsumer,
  createInboundConsumer,
  createOutboundConsumer,
  type MessageHandler,
  type ConsumerOptions,
} from './consumer';

// 幂等性管理
export { IdempotencyManager, getIdempotencyManager } from './idempotency';

// Session 管理
export {
  SessionManager,
  getSessionManager,
  type SessionLockOptions,
} from './session';

// Conversation 管理
export { ConversationManager, getConversationManager } from './conversation';
