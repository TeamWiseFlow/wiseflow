/**
 * WorkTool 机器人管理模块
 * 根据 OpenAPI 文档实现
 */

import { worktoolClient } from './client';
import { ApiResponse, RobotInfo, RobotOnlineStatus, SetCallbackParams } from './types';
import { createLogger } from '../../src/utils/logger';

const logger = createLogger('WorkTool-Robot');

/**
 * 获取机器人信息
 * GET /robot/robotInfo/get
 * 
 * @param robotId 机器人ID
 * @param key 校验码（可选）
 */
export const getRobotInfo = async (
  robotId: string,
  key?: string
): Promise<ApiResponse<RobotInfo>> => {
  logger.debug(`获取机器人信息: ${robotId}`);
  
  const params: Record<string, string> = { robotId };
  if (key) {
    params.key = key;
  }

  const response = await worktoolClient.get<RobotInfo>('/robot/robotInfo/get', params);

  if (response.code === 200 && response.data) {
    logger.info(`✅ 机器人信息获取成功: ${response.data.name} (${response.data.robotId})`);
  } else {
    logger.error(`❌ 机器人信息获取失败: ${response.message}`);
  }

  return response;
};

/**
 * 查询机器人是否在线
 * GET /robot/robotInfo/online
 * 
 * @param robotId 机器人ID
 */
export const checkRobotOnline = async (
  robotId: string
): Promise<ApiResponse<RobotOnlineStatus>> => {
  logger.debug(`查询机器人在线状态: ${robotId}`);
  
  const response = await worktoolClient.get<RobotOnlineStatus>('/robot/robotInfo/online', {
    robotId
  });

  if (response.code === 200) {
    logger.info(`✅ 机器人在线状态查询成功`);
  } else {
    logger.error(`❌ 机器人在线状态查询失败: ${response.message}`);
  }

  return response;
};

/**
 * 设置机器人消息回调配置
 * POST /robot/robotInfo/update
 * 
 * 文档: https://www.apifox.cn/apidoc/project-1035094/doc-861677
 * 
 * @param robotId 机器人ID
 * @param params 回调配置参数
 * @param key 校验码（可选）
 */
export const setCallback = async (
  robotId: string,
  params: SetCallbackParams,
  key?: string
): Promise<ApiResponse<null>> => {
  logger.debug(`设置机器人回调配置: ${robotId}`);
  logger.debug(`回调地址: ${params.callbackUrl || '未设置'}`);
  logger.debug(`开启回调: ${params.openCallback === 1 ? '是' : '否'}`);
  logger.debug(`回复策略: ${params.replyAll}`);
  
  const queryParams: Record<string, string> = { robotId };
  if (key) {
    queryParams.key = key;
  }

  const response = await worktoolClient.post<null>(
    '/robot/robotInfo/update',
    params,
    { params: queryParams }
  );

  if (response.code === 200) {
    logger.info(`✅ 机器人回调配置设置成功`);
    if (params.callbackUrl) {
      logger.info(`   回调地址: ${params.callbackUrl}`);
    }
  } else {
    logger.error(`❌ 机器人回调配置设置失败: ${response.message}`);
  }

  return response;
};

