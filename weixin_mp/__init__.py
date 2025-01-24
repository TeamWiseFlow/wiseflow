import websockets
import json
import re
import httpx
import asyncio
import os, sys

core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
sys.path.append(core_path)
env_path = os.path.join(core_path, '.env')

from dotenv import load_dotenv
if os.path.exists(env_path):
    print(f"loading env from {env_path}")
    load_dotenv(env_path)

import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

from general_process import main_process, wiseflow_logger, pb
from typing import Optional


# 千万注意扫码登录时不要选择"同步历史消息"，否则会造成 bot 上来挨个回复历史消息
# 先检查下 wx 的登录状态，同时获取已登录微信的 wxid

WX_BOT_ENDPOINT = os.environ.get('WX_BOT_ENDPOINT', '127.0.0.1:8066')
wx_url = f"http://{WX_BOT_ENDPOINT}/api/"
try:
    # 发送GET请求
    response = httpx.get(f"{wx_url}checklogin")
    response.raise_for_status()  # 检查HTTP响应状态码是否为200
    # 解析JSON响应
    data = response.json()
    # 检查status字段
    if data['data']['status'] == 1:
        # 记录wxid
        self_wxid = data['data']['wxid']
        wiseflow_logger.info(f"已登录微信账号: {self_wxid}")
    else:
        # 抛出异常
        wiseflow_logger.error("未检测到任何登录信息，将退出")
        raise ValueError("登录失败，status不为1")
except Exception as e:
    wiseflow_logger.error(f"无法链接微信端点:{wx_url}, 错误：\n{e}")
    raise ValueError("登录失败，无法连接")

# 获取登录微信昵称，用于后面判断是否@自己的消息
response = httpx.get(f"{wx_url}userinfo")
response.raise_for_status()  # 检查HTTP响应状态码是否为200
# 解析JSON响应
data = response.json()
self_nickname = data['data'].get('nickname', " ")
wiseflow_logger.info(f"self_nickname: {self_nickname}")

# 如果要选定只监控部分公众号，请在同一文件夹内创建 config.json 文件，内容为要监控的公众号列表
# 注意这里要写公众号的原始id，即 gh_ 开头的id, 可以通过历史 logger 获取
config_file = 'config.json'
if not os.path.exists(config_file):
    wiseflow_logger.error("config.json not found, please create it in the same folder as this script")
    raise ValueError(f"config.json not found, please create it in the same folder as this script")
else:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    focus_points = pb.read('focus_points', fields=['id', 'focuspoint', 'explanation'])
    _dict = {point['id']: point for point in focus_points}
    focus_dict = {}
    defaut_focus = None
    for key, value in config.items():
        if "__all__" in value:
            defaut_focus = _dict[key]
        else:
            for nickname in value:
                focus_dict[nickname] = _dict[key]

#如下 pattern 仅适用于public msg的解析，群内分享的公号文章不在此列
# The XML parsing scheme is not used because there are abnormal characters in the XML code extracted from the weixin public_msg
item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
url_pattern = re.compile(r'<url><!\[CDATA\[(.*?)]]></url>')
appname_pattern = re.compile(r'<appname><!\[CDATA\[(.*?)]]></appname>')

async def get_public_msg(websocket_uri):
    reconnect_attempts = 0
    max_reconnect_attempts = 3
    while True:
        try:
            async with websockets.connect(websocket_uri, max_size=10 * 1024 * 1024) as websocket:
                while True:
                    response = await websocket.recv()
                    datas = json.loads(response)
                    for data in datas["data"]:
                        if "Content" not in data:
                            wiseflow_logger.warning(f"invalid data:\n{data}")
                            continue
                        # user_id = data["StrTalker"]
                        appname_match = appname_pattern.search(data["Content"])
                        appname = appname_match.group(1).strip() if appname_match else None
                        if not appname:
                            wiseflow_logger.warning(f"can not find appname in \n{data['Content']}")
                            continue
                        focus = focus_dict.get(appname, defaut_focus)
                        if not focus:
                            wiseflow_logger.debug(f"{appname} related to no focus and there is no default focus")
                            continue
                        sites = []
                        items = item_pattern.findall(data["Content"])
                        # Iterate through all < item > content, extracting < url > and < summary >
                        for item in items:
                            url_match = url_pattern.search(item)
                            url = url_match.group(1) if url_match else None
                            if not url:
                                wiseflow_logger.warning(f"can not find url in \n{item}")
                                continue
                            # URL processing, http is replaced by https, and the part after chksm is removed.
                            url = url.replace('http://', 'https://')
                            cut_off_point = url.find('chksm=')
                            if cut_off_point != -1:
                                url = url[:cut_off_point - 1]
                            # summary_match = summary_pattern.search(item)
                            # addition = summary_match.group(1) if summary_match else None
                            sites.append({'url': url, 'type': 'web'})
                        if sites:
                            # 不等待任务完成，直接创建任务
                            asyncio.create_task(main_process(focus, sites))
        except websockets.exceptions.ConnectionClosedError as e:
            wiseflow_logger.error(f"Connection closed with exception: {e}")
            reconnect_attempts += 1
            if reconnect_attempts <= max_reconnect_attempts:
                wiseflow_logger.info(f"Reconnecting attempt {reconnect_attempts}...")
                await asyncio.sleep(1)
            else:
                wiseflow_logger.error("Max reconnect attempts reached. Exiting.")
                break
        except Exception as e:
            wiseflow_logger.error(f"PublicMsgHandler error: {e}")

uri_public = f"ws://{WX_BOT_ENDPOINT}/ws/publicMsg"
asyncio.run(get_public_msg(uri_public))
