/**
 * WorkTool API 服务入口
 */

export { worktoolClient, default as WorkToolClient } from './client';
export * from './types';
export { getRobotInfo, checkRobotOnline, setCallback } from './robot';
export { sendTextMessage, sendMicroDiskFile, batchSendMessages, BatchSendItem, BatchSendParams, SendMicroDiskFileParams } from './message';

