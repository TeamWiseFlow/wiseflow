#!/usr/bin/env bash
# cal-toggle.sh — 管理平台 content-calibrator 打分开关与阈值
#
# 用法:
#   cal-toggle.sh --list                              # 查看所有平台打分开关状态
#   cal-toggle.sh --platform <platform> --enable      # 启用某平台打分
#   cal-toggle.sh --platform <platform> --disable     # 停用某平台打分
#   cal-toggle.sh --platform <platform> --status      # 查看某平台打分状态
#   cal-toggle.sh --platform <platform> --threshold   # 查看某平台打分阈值
#   cal-toggle.sh --platform <platform> --set-threshold <N>  # 设置阈值（每维 0-5，需 >N 才放行发布；0=不拦截）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CAL_ROOT="$ROOT/calibration"
DB="$ROOT/db/published_track.db"

ACTION="" PLATFORM="" THRESHOLD_VAL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    --enable)   ACTION=enable; shift ;;
    --disable)  ACTION=disable; shift ;;
    --status)   ACTION=status; shift ;;
    --list)     ACTION=list; shift ;;
    --threshold)      ACTION=threshold; shift ;;
    --set-threshold)  ACTION=set_threshold; THRESHOLD_VAL="$2"; shift 2 ;;
    *) echo "{\"ok\":false,\"error\":\"unknown arg: $1\"}"; exit 1 ;;
  esac
done

# 支持的平台
VALID_PLATFORMS="wx_mp wx_channel xhs zhihu bilibili douyin kuaishou toutiao youtube juejin twitter facebook instagram tiktok pinterest threads"

if [ "$ACTION" = "list" ]; then
  echo "📊 Content-Calibrator 平台打分开关"
  echo ""
  for p in $VALID_PLATFORMS; do
    CAL_DIR="$CAL_ROOT/$p"
    if [ -d "$CAL_DIR" ] && [ -f "$CAL_DIR/.cheat-state.json" ]; then
      thr=$(python3 -c "import json; print(json.load(open('$CAL_DIR/.cheat-state.json')).get('score_threshold',0))" 2>/dev/null || echo 0)
      echo "  ✅ $p — 已启用（阈值 >$thr 放行）"
    else
      echo "  ⬜ $p — 未启用"
    fi
  done
  exit 0
fi

if [ -z "$PLATFORM" ]; then
  echo '{"ok":false,"error":"--platform is required (or use --list)"}'
  exit 1
fi

if ! echo "$VALID_PLATFORMS" | grep -qw "$PLATFORM"; then
  echo "{\"ok\":false,\"error\":\"unsupported platform: $PLATFORM\"}"
  exit 1
fi

CAL_DIR="$CAL_ROOT/$PLATFORM"

case "$ACTION" in
  status)
    if [ -d "$CAL_DIR" ] && [ -f "$CAL_DIR/.cheat-state.json" ]; then
      echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"cal_enabled\":true}"
    else
      echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"cal_enabled\":false}"
    fi
    ;;
  threshold)
    if [ ! -f "$CAL_DIR/.cheat-state.json" ]; then
      echo "{\"ok\":false,\"error\":\"platform $PLATFORM not initialized (no .cheat-state.json)\"}"; exit 1
    fi
    thr=$(python3 -c "import json; print(json.load(open('$CAL_DIR/.cheat-state.json')).get('score_threshold',0))")
    echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"score_threshold\":$thr,\"meaning\":\"每维需 >$thr 才放行发布\"}"
    ;;
  set_threshold)
    if [ ! -f "$CAL_DIR/.cheat-state.json" ]; then
      echo "{\"ok\":false,\"error\":\"platform $PLATFORM not initialized (no .cheat-state.json)\"}"; exit 1
    fi
    if [[ -z "$THRESHOLD_VAL" ]]; then
      echo '{"ok":false,"error":"--set-threshold requires a value 0-4"}'; exit 1
    fi
    if [[ "$THRESHOLD_VAL" -lt 0 || "$THRESHOLD_VAL" -gt 4 ]] 2>/dev/null; then
      echo "{\"ok\":false,\"error\":\"threshold must be integer 0-4 (每维 0-5, 需 >threshold, 故 threshold 上限 4)\"}"; exit 1
    fi
    python3 -c "
import json
f='$CAL_DIR/.cheat-state.json'
d=json.load(open(f)); d['score_threshold']=$THRESHOLD_VAL
json.dump(d,open(f,'w'),ensure_ascii=False,indent=2)
"
    echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"score_threshold\":$THRESHOLD_VAL,\"meaning\":\"每维需 >$THRESHOLD_VAL 才放行发布\"}"
    ;;
  enable)
    if [ -d "$CAL_DIR" ] && [ -f "$CAL_DIR/.cheat-state.json" ]; then
      echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"action\":\"enable\",\"message\":\"already enabled\"}"
    else
      # 调 content-calibrator 的 init.sh
      bash "$(dirname "$0")/../../content-calibrator/scripts/init.sh" --platform "$PLATFORM"
      echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"action\":\"enable\",\"message\":\"calibration initialized\"}"
    fi
    ;;
  disable)
    if [ ! -d "$CAL_DIR" ]; then
      echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"action\":\"disable\",\"message\":\"already disabled (dir not found)\"}"
    else
      echo "⚠️  禁用 $PLATFORM 的 content-calibrator 将删除 calibration/$PLATFORM/ 目录"
      echo "   rubric、预测日志、对标数据等将全部删除"
      echo "   确认请输入 YES: "
      read -r CONFIRM
      if [ "$CONFIRM" = "YES" ]; then
        rm -rf "$CAL_DIR"
        echo "{\"ok\":true,\"platform\":\"$PLATFORM\",\"action\":\"disable\",\"message\":\"calibration directory removed\"}"
      else
        echo "{\"ok\":false,\"platform\":\"$PLATFORM\",\"action\":\"disable\",\"message\":\"cancelled by user\"}"
      fi
    fi
    ;;
  *)
    echo '{"ok":false,"error":"action required: --enable, --disable, --status, --threshold, --set-threshold, or --list"}'
    exit 1
    ;;
esac
