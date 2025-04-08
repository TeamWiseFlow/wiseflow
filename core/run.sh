#!/bin/bash

# Check if PocketBase is running
pb_running=false
if pgrep -f "pocketbase serve" > /dev/null; then
    echo "PocketBase is already running."
    pb_running=true
else
    echo "Starting PocketBase..."
    cd ../pb
    ./pocketbase serve &
    cd ../core
    sleep 2
    echo "PocketBase started."
fi

# Run the schema update script to ensure database is up to date
echo "Updating database schema..."
python -c "
import asyncio
from utils.pb_api import PbTalker
from utils.general_utils import get_logger
from utils.schema_update import update_schema
import os

async def run_schema_update():
    project_dir = os.environ.get('PROJECT_DIR', '')
    logger = get_logger('schema_update', project_dir)
    pb = PbTalker(logger)
    success = await update_schema(pb)
    if success:
        print('Schema update completed successfully')
    else:
        print('Schema update failed')

asyncio.run(run_schema_update())
"

# Run the main process
echo "Starting Wiseflow..."
python run_task.py

# If we started PocketBase, we should stop it when the script exits
if [ "$pb_running" = false ]; then
    echo "Stopping PocketBase..."
    pkill -f "pocketbase serve"
fi