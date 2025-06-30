import os
from openai import AsyncOpenAI as OpenAI
from openai import RateLimitError, APIError
import asyncio
from typing import List, Dict, Any

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

# 设置最大并发数为3
concurrent_number = os.environ.get('LLM_CONCURRENT_NUMBER', 1)
semaphore = asyncio.Semaphore(int(concurrent_number))


async def openai_llm(messages: List, model: str, logger=None, **kwargs) -> str:
    """
    使用OpenAI API异步调用
    
    Args:
        messages: 消息列表
        model: 模型名称
        logger: 日志记录器
        **kwargs: 其他参数
        
    Returns:
        str: API返回的内容
    """
    if logger:
        logger.debug(f'messages:\n {messages}')
        logger.debug(f'model: {model}')
        logger.debug(f'kwargs:\n {kwargs}')

    async with semaphore:  # 使用信号量控制并发
        # 最大重试次数
        max_retries = 3
        # 初始等待时间（秒）
        wait_time = 30
        
        for retry in range(max_retries):
            try:
                response = await client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs
                )
                
                if logger:
                    logger.debug(f'choices:\n {response.choices}')
                    logger.debug(f'usage:\n {response.usage}')
                return response.choices[0].message.content
                
            except RateLimitError as e:
                # 速率限制错误需要重试
                error_msg = f"{model} Rate limit error: {str(e)}. Retry {retry+1}/{max_retries}."
                if logger:
                    logger.warning(error_msg)
                else:
                    print(error_msg)
            except APIError as e:
                if hasattr(e, 'status_code'):
                    if e.status_code in [400, 401]:
                        # 客户端错误不需要重试
                        error_msg = f"{model} Client error: {e.status_code}. Detail: {str(e)}"
                        if logger:
                            logger.warning(error_msg)
                        else:
                            print(error_msg)
                        return ''
                    else:
                        # 其他API错误需要重试
                        error_msg = f"{model} API error: {e.status_code}. Retry {retry+1}/{max_retries}."
                        if logger:
                            logger.warning(error_msg)
                        else:
                            print(error_msg)
                else:
                    # 未知API错误需要重试
                    error_msg = f"{model} Unknown API error: {str(e)}. Retry {retry+1}/{max_retries}."
                    if logger:
                        logger.warning(error_msg)
                    else:
                        print(error_msg)
            except Exception as e:
                # 其他异常需要重试
                error_msg = f"{model} Unexpected error: {str(e)}. Retry {retry+1}/{max_retries}."
                if logger:
                    logger.warning(error_msg)
                else:
                    print(error_msg)

            if retry < max_retries - 1:
                # 指数退避策略
                await asyncio.sleep(wait_time)
                # 下次等待时间翻倍
                wait_time *= 2

    # 如果所有重试都失败
    error_msg = "达到最大重试次数，仍然无法获取有效响应。"
    if logger:
        logger.warning(error_msg)
    else:
        print(error_msg)
    return ''
