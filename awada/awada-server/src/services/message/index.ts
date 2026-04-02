/**
 * 消息处理服务
 * 负责将 qiweapi 回调消息转换为 InboundEvent 并发布到 Redis Stream
 */

import { CallbackMessage, MsgType, FileWxMsgData } from '@/services/qiweapi/types';
import { EventProducer, getConversationManager, Lane, Payload, ContentObject } from '../../infrastructure/redis';
import { staticConfig } from '@/config';
import { downloadWxFile } from '@/services/qiweapi/cdn';
import CONFIG, { needPermission } from '@/config';
import { BotConfig } from '@/config/bots';
import { getUserStatus } from '@/services/qiweapi/login';
import { fetchAndSaveRoomDetail, roomExists, removeRoom, readRoomUsers } from '../room';
import { sendMessage } from '@/services/qiweapi/message';
import { createLogger } from '../../utils/logger';
// 懒加载实例，避免模块加载时初始化 Redis（此时 Redis 可能还未初始化）
let producerInstance: EventProducer | null = null;
let conversationManagerInstance: ReturnType<typeof getConversationManager> | null = null;

// 创建日志实例
const logger = createLogger('Message');

/**
 * 获取 EventProducer 实例（懒加载）
 */
function getProducer(): EventProducer {
  if (!producerInstance) {
    producerInstance = new EventProducer();
  }
  return producerInstance;
}

/**
 * 获取 ConversationManager 实例（懒加载）
 */
function getConversationMgr() {
  if (!conversationManagerInstance) {
    conversationManagerInstance = getConversationManager();
  }
  return conversationManagerInstance;
}

/**
 * 判断用户是否是导演
 */
function isDirector(userId: string): boolean {
  if (!staticConfig?.directors) {
    return false;
  }
  return staticConfig.directors.includes(userId);
}

/**
 * 从消息内容中提取命令部分（去掉 @ 信息）
 * 例如："@Liebe /start" -> "/start"
 *       "/start" -> "/start"
 *       "这里@某人 /start" -> "/start"
 */
function extractCommand(content: string): string {
  const trimmed = content.trim();

  // 如果直接以 '/' 开头，直接返回
  if (trimmed.startsWith('/')) {
    return trimmed;
  }

  // 去掉开头的 @ 信息（可能多个）
  // 匹配模式：@[^\s]+ 后跟空格（可能多个）
  let cleaned = trimmed.replace(/^(@[^\s]+\s+)+/, '').trim();

  // 如果去掉 @ 后以 '/' 开头，返回命令部分
  if (cleaned.startsWith('/')) {
    // 提取第一个命令（到空格或行尾）
    const match = cleaned.match(/^(\/\w+)/);
    return match ? match[1] : cleaned;
  }

  // 检查内容中是否包含命令（处理命令在中间的情况）
  const commandMatch = trimmed.match(/\s+(\/\w+)/);
  if (commandMatch) {
    return commandMatch[1];
  }

  return trimmed;
}

/**
 * 判断是否是导演指令
 * 条件：1. 用户在导演名单中 2. 消息为纯文本且包含以 '/' 开头的命令
 *
 * 注意：群消息中可能包含 @ 信息，如 "@Liebe /start"，需要去掉 @ 部分后检查命令
 */
function isDirectorCommand(message: CallbackMessage): boolean {
  if (!isDirector(message.senderId.toString())) {
    return false;
  }

  // 只处理文本消息
  if (message.msgType !== MsgType.TEXT && message.msgType !== MsgType.TEXT_2) {
    return false;
  }

  const content = message.content || '';
  const command = extractCommand(content);
  return command.startsWith('/');
}

/**
 * 获取机器人自己的userId
 * 优先从 BotConfig 中获取（启动时已缓存），如果不存在则从 API 获取
 */
async function getBotUserId(botConfig: BotConfig): Promise<string | null> {
  // 优先使用 BotConfig 中缓存的 userId
  if (botConfig.userId) {
    return botConfig.userId;
  }

  // 如果缓存中没有，尝试从 API 获取（向后兼容）
  try {
    const response = await getUserStatus(botConfig.deviceGuid, botConfig.token);
    if (response.code === 0 && response.data?.wxid) {
      // 更新 BotConfig 中的 userId（如果 BotManager 可用）
      try {
        const { getBotManager } = await import('../bot/manager');
        const botManager = getBotManager();
        botManager.updateBotUserId(botConfig.botId, response.data.wxid);
      } catch (error) {
        // BotManager 可能还未初始化，忽略错误
      }
      logger.info(`从 API 获取机器人userId: ${response.data.wxid}`);
      return response.data.wxid;
    }
  } catch (error) {
    logger.error('获取机器人userId失败:', error);
  }

  return null;
}

/**
 * 检查消息是否@了机器人
 */
export async function isMentioningBot(message: CallbackMessage, botConfig: BotConfig): Promise<boolean> {
  // 只有在群消息中才可能有@
  if (!message.fromRoomId || Number(message.fromRoomId) === 0) {
    return false;
  }

  // 检查是否有@列表
  if (!message.atList || message.atList.length === 0) {
    return false;
  }

  // 获取机器人userId
  const botId = await getBotUserId(botConfig);
  if (!botId) {
    return false;
  }

  // 检查@列表中是否包含机器人
  return message.atList.some((at) => at.userId === botId);
}

/**
 * 判断是否是立即响应的导演指令（如 /ding, /start, /stop）
 */
async function isImmediateDirectorCommand(message: CallbackMessage, botConfig: BotConfig): Promise<boolean> {
  if (!isDirectorCommand(message)) {
    return false;
  }

  const content = message.content || '';
  const command = extractCommand(content);

  // /ding 指令（私聊或群聊都可以）
  if (command === '/ding') {
    return true;
  }

  // /start 指令（必须在群聊中且@了机器人）
  if (command === '/start') {
    const isMentioned = await isMentioningBot(message, botConfig);
    logger.debug(`是否@了机器人: ${isMentioned}`);
    if (isMentioned && message.fromRoomId) {
      return true;
    }
  }

  // /stop 指令（必须在群聊中且@了机器人）
  if (command === '/stop') {
    const isMentioned = await isMentioningBot(message, botConfig);
    if (isMentioned && message.fromRoomId) {
      return true;
    }
  }

  return false;
}

/**
 * 检查用户是否有权限（是否在权限群组中或导演列表中）
 *
 * @param userId 用户ID
 * @returns 是否有权限
 */
function hasUserPermission(userId: string): boolean {
  if (!needPermission) return true;

  // 检查是否是导演
  if (isDirector(userId)) {
    return true;
  }

  // 检查是否在权限群组的成员列表中
  const roomUsers = readRoomUsers();
  const allMemberIds = roomUsers.reduce<string[]>((acc, entry) => {
    if (entry.room?.memberIdList) {
      return [...acc, ...entry.room.memberIdList];
    }
    return acc;
  }, []);

  return allMemberIds.includes(userId);
}

/**
 * 检查群是否已开启权限
 */
function isRoomEnabled(roomId: string | number | undefined): boolean {
  if (!needPermission) return true;
  if (!roomId || roomId === 0) {
    // 私聊消息，不受群权限限制
    return true;
  }

  return roomExists(roomId.toString());
}

/**
 * 确定消息应该路由到哪个 lane
 */
function determineLane(message: CallbackMessage, botConfig: BotConfig): Lane {
  // 多 Bot 支持：使用 botConfig 的 lanes
  const configuredLanes = botConfig.lanes;

  // 检查是否是导演发的以 / 开头的命令（但不是 /stop、/start、/ding）
  const content = message.content?.trim() || '';
  const isDirector = isDirectorCommand(message);
  const isCustomCommand = content.startsWith('/') && !['/stop', '/start', '/ding'].includes(content.split(/\s/)[0]);

  // 如果是导演发的自定义命令（/开头但不是 /stop、/start、/ding），使用 admin lane
  if (isDirector && isCustomCommand) {
    if (configuredLanes.includes('admin')) {
      return 'admin';
    }
  }

  // 如果只配置了一个 lane，直接使用
  if (configuredLanes.length === 1) {
    return configuredLanes[0];
  }

  // 默认使用第一个配置的 lane
  return configuredLanes[0];
}

/**
 * 构建 Session Key
 * 格式: {platform}:{user_id_external}:{channel_id}:{tenant_id}
 */
function buildSessionKey(platform: string, userId: string, channelId: string, tenantId: string): string {
  return `${platform}:${userId}:${channelId}:${tenantId}`;
}

/**
 * 将文本消息转换为 Payload
 */
function convertTextMessage(message: CallbackMessage): Payload {
  const content = message.content || '';

  return [{ type: 'text', text: content }];
}

/**
 * 将多媒体消息转换为 Payload
 * 目前支持：图片、文件、语音
 */
async function convertMediaMessage(message: CallbackMessage, botConfig: BotConfig): Promise<Payload | null> {
  const contentObjects: ContentObject[] = [];

  // 文本内容（如果有）
  if (message.content) {
    contentObjects.push({
      type: 'text',
      text: message.content
    });
  }

  // 根据消息类型添加媒体内容
  switch (message.msgType) {
    case MsgType.IMAGE_WORK:
    case MsgType.IMAGE_WORK_2: {
      // 企微图片消息
      const imageData = message.msgData as any;
      if (imageData?.fileId) {
        contentObjects.push({
          type: 'image',
          file_id: imageData.fileId
        });
      } else if (imageData?.fileHttpUrl) {
        contentObjects.push({
          type: 'image',
          file_url: imageData.fileHttpUrl
        });
      }
      break;
    }

    case MsgType.IMAGE_WX: {
      // 个微图片消息 - 有 fileBigHttpUrl, fileMiddleHttpUrl, fileThumbHttpUrl
      const imageData = message.msgData as any;
      // 优先使用大图，其次中图，最后缩略图
      if (imageData?.fileBigHttpUrl) {
        contentObjects.push({
          type: 'image',
          file_url: imageData.fileBigHttpUrl
        });
      } else if (imageData?.fileMiddleHttpUrl) {
        contentObjects.push({
          type: 'image',
          file_url: imageData.fileMiddleHttpUrl
        });
      } else if (imageData?.fileThumbHttpUrl) {
        contentObjects.push({
          type: 'image',
          file_url: imageData.fileThumbHttpUrl
        });
      }
      break;
    }

    case MsgType.FILE_WORK:
    case MsgType.FILE_LARGE: {
      // 企微文件消息（包括大文件 >20M）
      const fileData = message.msgData as any;
      if (fileData?.fileId) {
        contentObjects.push({
          type: 'file',
          file_id: fileData.fileId
        });
      } else if (fileData?.fileHttpUrl) {
        contentObjects.push({
          type: 'file',
          file_url: fileData.fileHttpUrl
        });
      }
      break;
    }

    case MsgType.FILE_WX: {
      // 个微文件消息 - 需要转换为可访问的 cloudUrl
      const fileData = message.msgData as FileWxMsgData;

      // 个微文件需要下载转换为 cloudUrl
      // 注意：实际API返回的字段名是 fileAesKey 和 fileAuthKey（大写K）
      const fileAeskey = (fileData as any).fileAesKey || (fileData as any).fileAeskey;
      const fileAuthkey = (fileData as any).fileAuthKey || (fileData as any).fileAuthkey;
      const fileName = fileData.fileName || fileData.filename;

      if (fileAeskey && fileAuthkey && fileData?.fileHttpUrl) {
        try {
          const deviceGuid = botConfig.deviceGuid;
          if (!deviceGuid) {
            logger.warn('设备GUID不存在，无法下载个微文件');
            break;
          }

          const downloadResult = await downloadWxFile(
            {
              fileAeskey: fileAeskey,
              fileAuthkey: fileAuthkey,
              fileSize: fileData.fileSize,
              fileType: 5, // 文件类型：5-文件/语音文件
              fileUrl: fileData.fileHttpUrl
            },
            botConfig.deviceGuid,
            botConfig.token
          );

          if (downloadResult.code === 0 && downloadResult.data?.cloudUrl) {
            contentObjects.push({
              type: 'file',
              file_name: fileName,
              file_url: downloadResult.data.cloudUrl
            });
            logger.info(`✅ 个微文件已转换为 cloudUrl: ${downloadResult.data.cloudUrl}`);
          } else {
            logger.error(`❌ 个微文件下载失败: ${downloadResult.msg}`);
            // 下载失败时，仍然使用原始 fileHttpUrl（虽然可能无法直接访问）
            contentObjects.push({
              type: 'file',
              file_url: fileData.fileHttpUrl
            });
          }
        } catch (error: any) {
          logger.error(`❌ 下载个微文件异常:`, error);
          // 异常时，仍然使用原始 fileHttpUrl
          contentObjects.push({
            type: 'file',
            file_url: fileData.fileHttpUrl
          });
        }
      } else if (fileData?.fileHttpUrl) {
        // 如果没有必要的下载参数，直接使用 fileHttpUrl（可能无法直接访问）
        logger.warn('⚠️ 个微文件缺少下载参数，使用原始 fileHttpUrl（可能无法访问）');
        contentObjects.push({
          type: 'file',
          file_url: fileData.fileHttpUrl
        });
      }
      break;
    }

    case MsgType.VOICE: {
      // 语音消息（语音消息下载默认走企微文件下载，文件格式为.silk）
      const voiceData = message.msgData as any;
      if (voiceData?.fileId) {
        contentObjects.push({
          type: 'audio',
          file_id: voiceData.fileId
        });
      } else if (voiceData?.fileHttpUrl) {
        // 如果有 fileHttpUrl，也支持
        contentObjects.push({
          type: 'audio',
          file_url: voiceData.fileHttpUrl
        });
      }
      break;
    }

    default:
      // 不支持的消息类型，返回纯文本（如果有）
      if (message.content) {
        return convertTextMessage(message);
      }
      return null;
  }

  // 如果没有内容，返回 null
  if (contentObjects.length === 0) {
    return null;
  }

  // 直接返回 ContentObject 数组
  return contentObjects;
}

/**
 * 处理普通消息并发布到 Redis
 */
export async function handleMessage(
  message: CallbackMessage,
  botConfig: BotConfig
): Promise<{
  eventId?: string;
  streamId?: string;
  handled: boolean;
  immediateResponse?: string;
}> {
  // 只处理普通消息（cmd=15000）
  if (message.cmd !== 15000) {
    return { handled: false };
  }

  // 检查是否是立即响应的导演指令
  const isImmediate = await isImmediateDirectorCommand(message, botConfig);
  if (isImmediate) {
    const content = message.content || '';
    const command = extractCommand(content);

    // /ding 指令
    if (command === '/ding') {
      if (botConfig.deviceGuid) {
        const responseText = handleDingCommand();
        const targetId = message.fromRoomId && Number(message.fromRoomId) !== 0 ? message.fromRoomId.toString() : message.senderId.toString();

        try {
          await sendMessage(targetId, responseText, undefined, botConfig.deviceGuid, botConfig.token);
          logger.info(`✅ 已发送 /ding 响应消息`);
        } catch (error) {
          logger.error(`❌ 发送 /ding 响应消息失败:`, error);
        }
      }

      return {
        handled: true,
        immediateResponse: 'ding' // 返回标识
      };
    }

    // /start 指令 - 设置群为服务群并保存群信息
    if (command === '/start' && message.fromRoomId) {
      const roomId = message.fromRoomId.toString();
      const channelId = roomId;

      logger.info(`处理 /start 指令: roomId=${roomId}`);

      // 获取群详情并保存
      const success = await fetchAndSaveRoomDetail(roomId, botConfig);

      // 发送响应消息
      if (botConfig.deviceGuid) {
        const responseText = success ? staticConfig?.room_speech?.start || '群服务已开启' : '获取群信息失败，请稍后重试';

        try {
          const sendResult = await sendMessage(channelId, responseText, undefined, botConfig.deviceGuid, botConfig.token);
          if (sendResult.code === 0) {
            logger.info(`✅ 已发送 /start 响应消息`);
          } else {
            logger.error(`❌ 发送 /start 响应消息失败: code=${sendResult.code}, msg=${sendResult.msg}`);
            // 如果是群消息发送失败，可能是 bot 不在群中或权限问题
            if (sendResult.msg?.includes('WxErrorCode') || sendResult.msg?.includes('-3020')) {
              logger.warn(`⚠️ 群消息发送失败，可能是 bot 不在群中或需要特殊权限`);
            }
          }
        } catch (error: any) {
          logger.error(`❌ 发送 /start 响应消息异常:`, error);
        }
      }

      return {
        handled: true,
        immediateResponse: 'start' // 返回标识
      };
    }

    // /stop 指令 - 关闭群权限
    if (command === '/stop' && message.fromRoomId) {
      const roomId = message.fromRoomId.toString();
      const channelId = roomId;

      logger.info(`处理 /stop 指令: roomId=${roomId}`);

      // 移除群（关闭权限）
      const success = removeRoom(roomId);

      // 发送响应消息
      if (botConfig.deviceGuid) {
        const responseText = staticConfig?.room_speech?.stop || '群服务已关闭';

        try {
          const sendResult = await sendMessage(channelId, responseText, undefined, botConfig.deviceGuid, botConfig.token);
          if (sendResult.code === 0) {
            logger.info(`✅ 已发送 /stop 响应消息`);
          } else {
            logger.error(`❌ 发送 /stop 响应消息失败: code=${sendResult.code}, msg=${sendResult.msg}`);
          }
        } catch (error: any) {
          logger.error(`❌ 发送 /stop 响应消息异常:`, error);
        }
      }

      return {
        handled: true,
        immediateResponse: 'stop' // 返回标识
      };
    }
  }

  // 检查是否需要自动回复"收到，请稍候"
  // 条件：1. 以 # 开头的文本消息  2. 文件消息
  const shouldAutoReply = (() => {
    // 检查是否以 # 开头
    if (message.msgType === MsgType.TEXT || message.msgType === MsgType.TEXT_2) {
      const content = message.content?.trim() || '';
      if (content.startsWith('#')) {
        return true;
      }
    }

    // 检查是否是文件消息
    if (message.msgType === MsgType.FILE_WORK || message.msgType === MsgType.FILE_LARGE || message.msgType === MsgType.FILE_WX) {
      return true;
    }

    return false;
  })();


  // 检查群消息权限
  const isGroupMessage = message.fromRoomId && Number(message.fromRoomId) !== 0;
  if (isGroupMessage) {
    const isMentioned = await isMentioningBot(message, botConfig);

    // 管理员的消息始终有权限，不需要检查群权限
    const isAdminMessage = isDirectorCommand(message);
    logger.debug(`是否@了机器人: ${isMentioned}`);

    logger.debug(`是否管理员指令: ${isAdminMessage}`);
    // 群消息必须@机器人才能处理（除非是管理员指令）
    if (!isMentioned && !isAdminMessage) {
      // 群消息但没@机器人，且不是管理员指令，不处理
      logger.debug(`群消息未@机器人，跳过处理`);
      return { handled: false };
    }

    // 如果@了机器人，需要检查群权限（但管理员指令不需要检查）
    if (isMentioned && !isRoomEnabled(message.fromRoomId) && !isAdminMessage) {
      logger.warn(`⚠️ 群 ${message.fromRoomId} 未开启权限，拒绝处理消息`);

      // 发送提示消息
      if (botConfig.deviceGuid) {
        const responseText = staticConfig?.room_speech?.no_permission || '请管理员先开启本群服务权限：@我并输入 start';

        try {
          const sendResult = await sendMessage(message.fromRoomId.toString(), responseText, undefined, botConfig.deviceGuid, botConfig.token);
          if (sendResult.code === 0) {
            logger.info(`✅ 已发送权限提示消息`);
          } else {
            logger.error(`❌ 发送权限提示消息失败: code=${sendResult.code}, msg=${sendResult.msg}`);
          }
        } catch (error: any) {
          logger.error(`❌ 发送权限提示消息异常:`, error);
        }
      }

      return {
        handled: true,
        immediateResponse: 'no_permission'
      };
    }
  }

  // 私聊消息需要检查用户权限
  if (!isGroupMessage) {
    const senderId = message.senderId.toString();
    const isAdminMessage = isDirectorCommand(message);

    // 管理员消息始终有权限
    if (!isAdminMessage && !hasUserPermission(senderId)) {
      logger.warn(`⚠️ 私聊用户 ${senderId} 不在权限列表中，拒绝处理消息`);

      // 发送提示消息
      if (botConfig.deviceGuid) {
        const responseText = staticConfig?.person_speech?.no_permission || '您暂无权限使用此服务，请联系管理员';

        try {
          await sendMessage(senderId, responseText, undefined, botConfig.deviceGuid, botConfig.token);
          logger.info(`✅ 已发送权限提示消息`);
        } catch (error) {
          logger.error(`❌ 发送权限提示消息失败:`, error);
        }
      }

      return {
        handled: true,
        immediateResponse: 'no_permission'
      };
    }
  }

  if (shouldAutoReply) {
    // 使用 botConfig 的 deviceGuid
    if (botConfig.deviceGuid) {
      const replyText = '收到，请稍候';
      const targetId = message.fromRoomId && Number(message.fromRoomId) !== 0 ? message.fromRoomId.toString() : message.senderId.toString();

      try {
        await sendMessage(targetId, replyText, undefined, botConfig.deviceGuid, botConfig.token);
        logger.info(`✅ 已发送自动回复: ${replyText}`);
      } catch (error) {
        logger.error(`❌ 发送自动回复失败:`, error);
      }
    }
  }
  
  // 确定 lane
  const lane = determineLane(message, botConfig);

  // 构建 Session Key
  const PLATFORM = CONFIG.platform;
  const userId = message.senderId.toString();
  const channelId = message.fromRoomId ? message.fromRoomId.toString() : '0';
  // tenantId 从原始消息的 TenantId 获取，如果没有则使用 userId 作为默认值
  const tenantId = message.raw?.TenantId?.toString() || message.userId || 'default';
  const sessionKey = buildSessionKey(PLATFORM, userId, channelId, tenantId);

  // 懒加载获取实例（此时 Redis 已经初始化）
  const producer = getProducer();
  const conversationManager = getConversationMgr();

  // 查询已有的 conversation_id
  const conversationId = await conversationManager.getConversationId(PLATFORM, userId, channelId);

  // 转换消息为 Payload
  let payload: Payload | null = null;

  // 文本消息
  if (message.msgType === MsgType.TEXT || message.msgType === MsgType.TEXT_2) {
    payload = convertTextMessage(message);
  } else {
    // 多媒体消息
    payload = await convertMediaMessage(message, botConfig);
  }

  // 如果无法转换 payload，跳过
  if (!payload) {
    logger.warn(`无法转换消息类型: ${message.msgType}`);
    return { handled: false };
  }

  // 发布 Inbound 事件
  try {
    const result = await producer.createAndPublishInbound({
      type: 'MESSAGE_NEW',
      meta: {
        platform: PLATFORM,
        tenant_id: tenantId,
        channel_id: channelId,
        lane,
        actor_type: lane === 'admin' ? 'admin' : 'end_user',
        user_id_external: userId,
        session_id: sessionKey,
        source_message_id: message.msgServerId.toString(),
        conversation_id: conversationId ?? undefined
      },
      payload: payload
    });

    // 高亮显示：消息已收到并发布到 Redis
    const payloadPreview = Array.isArray(payload) && payload.length > 0 ? payload.map((p) => (p.type === 'text' ? `[${p.type}:${(p as any).text?.substring(0, 30)}]` : `[${p.type}]`)).join(' ') : '[空]';
    logger.received(`📤 消息已发布到 Redis - lane=${lane}, payload=${payloadPreview}`);

    return {
      handled: true,
      eventId: result.eventId,
      streamId: result.streamId
    };
  } catch (error) {
    logger.error('发布消息到 Redis 失败:', error);
    throw error;
  }
}

/**
 * 处理 /ding 指令的立即响应
 * 返回响应内容
 */
export function handleDingCommand(): string {
  // 从配置中获取 ding 响应内容
  const dingResponse = staticConfig?.common_speech?.ding || 'ding';
  return dingResponse;
}
