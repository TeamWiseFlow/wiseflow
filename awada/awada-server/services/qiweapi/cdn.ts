/**
 * qiweapi CDN模块
 * 负责文件上传、下载
 */

import * as fs from 'fs';
import * as path from 'path';
import { apiClient } from './client';
import {
  ApiResponse,
  UploadFileData,
  FileType,
  API_METHODS,
  WxDownloadFileParams,
  WxDownloadFileData,
  UploadFileByUrlParams,
  UploadFileByUrlData,
  DownloadFileParams,
  DownloadFileData,
} from './types';
import { createLogger } from '../../src/utils/logger';

const logger = createLogger('CDN');

/**
 * 上传文件
 * 端点: POST /api/qw/doFileApi
 * method: /cloud/cdnBigUpload
 * 
 * @param file 文件（File/Buffer/Blob 或文件路径）
 * @param fileType 文件类型: 1-图片 4-视频 5-文件
 * @param guid 设备GUID（可选）
 */
export const uploadFile = async (
  file: File | Buffer | Blob | string,
  fileType: FileType | number,
  guid: string
): Promise<ApiResponse<UploadFileData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {} as UploadFileData,
    };
  }
  const deviceGuid = guid;

  // 如果是文件路径，读取文件
  let fileData: File | Buffer | Blob;
  if (typeof file === 'string') {
    if (!fs.existsSync(file)) {
      return {
        code: -1,
        msg: `文件不存在: ${file}`,
        data: {} as UploadFileData,
      };
    }
    fileData = fs.readFileSync(file);
    logger.info(`上传文件: ${path.basename(file)}, 类型: ${fileType}`);
  } else {
    fileData = file;
    logger.info(`上传文件, 类型: ${fileType}`);
  }

  const response = await apiClient.uploadFile<UploadFileData>(
    API_METHODS.UPLOAD_FILE,
    deviceGuid,
    fileData,
    fileType
  );

  if (response.code === 0 && response.data) {
    logger.info('✅ 文件上传成功');
    logger.debug(`fileId: ${response.data.fileId}`);
    logger.debug(`fileKey: ${response.data.fileKey}`);
    logger.debug(`fileSize: ${response.data.fileSize}`);
  } else {
    logger.error('❌ 文件上传失败:', response.msg);
  }

  return response;
};

/**
 * 上传图片
 * 便捷方法
 */
export const uploadImage = async (
  file: File | Buffer | Blob | string,
  guid: string
): Promise<ApiResponse<UploadFileData>> => {
  return uploadFile(file, FileType.IMAGE, guid);
};

/**
 * 上传视频
 * 便捷方法
 */
export const uploadVideo = async (
  file: File | Buffer | Blob | string,
  guid: string
): Promise<ApiResponse<UploadFileData>> => {
  return uploadFile(file, FileType.VIDEO, guid);
};

/**
 * 上传普通文件（包括语音）
 * 便捷方法
 */
export const uploadDocument = async (
  file: File | Buffer | Blob | string,
  guid: string
): Promise<ApiResponse<UploadFileData>> => {
  return uploadFile(file, FileType.FILE, guid);
};

/**
 * 下载个微文件
 * method: /cloud/wxDownload
 * 
 * 将个微文件（fileHttpUrl）转换为可访问的 cloudUrl
 * 
 * @param params 下载参数
 * @param guid 设备GUID（可选）
 */
export const downloadWxFile = async (
  params: Omit<WxDownloadFileParams, 'guid'>,
  guid: string,
  token: string
): Promise<ApiResponse<WxDownloadFileData>> => {
  logger.info(`下载个微文件: fileSize=${params.fileSize}, fileType=${params.fileType}`);

  const requestParams: WxDownloadFileParams = {
    guid: guid,
    ...params,
  };

  const response = await apiClient.call<WxDownloadFileData, WxDownloadFileParams>(
    API_METHODS.WX_DOWNLOAD_FILE,
    requestParams,
    token
  );

  if (response.code === 0 && response.data) {
    logger.info('✅ 个微文件下载成功');
    logger.debug(`cloudUrl: ${response.data.cloudUrl}`);
  } else {
    logger.error('❌ 个微文件下载失败:', response.msg);
  }

  return response;
};

/**
 * 通过 URL 上传文件
 * method: /cloud/cdnBigUploadByUrl
 * 端点: POST /api/qw/doApi (application/json)
 * 
 * 这种方式不需要下载文件，直接通过 URL 上传，更高效
 * 
 * @param fileUrl 文件URL
 * @param filename 文件名
 * @param fileType 文件类型: 1-图片 4-视频 5-文件
 * @param guid 设备GUID（可选）
 */
export const uploadFileByUrl = async (
  fileUrl: string,
  filename: string,
  fileType: FileType | number,
  guid: string,
  token: string
): Promise<ApiResponse<UploadFileByUrlData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {} as UploadFileByUrlData,
    };
  }

  logger.info(`通过 URL 上传文件: ${filename}`);
  logger.debug(`URL: ${fileUrl}`);

  const params: UploadFileByUrlParams = {
    guid: guid,
    filename,
    fileUrl,
    fileType,
  };

  const response = await apiClient.call<UploadFileByUrlData, UploadFileByUrlParams>(
    API_METHODS.UPLOAD_FILE_BY_URL,
    params,
    token
  );

  if (response.code === 0 && response.data) {
    logger.info('✅ 文件上传成功（通过URL）');
    logger.debug(`fileId: ${response.data.fileId}`);
    logger.debug(`fileAesKey: ${response.data.fileAesKey}`);
    logger.debug(`cloudUrl: ${response.data.cloudUrl}`);
  } else {
    logger.error('❌ 文件上传失败（通过URL）:', response.msg);
  }

  return response;
};

/**
 * 企微文件下载
 * method: /cloud/wxWorkDownload
 * 文档: https://doc.qiweapi.com/api-344613901.md
 * 
 * 说明：下载响应的地址为临时云资源，非官方CDN地址，并且会定期清理，请自行及时下载
 * 
 * @param params 下载参数（包含 fileAeskey, fileId, fileSize, fileType）
 * @param guid 设备GUID（可选）
 */
export const downloadFile = async (
  params: Omit<DownloadFileParams, 'guid'>,
  guid: string,
  token: string
): Promise<ApiResponse<DownloadFileData>> => {
  if (!guid) {
    return {
      code: -1,
      msg: '设备GUID必须通过参数传递',
      data: {} as DownloadFileData,
    };
  }

  logger.info(`下载企微文件: fileSize=${params.fileSize}, fileType=${params.fileType}`);

  const requestParams: DownloadFileParams = {
    guid: guid,
    ...params,
  };

  const response = await apiClient.call<DownloadFileData, DownloadFileParams>(
    API_METHODS.DOWNLOAD_FILE,
    requestParams,
    token
  );

  if (response.code === 0 && response.data) {
    logger.info('✅ 企微文件下载成功');
    logger.debug(`cloudUrl: ${response.data.cloudUrl}`);
    logger.warn('⚠️ 注意：此地址为临时云资源，会定期清理，请及时下载');
  } else {
    logger.error('❌ 企微文件下载失败:', response.msg);
  }

  return response;
};

export default {
  uploadFile,
  uploadImage,
  uploadVideo,
  uploadDocument,
  uploadFileByUrl,
  downloadWxFile,
  downloadFile,
  FileType,
};

