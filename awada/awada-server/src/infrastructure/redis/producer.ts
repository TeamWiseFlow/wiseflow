/**
 * EventProducer - 事件生产者
 * 负责将事件写入 Redis Streams (XADD)
 */

import Redis from 'ioredis';
import { v4 as uuidv4 } from 'uuid';
import {
  InboundEvent,
  OutboundEvent,
  Lane,
  STREAM_KEYS,
  InboundMeta,
  Payload,
  InboundEventType,
  ContentObject,
} from './types';
import { getRedisClient } from './connection';
import { createLogger } from '../../utils/logger';

const logger = createLogger('EventProducer');

export class EventProducer {
  private redis: Redis;

  constructor(redis?: Redis) {
    this.redis = redis ?? getRedisClient();
  }

  /**
   * 发布 Inbound 事件（Server -> Bot）
   * @param event 完整的 Inbound 事件
   * @returns Redis Stream message ID
   */
  async publishInbound(event: InboundEvent): Promise<string> {
    const streamKey = STREAM_KEYS.inbound(event.meta.lane);
    return this.publish(streamKey, event);
  }

  /**
   * 发布 Outbound 事件（Bot -> Server）
   * @param event 完整的 Outbound 事件
   * @returns Redis Stream message ID
   */
  async publishOutbound(event: OutboundEvent): Promise<string> {
    const streamKey = STREAM_KEYS.outbound(event.target.lane);
    return this.publish(streamKey, event);
  }

  /**
   * 构建并发布 Inbound 事件的便捷方法
   * Server 端使用此方法将平台消息标准化后写入
   */
  async createAndPublishInbound(params: {
    type: InboundEventType;
    meta: Omit<InboundMeta, 'session_seq'>;
    payload: Payload;
    correlationId?: string;
    traceId?: string;
  }): Promise<{ eventId: string; streamId: string; sessionSeq: number }> {
    // 获取并递增 session_seq
    const sessionSeq = await this.incrementSessionSeq(params.meta.session_id);

    const event: InboundEvent = {
      schema_version: 1,
      event_id: `evt_${uuidv4()}`,
      type: params.type,
      timestamp: Math.floor(Date.now() / 1000),
      correlation_id: params.correlationId ?? `corr_${uuidv4()}`,
      trace_id: params.traceId ?? `trace_${uuidv4()}`,
      meta: {
        ...params.meta,
        session_seq: sessionSeq,
      },
      payload: params.payload,
    };

    const streamId = await this.publishInbound(event);

    return {
      eventId: event.event_id,
      streamId,
      sessionSeq,
    };
  }

  /**
   * 写入 DLQ
   */
  async publishToDlq(
    type: 'inbound' | 'outbound',
    originalEvent: InboundEvent | OutboundEvent,
    originalStreamId: string,
    error: Error,
    deliveryCount: number
  ): Promise<string> {
    const streamKey = type === 'inbound'
      ? STREAM_KEYS.inboundDlq()
      : STREAM_KEYS.outboundDlq();

    const dlqEntry = {
      originalEvent,
      originalStreamId,
      lastError: error.message,
      lastErrorAt: Math.floor(Date.now() / 1000),
      deliveryCount,
      movedToDlqAt: Math.floor(Date.now() / 1000),
    };

    return this.publish(streamKey, dlqEntry);
  }

  /**
   * 底层发布方法
   */
  private async publish(streamKey: string, data: object): Promise<string> {
    // Redis Streams 要求字段为 string
    // 我们将整个事件序列化为 JSON 存储在 'data' 字段中
    const messageId = await this.redis.xadd(
      streamKey,
      '*', // 自动生成 ID
      'data',
      JSON.stringify(data)
    );

    if (!messageId) {
      throw new Error(`Failed to publish to stream: ${streamKey}`);
    }

    // 清理 24 小时前的消息（符合 AWADA_SERVER_NOTICE.md 要求）
    // 使用异步方式，不阻塞发布流程
    this.trimOldMessages(streamKey).catch((err) => {
      console.warn(`[EventProducer] 清理旧消息失败 (${streamKey}):`, err);
    });

    return messageId;
  }

  /**
   * 清理 24 小时前的消息
   * 使用 XTRIM MINID 命令，保留最近 24 小时的消息
   */
  private async trimOldMessages(streamKey: string): Promise<void> {
    // 计算 24 小时前的时间戳（毫秒）
    const twentyFourHoursAgo = Date.now() - 24 * 60 * 60 * 1000;
    // 转换为 Redis Stream ID 格式：时间戳-0
    const minId = `${twentyFourHoursAgo}-0`;

    try {
      // 使用 XTRIM MINID ~ 清理旧消息
      // ~ 表示近似值，性能更好
      await this.redis.xtrim(streamKey, 'MINID', '~', minId);
    } catch (error) {
      // 忽略清理错误，不影响主流程
      console.warn(`[EventProducer] 清理 Stream ${streamKey} 失败:`, error);
    }
  }

  /**
   * 递增并获取 session_seq
   * 保证每个 session 的消息有序
   */
  private async incrementSessionSeq(sessionId: string): Promise<number> {
    const key = STREAM_KEYS.sessionSeq(sessionId);
    const seq = await this.redis.incr(key);

    // 设置过期时间（7天），避免无限增长
    // 只在 seq === 1 时设置，避免每次都重置 TTL
    if (seq === 1) {
      await this.redis.expire(key, 7 * 24 * 60 * 60);
    }

    return seq;
  }

  /**
   * 批量发布事件
   * 使用 pipeline 提升性能
   */
  async publishBatch(
    events: Array<{ streamKey: string; data: object }>
  ): Promise<string[]> {
    const pipeline = this.redis.pipeline();

    for (const { streamKey, data } of events) {
      pipeline.xadd(streamKey, '*', 'data', JSON.stringify(data));
    }

    const results = await pipeline.exec();

    if (!results) {
      throw new Error('Failed to execute pipeline');
    }

    return results.map(([err, id]) => {
      if (err) throw err;
      return id as string;
    });
  }

  /**
   * 获取 Stream 长度（用于监控）
   */
  async getStreamLength(streamKey: string): Promise<number> {
    return this.redis.xlen(streamKey);
  }

  /**
   * 获取 Stream 信息（用于监控）
   */
  async getStreamInfo(streamKey: string): Promise<{
    length: number;
    firstEntry: string | null;
    lastEntry: string | null;
  }> {
    const info = await this.redis.xinfo('STREAM', streamKey).catch(() => null);

    if (!info) {
      return { length: 0, firstEntry: null, lastEntry: null };
    }

    // xinfo 返回扁平数组，需要解析
    const infoMap = this.parseXinfoResult(info as unknown[]);

    return {
      length: infoMap.get('length') as number ?? 0,
      firstEntry: (infoMap.get('first-entry') as string[])?.[0] ?? null,
      lastEntry: (infoMap.get('last-entry') as string[])?.[0] ?? null,
    };
  }

  private parseXinfoResult(result: unknown[]): Map<string, unknown> {
    const map = new Map<string, unknown>();
    for (let i = 0; i < result.length; i += 2) {
      map.set(result[i] as string, result[i + 1]);
    }
    return map;
  }

  /**
   * 从 Redis Stream 中查询指定 session_id 的上一个文本消息
   * @param sessionId session ID
   * @param lane lane 名称
   * @returns 上一个文本消息的 ContentObject，如果找不到则返回 null
   */
  async getLastTextMessage(sessionId: string, lane: Lane): Promise<ContentObject | null> {
    try {
      const streamKey = STREAM_KEYS.inbound(lane);

      // 使用 XREVRANGE 从最新的消息开始往前查找，最多查找 100 条
      // XREVRANGE streamKey + - COUNT 100
      const messages = await this.redis.xrevrange(streamKey, '+', '-', 'COUNT', 20);

      if (!messages || messages.length === 0) {
        logger.debug(`📭 Redis Stream 中没有找到历史消息 (streamKey: ${streamKey})`);
        return null;
      }

      // 遍历消息，找到第一个匹配 session_id 且包含文本消息的事件
      for (const [messageId, fields] of messages) {
        // fields 格式: ['data', '{"schema_version":1,...}', ...]
        // 需要找到 'data' 字段
        let eventData: InboundEvent | null = null;
        for (let i = 0; i < fields.length; i += 2) {
          if (fields[i] === 'data') {
            try {
              eventData = JSON.parse(fields[i + 1] as string) as InboundEvent;
              break;
            } catch (e) {
              logger.warn(`解析 Redis 消息失败 (messageId: ${messageId}):`, e);
              continue;
            }
          }
        }

        if (!eventData) {
          continue;
        }

        // 检查 session_id 是否匹配
        if (eventData.meta?.session_id !== sessionId) {
          continue;
        }

        // 检查 payload 中是否有文本消息
        if (eventData.payload && Array.isArray(eventData.payload)) {
          // 从后往前查找文本消息（因为 payload 数组可能包含多个元素）
          for (let i = eventData.payload.length - 1; i >= 0; i--) {
            const content = eventData.payload[i];
            if (content.type === 'text' && content.text) {
              logger.debug(`✅ 找到上一个文本消息 (messageId: ${messageId}, text: ${content.text.substring(0, 30)}...)`);
              return content;
            }
          }
        }
      }

      logger.debug(`📭 未找到 session_id=${sessionId} 的上一个文本消息`);
      return null;
    } catch (error: any) {
      logger.error(`❌ 从 Redis 查询上一个文本消息失败:`, error);
      return null;
    }
  }
}
