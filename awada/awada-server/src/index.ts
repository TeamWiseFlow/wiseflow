/**
 * awada-server 主入口文件
 * 基于 qiweapi 的微信智能机器人
 *
 * qiweapi 文档: https://doc.qiweapi.com/
 */

require('dotenv').config();

import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import * as qrcode from 'qrcode-terminal';
import app from './app';
import CONFIG, { init as initConfig } from '@/config';
// import qiweapiConfig from '@/config/qiweapi'; // 已移除，现在使用 Bot 配置
// import { createClient, recoverClient, setCallbackUrl, getLoginQrcode, checkLogin, verifyQrCode, LoginStatus } from '@/services/qiweapi'; // 登录逻辑暂时注释
import { RedisConnection } from './infrastructure/redis';
import { startOutboundConsumers, stopOutboundConsumers } from './services/outbound';
import { Lane } from './infrastructure/redis/types';
import { createLogger } from './utils/logger';
import { initializeBotManager, getBotManager } from './services/bot/manager';
import { BOT_CONFIGS } from '@/config/bots';
import { getUserStatus } from '@/services/qiweapi/login';
import { getRobotInfo, checkRobotOnline, setCallback } from '@/services/worktool';
import worktoolConfig from '@/config/worktool';

const logger = createLogger('Main');
const botLogger = createLogger('Bot');
const qrcodeLogger = createLogger('QRCode');

const PORT = process.env.PORT || 8088;

/** 二维码图片保存路径 */
const QRCODE_IMAGE_PATH = path.join(process.cwd(), 'qrcode.png');

/** 从 base64 图片中解码二维码内容 */
const decodeQrcodeFromBase64 = async (base64Data: string): Promise<string | null> => {
  try {
    // 动态导入，避免在服务器环境下的依赖问题
    let Jimp: any;
    try {
      Jimp = (await import('jimp')).default;
    } catch {
      Jimp = require('jimp');
    }

    const jsQR = require('jsqr');

    // 移除可能的 data:image 前缀
    const pureBase64 = base64Data.replace(/^data:image\/\w+;base64,/, '');
    const imageBuffer = Buffer.from(pureBase64, 'base64');

    // 使用 Jimp 读取图片（兼容不同的导入方式）
    const image = Jimp.default ? await Jimp.default.read(imageBuffer) : await Jimp.read(imageBuffer);
    const { width, height, data } = image.bitmap;

    // 使用 jsQR 解码二维码
    const code = jsQR(new Uint8ClampedArray(data), width, height);

    if (code) {
      return code.data;
    }
    return null;
  } catch (err) {
    // 静默失败，不打印错误（因为这是备选方案，URL 方式优先）
    return null;
  }
};

/** 在控制台显示二维码 */
const displayQrcode = async (base64Data: string) => {
  qrcodeLogger.info('\n');
  qrcodeLogger.info('╔════════════════════════════════════════════════════════╗');
  qrcodeLogger.info('║           📱 请使用企业微信扫描二维码登录 📱           ║');
  qrcodeLogger.info('╚════════════════════════════════════════════════════════╝');
  qrcodeLogger.info('\n');

  // 如果是 URL，直接生成终端二维码
  if (base64Data.startsWith('http')) {
    qrcode.generate(base64Data, { small: true });
    qrcodeLogger.info(`\n二维码URL: ${base64Data}`);
  } else {
    // 尝试从 base64 图片中解码二维码内容
    qrcodeLogger.info('正在解析二维码...');
    const qrcodeContent = await decodeQrcodeFromBase64(base64Data);

    if (qrcodeContent) {
      // 成功解码，在终端显示二维码
      qrcodeLogger.info('✅ 二维码解析成功!\n');
      qrcode.generate(qrcodeContent, { small: true });
      qrcodeLogger.info(`\n内容: ${qrcodeContent.substring(0, 50)}...`);
    } else {
      // 解码失败，保存为图片文件
      qrcodeLogger.warn('⚠️ 无法在终端显示，保存为图片...');
      try {
        const pureBase64 = base64Data.replace(/^data:image\/\w+;base64,/, '');
        const imageBuffer = Buffer.from(pureBase64, 'base64');
        fs.writeFileSync(QRCODE_IMAGE_PATH, imageBuffer);

        qrcodeLogger.info(`📁 图片已保存: ${QRCODE_IMAGE_PATH}`);
        qrcodeLogger.info(`🌐 或访问: http://localhost:${PORT}/api/qrcode/image`);

        // 尝试自动打开图片（macOS）
        const { exec } = require('child_process');
        exec(`open "${QRCODE_IMAGE_PATH}"`);
      } catch (err) {
        qrcodeLogger.error('❌ 保存图片失败:', err);
      }
    }
  }

  qrcodeLogger.info('\n');
  qrcodeLogger.info('💡 提示: 扫码后请在手机上确认登录');
  qrcodeLogger.info('💡 如需验证码，请调用 POST /api/login/verify 接口');
  qrcodeLogger.info('\n');
};

/** 启动机器人（登录逻辑已注释，使用手动创建的 GUID） */
const startBot = async () => {
  botLogger.info('🤖🤖🤖 awada-server 启动中... 🤖🤖🤖');

  // 获取所有 Bot 配置
  const botManager = getBotManager();
  const bots = botManager.getAllBots();

  if (bots.length === 0) {
    botLogger.warn('⚠️ 警告: 未配置任何 Bot');
    botLogger.warn('请在 .env 文件中配置 Bot 的 TOKEN 和 DEVICE_GUID');
    return;
  }

  botLogger.info(`📋 检测到 ${bots.length} 个 Bot 配置:`);
  for (const bot of bots) {
    botLogger.info(`  - ${bot.name} (${bot.botId}): platform=${bot.platform}, guid=${bot.deviceGuid ? '已配置' : '未配置'}`);
  }

  // 登录逻辑暂时注释，使用手动创建的 GUID
  /*
  // 1. 如果有实例ID，先检查登录状态（避免不必要的恢复/创建流程）
  if (botConfig.deviceGuid) {
    botLogger.info(`检测到已有设备GUID: ${botConfig.deviceGuid}`);
    botLogger.info('先检查实例登录状态...');

    const statusResult = await checkLogin(botConfig.deviceGuid);

    if (statusResult.code === 0 && statusResult.data) {
      const status = statusResult.data.loginQrcodeStatus;

      if (status === LoginStatus.SUCCESS) {
        botLogger.info('\n');
        botLogger.info('╔════════════════════════════════════════════════════════╗');
        botLogger.info('║              ✅ 实例已登录，无需重新登录 ✅            ║');
        botLogger.info('╚════════════════════════════════════════════════════════╝');
        botLogger.info(`👤 用户: ${statusResult.data.nickname} (${statusResult.data.userId})`);
        botLogger.info(`🏢 企业: ${statusResult.data.corpId || 'N/A'}`);
        botLogger.info('\n');
        return; // 已登录，直接返回，不需要走后续流程
      }

      botLogger.info(`当前登录状态: ${status}，需要重新登录`);
    } else {
      // 检查失败，可能是实例不存在或已过期，继续走恢复/创建流程
      botLogger.warn(`⚠️ 检查登录状态失败: ${statusResult.msg}`);
      botLogger.info('将尝试恢复或重新创建实例...');
    }
  }

  // 2. 恢复或创建设备实例
  let deviceReady = false;

  if (botConfig.deviceGuid) {
    botLogger.info('尝试恢复实例...');
    const recoverResult = await recoverClient(botConfig.deviceGuid);

    if (recoverResult.code === 0) {
      botLogger.info('✅ 实例恢复成功');
      deviceReady = true;
    } else {
      botLogger.warn('⚠️ 实例恢复失败:', recoverResult.msg);
      botLogger.info('💡 将创建新设备实例...');
    }
  }

  // 如果没有设备或恢复失败，创建新设备
  if (!deviceReady) {
    botLogger.info('创建新设备实例...');
    const createResult = await createClient({
      deviceName: CONFIG.name || 'chatbot-new'
    });

    if (createResult.code === 0 && createResult.data?.guid) {
      botLogger.info('✅ 设备创建成功');
      botLogger.info(`📝 新设备GUID: ${createResult.data.guid}`);
      botLogger.info('💡 建议将此GUID保存到 .env 文件的 QIWEAPI_DEVICE_GUID 中');
      deviceReady = true;
    } else {
      botLogger.error('❌ 创建设备失败:', createResult.msg);
      botLogger.info('💡 如需登录，请调用 GET /api/qrcode');
      return;
    }
  }

  // 3. 设置回调地址
  // if (qiweapiConfig.callbackUrl) {
  //     console.log("[Bot] 设置回调地址...");
  //     await setCallbackUrl(qiweapiConfig.callbackUrl);
  // }

  // 4. 再次检查登录状态（恢复/创建后可能已经登录）
  botLogger.info('检查当前登录状态...');
  const statusResult = await checkLogin(botConfig.deviceGuid);

  if (statusResult.code === 0 && statusResult.data) {
    const status = statusResult.data.loginQrcodeStatus;

    if (status === LoginStatus.SUCCESS) {
      botLogger.info(`✅ 已登录: ${statusResult.data.nickname} (${statusResult.data.userId})`);
      return;
    }

    botLogger.info(`当前状态: ${status}`);
  }

  // 4. 获取并显示登录二维码
  const qrcodeInfo = await fetchAndDisplayQrcode(botConfig);
  if (!qrcodeInfo) {
    return;
  }

  // 5. 开始轮询登录状态
  botLogger.info('开始监听登录状态...');
  await pollLoginStatus(botConfig);
  */

  botLogger.info('✅ Bot 启动完成（使用手动创建的 GUID，登录逻辑已注释）');
};

/** 获取并显示登录二维码（已注释） */
/*
const fetchAndDisplayQrcode = async (botConfig: BotConfig): Promise<{ qrcodeKey: string } | null> => {
  botLogger.info('获取登录二维码...');
  const qrcodeResult = await getLoginQrcode({ guid: botConfig.deviceGuid, useCache: false });

  if (qrcodeResult.code !== 0 || !qrcodeResult.data) {
    botLogger.error('❌ 获取二维码失败:', qrcodeResult.msg);
    botLogger.info('💡 可以手动调用 GET /api/qrcode 获取二维码');
    return null;
  }

  // 显示二维码
  const qrcodeKey = qrcodeResult.data.loginQrcodeKey;
  const qrcodeBase64 = qrcodeResult.data.loginQrcodeBase64Data;

  // 优先使用 qrUrl（如果 API 返回了），否则从 loginQrcodeKey 构建二维码 URL
  // 二维码 URL 格式: https://wx.work.weixin.qq.com/cgi-bin/crtx_auth?key={key}&wx=1
  const qrcodeUrl = (qrcodeResult.data as any).qrUrl || (qrcodeKey ? `https://wx.work.weixin.qq.com/cgi-bin/crtx_auth?key=${qrcodeKey}&wx=1` : null);

  if (qrcodeUrl) {
    // 优先使用 URL 方式显示（不需要依赖 Jimp，服务器环境友好）
    await displayQrcode(qrcodeUrl);
  } else if (qrcodeBase64) {
    // 如果没有 URL，尝试使用 base64 图片
    await displayQrcode(qrcodeBase64);
  } else {
    botLogger.info('📱 被动确认模式，请在手机端确认登录');
  }

  botLogger.info(`🔑 QrcodeKey: ${qrcodeKey}`);

  return { qrcodeKey };
};
*/

/** 轮询登录状态（已注释） */
/*
const pollLoginStatus = async (botConfig: BotConfig) => {
  const maxAttempts = 90; // 最多轮询90次（约3分钟）
  const interval = 2000; // 每2秒检查一次

  let lastStatus: number | null = null;
  let needCodeHandled = false;
  let consecutiveErrors = 0; // 连续错误计数
  const maxConsecutiveErrors = 3; // 最多连续3次错误后处理

  for (let i = 0; i < maxAttempts; i++) {
    await sleep(interval);

    const result = await checkLogin(botConfig.deviceGuid);

    // 处理错误情况
    if (result.code !== 0 || !result.data) {
      consecutiveErrors++;
      const errorMsg = result.msg || '';

      // 检查是否是二维码过期或设备异常的错误（立即处理，不等待）
      const isExpiredError = errorMsg.includes('expired') || errorMsg.includes('过期') || errorMsg.includes('get expired data empty') || errorMsg.includes('交互异常') || errorMsg.includes('WxErrorCode') || (result.code === 422100 && errorMsg.includes('底层流程错误'));

      if (isExpiredError) {
        botLogger.info('\n');
        botLogger.info('╔════════════════════════════════════════════════════════╗');
        botLogger.info('║         ⚠️  二维码过期或设备异常 ⚠️                  ║');
        botLogger.info('╚════════════════════════════════════════════════════════╝');
        botLogger.info(`错误代码: ${result.code}`);
        botLogger.info(`错误信息: ${errorMsg}`);
        botLogger.info('\n🔄 自动重新获取二维码...\n');

        // 自动重新获取二维码
        const newQrcodeInfo = await fetchAndDisplayQrcode(botConfig);
        if (!newQrcodeInfo) {
          botLogger.error('❌ 重新获取二维码失败，请检查设备状态');
          return;
        }

        // 重置状态，继续轮询
        lastStatus = null;
        needCodeHandled = false;
        consecutiveErrors = 0;
        botLogger.info('✅ 已重新获取二维码，继续监听登录状态...\n');
        continue;
      }

      // 如果是其他错误，继续尝试（可能是临时网络问题）
      if (consecutiveErrors >= maxConsecutiveErrors) {
        botLogger.warn(`⚠️ 连续 ${consecutiveErrors} 次检查失败，可能存在问题`);
        botLogger.warn(`错误代码: ${result.code}, 错误信息: ${errorMsg}`);
        botLogger.warn('继续尝试中...');
      }

      continue;
    }

    // 重置错误计数
    consecutiveErrors = 0;

    const status = result.data.loginQrcodeStatus;

    // 状态变化时打印
    if (status !== lastStatus) {
      lastStatus = status;

      switch (status) {
        case LoginStatus.INVALID:
          botLogger.warn('⚠️ 登录状态失效，需要重新扫码');
          return;
        case LoginStatus.NOT_LOGGED_IN:
          botLogger.info('⏳ 等待扫码...');
          needCodeHandled = false;
          break;
        case LoginStatus.SCANNED:
          botLogger.info('📱 已扫码，请在手机上确认...');
          break;
        case LoginStatus.SUCCESS:
          botLogger.info('\n');
          botLogger.info('╔════════════════════════════════════════════════════════╗');
          botLogger.info('║                   ✅ 登录成功! ✅                      ║');
          botLogger.info('╚════════════════════════════════════════════════════════╝');
          botLogger.info(`👤 用户: ${result.data.nickname} (${result.data.userId})`);
          botLogger.info('\n');
          return;
        case LoginStatus.FAILED:
          botLogger.error('❌ 登录失败');
          return;
        case LoginStatus.CANCELLED:
          botLogger.error('❌ 用户取消登录');
          return;
        case LoginStatus.NEED_CODE:
          if (!needCodeHandled) {
            needCodeHandled = true;
            // 处理验证码输入
            const verified = await handleVerifyCode(botConfig);
            if (verified) {
              // 验证成功后，立即检查登录状态（不等待下一次轮询）
              botLogger.info('🔄 验证码验证成功，立即检查登录状态...');
              await sleep(500); // 短暂等待，确保服务端状态更新

              const checkResult = await checkLogin(botConfig.deviceGuid);
              if (checkResult.code === 0 && checkResult.data) {
                const newStatus = checkResult.data.loginQrcodeStatus;

                if (newStatus === LoginStatus.SUCCESS) {
                  // 登录成功
                  botLogger.info('\n');
                  botLogger.info('╔════════════════════════════════════════════════════════╗');
                  botLogger.info('║                   ✅ 登录成功! ✅                      ║');
                  botLogger.info('╚════════════════════════════════════════════════════════╝');
                  botLogger.info(`👤 用户: ${checkResult.data.nickname} (${checkResult.data.userId})`);
                  botLogger.info('\n');
                  return;
                } else if (newStatus === LoginStatus.NEED_CODE) {
                  // 还是需要验证码，重置状态继续轮询
                  botLogger.warn('⚠️ 验证码验证成功，但状态仍未更新，继续等待...');
                  lastStatus = null;
                  needCodeHandled = false; // 允许再次处理
                } else {
                  // 其他状态，重置继续轮询
                  lastStatus = null;
                }
              } else {
                // 检查失败，重置状态继续轮询
                botLogger.warn('⚠️ 检查登录状态失败，继续轮询...');
                lastStatus = null;
              }
            } else {
              // 验证失败，允许重试
              const retry = await readInput('[Bot] 是否重试? (y/n): ');
              if (retry.toLowerCase() === 'y') {
                needCodeHandled = false;
                lastStatus = null;
              } else {
                return;
              }
            }
          }
          break;
      }
    }
  }

  botLogger.warn('⏰ 登录超时，请重新获取二维码');
};
*/

/** 辅助函数：延时 */
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** 从控制台读取输入 */
const readInput = (prompt: string): Promise<string> => {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
};

/** 处理验证码输入（已注释） */
/*
const handleVerifyCode = async (botConfig: BotConfig): Promise<boolean> => {
  botLogger.info('\n');
  botLogger.info('╔════════════════════════════════════════════════════════╗');
  botLogger.info('║              🔢 需要输入6位验证码 🔢                   ║');
  botLogger.info('╚════════════════════════════════════════════════════════╝');
  botLogger.info('\n');

  const code = await readInput('[Bot] 请输入6位验证码: ');

  if (!code || code.length !== 6) {
    botLogger.error('❌ 验证码格式错误，请输入6位数字');
    return false;
  }

  botLogger.info(`正在验证: ${code}`);
  const result = await verifyQrCode(code, botConfig.deviceGuid);

  if (result.code === 0) {
    botLogger.info('✅ 验证码验证成功!');
    return true;
  } else {
    botLogger.error(`❌ 验证码验证失败: ${result.msg}`);
    return false;
  }
};
*/

/** 主函数 */
const main = async () => {
  try {
    // 初始化配置
    await initConfig();
    logger.info('✅ 配置加载完成');
    const qiweBots = BOT_CONFIGS.filter((bot) => bot.type === 'qiwe');
    const worktoolBots = BOT_CONFIGS.filter((bot) => bot.type === 'worktool');

    // 初始化 Bot 管理器（多 Bot 支持，包含所有类型的 Bot）
    const botManager = initializeBotManager(BOT_CONFIGS);
    logger.info(`✅ Bot 管理器已初始化，共 ${BOT_CONFIGS.length} 个 Bot (QiweAPI: ${qiweBots.length}, WorkTool: ${worktoolBots.length})`);

    // 启动时获取所有 Bot 的 userId 并缓存
    logger.info('📋 开始获取所有 Bot 的 userId...');
    const botUserIdPromises = qiweBots.map(async (botConfig) => {
      try {
        logger.info(`正在获取 Bot ${botConfig.botId} (${botConfig.name || botConfig.botId}) 的 userId...`);
        const response = await getUserStatus(botConfig.deviceGuid, botConfig.token);
        if (response.code === 0 && response.data?.wxid) {
          botManager.updateBotUserId(botConfig.botId, response.data.wxid);
          logger.info(`✅ Bot ${botConfig.botId} 的 userId: ${response.data.wxid}`);
          return { botId: botConfig.botId, userId: response.data.wxid, success: true };
        } else {
          logger.warn(`⚠️ Bot ${botConfig.botId} 获取 userId 失败: ${response.msg}`);
          return { botId: botConfig.botId, success: false, error: response.msg };
        }
      } catch (error: any) {
        logger.error(`❌ Bot ${botConfig.botId} 获取 userId 异常:`, error.message);
        return { botId: botConfig.botId, success: false, error: error.message };
      }
    });

    const results = await Promise.all(botUserIdPromises);
    const successCount = results.filter((r) => r.success).length;
    const failCount = results.filter((r) => !r.success).length;
    logger.info(`📋 Bot userId 获取完成: 成功 ${successCount} 个，失败 ${failCount} 个`);

    if (failCount > 0) {
      logger.warn('⚠️ 部分 Bot 的 userId 获取失败，可能会影响 @ 检测功能');
      results
        .filter((r) => !r.success)
        .forEach((r) => {
          logger.warn(`  - Bot ${r.botId}: ${r.error}`);
        });
    }

    // 初始化 Redis 连接
    const REDIS_CONFIG = {
      host: process.env.REDIS_HOST ?? 'localhost',
      port: parseInt(process.env.REDIS_PORT ?? '6379', 10),
      password: process.env.REDIS_PASSWORD
    };

    RedisConnection.initialize(REDIS_CONFIG);

    // 检查 Redis 连接健康状态
    const redisHealthy = await RedisConnection.getInstance().healthCheck();
    if (redisHealthy) {
      logger.info('✅ Redis 连接成功');
    } else {
      logger.warn('⚠️ Redis 连接检查失败，但继续启动');
    }

    // 启动HTTP服务（先启动服务，确保回调接口可访问）
    await new Promise<void>((resolve) => {
      app.listen(PORT, () => {
        logger.info(`🚀 服务已启动: http://localhost:${PORT}`);
        logger.info(`📡 QiweAPI Webhook地址: http://localhost:${PORT}/webhook`);
        logger.info(`📡 WorkTool Webhook地址: http://localhost:${PORT}/webhook_worktool`);
        logger.info(`🔧 API地址: http://localhost:${PORT}/api`);
        resolve();
      });
    });

    // 启动 WorkTool Bot（如果配置了）- 在 HTTP 服务启动后设置回调
    if (worktoolBots.length > 0) {
      logger.info('🤖 开始启动 WorkTool Bot...');
      const worktoolStatusPromises = worktoolBots.map(async (botConfig) => {
        try {
          const robotId = botConfig.deviceGuid;
          logger.info(`正在获取 WorkTool Bot ${botConfig.botId} (robotId: ${robotId}) 的信息...`);
          const infoResponse = await getRobotInfo(robotId);

          if (infoResponse.code === 200 && infoResponse.data) {
            logger.info(`✅ WorkTool Bot ${botConfig.botId} 信息:`);
            logger.info(`   - 名称: ${infoResponse.data.name}`);
            logger.info(`   - 机器人ID: ${infoResponse.data.robotId}`);
            logger.info(`   - 机器人类型: ${infoResponse.data.robotType === 0 ? '企业微信' : '微信'}`);
            logger.info(`   - 回调状态: ${infoResponse.data.openCallback === 1 ? '已开启' : '未开启'}`);

            // 构建回调地址：优先使用配置的地址，否则使用默认地址
            const callbackUrl = worktoolConfig.callbackUrl || `${process.env.CALLBACK_BASE_URL}`;

            if (!callbackUrl || callbackUrl === '/webhook_worktool') {
              logger.error(`❌ 回调地址未配置，请在 .env 文件中配置 WORKTOOL_CALLBACK_URL 或 CALLBACK_BASE_URL`);
              return { botId: botConfig.botId, success: false, error: '回调地址未配置' };
            }

            // 如果回调未开启，则自动设置回调地址
            if (infoResponse.data.openCallback === 0) {
              logger.info(`📡 检测到回调未开启，正在设置回调地址: ${callbackUrl}`);
              // 等待一小段时间，确保 HTTP 服务完全启动
              await new Promise((resolve) => setTimeout(resolve, 1000));

              const callbackResponse = await setCallback(robotId, {
                openCallback: 1,
                replyAll: 1, // 根据文档示例，replyAll 为数字
                callbackUrl: callbackUrl
              });

              if (callbackResponse.code === 200) {
                logger.info(`✅ WorkTool Bot ${botConfig.botId} 回调地址设置成功: ${callbackUrl}`);
              } else {
                logger.warn(`⚠️ WorkTool Bot ${botConfig.botId} 回调地址设置失败: ${callbackResponse.message}`);
                logger.warn(`   回调地址: ${callbackUrl}`);
                logger.warn(`   可能的原因:`);
                logger.warn(`   1. WorkTool 服务器无法访问该地址（防火墙、NAT 或网络问题）`);
                logger.warn(`   2. 回调地址必须是公网可访问的地址`);
                logger.warn(`   3. 检查防火墙是否允许 WorkTool 服务器访问`);
                logger.warn(`   4. 可以手动在 WorkTool 管理后台设置回调地址`);
              }
            } else if (infoResponse.data.openCallback === 1) {
              logger.info(`✅ WorkTool Bot ${botConfig.botId} 回调已开启`);
            }

            const onlineResponse = await checkRobotOnline(robotId);
            if (onlineResponse.code === 200) {
              logger.info(`✅ WorkTool Bot ${botConfig.botId} 在线状态检查完成`);
            }

            return { botId: botConfig.botId, success: true };
          } else {
            logger.warn(`⚠️ WorkTool Bot ${botConfig.botId} 获取信息失败: ${infoResponse.message}`);
            return { botId: botConfig.botId, success: false, error: infoResponse.message };
          }
        } catch (error: any) {
          logger.error(`❌ WorkTool Bot ${botConfig.botId} 检查异常:`, error.message);
          return { botId: botConfig.botId, success: false, error: error.message };
        }
      });

      const worktoolResults = await Promise.all(worktoolStatusPromises);
      const worktoolSuccessCount = worktoolResults.filter((r) => r.success).length;
      logger.info(`📋 WorkTool Bot 状态检查完成: 成功 ${worktoolSuccessCount} 个，失败 ${worktoolResults.length - worktoolSuccessCount} 个`);
    }

    // 启动 Outbound 消费者（监听 Bot 发送的消息）
    // 从环境变量读取 lanes，格式：OUTBOUND_LANES=user,admin,linfen
    const lanesEnv = process.env.OUTBOUND_LANES || 'user,admin';
    const lanes: Lane[] = lanesEnv
      .split(',')
      .map((lane) => lane.trim())
      .filter(Boolean);

    if (lanes.length === 0) {
      logger.warn('⚠️ 没有有效的 lanes，使用默认值: user,admin');
      lanes.push('user', 'admin');
    }

    logger.info(`📡 Outbound 消费者将监听 lanes: ${lanes.join(', ')}`);
    await startOutboundConsumers(lanes);
    logger.info('✅ Outbound 消费者已启动');

    // 启动机器人（自动获取二维码）
    await startBot();

    logger.info('✅ awada-server 启动完成');
  } catch (error) {
    logger.error('❌ 启动失败:', error);
    process.exit(1);
  }
};

// 优雅退出
process.on('SIGINT', async () => {
  logger.info('\n收到退出信号，正在关闭...');
  try {
    await stopOutboundConsumers();
    await RedisConnection.getInstance().disconnect();
    logger.info('✅ Redis 连接已关闭');
  } catch (error) {
    logger.error('❌ 关闭失败:', error);
  }
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('\n收到终止信号，正在关闭...');
  try {
    await stopOutboundConsumers();
    await RedisConnection.getInstance().disconnect();
    logger.info('✅ Redis 连接已关闭');
  } catch (error) {
    logger.error('❌ 关闭失败:', error);
  }
  process.exit(0);
});

// 启动
main();
