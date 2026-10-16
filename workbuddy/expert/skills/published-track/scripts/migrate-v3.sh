#!/usr/bin/env bash
# migrate-v3.sh — 迁移到 v3 schema：数据直连 DNA
#   1. 为所有 pub_* 表添加 dna_id TEXT（作品 ↔ DNA 关联；NULL = 未归属/历史作品）
#   2. 为所有 pub_* 表添加 account TEXT（发布账号 alias；DNA 评估按账号基线归一化用）
#   3. 为所有 pub_* 表添加 perf_evaluated INTEGER DEFAULT 0（是否已被 DNA 表现评估覆盖）
#   cal_* 列保留做历史兼容，停止写入。幂等可重复执行。
set -euo pipefail

ROOT="${XIAOBEI_WORKSPACE:?WorkBuddy workspace required}"
DB="$ROOT/db/published_track.db"

if [ ! -f "$DB" ]; then
  echo '{"ok":false,"error":"database not found, run init-db.sh first"}'
  exit 1
fi

echo "🔄 迁移 published_track.db → v3 schema（dna_id / account / perf_evaluated）..."

TABLES=$(sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'pub_%';")

add_col() {
  local table="$1" col="$2" decl="$3"
  local has
  has=$(sqlite3 "$DB" "SELECT count(*) FROM pragma_table_info('$table') WHERE name='$col';")
  if [ "$has" = "0" ]; then
    sqlite3 "$DB" "ALTER TABLE $table ADD COLUMN $decl;"
    echo "    + $col"
  fi
}

for TABLE in $TABLES; do
  echo "  处理 $TABLE ..."
  add_col "$TABLE" dna_id "dna_id TEXT"
  add_col "$TABLE" account "account TEXT"
  add_col "$TABLE" perf_evaluated "perf_evaluated INTEGER DEFAULT 0"
done

echo '{"ok":true,"message":"v3 migration done: dna_id + account + perf_evaluated"}'
