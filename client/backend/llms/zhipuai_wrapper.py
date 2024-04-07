import os

from zhipuai import ZhipuAI

zhipu_token = os.environ.get('ZHIPUAI_API_KEY', "")
if not zhipu_token:
    raise ValueError('请设置环境变量ZHIPUAI_API_KEY')

client = ZhipuAI(api_key=zhipu_token)  # 填写您自己的APIKey


def zhipuai_llm(messages: list,
                  model: str,
                  seed: int = 1234,
                  max_tokens: int = 2000,
                  temperature: float = 0.8,
                  stop: list = None,
                  enable_search: bool = False,
                  logger=None) -> str:

    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'params:\n model: {model}, max_tokens: {max_tokens}, temperature: {temperature}, stop: {stop},'
                     f'enable_search: {enable_search}, seed: {seed}')

    for i in range(3):
        try:
            response = client.chat.completions.create(
                model="glm-4",  # 填写需要调用的模型名称
                seed=seed,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if response and response.choices:
                break
        except Exception as e:
            if logger:
                logger.error(f'error:\n {e}')
            else:
                print(e)
            continue

    if logger:
        logger.debug(f'result:\n {response}')
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
    pprint(zhipuai_llm(data, 'glm-4'))
    print(f'time cost: {time.time() - start_time}')
