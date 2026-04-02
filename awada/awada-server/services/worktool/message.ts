/**
 * WorkTool 消息发送模块
 * 根据 OpenAPI 文档实现
 * 文档: 
 * - 发送消息: https://doc.worktool.ymdyes.cn/api-23520034.md
 * - 批量发送指令: https://doc.worktool.ymdyes.cn/api-147612959.md
 * - 推送微盘文件: https://doc.worktool.ymdyes.cn/api-23521804.md
 */

import { worktoolClient } from './client';
import { ApiResponse } from './types';
import { createLogger } from '../../src/utils/logger';

const logger = createLogger('WorkTool-Message');

/**
 * 发送文本消息请求参数
 * 根据 OpenAPI 文档：POST /wework/sendRawMessage
 */
export interface SendTextMessageParams {
  /** 接收者列表（昵称或群名） */
  titleList: string[];
  /** 消息内容（\n换行） */
  receivedContent: string;
  /** @的人列表（可选，at所有人用"@所有人"） */
  atList?: string[];
}

/**
 * 发送文本消息
 * POST /wework/sendRawMessage
 * 
 * 文档: https://doc.worktool.ymdyes.cn/api-23520034.md
 * 
 * 注意：
 * 1. at所有人可以填入"@所有人"（应为群主或群管理）
 * 2. 减号- 空格和英文括号()和@符号为保留字请勿在人名/群名/备注名中使用
 * 3. 群名定义尽量短，一般不要超过12个汉字
 * 4. 存在重名问题考虑设置好友备注名或群备注名
 * 5. 建议titleList仅填一个，因为有失败重试机制，防止多个批量重试导致重发
 * 6. 指令接口IP请求限流为60QPM
 * 
 * @param robotId 机器人ID
 * @param params 消息参数
 */
export const sendTextMessage = async (
  robotId: string,
  params: SendTextMessageParams
): Promise<ApiResponse<string>> => {
  logger.debug(`发送文本消息 -> ${params.titleList.join(', ')}`);
  logger.debug(`内容: ${params.receivedContent.substring(0, 50)}${params.receivedContent.length > 50 ? '...' : ''}`);
  if (params.atList && params.atList.length > 0) {
    logger.debug(`@列表: ${params.atList.join(', ')}`);
  }

  // 构建请求体（根据 OpenAPI 文档）
  const requestBody = {
    socketType: 2, // 固定值=2，通讯类型
    list: [
      {
        type: 203, // 固定值=203，消息类型
        titleList: params.titleList, // 昵称或群名
        receivedContent: params.receivedContent, // 发送文本内容（\n换行）
        ...(params.atList && params.atList.length > 0 ? { atList: params.atList } : {}) // @的人（可选）
      }
    ]
  };

  // 调用发送消息接口
  const response = await worktoolClient.post<string>(
    '/wework/sendRawMessage',
    requestBody,
    { params: { robotId } }
  );

  if (response.code === 200) {
    logger.info(`✅ WorkTool 文本消息发送成功`);
    if (response.data) {
      // data 字段是 messageId (string)
      logger.debug(`   消息ID: ${response.data}`);
    }
  } else {
    logger.error(`❌ WorkTool 文本消息发送失败: ${response.message}`);
  }

  return response;
};

/**
 * 推送微盘文件请求参数
 * 根据 OpenAPI 文档：POST /wework/sendRawMessage (type=209)
 */
export interface SendMicroDiskFileParams {
  /** 接收者列表（昵称或群名） */
  titleList: string[];
  /** 文件名称（微盘里存在） */
  objectName: string;
  /** 附加留言（选填） */
  extraText?: string;
}

/**
 * 推送微盘文件
 * POST /wework/sendRawMessage
 * 
 * 文档: https://doc.worktool.ymdyes.cn/api-23521804.md
 * 
 * 注意：
 * 1. 如果好友昵称改过备注则只能使用备注名调用
 * 2. objectName 必须是微盘中存在的文件名称
 * 
 * @param robotId 机器人ID
 * @param params 微盘文件参数
 */
export const sendMicroDiskFile = async (
  robotId: string,
  params: SendMicroDiskFileParams
): Promise<ApiResponse<string>> => {
  logger.debug(`推送微盘文件 -> ${params.titleList.join(', ')}`);
  logger.debug(`文件名称: ${params.objectName}`);
  if (params.extraText) {
    logger.debug(`附加留言: ${params.extraText}`);
  }

  // 构建请求体（根据 OpenAPI 文档）
  const requestBody = {
    socketType: 2, // 固定值=2，通讯类型
    list: [
      {
        type: 209, // 固定值=209，推送微盘文件
        titleList: params.titleList, // 待发送姓名
        objectName: params.objectName, // 文件名称（微盘里存在）
        ...(params.extraText ? { extraText: params.extraText } : {}) // 附加留言（选填）
      }
    ]
  };

  // 调用推送微盘文件接口
  const response = await worktoolClient.post<string>(
    '/wework/sendRawMessage',
    requestBody,
    { params: { robotId } }
  );

  if (response.code === 200) {
    logger.info(`✅ WorkTool 微盘文件推送成功`);
    if (response.data) {
      // data 字段是 messageId (string)
      logger.debug(`   消息ID: ${response.data}`);
    }
  } else {
    logger.error(`❌ WorkTool 微盘文件推送失败: ${response.message}`);
  }

  return response;
};

/**
 * 批量发送指令项
 * 支持不同类型的指令（文本消息、文件消息等）
 */
export interface BatchSendItem {
  /** 消息类型，203=文本消息，218=文件消息等 */
  type: number;
  /** 接收者列表（昵称或群名） */
  titleList: string[];
  /** 文本消息内容（type=203时必需） */
  receivedContent?: string;
  /** @的人列表（可选，at所有人用"@所有人"） */
  atList?: string[];
  /** 文件名称（type=218时必需） */
  objectName?: string;
  /** 文件URL（type=218时必需） */
  fileUrl?: string;
  /** 文件类型（type=218时必需，如：image, video, audio, file） */
  fileType?: string;
  /** 附加文本（type=218时可选） */
  extraText?: string;
}

/**
 * 批量发送指令参数
 */
export interface BatchSendParams {
  /** 指令列表，最多100条 */
  list: BatchSendItem[];
}

/**
 * 批量发送指令
 * POST /wework/sendRawMessage
 * 
 * 文档: https://doc.worktool.ymdyes.cn/api-147612959.md
 * 
 * 功能介绍：
 * - 可以将多条发送指令合并在一个请求当中，提高网络效率
 * - 单次调用该接口可合并最多100条指令
 * - 此接口可解决并发请求太多导致被服务器拦截的问题
 * - 指令消息IP请求频率不可超过60QPM
 * 
 * 注意：
 * 1. 【指令消息】目录下的所有指令均可合并
 * 2. 单次最多100条指令
 * 
 * @param robotId 机器人ID
 * @param params 批量发送参数
 */
export const batchSendMessages = async (
  robotId: string,
  params: BatchSendParams
): Promise<ApiResponse<string>> => {
  const itemCount = params.list.length;
  
  if (itemCount === 0) {
    throw new Error('批量发送指令列表不能为空');
  }
  
  if (itemCount > 100) {
    throw new Error(`批量发送指令最多100条，当前有${itemCount}条`);
  }

  logger.debug(`批量发送 ${itemCount} 条指令`);

  // 构建请求体（根据 OpenAPI 文档）
  const requestBody = {
    socketType: 2, // 固定值=2，通讯类型
    list: params.list.map((item, index) => {
      const baseItem: any = {
        type: item.type,
        titleList: item.titleList
      };

      // 根据消息类型添加不同的字段
      if (item.type === 203) {
        // 文本消息
        baseItem.receivedContent = item.receivedContent;
        if (item.atList && item.atList.length > 0) {
          baseItem.atList = item.atList;
        }
      } else if (item.type === 218) {
        // 文件消息
        baseItem.objectName = item.objectName;
        baseItem.fileUrl = item.fileUrl;
        baseItem.fileType = item.fileType;
        if (item.extraText) {
          baseItem.extraText = item.extraText;
        }
      }
      // 其他类型的消息可以根据需要扩展

      return baseItem;
    })
  };

  // 调用批量发送接口（和单条消息使用同一个接口）
  const response = await worktoolClient.post<string>(
    '/wework/sendRawMessage',
    requestBody,
    { params: { robotId } }
  );

  if (response.code === 200) {
    logger.info(`✅ WorkTool 批量发送 ${itemCount} 条指令成功`);
    if (response.data) {
      // data 字段是 messageId (string)
      logger.debug(`   消息ID: ${response.data}`);
    }
  } else {
    logger.error(`❌ WorkTool 批量发送指令失败: ${response.message}`);
  }

  return response;
};

export default {
  sendTextMessage,
  sendMicroDiskFile,
  batchSendMessages,
};

