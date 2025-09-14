#!/usr/bin/env python3
"""
Clear script - Removes specific cache directories from the base directory.

This script removes:
- base_directory/.crawl4ai
- base_directory/browser_data

This is a safe cleanup operation that only removes cached data.
"""

import os
import shutil
import sys


def get_base_directory():
    """Get the base directory path from the same logic as async_logger.py"""
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_file_dir)  # Go back to project root
    base_directory = os.path.join(project_root, os.getenv("PROJECT_DIR", "work_dir"))
    return base_directory


def clear_cache_directories():
    """Remove specific cache directories from base_directory"""
    base_dir = get_base_directory()
    
    # Directories to clean
    crawl4ai_dir = os.path.join(base_dir, ".crawl4ai")
    browser_data_dir = os.path.join(base_dir, "browser_data")
    
    removed_dirs = []
    
    # Remove .crawl4ai directory
    if os.path.exists(crawl4ai_dir):
        try:
            shutil.rmtree(crawl4ai_dir)
            removed_dirs.append(".crawl4ai")
            print(f"✓ Removed: {crawl4ai_dir}")
        except Exception as e:
            print(f"✗ Failed to remove {crawl4ai_dir}: {e}")
    else:
        print(f"• Directory not found: {crawl4ai_dir}")
    
    # Remove browser_data directory
    if os.path.exists(browser_data_dir):
        try:
            shutil.rmtree(browser_data_dir)
            removed_dirs.append("browser_data")
            print(f"✓ Removed: {browser_data_dir}")
        except Exception as e:
            print(f"✗ Failed to remove {browser_data_dir}: {e}")
    else:
        print(f"• Directory not found: {browser_data_dir}")
    
    if removed_dirs:
        print(f"\nCache cleanup completed. Removed directories: {', '.join(removed_dirs)}")
    else:
        print("\nNo directories were removed.")


if __name__ == "__main__":
    print("WiseFlow Cache Cleaner")
    print("======================")
    print("This will remove cached data (.crawl4ai and browser_data directories)")
    print()
    
    try:
        clear_cache_directories()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
