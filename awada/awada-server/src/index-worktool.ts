/**
 * WorkTool 启动入口
 * 只启动 WorkTool 类型的 Bot
 */

require('dotenv').config();

import app from './app-worktool';
import { init as initConfig } from '@/config';
import { initializeBotManager } from './services/bot/manager';
import { BOT_CONFIGS } from '@/config/bots';
import { getRobotInfo, checkRobotOnline } from '@/services/worktool';
import { createLogger } from './utils/logger';
import worktoolConfig from '@/config/worktool';

const logger = createLogger('WorkTool-Main');
const PORT = process.env.WORKTOOL_PORT || 8089; // 使用不同端口

/** 启动 WorkTool Bot */
const startWorkToolBot = async () => {
  logger.info('🤖 WorkTool Bot 启动中...');

  // 只加载 WorkTool 类型的 Bot
  const worktoolBots = BOT_CONFIGS.filter((bot) => bot.type === 'worktool');

  if (worktoolBots.length === 0) {
    logger.warn('⚠️ 警告: 未配置任何 WorkTool Bot');
    logger.warn('请在 .env 文件中配置 BOT_1_TYPE=worktool、BOT_1_ID、BOT_1_DEVICE_GUID 等环境变量');
    return;
  }

  logger.info(`📋 检测到 ${worktoolBots.length} 个 WorkTool Bot 配置:`);
  for (const bot of worktoolBots) {
    logger.info(`  - ${bot.name || bot.botId} (${bot.botId}): robotId=${bot.deviceGuid}`);
  }

  // 初始化 Bot 管理器
  const botManager = initializeBotManager(worktoolBots);
  logger.info(`✅ WorkTool Bot 管理器已初始化，共 ${worktoolBots.length} 个 Bot`);

  // 检查每个 Bot 的状态
  logger.info('📋 开始检查 WorkTool Bot 状态...');
  const botStatusPromises = worktoolBots.map(async (botConfig) => {
    try {
      const robotId = botConfig.deviceGuid;

      // 获取机器人信息
      logger.info(`正在获取 Bot ${botConfig.botId} (robotId: ${robotId}) 的信息...`);
      const infoResponse = await getRobotInfo(robotId);

      if (infoResponse.code === 200 && infoResponse.data) {
        logger.info(`✅ Bot ${botConfig.botId} 信息:`);
        logger.info(`   - 名称: ${infoResponse.data.name}`);
        logger.info(`   - 机器人ID: ${infoResponse.data.robotId}`);
        logger.info(`   - 机器人类型: ${infoResponse.data.robotType === 0 ? '企业微信' : '微信'}`);
        logger.info(`   - 回调状态: ${infoResponse.data.openCallback === 1 ? '已开启' : '未开启'}`);

        // 检查在线状态
        const onlineResponse = await checkRobotOnline(robotId);
        if (onlineResponse.code === 200) {
          logger.info(`✅ Bot ${botConfig.botId} 在线状态检查完成`);
        }

        return { botId: botConfig.botId, success: true };
      } else {
        logger.warn(`⚠️ Bot ${botConfig.botId} 获取信息失败: ${infoResponse.message}`);
        return { botId: botConfig.botId, success: false, error: infoResponse.message };
      }
    } catch (error: any) {
      logger.error(`❌ Bot ${botConfig.botId} 检查异常:`, error.message);
      return { botId: botConfig.botId, success: false, error: error.message };
    }
  });

  const results = await Promise.all(botStatusPromises);
  const successCount = results.filter((r) => r.success).length;
  const failCount = results.filter((r) => !r.success).length;
  logger.info(`📋 WorkTool Bot 状态检查完成: 成功 ${successCount} 个，失败 ${failCount} 个`);

  if (failCount > 0) {
    logger.warn('⚠️ 部分 Bot 的状态检查失败');
    results
      .filter((r) => !r.success)
      .forEach((r) => {
        logger.warn(`  - Bot ${r.botId}: ${r.error}`);
      });
  }

  logger.info('✅ WorkTool Bot 启动完成');
};

/** 主函数 */
const main = async () => {
  try {
    // 初始化配置
    await initConfig();
    logger.info('✅ 配置加载完成');

    // 启动 WorkTool Bot
    await startWorkToolBot();

    // 启动 HTTP 服务（接收 Webhook）
    app.listen(PORT, () => {
      logger.info(`🚀 WorkTool 服务已启动: http://localhost:${PORT}`);
      logger.info(`📡 Webhook地址: ${worktoolConfig.callbackUrl}`);
    });

    logger.info('✅ WorkTool 服务启动完成');
  } catch (error) {
    logger.error('❌ 启动失败:', error);
    process.exit(1);
  }
};

// 启动
main();
