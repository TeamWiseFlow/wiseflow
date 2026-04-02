/**
 * WorkTool API 类型定义
 * 根据 OpenAPI 文档: docs/worktool/worktool.openapi.json
 */

/** API 统一响应格式 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

/** 机器人信息 */
export interface RobotInfo {
  robotId: string;
  name: string;
  corporation?: string;
  sumInfo?: string; // 机器人完整信息，包含名称、备注等，用于匹配@的名称
  openCallback: number;
  encryptType: number;
  createTime: string;
  enableAdd: boolean;
  replyAll: number;
  robotKeyCheck: number;
  callBackRequestType: number;
  robotType: number;
  firstLogin?: string;
  authExpir?: string;
  [key: string]: any;
}

/** 机器人在线状态 */
export interface RobotOnlineStatus {
  online?: boolean;
  [key: string]: any;
}

/**
 * 设置回调地址请求参数
 * POST /robot/robotInfo/update
 */
export interface SetCallbackParams {
  /** 是否开启QA回调 0关闭 1开启 */
  openCallback: number;
  /** 开启回复策略（根据文档示例为数字，但类型定义是 string，这里支持两种类型） */
  replyAll: string | number;
  /** QA回调url */
  callbackUrl?: string;
}

/**
 * WorkTool QA回调消息（消息回调）
 * 文档: https://www.apifox.cn/apidoc/project-1035094/doc-861677
 * 消息回调接口规范: https://www.apifox.cn/apidoc/project-1035094/doc-861677
 */
export interface WorkToolCallbackMessage {
  /** 处理后的消息内容（去除了@信息等） */
  spoken: string;
  /** 原始消息内容 */
  rawSpoken: string;
  /** 提问者名称 */
  receivedName: string;
  /** QA所在群名（群聊） */
  groupName: string;
  /** QA所在群备注名（群聊） */
  groupRemark: string;
  /** 
   * QA所在房间类型
   * 1=外部群, 2=外部联系人, 3=内部群, 4=内部联系人
   */
  roomType: number;
  /** 是否@机器人（群聊）："true" 或 "false" */
  atMe: string;
  /** 
   * 消息类型
   * 0=未知, 1=文本, 2=图片, 3=语音, 5=视频, 7=小程序, 8=链接, 9=文件, 13=合并记录, 15=带回复文本
   */
  textType: number;
  /** 图片 base64 数据（PNG格式，图片消息时存在，textType=2） */
  fileBase64?: string;
  /** 其他可能的字段 */
  [key: string]: any;
}

/**
 * WorkTool QA回调响应
 * 需要在 3 秒内响应
 */
export interface WorkToolCallbackResponse {
  /** 0 调用成功，-1或其他值 调用失败并回复message */
  code: number;
  /** 对本次接口调用的信息描述 */
  message: string;
  /** 回答数据 */
  data: {
    /** 5000 回答类型为文本 */
    type: number;
    /** 回答结果集合 */
    info: {
      /** 回答文本(您期望的回复内容) \n可换行 */
      text: string;
    };
  };
}

