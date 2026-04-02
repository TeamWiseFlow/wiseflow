/**
 * Redis 连接管理器
 * 单例模式，支持连接池
 */

import Redis, { RedisOptions } from 'ioredis';
import { RedisConfig } from './types';
import { createLogger } from '../../utils/logger';

const logger = createLogger('Redis');

export class RedisConnection {
  private static instance: RedisConnection;
  private client: Redis | null = null;
  private subscriber: Redis | null = null; // 用于订阅的独立连接
  private config: RedisConfig;

  private constructor(config: RedisConfig) {
    this.config = config;
  }

  /**
   * 获取单例实例
   */
  static getInstance(config?: RedisConfig): RedisConnection {
    if (!RedisConnection.instance) {
      if (!config) {
        throw new Error('RedisConnection must be initialized with config first');
      }
      RedisConnection.instance = new RedisConnection(config);
    }
    return RedisConnection.instance;
  }

  /**
   * 初始化连接（支持依赖注入测试）
   */
  static initialize(config: RedisConfig): RedisConnection {
    RedisConnection.instance = new RedisConnection(config);
    return RedisConnection.instance;
  }

  /**
   * 重置实例（仅用于测试）
   */
  static reset(): void {
    if (RedisConnection.instance) {
      RedisConnection.instance.disconnect();
      RedisConnection.instance = null as any;
    }
  }

  /**
   * 获取主 Redis 客户端
   */
  getClient(): Redis {
    if (!this.client) {
      this.client = this.createClient();
    }
    return this.client;
  }

  /**
   * 获取订阅专用客户端
   * Redis 订阅需要独立连接
   */
  getSubscriber(): Redis {
    if (!this.subscriber) {
      this.subscriber = this.createClient();
    }
    return this.subscriber;
  }

  /**
   * 创建新的 Redis 客户端
   * 用于需要独立连接的场景（如 blocking 操作）
   */
  createClient(): Redis {
    const options: RedisOptions = {
      host: this.config.host,
      port: this.config.port,
      password: this.config.password,
      db: this.config.db ?? 0,
      keyPrefix: this.config.keyPrefix,
      retryStrategy: (times: number) => {
        // 指数退避重试，最大延迟 30 秒
        const delay = Math.min(times * 100, 30000);
        logger.debug(`连接重试 #${times}, 延迟: ${delay}ms`);
        return delay;
      },
      maxRetriesPerRequest: 3,
      enableReadyCheck: true,
      lazyConnect: false
    };

    const client = new Redis(options);

    client.on('connect', () => {
      logger.info('Redis 连接成功');
    });

    client.on('error', (err) => {
      logger.error('Redis 错误:', err);
    });

    client.on('close', () => {
      logger.info('Redis 连接已关闭');
    });

    return client;
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<boolean> {
    try {
      const client = this.getClient();
      const result = await client.ping();
      return result === 'PONG';
    } catch (error) {
      logger.error('Redis 健康检查失败:', error);
      return false;
    }
  }

  /**
   * 关闭所有连接
   */
  async disconnect(): Promise<void> {
    const promises: Promise<void>[] = [];

    if (this.client) {
      promises.push(
        this.client.quit().then(() => {
          this.client = null;
        })
      );
    }

    if (this.subscriber) {
      promises.push(
        this.subscriber.quit().then(() => {
          this.subscriber = null;
        })
      );
    }

    await Promise.all(promises);
    logger.info('Redis 连接已关闭');
  }
}

/**
 * 便捷函数：获取 Redis 客户端
 */
export function getRedisClient(): Redis {
  return RedisConnection.getInstance().getClient();
}

/**
 * 便捷函数：创建新的 Redis 客户端
 */
export function createRedisClient(): Redis {
  return RedisConnection.getInstance().createClient();
}
