/**
 * qiweapi 类型定义
 * 文档地址: https://doc.qiweapi.com/
 * 
 * API 统一入口: POST /api/qw/doApi
 * 通过 method 字段指定具体操作
 */

// ==================== 通用类型 ====================

/** API 统一请求格式 */
export interface ApiRequest<T = any> {
  /** 执行方法，如 /client/createClient */
  method: string;
  /** 请求参数 */
  params: T;
}

/** API 统一响应格式 */
export interface ApiResponse<T = any> {
  /** 状态码，0 表示成功 */
  code: number;
  /** 消息 */
  msg: string;
  /** 数据 */
  data: T;
}

// ==================== 实例管理 ====================

/** 
 * 创建设备请求参数
 * method: /client/createClient
 */
export interface CreateClientParams {
  /** 代理地址，格式: scheme://user:password@ip:port，支持 socks5 */
  proxyUrl?: string;
  /** 
   * 代理地区代码
   * 110000:北京 120000:天津 130000:河北 140000:山西 210000:辽宁
   * 220000:吉林 230000:黑龙江 310000:上海 320000:江苏 330000:浙江
   * 340000:安徽 350000:福建 360000:江西 370000:山东 410000:河南
   * 420000:湖北 430000:湖南 440000:广东 450000:广西 460000:海南
   * 500000:重庆 510000:四川 520000:贵州 530000:云南 540000:西藏
   * 610000:陕西 620000:甘肃 630000:青海 640000:宁夏 150000:内蒙古
   * 650000:新疆
   */
  areaCode: number;
  /** 设备名称 */
  deviceName: string;
  /** 
   * 设备类型
   * 0-ipad, 2-windows, 3-macOS, 4-android, 5-iOS
   * 目前支持 ipad 和 windows
   */
  deviceType: number;
  /** 
   * 客户端版本号
   * 支持: 4.1.36.6011、5.0.0.6008
   */
  clientVersion: string;
}

/** 创建设备响应数据 */
export interface CreateClientData {
  /** 设备GUID */
  guid: string;
}

/** 
 * 恢复实例请求参数
 * method: /client/restoreClient
 */
export interface RecoverClientParams {
  /** 设备GUID */
  guid: string;
}

/** 
 * 停止实例请求参数
 * method: /client/stopClient
 */
export interface StopClientParams {
  /** 设备GUID */
  guid: string;
}

/** 
 * 设置回调地址请求参数
 * method: /client/setCallback
 * 
 * 说明：
 * - 回调按用户token来推送消息，该token下的所有账号消息都会推送到此URL
 * - 各租户间的消息有数据隔离
 */
export interface SetCallbackParams {
  /** 回调地址 */
  callbackUrl: string;
}

// ==================== 登录模块 ====================

/**
 * 获取二维码请求参数
 * method: /login/getLoginQrcode
 * 
 * 说明：
 * - useCache=false: 主动扫码模式，强制获取新的登录二维码，使用手机主动扫码
 * - useCache=true: 被动确认模式，推送登录授权消息到（实例上最近一次登录过的）账号对应的手机端
 */
export interface GetLoginQrcodeParams {
  /** 设备GUID/实例ID */
  guid: string;
  /** 
   * 是否使用缓存数据
   * - false: 主动扫码模式（默认）
   * - true: 被动确认模式
   */
  useCache: boolean;
}

/** 获取二维码响应数据 */
export interface GetLoginQrcodeData {
  /** 
   * 二维码数据流（base64）
   * 实例上登过账号且 useCache=true 时为空，否则有值
   */
  loginQrcodeBase64Data?: string;
  /** 二维码key */
  loginQrcodeKey: string;
}

/**
 * 检测二维码状态请求参数
 * method: /login/checkLoginQrCode
 */
export interface CheckLoginParams {
  /** 设备GUID */
  guid: string;
}

/** 
 * 检测登录状态响应数据
 * 
 * loginQrcodeStatus 状态码:
 * -1: 登录状态失效，需要重新扫码登陆
 *  0: 未登陆，可免扫码登陆
 *  1: 已扫码，待确认
 *  2: 登陆成功
 *  3: 登陆失败
 *  4: 用户取消登陆
 * 10: 已扫码确认，待检测6位验证码
 */
export interface CheckLoginData {
  /** 登录状态码 */
  loginQrcodeStatus: number;
  /** 二维码key */
  loginQrcodeKey: string;
  /** 用户昵称 */
  nickname: string;
  /** 用户ID */
  userId: string;
  /** 用户头像URL */
  avatarUrl: string;
  /** 企业ID */
  corpId: string;
  /** 企业Logo */
  corpLogo: string;
}

/**
 * 二维码 code 验证请求参数
 * method: /login/verifyLoginQrcode
 * 
 * 说明：
 * - 只有新实例登陆时才需要调用
 * - 验证码验证成功后需再次调用二维码-检测接口即可登录成功
 */
export interface CheckQrCodeParams {
  /** 设备GUID */
  guid: string;
  /** 6位登录验证码 */
  code: string;
}

/**
 * 用户登录请求参数
 * method: /login/login
 */
export interface LoginParams {
  /** 设备GUID */
  guid: string;
}

/**
 * 用户状态请求参数
 * method: /user/getProfile
 */
export interface GetUserStatusParams {
  /** 设备GUID */
  guid: string;
}

/**
 * 获取个人信息 API 返回的原始数据
 * method: /user/getProfile
 */
export interface GetProfileData {
  /** 账户id */
  acctid: string;
  /** 别名 */
  alias: string;
  /** 头像URL */
  avatarUrl: string;
  /** 企业ID */
  corpId: string;
  /** 性别 */
  gender: number;
  /** 组ID */
  groupId: string;
  /** 国际区号 */
  internationCode: string;
  /** 手机号 */
  mobile: string;
  /** 昵称 */
  nickname: string;
  /** 真实姓名 */
  realName: string;
  /** 用户ID (对应 wxid) */
  userId: string;
}

/** 用户状态响应数据 */
export interface UserStatusData {
  /** 是否在线 */
  online?: boolean;
  /** 用户wxid */
  wxid?: string;
  /** 用户昵称 */
  nickName?: string;
  /** 用户头像 */
  headImgUrl?: string;
  /** 企业ID */
  corpId?: string;
}

// ==================== 消息模块 ====================

/**
 * 发送纯文本消息请求参数
 * method: /msg/sendText
 */
export interface SendTextMsgParams {
  /** 设备GUID */
  guid: string;
  /** 接收者ID（字符串类型，如 '1688855655434798'） */
  toId: string;
  /** 消息内容 */
  content: string;
}

/**
 * 混合文本消息内容项
 */
export interface HyperTextContentItem {
  /** 
   * 子类型
   * 0: 普通文本
   * 1: @具体人（text为对方的userId，当text为"0"时为@所有人）
   * 2: 系统表情（如：[微笑][憨笑]）
   */
  subtype: number;
  /** 文本内容 */
  text: string;
}

/**
 * 发送混合文本消息请求参数（支持@、表情等）
 * method: /msg/sendHyperText
 * 文档: https://doc.qiweapi.com/api-344613907.md
 */
export interface SendHyperTextMsgParams {
  /** 设备GUID */
  guid: string;
  /** 接收者ID */
  toId: string;
  /** 消息内容数组 */
  content: HyperTextContentItem[];
}

/** @deprecated 使用 SendHyperTextMsgParams 代替 */
export type SendMixTextMsgParams = SendHyperTextMsgParams;

/**
 * 发送图片消息请求参数
 * method: /msg/sendImage
 * 文档: https://doc.qiweapi.com/api-344613908.md
 * 
 * 说明：图片消息参数可以通过文件上传或文件上传-URL接口获取
 */
export interface SendImageMsgParams {
  /** 设备GUID */
  guid: string;
  /** 接收者ID */
  toId: string;
  /** 文件AES密钥（通过上传文件获得） */
  fileAesKey: string;
  /** 文件ID（通过上传文件获得） */
  fileId: string;
  /** 文件Key */
  fileKey: string;
  /** 文件MD5 */
  fileMd5: string;
  /** 文件大小 */
  fileSize: number;
  /** 文件名 */
  filename: string;
}

/**
 * 发送文件消息请求参数
 * method: /msg/sendFile
 * 
 * 根据文档，发送文件需要 fileId 和 fileAesKey（通过上传文件获得）
 */
export interface SendFileMsgParams {
  /** 设备GUID */
  guid: string;
  /** 接收者ID */
  toId: string;
  /** 文件AES密钥（通过上传文件获得） */
  fileAesKey: string;
  /** 文件ID（通过上传文件获得） */
  fileId: string;
  /** 文件大小 */
  fileSize: number;
  /** 文件名 */
  filename: string;
}

/**
 * 发送语音消息请求参数
 * method: /msg/sendVoice
 * 文档: https://doc.qiweapi.com/api-344613912.md
 * 
 * 说明：AMR格式，语音消息参数可以通过文件上传或文件上传-URL接口获取
 */
export interface SendVoiceMsgParams {
  /** 设备GUID */
  guid: string;
  /** 接收者ID */
  toId: string;
  /** 文件AES密钥（通过上传文件获得） */
  fileAesKey: string;
  /** 文件ID（通过上传文件获得） */
  fileId: string;
  /** 文件大小 */
  fileSize: number;
  /** 语音时长（秒） */
  voiceTime: number;
}

/** 发送消息响应数据 */
export interface SendMsgData {
  /** 消息ID */
  msgId?: string;
  /** 消息SVR ID */
  msgSvrId?: string;
}

// ==================== 消息回调 ====================

/**
 * 回调类型 (cmd)
 * 文档: https://doc.qiweapi.com/doc-7331304
 */
export enum CallbackCmd {
  /** 账号状态变化消息 */
  ACCOUNT_STATUS = 11016,
  /** API异步消息 */
  API_ASYNC = 20000,
  /** VX系统消息 */
  SYSTEM = 15500,
  /** VX普通消息 */
  MESSAGE = 15000,
}

/**
 * 账号状态码 (msgData.code) - cmd=11016时
 */
export enum AccountStatusCode {
  /** 登录成功 */
  LOGIN_SUCCESS = 11001,
  /** 注销成功 */
  LOGOUT_SUCCESS = 11002,
  /** 刷新session失败 */
  SESSION_REFRESH_FAILED = 11013,
  /** 其它端顶号 */
  KICKED_BY_OTHER = 11017,
  /** 手机端主动退出，取消设备授权 */
  PHONE_LOGOUT = 11022,
  /** 账号环境出现异常，请重新登录使用 */
  ACCOUNT_ABNORMAL = 11023,
  /** 登录态已过期，请重新登录 */
  LOGIN_EXPIRED = 11024,
  /** 新设备需验证 */
  NEW_DEVICE_VERIFY = 11025,
}

/**
 * 系统消息类型 (msgType) - cmd=15500时
 */
export enum SystemMsgType {
  // 联系人相关
  /** 外部联系人信息变动或删除通知 */
  EXTERNAL_CONTACT_CHANGE = 2131,
  /** 外部联系人加入黑名单通知 */
  EXTERNAL_CONTACT_BLACKLIST = 2313,
  /** 内部联系人信息变动通知 */
  INTERNAL_CONTACT_CHANGE = 2188,
  /** 好友申请通知 */
  FRIEND_APPLY = 2357,
  /** 好友申请通知(另一种) */
  FRIEND_APPLY_2 = 2132,
  /** 联系人免打扰/置顶通知 */
  CONTACT_MUTE_TOP = 2104,
  /** 联系人标记操作通知 */
  CONTACT_MARK = 2115,
  
  // 标签相关
  /** 聊天标签变动通知 */
  CHAT_TAG_CHANGE = 2160,
  /** 聊天标签中的联系人变动通知 */
  CHAT_TAG_CONTACT_CHANGE = 2161,
  /** 企业标签新增或删除通知 */
  CORP_TAG_CHANGE = 2185,
  /** 个人标签新增或删除通知 */
  PERSONAL_TAG_CHANGE = 2186,
  
  // 群相关
  /** 群名变换通知 */
  ROOM_NAME_CHANGE = 1001,
  /** 新增群成员通知 */
  ROOM_MEMBER_ADD = 1002,
  /** 移除群成员通知 */
  ROOM_MEMBER_REMOVE = 1003,
  /** 群成员自己退群通知 */
  ROOM_MEMBER_QUIT = 1005,
  /** 群新增通知 */
  ROOM_CREATE = 1006,
  /** 转让群主通知 */
  ROOM_OWNER_TRANSFER = 1022,
  /** 群解散通知 */
  ROOM_DISMISS = 1023,
  /** 群管理员变动通知 */
  ROOM_ADMIN_CHANGE = 1043,
  
  // 会话消息
  /** 清空聊天记录通知 */
  CHAT_CLEAR = 2055,
  /** 删除聊天通知 */
  CHAT_DELETE = 2002,
}

/** 
 * 普通消息类型 (msgType) - cmd=15000时
 * 文档: https://doc.qiweapi.com/doc-7331304
 */
export enum MsgType {
  /** 文本消息 */
  TEXT = 0,
  /** 文本消息(另一种) */
  TEXT_2 = 2,
  /** 位置消息 */
  LOCATION = 6,
  /** 企微图片消息 */
  IMAGE_WORK = 7,
  /** 链接消息 */
  LINK = 13,
  /** 企微图片消息 */
  IMAGE_WORK_2 = 14,
  /** 企微文件消息 */
  FILE_WORK = 15,
  /** 语音消息 */
  VOICE = 16,
  /** 大文件(>20M) / 企微文件 */
  FILE_LARGE = 20,
  /** 大视频(>20M) / 企微视频 */
  VIDEO_LARGE = 22,
  /** 企微视频消息 */
  VIDEO_WORK = 23,
  /** 红包消息 */
  REDPACKET = 26,
  /** 企微GIF消息 */
  GIF_WORK = 29,
  /** 名片消息 */
  CARD = 41,
  /** 小程序消息 */
  MINIPROGRAM = 78,
  /** 个微图片消息 */
  IMAGE_WX = 101,
  /** 个微文件消息 */
  FILE_WX = 102,
  /** 个微视频消息 */
  VIDEO_WX = 103,
  /** 个微GIF消息 */
  GIF_WX = 104,
  /** 图文混合消息 */
  MIXED = 123,
  /** 视频号消息 */
  VIDEO_CHANNEL = 141,
  /** 直播消息 */
  LIVE = 146,
  /** 消息已读通知 */
  MSG_READ = 2001,
  /** 消息未读通知 */
  MSG_UNREAD = 2005,
}

/** 
 * 回调消息原始格式
 * 文档: https://doc.qiweapi.com/doc-7331304
 */
export interface CallbackMessageRaw {
  /** 租户ID */
  TenantId?: number;
  /** 设备GUID */
  guid: string;
  /** 用户ID */
  userId: string;
  /** 请求ID */
  requestId: string;
  /** 自定义参数 */
  customParam?: string;
  /** 回调类型: 11016-账号状态 20000-API异步 15500-系统消息 15000-普通消息 */
  cmd: number;
  /** 原始数据base64 */
  base64RawData?: string;
  /** 来自群ID（群消息时有值） */
  fromRoomId?: string;
  /** 是否群通知：0-否 1-是 */
  isRoomNotice?: number;
  /** 消息数据（不同类型结构不同） */
  msgData: any;
  /** 消息服务器ID */
  msgServerId: number;
  /** 消息类型 */
  msgType: number;
  /** 消息唯一标识 */
  msgUniqueIdentifier: string;
  /** 接收者ID */
  receiverId?: number;
  /** 发送者ID */
  senderId: number;
  /** 发送者名称 */
  senderName?: string;
  /** 序列号 */
  seq?: number;
  /** 时间戳（秒） */
  timestamp: number;
}

/**
 * 回调响应包装
 */
export interface CallbackResponse {
  code: number;
  msg: string;
  data: CallbackMessageRaw[];
}

// ==================== 消息数据结构 (msgData) ====================

/** 文本消息数据 - msgType=0/2 */
export interface TextMsgData {
  content: string;
  atList?: Array<{
    userId: string;
    nickname: string;
  }>;
}

/** 企微图片消息数据 - msgType=14 */
export interface ImageWorkMsgData {
  fileAeskey: string;
  fileId: string;
  fileMd5: string;
  fileName: string;
  fileSize: number;
  imageHasHd: boolean;
}

/** 个微图片消息数据 - msgType=101 */
export interface ImageWxMsgData {
  fileAeskey: string;
  fileAuthkey: string;
  fileBigHttpUrl: string;
  fileBigSize: number;
  fileMd5: string;
  fileMiddleHttpUrl: string;
  fileMiddleSize: number;
  fileName: string;
  fileThumbHttpUrl: string;
  fileThumbSize: number;
  imageHasHd: boolean;
}

/** 企微视频消息数据 - msgType=23 */
export interface VideoWorkMsgData {
  coverImageAeskey: string;
  coverImageId: string;
  coverImageMd5: string;
  coverImageSize: number;
  duration: number;
  fileAeskey: string;
  fileId: string;
  fileMd5: string;
  fileName: string;
  fileSize: number;
}

/** 个微视频消息数据 - msgType=103 */
export interface VideoWxMsgData {
  coverImageHttpUrl: string;
  coverImageSize: number;
  duration: number;
  fileAeskey: string;
  fileAuthkey: string;
  fileHttpUrl: string;
  fileMd5: string;
  fileName: string;
  fileSize: number;
}

/** 企微文件消息数据 - msgType=15 */
export interface FileWorkMsgData {
  fileAeskey: string;
  fileId: string;
  fileMd5: string;
  fileName: string;
  fileNameExt: string;
  fileSize: number;
}

/** 个微文件消息数据 - msgType=102 */
export interface FileWxMsgData {
  fileAesKey: string;  // 注意：实际API返回的是 fileAesKey（大写K）
  fileAuthKey: string; // 注意：实际API返回的是 fileAuthKey（大写K）
  fileHttpUrl: string;
  fileMd5: string;
  fileName: string;
  fileSize: number;
  filename?: string;   // 有些情况下字段名是 filename（小写f）
}

/** 语音消息数据 - msgType=16 */
export interface VoiceMsgData {
  fileAesKey: string;
  fileId: string;
  fileMd5: string;
  fileSize: number;
  voiceTime: number;
}

/** 位置消息数据 - msgType=6 */
export interface LocationMsgData {
  address: string;
  latitude: number;
  longitude: number;
  title: string;
  zoom: number;
}

/** 链接消息数据 - msgType=13 */
export interface LinkMsgData {
  desc: string;
  iconUrl: string;
  linkUrl: string;
  title: string;
  iconAeskey?: string;
  iconAuthkey?: string;
  iconSize?: number;
}

/** 名片消息数据 - msgType=41 */
export interface CardMsgData {
  avatarUrl: string;
  corpId: number;
  corpName: string;
  nickname: string;
  realName: string;
  shared_id: string;
}

/** 红包消息数据 - msgType=26 */
export interface RedPacketMsgData {
  coverUrl1x: string;
  coverUrl2x: string;
  hongbaoSubtype: number;
  hongbaoType: number;
  lookWording: string;
  orderId: string;
  recvWording: string;
  ticket: string;
  toIdList: string[];
  totalAmount: number;
  wishingContent: string;
}

/** 小程序消息数据 - msgType=78 */
export interface MiniProgramMsgData {
  appid: string;
  coverImageAeskey: string;
  coverImageId: string;
  coverImage_md5: string;
  coverImageSize: number;
  desc: string;
  iconUrl: string;
  pagepath: string;
  title: string;
  username: string;
}

/** 好友申请通知数据 - msgType=2357 */
export interface FriendApplyMsgData {
  applyTime: number;
  contactId: number;
  contactNickname: string;
  contactType: string;
  userId: number;
}

/** 群成员变动数据 - msgType=1002/1003等 */
export interface RoomMemberChangeMsgData {
  changedMemberList: string;
}

/** 账号状态变化数据 - cmd=11016 */
export interface AccountStatusMsgData {
  guid: string;
  msg: string;
  code: number;
  status: number;
  serverReboot?: boolean;
}

// ==================== 解析后的消息格式 ====================

/** 
 * 消息回调（解析后的标准格式）
 * 用于内部业务处理
 */
export interface CallbackMessage {
  /** 设备GUID */
  guid: string;
  /** 用户ID */
  userId: string;
  /** 回调类型 */
  cmd: number;
  /** 消息类型 */
  msgType: number;
  /** 消息服务器ID */
  msgServerId: number;
  /** 消息唯一标识 */
  msgUniqueIdentifier: string;
  /** 发送者ID */
  senderId: number;
  /** 发送者名称 */
  senderName: string;
  /** 接收者ID */
  receiverId: number;
  /** 来自群ID（群消息时） */
  fromRoomId: string;
  /** 是否群通知 */
  isRoomNotice: boolean;
  /** 消息内容（文本消息时） */
  content: string;
  /** @列表（文本消息时） */
  atList: Array<{ userId: string; nickname: string }>;
  /** 时间戳（秒） */
  timestamp: number;
  /** 序列号 */
  seq?: number;
  /** 原始消息数据 */
  msgData: any;
  /** 原始base64数据 */
  base64RawData?: string;
  /** 原始数据 */
  raw?: CallbackMessageRaw;
}

/** 好友申请回调 - msgType=2357 */
export interface FriendApplyCallback {
  /** 设备GUID */
  guid: string;
  /** 用户ID */
  userId: string;
  /** 申请时间 */
  applyTime: number;
  /** 联系人ID */
  contactId: number;
  /** 联系人昵称 */
  contactNickname: string;
  /** 联系人类型: 微信/企微 */
  contactType: string;
  /** 原始数据 */
  raw?: CallbackMessageRaw;
}

/** 群成员变动回调 - msgType=1002/1003/1005 */
export interface RoomMemberChangeCallback {
  /** 设备GUID */
  guid: string;
  /** 用户ID */
  userId: string;
  /** 群ID */
  fromRoomId: string;
  /** 消息类型: 1002-新增 1003-移除 1005-退群 */
  msgType: number;
  /** 变动的成员列表(base64) */
  changedMemberList: string;
  /** 发送者ID */
  senderId: number;
  /** 时间戳 */
  timestamp: number;
  /** 原始数据 */
  raw?: CallbackMessageRaw;
}

/** 账号状态变化回调 - cmd=11016 */
export interface AccountStatusCallback {
  /** 设备GUID */
  guid: string;
  /** 用户ID */
  userId: string;
  /** 状态码: 11001-登录成功 11002-注销成功 等 */
  code: number;
  /** 状态消息 */
  msg: string;
  /** 二维码状态: 0/-1-离线 1-已扫码待确认 2-在线 3-登录失败 4-用户取消 10-待输验证码 */
  status: number;
  /** 服务重启标记 */
  serverReboot: boolean;
  /** 原始数据 */
  raw?: CallbackMessageRaw;
}

// ==================== 联系人模块 ====================

/**
 * 联系人详情批量请求参数
 * method: /contact/getContactList
 */
export interface GetContactListParams {
  /** 设备GUID */
  guid: string;
  /** wxid列表 */
  wxidList: string[];
}

/** 联系人信息 */
export interface ContactInfo {
  /** wxid */
  wxid: string;
  /** 昵称 */
  nickName: string;
  /** 头像URL */
  headImgUrl?: string;
  /** 备注名 */
  remark?: string;
  /** 性别：0未知 1男 2女 */
  sex?: number;
  /** 地区 */
  area?: string;
}

/**
 * 同意好友申请请求参数
 * method: /contact/agreeContact
 */
export interface AcceptFriendParams {
  /** 设备GUID */
  guid: string;
  /** 申请者用户ID */
  userId: string;
  /** 企业ID */
  corpId: string;
}

// ==================== 群模块 ====================

/**
 * 群详情批量请求参数
 * method: /chatroom/getChatRoomInfo
 */
export interface GetChatRoomInfoParams {
  /** 设备GUID */
  guid: string;
  /** 群ID列表 */
  chatRoomIdList: string[];
}

/** 群信息 */
export interface ChatRoomInfo {
  /** 群ID */
  chatRoomId: string;
  /** 群名称 */
  nickName: string;
  /** 群头像 */
  headImgUrl?: string;
  /** 群公告 */
  notice?: string;
  /** 群主wxid */
  ownerWxid?: string;
  /** 成员数量 */
  memberCount?: number;
  /** 成员wxid列表 */
  memberList?: string[];
}

// ==================== CDN模块 ====================

/**
 * 文件类型枚举
 */
export enum FileType {
  /** JPG图片 */
  IMAGE = 1,
  /** MP4视频 */
  VIDEO = 4,
  /** 文件（包括语音amr） */
  FILE = 5,
}

/**
 * 文件上传请求参数
 * 端点: POST /api/qw/doFileApi (multipart/form-data)
 * method: /cloud/cdnBigUpload
 */
export interface UploadFileParams {
  /** 设备GUID */
  guid: string;
  /** 文件（二进制） */
  file: File | Buffer | Blob;
  /** 
   * 文件类型
   * 1: jpg图片
   * 4: mp4视频
   * 5: 文件(也包括语音amr文件)
   */
  fileType: FileType | number;
}

/** 文件上传响应数据 */
export interface UploadFileData {
  /** 文件AES密钥 */
  fileAesKey: string;
  /** 文件ID */
  fileId: string;
  /** 文件Key */
  fileKey: string;
  /** 文件MD5 */
  fileMd5: string;
  /** 文件大小 */
  fileSize: number;
  /** 缩略图大小 */
  fileThumbSize: number;
  /** 时长（视频/语音） */
  durationTime: number;
}

/**
 * 通过 URL 上传文件请求参数
 * method: /cloud/cdnBigUploadByUrl
 * 端点: POST /api/qw/doApi (application/json)
 */
export interface UploadFileByUrlParams {
  /** 设备GUID */
  guid: string;
  /** 文件名 */
  filename: string;
  /** 文件URL */
  fileUrl: string;
  /** 
   * 文件类型
   * 1: jpg图片
   * 4: mp4视频
   * 5: 文件(也包括语音amr文件)
   */
  fileType: FileType | number;
}

/** 通过 URL 上传文件响应数据 */
export interface UploadFileByUrlData {
  /** 文件AES密钥 */
  fileAesKey: string;
  /** 文件ID */
  fileId: string;
  /** 文件Key */
  fileKey: string;
  /** 文件MD5 */
  fileMd5: string;
  /** 文件大小 */
  fileSize: number;
  /** 缩略图大小 */
  fileThumbSize: number;
  /** 云存储URL（可访问的临时地址） */
  cloudUrl: string;
  /** 文件名 */
  filename: string;
}

/**
 * 企微文件下载请求参数
 * method: /cloud/wxWorkDownload
 * 文档: https://doc.qiweapi.com/api-344613901.md
 * 
 * 说明：下载响应的地址为临时云资源，非官方CDN地址，并且会定期清理，请自行及时下载
 */
export interface DownloadFileParams {
  /** 设备GUID */
  guid: string;
  /** 文件AES密钥 */
  fileAeskey: string;
  /** 文件ID */
  fileId: string;
  /** 文件大小 */
  fileSize: number;
  /** 
   * 文件类型
   * 1: 大图（如果 image_has_hd=1，则可以使用这个type下载）
   * 2: 小图（如果 image_has_hd=0，则应该用这个type下载）
   * 3: 视频/图片缩略图（对应thumb这个字段）
   * 4: 视频
   * 5: 文件/语音文件
   */
  fileType: number;
}

/** 企微文件下载响应数据 */
export interface DownloadFileData {
  /** 云存储URL（临时地址，会定期清理） */
  cloudUrl: string;
}

/**
 * 个微文件下载请求参数
 * method: /cloud/wxDownload
 */
export interface WxDownloadFileParams {
  /** 设备GUID */
  guid: string;
  /** 文件AES密钥 */
  fileAeskey: string;
  /** 文件认证密钥 */
  fileAuthkey: string;
  /** 文件大小 */
  fileSize: number;
  /** 
   * 文件类型
   * 1: 大图（如果 image_has_hd=1 或 fileBigHttpUrl 有值）
   * 2: 小图（如果 image_has_hd=0 或 fileMiddleHttpUrl 有值）
   * 3: 视频/图片缩略图（对应 thumb）
   * 4: 视频
   * 5: 文件/语音文件
   */
  fileType: number;
  /** 文件URL（从 fileHttpUrl 获取） */
  fileUrl: string;
}

/** 个微文件下载响应数据 */
export interface WxDownloadFileData {
  /** 云存储URL（可访问的临时地址） */
  cloudUrl: string;
}

// ==================== API Methods 常量 ====================

/** API方法常量 */
export const API_METHODS = {
  // 实例管理
  CREATE_CLIENT: '/client/createClient',
  RECOVER_CLIENT: '/client/restoreClient',  // 恢复实例
  STOP_CLIENT: '/client/stopClient',
  SET_CALLBACK: '/client/setCallback',
  
  // 登录模块
  GET_LOGIN_QRCODE: '/login/getLoginQrcode',
  CHECK_LOGIN: '/login/checkLoginQrCode',       // 二维码-检测
  CHECK_LOGIN_STATUS: '/login/checkLogin',       // 登录状态检测（获取用户信息）
  VERIFY_QRCODE: '/login/verifyLoginQrcode',    // 二维码-code验证
  LOGIN: '/login/login',
  
  // 用户模块
  GET_USER_PROFILE: '/user/getProfile',  // 获取个人信息
  
  // 消息模块
  SEND_TEXT_MSG: '/msg/sendText',
  SEND_HYPER_TEXT_MSG: '/msg/sendHyperText',  // 发送混合文本消息（支持@、表情）
  SEND_IMAGE_MSG: '/msg/sendImage',           // 发送图片消息
  SEND_FILE_MSG: '/msg/sendFile',             // 发送文件消息
  SEND_VOICE_MSG: '/msg/sendVoice',           // 发送语音消息（AMR格式）
  
  /** @deprecated 使用 SEND_HYPER_TEXT_MSG 代替 */
  SEND_MIX_TEXT_MSG: '/msg/sendHyperText',
  
  // 联系人模块
  GET_CONTACT_LIST: '/contact/getContactList',
  AGREE_CONTACT: '/contact/agreeContact',  // 同意好友申请
  
  // 群模块
  GET_CHATROOM_INFO: '/chatroom/getChatRoomInfo',
  
  // CDN模块
  UPLOAD_FILE: '/cloud/cdnBigUpload',  // 文件上传（multipart/form-data）
  UPLOAD_FILE_BY_URL: '/cloud/cdnBigUploadByUrl', // 文件上传-URL（application/json）
  DOWNLOAD_FILE: '/cloud/wxWorkDownload',  // 企微文件下载（临时云资源）
  WX_DOWNLOAD_FILE: '/cloud/wxDownload',   // 个微文件下载
} as const;
