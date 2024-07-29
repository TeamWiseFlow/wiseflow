#!/bin/bash
exec pb/pocketbase serve --https://pocketbase-d884cgo.sindge.com:8090 &
exec python tasks.py &
exec uvicorn backend:app --reload --host https://is4wkkk.sindge.com --port 8077
