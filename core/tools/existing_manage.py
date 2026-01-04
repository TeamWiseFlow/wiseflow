import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.async_logger import wis_logger, base_directory
from core.wis.config import config


def get_existings_for_focus(focus_id: str) -> dict:
    all_platforms = config['ALL_PLATFORMS']
    visited_record_dir = base_directory / ".wis" / "visited_record" / focus_id
    if not visited_record_dir.exists():
        visited_record_dir.mkdir(parents=True, exist_ok=True)
        return {name: set() for name in all_platforms}
    
    existings = {}
    for name in all_platforms:
        file_path = visited_record_dir / f"{name}.pkl"
        if not file_path.exists():
            existings[name] = set()
            continue
        with open(file_path, "rb") as f:
            existings[name] = pickle.load(f)

    return existings

def save_existings_for_focus(focus_id: str, existings: dict) -> None:
    """
    Save existings data to local files using thread pool
    
    Args:
        focus_id: The focus ID
        existings: Dictionary containing platform names as keys and sets as values
    """
    if not existings:
        return
    
    visited_record_dir = base_directory / ".wis" / "visited_record" / focus_id
    if not visited_record_dir.exists():
        visited_record_dir.mkdir(parents=True, exist_ok=True)
    
    def save_platform_data(platform_name: str, data: set) -> None:
        """Save data for a single platform"""
        file_path = visited_record_dir / f"{platform_name}.pkl"
        with open(file_path, "wb") as f:
            pickle.dump(data, f)
    
    # Use thread pool to save data concurrently
    with ThreadPoolExecutor(max_workers=len(existings)) as executor:
        futures = []
        for platform_name, data in existings.items():
            if isinstance(data, set):
                future = executor.submit(save_platform_data, platform_name, data)
                futures.append(future)
            else:
                wis_logger.warning(f"Skipping platform '{platform_name}' for focus {focus_id}: data is not a set")
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                wis_logger.error(f" ✗ Error saving platform data for focus {focus_id}: {e}")
