/**
 * Webhook路由 - 接收 WorkTool 消息回调
 * 文档: https://www.apifox.cn/apidoc/project-1035094/doc-861677
 *
 * 注意：
 * 1. 回调接口需要在 3 秒内响应
 * 2. 响应格式必须为 JSON (application/json)
 * 3. 响应码必须为 200
 */

import Router from 'koa-router';
import { WorkToolCallbackMessage } from '@/services/worktool/types';
import { createLogger } from '../utils/logger';
import { getBotManager } from '../services/bot/manager';
import { BotConfig } from '@/config/bots';
import { EventProducer, getConversationManager, Payload, ContentObject, Platform, Lane } from '../infrastructure/redis';
import { getRobotInfo } from '@/services/worktool';
import { sendTextMessage } from '@/services/worktool';
import { RobotInfo } from '@/services/worktool/types';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

const logger = createLogger('WorkTool-Webhook');

const router = new Router({
  prefix: '/webhook_worktool'
});

// 机器人信息缓存（robotId -> RobotInfo）
// 机器人信息一般不会频繁变化，使用永久缓存
const robotInfoCache = new Map<string, RobotInfo>();

// 正在进行的请求缓存（robotId -> Promise<RobotInfo | null>）
// 用于防止并发请求时重复调用 API
const pendingRequests = new Map<string, Promise<RobotInfo | null>>();

// 消息合并缓冲区
interface MessageBuffer {
  messages: Array<{
    message: WorkToolCallbackMessage;
    botConfig: BotConfig;
    robotId: string;
    sessionKey: string;
    userIdExternal: string;
    channelId: string;
    lane: Lane;
    tenantId: string;
    platform: Platform;
    conversationId?: string;
  }>;
  timer: NodeJS.Timeout | null;
  firstMessageIsImage: boolean; // 第一条消息是否是图片
}

// 消息缓冲区（sessionKey -> MessageBuffer）
const messageBuffers = new Map<string, MessageBuffer>();

// 消息合并等待时间（毫秒）
const MERGE_WAIT_TIME_NORMAL = 1000; // 1秒
const MERGE_WAIT_TIME_IMAGE = 5000; // 5秒（第一条消息是图片时）

// 消息缓冲开关（通过环境变量控制，默认为 true）
const ENABLE_MESSAGE_BUFFER = false;

/**
 * 指令集配置：针对特定指令返回特定文案
 * 通过环境变量 WORKTOOL_COMMAND_RESPONSES 配置，格式为 JSON 字符串
 * 例如：WORKTOOL_COMMAND_RESPONSES='{"link":"付款链接内容","help":"帮助内容"}'
 */
function loadCommandResponses(): Record<string, string> {
  const raw = process.env.WORKTOOL_COMMAND_RESPONSES;
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    logger.warn('⚠️ WORKTOOL_COMMAND_RESPONSES 解析失败，请检查 JSON 格式');
    return {};
  }
}

const COMMAND_RESPONSES: Record<string, string> = loadCommandResponses();

/**
 * 检查消息是否匹配指令集，如果匹配则返回对应的文案
 * @param message 回调消息
 * @returns 如果匹配指令，返回对应文案；否则返回 null
 */
function getCommandResponse(message: WorkToolCallbackMessage): string | null {
  const { spoken, rawSpoken, roomType, atMe } = message;
  const messageText = spoken || rawSpoken || '';

  if (!messageText) {
    return null;
  }

  // 如果是群聊，必须@机器人才能匹配指令
  //   const isGroupChat = roomType === 1 || roomType === 3;
  //   if (isGroupChat && atMe !== 'true') {
  //     // 群聊时未@机器人，不匹配指令
  //     return null;
  //   }

  // 去除首尾空格，转为小写进行匹配
  const normalizedMessage = messageText.trim().toLowerCase();

  // 精确匹配
  for (const [command, response] of Object.entries(COMMAND_RESPONSES)) {
    if (normalizedMessage === command.toLowerCase()) {
      return response;
    }
  }

  return null;
}

/**
 * 获取机器人信息（带缓存）
 * @param robotId 机器人ID
 * @returns 机器人信息，如果缓存中没有则调用 API 获取并缓存
 */
async function getCachedRobotInfo(robotId: string): Promise<RobotInfo | null> {
  // 先检查缓存
  if (robotInfoCache.has(robotId)) {
    const cachedInfo = robotInfoCache.get(robotId)!;
    logger.debug(`📦 使用缓存的机器人信息: ${robotId} (${cachedInfo.name})`);
    return cachedInfo;
  }

  // 检查是否有正在进行的请求（防止并发请求时重复调用 API）
  if (pendingRequests.has(robotId)) {
    logger.debug(`⏳ 等待正在进行的机器人信息请求: ${robotId}`);
    return await pendingRequests.get(robotId)!;
  }

  // 创建新的请求 Promise
  const requestPromise = (async () => {
    try {
      logger.debug(`🔍 从 API 获取机器人信息: ${robotId}`);
      const robotInfoResponse = await getRobotInfo(robotId);

      if (robotInfoResponse.code === 200 && robotInfoResponse.data) {
        const robotInfo = robotInfoResponse.data;
        // 缓存结果
        robotInfoCache.set(robotId, robotInfo);
        logger.debug(`✅ 机器人信息已缓存: ${robotId} (${robotInfo.name})`);
        return robotInfo;
      } else {
        logger.warn(`⚠️ 获取机器人信息失败: ${robotInfoResponse.message}`);
        return null;
      }
    } catch (error: any) {
      logger.error(`❌ 获取机器人信息异常: ${error.message}`);
      return null;
    } finally {
      // 请求完成后，从 pendingRequests 中移除
      pendingRequests.delete(robotId);
    }
  })();

  // 将请求 Promise 添加到 pendingRequests
  pendingRequests.set(robotId, requestPromise);

  return await requestPromise;
}

// 图片缓存目录
const IMAGE_CACHE_DIR = path.join(process.cwd(), 'database', 'cache', 'images');

// 确保图片缓存目录存在
if (!fs.existsSync(IMAGE_CACHE_DIR)) {
  fs.mkdirSync(IMAGE_CACHE_DIR, { recursive: true });
}

/**
 * 从 body 中查找 base64 图片数据
 * 根据文档，图片字段名为 fileBase64，格式为 PNG
 * @param body 回调消息体
 * @returns base64 图片数据，如果没有则返回 null
 */
function findBase64Image(body: any): string | null {
  // 优先检查 fileBase64 字段（根据文档规范）
  if (body.fileBase64 && typeof body.fileBase64 === 'string' && body.fileBase64.length > 0) {
    return body.fileBase64;
  }

  // 兼容其他可能的字段名
  const possibleFields = ['imageBase64', 'image', 'base64', 'imageData'];

  for (const field of possibleFields) {
    if (body[field] && typeof body[field] === 'string') {
      const value = body[field];
      // 检查是否是 base64 格式（包含 data:image 前缀或纯 base64）
      if (value.startsWith('data:image/') || (value.length > 100 && /^[A-Za-z0-9+/=]+$/.test(value))) {
        return value;
      }
    }
  }

  return null;
}

/**
 * 保存 base64 图片到本地文件
 * 根据文档，图片格式为 PNG
 * @param base64Data base64 图片数据（可能包含 data:image 前缀，或纯 base64）
 * @returns 保存的文件路径（绝对路径）
 */
function saveBase64Image(base64Data: string): string {
  try {
    // 移除 data:image 前缀（如果存在）
    const base64Pattern = /^data:image\/(\w+);base64,/i;
    const match = base64Data.match(base64Pattern);
    // 根据文档，WorkTool 图片格式为 PNG，如果没有前缀则默认使用 png
    const imageFormat = match ? match[1] : 'png';
    const pureBase64 = base64Data.replace(base64Pattern, '');

    // 转换为 Buffer
    const imageBuffer = Buffer.from(pureBase64, 'base64');

    // 生成文件名（使用 UUID + 时间戳）
    const filename = `${Date.now()}_${uuidv4()}.${imageFormat}`;
    const filePath = path.join(IMAGE_CACHE_DIR, filename);

    // 保存文件
    fs.writeFileSync(filePath, imageBuffer);

    logger.debug(`📷 图片已保存: ${filePath}`);
    return filePath;
  } catch (error: any) {
    logger.error('保存图片失败:', error);
    throw error;
  }
}

/**
 * WorkTool QA回调入口
 * POST /webhook_worktool
 *
 * 文档: https://www.apifox.cn/apidoc/project-1035094/doc-861677
 *
 * 请求格式（根据 OpenAPI 文档）:
 * {
 *   "spoken": "您好,欢迎使用WorkTool~",
 *   "rawSpoken": "@小明 您好,欢迎使用WorkTool~",
 *   "receivedName": "WorkTool",
 *   "groupName": "WorkTool",
 *   "groupRemark": "WorkTool",
 *   "roomType": 1,
 *   "atMe": "true",
 *   "textType": 1
 * }
 *
 * 响应格式（必须在 3 秒内响应）:
 * {
 *   "code": 0,
 *   "message": "success",
 *   "data": {
 *     "type": 5000,
 *     "info": {
 *       "text": "回复内容"
 *     }
 *   }
 * }
 */
router.post('/', async (ctx) => {
  const body = ctx.request.body as WorkToolCallbackMessage;
  // 从 query 参数获取 robotId，如果未提供则从 botConfig 获取第一个 WorkTool Bot 的 deviceGuid
  let robotId = ctx.query.robotId as string;
  if (!robotId) {
    const botManager = getBotManager();
    const worktoolBots = botManager.getAllBots().filter((bot) => bot.type === 'worktool');
    if (worktoolBots.length > 0) {
      robotId = worktoolBots[0].deviceGuid;
      logger.debug(`从 Bot 配置获取 robotId: ${robotId}`);
    }
  }

  logger.received('📥 收到 WorkTool 回调');
  logger.debug(`robotId: ${robotId || '未提供'}`);
  logger.debug('原始数据:', JSON.stringify(body, null, 2).substring(0, 1000));

  // 立即响应（必须在 3 秒内响应）
  ctx.body = { code: 0, message: 'received' };
  ctx.status = 200;

  // 检查是否匹配指令集，如果匹配则返回特定文案
  const commandResponse = getCommandResponse(body);
  let responseText = '';
  let isCommandMatched = false;

  if (commandResponse) {
    responseText = commandResponse;
    isCommandMatched = true;
    const roomTypeName = body.roomType === 1 ? '外部群' : body.roomType === 2 ? '外部联系人' : body.roomType === 3 ? '内部群' : body.roomType === 4 ? '内部联系人' : `未知(${body.roomType})`;
    logger.info(`✅ 匹配到指令，直接返回响应文案 (房间类型: ${roomTypeName}): ${responseText.substring(0, 50)}...`);
  }

  // 如果匹配到指令，需要向用户发送指定消息
  if (isCommandMatched) {
    // 异步发送消息，不阻塞 Webhook 响应
    setImmediate(async () => {
      try {
        const botManager = getBotManager();
        let finalRobotId = robotId;

        // 如果 query 参数中没有 robotId，尝试从 Bot 配置中获取
        if (!finalRobotId) {
          const worktoolBots = botManager.getAllBots().filter((bot) => bot.type === 'worktool');
          if (worktoolBots.length > 0) {
            // 使用第一个 WorkTool Bot 的 deviceGuid 作为 robotId
            finalRobotId = worktoolBots[0].deviceGuid;
            logger.debug(`从 Bot 配置中获取 robotId: ${finalRobotId}`);
          }
        }

        if (!finalRobotId) {
          logger.warn('⚠️ 匹配到指令但无法获取 robotId，无法发送消息');
          return;
        }

        // 确定接收者：群聊使用群名，私聊使用 receivedName
        const isGroupChat = body.roomType === 1 || body.roomType === 3;
        const titleList = isGroupChat ? [body.groupName || ''] : [body.receivedName || ''];

        if (titleList[0]) {
          // 发送消息给用户
          const sendResult = await sendTextMessage(finalRobotId, {
            titleList: titleList,
            receivedContent: responseText
          });

          if (sendResult.code === 200) {
            logger.info(`✅ 指令消息已发送给用户: ${titleList.join(', ')}`);
          } else {
            logger.error(`❌ 指令消息发送失败: ${sendResult.message}`);
          }
        } else {
          logger.warn('⚠️ 无法确定接收者，跳过发送指令消息');
        }
      } catch (error: any) {
        logger.error('发送指令消息失败:', error);
      }
    });

    logger.debug(`⏭️ 指令已直接处理，跳过后续 inbound 处理`);
    return;
  }

  // 异步处理消息，不阻塞 Webhook 响应
  setImmediate(async () => {
    try {
      const botManager = getBotManager();

      // 通过 robotId (deviceGuid) 识别 Bot
      let botConfig: BotConfig | null = null;

      if (robotId) {
        // 通过 deviceGuid 查找 Bot（WorkTool 的 deviceGuid 就是 robotId）
        botConfig = botManager.getBotByGuid(robotId);
        if (botConfig) {
          logger.debug(`通过 robotId 找到 Bot: ${botConfig.botId}`);
        }
      }

      // 如果通过 robotId 没找到，尝试获取所有 WorkTool Bot
      if (!botConfig) {
        const worktoolBots = botManager.getAllBots().filter((bot) => bot.type === 'worktool');

        if (worktoolBots.length === 0) {
          logger.warn('⚠️ 未找到 WorkTool Bot 配置');
          logger.warn(
            `   当前已注册的 Bot: ${
              botManager
                .getAllBots()
                .map((b) => `${b.botId}(${b.type})`)
                .join(', ') || '无'
            }`
          );
          return;
        }

        // 如果有多个 Bot，使用第一个（后续可以根据实际需求调整匹配逻辑）
        botConfig = worktoolBots[0];
        logger.debug(`使用第一个 WorkTool Bot: ${botConfig.botId}`);
      }

      logger.debug(`处理消息 - Bot: ${botConfig.botId} (robotId: ${robotId || botConfig.deviceGuid})`);

      // 根据开关决定是否使用消息缓冲机制
      if (ENABLE_MESSAGE_BUFFER) {
        // 使用消息合并机制处理消息
        await addMessageToBuffer(body, botConfig, robotId || botConfig.deviceGuid);
        logger.info(`✅ 消息已加入缓冲区（缓冲模式）`);
      } else {
        // 直接处理消息（无缓冲模式）
        await handleWorkToolMessage(body, botConfig, robotId || botConfig.deviceGuid);
        logger.info(`✅ 消息已直接处理（无缓冲模式）`);
      }
    } catch (error: any) {
      logger.error('异步处理消息失败:', error);
      // 异步处理失败不影响 Webhook 响应
    }
  });
});

/**
 * 检查消息是否应该处理（群消息需要@机器人）
 * @param message 回调消息
 * @param robotId 机器人ID
 * @returns 如果应该处理，返回 true
 */
export async function shouldProcessMessage(message: WorkToolCallbackMessage, robotId: string): Promise<boolean> {
  const { rawSpoken, roomType, atMe } = message;
  const isGroupChat = roomType === 1 || roomType === 3;

  // 私聊消息直接处理
  if (!isGroupChat) {
    return true;
  }

  // 群消息如果 atMe=true，直接处理
  if (atMe === 'true') {
    return true;
  }

  // 群消息如果 atMe=false，检查 rawSpoken 中 @ 的名称是否在 sumInfo 中
  const robotInfo = await getCachedRobotInfo(robotId);
  // 先匹配name
  if (robotInfo?.name) {
    return checkAtRobotInSumInfo(rawSpoken, robotInfo.name);
  }
  // 再匹配sumInfo
  if (robotInfo?.sumInfo) {
    return checkAtRobotInSumInfo(rawSpoken, robotInfo.sumInfo);
  }

  return false;
}

/**
 * 计算会话信息（sessionKey, userIdExternal 等）
 * @param message 回调消息
 * @param botConfig Bot 配置
 * @returns 会话信息
 */
function calculateSessionInfo(
  message: WorkToolCallbackMessage,
  botConfig: BotConfig
): {
  sessionKey: string;
  userIdExternal: string;
  channelId: string;
  lane: Lane;
  tenantId: string;
  platform: Platform;
} {
  const { receivedName, groupName, roomType } = message;
  const isGroupChat = roomType === 1 || roomType === 3;

  // 确定 lane
  const lane = botConfig.lanes[0] || 'user';

  // 确定 channel_id
  const channelId = isGroupChat ? groupName || '0' : '0';

  // 确定 user_id_external
  // ⚠️ 重要：user_id_external 必须使用 WorkTool 能够识别的用户标识
  // 在 outbound 中，私聊消息会使用 user_id_external 作为 titleList 来发送消息
  // 因此必须使用 receivedName（提问者名称），这是 WorkTool 回调中提供的真实发送者标识
  // 不能自定义生成，否则无法正确发送回复消息
  const userIdExternal = receivedName || 'unknown';

  // 确定 tenant_id
  const tenantId = 'default';

  // 构建 Session Key
  const platform = botConfig.platform;
  const sessionKey = `${platform}:${userIdExternal}:${channelId}:${tenantId}`;

  return {
    sessionKey,
    userIdExternal,
    channelId,
    lane,
    tenantId,
    platform
  };
}

/**
 * 将消息添加到缓冲区，实现消息合并
 * @param message 回调消息
 * @param botConfig Bot 配置
 * @param robotId 机器人ID
 */
async function addMessageToBuffer(message: WorkToolCallbackMessage, botConfig: BotConfig, robotId: string): Promise<void> {
  // 检查是否是系统消息，如果是则跳过处理
  if (isSystemMessage(message)) {
    logger.debug(`⏭️ 检测到系统消息，跳过处理: ${message.spoken || message.rawSpoken}`);
    return;
  }

  // 检查是否应该处理
  const shouldProcess = await shouldProcessMessage(message, robotId);
  if (!shouldProcess) {
    logger.debug(`⏭️ 消息不需要处理，跳过`);
    return;
  }

  // 计算会话信息
  const sessionInfo = calculateSessionInfo(message, botConfig);
  const { sessionKey } = sessionInfo;

  // 获取或创建缓冲区
  let buffer = messageBuffers.get(sessionKey);
  const isFirstMessage = !buffer;

  if (!buffer) {
    buffer = {
      messages: [],
      timer: null,
      firstMessageIsImage: message.textType === 2
    };
    messageBuffers.set(sessionKey, buffer);
  }

  // 添加消息到缓冲区
  const conversationManager = getConversationManager();
  const conversationId = await conversationManager.getConversationId(sessionInfo.platform, sessionInfo.userIdExternal, sessionInfo.channelId);

  buffer.messages.push({
    message,
    botConfig,
    robotId,
    ...sessionInfo,
    conversationId: conversationId ?? undefined
  });

  logger.debug(`📥 消息已添加到缓冲区 (sessionKey: ${sessionKey}, 当前消息数: ${buffer.messages.length}, 第一条消息${buffer.firstMessageIsImage ? '是' : '不是'}图片)`);

  // 清除旧的定时器（如果存在）
  if (buffer.timer) {
    clearTimeout(buffer.timer);
    buffer.timer = null;
    logger.debug(`🔄 重置消息合并定时器`);
  }

  // 确定等待时间：如果第一条消息是图片，等待 5s；否则等待 1s
  const waitTime = buffer.firstMessageIsImage ? MERGE_WAIT_TIME_IMAGE : MERGE_WAIT_TIME_NORMAL;

  // 设置新的定时器：等待指定时间后，如果没有新消息，则处理缓冲区中的所有消息
  buffer.timer = setTimeout(async () => {
    await processBufferedMessages(sessionKey);
  }, waitTime);

  logger.debug(`⏳ 设置消息合并定时器: ${waitTime}ms，${waitTime}ms 内如有新消息将重置定时器`);
}

/**
 * 处理缓冲区中的消息（合并并发布）
 * @param sessionKey 会话 Key
 */
async function processBufferedMessages(sessionKey: string): Promise<void> {
  const buffer = messageBuffers.get(sessionKey);
  if (!buffer || buffer.messages.length === 0) {
    messageBuffers.delete(sessionKey);
    return;
  }

  // 从缓冲区中移除（避免重复处理）
  messageBuffers.delete(sessionKey);
  if (buffer.timer) {
    clearTimeout(buffer.timer);
  }

  const messages = buffer.messages;
  logger.info(`🔄 开始处理合并消息 (sessionKey: ${sessionKey}, 消息数: ${messages.length})`);

  // 使用第一条消息的会话信息（所有消息来自同一用户，会话信息相同）
  const firstMessage = messages[0];
  const { botConfig, platform, tenantId, channelId, lane, userIdExternal, conversationId } = firstMessage;

  // 合并所有消息的 payload 到一个数组中
  // 按照消息接收顺序，将每条消息的内容添加到 payload 数组
  const mergedPayload: Payload = [];

  for (const msgData of messages) {
    const { message } = msgData;
    const { spoken, rawSpoken, textType } = message;

    // 处理图片消息
    if (textType === 2) {
      const base64Image = findBase64Image(message);
      if (base64Image) {
        try {
          //   const imageFilePath = saveBase64Image(base64Image);
          //   logger.debug(`📷 图片已保存: ${imageFilePath}`);
          mergedPayload.push({
            type: 'image',
            base64: base64Image
            // file_path: imageFilePath
          } as ContentObject);
        } catch (error: any) {
          logger.error('处理图片失败:', error);
        }
      }
    }

    // 处理文本消息
    if (textType === 1 || textType === 15) {
      if (spoken) {
        mergedPayload.push({
          type: 'text',
          text: spoken
        } as ContentObject);
      } else if (rawSpoken) {
        mergedPayload.push({
          type: 'text',
          text: rawSpoken
        } as ContentObject);
      }
    } else if (textType === 3) {
      // textType=3（语音）时，企微客户端会自动识别为文字，WorkTool 会把文字发到 server
      // 应该把它按普通 Text 消息类型处理
      if (spoken) {
        mergedPayload.push({
          type: 'text',
          text: spoken
        } as ContentObject);
      } else if (rawSpoken) {
        mergedPayload.push({
          type: 'text',
          text: rawSpoken
        } as ContentObject);
      }
    } else if (textType === 0 || textType === 2) {
      // textType=0 或 2 时，如果有文本内容也添加
      if (spoken) {
        mergedPayload.push({
          type: 'text',
          text: spoken
        } as ContentObject);
      } else if (rawSpoken) {
        mergedPayload.push({
          type: 'text',
          text: rawSpoken
        } as ContentObject);
      }
    }
  }

  // 如果无法转换 payload，跳过
  if (mergedPayload.length === 0) {
    logger.warn(`⚠️ 合并后的消息无法转换 payload，跳过`);
    return;
  }

  // 确定 actor_type
  const actorType = lane === 'admin' ? 'admin' : 'end_user';

  // 发布 Inbound 事件
  try {
    const producer = new EventProducer();
    const result = await producer.createAndPublishInbound({
      type: 'MESSAGE_NEW',
      meta: {
        platform: platform,
        tenant_id: tenantId,
        channel_id: channelId,
        lane: lane,
        actor_type: actorType,
        user_id_external: userIdExternal,
        session_id: sessionKey,
        source_message_id: `${Date.now()}-${Math.random()}`,
        conversation_id: conversationId
      },
      payload: mergedPayload
    });

    const payloadPreview = mergedPayload.map((p) => (p.type === 'text' ? `[${p.type}:${(p as any).text?.substring(0, 30)}]` : `[${p.type}]`)).join(' ');
    logger.received(`📤 合并消息已发布到 Redis - 合并了 ${messages.length} 条消息到一个 inbound event, lane=${lane}, payload项数=${mergedPayload.length}`);
    logger.debug(`   payload预览: ${payloadPreview}`);
    logger.debug(`   eventId: ${result.eventId}, streamId: ${result.streamId}, sessionSeq: ${result.sessionSeq}`);
  } catch (error: any) {
    logger.error('发布合并消息到 Redis 失败:', error);
    throw error;
  }
}

/**
 * 检查 rawSpoken 中 @ 的名称是否在机器人的 sumInfo 中
 * @param rawSpoken 原始消息内容
 * @param sumInfo 机器人的 sumInfo（包含名称、备注等信息）
 * @returns 如果 @ 的名称在 sumInfo 中，返回 true
 */
export function checkAtRobotInSumInfo(rawSpoken: string, sumInfo: string): boolean {
  if (!rawSpoken || !sumInfo) {
    return false;
  }

  // 从 rawSpoken 中提取所有 @ 的名称
  const atMatches = rawSpoken.match(/@([^\s@]+)/g);
  if (!atMatches || atMatches.length === 0) {
    return false;
  }

  // 检查每个 @ 的名称是否在 sumInfo 中
  for (const atMatch of atMatches) {
    const atName = atMatch.substring(1); // 去掉 @ 符号
    if (sumInfo.includes(atName)) {
      logger.debug(`✅ 检测到 @${atName} 在机器人的 sumInfo 中`);
      return true;
    }
  }

  return false;
}

/**
 * 检查是否是系统消息（需要屏蔽的消息）
 * @param message 回调消息
 * @returns 如果是系统消息，返回 true
 */
function isSystemMessage(message: WorkToolCallbackMessage): boolean {
  const { spoken, rawSpoken } = message;
  const messageText = (spoken || rawSpoken || '').trim();

  // 系统消息关键词列表
  const systemMessageKeywords = ['我已经添加了你，现在我们可以开始聊天了。', '我已经添加了你，现在我们可以开始聊天了', '我已经添加了你', '现在我们可以开始聊天了', '我们已经是好友了', '我们已经是好友了，现在可以开始聊天了', '我们已经是好友了，现在可以开始聊天了。'];

  // 检查消息内容是否匹配系统消息关键词
  for (const keyword of systemMessageKeywords) {
    if (messageText === keyword || messageText.includes(keyword)) {
      return true;
    }
  }

  return false;
}

/**
 * 处理 WorkTool 回调消息
 * @param message 回调消息
 * @param botConfig Bot 配置
 * @param robotId 机器人ID（用于获取机器人信息）
 */
async function handleWorkToolMessage(message: WorkToolCallbackMessage, botConfig: BotConfig, robotId: string): Promise<void> {
  const { spoken, rawSpoken, receivedName, groupName, groupRemark, roomType, atMe, textType } = message;

  // 检查是否是系统消息，如果是则跳过处理
  if (isSystemMessage(message)) {
    logger.debug(`⏭️ 检测到系统消息，跳过处理: ${spoken || rawSpoken}`);
    return;
  }

  // 根据文档，roomType: 1=外部群, 2=外部联系人, 3=内部群, 4=内部联系人
  const isGroupChat = roomType === 1 || roomType === 3;
  const roomTypeName = roomType === 1 ? '外部群' : roomType === 2 ? '外部联系人' : roomType === 3 ? '内部群' : roomType === 4 ? '内部联系人' : `未知(${roomType})`;

  // 根据文档，textType: 0=未知, 1=文本, 2=图片, 3=语音, 5=视频, 7=小程序, 8=链接, 9=文件, 13=合并记录, 15=带回复文本
  const textTypeName = textType === 0 ? '未知' : textType === 1 ? '文本' : textType === 2 ? '图片' : textType === 3 ? '语音' : textType === 5 ? '视频' : textType === 7 ? '小程序' : textType === 8 ? '链接' : textType === 9 ? '文件' : textType === 13 ? '合并记录' : textType === 15 ? '带回复文本' : `未知(${textType})`;

  logger.info(`📨 收到消息`);
  logger.info(`发送者: ${receivedName}`);
  logger.info(`群名称: ${groupName || '私聊'}`);
  logger.info(`是否@我: ${atMe === 'true' ? '是' : '否'}`);
  logger.info(`房间类型: ${roomTypeName} (${roomType})`);
  logger.info(`消息类型: ${textTypeName} (${textType})`);
  logger.info(`原始内容: ${rawSpoken}`);
  logger.info(`处理后内容: ${spoken}`);

  // 群消息如果没有@机器人，则不需要添加到 inbound
  // 但需要检查 rawSpoken 中 @ 的名称是否在机器人的 sumInfo 中
  if (isGroupChat && atMe !== 'true') {
    // 使用缓存获取机器人信息
    const robotInfo = await getCachedRobotInfo(robotId);

    if (robotInfo?.sumInfo) {
      const isAtRobot = checkAtRobotInSumInfo(rawSpoken, robotInfo.sumInfo);

      if (isAtRobot) {
        logger.info(`✅ 检测到 @ 的名称在机器人的 sumInfo 中，继续处理消息`);
      } else {
        logger.debug(`⏭️ 群消息未@机器人（atMe=false 且 @ 的名称不在 sumInfo 中），跳过处理`);
        return;
      }
    } else {
      logger.debug(`⏭️ 群消息未@机器人（无法获取机器人信息或 sumInfo），跳过处理`);
      return;
    }
  }

  // 确定 lane（根据 botConfig 的 lanes 配置，使用第一个 lane）
  const lane = botConfig.lanes[0] || 'user';

  // 确定 channel_id（群聊使用群名称，私聊使用 '0'）
  // 根据文档，roomType: 1=外部群, 3=内部群 是群聊；2=外部联系人, 4=内部联系人 是私聊
  const channelId = isGroupChat ? groupName || '0' : '0';

  // 确定 user_id_external
  // ⚠️ 重要：user_id_external 必须使用 WorkTool 能够识别的用户标识
  // 在 outbound 中，私聊消息会使用 user_id_external 作为 titleList 来发送消息
  // 因此必须使用 receivedName（提问者名称），这是 WorkTool 回调中提供的真实发送者标识
  // 不能自定义生成，否则无法正确发送回复消息
  const userIdExternal = receivedName || 'unknown';

  // 确定 tenant_id（暂时使用默认值）
  const tenantId = 'default';

  // 构建 Session Key
  const platform = botConfig.platform;
  const sessionKey = `${platform}:${userIdExternal}:${channelId}:${tenantId}`;

  // 获取 producer 和 conversationManager 实例
  const producer = new EventProducer();
  const conversationManager = getConversationManager();

  // 查询已有的 conversation_id
  const conversationId = await conversationManager.getConversationId(platform, userIdExternal, channelId);

  // 转换消息为 Payload
  const payload: Payload = [];

  // 根据 textType 处理不同类型的消息
  // textType: 0=未知, 1=文本, 2=图片, 3=语音, 5=视频, 7=小程序, 8=链接, 9=文件, 13=合并记录, 15=带回复文本

  // 处理图片消息 (textType = 2)
  // WorkTool 特殊规则：图片消息必须与上一个文本消息组合投递
  // 原因：Coze 不会处理单独的图片消息，必须连一个文本，否则相当于不处理
  if (textType === 2) {
    const base64Image = findBase64Image(message);
    if (base64Image) {
      try {
        payload.push({
          type: 'image',
          base64: base64Image
        } as ContentObject);
        // 从 Redis 查询同一个 session 的上一个文本消息
        // const lastTextMessage = await producer.getLastTextMessage(sessionKey, lane);

        // if (lastTextMessage) {
        //   // 找到上一个文本消息，将文本放在前面，图片放在后面
        //   logger.info(`📷 检测到图片消息，已找到上一个文本消息，将组合投递`);
        //   payload.push(lastTextMessage);
        //   payload.push({
        //     type: 'image',
        //     base64: base64Image
        //   } as ContentObject);
        // } else {
        //   // 未找到上一个文本消息，仍然发送图片（可能会被 Coze 忽略，但比丢消息好）
        //   logger.warn(`⚠️ 检测到图片消息，但未找到上一个文本消息，将单独发送图片（可能被 Coze 忽略）`);
        //   payload.push({
        //     type: 'image',
        //     base64: base64Image
        //   } as ContentObject);
        // }
      } catch (error: any) {
        logger.error('处理图片失败:', error);
        // 图片处理失败不影响文本消息的处理
      }
    } else {
      logger.warn('⚠️ textType=2（图片消息）但未找到 fileBase64 字段');
    }
  }

  // 处理文本消息 (textType = 1 或 15=带回复文本)
  if (textType === 1 || textType === 15) {
    if (spoken) {
      payload.push({
        type: 'text',
        text: spoken
      } as ContentObject);
    } else if (rawSpoken) {
      // 如果没有处理后的内容，使用原始内容
      payload.push({
        type: 'text',
        text: rawSpoken
      } as ContentObject);
    }
  } else if (textType === 3) {
    // textType=3（语音）时，企微客户端会自动识别为文字，WorkTool 会把文字发到 server
    // 应该把它按普通 Text 消息类型处理
    if (spoken) {
      payload.push({
        type: 'text',
        text: spoken
      } as ContentObject);
    } else if (rawSpoken) {
      payload.push({
        type: 'text',
        text: rawSpoken
      } as ContentObject);
    }
  } else if (textType === 0 || textType === 2) {
    // textType=0（未知）或 textType=2（图片）时，如果有文本内容也添加
    if (spoken) {
      payload.push({
        type: 'text',
        text: spoken
      } as ContentObject);
    } else if (rawSpoken) {
      payload.push({
        type: 'text',
        text: rawSpoken
      } as ContentObject);
    }
  }

  // 如果无法转换 payload，跳过
  if (payload.length === 0) {
    logger.warn(`⚠️ 无法转换消息，textType: ${textTypeName} (${textType}), spoken: ${spoken}, rawSpoken: ${rawSpoken}`);
    return;
  }

  // 确定 actor_type（根据 lane 判断）
  const actorType = lane === 'admin' ? 'admin' : 'end_user';

  // 发布 Inbound 事件
  try {
    const result = await producer.createAndPublishInbound({
      type: 'MESSAGE_NEW',
      meta: {
        platform: platform,
        tenant_id: tenantId,
        channel_id: channelId,
        lane: lane,
        actor_type: actorType,
        user_id_external: userIdExternal,
        session_id: sessionKey,
        source_message_id: `${Date.now()}-${Math.random()}`, // 生成唯一消息 ID
        conversation_id: conversationId ?? undefined
      },
      payload: payload
    });

    const payloadPreview = payload.map((p) => (p.type === 'text' ? `[${p.type}:${(p as any).text?.substring(0, 30)}]` : `[${p.type}]`)).join(' ');
    logger.received(`📤 消息已发布到 Redis - lane=${lane}, payload=${payloadPreview}`);
    logger.debug(`   eventId: ${result.eventId}, streamId: ${result.streamId}, sessionSeq: ${result.sessionSeq}`);
  } catch (error: any) {
    logger.error('发布消息到 Redis 失败:', error);
    throw error;
  }
}

/**
 * 健康检查
 * GET /webhook_worktool/health
 */
router.get('/health', async (ctx) => {
  ctx.body = { code: 0, message: 'ok', timestamp: Date.now() };
});

export default router;
