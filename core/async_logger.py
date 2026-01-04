import sys, traceback
from core.tools.general_utils import get_logger
from core.async_database import base_directory


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
