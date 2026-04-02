/**
 * Outbound 消息处理服务
 * 负责消费 Outbound Stream 并将消息发送到各个平台
 */

import { createOutboundConsumer, getIdempotencyManager, getConversationManager, OutboundEvent, Lane, StreamMessage, Payload, ContentObject, EventConsumer, FileObject } from '../../infrastructure/redis';
import { sendTextMsg, sendImageMsg, sendFileMsg, sendMessage } from '@/services/qiweapi/message';
import { uploadFileByUrl } from '@/services/qiweapi/cdn';
import { FileType } from '@/services/qiweapi/types';
import { getBotManager } from '../bot/manager';
import { BotConfig } from '@/config/bots';
import * as path from 'path';
import { createLogger } from '../../utils/logger';
import { batchSendMessages, BatchSendItem, sendMicroDiskFile } from '@/services/worktool/message';

const logger = createLogger('Outbound');

// 懒加载实例
let idempotencyManagerInstance: ReturnType<typeof getIdempotencyManager> | null = null;
let conversationManagerInstance: ReturnType<typeof getConversationManager> | null = null;

// 保存消费者实例，以便优雅停止
const consumers: EventConsumer[] = [];

/**
 * 获取 IdempotencyManager 实例（懒加载）
 */
function getIdempotencyMgr() {
  if (!idempotencyManagerInstance) {
    idempotencyManagerInstance = getIdempotencyManager();
  }
  return idempotencyManagerInstance;
}

/**
 * 获取 ConversationManager 实例（懒加载）
 */
function getConversationMgr() {
  if (!conversationManagerInstance) {
    conversationManagerInstance = getConversationManager();
  }
  return conversationManagerInstance;
}

/**
 * 从 file_url 提取文件名
 */
function extractFilenameFromUrl(fileUrl: string): string {
  let filename = 'file';
  try {
    const url = new URL(fileUrl);
    const pathname = url.pathname;
    // 获取路径的最后一部分作为文件名
    const urlFilename = pathname.split('/').pop() || 'file';
    // 解码文件名（处理 URL 编码）
    filename = decodeURIComponent(urlFilename);
    // 如果解码后仍然是编码格式，尝试再次解码
    if (filename.includes('%')) {
      filename = decodeURIComponent(filename);
    }
    // 如果还是没有有效的文件名，使用默认值
    if (!filename || filename === '/' || filename === 'file') {
      // 尝试从 URL 的查询参数或其他部分获取文件名
      const urlParams = new URLSearchParams(url.search);
      const paramFilename = urlParams.get('filename') || urlParams.get('name');
      if (paramFilename) {
        filename = decodeURIComponent(paramFilename);
      } else {
        // 使用文件扩展名推断文件名
        const ext = path.extname(pathname);
        filename = `file${ext || ''}`;
      }
    }
  } catch (e) {
    // 如果 URL 解析失败，使用默认文件名
    logger.warn(`⚠️ 无法从 URL 提取文件名: ${fileUrl}`, e);
    filename = 'file';
  }
  return filename;
}

/**
 * 从 file_id JSON 字符串解析文件参数
 */
interface ParsedFileId {
  fileAesKey: string;
  fileId: string;
  fileKey?: string;
  fileMd5?: string;
  fileSize: number;
  fileThumbSize?: number;
  durationTime?: number;
  filename?: string;
}

function parseFileId(fileIdStr: string): ParsedFileId | null {
  try {
    const parsed = JSON.parse(fileIdStr);
    if (!parsed.fileAesKey || !parsed.fileId || !parsed.fileSize) {
      logger.error('❌ file_id 解析失败：缺少必需字段');
      return null;
    }
    return {
      fileAesKey: parsed.fileAesKey,
      fileId: parsed.fileId,
      fileKey: parsed.fileKey,
      fileMd5: parsed.fileMd5,
      fileSize: parsed.fileSize,
      fileThumbSize: parsed.fileThumbSize,
      durationTime: parsed.durationTime,
      filename: parsed.filename
    };
  } catch (error: any) {
    logger.error(`❌ 解析 file_id JSON 失败:`, error.message);
    return null;
  }
}

/**
 * 处理 Payload 数组
 * 新的 payload 格式是 ContentObject[] 数组
 * 必须按照数组顺序逐个发送消息
 */
async function handlePayload(payload: Payload, toId: string, channelId: string, botConfig: BotConfig): Promise<void> {
  // 多 Bot 支持：使用 botConfig 的 token 和 deviceGuid
  if (!Array.isArray(payload) || payload.length === 0) {
    throw new Error('Payload 必须是非空数组');
  }

  const deviceGuid = botConfig.deviceGuid;

  if (!deviceGuid) {
    throw new Error(`Bot ${botConfig.botId} 的设备GUID不存在，无法发送消息`);
  }

  // 按照 payload 数组顺序逐个发送
  for (let i = 0; i < payload.length; i++) {
    const obj = payload[i];

    try {
      switch (obj.type) {
        case 'text': {
          const textResult = await sendMessage(toId, obj.text, undefined, deviceGuid, botConfig.token);
          if (textResult.code !== 0) {
            throw new Error(`发送文本消息失败: ${textResult.msg}`);
          }
          // 高亮显示发送的消息
          const textPreview = obj.text.length > 50 ? obj.text.substring(0, 50) + '...' : obj.text;
          logger.sent(`📤 [${i + 1}/${payload.length}] 文本消息已发送到 ${toId}: ${textPreview}`);
          break;
        }

        case 'image': {
          if (obj.file_url) {
            const filename = extractFilenameFromUrl(obj.file_url);
            // logger.debug(`准备发送图片: ${filename} (${obj.file_url})`); // 减少日志

            try {
              // 先通过 URL 上传文件获取发送参数
              const uploadResult = await uploadFileByUrl(
                obj.file_url,
                filename,
                FileType.IMAGE, // 1: 图片
                deviceGuid,
                botConfig.token
              );

              if (uploadResult.code !== 0 || !uploadResult.data) {
                logger.error(`❌ [${i + 1}/${payload.length}] 图片上传失败: ${uploadResult.msg}`);
                break;
              }

              // 使用上传结果发送图片消息
              const imageResult = await sendImageMsg(
                toId,
                {
                  fileAesKey: uploadResult.data.fileAesKey,
                  fileId: uploadResult.data.fileId,
                  fileKey: uploadResult.data.fileKey,
                  fileMd5: uploadResult.data.fileMd5,
                  fileSize: uploadResult.data.fileSize,
                  filename: filename
                },
                deviceGuid,
                botConfig.token
              );

              if (imageResult.code !== 0) {
                logger.error(`❌ [${i + 1}/${payload.length}] 发送图片失败: ${imageResult.msg}`);
              } else {
                logger.sent(`📤 [${i + 1}/${payload.length}] 图片已发送到 ${toId} (${filename})`);
              }
            } catch (error: any) {
              logger.error(`❌ [${i + 1}/${payload.length}] 处理图片失败:`, error.message);
            }
          } else if (obj.file_id) {
            // 从 file_id JSON 字符串解析文件参数
            // logger.debug(`准备从 file_id 发送图片`); // 减少日志
            const parsed = parseFileId(obj.file_id);

            if (!parsed) {
              console.error(`[Outbound] ❌ [${i + 1}/${payload.length}] 解析 file_id 失败`);
              break;
            }

            // 检查必需字段（图片需要 fileKey 和 fileMd5）
            if (!parsed.fileKey || !parsed.fileMd5) {
              logger.error(`❌ [${i + 1}/${payload.length}] file_id 缺少必需字段（fileKey 或 fileMd5）`);
              break;
            }

            // 尝试从 fileKey 提取文件名，如果没有则使用默认值
            // fileKey 通常是 UUID 格式，不是真正的文件名，所以使用默认值
            const filename = 'image.jpg';

            try {
              const imageResult = await sendImageMsg(
                toId,
                {
                  fileAesKey: parsed.fileAesKey,
                  fileId: parsed.fileId,
                  fileKey: parsed.fileKey,
                  fileMd5: parsed.fileMd5,
                  fileSize: parsed.fileSize,
                  filename: filename
                },
                deviceGuid,
                botConfig.token
              );

              if (imageResult.code !== 0) {
                logger.error(`❌ [${i + 1}/${payload.length}] 发送图片失败: ${imageResult.msg}`);
              } else {
                logger.sent(`📤 [${i + 1}/${payload.length}] 图片已发送到 ${toId} (${filename})`);
              }
            } catch (error: any) {
              logger.error(`❌ [${i + 1}/${payload.length}] 处理图片失败:`, error.message);
            }
          } else if (obj.file_path) {
            // TODO: 如果 qiweapi 支持 file_path，需要实现相应逻辑
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 暂不支持通过 file_path 发送图片: ${obj.file_path}`);
          } else {
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 图片对象缺少 file_url、file_path 或 file_id`);
          }
          break;
        }

        case 'file': {
          if (obj.file_url) {
            const filename = extractFilenameFromUrl(obj.file_url);
            // logger.debug(`准备发送文件: ${filename} (${obj.file_url})`); // 减少日志

            const fileResult = await sendFileMsg(
              toId,
              {
                fileUrl: obj.file_url,
                filename: filename
              },
              deviceGuid,
              botConfig.token
            );

            if (fileResult.code !== 0) {
              logger.error(`❌ [${i + 1}/${payload.length}] 发送文件失败: ${fileResult.msg}`);
              // 继续发送其他内容，不中断
            } else {
              logger.sent(`📤 [${i + 1}/${payload.length}] 文件已发送到 ${toId} (${filename})`);
            }
          } else if (obj.file_id) {
            // 从 file_id JSON 字符串解析文件参数
            // logger.debug(`准备从 file_id 发送文件`); // 减少日志
            const parsed = parseFileId(obj.file_id);

            if (!parsed) {
              console.error(`[Outbound] ❌ [${i + 1}/${payload.length}] 解析 file_id 失败`);
              break;
            }

            // fileKey 通常是 UUID 格式，不是真正的文件名
            // 如果没有明确的文件名，使用默认值

            try {
              const fileResult = await sendFileMsg(
                toId,
                {
                  fileId: parsed.fileId,
                  fileAesKey: parsed.fileAesKey,
                  fileSize: parsed.fileSize,
                  filename: parsed.filename || 'file'
                },
                deviceGuid,
                botConfig.token
              );

              if (fileResult.code !== 0) {
                logger.error(`❌ [${i + 1}/${payload.length}] 发送文件失败: ${fileResult.msg}`);
              } else {
                logger.sent(`📤 [${i + 1}/${payload.length}] 文件已发送到 ${toId} (${parsed.filename || 'file'})`);
              }
            } catch (error: any) {
              logger.error(`❌ [${i + 1}/${payload.length}] 处理文件失败:`, error.message);
            }
          } else if (obj.file_path) {
            // TODO: 如果 qiweapi 支持 file_path，需要实现相应逻辑
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 暂不支持通过 file_path 发送文件: ${obj.file_path}`);
          } else {
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 文件对象缺少 file_url、file_path 或 file_id`);
          }
          break;
        }

        case 'audio': {
          if (obj.file_url) {
            // TODO: 如果 qiweapi 支持音频发送，需要实现相应逻辑
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 暂不支持发送音频: ${obj.file_url}`);
          } else if (obj.file_path) {
            // TODO: 如果 qiweapi 支持 file_path，需要实现相应逻辑
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 暂不支持通过 file_path 发送音频: ${obj.file_path}`);
          } else if (obj.file_id) {
            // TODO: 如果 qiweapi 支持 file_id，需要实现相应逻辑
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 暂不支持通过 file_id 发送音频: ${obj.file_id}`);
          } else {
            logger.warn(`⚠️ [${i + 1}/${payload.length}] 音频对象缺少 file_url、file_path 或 file_id`);
          }
          break;
        }

        default:
          logger.warn(`⚠️ [${i + 1}/${payload.length}] 未知的消息类型: ${(obj as any).type}`);
      }
    } catch (error: any) {
      // 单个消息发送失败，记录错误但继续发送后续消息
      logger.error(`❌ [${i + 1}/${payload.length}] 处理消息失败:`, error.message);
      // 根据业务需求决定是否继续：目前选择继续发送后续消息
    }
  }

  logger.sent(`✅ 已完成 ${payload.length} 条消息的发送`);
}

/**
 * 处理 WorkTool Payload 数组
 * WorkTool 的消息发送格式与 QiweAPI 不同
 * 使用批量发送接口提高效率，避免超过60QPM限制
 * @param payload 消息内容数组
 * @param toId 接收者ID
 * @param channelId 频道ID（群名）
 * @param botConfig Bot配置
 * @param actionAsk action_ask 字段，格式为 [int, ["string", ...]]，用于群聊@用户
 */
async function handleWorkToolPayload(payload: Payload, toId: string, channelId: string, botConfig: BotConfig, actionAsk?: [number, string[]]): Promise<void> {
  if (!Array.isArray(payload) || payload.length === 0) {
    throw new Error('Payload 必须是非空数组');
  }

  const robotId = botConfig.deviceGuid; // WorkTool 使用 deviceGuid 作为 robotId

  if (!robotId) {
    throw new Error(`Bot ${botConfig.botId} 的 robotId 不存在，无法发送消息`);
  }

  // WorkTool 的接收者格式：titleList 是数组，包含群名或用户名
  // 如果是群消息，使用 channelId（群名）；如果是私聊，使用 toId（用户名）
  const titleList = channelId && channelId !== '0' ? [channelId] : [toId];
  const isGroupChat = channelId && channelId !== '0';

  // 处理 action_ask：提取需要@的用户列表
  // action_ask 格式: [0, ["string", ...]]，其中 "all" 代表@所有人
  let atList: string[] | undefined = undefined;
  if (isGroupChat && actionAsk && Array.isArray(actionAsk) && actionAsk.length === 2) {
    const userList = actionAsk[1];
    if (Array.isArray(userList) && userList.length > 0) {
      // 检查是否有 "all"（@所有人）
      if (userList.includes('all')) {
        atList = ['@所有人'];
        logger.debug(`📢 群聊消息需要@所有人`);
      } else {
        // 提取用户列表，过滤掉 "all"
        atList = userList.filter((user) => user !== 'all');
        if (atList.length > 0) {
          logger.debug(`📢 群聊消息需要@用户: ${atList.join(', ')}`);
        }
      }
    }
  }

  // 将 payload 转换为批量发送指令格式
  const batchItems: BatchSendItem[] = [];
  const unsupportedTypes: string[] = [];

  for (let i = 0; i < payload.length; i++) {
    const obj = payload[i];

    try {
      switch (obj.type) {
        case 'text': {
          batchItems.push({
            type: 203, // 文本消息类型
            titleList: titleList,
            receivedContent: obj.text,
            // 如果是群聊且有 action_ask，添加 atList
            ...(atList && atList.length > 0 ? { atList: atList } : {})
          });
          break;
        }

        case 'image': {
          // ⚠️ TODO: 需要根据 WorkTool API 文档实现图片发送
          // 可能需要 type=218 或其他类型，需要确认 API 文档
          logger.warn(`⚠️ [${i + 1}/${payload.length}] WorkTool 图片消息暂未实现，跳过`);
          unsupportedTypes.push('image');
          break;
        }

        case 'file': {
          const fileObj = obj as FileObject;

          // 检查是否是微盘文件（有 file_id）
          if (fileObj.file_id) {
            // 使用推送微盘文件 API (type=209)
            try {
              const response = await sendMicroDiskFile(robotId, {
                titleList: titleList,
                objectName: fileObj.file_id, // 微盘文件名称
                ...(fileObj.file_name ? { extraText: fileObj.file_name } : {}) // 附加留言（使用 file_name）
              });

              if (response.code === 200) {
                logger.sent(`📤 [${i + 1}/${payload.length}] WorkTool 微盘文件发送成功: ${fileObj.file_id} -> ${titleList.join(', ')}`);
                if (response.data) {
                  logger.debug(`   消息ID: ${response.data}`);
                }
              } else {
                logger.error(`❌ [${i + 1}/${payload.length}] WorkTool 微盘文件发送失败: ${response.message}`);
                unsupportedTypes.push('file');
              }
            } catch (error: any) {
              logger.error(`❌ [${i + 1}/${payload.length}] WorkTool 微盘文件发送异常:`, error.message);
              unsupportedTypes.push('file');
            }
          } else {
            // 普通文件消息暂未实现（需要 file_url 或 file_path）
            logger.warn(`⚠️ [${i + 1}/${payload.length}] WorkTool 普通文件消息暂未实现（需要 file_url 或 file_path），跳过`);
            unsupportedTypes.push('file');
          }
          break;
        }

        case 'audio': {
          // ⚠️ TODO: 需要根据 WorkTool API 文档实现音频发送
          logger.warn(`⚠️ [${i + 1}/${payload.length}] WorkTool 音频消息暂未实现，跳过`);
          unsupportedTypes.push('audio');
          break;
        }

        default:
          logger.warn(`⚠️ [${i + 1}/${payload.length}] 未知的消息类型: ${(obj as any).type}`);
          unsupportedTypes.push((obj as any).type);
      }
    } catch (error: any) {
      logger.error(`❌ [${i + 1}/${payload.length}] WorkTool 转换消息失败:`, error.message);
    }
  }

  // 如果没有可发送的消息，直接返回
  if (batchItems.length === 0) {
    if (unsupportedTypes.length > 0) {
      logger.warn(`⚠️ WorkTool 没有可发送的消息（${unsupportedTypes.length} 条不支持的类型）`);
    }
    return;
  }

  // 批量发送（单次最多100条，如果超过需要分批）
  const MAX_BATCH_SIZE = 100;
  const batches: BatchSendItem[][] = [];

  for (let i = 0; i < batchItems.length; i += MAX_BATCH_SIZE) {
    batches.push(batchItems.slice(i, i + MAX_BATCH_SIZE));
  }

  logger.debug(`WorkTool 准备批量发送 ${batchItems.length} 条消息，分 ${batches.length} 批`);

  for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
    const batch = batches[batchIndex];

    try {
      const result = await batchSendMessages(robotId, {
        list: batch
      });

      if (result.code !== 200 && result.code !== 0) {
        throw new Error(`批量发送消息失败: ${result.message}`);
      }

      const batchStart = batchIndex * MAX_BATCH_SIZE + 1;
      const batchEnd = Math.min((batchIndex + 1) * MAX_BATCH_SIZE, batchItems.length);
      logger.sent(`📤 WorkTool 批量发送成功 [${batchStart}-${batchEnd}/${batchItems.length}] 到 ${titleList.join(', ')}`);

      if (result.data) {
        logger.debug(`   消息ID: ${result.data}`);
      }
    } catch (error: any) {
      logger.error(`❌ WorkTool 批量发送失败 [批次 ${batchIndex + 1}/${batches.length}]:`, error.message);
      // 继续发送下一批
    }
  }

  if (unsupportedTypes.length > 0) {
    logger.warn(`⚠️ WorkTool 跳过了 ${unsupportedTypes.length} 条不支持的消息类型`);
  }

  logger.sent(`✅ WorkTool 已完成 ${batchItems.length} 条消息的批量发送`);
}

/**
 * 根据平台分发消息
 */
async function dispatchToPlatform(event: OutboundEvent): Promise<void> {
  const { platform, user_id_external, channel_id } = event.target;

  // 多 Bot 支持：通过 platform 获取 bot 配置
  // platform 和 bot_id 一一对应
  const botManager = getBotManager();
  let botConfig = botManager.getBotByPlatform(platform);

  // 如果还是找不到，使用第一个可用的 bot（向后兼容）
  if (!botConfig) {
    const allBots = botManager.getAllBots();
    if (allBots.length > 0) {
      botConfig = allBots[0];
      logger.warn(`未找到 platform ${platform} 对应的 Bot，使用默认 Bot: ${botConfig.botId}`);
    } else {
      // 如果找不到 Bot 配置，抛出错误
      throw new Error(`无法找到 platform ${platform} 对应的 Bot 配置`);
    }
  }

  logger.debug(`使用 Bot: ${botConfig.botId} 发送消息 (platform: ${platform})`);

  // Payload 现在是 ContentObject[] 数组
  const payload = event.payload;

  if (!payload || !Array.isArray(payload) || payload.length === 0) {
    throw new Error('Payload 必须是非空数组');
  }

  // 确定接收者ID
  // 如果是群消息，使用 channel_id；如果是私聊，使用 user_id_external
  const toId = channel_id && channel_id !== '0' ? channel_id : user_id_external;

  // 根据 Bot 类型分发消息
  if (botConfig.type === 'qiwe') {
    await handlePayload(payload, toId, channel_id, botConfig);
  } else if (botConfig.type === 'worktool') {
    await handleWorkToolPayload(payload, toId, channel_id, botConfig);
  } else {
    throw new Error(`未知的 Bot 类型: ${(botConfig as any).type}，platform: ${platform}`);
  }
}

/**
 * 启动 Outbound 消费者
 * @param lanes 要监听的 lane 列表，默认为 ['user', 'admin','test']
 */
export async function startOutboundConsumers(lanes: Lane[] = ['user', 'admin', 'test']): Promise<void> {
  const idempotencyManager = getIdempotencyMgr();
  const conversationManager = getConversationMgr();

  for (const lane of lanes) {
    const consumer = createOutboundConsumer(
      lane,
      async (message: StreamMessage<OutboundEvent>) => {
        const event = message.data as OutboundEvent;
        logger.info(`📥 收到 Outbound 消息: event_id=${event.event_id}, type=${event.type}`);
        // 只处理 REPLY_MESSAGE 类型
        if (event.type !== 'REPLY_MESSAGE') {
          logger.debug(`跳过非 REPLY_MESSAGE 类型: ${event.type}`);
          return;
        }

        // 检查 payload 和 target 是否为空
        if (!event.payload || !event.target) {
          logger.warn(`跳过 payload 或 target 为空的消息: ${event.event_id}`);
          return;
        }

        // 幂等检查
        const acquired = await idempotencyManager.tryAcquire(event.event_id);
        if (!acquired) {
          logger.debug(`事件 ${event.event_id} 已处理，跳过`);
          return;
        }

        try {
          // 更新 conversation_id 映射
          if (event.target.conversation_id) {
            await conversationManager.setConversationId(event.target.platform, event.target.user_id_external, event.target.channel_id, event.target.conversation_id);
          }

          // 根据平台发送消息
          await dispatchToPlatform(event);

          // 高亮显示：消息已发送
          const toId = event.target.channel_id && event.target.channel_id !== '0' ? `群[${event.target.channel_id}]` : event.target.user_id_external;
          logger.sent(`📤 消息已发送 - platform=${event.target.platform}, toId=${toId}`);
        } catch (error: any) {
          // 处理失败，移除幂等标记以便重试
          await idempotencyManager.removeProcessedMark(event.event_id);
          logger.error(`❌ 处理消息失败: ${error.message}`, error);
          throw error;
        }
      },
      {
        consumerName: `server_outbound_${process.pid}`,
        maxRetries: 5,
        minIdleTimeMs: 30000
      }
    );

    await consumer.start();
    consumers.push(consumer);
    logger.info(`✅ 消费者已启动: lane=${lane}`);
  }
}

/**
 * 停止所有 Outbound 消费者
 */
export async function stopOutboundConsumers(): Promise<void> {
  logger.info('正在停止所有消费者...');
  const stopPromises = consumers.map((consumer) => consumer.stop());
  await Promise.all(stopPromises);
  consumers.length = 0; // 清空数组
  logger.info('✅ 所有消费者已停止');
}
