import { MsgType, SystemMsgType } from "@/services/qiweapi/types";

/** 普通消息类型名称映射 */
export const MsgTypeName: Record<number, string> = {
    [MsgType.TEXT]: '文本',
    [MsgType.TEXT_2]: '文本',
    [MsgType.IMAGE_WORK]: '企微图片',
    [MsgType.IMAGE_WORK_2]: '企微图片',
    [MsgType.IMAGE_WX]: '个微图片',
    [MsgType.VIDEO_WORK]: '企微视频',
    [MsgType.VIDEO_WX]: '个微视频',
    [MsgType.FILE_WORK]: '企微文件',
    [MsgType.FILE_WX]: '个微文件',
    [MsgType.VOICE]: '语音',
    [MsgType.LOCATION]: '位置',
    [MsgType.LINK]: '链接',
    [MsgType.CARD]: '名片',
    [MsgType.REDPACKET]: '红包',
    [MsgType.MINIPROGRAM]: '小程序',
    [MsgType.GIF_WORK]: '企微GIF',
    [MsgType.GIF_WX]: '个微GIF',
    [MsgType.MIXED]: '图文混合',
    [MsgType.VIDEO_CHANNEL]: '视频号',
    [MsgType.LIVE]: '直播',
    [MsgType.MSG_READ]: '已读通知',
    [MsgType.MSG_UNREAD]: '未读通知'
  };
  
  /** 系统消息类型名称映射 */
  export const SystemMsgTypeName: Record<number, string> = {
    [SystemMsgType.EXTERNAL_CONTACT_CHANGE]: '外部联系人变动',
    [SystemMsgType.EXTERNAL_CONTACT_BLACKLIST]: '外部联系人加黑名单',
    [SystemMsgType.INTERNAL_CONTACT_CHANGE]: '内部联系人变动',
    [SystemMsgType.FRIEND_APPLY]: '好友申请',
    [SystemMsgType.FRIEND_APPLY_2]: '好友申请',
    [SystemMsgType.CONTACT_MUTE_TOP]: '联系人免打扰/置顶',
    [SystemMsgType.CONTACT_MARK]: '联系人标记',
    [SystemMsgType.CHAT_TAG_CHANGE]: '聊天标签变动',
    [SystemMsgType.CHAT_TAG_CONTACT_CHANGE]: '聊天标签联系人变动',
    [SystemMsgType.CORP_TAG_CHANGE]: '企业标签变动',
    [SystemMsgType.PERSONAL_TAG_CHANGE]: '个人标签变动',
    [SystemMsgType.ROOM_NAME_CHANGE]: '群名变更',
    [SystemMsgType.ROOM_MEMBER_ADD]: '新增群成员',
    [SystemMsgType.ROOM_MEMBER_REMOVE]: '移除群成员',
    [SystemMsgType.ROOM_MEMBER_QUIT]: '成员退群',
    [SystemMsgType.ROOM_CREATE]: '群新增',
    [SystemMsgType.ROOM_OWNER_TRANSFER]: '转让群主',
    [SystemMsgType.ROOM_DISMISS]: '群解散',
    [SystemMsgType.ROOM_ADMIN_CHANGE]: '群管理员变动',
    [SystemMsgType.CHAT_CLEAR]: '清空聊天记录',
    [SystemMsgType.CHAT_DELETE]: '删除聊天'
  };
  