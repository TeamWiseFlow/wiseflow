import os
from openai import AsyncOpenAI as OpenAI
from openai import RateLimitError
import asyncio

base_url = os.environ.get('LLM_API_BASE', "")
token = os.environ.get('LLM_API_KEY', "")

if not base_url and not token:
    raise ValueError("LLM_API_BASE or LLM_API_KEY must be set")
elif base_url and not token:
    client = OpenAI(base_url=base_url, api_key="not_use")
elif not base_url and token:
    client = OpenAI(api_key=token)
else:
    client = OpenAI(api_key=token, base_url=base_url)

concurrent_number = os.environ.get('LLM_CONCURRENT_NUMBER', 1)
semaphore = asyncio.Semaphore(int(concurrent_number))


async def openai_llm(messages: list, model: str, logger=None, **kwargs) -> str:
    resp = ''
    await semaphore.acquire()
    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'model: {model}')
        logger.debug(f'kwargs:\n {kwargs}')

    try:
        response = await client.chat.completions.create(messages=messages, model=model, **kwargs)
        resp = response.choices[0].message.content
    except RateLimitError as e:
        # 直接处理速率限制错误
        if logger:
            logger.warning(f"触发速率限制，等待60秒后重试: {e}")
        else:
            print(f"触发速率限制，等待60秒后重试: {e}")
        
        # 全局等待60秒
        await asyncio.sleep(60)
        
        # 重试请求
        try:
            response = await client.chat.completions.create(messages=messages, model=model, **kwargs)
            resp = response.choices[0].message.content
        except Exception as retry_e:
            if logger:
                logger.error(f"重试失败: {retry_e}")
            else:
                print(f"重试失败: {retry_e}")
    except Exception as e:
        error_msg = str(e)
        if 'Image url should be a valid url or should like data:image/TYPE;base64,YOUR-BASE64-CONTENT' not in error_msg:
            if logger:
                logger.warning(e)
            else:
                print(e)
    finally:
        semaphore.release()

    if logger and resp:
        logger.debug(f'result:\n {response.choices[0]}')
        logger.debug(f'usage:\n {response.usage}')
    return resp
