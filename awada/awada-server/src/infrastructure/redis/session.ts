/**
 * Session 管理器
 * 负责 Session 锁和序号管理，确保同一 session 的消息按序处理
 */

import Redis from 'ioredis';
import { STREAM_KEYS } from './types';
import { getRedisClient } from './connection';

export interface SessionLockOptions {
  lockTimeoutMs: number; // 锁超时时间，默认 60000 (60s)
  renewIntervalMs: number; // 续租间隔，默认 20000 (20s)
}

const DEFAULT_LOCK_OPTIONS: SessionLockOptions = {
  lockTimeoutMs: 60000,
  renewIntervalMs: 20000
};

export class SessionManager {
  private redis: Redis;
  private lockOptions: SessionLockOptions;
  private renewTimers: Map<string, NodeJS.Timer> = new Map();
  private lockValues: Map<string, string> = new Map(); // sessionId -> lockValue

  constructor(options?: Partial<SessionLockOptions>, redis?: Redis) {
    this.redis = redis ?? getRedisClient();
    this.lockOptions = { ...DEFAULT_LOCK_OPTIONS, ...options };
  }

  /**
   * 获取 Session 锁
   * @returns lockValue 如果成功获取，null 如果已被其他 worker 持有
   */
  async acquireLock(sessionId: string): Promise<string | null> {
    const lockKey = STREAM_KEYS.sessionLock(sessionId);
    const lockValue = `${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2)}`;

    const result = await this.redis.set(lockKey, lockValue, 'PX', this.lockOptions.lockTimeoutMs, 'NX');

    if (result === 'OK') {
      this.lockValues.set(sessionId, lockValue);
      this.startRenew(sessionId, lockKey, lockValue);
      return lockValue;
    }

    return null;
  }

  /**
   * 释放 Session 锁
   * 使用 Lua 脚本确保只释放自己持有的锁
   */
  async releaseLock(sessionId: string): Promise<boolean> {
    const lockKey = STREAM_KEYS.sessionLock(sessionId);
    const lockValue = this.lockValues.get(sessionId);

    if (!lockValue) {
      return false;
    }

    // 停止续租
    this.stopRenew(sessionId);

    // Lua 脚本：只有当锁值匹配时才删除
    const script = `
      if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
      else
        return 0
      end
    `;

    const result = await this.redis.eval(script, 1, lockKey, lockValue);
    this.lockValues.delete(sessionId);

    return result === 1;
  }

  /**
   * 检查当前期望的序号
   */
  async getExpectedSeq(sessionId: string): Promise<number> {
    const key = STREAM_KEYS.sessionNextSeq(sessionId);
    const value = await this.redis.get(key);
    // 如果不存在，期望序号为 1
    return value ? parseInt(value, 10) : 1;
  }

  /**
   * 检查消息是否按序到达
   */
  async isInOrder(sessionId: string, messageSeq: number): Promise<boolean> {
    const expectedSeq = await this.getExpectedSeq(sessionId);
    return messageSeq === expectedSeq;
  }

  /**
   * 更新下一个期望序号
   * 只有在处理完消息后调用
   */
  async updateNextSeq(sessionId: string, processedSeq: number): Promise<void> {
    const key = STREAM_KEYS.sessionNextSeq(sessionId);
    await this.redis.set(key, (processedSeq + 1).toString());
    // 设置过期时间（7天）
    await this.redis.expire(key, 7 * 24 * 60 * 60);
  }

  /**
   * 完整的 Session 处理流程
   * 包含：获取锁 -> 检查顺序 -> 执行处理 -> 更新序号 -> 释放锁
   */
  async withSessionLock<T>(
    sessionId: string,
    messageSeq: number,
    handler: () => Promise<T>
  ): Promise<{
    success: boolean;
    result?: T;
    reason?: 'lock_failed' | 'out_of_order' | 'error';
    error?: Error;
  }> {
    // 1. 获取锁
    const lockValue = await this.acquireLock(sessionId);
    if (!lockValue) {
      return { success: false, reason: 'lock_failed' };
    }

    try {
      // 2. 检查顺序
      const inOrder = await this.isInOrder(sessionId, messageSeq);
      if (!inOrder) {
        return { success: false, reason: 'out_of_order' };
      }

      // 3. 执行处理
      const result = await handler();

      // 4. 更新序号
      await this.updateNextSeq(sessionId, messageSeq);

      return { success: true, result };
    } catch (error) {
      return { success: false, reason: 'error', error: error as Error };
    } finally {
      // 5. 释放锁
      await this.releaseLock(sessionId);
    }
  }

  /**
   * 开始锁续租
   */
  private startRenew(sessionId: string, lockKey: string, lockValue: string): void {
    const timer = setInterval(async () => {
      try {
        // Lua 脚本：只有当锁值匹配时才续租
        const script = `
          if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("pexpire", KEYS[1], ARGV[2])
          else
            return 0
          end
        `;

        const result = await this.redis.eval(script, 1, lockKey, lockValue, this.lockOptions.lockTimeoutMs.toString());

        if (result !== 1) {
          // 续租失败，锁已丢失
          console.warn(`Lock renewal failed for session ${sessionId}`);
          this.stopRenew(sessionId);
        }
      } catch (error) {
        console.error(`Error renewing lock for session ${sessionId}:`, error);
      }
    }, this.lockOptions.renewIntervalMs);

    this.renewTimers.set(sessionId, timer);
  }

  /**
   * 停止锁续租
   */
  private stopRenew(sessionId: string): void {
    const timer = this.renewTimers.get(sessionId);
    if (timer) {
      clearInterval(Number(timer));
      this.renewTimers.delete(sessionId);
    }
  }

  /**
   * 清理所有续租定时器（用于优雅关闭）
   */
  async cleanup(): Promise<void> {
    for (const [sessionId] of this.renewTimers) {
      await this.releaseLock(sessionId);
    }
    this.renewTimers.clear();
    this.lockValues.clear();
  }
}

/**
 * 单例便捷函数
 */
let sessionManager: SessionManager | null = null;

export function getSessionManager(options?: Partial<SessionLockOptions>): SessionManager {
  if (!sessionManager) {
    sessionManager = new SessionManager(options);
  }
  return sessionManager;
}
