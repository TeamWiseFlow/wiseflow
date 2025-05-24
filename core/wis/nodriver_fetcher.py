from __future__ import annotations
import asyncio
import json
# from typing import Callable, Dict, Any, List, Union
from typing import Optional
import nodriver as uc
from pathlib import Path
import random


class NodriverHelper:
    def __init__(self, work_dir: str = None):
        """
        initialize NodriverHelper
        
        Args:
            platform: platform name, like 'wb', 'zhihu' , or just use the domain.
        """
        self.browser: Optional[uc.Browser] = None
        self.page: Optional[uc.Tab] = None
        
        # 使用单一的浏览器数据目录
        data_dir = Path(work_dir) if work_dir else Path(__file__).parent.parent / 'work_dir'
        self.browser_data = data_dir / 'browser_data'
        self.browser_data.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    async def start(self):
        """启动浏览器"""
        # 设置浏览器配置
        config = {
            'user_data_dir': str(self.browser_data),  # 使用单一的浏览器数据目录
            'headless': True,
            'browser_args': [
                "--disable-gpu",
                "--disable-gpu-compositing",
                "--disable-software-rasterizer",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars",
                "--window-position=400,0",
                "--ignore-certificate-errors",
                "--ignore-certificate-errors-spki-list",
                "--disable-blink-features=AutomationControlled",
                "--disable-renderer-backgrounding",
                "--disable-ipc-flooding-protection",
                "--force-color-profile=srgb",
                "--mute-audio",
                "--disable-background-timer-throttling",
                "--window-size=1920,1080",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-backgrounding-occluded-windows",
                "--disable-breakpad",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-default-apps",
                "--disable-features=TranslateUI",
                "--disable-hang-monitor",
                "--disable-popup-blocking",
                "--disable-prompt-on-repost",
                "--disable-sync",
                "--metrics-recording-only",
                "--password-store=basic",
                "--use-mock-keychain",
            ]
        }
        
        self.browser = await uc.start(**config)

    async def get_content(self, url: str, timeout: int = 600) -> str:
        """
        获取页面内容
        """
        self.page = await self.browser.get(url)

        start_time = asyncio.get_event_loop().time()

        while not await self.page.scroll_bottom_reached():
            # 检查是否超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"等待验证超时（{timeout}秒）")

            await self.page.scroll_down()
            await asyncio.sleep(random.randint(1, 10))

        return await self.page.get_content()
        
    async def close(self):
        """关闭浏览器"""
        try:
            if self.browser and not self.browser.stopped:
                self.browser.stop()
        except Exception as e:
            print(f"关闭浏览器时发生错误: {str(e)}")
        finally:
            self.browser = None
            self.page = None

    # the followin two methods have the possiblity to replace the crawl4ai CSSExtractor and may do wonderful job with regex-extractor
    # but I'm not sure the difference of the similar function from nodrive and which one should be the best...
    # for css select: query_selector_all(equivalent of javascripts document.querySelectorAll)
    # and still can find by text: find_all, find_elements_by_text
    # more study and test still needed
    
    async def get_select_source(self, url: str, selectors: list[str], timeout: int = 600) -> str:
        """
        获取页面选择器源码
        """
        self.page = await self.browser.get(url)
        results = []
        for selector in selectors:
            # this will wait for the selector to be visible and then get the all the source of the elements
            results.extend(await self.page.select_all(selector, timeout=timeout))
        return results
    
    async def get_select_source_by_xpath(self, url: str, xpaths: list[str], timeout: int = 600) -> str:
        """
        获取页面选择器源码
        """
        self.page = await self.browser.get(url)
        results = []
        for xpath in xpaths:
            results.extend(await self.page.xpath(xpath, timeout=timeout))
        return results

if __name__ == "__main__":
    test_urls = ['https://www.cat.com/',
                 'https://www.komatsu.com/']
    async def main():
        async with NodriverHelper() as helper:
            for url in test_urls:
                content = await helper.get_content(url)
                print(f"url: {url}")
                print(content)
                print("-"*100)

    asyncio.run(main())