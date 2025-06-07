import os
from tools.general_utils import get_logger


base_directory = os.path.join(".", os.getenv("PROJECT_DIR", "work_dir"))
os.makedirs(base_directory, exist_ok=True)
wis_logger = get_logger(base_directory, "wiseflow_info_scraper")