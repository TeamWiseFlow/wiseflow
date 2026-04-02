#!/bin/bash
# sales-cs / customer-db / db.sh
# 固定操作 workspace 下的 db/customer.db
set -euo pipefail

DB_DIR="./db"
DB_FILE="$DB_DIR/customer.db"
SCHEMA_FILE="$DB_DIR/schema.sql"
REQUIRED_TABLE="cs_record"

usage() {
  cat <<EOF
Usage: $0 <command> [args]

Commands:
  ensure              Ensure DB exists and required table is initialized
  init                Initialize DB from db/schema.sql
  tables              List all tables
  describe <table>    Show CREATE statement for a table
  schema              Show full schema (all tables)
  sql "<SQL>"         Execute SQL (SELECT/INSERT/UPDATE/DELETE only)
EOF
  exit 1
}

[ $# -lt 1 ] && usage
CMD="$1"
shift

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "❌ sqlite3 not found. Install sqlite3 first." >&2
  exit 1
fi

validate_sql() {
  local sql="$1"
  local first_word
  first_word="$(printf '%s' "$sql" | sed 's/^[[:space:]]*//' | awk '{print toupper($1)}')"

  case "$first_word" in
    SELECT|INSERT|UPDATE|DELETE|WITH|EXPLAIN)
      ;;
    *)
      echo "❌ Forbidden SQL operation: $first_word" >&2
      echo "   Only SELECT, INSERT, UPDATE, DELETE are allowed." >&2
      echo "   To change schema, contact HRBP for a formal upgrade." >&2
      exit 1
      ;;
  esac

  local upper_sql
  upper_sql="$(printf '%s' "$sql" | tr '[:lower:]' '[:upper:]')"
  for banned in 'CREATE ' 'DROP ' 'ALTER ' 'ATTACH ' 'DETACH ' 'REINDEX' 'VACUUM' 'PRAGMA'; do
    if printf '%s' "$upper_sql" | grep -q "$banned"; then
      echo "❌ SQL contains forbidden keyword: $banned" >&2
      exit 1
    fi
  done
}

ensure_db_file_and_schema() {
  if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Schema file not found: $SCHEMA_FILE" >&2
    echo "   HRBP should create db/schema.sql before running init." >&2
    exit 1
  fi
  mkdir -p "$DB_DIR"
}

has_required_table() {
  [ -f "$DB_FILE" ] || return 1
  local result
  result="$(sqlite3 "$DB_FILE" "SELECT name FROM sqlite_master WHERE type='table' AND name='$REQUIRED_TABLE';" 2>/dev/null || true)"
  [ "$result" = "$REQUIRED_TABLE" ]
}

cmd_init() {
  ensure_db_file_and_schema

  if [ -f "$DB_FILE" ] && has_required_table; then
    echo "✅ Database already initialized: $DB_FILE"
    echo "   Required table exists: $REQUIRED_TABLE"
    return 0
  fi

  if [ -f "$DB_FILE" ] && ! has_required_table; then
    echo "⚠️  Database exists but required table is missing. Re-applying schema."
  fi

  sqlite3 "$DB_FILE" < "$SCHEMA_FILE"
  echo "✅ Database initialized: $DB_FILE"
  echo "   Schema loaded from: $SCHEMA_FILE"
  cmd_tables_quiet
}

cmd_ensure() {
  ensure_db_file_and_schema
  if has_required_table; then
    echo "✅ Database ready: $DB_FILE"
    echo "   Required table exists: $REQUIRED_TABLE"
    return 0
  fi
  cmd_init
}

cmd_tables_quiet() {
  local tables
  tables="$(sqlite3 "$DB_FILE" ".tables" 2>/dev/null || true)"
  if [ -n "$tables" ]; then
    echo "   Tables: $tables"
  fi
}

ensure_db() {
  if [ ! -f "$DB_FILE" ]; then
    echo "❌ Database not found: $DB_FILE" >&2
    echo "   Run: bash ./skills/customer-db/scripts/db.sh ensure" >&2
    exit 1
  fi
}

cmd_tables() {
  ensure_db
  sqlite3 "$DB_FILE" ".tables"
}

cmd_describe() {
  [ $# -lt 1 ] && { echo "Usage: $0 describe <table>"; exit 1; }
  ensure_db
  local table="$1"
  if ! printf '%s' "$table" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*$'; then
    echo "❌ Invalid table name: $table" >&2
    exit 1
  fi
  sqlite3 "$DB_FILE" ".schema $table"
}

cmd_schema() {
  ensure_db
  sqlite3 "$DB_FILE" ".schema"
}

cmd_sql() {
  [ $# -lt 1 ] && { echo "Usage: $0 sql \"<SQL>\""; exit 1; }
  ensure_db
  local sql="$1"
  validate_sql "$sql"
  sqlite3 -header -separator $'\t' "$DB_FILE" "$sql"
}

case "$CMD" in
  ensure)   cmd_ensure ;;
  init)     cmd_init ;;
  tables)   cmd_tables ;;
  describe) cmd_describe "$@" ;;
  schema)   cmd_schema ;;
  sql)      cmd_sql "$@" ;;
  *)        echo "❌ Unknown command: $CMD" >&2; usage ;;
esac
