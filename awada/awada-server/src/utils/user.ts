/**
 * 混淆用户ID
 * 1. base64 编码
 * 2. 字符串反转
 * @param userId 原始用户ID
 * @returns 混淆后的用户ID字符串
 */
export function obfuscateUserId(userId: string): string {
  if (!userId) {
    throw new Error('用户ID不能为空');
  }

  try {
    // 1. base64 编码
    const encoded = btoa(userId);
    // 2. 字符串反转
    return encoded.split('').reverse().join('');
  } catch (error) {
    console.error('用户ID混淆失败:', error);
    throw new Error('用户ID混淆失败');
  }
}
