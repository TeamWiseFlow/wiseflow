#!/usr/bin/env bash
# proactive-send/scripts/send.sh
# 主动向 awada 客户发送消息（在 openclaw 消息处理循环之外）
#
# 用法：
#   bash ./skills/proactive-send/scripts/send.sh \
#     --awada-customer-id "wechat:ch001:wxid_abc123:default" \
#     --text "您好，昨天咱们聊过专业版的事，不知道今天方便看看吗？"
#
# 成功：打印 Redis stream message ID，exit 0
# 失败：打印错误信息到 stderr，exit 1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec node "$SCRIPT_DIR/send.mjs" "$@"
