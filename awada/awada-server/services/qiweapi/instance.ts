/**
 * qiweapi 实例管理模块
 * 负责设备创建、恢复、停止
 */

import { apiClient } from './client';
import qiweapiConfig from '@/config/qiweapi';
import { ApiResponse, CreateClientParams, CreateClientData, RecoverClientParams, StopClientParams, SetCallbackParams, API_METHODS } from './types';

/**
 * 创建设备实例
 *
 * 说明：
 * - 使用此API登录，每次都会验证6位code码
 * - 为避免频繁验证，推荐使用 recoverClient 来替代
 * - guid 可以自行生成，如时间戳+业务规则+随机数 => md5 => uuid
 * - 一个实例(guid)可以理解为一个设备
 *
 * @param options 创建选项
 */
export const createClient = async (options?: { deviceName?: string; deviceType?: number; clientVersion?: string; areaCode?: number; proxyUrl?: string; token: string }): Promise<ApiResponse<CreateClientData>> => {
  const { token } = options || {};
  console.log('[Instance] 创建设备实例...');

  if (!token) {
    return {
      code: -1,
      msg: 'Token 必须通过参数传递',
      data: {} as CreateClientData
    };
  }
  const params: CreateClientParams = {
    deviceName: options?.deviceName || `chatbot-${Date.now()}`,
    deviceType: options?.deviceType ?? qiweapiConfig.defaultDeviceType,
    clientVersion: options?.clientVersion || qiweapiConfig.defaultClientVersion,
    areaCode: options?.areaCode || qiweapiConfig.defaultAreaCode,
    proxyUrl: options?.proxyUrl || ''
  };

  const response = await apiClient.call<CreateClientData, CreateClientParams>(API_METHODS.CREATE_CLIENT, params, token);

  if (response.code === 0 && response.data?.guid) {
    console.log(`[Instance] ✅ 设备创建成功, GUID: ${response.data.guid}`);
  } else {
    console.error('[Instance] ❌ 设备创建失败:', response.msg);
  }

  return response;
};

/**
 * 恢复设备实例
 *
 * 说明：
 * - 推荐使用此接口代替 createClient，可避免频繁验证
 * - 在已登录过的实例上重新登录，可以免验证码登录
 *
 * @param guid 设备GUID（可选，默认使用配置中的GUID）
 */
export const recoverClient = async (guid: string, token: string): Promise<ApiResponse<void>> => {
  console.log(`[Instance] 恢复实例: ${guid}`);

  const params: RecoverClientParams = {
    guid: guid
  };

  const response = await apiClient.call<void, RecoverClientParams>(API_METHODS.RECOVER_CLIENT, params, token);

  if (response.code === 0) {
    console.log('[Instance] ✅ 实例恢复成功');
  } else {
    console.error('[Instance] ❌ 实例恢复失败:', response.msg);
  }

  return response;
};

/**
 * 停止设备实例
 *
 * @param guid 设备GUID（可选，默认使用配置中的GUID）
 */
export const stopClient = async (guid: string, token: string): Promise<ApiResponse<void>> => {
  console.log(`[Instance] 停止实例: ${guid}`);

  const params: StopClientParams = {
    guid: guid
  };

  const response = await apiClient.call<void, StopClientParams>(API_METHODS.STOP_CLIENT, params, token);

  if (response.code === 0) {
    console.log('[Instance] ✅ 实例已停止');
  } else {
    console.error('[Instance] ❌ 停止实例失败:', response.msg);
  }

  return response;
};

/**
 * 设置消息回调地址
 * method: /client/setCallback
 *
 * 说明：
 * - 回调按用户token来推送消息，该token下的所有账号消息都会推送到此URL
 * - 各租户间的消息有数据隔离
 *
 * @param callbackUrl 回调URL
 */
export const setCallbackUrl = async (callbackUrl: string, token: string): Promise<ApiResponse<void>> => {
  console.log(`[Instance] 设置回调地址: ${callbackUrl}`);

  const response = await apiClient.call<void, { callbackUrl: string }>(API_METHODS.SET_CALLBACK, { callbackUrl }, token);

  if (response.code === 0) {
    console.log('[Instance] ✅ 回调地址设置成功');
    qiweapiConfig.callbackUrl = callbackUrl;
  } else {
    console.error('[Instance] ❌ 设置回调地址失败:', response.msg);
  }

  return response;
};

export default {
  createClient,
  recoverClient,
  stopClient,
  setCallbackUrl
};
