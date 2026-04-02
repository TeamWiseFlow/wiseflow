/**
 * 幂等性管理器
 * 确保消息只被处理一次（At-least-once 语义下的去重）
 */

import Redis from 'ioredis';
import { STREAM_KEYS } from './types';
import { getRedisClient } from './connection';

export class IdempotencyManager {
  private redis: Redis;
  private ttlSeconds: number;

  constructor(ttlSeconds: number = 86400, redis?: Redis) {
    this.redis = redis ?? getRedisClient();
    this.ttlSeconds = ttlSeconds;
  }

  /**
   * 检查事件是否已处理
   * @returns true 如果事件已被处理过
   */
  async isProcessed(eventId: string): Promise<boolean> {
    const key = STREAM_KEYS.processed(eventId);
    const result = await this.redis.exists(key);
    return result === 1;
  }

  /**
   * 标记事件为已处理
   * 使用 SETNX 确保原子性
   * @returns true 如果成功标记（之前未处理），false 如果已被其他 worker 处理
   */
  async markAsProcessed(eventId: string): Promise<boolean> {
    const key = STREAM_KEYS.processed(eventId);
    // SETNX + EXPIRE 原子操作
    const result = await this.redis.set(key, '1', 'EX', this.ttlSeconds, 'NX');
    return result === 'OK';
  }

  /**
   * 尝试获取处理权
   * 结合检查和标记的原子操作
   * @returns true 如果获得处理权，false 如果事件已被处理
   */
  async tryAcquire(eventId: string): Promise<boolean> {
    return this.markAsProcessed(eventId);
  }

  /**
   * 移除处理标记（用于需要重试的场景）
   */
  async removeProcessedMark(eventId: string): Promise<void> {
    const key = STREAM_KEYS.processed(eventId);
    await this.redis.del(key);
  }

  /**
   * 批量检查事件是否已处理
   */
  async areProcessed(eventIds: string[]): Promise<Map<string, boolean>> {
    if (eventIds.length === 0) {
      return new Map();
    }

    const pipeline = this.redis.pipeline();
    for (const eventId of eventIds) {
      pipeline.exists(STREAM_KEYS.processed(eventId));
    }

    const results = await pipeline.exec();
    const map = new Map<string, boolean>();

    if (results) {
      for (let i = 0; i < eventIds.length; i++) {
        const [err, result] = results[i];
        map.set(eventIds[i], !err && result === 1);
      }
    }

    return map;
  }

  /**
   * 创建带幂等检查的处理包装器
   * 简化业务代码中的幂等处理
   */
  createIdempotentHandler<T>(
    handler: (data: T) => Promise<void>,
    getEventId: (data: T) => string
  ): (data: T) => Promise<{ processed: boolean; skipped: boolean }> {
    return async (data: T) => {
      const eventId = getEventId(data);

      // 尝试获取处理权
      const acquired = await this.tryAcquire(eventId);

      if (!acquired) {
        // 已被处理，跳过
        return { processed: false, skipped: true };
      }

      try {
        await handler(data);
        return { processed: true, skipped: false };
      } catch (error) {
        // 处理失败，移除标记以便重试
        await this.removeProcessedMark(eventId);
        throw error;
      }
    };
  }
}

/**
 * 单例便捷函数
 */
let idempotencyManager: IdempotencyManager | null = null;

export function getIdempotencyManager(ttlSeconds?: number): IdempotencyManager {
  if (!idempotencyManager) {
    idempotencyManager = new IdempotencyManager(ttlSeconds);
  }
  return idempotencyManager;
}
