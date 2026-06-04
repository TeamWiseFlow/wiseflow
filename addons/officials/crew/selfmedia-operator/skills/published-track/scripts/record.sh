#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
DB="$ROOT/db/published_track.db"

# Ensure db exists
if [ ! -f "$DB" ]; then
  bash "$(dirname "$0")/init-db.sh"
fi

# Parse args
PLATFORM="" TITLE="" CONTENT_TYPE="" SOURCE_FOLDER="" PUBLISH_URL="" PUBLISH_DATE="" NOTES=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)       PLATFORM="$2"; shift 2 ;;
    --title)          TITLE="$2"; shift 2 ;;
    --content-type)   CONTENT_TYPE="$2"; shift 2 ;;
    --source-folder)  SOURCE_FOLDER="$2"; shift 2 ;;
    --publish-url)    PUBLISH_URL="$2"; shift 2 ;;
    --publish-date)   PUBLISH_DATE="$2"; shift 2 ;;
    --notes)          NOTES="$2"; shift 2 ;;
    *) echo "{\"ok\":false,\"error\":\"unknown arg: $1\"}"; exit 1 ;;
  esac
done

# Validate required args
if [ -z "$PLATFORM" ] || [ -z "$TITLE" ] || [ -z "$CONTENT_TYPE" ] || [ -z "$SOURCE_FOLDER" ] || [ -z "$PUBLISH_DATE" ]; then
  echo '{"ok":false,"error":"missing required args: --platform, --title, --content-type, --source-folder, --publish-date"}'
  exit 1
fi

# Validate platform
TABLE="pub_${PLATFORM}"
VALID=$(sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name='$TABLE';")
if [ -z "$VALID" ]; then
  echo "{\"ok\":false,\"error\":\"unknown platform: $PLATFORM (table $TABLE not found)\"}"
  exit 1
fi

# Validate content_type
case "$CONTENT_TYPE" in
  article|video|post) ;;
  *) echo "{\"ok\":false,\"error\":\"invalid content_type: $CONTENT_TYPE (must be article/video/post)\"}"; exit 1 ;;
esac

# Check duplicate
EXISTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM $TABLE WHERE source_folder='${SOURCE_FOLDER//\'/\'\'}';")
if [ "$EXISTS" -gt 0 ]; then
  # Update existing record
  ESC_URL="${PUBLISH_URL//\'/\'\'}"
  ESC_NOTES="${NOTES//\'/\'\'}"
  sqlite3 "$DB" "UPDATE $TABLE SET publish_url='$ESC_URL', notes='$ESC_NOTES', updated_at=strftime('%Y-%m-%d %H:%M:%S','now','localtime') WHERE source_folder='${SOURCE_FOLDER//\'/\'\'}';"
  ID=$(sqlite3 "$DB" "SELECT id FROM $TABLE WHERE source_folder='${SOURCE_FOLDER//\'/\'\'}';")
  echo "{\"ok\":true,\"action\":\"updated\",\"id\":$ID,\"table\":\"$TABLE\"}"
else
  # Insert new record
  ESC_TITLE="${TITLE//\'/\'\'}"
  ESC_FOLDER="${SOURCE_FOLDER//\'/\'\'}"
  ESC_URL="${PUBLISH_URL//\'/\'\'}"
  ESC_NOTES="${NOTES//\'/\'\'}"
  sqlite3 "$DB" "INSERT INTO $TABLE (title,content_type,source_folder,publish_url,publish_date,notes) VALUES ('$ESC_TITLE','$CONTENT_TYPE','$ESC_FOLDER','$ESC_URL','$PUBLISH_DATE','$ESC_NOTES');"
  ID=$(sqlite3 "$DB" "SELECT last_insert_rowid();")
  echo "{\"ok\":true,\"action\":\"inserted\",\"id\":$ID,\"table\":\"$TABLE\"}"
fi
