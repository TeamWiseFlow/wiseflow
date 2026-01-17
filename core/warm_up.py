from core.wis.config import config
from core.wis.ws_connect import ask_user, notify_user, ping_frontend
from core.async_logger import wis_logger, base_directory
import json
import asyncio
import time
from core.wis import (SqliteCache, 
                 AsyncWebCrawler, 
                 CrawlerRunConfig, 
                 BrowserConfig)

from core.wis.browser_manager import BrowserManager
from core.custom_processes import DEFAULT_CRAWLER_CONFIG, crawler_config_map
from core.async_database import AsyncDatabaseManager
from core.wis.proxy_providers import KuaiDaiLiProxy, LocalProxy


async def load_proxies(db: AsyncDatabaseManager, required_platforms: set) -> dict:

    if not db or not required_platforms:
        return {}
    
    try:
        # 1. 读取所有代理数据
        local_proxies = await db.list_local_proxies()
        kdl_proxies = await db.list_kdl_proxies()
        wis_logger.debug(f"读取到 {len(local_proxies)} 个本地代理，{len(kdl_proxies)} 个快代理配置")

        platform_proxies = {}
        # 2. 为每个平台挑选代理
        for platform in required_platforms:
            # 优先检查快代理配置
            selected_kdl_proxy = None
            latest_kdl_updated = None
            
            for proxy in kdl_proxies:
                apply_to = proxy.get('apply_to', [])
                if platform in apply_to:
                    updated = proxy.get('updated', '')
                    if latest_kdl_updated is None or updated > latest_kdl_updated:
                        selected_kdl_proxy = proxy
                        latest_kdl_updated = updated
            
            # 3. 创建代理对象
            if selected_kdl_proxy:
                # 使用快代理
                try:
                    proxy_provider = KuaiDaiLiProxy(
                        uni_name=f"{platform}_kdl_proxy",
                        ip_pool_count=2,  # 快代理可以获取多个IP，2个够了
                        enable_validate_ip=False,
                        kdl_user_name=selected_kdl_proxy.get('USER_NAME', ''),
                        kdl_user_pwd=selected_kdl_proxy.get('USER_PWD', ''),
                        kdl_secret_id=selected_kdl_proxy.get('SECERT_ID', ''),
                        kdl_signature=selected_kdl_proxy.get('SIGNATURE', ''),
                        clear_all_cache=True
                    )
                    platform_proxies[platform] = proxy_provider
                    wis_logger.debug(f"✓ {platform} 使用快代理配置")
                except Exception as e:
                    wis_logger.warning(f"✗ 为平台 {platform} 创建快代理失败: {e}")
            else:
                # 没有快代理，检查本地代理
                matched_local_proxies = []
                for proxy in local_proxies:
                    apply_to = proxy.get('apply_to', [])
                    if platform in apply_to:
                        proxy_config = {
                            "ip": proxy.get('ip', ''),
                            "port": proxy.get('port', 0),
                            "user": proxy.get('user', ''),
                            "password": proxy.get('password', ''),
                            "life_time": proxy.get('life_time', 0)
                        }
                        matched_local_proxies.append(proxy_config)
                
                if matched_local_proxies:
                    # 创建本地代理
                    try:
                        temp_file = base_directory / "local_proxies" / f"{platform}_local_proxy.json"
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            json.dump(matched_local_proxies, f, ensure_ascii=False, indent=2)
                        proxy_provider = LocalProxy(
                            uni_name=f"{platform}_local_proxy",
                            ip_pool_count=len(matched_local_proxies),
                            enable_validate_ip=False,
                            local_proxy_file=str(temp_file),
                            clear_all_cache=True
                        )
                        platform_proxies[platform] = proxy_provider
                        wis_logger.debug(f"✓ {platform} 使用本地代理，共 {len(matched_local_proxies)} 个配置")
                    except Exception as e:
                        wis_logger.warning(f"✗ 为平台 {platform} 创建本地代理失败: {e}")

        return platform_proxies
        
    except Exception as e:
        wis_logger.warning(f"加载代理失败: {e}")
        await ask_user(180, [], timeout=5)
        return {}

# 实际使用时，先初始化 db_manager, 然后load_proxies, 如果 web 配置了 proxy_provider, 更新 run_config.proxy_provider后传入
# 本方法要用 try，网页访问失败率很高。
async def pre_login(
    urls: list[str],
    browser_manager: BrowserManager,
    run_config: CrawlerRunConfig,
    timeout: int = 120
) -> None:
    """
    Open a persistent browser context for the given CrawlerRunConfig, show a blank page,
    wait until the user types 'quit', then close the browser.

    This allows users to pre-login on target sites so the persisted context (by context_marker)
    can be reused by later crawls.
    """
    web_lock = asyncio.Lock()
    for url in urls:
        url = url.strip()
        if not url.startswith('http'):
            main_url_parts = url.rsplit('/', 1)[0].split('.')
            if len(main_url_parts) < 2:
                wis_logger.warning(f"url is not a valid url: {url}")
                await ask_user(103, [url])
                continue
            else:
                url = f"https://{url}"

        # 需要用户逐一操作
        async with web_lock:
            await notify_user(5, [url])
            try:
                page, context = await browser_manager.get_page(crawlerRunConfig=run_config)
                await page.goto(url, wait_until=run_config.wait_until, timeout=run_config.page_timeout)

                async def _check_login_status() -> bool:
                    # 1. 检查 localStorage - 高准确度，低运算量，优先检查
                    try:
                        local_storage = await page.evaluate('''() => {
                            const storage = {};
                            for (let i = 0; i < localStorage.length; i++) {
                                const key = localStorage.key(i);
                                storage[key] = localStorage.getItem(key);
                            }
                            return storage;
                        }''')
                        
                        # 检查常见的登录标识
                        login_keys = ['accesstoken', 'authtoken', 'userinfo', 'isloggedin', 'loginstate']
                        storage_str = str(local_storage).lower()
                        
                        for key in login_keys:
                            if key in storage_str:
                                wis_logger.info(f"Found login-related data in localStorage: {key}")
                                return True
                                
                    except Exception as e:
                        wis_logger.info(f"Failed to check localStorage: {e}")
                    
                    # 2. 检查 sessionStorage - 高准确度，低运算量
                    try:
                        session_storage = await page.evaluate('''() => {
                            const storage = {};
                            for (let i = 0; i < sessionStorage.length; i++) {
                                const key = sessionStorage.key(i);
                                storage[key] = sessionStorage.getItem(key);
                            }
                            return storage;
                        }''')
                        
                        storage_str = str(session_storage).lower()
                        login_keys = ['accesstoken', 'authtoken', 'userinfo', 'isloggedin', 'loginstate']
                        
                        for key in login_keys:
                            if key in storage_str:
                                wis_logger.info(f"Found login-related data in sessionStorage: {key}")
                                return True
                            
                    except Exception as e:
                        wis_logger.info(f"Failed to check sessionStorage: {e}")
                    
                    # 3. 检查 Cookie - 高准确度，低运算量
                    try:
                        # 使用当前页面URL获取cookies，更安全可靠
                        cookies = await page.context.cookies(page.url)
                        login_cookie_names = ['login', 'sid', 'authtoken']
                        
                        for cookie in cookies:
                            cookie_name = cookie['name'].lower()
                            for name_pattern in login_cookie_names:
                                if name_pattern == cookie_name:
                                    wis_logger.info(f"Found login-related cookie: {cookie['name']}")
                                    return True
                            
                    except Exception as e:
                        wis_logger.info(f"Failed to check cookies: {e}")
                    
                    # 4. 检查页面中的用户信息元素 - 中等准确度，中等运算量
                    try:
                        user_element_selectors = [
                            # 用户头像和信息
                            '.avatar', '.user-avatar', '.profile-img', '.profile-image',
                            '.username', '.user-name', '.profile-name', '.user-info',
                            # 登出相关元素
                            '.logout', '.sign-out', '.log-out',
                            # 中文登出
                            '*:has-text("注销")', '*:has-text("登出")',
                            # 英文登出
                            'button:has-text("Logout")', 'a:has-text("Logout")',
                            'button:has-text("Sign Out")', 'a:has-text("Sign Out")',
                            'button:has-text("Log Out")', 'a:has-text("Log Out")'
                        ]
                        
                        for selector in user_element_selectors:
                            try:
                                elements = await page.query_selector_all(selector)
                                if elements:
                                    wis_logger.info(f"Found user element: {selector}")
                                    return True
                            except Exception:
                                continue
                                
                    except Exception as e:
                        wis_logger.info(f"Failed to check user elements: {e}")
                    
                    # 5. 最后检查登录相关元素 - 使用特征文本和表单元素检测
                    login_element_selectors = [
                        # 中文登录相关文本元素
                        '*:has-text("登录")', '*:has-text("登錄")', '*:has-text("立即登录")', '*:has-text("马上登录")',
                        # 英文登录相关文本元素
                        '*:has-text("Login")', '*:has-text("Log In")', '*:has-text("Log On")',
                        # 表单元素（高准确度）
                        'input[name="username" i]', 'input[name="password" i]', 
                        'input[name="email" i]', 'input[type="password"]',
                        'form[id*="login" i]', 'form[class*="login" i]',
                        # 登录按钮和链接
                        'button[id*="login" i]', 'button[class*="login" i]',
                        # 'a[href*="login" i]', 'a[href*="signin" i]',
                        # 验证相关元素
                        '.verification', '.verify-btn', '.verify', '.captcha',
                        # 去验证按键
                        'button:has-text("去验证")'
                    ]
                    
                    for selector in login_element_selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            if elements:
                                wis_logger.info(f"Found login element: {selector}")
                                return False
                        except Exception:
                            continue
                    # pre-login 环节应该保守
                    return False

                start_time = time.monotonic()
                # 首先用户点击登录，可能会跳转，跳转页面很可能检测不出来登录状态，或者会产生误判。这个时候就会发生用户正在操作，突然网页关了
                # 其次登录好之后，我也不知道它会不会跳回来
                # 这里也只能让用户来手动确认了，但可以设定一个时间（每次问询已经是等待3min了），超时了就自然过，这对应用户完成操作，没有回来点确认的情况
                while True:
                    if await _check_login_status():
                        return
                    
                    if await ask_user(113, [url]):
                        break
                    
                    if time.monotonic() - start_time > timeout:
                        wis_logger.warning(f"pre-login timeout, user not confirm, exit")
                        break
                    
                if not await _check_login_status():
                    wis_logger.info(f"Login check failed, but user confirmed or timeout, continue...")
                    # await notify_user(16, [url])

            except Exception as e:
                wis_logger.warning(f"pre-login failed: {e}")
                await notify_user(14, [url])
                # await notify_user(16, [url])
                
            finally:
                if not page.is_closed():
                    await page.close()

# 上层调用本函数时，必须使用 try except finally 结构，finally 中进行优雅关闭（清理 db_manager\cache_manager\browser_manager）
# db_manager\cache_manager  在外层初始化，crawlers按 required platform，传入空值字典，在函数内进行初始化
# 期间任何报错都会被以 RuntimeError 报出，上层可以通过 msg 捕获到错误信息
async def prepare_to_work(db_manager: AsyncDatabaseManager, cache_manager: SqliteCache, crawlers: dict):
    # 打开控制台页面（前端）
    if not await ping_frontend():
        print("\033[35mwiseflow 预检程序即将启动\033[0m")
    
    # 1. prepare proxies
    proxies = await load_proxies(db_manager, set(crawlers.keys()))

    # 2. init crawlers
    # 这一步所有的错误都已经在 crawler 中进行记录和用户反馈（而且已经完成了全部用户引导动作），这里仅需捕捉后兜底通知用户即可
    initialed_crawlers = 0
    # web crawler 最后，在这之前需要先执行 pre_login
    if "web" in crawlers:
        if "web" in proxies:
            for _, crawl_run_config in crawler_config_map.items():
                crawl_run_config.proxy_provider = proxies["web"]
        try:
            async with BrowserManager(browser_config=BrowserConfig(), logger=wis_logger) as browser_manager:
                await pre_login(config["NEED_LOGIN_DOMAINS"], browser_manager, crawler_config_map["default"])
        except Exception as e:
            wis_logger.warning(f"during web pre-login process, error occurred: {e}")
            await notify_user(74)

    if "web" in crawlers or "bing" in crawlers or "rss" in crawlers:
        try:
            crawler = AsyncWebCrawler(crawler_config_map=crawler_config_map, db_manager=cache_manager)
            await crawler.start()
            crawlers["web"] = crawler
            initialed_crawlers += 1
        except Exception as e:
            wis_logger.warning(f"web crawler start failed: {e}")
            await notify_user(74, [])
    
    if initialed_crawlers == 0:
        wis_logger.warning("no crawlers initialized during warm up")
        raise RuntimeError('197')

def _parse_cli_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Open a persistent browser context for pre-login and wait for 'quit'"
    )
    parser.add_argument(
        "--url",
        dest="url",
        type=str,
        default=None,
        help="Optional URL to open initially",
    )

    return parser.parse_args()

if __name__ == "__main__":
    cli_args = _parse_cli_args()
    browser_manager = BrowserManager(browser_config=BrowserConfig(), logger=wis_logger)
    asyncio.run(pre_login(urls=[cli_args.url], browser_manager=browser_manager, run_config=DEFAULT_CRAWLER_CONFIG))
