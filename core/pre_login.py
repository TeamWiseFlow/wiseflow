from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    
import asyncio
import sys
import select
from typing import Optional

from wis import BrowserConfig, CrawlerRunConfig
from wis.browser_manager import BrowserManager
from custom_processes import crawler_config_map


async def _bring_page_to_front(page) -> None:
    try:
        await page.bring_to_front()
        await asyncio.sleep(0.2)
    except Exception:
        pass


async def _wait_until_quit(prompt: str = "Type 'quit' then Enter to close the browser...", check_interval: float = 0.1) -> None:
    print("\n" + "=" * 60)
    print("🧪 Browser Profiler")
    print(prompt)
    print("=" * 60)

    try:
        while True:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                try:
                    line = sys.stdin.readline().strip().lower()
                except Exception:
                    # If reading stdin fails (e.g., redirected), proceed to exit
                    break

                if line in {"q", "quit", "exit"}:
                    break
            await asyncio.sleep(check_interval)
    except KeyboardInterrupt:
        # Allow Ctrl-C to quit
        pass


async def run_browser_profiler(
    run_config: CrawlerRunConfig,
    start_url: Optional[str] = None,
) -> None:
    """
    Open a persistent browser context for the given CrawlerRunConfig, show a blank page,
    wait until the user types 'quit', then close the browser.

    This allows users to pre-login on target sites so the persisted context (by context_marker)
    can be reused by later crawls.
    """

    manager = BrowserManager(browser_config=BrowserConfig())

    # Create or reuse the persistent context and a fresh page
    page, context = await manager.get_page(crawlerRunConfig=run_config)

    # Show a blank page or an optional start URL
    try:
        await _bring_page_to_front(page)
        if start_url:
            await page.goto(start_url)
        else:
            # Ensure explicit blank page
            await page.goto("about:blank")
    except Exception:
        # Ignore navigation errors for blank/new tab setups
        pass

    # Prompt and wait for user to finish manual actions
    marker = getattr(run_config, "context_marker", "invalide, warning...")
    print(f"Context UID: {marker}")
    await _wait_until_quit()

    # Cleanup
    try:
        await manager.close()
    except Exception:
        pass


def _parse_cli_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Open a persistent browser context for pre-login and wait for 'quit'"
    )
    parser.add_argument(
        "--config-name",
        dest="crawlerunconfig_name",
        type=str,
        default="default",
        help="Name of the CrawlerRunConfig to use, must be in the crawler_config_map",
    )
    parser.add_argument(
        "--start-url",
        dest="start_url",
        type=str,
        default=None,
        help="Optional URL to open initially (default: about:blank)",
    )

    return parser.parse_args()

if __name__ == "__main__":
    cli_args = _parse_cli_args()
    run_cfg = crawler_config_map.get(cli_args.crawlerunconfig_name)
    if not run_cfg:
        print(f"Config name {cli_args.crawlerunconfig_name} not found in crawler_config_map")
        exit(1)
    asyncio.run(run_browser_profiler(run_cfg, start_url=cli_args.start_url))
