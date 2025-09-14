import os
from tools.general_utils import get_logger
import sys, traceback


# 获取脚本所在目录的父目录作为项目根目录
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_current_file_dir)  # 回到项目根目录
base_directory = os.path.join(_project_root, os.getenv("PROJECT_DIR", "work_dir"))
os.makedirs(base_directory, exist_ok=True)
wis_logger = get_logger(base_directory, "wiseflow_info_scraper")

# --- Enhance error logging with traceback information ---
_original_error = wis_logger.error  # Preserve original method

def _error_with_traceback(message: str, *args, **kwargs):
    """Wrap wis_logger.error to append traceback when within an exception context."""
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_type is not None:
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        message = f"{message}\n{tb_str}"
    return _original_error(message, *args, **kwargs)

# Patch the logger so every `.error` call automatically contains traceback data (if available)
wis_logger.error = _error_with_traceback
