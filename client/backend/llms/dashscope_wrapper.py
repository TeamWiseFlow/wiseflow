# 使用aliyun dashscope的api封装
# 非流式接口
# 为了兼容性，输入输出都使用message格式（与openai SDK格式一致）
import time
from http import HTTPStatus
import dashscope
import random
import os


DASHSCOPE_KEY = os.getenv("LLM_API_KEY")
if not DASHSCOPE_KEY:
    raise ValueError("请指定LLM_API_KEY的环境变量")
dashscope.api_key = DASHSCOPE_KEY


def dashscope_llm(messages: list, model: str, logger=None, **kwargs) -> str:

    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'model: {model}')
        logger.debug(f'kwargs:\n {kwargs}')

    response = dashscope.Generation.call(
        messages=messages,
        model=model,
        result_format='message',  # set the result to be "message" format.
        **kwargs
    )

    for i in range(2):
        if response.status_code == HTTPStatus.OK:
            break
        if response.message == "Input data may contain inappropriate content.":
            break

        if logger:
            logger.warning(f"request failed. code: {response.code}, message:{response.message}\nretrying...")
        else:
            print(f"request failed. code: {response.code}, message:{response.message}\nretrying...")

        time.sleep(1 + i*30)
        kwargs['seed'] = random.randint(1, 10000)
        response = dashscope.Generation.call(
            messages=messages,
            model=model,
            result_format='message',  # set the result to be "message" format.
            **kwargs
        )

    if response.status_code != HTTPStatus.OK:
        if logger:
            logger.warning(f"request failed. code: {response.code}, message:{response.message}\nabort after multiple retries...")
        else:
            print(f"request failed. code: {response.code}, message:{response.message}\naborted after multiple retries...")
        return ''

    if logger:
        logger.debug(f'result:\n {response.output.choices[0]}')
        logger.debug(f'usage:\n {response.usage}')

    return response.output.choices[0]['message']['content']


if __name__ == '__main__':
    from pprint import pprint

    # logging.basicConfig(level=logging.DEBUG)
    system_content = ''
    user_content = '''你是一名优秀的翻译，请帮我把如下新闻标题逐条（一行为一条）翻译为中文，你的输出也必须为一条一行的格式。

The New York Times reported on 2021-01-01 that the COVID-19 cases in China are increasing.
Cyber ops linked to Israel-Hamas conflict largely improvised, researchers say
Russian hackers disrupted Ukrainian electrical grid last year
Reform bill would overhaul controversial surveillance law
GitHub disables pro-Russian hacktivist DDoS pages
Notorious Russian hacking group appears to resurface with fresh cyberattacks on Ukraine
Russian hackers attempted to breach petroleum refining company in NATO country, researchers say
As agencies move towards multi-cloud networks, proactive security is key
Keeping a competitive edge in the cybersecurity ‘game’
Mud, sweat and data: The hard work of democratizing data at scale
SEC sues SolarWinds and CISO for fraud
Cyber workforce demand is outpacing supply, survey finds
Four dozen countries declare they won
White House executive order on AI seeks to address security risks
malware resembling NSA code
CISA budget cuts would be
Hackers that breached Las Vegas casinos rely on violent threats, research shows'''

    data = [{'role': 'user', 'content': user_content}]
    start_time = time.time()
    pprint(dashscope_llm(data, 'qwen-72b-chat'))
    print(f'time cost: {time.time() - start_time}')
