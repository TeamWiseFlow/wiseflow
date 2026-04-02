/**
 * Redis Streams 事件类型定义
 * 基于 awada_top_architecture.md 的协议规范
 */

// ============ 基础类型 ============

export type Lane = string;
export type ActorType = 'end_user' | 'admin' | 'system';
export type Platform = string;

// Inbound 事件类型
export type InboundEventType = 'MESSAGE_NEW' | 'PAYMENT_SUCCESS' | 'BUTTON_CLICK';

// Outbound 事件类型
export type OutboundEventType = 'REPLY_MESSAGE' | 'COMMAND_EXECUTE';

// ============ Payload 类型 ============

// 内容对象类型
export interface TextObject {
  type: 'text';
  text: string;
}

export interface ImageObject {
  type: 'image';
  file_path?: string;
  file_url?: string;
  file_id?: string; // 上传后获得的 file_id
  base64?: string;
}

export interface AudioObject {
  type: 'audio';
  file_path?: string;
  file_url?: string;
  file_id?: string; // 上传后获得的 file_id
}

export interface FileObject {
  type: 'file';
  file_path?: string;
  file_url?: string;
  file_name?: string;
  file_id?: string; // 上传后获得的 file_id
}

export type ContentObject = TextObject | ImageObject | AudioObject | FileObject;

// Payload 是 ContentObject 数组
// 每个元素代表一条消息内容，数组中的元素按顺序发送
export type Payload = ContentObject[];

// ============ Inbound 事件 ============

export interface InboundMeta {
  platform: Platform;
  tenant_id: string;
  channel_id: string;
  lane: Lane;
  actor_type: ActorType;
  user_id_external: string;
  session_id: string;
  session_seq: number;
  source_message_id: string;
  raw_ref?: string;
  conversation_id?: string;
}

export interface InboundEvent {
  schema_version: number;
  event_id: string;
  type: InboundEventType;
  timestamp: number;
  correlation_id: string;
  trace_id: string;
  meta: InboundMeta;
  payload: Payload;
}

// ============ Outbound 事件 ============

export interface OutboundTarget {
  platform: Platform;
  tenant_id: string;
  lane: Lane;
  user_id_external: string;
  channel_id: string;
  reply_token?: string;
  conversation_id?: string;
  /**
   * action_ask: [int, ["string", ...]]
   * 用于群聊消息中@特定用户
   * 第一个元素为 int（当前为 0），第二个元素为用户列表
   * "all" 代表@所有人
   */
  action_ask?: [number, string[]];
}

export interface OutboundEvent {
  schema_version: number;
  event_id: string;
  reply_to_event_id: string;
  type: OutboundEventType;
  timestamp: number;
  correlation_id: string;
  trace_id: string;
  target: OutboundTarget;
  payload: Payload;
}

// ============ Redis Streams 相关类型 ============

export interface StreamMessage<T = InboundEvent | OutboundEvent> {
  id: string; // Redis Stream message ID (e.g., "1715667890-0")
  data: T;
  deliveryCount?: number;
}

export interface ConsumerGroupInfo {
  name: string;
  consumers: number;
  pending: number;
  lastDeliveredId: string;
}

export interface PendingMessage {
  id: string;
  consumer: string;
  idleTime: number;
  deliveryCount: number;
}

// ============ DLQ 相关类型 ============

export interface DLQEntry<T = InboundEvent | OutboundEvent> {
  originalEvent: T;
  originalStreamId: string;
  lastError: string;
  lastErrorAt: number;
  deliveryCount: number;
  movedToDlqAt: number;
}

// ============ 配置类型 ============

export interface RedisConfig {
  host: string;
  port: number;
  password?: string;
  db?: number;
  keyPrefix?: string;
}

export interface StreamConfig {
  // Consumer Group 配置
  consumerGroup: string;
  consumerName: string;

  // 重试配置
  maxRetries: number; // 最大重试次数，默认 5
  minIdleTimeMs: number; // 最小空闲时间（ms），默认 30000

  // 消费配置
  blockTimeMs: number; // XREADGROUP BLOCK 时间（ms），默认 5000
  batchSize: number; // 每次拉取消息数量，默认 10

  // 幂等配置
  idempotencyTtlSeconds: number; // 幂等 key 过期时间（秒），默认 86400 (24h)
}

export const DEFAULT_STREAM_CONFIG: StreamConfig = {
  consumerGroup: 'default_group',
  consumerName: 'default_consumer',
  maxRetries: 5,
  minIdleTimeMs: 30000,
  blockTimeMs: 5000,
  batchSize: 10,
  idempotencyTtlSeconds: 86400
};

// ============ Stream Key 生成 ============

export const STREAM_KEYS = {
  inbound: (lane: Lane) => `awada:events:inbound:${lane}`,
  outbound: (lane: Lane) => `awada:events:outbound:${lane}`,
  inboundDlq: () => 'awada:events:inbound:dlq',
  outboundDlq: () => 'awada:events:outbound:dlq',

  // Session 相关
  sessionSeq: (sessionId: string) => `awada:session_seq:${sessionId}`,
  sessionNextSeq: (sessionId: string) => `awada:session_next_seq:${sessionId}`,
  sessionLock: (sessionId: string) => `awada:lock:session:${sessionId}`,

  // 幂等相关
  processed: (eventId: string) => `awada:processed:${eventId}`,

  // Conversation 相关
  conversationMapping: (platform: Platform, userIdExternal: string, channelId: string) => `awada:conversation:${platform}:${userIdExternal}:${channelId}`
} as const;

// ============ Consumer Group 命名约定 ============

export const CONSUMER_GROUPS = {
  // Bot 消费 Inbound
  botWorkers: (lane: Lane) => `bot_workers_${lane}`,
  // Server 消费 Outbound
  serverDispatchers: (lane: Lane) => `server_dispatchers_${lane}`
} as const;
