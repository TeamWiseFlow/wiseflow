#!/bin/bash

# 从 .env 文件中加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 启动 PocketBase
pb/pocketbase serve --http=0.0.0.0:8090 &
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