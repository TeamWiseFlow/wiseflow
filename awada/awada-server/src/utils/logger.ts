/**
 * 日志工具
 * 提供统一的日志方法，时间格式为北京时间（UTC+8）
 * 支持高亮显示，方便查找关键消息
 */

/**
 * ANSI 颜色代码
 */
const Colors = {
  RESET: '\x1b[0m',
  BRIGHT: '\x1b[1m',
  // 前景色
  BLACK: '\x1b[30m',
  RED: '\x1b[31m',
  GREEN: '\x1b[32m',
  YELLOW: '\x1b[33m',
  BLUE: '\x1b[34m',
  MAGENTA: '\x1b[35m',
  CYAN: '\x1b[36m',
  WHITE: '\x1b[37m',
  // 背景色
  BG_BLACK: '\x1b[40m',
  BG_RED: '\x1b[41m',
  BG_GREEN: '\x1b[42m',
  BG_YELLOW: '\x1b[43m',
  BG_BLUE: '\x1b[44m',
  BG_MAGENTA: '\x1b[45m',
  BG_CYAN: '\x1b[46m',
  BG_WHITE: '\x1b[47m',
} as const;

/**
 * 高亮样式
 */
export const Highlight = {
  /** 收到消息 - 绿色高亮 */
  RECEIVED: `${Colors.BRIGHT}${Colors.GREEN}`,
  /** 发送消息 - 蓝色高亮 */
  SENT: `${Colors.BRIGHT}${Colors.BLUE}`,
  /** 重要信息 - 黄色高亮 */
  IMPORTANT: `${Colors.BRIGHT}${Colors.YELLOW}`,
  /** 错误 - 红色高亮 */
  ERROR: `${Colors.BRIGHT}${Colors.RED}`,
  /** 重置颜色 */
  RESET: Colors.RESET,
} as const;

/**
 * 获取北京时间（UTC+8）的时间戳字符串
 * 格式: YYYY-MM-DD HH:mm:ss.SSS
 */
function getBeijingTime(): string {
  const now = new Date();
  // 获取 UTC 时间戳（毫秒）
  const utcTime = now.getTime() + (now.getTimezoneOffset() * 60 * 1000);
  // 转换为北京时间（UTC+8）
  const beijingTime = new Date(utcTime + (8 * 60 * 60 * 1000));
  
  const year = beijingTime.getFullYear();
  const month = String(beijingTime.getMonth() + 1).padStart(2, '0');
  const day = String(beijingTime.getDate()).padStart(2, '0');
  const hours = String(beijingTime.getHours()).padStart(2, '0');
  const minutes = String(beijingTime.getMinutes()).padStart(2, '0');
  const seconds = String(beijingTime.getSeconds()).padStart(2, '0');
  const milliseconds = String(beijingTime.getMilliseconds()).padStart(3, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds}`;
}

/**
 * 格式化日志消息
 */
function formatMessage(level: string, ...args: any[]): string {
  const timestamp = getBeijingTime();
  const messages = args.map(arg => {
    if (typeof arg === 'object') {
      try {
        return JSON.stringify(arg, null, 2);
      } catch {
        return String(arg);
      }
    }
    return String(arg);
  });
  
  return `[${timestamp}] [${level}] ${messages.join(' ')}`;
}

/**
 * 日志级别枚举
 */
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

/**
 * 日志工具类
 */
class Logger {
  private prefix: string;
  
  constructor(prefix: string = '') {
    this.prefix = prefix ? `[${prefix}]` : '';
  }
  
  /**
   * 创建带前缀的 Logger 实例
   */
  static create(prefix: string): Logger {
    return new Logger(prefix);
  }
  
  /**
   * 格式化带前缀的消息
   */
  private format(level: string, ...args: any[]): void {
    const timestamp = getBeijingTime();
    const prefix = this.prefix ? `${this.prefix} ` : '';
    const levelTag = `[${level}]`;
    
    // 如果第一个参数是字符串且包含特殊字符（如 emoji），直接输出
    if (args.length > 0 && typeof args[0] === 'string' && /[\u{1F300}-\u{1F9FF}]/u.test(args[0])) {
      console.log(`[${timestamp}] ${prefix}${levelTag}`, ...args);
    } else {
      // 格式化对象参数
      const formattedArgs = args.map(arg => {
        if (typeof arg === 'object' && arg !== null) {
          try {
            return JSON.stringify(arg, null, 2);
          } catch {
            return String(arg);
          }
        }
        return arg;
      });
      console.log(`[${timestamp}] ${prefix}${levelTag}`, ...formattedArgs);
    }
  }
  
  /**
   * 调试日志
   */
  debug(...args: any[]): void {
    this.format(LogLevel.DEBUG, ...args);
  }
  
  /**
   * 信息日志
   */
  info(...args: any[]): void {
    this.format(LogLevel.INFO, ...args);
  }
  
  /**
   * 警告日志
   */
  warn(...args: any[]): void {
    const timestamp = getBeijingTime();
    const prefix = this.prefix ? `${this.prefix} ` : '';
    console.warn(`[${timestamp}] ${prefix}[${LogLevel.WARN}]`, ...args);
  }
  
  /**
   * 错误日志
   */
  error(...args: any[]): void {
    const timestamp = getBeijingTime();
    const prefix = this.prefix ? `${this.prefix} ` : '';
    console.error(`[${timestamp}] ${prefix}[${LogLevel.ERROR}]`, ...args);
  }
  
  /**
   * 普通日志（兼容 console.log）
   */
  log(...args: any[]): void {
    this.info(...args);
  }
  
  /**
   * 高亮日志 - 收到消息（绿色高亮）
   */
  received(...args: any[]): void {
    const timestamp = getBeijingTime();
    const prefix = this.prefix ? `${this.prefix} ` : '';
    const highlightedArgs = args.map(arg => {
      if (typeof arg === 'string') {
        return `${Highlight.RECEIVED}${arg}${Highlight.RESET}`;
      }
      return arg;
    });
    console.log(`${Highlight.RECEIVED}[${timestamp}] ${prefix}[RECEIVED]${Highlight.RESET}`, ...highlightedArgs);
  }
  
  /**
   * 高亮日志 - 发送消息（蓝色高亮）
   */
  sent(...args: any[]): void {
    const timestamp = getBeijingTime();
    const prefix = this.prefix ? `${this.prefix} ` : '';
    const highlightedArgs = args.map(arg => {
      if (typeof arg === 'string') {
        return `${Highlight.SENT}${arg}${Highlight.RESET}`;
      }
      return arg;
    });
    console.log(`${Highlight.SENT}[${timestamp}] ${prefix}[SENT]${Highlight.RESET}`, ...highlightedArgs);
  }
}

/**
 * 默认 Logger 实例（无前缀）
 */
export const logger = new Logger();

/**
 * 创建带前缀的 Logger
 * @example
 * const webhookLogger = createLogger('Webhook');
 * webhookLogger.info('收到回调');
 */
export function createLogger(prefix: string): Logger {
  return Logger.create(prefix);
}

/**
 * 导出 Logger 类，方便扩展
 */
export { Logger };

/**
 * 便捷方法：直接使用默认 logger
 */
export const log = logger.log.bind(logger);
export const info = logger.info.bind(logger);
export const warn = logger.warn.bind(logger);
export const error = logger.error.bind(logger);
export const debug = logger.debug.bind(logger);

