/**
 * qiweapi 服务模块导出
 */

export { apiClient } from "./client";
export * from "./types";
export * as instanceModule from "./instance";
export * as loginModule from "./login";
export * as messageModule from "./message";
export * as contactModule from "./contact";
export * as cdnModule from "./cdn";

// 便捷导出 - 实例管理
export {
  createClient,
  recoverClient,
  stopClient,
  setCallbackUrl,
} from "./instance";

// 便捷导出 - 登录模块
export {
  getLoginQrcode,
  checkLogin,
  verifyQrCode,
  checkQrCode,  // deprecated, use verifyQrCode
  login,
  getUserStatus,
  waitForLogin,
  getLoginStatus,
  getCurrentUser,
  LoginStatus,
} from "./login";

// 便捷导出 - 消息模块
export {
  sendTextMsg,
  sendMixTextMsg,
  sendImageMsg,
  sendFileMsg,
  sendMessage,
} from "./message";

// 便捷导出 - 联系人模块
export {
  agreeContact,
  acceptFriend,
} from "./contact";

// 便捷导出 - CDN模块
export {
  uploadFile,
  uploadImage,
  uploadVideo,
  uploadDocument,
} from "./cdn";
