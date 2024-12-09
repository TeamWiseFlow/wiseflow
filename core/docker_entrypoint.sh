#!/bin/bash

set -o allexport
source .env
set +o allexport

# 启动 PocketBase
/pb/pocketbase serve --http=0.0.0.0:8090 &
pocketbase_pid=$!

# 启动 Python 任务
python tasks.py &
python_pid=$!

# 启动 Uvicorn
# uvicorn backend:app --reload --host 0.0.0.0 --port 8077 &
# uvicorn_pid=$!

# 定义信号处理函数
trap 'kill $pocketbase_pid $python_pid' SIGINT SIGTERM

# 等待所有进程结束
wait