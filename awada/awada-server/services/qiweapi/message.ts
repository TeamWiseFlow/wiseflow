/**
 * qiweapi 消息模块
 * 负责发送各类消息
 */

import { apiClient } from './client';
import { ApiResponse, SendTextMsgParams, SendHyperTextMsgParams, SendMixTextMsgParams, SendImageMsgParams, SendFileMsgParams, SendVoiceMsgParams, SendMsgData, API_METHODS, FileType, HyperTextContentItem } from './types';
import { uploadFileByUrl } from './cdn';
import { createLogger } from '../../src/utils/logger';

const logger = createLogger('QiweAPI-Message');

/**
 * 发送纯文本消息
 * method: /msg/sendText
 *
 * @param toId 接收者ID（字符串类型）
 * @param content 消息内容
 * @param guid 设备GUID（可选，默认使用配置中的GUID）
 * @param token Token
 */
export const sendTextMsg = async (toId: string, content: string, guid: string, token: string): Promise<ApiResponse<SendMsgData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {}
    };
  }
  const deviceGuid = guid;

  logger.debug(`发送文本消息 -> ${toId}`);
  logger.debug(`内容: ${content.substring(0, 50)}${content.length > 50 ? '...' : ''}`);

  const params: SendTextMsgParams = {
    guid: deviceGuid,
    toId,
    content
  };

  const response = await apiClient.call<SendMsgData, SendTextMsgParams>(API_METHODS.SEND_TEXT_MSG, params, token);

  if (response.code === 0) {
    logger.info('✅ 文本消息发送成功');
  } else {
    logger.error('❌ 文本消息发送失败:', response.msg);
  }

  return response;
};

/**
 * 发送混合文本消息（支持@、表情等）
 * method: /msg/sendHyperText
 * 文档: https://doc.qiweapi.com/api-344613907.md
 *
 * @param toId 接收者ID
 * @param content 消息内容数组，每个元素包含 subtype 和 text
 * @param guid 设备GUID（可选）
 */
export const sendHyperTextMsg = async (toId: string, content: HyperTextContentItem[], guid: string, token: string): Promise<ApiResponse<SendMsgData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {}
    };
  }
  const deviceGuid = guid;

  logger.debug(`发送混合文本消息 -> ${toId}`);
  logger.debug(`内容项数量: ${content.length}`);

  const params: SendHyperTextMsgParams = {
    guid: deviceGuid,
    toId,
    content
  };

  const response = await apiClient.call<SendMsgData, SendHyperTextMsgParams>(API_METHODS.SEND_HYPER_TEXT_MSG, params, token);

  if (response.code === 0) {
    logger.info('✅ 混合文本消息发送成功');
  } else {
    logger.error('❌ 混合文本消息发送失败:', response.msg);
  }

  return response;
};

/**
 * 发送混合文本消息（兼容旧接口，自动转换）
 * @deprecated 使用 sendHyperTextMsg 代替
 *
 * @param toId 接收者ID
 * @param content 消息内容
 * @param atList @的用户ID列表
 * @param guid 设备GUID（可选）
 */
export const sendMixTextMsg = async (toId: string, content: string, atList: string[] | undefined, guid: string, token: string): Promise<ApiResponse<SendMsgData>> => {
  const contentItems: HyperTextContentItem[] = [];

  // 如果有@列表，构建@消息
  if (atList && atList.length > 0) {
    for (const userId of atList) {
      if (userId === 'notify@all' || userId === '0') {
        // @所有人
        contentItems.push({ subtype: 1, text: '0' });
      } else {
        // @具体人
        contentItems.push({ subtype: 1, text: userId });
      }
    }
  }

  // 添加文本内容
  if (content) {
    contentItems.push({ subtype: 0, text: content });
  }

  return sendHyperTextMsg(toId, contentItems, guid, token);
};

/**
 * 发送图片消息
 * method: /msg/sendImage
 * 文档: https://doc.qiweapi.com/api-344613908.md
 *
 * 说明：图片消息参数可以通过文件上传或文件上传-URL接口获取
 *
 * @param toId 接收者ID
 * @param params 图片消息参数（包含 fileAesKey, fileId, fileKey, fileMd5, fileSize, filename）
 * @param guid 设备GUID（可选）
 */
export const sendImageMsg = async (
  toId: string,
  params: {
    fileAesKey: string;
    fileId: string;
    fileKey: string;
    fileMd5: string;
    fileSize: number;
    filename: string;
  },
  guid: string,
  token: string
): Promise<ApiResponse<SendMsgData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {}
    };
  }
  const deviceGuid = guid;

  logger.debug(`发送图片消息 -> ${toId}`);
  logger.debug(`文件名: ${params.filename}, 大小: ${params.fileSize}`);

  const requestParams: SendImageMsgParams = {
    guid: deviceGuid,
    toId,
    ...params
  };

  const response = await apiClient.call<SendMsgData, SendImageMsgParams>(API_METHODS.SEND_IMAGE_MSG, requestParams, token);

  if (response.code === 0) {
    logger.info('✅ 图片消息发送成功');
  } else {
    logger.error('❌ 图片消息发送失败:', response.msg);
  }

  return response;
};

/**
 * 发送文件消息
 * method: /msg/sendFile
 *
 * 如果提供 fileUrl，会自动下载并上传文件获取 fileId 和 fileAesKey
 * 如果提供 fileId 和 fileAesKey，直接使用（跳过上传步骤）
 *
 * @param toId 接收者ID
 * @param options 文件选项
 * @param options.fileUrl 文件URL（如果提供，会自动下载并上传）
 * @param options.fileId 文件ID（如果提供，直接使用，跳过上传）
 * @param options.fileAesKey 文件AES密钥（如果提供，直接使用，跳过上传）
 * @param options.fileSize 文件大小（如果提供 fileUrl，会自动获取）
 * @param options.filename 文件名（必需）
 * @param guid 设备GUID（可选）
 */
export const sendFileMsg = async (
  toId: string,
  options: {
    fileUrl?: string;
    fileId?: string;
    fileAesKey?: string;
    fileSize?: number;
    filename: string;
  },
  guid: string,
  token: string
): Promise<ApiResponse<SendMsgData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {}
    };
  }
  const deviceGuid = guid;

  let fileId: string;
  let fileAesKey: string;
  let fileSize: number;

  // 如果提供了 fileId 和 fileAesKey，直接使用
  if (options.fileId && options.fileAesKey) {
    fileId = options.fileId;
    fileAesKey = options.fileAesKey;
    fileSize = options.fileSize || 0;
    logger.debug(`使用已有的 fileId 和 fileAesKey 发送文件`);
  } else if (options.fileUrl) {
    // 如果提供了 fileUrl，使用 URL 上传方式（更高效，不需要下载文件）
    logger.debug(`通过 URL 上传文件: ${options.fileUrl}`);

    try {
      // 使用 URL 上传方式（不需要下载文件，直接通过 URL 上传）
      const uploadResult = await uploadFileByUrl(
        options.fileUrl,
        options.filename,
        FileType.FILE, // 文件类型：5-文件
        deviceGuid,
        token
      );

      if (uploadResult.code !== 0 || !uploadResult.data) {
        return {
          code: uploadResult.code,
          msg: `文件上传失败: ${uploadResult.msg}`,
          data: {}
        };
      }

      fileId = uploadResult.data.fileId;
      fileAesKey = uploadResult.data.fileAesKey;
      fileSize = uploadResult.data.fileSize;

      logger.info(`文件上传成功（通过URL），fileId: ${fileId}`);
    } catch (error: any) {
      logger.error(`❌ URL 上传文件失败:`, error);
      return {
        code: -1,
        msg: `URL 上传文件失败: ${error.message}`,
        data: {}
      };
    }
  } else {
    return {
      code: -1,
      msg: '必须提供 fileUrl 或 fileId+fileAesKey',
      data: {}
    };
  }

  // 发送文件消息
  logger.debug(`发送文件消息 -> ${toId}`);
  logger.debug(`文件名: ${options.filename}, 大小: ${fileSize}`);

  const params: SendFileMsgParams = {
    guid: deviceGuid,
    toId,
    fileAesKey,
    fileId,
    fileSize,
    filename: options.filename
  };

  const response = await apiClient.call<SendMsgData, SendFileMsgParams>(API_METHODS.SEND_FILE_MSG, params, token);

  if (response.code === 0) {
    logger.info('✅ 文件消息发送成功');
  } else {
    logger.error('❌ 文件消息发送失败:', response.msg);
  }

  return response;
};

/**
 * 发送语音消息
 * method: /msg/sendVoice
 * 文档: https://doc.qiweapi.com/api-344613912.md
 *
 * 说明：AMR格式，语音消息参数可以通过文件上传或文件上传-URL接口获取
 *
 * @param toId 接收者ID
 * @param params 语音消息参数（包含 fileAesKey, fileId, fileSize, voiceTime）
 * @param guid 设备GUID（可选）
 */
export const sendVoiceMsg = async (
  toId: string,
  params: {
    fileAesKey: string;
    fileId: string;
    fileSize: number;
    voiceTime: number;
  },
  guid: string,
  token: string
): Promise<ApiResponse<SendMsgData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {}
    };
  }
  const deviceGuid = guid;

  logger.debug(`发送语音消息 -> ${toId}`);
  logger.debug(`语音时长: ${params.voiceTime}秒, 大小: ${params.fileSize}`);

  const requestParams: SendVoiceMsgParams = {
    guid: deviceGuid,
    toId,
    ...params
  };

  const response = await apiClient.call<SendMsgData, SendVoiceMsgParams>(API_METHODS.SEND_VOICE_MSG, requestParams, token);

  if (response.code === 0) {
    logger.info('✅ 语音消息发送成功');
  } else {
    logger.error('❌ 语音消息发送失败:', response.msg);
  }

  return response;
};

/**
 * 智能发送消息
 * 根据是否有@列表自动选择发送方式
 *
 * @param toId 接收者ID
 * @param content 消息内容
 * @param atList @的用户ID列表（可选）
 * @param guid 设备GUID（可选）
 */
export const sendMessage = async (toId: string, content: string, atList: string[] | undefined, guid: string, token: string): Promise<ApiResponse<SendMsgData>> => {
  if (atList && atList.length > 0) {
    return sendMixTextMsg(toId, content, atList, guid, token);
  }
  return sendTextMsg(toId, content, guid, token);
};

export default {
  sendTextMsg,
  sendHyperTextMsg,
  sendMixTextMsg,
  sendImageMsg,
  sendFileMsg,
  sendVoiceMsg,
  sendMessage
};
