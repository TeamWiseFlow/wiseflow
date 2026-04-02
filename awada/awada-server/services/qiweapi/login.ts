/**
 * qiweapi 登录模块
 * 负责二维码获取、状态检测、登录验证
 */

import { apiClient } from './client';
import { ApiResponse, GetLoginQrcodeParams, GetLoginQrcodeData, CheckLoginParams, CheckLoginData, CheckQrCodeParams, LoginParams, GetUserStatusParams, UserStatusData, GetProfileData, API_METHODS } from './types';
import { createLogger } from '../../src/utils/logger';

const logger = createLogger('QiweAPI-Login');

// 解构 API_METHODS 以支持新旧常量名
const { VERIFY_QRCODE } = API_METHODS;

/**
 * 登录状态枚举
 * 对应 loginQrcodeStatus 字段
 */
export enum LoginStatus {
  /** 登录状态失效，需要重新扫码登陆 */
  INVALID = -1,
  /** 未登陆，可免扫码登陆 */
  NOT_LOGGED_IN = 0,
  /** 已扫码，待确认 */
  SCANNED = 1,
  /** 登陆成功 */
  SUCCESS = 2,
  /** 登陆失败 */
  FAILED = 3,
  /** 用户取消登陆 */
  CANCELLED = 4,
  /** 已扫码确认，待检测6位验证码 */
  NEED_CODE = 10
}

/** 当前登录信息 */
let currentUser: UserStatusData | null = null;
let isLoggedIn = false;

/**
 * 获取登录二维码
 * method: /login/getLoginQrcode
 *
 * 说明：
 * - 当旧设备取码提示"guid错误: 客户端实例不存在/不在线"时
 * - 需先调用 recoverClient 接口，调用成功后再次执行取码接口
 *
 * 两种模式：
 * - useCache=false（默认）: 主动扫码模式，强制获取新的登录二维码
 * - useCache=true: 被动确认模式，推送登录授权消息到手机端
 *
 * @param options 配置选项
 * @param options.guid 设备GUID（可选，默认使用配置中的GUID）
 * @param options.useCache 是否使用缓存（可选，默认false）
 */
export const getLoginQrcode = async (options: { guid: string; useCache?: boolean; token: string }): Promise<ApiResponse<GetLoginQrcodeData>> => {
  const { guid, useCache = false, token } = options;
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {} as GetLoginQrcodeData
    };
  }

  const mode = useCache ? '被动确认模式' : '主动扫码模式';
  logger.info(`获取登录二维码 (${mode})...`);

  const params: GetLoginQrcodeParams = {
    guid: guid,
    useCache
  };

  const response = await apiClient.call<GetLoginQrcodeData, GetLoginQrcodeParams>(API_METHODS.GET_LOGIN_QRCODE, params, token);

  if (response.code === 0 && response.data) {
    logger.info('✅ 二维码获取成功');
    logger.debug(`QrcodeKey: ${response.data.loginQrcodeKey}`);
    if (response.data.loginQrcodeBase64Data) {
      logger.debug(`二维码数据长度: ${response.data.loginQrcodeBase64Data.length}`);
    } else {
      logger.info('无二维码数据（被动确认模式，请在手机端确认）');
    }
  } else {
    logger.error('❌ 获取二维码失败:', response.msg);
  }

  return response;
};

/**
 * 检测登录状态
 * method: /login/checkLoginQrCode
 *
 * @param guid 设备GUID（可选）
 */
export const checkLogin = async (guid: string, token: string): Promise<ApiResponse<CheckLoginData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID不存在',
      data: {} as CheckLoginData
    };
  }

  const params: CheckLoginParams = {
    guid: guid
  };

  const response = await apiClient.call<CheckLoginData, CheckLoginParams>(API_METHODS.CHECK_LOGIN, params, token);

  if (response.code === 0 && response.data) {
    const statusMap: Record<number, string> = {
      [LoginStatus.INVALID]: '登录状态失效，需重新扫码',
      [LoginStatus.NOT_LOGGED_IN]: '未登陆，可免扫码登陆',
      [LoginStatus.SCANNED]: '已扫码，待确认',
      [LoginStatus.SUCCESS]: '登陆成功',
      [LoginStatus.FAILED]: '登陆失败',
      [LoginStatus.CANCELLED]: '用户取消登陆',
      [LoginStatus.NEED_CODE]: '已扫码确认，待检测6位验证码'
    };
    const status = response.data.loginQrcodeStatus;
    logger.debug(`登录状态: ${statusMap[status] || `未知(${status})`}`);

    if (response.data.nickname) {
      logger.debug(`用户: ${response.data.nickname} (${response.data.userId})`);
    }
  }

  return response;
};

/**
 * 二维码 code 验证
 * method: /login/verifyLoginQrcode
 *
 * 说明：
 * - 只有新实例登录时才需要调用
 * - 验证码验证成功后需再次调用 checkLogin 接口即可登录成功
 *
 * @param code 6位登录验证码
 * @param guid 设备GUID（可选）
 */
export const verifyQrCode = async (code: string, guid: string, token: string): Promise<ApiResponse<void>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID不存在',
      data: undefined as any
    };
  }

  logger.info(`验证登录码: ${code}`);

  const params: CheckQrCodeParams = {
    guid: guid,
    code
  };

  const response = await apiClient.call<void, CheckQrCodeParams>(API_METHODS.VERIFY_QRCODE, params, token);

  if (response.code === 0) {
    logger.info('✅ 验证码验证成功，请再次调用 checkLogin 完成登录');
  } else {
    logger.error('❌ 验证码验证失败:', response.msg);
  }

  return response;
};

/** @deprecated 使用 verifyQrCode 代替 */
export const checkQrCode = verifyQrCode;

/**
 * 用户登录
 * 无特殊情况下，demo调试时无需调用此接口
 *
 * @param guid 设备GUID（可选）
 */
export const login = async (guid: string, token: string): Promise<ApiResponse<UserStatusData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID不存在',
      data: {} as UserStatusData
    };
  }

  logger.info('执行登录...');

  const params: LoginParams = {
    guid: guid
  };

  const response = await apiClient.call<UserStatusData, LoginParams>(API_METHODS.LOGIN, params, token);

  if (response.code === 0 && response.data) {
    isLoggedIn = true;
    currentUser = response.data;
    logger.info(`✅ 登录成功! 用户: ${response.data.nickName} (${response.data.wxid})`);
  } else {
    logger.error('❌ 登录失败:', response.msg);
  }

  return response;
};

/**
 * 获取用户信息/状态
 * method: /user/getProfile
 *
 * @param guid 设备GUID（可选）
 */
export const getUserStatus = async (guid: string, token: string): Promise<ApiResponse<UserStatusData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID不存在',
      data: {} as UserStatusData
    };
  }

  if (!token) {
    return {
      code: -1,
      msg: 'Token 必须通过参数传递',
      data: {} as UserStatusData
    };
  }

  const params: GetUserStatusParams = {
    guid: guid
  };

  // 调用 /user/getProfile API
  const response = await apiClient.call<GetProfileData, GetUserStatusParams>(API_METHODS.GET_USER_PROFILE, params, token);

  // 将 GetProfileData 转换为 UserStatusData
  if (response.code === 0 && response.data) {
    const profileData = response.data;
    const userStatusData: UserStatusData = {
      wxid: profileData.userId,
      nickName: profileData.nickname,
      headImgUrl: profileData.avatarUrl,
      online: !!profileData.userId, // 如果有 userId，则认为在线
      corpId: profileData.corpId
    };

    isLoggedIn = !!userStatusData.wxid;
    if (isLoggedIn) {
      currentUser = userStatusData;
      logger.info(`用户在线: ${userStatusData.nickName} (${userStatusData.wxid})`);
    } else {
      logger.info('用户离线');
    }

    return {
      code: response.code,
      msg: response.msg,
      data: userStatusData
    };
  }

  // 如果 API 调用失败，返回错误响应
  return {
    code: response.code,
    msg: response.msg,
    data: {} as UserStatusData
  };
};

/**
 * 轮询等待登录完成
 *
 * @param options 配置选项
 */
export const waitForLogin = async (options: {
  guid: string;
  /** 轮询间隔（毫秒），默认2000 */
  interval?: number;
  /** 超时时间（毫秒），默认120000 */
  timeout?: number;
  /** 状态回调 */
  onStatusChange?: (status: LoginStatus, data?: CheckLoginData) => void;
  token: string;
}): Promise<ApiResponse<UserStatusData>> => {
  const { guid, interval = 2000, timeout = 120000, onStatusChange, token } = options;

  const startTime = Date.now();
  let lastStatus: LoginStatus | null = null;

  logger.info('开始轮询登录状态...');

  while (Date.now() - startTime < timeout) {
    const checkResult = await checkLogin(guid, token);

    if (checkResult.code !== 0 || !checkResult.data) {
      logger.error('检测状态失败:', checkResult.msg);
      await sleep(interval);
      continue;
    }

    const status = checkResult.data.loginQrcodeStatus;

    // 状态变化时触发回调
    if (status !== lastStatus) {
      lastStatus = status;
      onStatusChange?.(status, checkResult.data);
    }

    switch (status) {
      case LoginStatus.SUCCESS:
        // 登录成功
        logger.info('✅ 登录成功!');
        // 更新本地状态
        isLoggedIn = true;
        if (checkResult.data.nickname && checkResult.data.userId) {
          currentUser = {
            wxid: checkResult.data.userId,
            nickName: checkResult.data.nickname,
            headImgUrl: checkResult.data.avatarUrl
          };
        }
        return {
          code: 0,
          msg: '登录成功',
          data: currentUser || ({} as UserStatusData)
        };

      case LoginStatus.FAILED:
        return {
          code: -1,
          msg: '登录失败',
          data: {} as UserStatusData
        };

      case LoginStatus.CANCELLED:
        return {
          code: -1,
          msg: '用户取消了登录',
          data: {} as UserStatusData
        };

      case LoginStatus.INVALID:
        return {
          code: -1,
          msg: '登录状态失效，需要重新扫码',
          data: {} as UserStatusData
        };

      case LoginStatus.NEED_CODE:
        // 需要验证码，提示用户
        logger.warn('⚠️ 需要输入6位验证码');
        // 这里需要用户调用 checkQrCode 接口提交验证码
        break;

      case LoginStatus.NOT_LOGGED_IN:
      case LoginStatus.SCANNED:
        // 继续等待
        break;

      default:
        logger.warn(`未知状态: ${status}`);
    }

    await sleep(interval);
  }

  return {
    code: -1,
    msg: '登录超时',
    data: {} as UserStatusData
  };
};

/**
 * 获取当前登录状态
 */
export const getLoginStatus = () => ({
  isLoggedIn,
  currentUser
});

/**
 * 获取当前用户信息
 */
export const getCurrentUser = () => currentUser;

/**
 * 设置登录状态（用于回调更新）
 */
export const setLoginStatus = (status: boolean, user?: UserStatusData) => {
  isLoggedIn = status;
  if (user) {
    currentUser = user;
  }
};

/** 辅助函数：延时 */
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export default {
  getLoginQrcode,
  checkLogin,
  checkQrCode,
  login,
  getUserStatus,
  waitForLogin,
  getLoginStatus,
  getCurrentUser,
  setLoginStatus,
  LoginStatus
};
