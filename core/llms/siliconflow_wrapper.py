"""
siliconflow api wrapper
https://siliconflow.readme.io/reference/chat-completions-1
"""
import os
import requests


token = os.environ.get('LLM_API_KEY', "")
if not token:
    raise ValueError('请设置环境变量LLM_API_KEY')

url = "https://api.siliconflow.cn/v1/chat/completions"


def sfa_llm(messages: list, model: str, logger=None, **kwargs) -> str:

    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'model: {model}')
        logger.debug(f'kwargs:\n {kwargs}')

    payload = {
        "model": model,
        "messages": messages
    }

    payload.update(kwargs)

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }

    for i in range(2):
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                try:
                    body = response.json()
                    usage = body.get('usage', 'Field "usage" not found')
                    choices = body.get('choices', 'Field "choices" not found')
                    if logger:
                        logger.debug(choices)
                        logger.debug(usage)
                    return choices[0]['message']['content']
                except ValueError:
                    # 如果响应体不是有效的JSON格式
                    if logger:
                        logger.warning("Response body is not in JSON format.")
                    else:
                        print("Response body is not in JSON format.")
        except requests.exceptions.RequestException as e:
            if logger:
                logger.warning(f"A request error occurred: {e}")
            else:
                print(f"A request error occurred: {e}")

        if logger:
            logger.info("retrying...")
        else:
            print("retrying...")

    if logger:
        logger.error("After many time, finally failed to get response from API.")
    else:
        print("After many time, finally failed to get response from API.")

    return ''
