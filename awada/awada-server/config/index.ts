const path = require('path');
const fs = require('fs');
import { Platform } from '@/src/infrastructure/redis';
import JSON5 from 'json5';
import { createLogger } from '../src/utils/logger';

const logger = createLogger('Config');

/** 路径配置 */
export const WechatyuiPath = path.join(__dirname, '../database/wechatyui');
export const FilesPath = path.join(__dirname, '../database/files');
export const CachePath = path.join(__dirname, '../database/cache');
export const ConfigPath = path.join(__dirname, './');

/** 静态配置类型 */
export interface StaticConfigType {
  variable_config: {
    welcome: string;
  };
  timeout: number;
  room_question: 'close' | 'open';
  directors: string[];
  common_order: {
    confirm: string;
    abort: string;
  };
  directors_order: {
    list: string;
    help: string;
    ding: string;
  };
  room_order: {
    start: string;
    stop: string;
    talking: string;
    update: string;
    list: string;
  };
  room_speech: {
    welcome: string;
    no_permission: string;
    person_join: string;
    modify_remarks: string;
    start: string;
    stop: string;
    update: string;
    open_talking: string;
    stop_talking: string;
    no_talking: string;
  };
  person_speech: {
    welcome: string;
    no_permission: string;
    room_stop: string;
  };
  common_speech: {
    bad_words: string;
    order_error: string;
    file_received: string;
    file_received_fail: string;
    file_saved: string;
    file_saved_success: string;
    file_list_none: string;
    file_list: string;
    file_delete: string;
    file_delete_start: string;
    file_delete_failed: string;
    file_delete_success: string;
    abort: string;
    help: string;
    ding: string;
  };
  request_speech: {
    ask_noanswer: string;
    audio_failed: string;
    error: string;
    path_error: string;
    retry: string;
  };
}

export let staticConfig: StaticConfigType | null = null;

// 是否需要权限控制
export let needPermission = false;

/**
 * 群ID映射配置（处理群ID偏移问题）
 * 通过环境变量 ROOM_ID_MAPPING 配置，格式为 JSON 字符串
 * 例如：ROOM_ID_MAPPING='{"10836417722719384":"10836417722719383"}'
 */
function loadRoomIdMapping(): Record<string, string> {
  const raw = process.env.ROOM_ID_MAPPING;
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    logger.warn('⚠️ ROOM_ID_MAPPING 解析失败，请检查 JSON 格式');
    return {};
  }
}

export const roomIdMapping: Record<string, string> = loadRoomIdMapping();

/**
 * 初始化全局配置
 */
export const init = async () => {
  logger.info('🌰🌰🌰 static config init 🌰🌰🌰');
  staticConfig = await getStaticConfig();
};

/**
 * 读取静态配置文件
 */
// export const getStaticConfig = async (): Promise<StaticConfigType> => {
//   const configPath = path.join(__dirname, './config.json');
//   try {
//     const content = fs.readFileSync(configPath, 'utf-8');
//     return JSON5.parse(content);
//   } catch (error) {
//     logger.error('读取配置文件失败:', error);
//     throw error;
//   }
// };
/** 获取项目全局配置 config.json */
export const getStaticConfig = async (): Promise<StaticConfigType> => {
  const res = await fs.readFileSync(`${ConfigPath}/config.json`, 'utf-8');

  let configValues = {};
  /** 对 ${} 进行匹配替换，只能匹配 ${a.b} 类型 */
  const result = JSON5.parse(res, (key, value) => {
    let newValue = value;

    // Type-safe set only for top-level keys of StaticConfigType
    // Using 'as any' since configValues is just a flat object mapping at this stage
    (configValues as any)[key] = value;

    if (typeof value === 'string') {
      const match = newValue.match(/\$\{.*?\}/g);
      if (!match || match.length === 0) return newValue;

      match.map((m: string) => {
        const fields = m
          .match(/\$\{(\S*)\}/)?.[1]
          ?.trim()
          .split('.');
        if (!fields || fields.length === 0) return;

        const fieldValue = fields.reduce((pre, next) => {
          return pre[next as keyof typeof pre];
        }, configValues);

        newValue = newValue.replace(m, fieldValue);
      });
    }
    return newValue;
  });

  return result;
};

const ConfigJson = path.join(__dirname, './config.json');

// 监听配置文件变化
if (fs.existsSync(ConfigJson)) {
  logger.info(`Watching for file changes on ${ConfigJson}`);
  fs.watch(ConfigJson, (event: string, filename: string) => {
    if (event === 'change') {
      logger.info(`${filename} file Changed`);
      init();
    }
  });
}

/**
 * 映射群ID（处理群ID偏移问题）
 * @param roomId 原始群ID
 * @returns 映射后的群ID（字符串），如果未配置映射则返回原值（转换为字符串），如果为空则返回 '0'
 */
export const mapRoomId = (roomId: string | undefined | null): string => {
  if (!roomId || Number(roomId) === 0) {
    return '0';
  }

  const roomIdStr = String(roomId);

  // 如果配置了映射，则使用映射后的值
  if (roomIdMapping[roomIdStr]) {
    const mappedId = roomIdMapping[roomIdStr];
    logger.debug(`群ID映射: ${roomIdStr} -> ${mappedId}`);
    return mappedId;
  }

  return roomIdStr;
};

/**
 * 常量配置
 */
export default {
  /** 应用名称，通过环境变量 APP_NAME 配置 */
  name: process.env.APP_NAME || 'awada-server',
  platform: process.env.PLATFORM as Platform,
  /** 默认导演ID，通过环境变量 DEFAULT_DIRECTOR_ID 配置 */
  defaultDirectorId: process.env.DEFAULT_DIRECTOR_ID || ''
};
