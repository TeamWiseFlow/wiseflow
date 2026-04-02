/**
 * 群管理服务
 * 负责群信息的保存和管理
 */

import * as fs from 'fs';
import * as path from 'path';
import { WechatyuiPath, staticConfig } from '@/config';
import { batchGetRoomDetail, RoomDetail, RoomMember } from '@/services/qiweapi/room';
import { sendMessage } from '@/services/qiweapi/message';
import { BotConfig } from '@/config/bots';
import { getUserStatus } from '@/services/qiweapi/login';
import { createLogger } from '../../utils/logger';

const logger = createLogger('RoomService');

// ==================== 类型定义 ====================

/** room_users.json 中的用户信息 */
export interface RoomUser {
  id: string;
  name: string;
  roomAlias: string;
}

/** room_users.json 中的群信息 */
export interface RoomUsersEntry {
  room: {
    id: string;
    memberIdList: string[];
  };
  users: RoomUser[];
}

// ==================== 文件路径 ====================

const ROOM_USERS_FILE = path.join(WechatyuiPath, 'room_users.json');

/**
 * 确保目录存在
 */
function ensureDirectoryExists(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * 读取 room_users.json
 */
export function readRoomUsers(): RoomUsersEntry[] {
  ensureDirectoryExists(WechatyuiPath);

  if (!fs.existsSync(ROOM_USERS_FILE)) {
    return [];
  }

  try {
    const content = fs.readFileSync(ROOM_USERS_FILE, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    logger.error('读取 room_users.json 失败:', error);
    return [];
  }
}

/**
 * 保存 room_users.json
 */
export function saveRoomUsers(entries: RoomUsersEntry[]): void {
  ensureDirectoryExists(WechatyuiPath);

  try {
    fs.writeFileSync(ROOM_USERS_FILE, JSON.stringify(entries, null, 2), 'utf-8');
    logger.info(`✅ 已保存 ${entries.length} 个群信息到 room_users.json`);
  } catch (error) {
    logger.error('❌ 保存 room_users.json 失败:', error);
    throw error;
  }
}

/**
 * 检查群是否已存在（已开启权限）
 */
export function roomExists(roomId: string): boolean {
  const entries = readRoomUsers();
  return entries.some(entry => entry.room.id === roomId);
}

/**
 * 移除群（关闭群权限）
 */
export function removeRoom(roomId: string): boolean {
  const entries = readRoomUsers();
  const initialLength = entries.length;
  
  const filtered = entries.filter(entry => entry.room.id !== roomId);
  
  if (filtered.length < initialLength) {
    saveRoomUsers(filtered);
    logger.info(`已移除群: ${roomId}`);
    return true;
  }
  
  logger.info(`群不存在: ${roomId}`);
  return false;
}

/**
 * 更新或添加群信息
 */
export function upsertRoom(roomDetail: RoomDetail): void {
  const entries = readRoomUsers();
  
  // 检查 roomId 是否有效
  if (!roomDetail.roomId || roomDetail.roomId.trim() === '') {
    logger.warn(`❌ 群详情无效: roomId 为空`);
    throw new Error('群详情无效: roomId 为空');
  }
  
  // 查找是否已存在
  const existingIndex = entries.findIndex(entry => entry.room.id === roomDetail.roomId);
  
  // 构建用户列表（处理 memberList 为 null 的情况）
  const memberList = roomDetail.memberList || [];
  const users: RoomUser[] = memberList.map(member => ({
    id: member.userId,
    name: member.name,
    roomAlias: member.roomRemarkName || member.name,
  }));

  // 构建群信息
  const roomEntry: RoomUsersEntry = {
    room: {
      id: roomDetail.roomId,
      memberIdList: memberList.map(m => m.userId),
    },
    users,
  };

  if (existingIndex >= 0) {
    // 更新已存在的群
    entries[existingIndex] = roomEntry;
    logger.info(`更新群信息: ${roomDetail.roomName || '未知'} (${roomDetail.roomId})`);
  } else {
    // 添加新群
    entries.push(roomEntry);
    logger.info(`添加新群: ${roomDetail.roomName || '未知'} (${roomDetail.roomId})`);
  }

  saveRoomUsers(entries);
}

/**
 * 获取群详情并保存
 * 
 * @param roomId 群ID
 * @returns 是否成功
 */
export async function fetchAndSaveRoomDetail(roomId: string, botConfig: BotConfig): Promise<boolean> {
  try {
    logger.info(`开始获取群详情: ${roomId}`);
    
    const response = await batchGetRoomDetail([roomId], botConfig.deviceGuid, botConfig.token);
    
    if (response.code !== 0 || !response.data || response.data.roomList.length === 0) {
      logger.error(`❌ 获取群详情失败: ${response.msg}`);
      return false;
    }

    const roomDetail = response.data.roomList[0];
    
    // 检查返回的群详情是否有效
    if (!roomDetail.roomId || roomDetail.roomId.trim() === '') {
      logger.warn(`❌ 获取的群详情无效: roomId 为空，可能是 bot 不在该群中或群ID错误`);
      return false;
    }
    
    // 检查是否有成员列表（memberList 为 null 时给出警告但继续处理）
    if (!roomDetail.memberList || roomDetail.memberList.length === 0) {
      logger.warn(`⚠️ 群 ${roomDetail.roomId} 的成员列表为空，将保存空的成员列表`);
    }
    
    upsertRoom(roomDetail);
    
    return true;
  } catch (error: any) {
    logger.error(`❌ 获取并保存群详情异常:`, error);
    return false;
  }
}

/**
 * 解码 base64 编码的成员列表
 * changedMemberList 格式：base64编码的字符串，解码后是用分号分隔的 userId 列表
 */
function decodeMemberList(base64List: string): string[] {
  if (!base64List) {
    return [];
  }

  try {
    const decoded = Buffer.from(base64List, 'base64').toString('utf-8');
    // 解码后可能是用分号分隔的 userId 列表
    return decoded.split(';').filter(id => id.trim().length > 0);
  } catch (error) {
    logger.error('解码成员列表失败:', error);
    return [];
  }
}

/**
 * 获取新加入的成员信息（排除机器人自己）
 */
function getNewMembers(roomDetail: RoomDetail, changedMemberIds: string[], botUserId: string | null): RoomMember[] {
  return roomDetail.memberList.filter(member => {
    // 排除机器人自己
    if (botUserId && member.userId === botUserId) {
      return false;
    }
    // 只返回在变动列表中的成员
    return changedMemberIds.includes(member.userId);
  });
}

/**
 * 检查成员是否设置了群昵称
 * 如果 roomRemarkName 为空或等于 name，则认为没有设置群昵称
 * 注意：roomRemarkName 是本群备注（仅自己可见），name 是本群昵称
 */
function hasNoAlias(member: RoomMember): boolean {
  // 如果 name 为空或只有空格，认为没有设置群昵称
  if (!member.name || member.name.trim() === '') {
    return true;
  }
  
  // 如果 name 看起来像是默认的（比如全是数字或特殊字符），也可能没有设置
  // 这里简化处理：如果 name 和 userId 相同，认为没有设置群昵称
  // 实际判断可能需要更复杂的逻辑，但先这样处理
  return member.name === member.userId;
}

/**
 * 处理群成员变动
 * 当权限群中增加新成员时，更新 room_users.json 并发送欢迎语
 * 
 * @param roomId 群ID
 * @param msgType 消息类型: 1002-新增 1003-移除 1005-退群
 * @param changedMemberList base64编码的变动成员列表（可选）
 * @returns 是否成功处理
 */
export async function handleRoomMemberChange(
  roomId: string | number, 
  msgType: number,
  changedMemberList: string | undefined,
  botConfig: BotConfig
): Promise<boolean> {
  const roomIdStr = roomId.toString();
  
  // 只有权限群才需要更新
  if (!roomExists(roomIdStr)) {
    logger.debug(`群 ${roomIdStr} 不在权限列表中，跳过更新`);
    return false;
  }

  // 对于新增成员、移除成员、退群，都需要更新群信息
  // 因为成员列表已经发生变化
  const msgTypeName = msgType === 1002 ? '新增成员' : msgType === 1003 ? '移除成员' : '成员退群';
  logger.info(`检测到权限群 ${roomIdStr} ${msgTypeName}，开始更新群信息`);

  // 重新获取群详情并更新
  const success = await fetchAndSaveRoomDetail(roomIdStr, botConfig);
  
  if (!success) {
    logger.error(`❌ 更新群 ${roomIdStr} 的成员信息失败`);
    return false;
  }

  logger.info(`✅ 已更新群 ${roomIdStr} 的成员信息`);

  // 移除成员（1003）和成员退群（1005）时，只更新配置，不发送消息
  if (msgType === 1003 || msgType === 1005) {
    logger.info(`用户离开群聊，仅更新配置，不发送消息`);
    return true;
  }

  // 只有新增成员（1002）时才发送欢迎语和昵称提醒
  if (msgType === 1002 && changedMemberList) {
    try {
      // 解码变动成员列表
      const changedMemberIds = decodeMemberList(changedMemberList);
      logger.debug(`变动成员ID列表: ${changedMemberIds.join(', ')}`);

      if (changedMemberIds.length === 0) {
        logger.debug(`未解析到变动成员，跳过欢迎语`);
        return true;
      }

      // 重新获取群详情以获取最新成员信息
      const response = await batchGetRoomDetail([roomIdStr], botConfig.deviceGuid, botConfig.token);
      if (response.code !== 0 || !response.data || response.data.roomList.length === 0) {
        logger.error(`❌ 获取群详情失败，无法发送欢迎语`);
        return true;
      }

      const roomDetail = response.data.roomList[0];
      
      // 获取机器人userId（用于排除自己）
      let botUserId: string | null = null;
      try {
        const userStatus = await getUserStatus(botConfig.deviceGuid, botConfig.token);
        if (userStatus.code === 0 && userStatus.data?.wxid) {
          botUserId = userStatus.data.wxid;
        }
      } catch (error) {
        logger.warn(`获取机器人userId失败，将不排除自己:`, error);
      }
      
      // 获取新加入的成员（排除机器人自己）
      const newMembers = getNewMembers(roomDetail, changedMemberIds, botUserId);
      
      if (newMembers.length === 0) {
        logger.debug(`没有新成员需要欢迎（可能都是机器人）`);
        return true;
      }

      if (!botConfig.deviceGuid) {
        logger.error(`❌ Bot ${botConfig.botId} 的设备GUID不存在，无法发送欢迎语`);
        return true;
      }

      // 1. 发送欢迎语并@新成员
      const welcomeText = staticConfig?.room_speech?.person_join || '欢迎加入数字社区！';
      const newMemberIds = newMembers.map(m => m.userId);
      
      try {
        await sendMessage(roomIdStr, welcomeText, newMemberIds, botConfig.deviceGuid, botConfig.token);
        logger.info(`✅ 已发送欢迎语并@${newMembers.length}位新成员`);
      } catch (error) {
        logger.error(`❌ 发送欢迎语失败:`, error);
      }

      // 2. 检查新成员是否设置了群昵称
      const noAliasMembers = newMembers.filter(hasNoAlias);
      
      if (noAliasMembers.length > 0) {
        const modifyRemarksText = staticConfig?.room_speech?.modify_remarks || '请您及时按群主要求设定昵称哦，谢谢配合[玫瑰]';
        const noAliasMemberIds = noAliasMembers.map(m => m.userId);
        
        try {
          await sendMessage(roomIdStr, modifyRemarksText, noAliasMemberIds, botConfig.deviceGuid, botConfig.token);
          logger.info(`✅ 已提醒${noAliasMembers.length}位未设置群昵称的成员`);
        } catch (error) {
          logger.error(`❌ 发送昵称提醒失败:`, error);
        }
      } else {
        logger.debug(`所有新成员都已设置群昵称`);
      }

    } catch (error: any) {
      logger.error(`❌ 处理新成员欢迎语异常:`, error);
      // 即使欢迎语发送失败，也不影响群信息更新
    }
  }

  return true;
}

