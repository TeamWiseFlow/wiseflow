/**
 * qiweapi HTTP客户端
 * 
 * API 特点：
 * - 统一入口: POST /api/qw/doApi
 * - 请求格式: { method: string, params: object }
 * - 认证头: X-QIWEI-TOKEN
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import qiweapiConfig from '@/config/qiweapi';
import { ApiRequest, ApiResponse } from './types';

class QiweApiClient {
  private client: AxiosInstance;
  private static instance: QiweApiClient;

  /** API统一入口 */
  private readonly API_ENDPOINT = '/api/qw/doApi';

  private constructor() {
    this.client = axios.create({
      baseURL: qiweapiConfig.baseUrl,
      timeout: qiweapiConfig.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        // Token 现在通过 call 方法的参数传递，不再从全局配置读取
        // 如果需要默认 token，可以在调用时传递

        console.log(`[QiweAPI] POST ${config.url}`);
        console.log(`[QiweAPI] Body:`, JSON.stringify(config.data, null, 2));
        return config;
      },
      (error) => {
        console.error('[QiweAPI] 请求错误:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        const { data } = response;
        console.log(`[QiweAPI] Response:`, JSON.stringify(data, null, 2));

        // 检查业务状态码
        if (data.code !== 0) {
          console.error(`[QiweAPI] 业务错误: code=${data.code}, msg=${data.msg}`);
        }

        return response;
      },
      (error) => {
        console.error('[QiweAPI] 响应错误:', error.message);
        if (error.response) {
          console.error('[QiweAPI] 状态码:', error.response.status);
          console.error('[QiweAPI] 响应数据:', error.response.data);
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * 获取单例实例
   */
  public static getInstance(): QiweApiClient {
    if (!QiweApiClient.instance) {
      QiweApiClient.instance = new QiweApiClient();
    }
    return QiweApiClient.instance;
  }

  /**
   * 调用 qiweapi 接口
   * @param method API方法，如 /client/createClient
   * @param params 请求参数
   * @param token 可选的 Token（多 Bot 支持：如果不提供，使用全局配置的 token）
   */
  public async call<T = any, P = any>(
    method: string,
    params: P,
    token: string
  ): Promise<ApiResponse<T>> {
    const requestBody: ApiRequest<P> = {
      method,
      params,
    };

    try {
      // Token 必须通过参数传递（多 Bot 支持）
      if (!token) {
        throw new Error('Token 必须通过参数传递');
      }
      const requestToken = token;
      
      const response = await this.client.post<ApiResponse<T>>(
        this.API_ENDPOINT,
        requestBody,
        {
          headers: {
            'X-QIWEI-TOKEN': requestToken,
          },
        }
      );
      return response.data;
    } catch (error: any) {
      return {
        code: error.response?.status || 500,
        msg: error.message || '请求失败',
        data: {} as T,
      };
    }
  }

  /**
   * 原始 POST 请求（用于非标准接口）
   */
  public async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post<ApiResponse<T>>(url, data, config);
      return response.data;
    } catch (error: any) {
      return {
        code: error.response?.status || 500,
        msg: error.message || '请求失败',
        data: {} as T,
      };
    }
  }

  /**
   * 文件上传（使用 multipart/form-data）
   * 端点: POST /api/qw/doFileApi
   * 
   * @param method API方法，如 /cloud/cdnBigUpload
   * @param guid 设备GUID
   * @param file 文件
   * @param fileType 文件类型: 1-图片 4-视频 5-文件
   */
  public async uploadFile<T = any>(
    method: string,
    guid: string,
    file: File | Buffer | Blob,
    fileType: number
  ): Promise<ApiResponse<T>> {
    const FormData = require('form-data');
    const formData = new FormData();
    
    formData.append('method', method);
    formData.append('guid', guid);
    formData.append('fileType', String(fileType));
    formData.append('file', file);

    console.log(`[QiweAPI] 文件上传: method=${method}, guid=${guid}, fileType=${fileType}`);

    try {
      const response = await this.client.post<ApiResponse<T>>(
        '/api/qw/doFileApi',
        formData,
        {
          headers: {
            ...formData.getHeaders?.(),
            'Content-Type': 'multipart/form-data',
          },
          timeout: 120000, // 文件上传超时时间较长
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('[QiweAPI] 文件上传失败:', error.message);
      return {
        code: error.response?.status || 500,
        msg: error.message || '文件上传失败',
        data: {} as T,
      };
    }
  }

  /**
   * 更新基础URL
   */
  public setBaseURL(baseURL: string) {
    this.client.defaults.baseURL = baseURL;
  }

  /**
   * 更新 Token（已废弃，Token 现在通过参数传递）
   * @deprecated Token 现在通过 call 方法的参数传递，不再使用全局配置
   */
  public setToken(token: string) {
    // Token 现在通过参数传递，不再使用全局配置
    // 保留此方法仅为向后兼容，实际不会生效
  }

  /**
   * 更新超时时间
   */
  public setTimeout(timeout: number) {
    this.client.defaults.timeout = timeout;
  }
}

// 导出单例
export const apiClient = QiweApiClient.getInstance();

export default QiweApiClient;
