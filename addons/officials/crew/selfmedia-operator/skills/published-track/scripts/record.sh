#!/usr/bin/env bash
# record.sh — 发布记录统一入口（已合并 score-and-record.sh）
#
# 行为：
#   - 提供任意 --cal-* 分数 → 自动置 cal_enabled=1，算 composite，记 rubric_version
#   - 不提供分数        → cal_enabled=0（不参与复盘）
#   - 显式 --cal-enabled 0/1 → 覆盖上述自动判定
#
# 打分由 Agent（blind sub-agent）对照 rubric 完成后，把 7 维分随本调用传入；
# 本脚本只做范围校验、composite 计算、DB 写入。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
CAL_ROOT="$ROOT/calibration"
DB="$ROOT/db/published_track.db"

# Self-heal stale schema: if a platform table is missing, run idempotent init-db.sh
ensure_platform_table() {
  local table="pub_$1" found
  found=$(sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name='$table';")
  if [ -z "$found" ]; then
    bash "$(dirname "$0")/init-db.sh" >/dev/null 2>&1 || true
    found=$(sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name='$table';")
  fi
  [ -n "$found" ]
}

if [ ! -f "$DB" ]; then
  bash "$(dirname "$0")/init-db.sh"
fi

# Parse args
PLATFORM="" TITLE="" CONTENT_TYPE="" SOURCE_FOLDER="" PUBLISH_URL="" PUBLISH_DATE="" NOTES=""
DISTRIBUTE_STATUS=""
CAL_ENABLED_EXPLICIT=""   # 仅当用户显式传 --cal-enabled 时非空
CAL_ER="" CAL_HP="" CAL_SR="" CAL_QL="" CAL_NA="" CAL_AB="" CAL_PV="" CAL_COMPOSITE="" CAL_RUBRIC_VERSION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)            PLATFORM="$2"; shift 2 ;;
    --title)               TITLE="$2"; shift 2 ;;
    --content-type)        CONTENT_TYPE="$2"; shift 2 ;;
    --source-folder)       SOURCE_FOLDER="$2"; shift 2 ;;
    --publish-url)         PUBLISH_URL="$2"; shift 2 ;;
    # ⚠️ 发布日期就是当天时不要传此参数，让脚本默认今天。
    # ❌ 不要用 --publish-date "$(date +%Y-%m-%d)" —— exec 沙箱不展开 $()。
    --publish-date)        PUBLISH_DATE="$2"; shift 2 ;;
    --notes)               NOTES="$2"; shift 2 ;;
    --distribute-status)   DISTRIBUTE_STATUS="$2"; shift 2 ;;
    --cal-enabled)         CAL_ENABLED_EXPLICIT="$2"; shift 2 ;;
    --cal-er)              CAL_ER="$2"; shift 2 ;;
    --cal-hp)              CAL_HP="$2"; shift 2 ;;
    --cal-sr)              CAL_SR="$2"; shift 2 ;;
    --cal-ql)              CAL_QL="$2"; shift 2 ;;
    --cal-na)              CAL_NA="$2"; shift 2 ;;
    --cal-ab)              CAL_AB="$2"; shift 2 ;;
    --cal-pv)              CAL_PV="$2"; shift 2 ;;
    --cal-composite)       CAL_COMPOSITE="$2"; shift 2 ;;
    --cal-rubric-version)  CAL_RUBRIC_VERSION="$2"; shift 2 ;;
    *) echo "{\"ok\":false,\"error\":\"unknown arg: $1\"}"; exit 1 ;;
  esac
done

# Default publish_date to today（防御 exec 沙箱不展开 $() 的脏数据）
if [ -z "$PUBLISH_DATE" ]; then
  PUBLISH_DATE="$(date +%Y-%m-%d)"
elif [[ "$PUBLISH_DATE" =~ ^\$\(*date* || "$PUBLISH_DATE" =~ ^\`*date* ]]; then
  echo "{\"ok\":false,\"error\":\"--publish-date looks unexpanded: '$PUBLISH_DATE'. omit --publish-date for today, or pass literal like 2026-06-14.\"}" >&2
  PUBLISH_DATE="$(date +%Y-%m-%d)"
fi

if [ -z "$PLATFORM" ] || [ -z "$TITLE" ] || [ -z "$CONTENT_TYPE" ] || [ -z "$SOURCE_FOLDER" ]; then
  echo '{"ok":false,"error":"missing required args: --platform, --title, --content-type, --source-folder"}'
  exit 1
fi

TABLE="pub_${PLATFORM}"
if ! ensure_platform_table "$PLATFORM"; then
  echo "{\"ok\":false,\"error\":\"unknown platform: $PLATFORM (table $TABLE not found)\"}"
  exit 1
fi

case "$CONTENT_TYPE" in
  article|video|post) ;;
  *) echo "{\"ok\":false,\"error\":\"invalid content_type: $CONTENT_TYPE (must be article/video/post)\"}"; exit 1 ;;
esac

# ── 是否提供了打分 ──
HAS_SCORES=0
for dim in ER HP SR QL NA AB PV; do
  var_name="CAL_$dim"
  if [[ -n "${!var_name}" ]]; then HAS_SCORES=1; break; fi
done

# ── 判定 cal_enabled ──
if [[ -n "$CAL_ENABLED_EXPLICIT" ]]; then
  CAL_ENABLED="$CAL_ENABLED_EXPLICIT"
else
  if [[ "$HAS_SCORES" -eq 1 ]]; then CAL_ENABLED=1; else CAL_ENABLED=0; fi
fi

# ── 有分数时：校验范围、算 composite、补 rubric_version ──
if [[ "$HAS_SCORES" -eq 1 ]]; then
  for dim in ER HP SR QL NA AB PV; do
    var_name="CAL_$dim"; val="${!var_name}"
    if [[ -n "$val" ]]; then
      if [[ "$val" -lt 0 || "$val" -gt 5 ]] 2>/dev/null; then
        echo "{\"ok\":false,\"error\":\"cal_score_$dim=$val out of range (must be 0-5 integer)\"}"; exit 1
      fi
    fi
  done

  if [[ -z "$CAL_COMPOSITE" ]]; then
    er="${CAL_ER:-0}" hp="${CAL_HP:-0}" sr="${CAL_SR:-0}"
    ql="${CAL_QL:-0}" na="${CAL_NA:-0}" ab="${CAL_AB:-0}" pv="${CAL_PV:-0}"
    CAL_COMPOSITE=$(python3 -c "
er=$er; hp=$hp; sr=$sr; ql=$ql; na=$na; ab=$ab; pv=$pv
print(f'{(er*1.5 + hp*1.5 + sr*1.5 + ql + na + ab + pv) / 8.5 * 2.0:.2f}')
")
  fi

  if [[ -z "$CAL_RUBRIC_VERSION" ]]; then
    CAL_DIR="$CAL_ROOT/$PLATFORM"
    if [[ -d "$CAL_DIR" && -f "$CAL_DIR/.cheat-state.json" ]]; then
      CAL_RUBRIC_VERSION=$(python3 -c "import json; print(json.load(open('$CAL_DIR/.cheat-state.json')).get('rubric_version','v0'))" 2>/dev/null || echo "v0")
    else
      CAL_RUBRIC_VERSION="v0"
    fi
  fi

  echo "📊 打分 — $PLATFORM  ER=${CAL_ER:-0} HP=${CAL_HP:-0} SR=${CAL_SR:-0} QL=${CAL_QL:-0} NA=${CAL_NA:-0} AB=${CAL_AB:-0} PV=${CAL_PV:-0}  composite=$CAL_COMPOSITE (rubric $CAL_RUBRIC_VERSION)" >&2
fi

# ── 构建 cal_ 列 ──
cal_cols=""; cal_vals=""

if [[ -n "$CAL_ENABLED" ]]; then
  cal_cols="cal_enabled"; cal_vals="$CAL_ENABLED"
fi

for dim in er hp sr ql na ab pv; do
  var_name="CAL_$(echo $dim | tr '[:lower:]' '[:upper:]')"; val="${!var_name}"
  if [[ -n "$val" ]]; then
    if [[ -n "$cal_cols" ]]; then cal_cols="$cal_cols,cal_score_$dim"; cal_vals="$cal_vals,$val"
    else cal_cols="cal_score_$dim"; cal_vals="$val"; fi
  fi
done

if [[ -n "$CAL_COMPOSITE" ]]; then
  if [[ -n "$cal_cols" ]]; then cal_cols="$cal_cols,cal_composite"; cal_vals="$cal_vals,$CAL_COMPOSITE"
  else cal_cols="cal_composite"; cal_vals="$CAL_COMPOSITE"; fi
fi

if [[ -n "$CAL_RUBRIC_VERSION" ]]; then
  esc_rv="${CAL_RUBRIC_VERSION//\'/\'\'}"
  if [[ -n "$cal_cols" ]]; then cal_cols="$cal_cols,cal_rubric_version"; cal_vals="$cal_vals,'$esc_rv'"
  else cal_cols="cal_rubric_version"; cal_vals="'$esc_rv'"; fi
fi

if [[ -n "$cal_cols" ]]; then
  cal_cols="$cal_cols,cal_scored_at"
  scored_at="$(strftime '%Y-%m-%d %H:%M:%S' 2>/dev/null || date '+%Y-%m-%d %H:%M:%S')"
  cal_vals="$cal_vals,'$scored_at'"
fi

# ── distribute_status ──
DS_VAL=0
if [[ -n "$DISTRIBUTE_STATUS" ]]; then
  case "$DISTRIBUTE_STATUS" in
    0|1|2) DS_VAL="$DISTRIBUTE_STATUS" ;;
    *) echo '{"ok":false,"error":"--distribute-status must be 0(pending), 1(no_distribution), or 2(distributed)"}'; exit 1 ;;
  esac
fi

ESC_TITLE="${TITLE//\'/\'\'}"
ESC_FOLDER="${SOURCE_FOLDER//\'/\'\'}"
ESC_URL="${PUBLISH_URL//\'/\'\'}"
ESC_NOTES="${NOTES//\'/\'\'}"

BASE_COLS="title,content_type,source_folder,publish_url,publish_date,distribute_status,notes"
BASE_VALS="'$ESC_TITLE','$CONTENT_TYPE','$ESC_FOLDER','$ESC_URL','$PUBLISH_DATE',$DS_VAL,'$ESC_NOTES'"

if [[ -n "$cal_cols" ]]; then
  ALL_COLS="$BASE_COLS,$cal_cols"; ALL_VALS="$BASE_VALS,$cal_vals"
else
  ALL_COLS="$BASE_COLS"; ALL_VALS="$BASE_VALS"
fi

sqlite3 "$DB" "INSERT INTO $TABLE ($ALL_COLS) VALUES ($ALL_VALS);"
ID=$(sqlite3 "$DB" "SELECT last_insert_rowid();")
echo "{\"ok\":true,\"action\":\"inserted\",\"id\":$ID,\"table\":\"$TABLE\",\"distribute_status\":$DS_VAL,\"cal_enabled\":${CAL_ENABLED:-0}}"
