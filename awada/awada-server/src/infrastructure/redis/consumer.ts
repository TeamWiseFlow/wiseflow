/**
 * EventConsumer - 事件消费者
 * 负责从 Redis Streams 消费事件 (XREADGROUP)
 * 包含 ACK、重试、DLQ 等机制
 */

import Redis from 'ioredis';
import {
  InboundEvent,
  OutboundEvent,
  StreamMessage,
  StreamConfig,
  DEFAULT_STREAM_CONFIG,
  PendingMessage,
  Lane,
  STREAM_KEYS,
  CONSUMER_GROUPS,
} from './types';
import { createRedisClient } from './connection';
import { EventProducer } from './producer';

export type MessageHandler<T> = (message: StreamMessage<T>) => Promise<void>;

export interface ConsumerOptions extends Partial<StreamConfig> {
  streamKey: string;
  onMessage: MessageHandler<InboundEvent | OutboundEvent>;
  onError?: (error: Error, message?: StreamMessage<any>) => void;
}

export class EventConsumer {
  private redis: Redis;
  private producer: EventProducer;
  private config: StreamConfig;
  private streamKey: string;
  private isRunning: boolean = false;
  private onMessage: MessageHandler<InboundEvent | OutboundEvent>;
  private onError?: (error: Error, message?: StreamMessage<any>) => void;

  constructor(options: ConsumerOptions, redis?: Redis) {
    // Consumer 需要独立的 Redis 连接（因为 XREADGROUP BLOCK 会阻塞）
    this.redis = redis ?? createRedisClient();
    this.producer = new EventProducer();
    this.config = { ...DEFAULT_STREAM_CONFIG, ...options };
    this.streamKey = options.streamKey;
    this.onMessage = options.onMessage;
    this.onError = options.onError;
  }

  /**
   * 启动消费者
   * 会先确保 Consumer Group 存在
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      console.warn('Consumer is already running');
      return;
    }

    await this.ensureConsumerGroup();
    this.isRunning = true;

    console.log(
      `Consumer started: stream=${this.streamKey}, group=${this.config.consumerGroup}, consumer=${this.config.consumerName}`
    );

    // 启动两个并行任务
    this.consumeLoop();
    this.reclaimLoop();
  }

  /**
   * 停止消费者
   */
  async stop(): Promise<void> {
    this.isRunning = false;
    console.log('Consumer stopping...');
    // 等待循环结束（最多等待 blockTimeMs + 1秒）
    await this.sleep(this.config.blockTimeMs + 1000);
    // 关闭 Redis 连接
    await this.redis.quit();
  }

  /**
   * 主消费循环
   */
  private async consumeLoop(): Promise<void> {
    while (this.isRunning) {
      try {
        await this.consumeBatch();
      } catch (error) {
        console.error('Error in consume loop:', error);
        this.onError?.(error as Error);
        // 出错后短暂休息避免死循环
        await this.sleep(1000);
      }
    }
  }

  /**
   * Pending 回收循环
   * 定期回收超时的消息
   */
  private async reclaimLoop(): Promise<void> {
    while (this.isRunning) {
      try {
        await this.reclaimPendingMessages();
      } catch (error) {
        console.error('Error in reclaim loop:', error);
      }
      // 每 10 秒检查一次
      await this.sleep(10000);
    }
  }

  /**
   * 消费一批消息
   */
  private async consumeBatch(): Promise<void> {
    // XREADGROUP GROUP group consumer [COUNT count] [BLOCK ms] STREAMS key id
    // 使用 '>' 表示只读取新消息
    const result = await this.redis.xreadgroup(
      'GROUP',
      this.config.consumerGroup,
      this.config.consumerName,
      'COUNT',
      this.config.batchSize,
      'BLOCK',
      this.config.blockTimeMs,
      'STREAMS',
      this.streamKey,
      '>' // 只读取新消息
    );

    if (!result || result.length === 0) {
      return; // 没有新消息
    }

    // result 格式: [[streamKey, [[id, [field, value, ...]]]]]
    const [, messages] = result[0] as [string, [string, string[]][]];

    for (const [id, fields] of messages) {
      await this.processMessage(id, fields);
    }
  }

  /**
   * 处理单条消息
   */
  private async processMessage(id: string, fields: string[]): Promise<void> {
    // 解析消息
    const data = this.parseFields(fields);
    if (!data) {
      console.error(`Failed to parse message: ${id}`);
      await this.ack(id);
      return;
    }

    const message: StreamMessage<InboundEvent | OutboundEvent> = {
      id,
      data,
    };

    try {
      await this.onMessage(message);
      // 处理成功，ACK
      await this.ack(id);
    } catch (error) {
      console.error(`Error processing message ${id}:`, error);
      this.onError?.(error as Error, message);
      // 不 ACK，让消息留在 Pending 中等待重试
    }
  }

  /**
   * 回收超时的 Pending 消息
   * 使用 XAUTOCLAIM（Redis 6.2+）自动回收超时消息
   */
  private async reclaimPendingMessages(): Promise<void> {
    try {
      // XAUTOCLAIM key group consumer min-idle-time start [COUNT count]
      // 返回: [next-id, [claimed-messages], [deleted-ids]]
      const result = await this.redis.call(
        'XAUTOCLAIM',
        this.streamKey,
        this.config.consumerGroup,
        this.config.consumerName,
        this.config.minIdleTimeMs,
        '0-0', // 从最早的消息开始
        'COUNT',
        this.config.batchSize
      ) as [string, [string, string[]][], string[]];

      if (!result || !result[1] || result[1].length === 0) {
        return; // 没有需要回收的消息
      }

      // result[1] 是 claimed messages: [[id, [field, value, ...]], ...]
      const claimedMessages = result[1] as [string, string[]][];

      console.log(`Auto-claimed ${claimedMessages.length} timed-out pending messages`);

      for (const [id, fields] of claimedMessages) {
        try {
          // 获取投递次数
          const deliveryCount = await this.getDeliveryCount(id);

          if (deliveryCount >= this.config.maxRetries) {
            // 超过最大重试次数，移入 DLQ
            await this.moveToDlq(id, fields, deliveryCount);
          } else {
            // 重新处理
            await this.processMessage(id, fields);
          }
        } catch (error) {
          console.error(`Error processing reclaimed message ${id}:`, error);
        }
      }
    } catch (error) {
      console.error('Error in reclaim loop:', error);
    }
  }

  /**
   * 获取消息的投递次数
   */
  private async getDeliveryCount(messageId: string): Promise<number> {
    // XPENDING key group start end count consumer
    const result = await this.redis.xpending(
      this.streamKey,
      this.config.consumerGroup,
      messageId,
      messageId,
      1
    );

    if (!result || result.length === 0) {
      return 0;
    }

    // result 格式: [[id, consumer, idle-time, delivery-count], ...]
    const [, , , deliveryCount] = result[0] as [string, string, number, number];
    return deliveryCount;
  }

  /**
   * 移动消息到 DLQ
   */
  private async moveToDlq(
    id: string,
    fields: string[],
    deliveryCount: number
  ): Promise<void> {
    const data = this.parseFields(fields);
    if (!data) {
      await this.ack(id);
      return;
    }

    const dlqType = this.streamKey.includes('inbound') ? 'inbound' : 'outbound';

    await this.producer.publishToDlq(
      dlqType,
      data,
      id,
      new Error(`Exceeded max retries (${this.config.maxRetries})`),
      deliveryCount
    );

    // ACK 原消息，从 Pending 中移除
    await this.ack(id);

    console.log(`Message ${id} moved to DLQ after ${deliveryCount} retries`);
  }

  /**
   * ACK 消息
   */
  async ack(messageId: string): Promise<void> {
    await this.redis.xack(
      this.streamKey,
      this.config.consumerGroup,
      messageId
    );
  }

  /**
   * 确保 Consumer Group 存在
   */
  private async ensureConsumerGroup(): Promise<void> {
    try {
      // XGROUP CREATE key groupname id [MKSTREAM]
      // 使用 '0' 从头开始消费，使用 '$' 只消费新消息
      await this.redis.xgroup(
        'CREATE',
        this.streamKey,
        this.config.consumerGroup,
        '0',
        'MKSTREAM' // 如果 stream 不存在则创建
      );
      console.log(
        `Consumer group created: ${this.config.consumerGroup} on ${this.streamKey}`
      );
    } catch (error: any) {
      // BUSYGROUP 错误表示 group 已存在，可以忽略
      if (error.message?.includes('BUSYGROUP')) {
        console.log(
          `Consumer group already exists: ${this.config.consumerGroup}`
        );
      } else {
        throw error;
      }
    }
  }

  /**
   * 解析 Redis Stream 字段
   */
  private parseFields(fields: string[]): InboundEvent | OutboundEvent | null {
    // fields 是 [field1, value1, field2, value2, ...] 格式
    for (let i = 0; i < fields.length; i += 2) {
      if (fields[i] === 'data') {
        try {
          return JSON.parse(fields[i + 1]);
        } catch {
          return null;
        }
      }
    }
    return null;
  }

  /**
   * 获取 Pending 消息列表（用于监控）
   */
  async getPendingMessages(count: number = 10): Promise<PendingMessage[]> {
    const result = await this.redis.xpending(
      this.streamKey,
      this.config.consumerGroup,
      '-',
      '+',
      count
    );

    if (!result || result.length === 0) {
      return [];
    }

    return (result as [string, string, number, number][]).map(
      ([id, consumer, idleTime, deliveryCount]) => ({
        id,
        consumer,
        idleTime,
        deliveryCount,
      })
    );
  }

  /**
   * 获取 Consumer Group 信息（用于监控）
   */
  async getConsumerGroupInfo(): Promise<{
    pending: number;
    consumers: number;
    lastDeliveredId: string;
  } | null> {
    try {
      const result = await this.redis.xinfo(
        'GROUPS',
        this.streamKey
      );

      if (!result || (result as unknown[]).length === 0) {
        return null;
      }

      // 找到当前 group 的信息
      for (const groupInfo of result as unknown[][]) {
        const infoMap = new Map<string, unknown>();
        for (let i = 0; i < groupInfo.length; i += 2) {
          infoMap.set(groupInfo[i] as string, groupInfo[i + 1]);
        }

        if (infoMap.get('name') === this.config.consumerGroup) {
          return {
            pending: infoMap.get('pending') as number ?? 0,
            consumers: infoMap.get('consumers') as number ?? 0,
            lastDeliveredId: infoMap.get('last-delivered-id') as string ?? '0',
          };
        }
      }

      return null;
    } catch {
      return null;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

/**
 * 创建 Inbound Consumer（Bot 使用）
 */
export function createInboundConsumer(
  lane: Lane,
  onMessage: MessageHandler<InboundEvent>,
  options?: Partial<StreamConfig>
): EventConsumer {
  return new EventConsumer({
    streamKey: STREAM_KEYS.inbound(lane),
    consumerGroup: CONSUMER_GROUPS.botWorkers(lane),
    onMessage: onMessage as MessageHandler<InboundEvent | OutboundEvent>,
    ...options,
  });
}

/**
 * 创建 Outbound Consumer（Server 使用）
 */
export function createOutboundConsumer(
  lane: Lane,
  onMessage: MessageHandler<OutboundEvent>,
  options?: Partial<StreamConfig>
): EventConsumer {
  return new EventConsumer({
    streamKey: STREAM_KEYS.outbound(lane),
    consumerGroup: CONSUMER_GROUPS.serverDispatchers(lane),
    onMessage: onMessage as MessageHandler<InboundEvent | OutboundEvent>,
    ...options,
  });
}
