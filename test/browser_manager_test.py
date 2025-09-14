import sys
import os
root_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(root_path)

from wis.async_configs import CrawlerRunConfig, BrowserConfig
from wis.browser_manager import BrowserManager
import asyncio


async def test_browser_manager():
    browser_manager = BrowserManager(BrowserConfig())
    await browser_manager.start()
    page1, context = await browser_manager.get_page(CrawlerRunConfig(context_marker="4f5488840da6a471524cd79b81b7103b0ab4e060e0a09ea71efed48ce147b18d"))
    if not context:
        print("context is None")
    await page1.goto("https://www.baidu.com")
    _ = input("press enter to close page1")
    await page1.close()
    page2, context = await browser_manager.get_page(CrawlerRunConfig(context_marker="4f5488840da6a471524cd79b81b7103b0ab4e060e0a09ea71efed48ce147b18d"))
    await page2.goto("https://www.163.com")
    _ = input("press enter to end")
    await browser_manager.close()

if __name__ == "__main__":
    asyncio.run(test_browser_manager())
