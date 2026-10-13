#!/usr/bin/env bash
# update-application.sh — Update an application's status and optionally notes/result
# Usage: update-application.sh --id <申报ID> --status <新状态> [--notes <备注>] [--result <结果>]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="${XIAOBEI_WORKSPACE:?WorkBuddy workspace required}"
DB_FILE="$WORKSPACE_DIR/db/ir_record.db"

ID=""
STATUS=""
NOTES=""
RESULT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --id)      ID="$2"; shift 2 ;;
    --status)  STATUS="$2"; shift 2 ;;
    --notes)   NOTES="$2"; shift 2 ;;
    --result)  RESULT="$2"; shift 2 ;;
    *) echo '{"ok": false, "error": "Unknown argument: '"$1"'"}' ; exit 1 ;;
  esac
done

if [[ -z "$ID" || -z "$STATUS" ]]; then
  echo '{"ok": false, "error": "--id and --status are required"}'
  exit 1
fi

if [[ ! -f "$DB_FILE" ]]; then
  echo '{"ok": false, "error": "Database not initialized. Run init-db.sh first."}'
  exit 1
fi

ST_ESC="${STATUS//\'/\'\'}"
NT_ESC="${NOTES//\'/\'\'}"
RS_ESC="${RESULT//\'/\'\'}"

SETS="status='$ST_ESC'"
if [[ -n "$NOTES" ]]; then SETS="$SETS, notes='$NT_ESC'"; fi
if [[ -n "$RESULT" ]]; then SETS="$SETS, result='$RS_ESC'"; fi
SETS="$SETS, updated_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime')"

sqlite3 "$DB_FILE" "UPDATE applications SET $SETS WHERE id=$ID;"

echo '{"ok": true}'
