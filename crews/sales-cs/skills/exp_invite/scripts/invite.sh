#!/bin/bash
# Send awada invite control message and update customer status to exp_invited.
# --peer: DB primary key (from [CustomerDB].peer), used for all DB operations.
# --user-id-external: raw awada user ID (from Sender.id), used for the invite routing message.
set -euo pipefail

PEER=""
USER_ID_EXTERNAL=""
GROUP_NAME="风暴眼（wiseflow情报小站）"

while [ $# -gt 0 ]; do
  case "$1" in
    --peer)
      PEER="${2:-}"
      shift 2
      ;;
    --user-id-external)
      USER_ID_EXTERNAL="${2:-}"
      shift 2
      ;;
    --group-name)
      GROUP_NAME="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [ -z "$PEER" ]; then
  echo "❌ --peer is required (use [CustomerDB].peer)" >&2
  exit 1
fi

if [ -z "$USER_ID_EXTERNAL" ]; then
  echo "❌ --user-id-external is required (use Sender.id)" >&2
  exit 1
fi

WORKDIR="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$WORKDIR"

bash ./skills/customer-db/scripts/db.sh ensure >/dev/null

existing_status="$(bash ./skills/customer-db/scripts/db.sh sql "SELECT business_status FROM cs_record WHERE peer = '$PEER'" | tail -n +2 | head -n 1 || true)"

if [ -z "$existing_status" ]; then
  bash ./skills/customer-db/scripts/db.sh sql "INSERT INTO cs_record (peer, business_status, purpose, prompt_source) VALUES ('$PEER', 'free', '', '')" >/dev/null
  existing_status="free"
fi

if [ "$existing_status" = "exp_invited" ]; then
  echo "ALREADY_INVITED"
  exit 10
fi

bash ./skills/customer-db/scripts/db.sh sql "UPDATE cs_record SET business_status = 'exp_invited' WHERE peer = '$PEER'" >/dev/null
printf '/invite//%s//%s\n' "$USER_ID_EXTERNAL" "$GROUP_NAME"
