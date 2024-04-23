#!/bin/bash
set -o allexport
set +o allexport
exec uvicorn main:app --reload --host 0.0.0.0 --port 7777 &
exec python background_task.py