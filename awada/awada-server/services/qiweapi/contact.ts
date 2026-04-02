/**
 * qiweapi 联系人模块
 * 负责联系人管理、好友申请处理
 */

import { apiClient } from './client';
import { ApiResponse, AcceptFriendParams, API_METHODS } from './types';

/**
 * 同意好友申请
 * method: /contact/agreeContact
 *
 * @param userId 申请者用户ID
 * @param corpId 企业ID
 * @param guid 设备GUID（可选）
 */
export const agreeContact = async (userId: string, corpId: string, guid: string, token: string): Promise<ApiResponse<void>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: undefined as any
    };
  }
  const deviceGuid = guid;

  console.log(`[Contact] 同意好友申请: userId=${userId}, corpId=${corpId}`);

  const params: AcceptFriendParams = {
    guid: deviceGuid,
    userId,
    corpId
  };

  const response = await apiClient.call<void, AcceptFriendParams>(API_METHODS.AGREE_CONTACT, params, token);

  if (response.code === 0) {
    console.log('[Contact] ✅ 好友申请已同意');
  } else {
    console.error('[Contact] ❌ 同意好友申请失败:', response.msg);
  }

  return response;
};

/** @deprecated 使用 agreeContact 代替 */
export const acceptFriend = agreeContact;

export default {
  agreeContact,
  acceptFriend
};
