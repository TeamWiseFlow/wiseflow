from __future__ import annotations
import asyncio
import json
# from typing import Callable, Dict, Any, List, Union
from typing import Optional
import nodriver as uc
from pathlib import Path
from .config.mc_config import PLATFORM_LOGIN_URLS, WEIBO_PLATFORM_NAME
from async_logger import wis_logger, base_directory


class NodriverHelper:
    def __init__(self, platform: str):
        """
        initialize NodriverHelper
        
        Args:
            platform: platform name, like 'wb', 'zhihu' , or just use the domain.
        """
        self.platform = platform
        self.browser: Optional[uc.Browser] = None
        self.page: Optional[uc.Tab] = None
        
        # 使用单一的浏览器数据目录
        data_dir = Path(base_directory)
        self.browser_data = data_dir / 'browser_data'
        self.export_dir = data_dir / 'nodriver_exported' / platform

        self.export_dir.mkdir(parents=True, exist_ok=True)
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
            'headless': False,
            'browser_args': [
                '--lang=zh-CN',
                #'--no-sandbox',
                '--disable-translate',  # 禁用翻译
                '--no-first-run',  # 禁用首次运行向导
                '--no-default-browser-check'
            ]
        }
        
        self.browser = await uc.start(**config)

    async def open_page(self, url: str = None):
        """
        打开登录页面
        
        Args:
            url: 登录页面的 URL
        """
        if not self.browser:
            await self.start()
        login_url = url or PLATFORM_LOGIN_URLS.get(self.platform)
        if not login_url:
            raise ValueError(f"未找到平台 {self.platform} 的登录URL")
        self.page = await self.browser.get(login_url)
    
    async def for_page_verification(self, url: str = None, timeout: int = 600):
        """
        等待用户完成验证
        
        Args:
            timeout: 最大等待时间（秒）
        """
        # print(f"coming in url: {url}")
        if not self.page:
            await self.open_page(url)

        start_time = asyncio.get_event_loop().time()

        while True:
            # 检查是否超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"等待验证超时（{timeout}秒）")

            await self.page
            verification_keywords = ['captcha', 'verify', 'security', 'challenge', 'recaptcha', 'hcaptcha']
            verification_selectors = [
                'iframe[src*="captcha"]',
                'iframe[src*="recaptcha"]',
                'iframe[src*="hcaptcha"]',
                'div[class*="captcha"]',
                'div[class*="verify"]',
                'form[action*="verify"]',
                'div[class*="recaptcha"]',
                'div[class*="hcaptcha"]',
                'div[class*="security"]',
                'div[class*="challenge"]'
            ]

            try:
                # 检查 URL 中是否包含验证关键词
                current_url = await self.page.evaluate("window.location.href")
                wis_logger.debug(f"current_url: {current_url}")
                if any(keyword in current_url.lower() for keyword in verification_keywords):
                    print(f"Detected verification keyword in URL: {current_url}, 7s后再次检查")
                    await asyncio.sleep(7)
                    continue

                # 检查页面中是否包含验证元素
                for selector in verification_selectors:
                    element = await self.page.query_selector(selector)
                    if element:
                        print(f"Detected verification element: {selector}, 7s后再次检查")
                        await asyncio.sleep(7)
                        continue
                # 如果没有检测到验证，跳出循环
                break

            except Exception as e:
                wis_logger.error(f"检测到验证操作错误: {str(e)}")
                print("请在浏览器中完成验证操作...完成后请按回车键（不要手动关闭浏览器，程序好了会自己关！！！）")
                input_text = await asyncio.get_event_loop().run_in_executor(None, input, "确认已完成验证操作后，请按回车键继续...")
                if input_text.strip() == "":
                    wis_logger.debug("检测到用户确认，登录成功")
                    break
        """
        await asyncio.sleep(7)
        # await self.page.open_external_inspector()
        selected_cookies = await self._get_cookies()
        playwright_cookies = []
        for cookie in selected_cookies.values():
            c = cookie.to_json()
            if 'name' not in c or 'value' not in c or 'domain' not in c or 'path' not in c:
                continue
            playwright_cookies.append({
                'name': c.get('name'),
                'value': c.get('value'),
                'domain': c.get('domain'),
                'path': c.get('path'),
                'expires': c.get('expires', -1),  # 如果 expires 为 None，则设为 -1
                'httpOnly': c.get('httpOnly', False),
                'secure': c.get('secure', False),
                'sameSite': c.get('sameSite', 'Lax') if c.get('sameSite', 'Lax') in ['Strict', 'Lax', 'None'] else 'Lax'
            })
        current_url = await self.page.evaluate("window.location.href")
        #print(f"redirected_url: {current_url}")
        return current_url, playwright_cookies, await self.page.get_local_storage()
        """

    async def for_mc_login(self, url: str = None, timeout: int = 600, force_login: bool = False) -> tuple[str, str]:
        if not self.page:
            await self.open_page(url)

        if force_login:
            await self.browser.cookies.clear()
            await self.page.reload()
            if await self._check_login_status():
                input_text = await asyncio.get_event_loop().run_in_executor(None, input, "请手动操作退出登录，然后再次登录，完成后按回车键继续...")
                if input_text.strip() == "":
                    wis_logger.debug("检测到用户确认，开始检查登录状态")

        start_time = asyncio.get_event_loop().time()
        # 获取初始页面内容
        initial_content = None  # 需要考虑用户已经登录的情况
        
        while True:
            # 检查是否超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"等待登录超时（{timeout}秒）")
            # 检查页面上是否没有登录按钮（通过按钮文字判断）
            try:
                if await self._check_login_status():
                    break
                # 微博平台比较特殊，无法通过按钮判断是否处于登录状态
                if self.platform in [WEIBO_PLATFORM_NAME]:
                    print("请在浏览器中完成登录或确认已登录（没有账号先注册，注册后再登录）...完成后请按回车键（不要手动关闭浏览器，程序好了会自己关！！！）")
                    input_text = await asyncio.get_event_loop().run_in_executor(None, input, "确认处于登录状态后，请按回车键继续...")
                    if input_text.strip() == "":
                        wis_logger.debug("检测到用户确认，登录成功")
                        break

                print("请在浏览器中完成登录（没有账号先注册，注册后再登录）...7s后再次检查")
                await asyncio.sleep(7)
                continue

            except Exception as e:
                wis_logger.error(f"查找'登录'按钮时出错: {str(e)}")
                if initial_content is None:
                    initial_content = await self.page.get_content()
                    wis_logger.debug("等待7s后再次检查...")
                    await asyncio.sleep(7)
                    continue
                #  报错状态只检查一次，第二次则退回到用户主动触发操作
                print("请在浏览器中完成登录或确认已登录（没有账号先注册，注册后再登录）...完成后请按回车键（不要手动关闭浏览器，程序好了会自己关！！！）")
                input_text = await asyncio.get_event_loop().run_in_executor(None, input, "确认处于登录状态后，请按回车键继续...")
                if input_text.strip() == "":
                    wis_logger.debug("检测到用户确认，登录成功")
                    break
        
        selected_cookies = await self._get_cookies()

        # 生成 header_string
        header_string = ";".join([f"{cookie.name}={cookie.value}" for cookie in selected_cookies.values()])
        
        # 获取当前 user agent
        user_agent = await self.page.evaluate("navigator.userAgent")
            
        # 保存信息到文件
        login_token_file = self.export_dir / "login_token.json"
        # 确保目录存在
        save_data = {
            'cookies': header_string,
            'user_agent': user_agent
        }
        with open(login_token_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        wis_logger.info(f"Cookies 已保存到: {login_token_file}")
        
        return header_string, user_agent

    async def _check_login_status(self) -> bool:
        """
        通过查看页面是否有登录特征元素按键判断是否处于已登录状态
        十分粗糙，有待精进

        Returns:
            False: 存在疑似登录按键，未处于已登录状态
            True: 不存在疑似登录按键，处于已登录状态
        """
        await self.page
        # 先尝试查找"登录"按钮
        login_button = await self.page.find_element_by_text("登录", best_match=True, return_enclosing_element=True)
        if login_button:
            if login_button.text.strip() in ["登录", "登录/注册", "一键登录", "验证码登录", "密码登录"]:
                return False

        # 再尝试查找"login"按钮
        login_button = await self.page.find_element_by_text("login", best_match=True, return_enclosing_element=True)
        if login_button:
            if login_button.text.strip().lower() in ["login", "login/register"]:
                return False

        wis_logger.debug("没有找到登录按钮, 判定登录成功")
        return True
    
    async def _get_cookies(self) -> dict:
        # if self.platform == constant.ZHIHU_PLATFORM_NAME:
            # self.page = await self.browser.get("https://www.zhihu.com/search?type=content&q=%E4%BB%8A%E5%A4%A9%E5%AE%89%E5%A5%BD")

        # 等待页面加载完成
        await self.page
        
        # 获取当前页面的 URL 和域名
        current_url = await self.page.evaluate("window.location.href")
        current_domain = await self.page.evaluate("window.location.hostname")
        wis_logger.debug(f"当前页面 URL: {current_url}")
        wis_logger.debug(f"当前域名: {current_domain}")
        
        # 获取 cookies
        cookies = await self.browser.cookies.get_all()

        # 使用字典存储 cookie 信息，包含 value 和 expires
        selected_cookies = {}
        
        # 先处理当前域名的 cookies
        for cookie in cookies:
            if cookie.domain == current_domain:
                if cookie.name not in selected_cookies:
                    selected_cookies[cookie.name] = cookie
                else:
                    if cookie.expires > selected_cookies[cookie.name].expires:
                        selected_cookies[cookie.name] = cookie
            elif cookie.domain in current_domain and cookie.name not in selected_cookies:
                selected_cookies[cookie.name] = cookie
        
        return selected_cookies
        
    async def close(self):
        """关闭浏览器"""
        try:
            if self.browser and not self.browser.stopped:
                self.browser.stop()
        except Exception as e:
            wis_logger.error(f"关闭浏览器时发生错误: {str(e)}")
        finally:
            self.browser = None
            self.page = None
