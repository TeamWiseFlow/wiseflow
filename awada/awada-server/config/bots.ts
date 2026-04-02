/**
 * Bot 配置管理
 * 支持多个 Bot 实例，每个 Bot 有独立的 token 和 deviceGuid
 *
 * 环境变量格式（以 BOT_1_ 为前缀，可配置多个 Bot，序号从 1 开始）：
 *   BOT_1_TYPE=qiwe           # Bot 类型：qiwe | worktool
 *   BOT_1_ID=bot1             # Bot 唯一标识
 *   BOT_1_TOKEN=xxx           # QiweAPI Token（worktool 可留空）
 *   BOT_1_DEVICE_GUID=yyy     # 设备 GUID（worktool 填 robotId）
 *   BOT_1_LANES=user,admin    # 该 Bot 监听的 lanes，逗号分隔
 *   BOT_1_PLATFORM=qiwe:bot1  # 平台标识，用于 outbound 路由
 *   BOT_1_NAME=My Bot         # Bot 名称（可选）
 */

import { createLogger } from '../src/utils/logger';

const logger = createLogger('BotConfig');

export interface BotConfig {
  type: 'qiwe' | 'worktool';
  /** Bot 唯一标识 */
  botId: string;
  /** QiweAPI Token（worktool 可留空） */
  token: string;
  /** 设备 GUID（worktool 填 robotId） */
  deviceGuid: string;
  /** 该 Bot 监听的 lanes */
  lanes: string[];
  /** 平台标识 */
  platform: string;
  /** Bot 名称（可选） */
  name?: string;
  /** Bot 的 userId（wxid），启动时获取并缓存 */
  userId?: string;
}

/**
 * 从环境变量加载 Bot 配置
 * 按 BOT_1_*, BOT_2_*, ... 顺序读取，遇到第一个缺少必填项的序号时停止
 */
function loadBotConfigs(): BotConfig[] {
  const bots: BotConfig[] = [];

  for (let i = 1; ; i++) {
    const prefix = `BOT_${i}_`;
    const type = process.env[`${prefix}TYPE`] as 'qiwe' | 'worktool' | undefined;

    if (!type) {
      break; // 没有更多 Bot 配���
    }

    if (type !== 'qiwe' && type !== 'worktool') {
      logger.warn(`⚠️ Bot ${i}: 未知类型 "${type}"，跳过`);
      continue;
    }

    const botId = process.env[`${prefix}ID`];
    const deviceGuid = process.env[`${prefix}DEVICE_GUID`];
    const lanesRaw = process.env[`${prefix}LANES`] || 'user,admin';
    const platform = process.env[`${prefix}PLATFORM`] || `${type}:${botId || i}`;
    const token = process.env[`${prefix}TOKEN`] || '';
    const name = process.env[`${prefix}NAME`];

    if (!botId || !deviceGuid) {
      logger.warn(`⚠️ Bot ${i}: 缺少 ${prefix}ID 或 ${prefix}DEVICE_GUID，跳过`);
      continue;
    }

    const lanes = lanesRaw
      .split(',')
      .map((l) => l.trim())
      .filter(Boolean);

    bots.push({
      type,
      botId,
      token,
      deviceGuid,
      lanes,
      platform,
      ...(name ? { name } : {}),
    });

    logger.info(`✅ 加载 Bot 配置: ${botId} (type: ${type}, platform: ${platform}, lanes: ${lanes.join(', ')})`);
  }

  if (bots.length === 0) {
    logger.warn('⚠️ 未配置任何 Bot，请在 .env 文件中设置 BOT_1_TYPE、BOT_1_ID、BOT_1_DEVICE_GUID 等环境变量');
  }

  return bots;
}

/**
 * 所有 Bot 配置
 */
export const BOT_CONFIGS: BotConfig[] = loadBotConfigs();

/**
 * 导出配置加载函数，供测试使用
 */
export { loadBotConfigs };
