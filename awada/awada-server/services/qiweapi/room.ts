/**
 * qiweapi 群模块
 * 负责群详情获取、群信息管理
 */

import { apiClient } from './client';
import { ApiResponse } from './types';

// ==================== 类型定义 ====================

/** 群成员信息 */
export interface RoomMember {
  inviterId: number;
  isAdmin: number;
  joinTime: number;
  name: string; // 本群昵称
  userId: string;
  roomRemarkName: string; // 本群备注(仅自己可见)
}

/** 群详情信息 */
export interface RoomDetail {
  memberList: RoomMember[];
  roomCreateTime: string;
  roomCreateUserId: string;
  roomExtType: number;
  roomId: string;
  roomName: string;
  roomAnnouncement: string;
  roomEnableInviteConfirm: number;
  roomIsForbidChangeName: number;
}

/** 批量获取群详情请求参数 */
export interface BatchGetRoomDetailParams {
  guid: string;
  roomIdList: string[];
}

/** 批量获取群详情响应数据 */
export interface BatchGetRoomDetailData {
  roomList: RoomDetail[];
}

// ==================== API 方法 ====================

/**
 * 批量获取群详情
 * method: /room/batchGetRoomDetail
 *
 * @param roomIdList 群ID列表
 * @param guid 设备GUID
 * @param token Token（多 Bot 支持）
 */
export const batchGetRoomDetail = async (roomIdList: string[], guid: string, token: string): Promise<ApiResponse<BatchGetRoomDetailData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: { roomList: [] }
    };
  }

  if (!token) {
    return {
      code: -1,
      msg: 'Token 必须通过参数传递',
      data: { roomList: [] }
    };
  }

  if (!roomIdList || roomIdList.length === 0) {
    return {
      code: -1,
      msg: '群ID列表不能为空',
      data: { roomList: [] }
    };
  }

  console.log(`[Room] 批量获取群详情: roomIds=${roomIdList.join(',')}`);

  const params: BatchGetRoomDetailParams = {
    guid: guid,
    roomIdList
  };

  const response = await apiClient.call<BatchGetRoomDetailData, BatchGetRoomDetailParams>('/room/batchGetRoomDetail', params, token);

  if (response.code === 0 && response.data) {
    console.log(`[Room] ✅ 成功获取 ${response.data.roomList.length} 个群详情`);
  } else {
    console.error(`[Room] ❌ 获取群详情失败: ${response.msg}`);
  }

  return response;
};
