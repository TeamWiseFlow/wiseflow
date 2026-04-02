/**
 * WorkTool API 配置
 * 文档: https://doc.worktool.ymdyes.cn/
 * 
 * 关键文档：
 * - 快速入门: https://doc.worktool.ymdyes.cn/doc-850007.md
 * - 消息回调接口规范: https://doc.worktool.ymdyes.cn/doc-861677.md
 * - 发送消息: https://doc.worktool.ymdyes.cn/api-23520034.md
 * - 机器人消息回调配置: https://doc.worktool.ymdyes.cn/api-22587884.md
 */

import { createLogger } from '../src/utils/logger';

const logger = createLogger('WorkTool');

export interface WorkToolConfig {
  /** API基础地址 */
  baseUrl: string;
  /** 回调地址 */
  callbackUrl: string;
  /** 请求超时时间（毫秒） */
  timeout: number;
}

/** 默认配置 */
const config: WorkToolConfig = {
  baseUrl: process.env.WORKTOOL_BASE_URL || 'https://api.worktool.ymdyes.cn',
  callbackUrl: process.env.WORKTOOL_CALLBACK_URL || '',
  timeout: 30000,
};

export default config;

