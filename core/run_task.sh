#!/bin/bash

set -o allexport
source .env
set +o allexport

if ! pgrep -x "pocketbase" > /dev/null; then
    if ! netstat -tuln | grep ":8090" > /dev/null && ! lsof -i :8090 > /dev/null; then
        echo "Starting PocketBase..."
        ../pb/pocketbase serve --http=127.0.0.1:8090 &
    else
        echo "Port 8090 is already in use."
    fi
else
    echo "PocketBase is already running."
fi

python tasks.py