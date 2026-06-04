#!/usr/bin/env bash
# publish-wx-mp.sh — 推送 Markdown 稿件到微信公众号草稿箱
#
# Usage: publish-wx-mp.sh <markdown_file> [theme]
#   theme: default|orangeheart|rainbow|lapis|pie|maize|purple|phycat（默认 pie）
#
# 环境变量（优先本地直连）：
#   本地直连：WECHAT_APP_ID + WECHAT_APP_SECRET
#   relay  ：WENYAN_SERVER_URL + WENYAN_API_KEY
#   可选   ：WECHAT_TARGET_APP_ID（多公众号时指定目标 AppID）
#            WENYAN_PROXY（代理，如 http://127.0.0.1:7890）

set -euo pipefail

MD_FILE="${1:?Usage: publish-wx-mp.sh <markdown_file> [theme]}"
THEME="${2:-pie}"

[[ -f "$MD_FILE" ]] || { echo "ERROR: 文件不存在: $MD_FILE"; exit 1; }

# ── 模式判断（优先本地直连）─────────────────────────────────────────────────
if [[ -n "${WECHAT_APP_ID:-}" && -n "${WECHAT_APP_SECRET:-}" ]]; then
  MODE=local
elif [[ -n "${WENYAN_SERVER_URL:-}" && -n "${WENYAN_API_KEY:-}" ]]; then
  MODE=relay
else
  echo "ERROR: 请配置环境变量："
  echo "  本地直连：WECHAT_APP_ID + WECHAT_APP_SECRET"
  echo "  relay  ：WENYAN_SERVER_URL + WENYAN_API_KEY"
  exit 1
fi

echo ">>> 模式: $MODE  主题: $THEME"
echo ">>> 文件: $MD_FILE"
[[ -n "${WECHAT_TARGET_APP_ID:-}" ]] && echo ">>> 目标公众号: $WECHAT_TARGET_APP_ID"
echo ">>> 注意：首次运行会自动下载 @wenyan-md/cli，约需 10–30 秒..."

# ── 构建可选参数 ─────────────────────────────────────────────────────────────
EXTRA_ARGS=()
[[ -n "${WECHAT_TARGET_APP_ID:-}" ]] && EXTRA_ARGS+=(--app-id "${WECHAT_TARGET_APP_ID}")
[[ -n "${WENYAN_PROXY:-}" ]]         && EXTRA_ARGS+=(--proxy "${WENYAN_PROXY}")

if [[ "$MODE" == "relay" ]]; then
  npx --yes @wenyan-md/cli publish \
    -f "$MD_FILE" \
    -t "$THEME" \
    --server "${WENYAN_SERVER_URL}" \
    --api-key "${WENYAN_API_KEY}" \
    "${EXTRA_ARGS[@]}"
else
  npx --yes @wenyan-md/cli publish \
    -f "$MD_FILE" \
    -t "$THEME" \
    "${EXTRA_ARGS[@]}"
fi
