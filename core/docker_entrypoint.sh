#!/bin/bash
set -o allexport
source ../.env
set +o allexport
uvicorn backend:app --reload --host localhost --port 8077
#exec uvicorn backend:app --reload --host localhost --port 8077 &
#exec python background_task.py