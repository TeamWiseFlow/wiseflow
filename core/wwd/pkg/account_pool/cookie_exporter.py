import asyncio
import json
from typing import Optional
import nodriver as uc
from pathlib import Path
# from constant import PLATFORM_LOGIN_URLS
import constant

class CookieExporter:
    def __init__(self, platform: str):
        """
        initialize CookieExporter
        
        Args:
            platform: platform name, like 'wb', 'zhihu' etc.
        """
        self.platform = platform
        self.login_url = constant.PLATFORM_LOGIN_URLS.get(platform)
        if not self.login_url:
            raise ValueError(f"未找到平台 {platform} 的登录URL")
        self.browser: Optional[uc.Browser] = None
        self.page: Optional[uc.Tab] = None
        
        # 设置固定的用户数据目录
        self.browser_data = Path(__file__).parent / 'browser_data'
        self.user_data_dir = self.browser_data / platform

    async def start(self):
        """启动浏览器"""
        # 设置浏览器配置
        config = {
            'headless': False,
            'user_data_dir': str(self.user_data_dir),  # 使用固定的用户数据目录
            'browser_args': [
                '--lang=zh-CN',
                '--disable-translate',  # 禁用翻译
                '--no-first-run',  # 禁用首次运行向导
                '--no-default-browser-check'
            ]
        }
        
        self.browser = await uc.start(**config)

    async def open_login_page(self, url: str = None):
        """
        打开登录页面
        
        Args:
            url: 登录页面的 URL
        """
        if not self.browser:
            await self.start()
        self.page = await self.browser.get(url or self.login_url)

    async def wait_for_login(self, timeout: int = 600, force_login: bool = False):
        """
        等待用户完成登录
        
        Args:
            timeout: 最大等待时间（秒）
        """
        if not self.page:
            await self.open_login_page()

        if force_login:
            input_text = input("请手动操作退出登录，然后再次登录，完成后按回车键继续...")
            if input_text.strip() == "":
                print("检测到用户确认，开始检查登录状态")

        start_time = asyncio.get_event_loop().time()
        
        # 获取初始页面内容
        initial_content = None  # 需要考虑用户已经登录的情况
        
        while True:
            # 检查是否超时
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"等待登录超时（{timeout}秒）")

            await self.page

            # 检查页面上是否没有登录按钮（通过按钮文字判断）
            try:
                # 先尝试查找"登录"按钮
                login_button = await self.page.find_element_by_text("登录", best_match=True, return_enclosing_element=True)
                if login_button:
                    # print("疑似登录按钮:")
                    # print(login_button.text)
                    if login_button.text.strip() in ["登录", "登录/注册", "一键登录", "验证码登录", "密码登录"]:
                        if self.platform in [constant.WEIBO_PLATFORM_NAME]:
                            print("请在浏览器中完成登录或确认已登录（没有账号先注册，注册后再登录）...完成后请按回车键（不要手动关闭浏览器，程序好了会自己关！！！）")
                            input_text = input("确认处于登录状态后，请按回车键继续...")
                            if input_text.strip() == "":
                                print("检测到用户确认，登录成功")
                                break
                        print("请在浏览器中完成登录（没有账号先注册，注册后再登录）...7s后再次检查")
                        await self.page.sleep(7)
                        continue

                login_button = await self.page.find_element_by_text("login", best_match=True, return_enclosing_element=True)
                if login_button:
                    # print("疑似login按钮:")
                    # print(login_button.text)
                    if login_button.text.strip().lower() in ["login", "login/register"]:
                        print("请在浏览器中完成登录（没有账号先注册，注册后再登录）...7s后再次检查")
                        await self.page.sleep(7)
                        continue
                print("没有找到登录按钮, 登录成功")
                break
            except Exception as e:
                print(f"查找'登录'按钮时出错: {str(e)}")
                if initial_content is None:
                    # initial_content = await self.page.get_content()
                    print("请在浏览器中完成登录或确认已登录（没有账号先注册，注册后再登录）...完成后请按回车键（不要手动关闭浏览器，程序好了会自己关！！！）...7s后再次检查")
                    await self.page.sleep(7)
                    continue
                input_text = input("如果已登录，请按回车键继续...")
                if input_text.strip() == "":
                    print("检测到用户确认，登录成功")
                    break

        
    async def __call__(self, url: str = None, force_login: bool = False) -> tuple[str, str]:
        """
        导出 cookies 到文件
        
        Returns:
            tuple: (header_string, user_agent) 两个字符串
        """
        if not self.browser:
            await self.start()
            await self.open_login_page(url)
            await self.wait_for_login(force_login=force_login)
        
        if not self.page:
            await self.wait_for_login()
        
        if self.platform == constant.ZHIHU_PLATFORM_NAME:
            self.page = await self.browser.get("https://www.zhihu.com/search?type=content&q=%E4%BB%8A%E5%A4%A9%E5%AE%89%E5%A5%BD")
        
        await self.page
            
        # 获取 cookies
        cookies = await self.browser.cookies.get_all()
        # print(f"获取到的 cookies 数量: {len(cookies)}")
        
        # 生成 header string
        header_string = ";".join([f"{cookie.name}={cookie.value}" for cookie in cookies])
        
        # 获取当前 user agent
        user_agent = await self.page.evaluate("navigator.userAgent")
            
        # 保存信息到文件
        login_token_file = self.user_data_dir / "login_token.json"
        save_data = {
            'cookies': header_string,
            'user_agent': user_agent
        }
        with open(login_token_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        print(f"Cookies 已保存到: {login_token_file}")
        
        return header_string, user_agent
        
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

    def get_exist_login_token(self) -> dict:
        """
        获取已存在的登录token
        """
        if not self.browser_data.exists():
            return {}

        exist_login_token = {}
        for platform_dir in self.browser_data.iterdir():
            if not platform_dir.is_dir():
                continue
                
            platform_name = platform_dir.name
            if platform_name not in [
                constant.XHS_PLATFORM_NAME,
                constant.DOUYIN_PLATFORM_NAME, 
                constant.KUAISHOU_PLATFORM_NAME,
                constant.BILIBILI_PLATFORM_NAME,
                constant.WEIBO_PLATFORM_NAME,
                constant.TIEBA_PLATFORM_NAME,
                constant.ZHIHU_PLATFORM_NAME
            ]:
                continue
                
            login_token_file = platform_dir / "login_token.json"
            if not login_token_file.exists():
                continue
                
            try:
                with open(login_token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                    exist_login_token[platform_name] = {
                        'cookies': token_data['cookies'],
                        'user_agent': token_data['user_agent']
                    }
            except Exception as e:
                print(f"读取 {login_token_file} 时发生错误: {str(e)}")
                continue
                
        return exist_login_token
    