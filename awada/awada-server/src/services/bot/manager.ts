/**
 * Bot 管理器
 * 负责管理多个 Bot 实例的配置和路由
 */

import { BotConfig } from '@/config/bots';
import { createLogger } from '../../utils/logger';

const logger = createLogger('BotManager');

export class BotManager {
  private bots: Map<string, BotConfig> = new Map();
  private guidToBotId: Map<string, string> = new Map();

  constructor(configs: BotConfig[]) {
    configs.forEach(config => {
      this.bots.set(config.botId, config);
      this.guidToBotId.set(config.deviceGuid, config.botId);
      logger.info(`注册 Bot: ${config.botId} (guid: ${config.deviceGuid}, lanes: ${config.lanes.join(', ')})`);
    });
  }

  /**
   * 根据 GUID 获取 Bot 配置
   */
  getBotByGuid(guid: string): BotConfig | null {
    const botId = this.guidToBotId.get(guid);
    if (!botId) {
      return null;
    }
    return this.bots.get(botId) || null;
  }

  /**
   * 根据 Bot ID 获取配置
   */
  getBotById(botId: string): BotConfig | null {
    return this.bots.get(botId) || null;
  }

  /**
   * 获取所有 Bot 配置
   */
  getAllBots(): BotConfig[] {
    return Array.from(this.bots.values());
  }

  /**
   * 根据 lane 获取对应的 Bot 配置
   * 可能有多个 Bot 监听同一个 lane
   */
  getBotsByLane(lane: string): BotConfig[] {
    return Array.from(this.bots.values()).filter(bot => 
      bot.lanes.includes(lane as any)
    );
  }

  /**
   * 根据 platform 获取对应的 Bot 配置
   * platform 和 bot_id 一一对应
   */
  getBotByPlatform(platform: string): BotConfig | null {
    return Array.from(this.bots.values()).find(bot => bot.platform === platform) || null;
  }

  /**
   * 检查 GUID 是否已注册
   */
  hasGuid(guid: string): boolean {
    return this.guidToBotId.has(guid);
  }

  /**
   * 更新 Bot 的 userId
   */
  updateBotUserId(botId: string, userId: string): void {
    const bot = this.bots.get(botId);
    if (bot) {
      bot.userId = userId;
      logger.info(`更新 Bot ${botId} 的 userId: ${userId}`);
    }
  }

  /**
   * 获取 Bot 的 userId
   */
  getBotUserId(botId: string): string | null {
    const bot = this.bots.get(botId);
    return bot?.userId || null;
  }

  /**
   * 根据 deviceGuid 获取 Bot 的 userId
   */
  getUserIdByGuid(guid: string): string | null {
    const bot = this.getBotByGuid(guid);
    return bot?.userId || null;
  }
}

// 单例
let botManager: BotManager | null = null;

/**
 * 初始化 Bot 管理器
 */
export function initializeBotManager(configs: BotConfig[]): BotManager {
  botManager = new BotManager(configs);
  return botManager;
}

/**
 * 获取 Bot 管理器实例
 */
export function getBotManager(): BotManager {
  if (!botManager) {
    throw new Error('BotManager 未初始化，请先调用 initializeBotManager');
  }
  return botManager;
}

