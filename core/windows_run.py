import os
import sys
import subprocess
import time
import signal
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('wiseflow')

# Get the absolute path to the PocketBase executable
pb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pb', 'pocketbase.exe'))

# Check if PocketBase is already running
def is_pocketbase_running():
    try:
        # Try to connect to PocketBase's port
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('127.0.0.1', 8090))
        s.close()
        return result == 0
    except:
        return False

# Start PocketBase if it's not already running
pb_process = None
if not is_pocketbase_running():
    logger.info("Starting PocketBase...")
    try:
        # Start PocketBase in a new process
        pb_process = subprocess.Popen([pb_path, 'serve'], 
                                     cwd=os.path.dirname(pb_path),
                                     creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        logger.info("PocketBase started with PID: %s", pb_process.pid)
        # Wait for PocketBase to start
        time.sleep(2)
    except Exception as e:
        logger.error("Failed to start PocketBase: %s", e)
        sys.exit(1)
else:
    logger.info("PocketBase is already running.")

# Update the database schema
async def update_schema():
    try:
        logger.info("Updating database schema...")
        from utils.pb_api import PbTalker
        from utils.general_utils import get_logger
        from utils.schema_update import update_schema
        
        project_dir = os.environ.get('PROJECT_DIR', '')
        schema_logger = get_logger('schema_update', project_dir)
        pb = PbTalker(schema_logger)
        success = await update_schema(pb)
        if success:
            logger.info('Schema update completed successfully')
        else:
            logger.error('Schema update failed')
    except Exception as e:
        logger.error(f"Error updating schema: {e}")

# Run the schema update
asyncio.run(update_schema())

# Define a function to handle cleanup
def cleanup(signum=None, frame=None):
    logger.info("Cleaning up...")
    if pb_process:
        logger.info("Stopping PocketBase...")
        try:
            pb_process.terminate()
            pb_process.wait(timeout=5)
        except:
            # Force kill if it doesn't terminate gracefully
            pb_process.kill()
        logger.info("PocketBase stopped.")
    logger.info("Exiting...")
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    # Run the main process
    logger.info("Starting Wiseflow...")
    from run_task import main
    main()
except KeyboardInterrupt:
    cleanup()
except Exception as e:
    logger.error("Error running Wiseflow: %s", e)
    cleanup()
    sys.exit(1)