from wwd.async_configs import BrowserConfig, CrawlerRunConfig
from wwd.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy
from wwd.async_logger import AsyncLogger
import os
import json
import asyncio
import sys

# 根据平台导入信号模块
if sys.platform != 'win32':
    import signal
else:
    # Windows 下使用 win32api 处理信号
    try:
        import win32api
        import win32con
    except ImportError:
        win32api = None


async def main():
    
    browser_config = BrowserConfig(
        user_data_dir="work_dir/browser_data",
        verbose=True
    )
    crawler_config = CrawlerRunConfig(
        # capture_network_requests=True,
        # capture_console_messages=True,
        scan_full_page=True,
        # 慎用magic，可能会造成页面上下文损坏，
        # magic=True
    )
    logger = AsyncLogger(
        log_file=os.path.join("work_dir", "wiseflow_web_driver.log"),
        verbose=browser_config.verbose,
        tag_width=10,
    )

    crawler = AsyncPlaywrightCrawlerStrategy(browser_config=browser_config, logger=logger)
    test_list = [
        "https://www.crunchbase.com/",
        # "https://www.yesdotnet.com/archive/post/1634324393.html",
        # "https://bot.sannysoft.com/"
        # "https://www.baidu.com/"
    ]
    
    try:
        await crawler.start()

        for i, url in enumerate(test_list):
            result = await crawler.crawl(url=url, config=crawler_config)
            # Export all captured data to a file for detailed analysis
            with open(f"network_capture_{i+1}.json", "w") as f:
                json.dump({
                    "network_requests": result.network_requests or [],
                    "console_messages": result.console_messages or []
                }, f, indent=4)
            print(f"Exported detailed capture data to network_capture_{i+1}.json")
            print('final html: ', result.html)
            print('final response headers: ', result.response_headers)

    except Exception as e:
        logger.error(f"Error during crawling: {str(e)}", tag="ERROR")
        raise
    finally:
        # 确保在程序结束时关闭浏览器
        try:
            await crawler.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", tag="CLEANUP_ERROR")


def setup_signal_handlers():
    """设置跨平台的信号处理器"""
    if sys.platform != 'win32':
        # Unix-like systems
        def signal_handler(signum, frame):
            print(f"\nReceived signal {signum}, cleaning up...")
            sys.exit(0)
            
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGABRT):
            signal.signal(sig, signal_handler)
    else:
        # Windows
        if win32api:
            def win32_handler(ctrl_type):
                if ctrl_type in (win32con.CTRL_C_EVENT, win32con.CTRL_BREAK_EVENT):
                    print("\nReceived Ctrl+C or Ctrl+Break, cleaning up...")
                    sys.exit(0)
                return False
            win32api.SetConsoleCtrlHandler(win32_handler, True)


if __name__ == "__main__":
    # 设置信号处理器
    setup_signal_handlers()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, cleaning up...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
