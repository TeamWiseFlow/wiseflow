#!/usr/bin/env bash
# content-calibrator init — 为指定平台创建校准系统目录和初始文件
# 用法: init.sh --platform <platform_id>
#   platform_id: wx_mp | xhs | zhihu | bilibili | douyin | kuaishou | toutiao | youtube
set -euo pipefail

WORKSPACE="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../../.." &> /dev/null && pwd )"
CAL_ROOT="$WORKSPACE/calibration"

PLATFORM=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

# 支持的平台列表
VALID_PLATFORMS="wx_mp wx_channel xhs zhihu bilibili douyin kuaishou toutiao youtube"

if [[ -z "$PLATFORM" ]]; then
  echo "用法: init.sh --platform <platform_id>"
  echo ""
  echo "支持的平台:"
  echo "  wx_mp       微信公众号"
  echo "  wx_channel  微信视频号"
  echo "  xhs         小红书"
  echo "  zhihu       知乎"
  echo "  bilibili    B站"
  echo "  douyin      抖音"
  echo "  kuaishou    快手"
  echo "  toutiao     今日头条"
  echo "  youtube     YouTube"
  exit 1
fi

if ! echo "$VALID_PLATFORMS" | grep -qw "$PLATFORM"; then
  echo "❌ 不支持的平台: $PLATFORM"
  echo "   支持的平台: $VALID_PLATFORMS"
  exit 1
fi

CAL_DIR="$CAL_ROOT/$PLATFORM"

echo "🔧 初始化 Content Calibrator — $PLATFORM"
echo "   工作区: $WORKSPACE"
echo "   校准目录: $CAL_DIR"
echo ""

# 创建目录结构
mkdir -p "$CAL_DIR/predictions"

# 检查已有文件
files=(rubric_notes.md rubric-memo.md .cheat-state.json benchmark.md audience.md)
existing=0
for f in "${files[@]}"; do
  if [[ -f "$CAL_DIR/$f" ]]; then
    existing=$((existing + 1))
  fi
done

if [[ $existing -eq ${#files[@]} ]]; then
  echo "✅ 平台 $PLATFORM 的校准系统已初始化（所有文件均存在）"
  echo ""
  echo "当前状态:"
  mode=$(python3 -c "import json; print(json.load(open('$CAL_DIR/.cheat-state.json'))['mode'])" 2>/dev/null || echo "unknown")
  samples=$(python3 -c "import json; print(json.load(open('$CAL_DIR/.cheat-state.json'))['calibration_samples'])" 2>/dev/null || echo "0")
  version=$(python3 -c "import json; print(json.load(open('$CAL_DIR/.cheat-state.json'))['rubric_version'])" 2>/dev/null || echo "unknown")
  echo "  模式: $mode"
  echo "  Rubric: $version"
  echo "  校准样本: $samples"
  exit 0
fi

if [[ $existing -gt 0 ]]; then
  echo "⚠️  校准目录已存在部分文件（$existing/${#files[@]}），跳过已存在文件。"
fi

# 创建不存在的文件
for f in "${files[@]}"; do
  if [[ ! -f "$CAL_DIR/$f" ]]; then
    echo "  创建 $f"
  fi
done

echo ""
echo "✅ 初始化完成 — 平台: $PLATFORM"
echo ""
echo "下一步:"
echo "  1. 对已有发布内容做首次复盘 → 积累校准样本"
echo "  2. 导入对标账号 → 获取初始 rubric 信号"
echo "  3. 对新稿子打分 → 开始校准循环"
echo ""
echo "其他平台初始化:"
echo "  ./skills/content-calibrator/scripts/init.sh --platform <另一个平台>"
