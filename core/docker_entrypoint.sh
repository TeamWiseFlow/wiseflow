#!/bin/bash
set -o allexport
source ../.env
set +o allexport
exec pb/pocketbase serve &
exec python tasks.py &
exec uvicorn backend:app --reload --host localhost --port 8077