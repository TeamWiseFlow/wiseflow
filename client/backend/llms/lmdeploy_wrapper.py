# 使用lmdepoly_wrapper的api封装
# 非流式接口
# 为了兼容性，输入输出都使用message格式（与openai SDK格式一致）
from lagent.llms.meta_template import INTERNLM2_META as META
from lagent.llms.lmdepoly_wrapper import LMDeployClient
from requests import ConnectionError
import os


def lmdeploy_llm(messages: list[dict],
                  model: str = "qwen-7b",
                  seed: int = 1234,
                  max_tokens: int = 2000,
                  temperature: float = 1,
                  stop: list = None,
                  enable_search: bool = False,
                  logger=None) -> str:

    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'params:\n model: {model}, max_tokens: {max_tokens}, temperature: {temperature}, stop: {stop},'
                     f'enable_search: {enable_search}, seed: {seed}')
        
    top_p = 0.7
    url = os.environ.get('LLM_API_BASE', "http://127.0.0.1:6003")
    api_client = LMDeployClient(model_name=model,
                                url=url, 
                                meta_template=META,
                                max_new_tokens=max_tokens,
                                top_p=top_p,
                                top_k=100,
                                temperature=temperature,
                                repetition_penalty=1.0,
                                stop_words=['<|im_end|>'])
    response = ""
    for i in range(3):
        try:
            response = api_client.chat(messages)
            break
        except ConnectionError:
            if logger:
                logger.warning(f'ConnectionError, url:{url}')
            else:
                print(f"ConnectionError, url:{url}")
            return ""

    return response


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
    pprint(lmdeploy_llm(data, 'qwen-7b'))
    print(f'time cost: {time.time() - start_time}')
