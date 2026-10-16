#!/usr/bin/env bash
# record.sh — 发布记录统一入口
#
# DNA 关联：优先取 --dna-id 入参；未传时自动读 <source-folder>/dna-meta.json
#   （内容生产环节落盘，形如 {"platform":"wx_mp","dna_id":"dna-0"}）。
#   两者都缺时 dna_id 留 NULL（历史补录/未归属作品），不报错。
#   account 传发布时所用账号 alias（如 wx_mp accounts.json 的 alias），缺省 NULL。
#
# ── 落库语义：upsert（同一篇文章 + 同一平台 + 同一发布日 → 更新，不重复插行）──
# 去重键：(source_folder, publish_date)。同 work 同平台同天重跑（重发/record 重调）
# 覆盖旧行，避免僵尸行；不同 publish_date（真正的再发布/补发历史）仍新建行。
# 这只管 DB 层去重——公众号后台是否堆积草稿由 wx-mp-publisher 自身幂等性决定，本脚本管不到。
#
# 历史兼容：cal_* 列保留但不再写入。
set -euo pipefail

ROOT="${XIAOBEI_WORKSPACE:?WorkBuddy workspace required}"
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

# Self-heal v3 columns on existing DBs (idempotent)
ensure_v3_columns() {
  local table="pub_$1"
  for spec in "dna_id:dna_id TEXT" "account:account TEXT" "perf_evaluated:perf_evaluated INTEGER DEFAULT 0"; do
    local col="${spec%%:*}" decl="${spec#*:}" has
    has=$(sqlite3 "$DB" "SELECT count(*) FROM pragma_table_info('$table') WHERE name='$col';")
    if [ "$has" = "0" ]; then
      sqlite3 "$DB" "ALTER TABLE $table ADD COLUMN $decl;"
    fi
  done
}

# --help/-h is a usage probe; honor it before the DB check so it works without a DB.
for arg in "$@"; do
  if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
    cat <<'EOF'
用法: record.sh --platform <name> --title <text> --content-type <article|video|post> --source-folder <folder> [可选参数...]

发布记录入库（upsert 到 pub_<platform>）。去重键 (source_folder, publish_date)：
同作品同平台同天重跑 → 更新原行不重复插行；不同 publish_date（补发/再发布）→ 新建行。

必填:
  --platform <name>        平台表后缀（落 pub_<name>，如 xhs / wx_channel / douyin）。
  --title <text>           标题。⚠️ wx_channel 必须传完整视频描述（含 hashtag，约 300 字），
                           不是短标题——engagement 抓取按它匹配后台作品；短标题不入库。
  --content-type <type>    article | video | post。
  --source-folder <folder> 作品目录（绝对路径，或相对 workspace 根）。目录内有
                           dna-meta.json 且未传 --dna-id 时自动从中读 dna_id。

可选:
  --publish-url <url>      公开链接（如 https://weixin.qq.com/sph/xxx）。发布时没拿到的，
                           后续用相同 --source-folder 重跑本命令补传（upsert 更新原行）。
  --publish-date <YYYY-MM-DD>  缺省为今天。当天发布不要传此参数；
                           ❌ 禁止传 "$(date +%Y-%m-%d)"——exec 沙箱不展开 $()。
  --notes <text>           备注。
  --distribute-status <n>  0=待分发（默认）| 1=不分发 | 2=已分发。
  --dna-id <id>            显式指定 DNA id，优先于 dna-meta.json 自动读取。
  --account <alias>        发布所用账号 alias（如 wx_mp accounts.json 的 alias）。

示例:
  record.sh --platform wx_channel --title "完整视频描述... #话题" --content-type video \
    --source-folder wx_channel/outputs/my-video/ --account xiaobei
  record.sh --platform xhs --title "标题" --content-type post --source-folder xhs/outputs/abc/ \
    --publish-url "https://www.xiaohongshu.com/..."

输出: stdout JSON。成功 {"ok":true,"action":"inserted|updated",...}，失败 {"ok":false,"error":...}。
EOF
    exit 0
  fi
done

if [ ! -f "$DB" ]; then
  bash "$(dirname "$0")/init-db.sh"
fi

# Parse args
PLATFORM="" TITLE="" CONTENT_TYPE="" SOURCE_FOLDER="" PUBLISH_URL="" PUBLISH_DATE="" NOTES=""
DISTRIBUTE_STATUS="" DNA_ID="" ACCOUNT=""

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
    --dna-id)              DNA_ID="$2"; shift 2 ;;
    --account)             ACCOUNT="$2"; shift 2 ;;
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
ensure_v3_columns "$PLATFORM"

case "$CONTENT_TYPE" in
  article|video|post) ;;
  *) echo "{\"ok\":false,\"error\":\"invalid content_type: $CONTENT_TYPE (must be article/video/post)\"}"; exit 1 ;;
esac

# ── 解析 work 绝对路径并读取 dna-meta.json（--dna-id 未传时）──
if [[ "$SOURCE_FOLDER" = /* ]]; then WORK_ABS="$SOURCE_FOLDER"; else WORK_ABS="$ROOT/$SOURCE_FOLDER"; fi

if [[ -z "$DNA_ID" && -f "$WORK_ABS/dna-meta.json" ]]; then
  DNA_ID=$(python3 -c "
import json,sys
try:
    d=json.load(open('$WORK_ABS/dna-meta.json'))
    print(d.get('dna_id') or '')
except Exception:
    print('')
")
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
ESC_DNA="${DNA_ID//\'/\'\'}"
ESC_ACCOUNT="${ACCOUNT//\'/\'\'}"

BASE_COLS="title,content_type,source_folder,publish_url,publish_date,distribute_status,notes"
BASE_VALS="'$ESC_TITLE','$CONTENT_TYPE','$ESC_FOLDER','$ESC_URL','$PUBLISH_DATE',$DS_VAL,'$ESC_NOTES'"

if [[ -n "$DNA_ID" ]]; then
  BASE_COLS="$BASE_COLS,dna_id"; BASE_VALS="$BASE_VALS,'$ESC_DNA'"
fi
if [[ -n "$ACCOUNT" ]]; then
  BASE_COLS="$BASE_COLS,account"; BASE_VALS="$BASE_VALS,'$ESC_ACCOUNT'"
fi

# ── upsert：同 (source_folder, publish_date) 存在则 UPDATE，否则 INSERT ──
EXISTING_ID=$(sqlite3 "$DB" "SELECT id FROM $TABLE WHERE source_folder='$ESC_FOLDER' AND publish_date='$PUBLISH_DATE' LIMIT 1;")

if [[ -n "$EXISTING_ID" ]]; then
  SET_CLAUSE="title='$ESC_TITLE',content_type='$CONTENT_TYPE',source_folder='$ESC_FOLDER',publish_url='$ESC_URL',publish_date='$PUBLISH_DATE',distribute_status=$DS_VAL,notes='$ESC_NOTES'"
  if [[ -n "$DNA_ID" ]]; then SET_CLAUSE="$SET_CLAUSE,dna_id='$ESC_DNA'"; fi
  if [[ -n "$ACCOUNT" ]]; then SET_CLAUSE="$SET_CLAUSE,account='$ESC_ACCOUNT'"; fi
  SET_CLAUSE="$SET_CLAUSE,updated_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime')"
  sqlite3 "$DB" "UPDATE $TABLE SET $SET_CLAUSE WHERE id=$EXISTING_ID;"
  echo "{\"ok\":true,\"action\":\"updated\",\"id\":$EXISTING_ID,\"table\":\"$TABLE\",\"distribute_status\":$DS_VAL,\"dna_id\":\"$DNA_ID\",\"account\":\"$ACCOUNT\"}"
else
  ID=$(sqlite3 "$DB" "INSERT INTO $TABLE ($BASE_COLS) VALUES ($BASE_VALS); SELECT last_insert_rowid();")
  echo "{\"ok\":true,\"action\":\"inserted\",\"id\":$ID,\"table\":\"$TABLE\",\"distribute_status\":$DS_VAL,\"dna_id\":\"$DNA_ID\",\"account\":\"$ACCOUNT\"}"
fi
