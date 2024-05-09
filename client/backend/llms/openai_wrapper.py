"""
除了openai外，很多大模型提供商也都使用openai的SDK，对于这一类可以统一使用本wrapper
这里演示使用deepseek提供的DeepSeek-V2
"""

import os
from openai import OpenAI


token = os.environ.get('LLM_API_KEY', "")
if not token:
    raise ValueError('请设置环境变量LLM_API_KEY')

base_url = os.environ.get('LLM_API_BASE', "")

client = OpenAI(api_key=token, base_url=base_url)


def openai_llm(messages: list, model: str, logger=None, **kwargs) -> str:

    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'model: {model}')
        logger.debug(f'kwargs:\n {kwargs}')

    try:
        response = client.chat.completions.create(messages=messages, model=model, **kwargs)

    except Exception as e:
        if logger:
            logger.error(f'openai_llm error: {e}')
        return ''

    if logger:
        logger.debug(f'result:\n {response.choices[0]}')
        logger.debug(f'usage:\n {response.usage}')

    return response.choices[0].message.content


if __name__ == '__main__':
    import time
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
    pprint(openai_llm(data, "deepseek-chat"))
    print(f'time cost: {time.time() - start_time}')
