#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DB="$ROOT/db/published_track.db"

if [ ! -f "$DB" ]; then
  echo '{"ok":false,"error":"database not initialized, run init-db.sh first"}'
  exit 1
fi

# Parse args
PLATFORM="" SOURCE_FOLDER=""
declare -A METRICS

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)       PLATFORM="$2"; shift 2 ;;
    --source-folder)  SOURCE_FOLDER="$2"; shift 2 ;;
    --*=*)
      KEY="${1#--}"
      VAL="${1#*=}"
      METRICS["$KEY"]="$VAL"
      shift
      ;;
    --*)
      KEY="${1#--}"
      VAL="$2"
      METRICS["$KEY"]="$VAL"
      shift 2
      ;;
    *) echo "{\"ok\":false,\"error\":\"unknown arg: $1\"}"; exit 1 ;;
  esac
done

if [ -z "$PLATFORM" ] || [ -z "$SOURCE_FOLDER" ]; then
  echo '{"ok":false,"error":"missing required args: --platform, --source-folder"}'
  exit 1
fi

TABLE="pub_${PLATFORM}"
VALID=$(sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name='$TABLE';")
if [ -z "$VALID" ]; then
  echo "{\"ok\":false,\"error\":\"unknown platform: $PLATFORM\"}"
  exit 1
fi

# Check record exists
EXISTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM $TABLE WHERE source_folder='${SOURCE_FOLDER//\'/\'\'}';")
if [ "$EXISTS" -eq 0 ]; then
  echo "{\"ok\":false,\"error\":\"no record found in $TABLE for source_folder=$SOURCE_FOLDER\"}"
  exit 1
fi

# Get valid columns for this table (exclude id, created_at)
COLS=$(sqlite3 "$DB" "PRAGMA table_info($TABLE);" | awk -F'|' '{print $2}' | grep -v -E '^(id|created_at|source_folder|content_type|title|publish_date)$' | tr '\n' ' ')

# Build SET clause
SET_PARTS=()
for KEY in "${!METRICS[@]}"; do
  # Validate column exists
  if ! echo " $COLS " | grep -q " $KEY "; then
    echo "{\"ok\":false,\"error\":\"column '$KEY' not found in $TABLE. Valid metric columns: $COLS\"}"
    exit 1
  fi
  VAL="${METRICS[$KEY]}"
  # Only allow integer or text values
  ESC_VAL="${VAL//\'/\'\'}"
  SET_PARTS+=("$KEY='$ESC_VAL'")
done

if [ ${#SET_PARTS[@]} -eq 0 ]; then
  echo '{"ok":false,"error":"no metrics provided to update"}'
  exit 1
fi

# Always update updated_at
SET_PARTS+=("updated_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime')")

SET_CLAUSE=$(IFS=','; echo "${SET_PARTS[*]}")

sqlite3 "$DB" "UPDATE $TABLE SET $SET_CLAUSE WHERE source_folder='${SOURCE_FOLDER//\'/\'\'}';"

echo "{\"ok\":true,\"table\":\"$TABLE\",\"source_folder\":\"$SOURCE_FOLDER\",\"updated_columns\":${#METRICS[@]}}"
