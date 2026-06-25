#!/usr/bin/env bash
# build-calibration-pool.sh — 从 published-track DB 构建指定平台的校准池
# 用法: build-calibration-pool.sh --platform <platform_id>
# 输出该平台有互动数据的发布记录，供复盘和 bump 使用
set -euo pipefail

WORKSPACE="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../../.." &> /dev/null && pwd )"
DB="$WORKSPACE/db/published_track.db"
CAL_ROOT="$WORKSPACE/calibration"

PLATFORM=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

if [[ -z "$PLATFORM" ]]; then
  echo "用法: build-calibration-pool.sh --platform <platform_id>"
  echo "  platform: wx_mp | xhs | zhihu | bilibili | douyin | kuaishou | toutiao | youtube"
  exit 1
fi

CAL_DIR="$CAL_ROOT/$PLATFORM"
if [[ ! -d "$CAL_DIR" ]]; then
  echo "❌ 平台 $PLATFORM 的校准目录不存在: $CAL_DIR"
  echo "   先运行 init.sh --platform $PLATFORM"
  exit 1
fi

if [[ ! -f "$DB" ]]; then
  echo "❌ published-track DB 不存在: $DB"
  exit 1
fi

TABLE="pub_${PLATFORM}"

# 检查表是否存在
table_exists=$(sqlite3 "$DB" "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='$TABLE';")
if [[ "$table_exists" -eq 0 ]]; then
  echo "❌ 平台表不存在: $TABLE"
  exit 1
fi

# 平台 → 主指标字段映射
declare -A METRIC_FIELD
METRIC_FIELD[wx_mp]="reads"
METRIC_FIELD[xhs]="views"
METRIC_FIELD[zhihu]="views"
METRIC_FIELD[bilibili]="plays"
METRIC_FIELD[douyin]="plays"
METRIC_FIELD[kuaishou]="plays"
METRIC_FIELD[toutiao]="reads"
METRIC_FIELD[youtube]="views"

METRIC="${METRIC_FIELD[$PLATFORM]:-views}"

echo "📊 从 published_track.$TABLE 构建校准池（主指标: $METRIC）..."
echo ""

# 查询该平台有互动数据的记录
sqlite3 -separator "|" "$DB" "
SELECT title, source_folder, publish_date,
       COALESCE($METRIC, 0) as metric
FROM $TABLE WHERE $METRIC > 0
ORDER BY publish_date DESC;
" 2>/dev/null | while IFS='|' read -r title folder date metric; do
  echo "$title | $folder | $date | $metric"
done

count=$(sqlite3 "$DB" "SELECT count(*) FROM $TABLE WHERE $METRIC > 0;" 2>/dev/null || echo "0")

echo ""
echo "---"
echo "平台: $PLATFORM | 总计: $count 条有互动数据的记录"
