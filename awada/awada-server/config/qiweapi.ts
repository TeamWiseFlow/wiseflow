/**
 * qiweapi 配置
 * 文档地址: https://doc.qiweapi.com/
 *
 * API 特点：
 * - 统一入口: POST /api/qw/doApi
 * - 请求格式: { method: string, params: object }
 * - 认证头: X-QIWEI-TOKEN
 */

import { createLogger } from '../src/utils/logger';

const logger = createLogger('QiweAPI');

export interface QiweApiConfig {
  /** API基础地址 */
  baseUrl: string;
  /** 回调地址 */
  callbackUrl: string;
  /** 请求超时时间（毫秒） */
  timeout: number;
  /** 默认设备类型: 0-ipad, 2-windows */
  defaultDeviceType: number;
  /** 默认客户端版本 */
  defaultClientVersion: string;
  /** 默认地区代码 */
  defaultAreaCode: number;
}

/** 默认配置 */
const config: QiweApiConfig = {
  baseUrl: process.env.QIWEAPI_BASE_URL || 'https://api.qiweapi.com',
  callbackUrl: process.env.CALLBACK_URL || '',
  timeout: 30000,
  defaultDeviceType: 0, // ipad
  defaultClientVersion: '4.1.36.6011',
  defaultAreaCode: 320000 // 江苏
};

export default config;
