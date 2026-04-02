/**
 * 好友申请处理服务
 * 参考 wechaty 项目的逻辑实现
 *
 * 功能：
 * 1. 检查用户权限（是否在权限群组中或导演列表中）
 * 2. 自动同意权限用户的好友申请
 * 3. 保存打招呼消息（用于后续过滤）
 * 4. 发送欢迎语
 */

import { FriendApplyCallback } from '@/services/qiweapi/types';
import { agreeContact } from '@/services/qiweapi/contact';
import { sendTextMsg } from '@/services/qiweapi/message';
import { needPermission, staticConfig } from '@/config';
import { readRoomUsers } from '../room';
import { getUserStatus } from '@/services/qiweapi/login';
import { BotConfig } from '@/config/bots';

// ==================== 打招呼消息存储 ====================

/** 打招呼消息映射表：userId -> helloMessage */
const HelloMap: { [key: string]: string } = {};

/**
 * 打招呼消息管理器
 */
export const Hello = {
  /** 获取打招呼消息 */
  get: (userId?: string): string | { [key: string]: string } => {
    if (userId) {
      return HelloMap[userId] || '';
    }
    return HelloMap;
  },
  /** 添加打招呼消息 */
  add: (userId: string, text: string): void => {
    HelloMap[userId] = text;
    console.log(`[Friendship] 保存打招呼消息: ${userId} -> ${text}`);
  },
  /** 移除打招呼消息 */
  remove: (userId: string): void => {
    delete HelloMap[userId];
    console.log(`[Friendship] 清除打招呼消息: ${userId}`);
  }
};

// ==================== 权限检查 ====================

/**
 * 检查用户是否有权限（是否在权限群组中或导演列表中）
 *
 * @param userId 用户ID
 * @returns 是否有权限
 */
function hasPermission(userId: string): boolean {
  // 检查是否是导演
  if (staticConfig?.directors?.includes(userId)) {
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
 * 获取权限用户列表（用于调试）
 */
export function getPermissionUsers(userId?: string): { users: string[]; permission: boolean } {
  const directors = staticConfig?.directors || [];
  const roomUsers = readRoomUsers();
  const allMemberIds = roomUsers.reduce<string[]>((acc, entry) => {
    if (entry.room?.memberIdList) {
      return [...acc, ...entry.room.memberIdList];
    }
    return acc;
  }, []);

  const allUsers = [...directors, ...allMemberIds];
  const permission = userId ? hasPermission(userId) : false;

  return { users: allUsers, permission };
}

// ==================== 好友申请处理 ====================

/**
 * 处理好友申请
 *
 * 逻辑：
 * 1. 检查用户是否在权限列表中
 * 2. 如果在权限列表中，自动同意申请
 * 3. 保存打招呼消息（如果有）
 * 4. 同意后发送欢迎语
 *
 * @param callback 好友申请回调
 */
export async function onFriendApply(callback: FriendApplyCallback, botConfig: BotConfig): Promise<void> {
  const { contactId, contactNickname, contactType, guid, userId } = callback;
  const contactIdStr = String(contactId);
  const { token } = botConfig;

  console.log(`[Friendship] 👋 收到好友申请`);
  console.log(`[Friendship] 联系人: ${contactNickname} (${contactType})`);
  console.log(`[Friendship] 联系人ID: ${contactIdStr}`);

  try {
    // 检查用户权限
    const hasPerm = hasPermission(contactIdStr);

    if (hasPerm || !needPermission) {
      console.log(`[Friendship] ✅ 用户是权限用户，自动同意好友申请`);

      // 获取当前用户信息（用于同意申请时需要的 corpId）
      // 使用 checkLogin 获取 corpId，因为 UserStatusData 中没有 corpId 字段
      const loginStatus = await getUserStatus(guid, token);
      if (loginStatus.code !== 0 || !loginStatus.data) {
        console.error(`[Friendship] ❌ 获取登录状态失败: ${loginStatus.msg}`);
        return;
      }

      const corpId = loginStatus.data.corpId;
      if (!corpId) {
        console.error(`[Friendship] ❌ 无法获取 corpId`);
        return;
      }

      // 保存打招呼消息（如果有的话，目前 FriendApplyMsgData 中没有 hello 字段，先留空）
      // 如果后续有打招呼消息，可以从 msgData 中提取
      const helloMessage = ''; // TODO: 从 msgData 中提取打招呼消息
      if (helloMessage) {
        Hello.add(contactIdStr, helloMessage);
      }

      // 同意好友申请
      const agreeResult = await agreeContact(contactIdStr, String(corpId), guid, token);

      if (agreeResult.code === 0) {
        console.log(`[Friendship] ✅ 好友申请已同意: ${contactNickname}`);

        // 发送欢迎语
        const welcomeMessage = staticConfig?.person_speech?.welcome || '欢迎！';
        await sendTextMsg(contactIdStr, welcomeMessage, guid, token);

        console.log(`[Friendship] ✅ 已发送欢迎语给: ${contactNickname}`);
      } else {
        console.error(`[Friendship] ❌ 同意好友申请失败: ${agreeResult.msg}`);
      }
    } else {
      console.log(`[Friendship] ⚠️ 用户不是权限用户，不自动同意好友申请`);
    }
  } catch (error: any) {
    console.error(`[Friendship] ❌ 处理好友申请异常:`, error);
  }
}

/**
 * 处理好友确认（好友添加成功）
 *
 * 注意：目前 QiweAPI 可能没有好友确认的系统消息，
 * 所以这个函数可能不会被调用。欢迎语在同意申请时已经发送。
 *
 * @param userId 用户ID
 * @param contactId 联系人ID
 */
export async function onFriendConfirm(userId: string, contactId: string): Promise<void> {
  console.log(`[Friendship] ✅ 好友确认: ${contactId}`);

  // 如果之前没有发送欢迎语，这里可以发送
  // 但由于我们在同意申请时已经发送了，这里可能不需要
}

export default {
  onFriendApply,
  onFriendConfirm,
  Hello,
  getPermissionUsers
};
