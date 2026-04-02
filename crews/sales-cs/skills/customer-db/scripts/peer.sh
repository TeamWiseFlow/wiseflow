#!/bin/bash
# Resolve awada peer from session key or meta.user_id_external
set -euo pipefail

SESSION_KEY=""
USER_ID_EXTERNAL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --session-key)
      SESSION_KEY="${2:-}"
      shift 2
      ;;
    --user-id-external)
      USER_ID_EXTERNAL="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

extract_from_session_key() {
  local key="$1"
  # Preferred pattern: agent:<agentId>:awada:direct:<sanitized_user_id_external>
  if printf '%s' "$key" | grep -Eq '^agent:[^:]+:awada:direct:.+$'; then
    printf '%s' "$key" | sed -E 's/^agent:[^:]+:awada:direct://'
    return 0
  fi
  # Tolerate odd variants such as agent::awada:direct:<id>
  if printf '%s' "$key" | grep -Eq '^agent:.*:awada:direct:.+$'; then
    printf '%s' "$key" | sed -E 's/^agent:.*:awada:direct://'
    return 0
  fi
  return 1
}

sanitize_user_id() {
  local raw="$1"
  # Keep it readable and SQLite-safe for SQL single-quoted strings.
  # Replace apostrophe and control/whitespace separators with underscores.
  printf '%s' "$raw" \
    | tr '\r\n\t' '___' \
    | sed "s/'/_/g" \
    | sed 's/[[:space:]]\+/_/g'
}

resolved=""
if [ -n "$SESSION_KEY" ]; then
  resolved="$(extract_from_session_key "$SESSION_KEY" || true)"
fi

if [ -z "$resolved" ] && [ -n "$USER_ID_EXTERNAL" ]; then
  resolved="$(sanitize_user_id "$USER_ID_EXTERNAL")"
fi

if [ -z "$resolved" ]; then
  echo "❌ Unable to resolve awada peer suffix from session key or meta.user_id_external" >&2
  exit 1
fi

printf '%s\n' "$resolved"
