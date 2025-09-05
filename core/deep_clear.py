#!/usr/bin/env python3
"""
Deep Clear script - Removes the entire base directory.

WARNING: This script removes the entire base directory including all data, 
cached content, and database files. This may cause duplicate infos to be 
generated for a period of time after running this script.

Use this script only when you want to completely reset the working directory.
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


def confirm_deletion():
    """Ask user for confirmation before proceeding with deep clear"""
    print("⚠️  WARNING: DEEP CLEAR OPERATION")
    print("=" * 50)
    print("This operation will:")
    print("• Remove the ENTIRE work dir and all its contents")
    print("• Delete all cached data, browser data, and database files")
    print("• May cause DUPLICATE INFOS to be generated for some time")
    print("• This action CANNOT be undone")
    print()
    
    base_dir = get_base_directory()
    print(f"Target directory: {base_dir}")
    print()
    
    # Ask for confirmation
    response = input("Are you sure you want to proceed? Type 'DELETE' to confirm: ").strip()
    return response == "DELETE"


def deep_clear_directory():
    """Remove the entire base directory"""
    base_dir = get_base_directory()
    
    if not os.path.exists(base_dir):
        print(f"• Directory not found: {base_dir}")
        print("Nothing to clear.")
        return
    
    try:
        # Get the size of directory before deletion (for information)
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(base_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    pass  # Skip files that can't be accessed
        
        size_mb = total_size / (1024 * 1024)
        print(f"Removing directory: {base_dir}")
        print(f"Total size: {size_mb:.2f} MB")
        print()
        
        # Remove the entire directory
        shutil.rmtree(base_dir)
        print("✓ Deep clear completed successfully!")
        print()
        print("⚠️  IMPORTANT NOTICE:")
        print("The system may generate duplicate infos for a period of time")
        print("as it rebuilds the working directory and cache.")
        
    except Exception as e:
        print(f"✗ Failed to remove directory: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("WiseFlow Deep Cleaner")
    print("=====================")
    print()
    
    try:
        if confirm_deletion():
            print("\nProceeding with deep clear...")
            deep_clear_directory()
        else:
            print("\nOperation cancelled. Directory was not removed.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
