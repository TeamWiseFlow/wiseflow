/**
 * Conversation 映射管理器
 * 负责维护 (platform, user_id_external, channel_id) -> conversation_id 的映射
 * 根据 README.md 的要求，这个映射必须在 awada-server 端维护
 */

import Redis from 'ioredis';
import { STREAM_KEYS, Platform } from './types';
import { getRedisClient } from './connection';

export class ConversationManager {
  private redis: Redis;
  private ttlSeconds: number;

  constructor(ttlSeconds: number = 30 * 24 * 60 * 60, redis?: Redis) {
    // 默认 30 天过期
    this.redis = redis ?? getRedisClient();
    this.ttlSeconds = ttlSeconds;
  }

  /**
   * 获取 conversation_id
   * @returns conversation_id 如果存在，否则返回 null
   */
  async getConversationId(
    platform: Platform,
    userIdExternal: string,
    channelId: string
  ): Promise<string | null> {
    const key = STREAM_KEYS.conversationMapping(platform, userIdExternal, channelId);
    return this.redis.get(key);
  }

  /**
   * 设置 conversation_id
   * 当 Bot 返回 Outbound 事件时调用
   */
  async setConversationId(
    platform: Platform,
    userIdExternal: string,
    channelId: string,
    conversationId: string
  ): Promise<void> {
    const key = STREAM_KEYS.conversationMapping(platform, userIdExternal, channelId);
    await this.redis.set(key, conversationId, 'EX', this.ttlSeconds);
  }

  /**
   * 删除 conversation_id 映射
   * 用于会话重置场景
   */
  async deleteConversationId(
    platform: Platform,
    userIdExternal: string,
    channelId: string
  ): Promise<void> {
    const key = STREAM_KEYS.conversationMapping(platform, userIdExternal, channelId);
    await this.redis.del(key);
  }

  /**
   * 获取或创建 conversation_id
   * 如果不存在则生成新的
   */
  async getOrCreateConversationId(
    platform: Platform,
    userIdExternal: string,
    channelId: string,
    generator?: () => string
  ): Promise<{ conversationId: string; isNew: boolean }> {
    const existing = await this.getConversationId(platform, userIdExternal, channelId);

    if (existing) {
      return { conversationId: existing, isNew: false };
    }

    // 生成新的 conversation_id
    const newId = generator
      ? generator()
      : `conv_${platform}_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;

    await this.setConversationId(platform, userIdExternal, channelId, newId);

    return { conversationId: newId, isNew: true };
  }

  /**
   * 刷新 conversation 过期时间
   * 用于保持活跃会话不过期
   */
  async refreshTtl(
    platform: Platform,
    userIdExternal: string,
    channelId: string
  ): Promise<boolean> {
    const key = STREAM_KEYS.conversationMapping(platform, userIdExternal, channelId);
    const result = await this.redis.expire(key, this.ttlSeconds);
    return result === 1;
  }

  /**
   * 批量获取 conversation_id
   */
  async batchGetConversationIds(
    queries: Array<{
      platform: Platform;
      userIdExternal: string;
      channelId: string;
    }>
  ): Promise<Map<string, string | null>> {
    if (queries.length === 0) {
      return new Map();
    }

    const pipeline = this.redis.pipeline();
    const keys: string[] = [];

    for (const { platform, userIdExternal, channelId } of queries) {
      const key = STREAM_KEYS.conversationMapping(platform, userIdExternal, channelId);
      keys.push(key);
      pipeline.get(key);
    }

    const results = await pipeline.exec();
    const map = new Map<string, string | null>();

    if (results) {
      for (let i = 0; i < keys.length; i++) {
        const [err, value] = results[i];
        map.set(keys[i], err ? null : (value as string | null));
      }
    }

    return map;
  }
}

/**
 * 单例便捷函数
 */
let conversationManager: ConversationManager | null = null;

export function getConversationManager(ttlSeconds?: number): ConversationManager {
  if (!conversationManager) {
    conversationManager = new ConversationManager(ttlSeconds);
  }
  return conversationManager;
}
