/**
 * WorkTool HTTP客户端
 * 文档: https://api.worktool.ymdyes.cn
 * OpenAPI: docs/worktool/worktool.openapi.json
 */

import axios, { AxiosInstance } from 'axios';
import worktoolConfig from '@/config/worktool';
import { ApiResponse } from './types';
import { createLogger } from '../../src/utils/logger';

const logger = createLogger('WorkTool-Client');

class WorkToolClient {
  private client: AxiosInstance;
  private static instance: WorkToolClient;

  private constructor() {
    this.client = axios.create({
      baseURL: worktoolConfig.baseUrl,
      timeout: worktoolConfig.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        logger.debug(`${config.method?.toUpperCase()} ${config.url}`);
        if (config.data) {
          logger.debug(`Body:`, JSON.stringify(config.data, null, 2));
        }
        return config;
      },
      (error) => {
        logger.error('请求错误:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        const { data } = response;
        logger.debug(`Response:`, JSON.stringify(data, null, 2));

        if (data.code !== 200 && data.code !== 0) {
          logger.error(`业务错误: code=${data.code}, message=${data.message}`);
        }

        return response;
      },
      (error) => {
        logger.error('响应错误:', error.message);
        if (error.response) {
          logger.error('状态码:', error.response.status);
          logger.error('响应数据:', error.response.data);
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * 获取单例实例
   */
  public static getInstance(): WorkToolClient {
    if (!WorkToolClient.instance) {
      WorkToolClient.instance = new WorkToolClient();
    }
    return WorkToolClient.instance;
  }

  /**
   * GET 请求
   */
  public async get<T = any>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get<ApiResponse<T>>(endpoint, { params });
      return response.data;
    } catch (error: any) {
      return {
        code: error.response?.status || 500,
        message: error.message || '请求失败',
        data: {} as T,
      };
    }
  }

  /**
   * POST 请求
   * 
   * @param endpoint API 端点路径
   * @param data 请求体数据
   * @param config 额外配置（如 query 参数）
   */
  public async post<T = any>(
    endpoint: string,
    data?: any,
    config?: { params?: Record<string, string> }
  ): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post<ApiResponse<T>>(
        endpoint,
        data,
        { params: config?.params }
      );
      return response.data;
    } catch (error: any) {
      return {
        code: error.response?.status || 500,
        message: error.message || '请求失败',
        data: {} as T,
      };
    }
  }
}

// 导出单例
export const worktoolClient = WorkToolClient.getInstance();
export default WorkToolClient;

