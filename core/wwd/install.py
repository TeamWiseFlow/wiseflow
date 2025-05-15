import subprocess
import sys
import asyncio
from .async_logger import AsyncLogger, LogLevel
from pathlib import Path
import os
import shutil


def setup_builtin_browser():
    """Set up a builtin browser for use with Crawl4AI"""
    try:
        logger.info("Setting up builtin browser...", tag="INIT")
        asyncio.run(_setup_builtin_browser())
        logger.success("Builtin browser setup completed!", tag="COMPLETE")
    except Exception as e:
        logger.warning(f"Failed to set up builtin browser: {e}")
        logger.warning("You can manually set up a builtin browser using 'crawl4ai-doctor builtin-browser-start'")
    
async def _setup_builtin_browser():
    try:
        # Import BrowserProfiler here to avoid circular imports
        from .browser_profiler import BrowserProfiler
        profiler = BrowserProfiler(logger=logger)
        
        # Launch the builtin browser
        cdp_url = await profiler.launch_builtin_browser(headless=True)
        if cdp_url:
            logger.success(f"Builtin browser launched at {cdp_url}", tag="BROWSER")
        else:
            logger.warning("Failed to launch builtin browser", tag="BROWSER")
    except Exception as e:
        logger.warning(f"Error setting up builtin browser: {e}", tag="BROWSER")
        raise
