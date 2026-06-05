#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DB="$ROOT/db/published_track.db"

if [ ! -f "$DB" ]; then
  echo '{"exists":false}'
  exit 0
fi

PLATFORM="" SOURCE_FOLDER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)       PLATFORM="$2"; shift 2 ;;
    --source-folder)  SOURCE_FOLDER="$2"; shift 2 ;;
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

ROW=$(sqlite3 "$DB" "SELECT id,publish_url FROM $TABLE WHERE source_folder='${SOURCE_FOLDER//\'/\'\'}';")
if [ -z "$ROW" ]; then
  echo '{"exists":false}'
else
  ID=$(echo "$ROW" | cut -d'|' -f1)
  URL=$(echo "$ROW" | cut -d'|' -f2)
  echo "{\"exists\":true,\"id\":$ID,\"publish_url\":\"$URL\"}"
fi
