#!/bin/bash
set -e

cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
  echo "Usage: ./scripts/generate-patch.sh <patch-name>"
  exit 1
fi

PATCH_NAME="$1"
PATCHES_DIR="patches"
mkdir -p "$PATCHES_DIR"

cd openclaw

# 获取下一个补丁编号
LAST_NUM=$(ls ../$PATCHES_DIR/*.patch 2>/dev/null | sed 's/.*\/\([0-9]*\)-.*/\1/' | sort -n | tail -1)
NEXT_NUM=$(printf "%03d" $((10#${LAST_NUM:-0} + 1)))

PATCH_FILE="../$PATCHES_DIR/${NEXT_NUM}-${PATCH_NAME}.patch"

echo "📝 Generating patch: $(basename "$PATCH_FILE")"

git diff -- . ':(exclude)pnpm-lock.yaml' > "$PATCH_FILE"

if [ ! -s "$PATCH_FILE" ]; then
  echo "⚠️  No changes detected"
  rm "$PATCH_FILE"
  exit 1
fi

echo "✅ Patch generated: $PATCH_FILE"
