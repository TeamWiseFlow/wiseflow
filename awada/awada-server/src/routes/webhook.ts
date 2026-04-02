/**
 * Webhook路由 - 接收 qiweapi 消息回调
 * 文档: https://doc.qiweapi.com/doc-7331304
 *
 * 回调类型 (cmd):
 * - 11016: 账号状态变化消息
 * - 20000: API异步消息
 * - 15500: VX系统消息
 * - 15000: VX普通消息
 */

import Router from 'koa-router';
import { CallbackResponse, CallbackMessageRaw, CallbackMessage, CallbackCmd, MsgType, SystemMsgType, AccountStatusCode, FriendApplyCallback, RoomMemberChangeCallback, AccountStatusCallback, TextMsgData } from '@/services/qiweapi/types';
import { MsgTypeName, SystemMsgTypeName } from './types';
import { handleMessage } from 'src/services/message';
import { onFriendApply } from '@/src/services/friendship';
import { handleRoomMemberChange } from '@/src/services/room';
import { createLogger } from '../utils/logger';
import { getBotManager } from '../services/bot/manager';
import { BotConfig } from '@/config/bots';
import { mapRoomId } from '@/config';

const logger = createLogger('QiWeAPI-Webhook');

const router = new Router({
  prefix: '/webhook'
});

/**
 * 通用回调入口
 * POST /webhook
 */
router.post('/', async (ctx) => {
  const body = ctx.request.body as CallbackResponse;
  console.log('body', body);

  logger.received('📥 收到回调');
  logger.debug('原始数据:', JSON.stringify(body, null, 2)); // 减少日志，需要时再开启

  // 立即响应，避免阻塞新消息接收
  ctx.body = { code: 0, msg: 'received' };

  // 异步处理消息，不阻塞 Webhook 响应
  setImmediate(async () => {
    try {
      if (body.code !== 0) {
        logger.warn('回调状态非成功:', body.msg);
        return;
      }

      const messages = body.data || [];
      logger.info('messages', messages);
      logger.info(`收到 ${messages.length} 条消息，开始异步处理`);

      // 并行处理多条消息（如果有多条）
      const promises = messages.map(async (rawMsg) => {
        rawMsg.fromRoomId = mapRoomId(rawMsg.fromRoomId);
        try {
          await handleRawMessage(rawMsg);
        } catch (error: any) {
          logger.error(`处理单条消息失败:`, error);
          // 单条消息失败不影响其他消息处理
        }
      });

      await Promise.all(promises);
      logger.info(`✅ 所有消息处理完成`);
    } catch (error: any) {
      logger.error('异步处理消息失败:', error);
      // 异步处理失败不影响 Webhook 响应
    }
  });
});

/**
 * 健康检查
 * GET /webhook/health
 */
router.get('/health', async (ctx) => {
  ctx.body = { code: 0, msg: 'ok', timestamp: Date.now() };
});

/**
 * 处理原始回调消息
 */
async function handleRawMessage(rawMsg: CallbackMessageRaw): Promise<void> {
  // 多 Bot 支持：通过 guid 识别是哪个 bot
  const botManager = getBotManager();
  const botConfig = botManager.getBotByGuid(rawMsg.guid);

  if (!botConfig) {
    logger.debug(`跳过未知 bot 的消息 (guid: ${rawMsg.guid})`);
    return; // 静默忽略，不报错
  }

  logger.debug(`处理消息 - Bot: ${botConfig.botId} (guid: ${rawMsg.guid})`);
  logger.info(JSON.stringify(rawMsg, null, 2));

  const cmd = rawMsg.cmd;

  switch (cmd) {
    case CallbackCmd.ACCOUNT_STATUS:
      await handleAccountStatus(rawMsg, botConfig);
      break;
    case CallbackCmd.API_ASYNC:
      await handleApiAsync(rawMsg, botConfig);
      break;
    case CallbackCmd.SYSTEM:
      await handleSystemMessage(rawMsg, botConfig);
      break;
    case CallbackCmd.MESSAGE:
      await handleNormalMessage(rawMsg, botConfig);
      break;
    default:
      logger.warn(`未知回调类型: ${cmd}`);
  }
}

/**
 * 处理账号状态变化 - cmd=11016
 */
async function handleAccountStatus(rawMsg: CallbackMessageRaw, botConfig: BotConfig): Promise<void> {
  const msgData = rawMsg.msgData as { code: number; msg: string; status: number; serverReboot?: boolean };

  const statusCodeName: Record<number, string> = {
    [AccountStatusCode.LOGIN_SUCCESS]: '登录成功',
    [AccountStatusCode.LOGOUT_SUCCESS]: '注销成功',
    [AccountStatusCode.SESSION_REFRESH_FAILED]: '刷新session失败',
    [AccountStatusCode.KICKED_BY_OTHER]: '其它端顶号',
    [AccountStatusCode.PHONE_LOGOUT]: '手机端退出',
    [AccountStatusCode.ACCOUNT_ABNORMAL]: '账号环境异常',
    [AccountStatusCode.LOGIN_EXPIRED]: '登录态过期',
    [AccountStatusCode.NEW_DEVICE_VERIFY]: '新设备需验证'
  };

  logger.info(`📱 账号状态变化`);
  logger.info(`状态码: ${msgData.code} - ${statusCodeName[msgData.code] || '未知'}`);
  logger.info(`消息: ${msgData.msg}`);
  logger.info(`二维码状态: ${msgData.status}`);

  const callback: AccountStatusCallback = {
    guid: rawMsg.guid,
    userId: rawMsg.userId,
    code: msgData.code,
    msg: msgData.msg,
    status: msgData.status,
    serverReboot: msgData.serverReboot || false,
    raw: rawMsg
  };

  // TODO: 调用账号状态处理模块
  // await onAccountStatus(callback);
}

/**
 * 处理API异步消息 - cmd=20000
 */
async function handleApiAsync(rawMsg: CallbackMessageRaw, botConfig: BotConfig): Promise<void> {
  logger.info(`🔄 API异步消息`);
  logger.debug(`RequestId: ${rawMsg.requestId}`);
  logger.debug(`MsgData:`, rawMsg.msgData);

  // TODO: 处理异步API响应
  // 例如文件上传完成后的回调
}

/**
 * 处理系统消息 - cmd=15500
 */
async function handleSystemMessage(rawMsg: CallbackMessageRaw, botConfig: BotConfig): Promise<void> {
  const msgType = rawMsg.msgType;
  const typeName = SystemMsgTypeName[msgType] || `未知(${msgType})`;

  logger.info(`⚙️ 系统消息`);
  logger.info(`类型: ${msgType} - ${typeName}`);

  // 好友申请
  if (msgType === SystemMsgType.FRIEND_APPLY || msgType === SystemMsgType.FRIEND_APPLY_2) {
    const applyData = rawMsg.msgData as { applyTime: number; contactId: number; contactNickname: string; contactType: string; userId: number };

    if (applyData && applyData.contactId) {
      const callback: FriendApplyCallback = {
        guid: rawMsg.guid,
        userId: rawMsg.userId,
        applyTime: applyData.applyTime,
        contactId: applyData.contactId,
        contactNickname: applyData.contactNickname,
        contactType: applyData.contactType,
        raw: rawMsg
      };

      logger.info(`👋 好友申请: ${callback.contactNickname} (${callback.contactType})`);
      await onFriendApply(callback, botConfig);
    }
    return;
  }

  // 群成员变动
  if ([SystemMsgType.ROOM_MEMBER_ADD, SystemMsgType.ROOM_MEMBER_REMOVE, SystemMsgType.ROOM_MEMBER_QUIT].includes(msgType)) {
    const memberData = rawMsg.msgData as { changedMemberList: string };

    const callback: RoomMemberChangeCallback = {
      guid: rawMsg.guid,
      userId: rawMsg.userId,
      fromRoomId: rawMsg.fromRoomId || '',
      msgType: msgType,
      changedMemberList: memberData?.changedMemberList || '',
      senderId: rawMsg.senderId,
      timestamp: rawMsg.timestamp,
      raw: rawMsg
    };

    const msgTypeName = msgType === SystemMsgType.ROOM_MEMBER_ADD ? '新增成员' : msgType === SystemMsgType.ROOM_MEMBER_REMOVE ? '移除成员' : '成员退群';

    logger.info(`👥 群成员变动: 群${callback.fromRoomId} - ${msgTypeName}`);

    // 处理群成员变动，更新 room_users.json 并发送欢迎语
    if (callback.fromRoomId) {
      await handleRoomMemberChange(callback.fromRoomId, msgType, callback.changedMemberList, botConfig);
    }

    return;
  }

  // 其他系统消息
  // TODO: 根据需要处理其他类型
}

/**
 * 处理普通消息 - cmd=15000
 */
async function handleNormalMessage(rawMsg: CallbackMessageRaw, botConfig: BotConfig): Promise<void> {
  const message = parseMessage(rawMsg);
  const typeName = MsgTypeName[message.msgType] || `类型${message.msgType}`;

  // 高亮显示收到的消息
  const senderInfo = message.fromRoomId ? `群[${message.fromRoomId}] ${message.senderName || '未知'}(${message.senderId})` : `${message.senderName || '未知'}(${message.senderId})`;
  logger.received(`📨 收到消息 - 类型: ${typeName}, 发送者: ${senderInfo}`);

  // if (message.fromRoomId) {
  //   logger.debug(`群ID: ${message.fromRoomId}`); // 减少日志
  // }

  // 检查是否是群通知消息（isRoomNotice=1）且包含群成员变动信息
  // 实际场景：cmd=15000, msgType=2118, isRoomNotice=1, msgData={ changedMemberId: number }
  if (message.isRoomNotice && rawMsg.msgData) {
    const msgData = rawMsg.msgData as any;

    // 检查是否有 changedMemberId 或 changedMemberList
    if (msgData.changedMemberId !== undefined || msgData.changedMemberList !== undefined) {
      let changedMemberList: string | undefined;
      let msgType: SystemMsgType;

      // 处理 changedMemberId (单个成员ID，数字类型)
      if (msgData.changedMemberId !== undefined) {
        // 将单个成员ID转换为 base64 编码的字符串格式
        // 格式：将 "userId;" 进行 base64 编码
        const memberIdStr = `${msgData.changedMemberId};`;
        changedMemberList = Buffer.from(memberIdStr, 'utf-8').toString('base64');
        logger.debug(`检测到群成员变动 (changedMemberId): ${msgData.changedMemberId}`);

        // 根据 msgType 判断
        if (rawMsg.msgType === SystemMsgType.ROOM_MEMBER_ADD || rawMsg.msgType === SystemMsgType.ROOM_MEMBER_REMOVE || rawMsg.msgType === SystemMsgType.ROOM_MEMBER_QUIT) {
          msgType = rawMsg.msgType;
        } else {
          // 未知类型（如2118），通过 msgUniqueIdentifier 判断操作类型
          const identifier = rawMsg.msgUniqueIdentifier || '';
          const identifierLower = identifier.toLowerCase();

          // 检查是否包含删除相关的关键字
          if (identifierLower.includes('del') || identifierLower.includes('remove') || identifierLower.includes('delete') || identifierLower.includes('disassociate')) {
            msgType = SystemMsgType.ROOM_MEMBER_REMOVE;
            logger.debug(`未知消息类型 ${rawMsg.msgType}，根据 msgUniqueIdentifier 推断为移除成员: ${identifier}`);
          }
          // 检查是否包含加入相关的关键字
          else if (identifierLower.includes('add') || identifierLower.includes('join') || (identifierLower.includes('associate') && !identifierLower.includes('del'))) {
            msgType = SystemMsgType.ROOM_MEMBER_ADD;
            logger.debug(`未知消息类型 ${rawMsg.msgType}，根据 msgUniqueIdentifier 推断为新增成员: ${identifier}`);
          }
          // 如果无法判断，文档中未标明的类型，不处理
          else {
            logger.warn(`未知消息类型 ${rawMsg.msgType}，无法从 msgUniqueIdentifier 判断，跳过处理: ${identifier}`);
            return; // 文档中未标明的类型，不处理
          }
        }
      }
      // 处理 changedMemberList (base64编码的字符串)
      else if (msgData.changedMemberList) {
        changedMemberList = msgData.changedMemberList;
        const preview = changedMemberList ? changedMemberList.substring(0, 50) : '';
        logger.debug(`检测到群成员变动 (changedMemberList): ${preview}...`);

        // 根据 msgType 判断
        if (rawMsg.msgType === SystemMsgType.ROOM_MEMBER_ADD || rawMsg.msgType === SystemMsgType.ROOM_MEMBER_REMOVE || rawMsg.msgType === SystemMsgType.ROOM_MEMBER_QUIT) {
          msgType = rawMsg.msgType;
        } else {
          // 未知类型，通过 msgUniqueIdentifier 判断操作类型
          const identifier = rawMsg.msgUniqueIdentifier || '';
          const identifierLower = identifier.toLowerCase();

          // 检查是否包含删除相关的关键字
          if (identifierLower.includes('del') || identifierLower.includes('remove') || identifierLower.includes('delete') || identifierLower.includes('disassociate')) {
            msgType = SystemMsgType.ROOM_MEMBER_REMOVE;
            logger.debug(`未知消息类型 ${rawMsg.msgType}，根据 msgUniqueIdentifier 推断为移除成员: ${identifier}`);
          }
          // 检查是否包含加入相关的关键字
          else if (identifierLower.includes('add') || identifierLower.includes('join') || (identifierLower.includes('associate') && !identifierLower.includes('del'))) {
            msgType = SystemMsgType.ROOM_MEMBER_ADD;
            logger.debug(`未知消息类型 ${rawMsg.msgType}，根据 msgUniqueIdentifier 推断为新增成员: ${identifier}`);
          }
          // 如果无法判断，文档中未标明的类型，不处理
          else {
            logger.warn(`未知消息类型 ${rawMsg.msgType}，无法从 msgUniqueIdentifier 判断，跳过处理: ${identifier}`);
            return; // 文档中未标明的类型，不处理
          }
        }
      } else {
        return; // 没有有效的成员变动信息
      }

      // 处理群成员变动
      if (message.fromRoomId && changedMemberList) {
        const msgTypeName = msgType === SystemMsgType.ROOM_MEMBER_ADD ? '新增成员' : msgType === SystemMsgType.ROOM_MEMBER_REMOVE ? '移除成员' : '成员退群';
        logger.info(`👥 群成员变动: 群${message.fromRoomId} - ${msgTypeName}`);

        await handleRoomMemberChange(message.fromRoomId, msgType, changedMemberList, botConfig);
      }

      return; // 群通知消息已处理，不需要继续处理
    }
  }

  // 文本消息 - 高亮显示内容
  if (message.msgType === MsgType.TEXT || message.msgType === MsgType.TEXT_2) {
    const content = message.content?.substring(0, 200) || '';
    logger.received(`内容: ${content}${content.length >= 200 ? '...' : ''}`);
    // if (message.atList?.length > 0) {
    //   logger.debug(`@列表: ${message.atList.map((a) => a.nickname + '(' + a.userId + ')').join(', ')}`); // 减少日志
    // }
  }

  // 调用消息处理服务，将消息发布到 Redis
  try {
    const result = await handleMessage(message, botConfig);

    if (result.handled) {
      if (result.immediateResponse) {
        // 立即响应的导演指令（如 /ding, /start, /stop）
        // 注意：响应消息已在 handleMessage 中发送，这里只需要记录日志
        logger.info(`立即响应指令: ${result.immediateResponse}`);
      } else {
        // 消息已发布到 Redis，在 message/index.ts 中已高亮显示
        // logger.info(`消息已发布到 Redis: eventId=${result.eventId}, streamId=${result.streamId}`); // 减少重复日志
      }
    } else {
      logger.debug(`消息未处理（可能是非普通消息类型）`);
    }
  } catch (error: any) {
    logger.error(`处理消息失败:`, error);
    // 不抛出错误，避免影响其他消息处理
  }
}

/**
 * 解析原始消息为标准格式
 */
function parseMessage(rawMsg: CallbackMessageRaw): CallbackMessage {
  // 解析文本消息内容
  let content = '';
  let atList: Array<{ userId: string; nickname: string }> = [];

  if (rawMsg.msgData) {
    const textData = rawMsg.msgData as TextMsgData;
    content = textData.content || '';
    atList = textData.atList || [];
  }

  return {
    guid: rawMsg.guid,
    userId: rawMsg.userId,
    cmd: rawMsg.cmd,
    msgType: rawMsg.msgType,
    msgServerId: rawMsg.msgServerId,
    msgUniqueIdentifier: rawMsg.msgUniqueIdentifier,
    senderId: rawMsg.senderId,
    senderName: rawMsg.senderName || '',
    receiverId: rawMsg.receiverId || 0,
    fromRoomId: rawMsg.fromRoomId || '',
    isRoomNotice: rawMsg.isRoomNotice === 1,
    content,
    atList,
    timestamp: rawMsg.timestamp,
    seq: rawMsg.seq,
    msgData: rawMsg.msgData,
    base64RawData: rawMsg.base64RawData,
    raw: rawMsg
  };
}

export default router;
