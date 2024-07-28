#!/bin/bash
exec pb/pocketbase serve --http=0.0.0.0:8090 &
exec python tasks.py &
exec uvicorn backend:app --reload --host 0.0.0.0 --port 8077