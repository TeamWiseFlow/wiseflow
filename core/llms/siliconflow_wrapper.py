import os
import httpx
import asyncio
from typing import List, Dict, Any


token = os.environ.get('SF_KEY', "")
if not token:
    raise ValueError('请设置环境变量SF_KEY')

url = "https://api.siliconflow.cn/v1/chat/completions"

# 设置最大并发数为3
concurrent_number = os.environ.get('LLM_CONCURRENT_NUMBER', 1)
semaphore = asyncio.Semaphore(int(concurrent_number))


async def sfa_llm_async(messages: List, model: str, logger=None, **kwargs) -> str:
    """
    使用httpx异步调用SiliconFlow API
    
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

    async with semaphore:  # 使用信号量控制并发
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 最大重试次数
            max_retries = 3
            # 初始等待时间（秒）
            wait_time = 30
            
            for retry in range(max_retries):
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        try:
                            body = response.json()
                            usage = body.get('usage', 'Field "usage" not found')
                            choices = body.get('choices', 'Field "choices" not found')
                            if logger:
                                logger.debug(choices)
                                logger.debug(usage)
                            return choices[0]['message']['content']
                        except (ValueError, KeyError, IndexError) as e:
                            # 如果响应体解析失败，记录错误但不需要重试
                            error_msg = f"Failed to parse successful response: {str(e)}\npayload: {payload}\nresponse: {response.text}"
                            if logger:
                                logger.error(error_msg)
                            else:
                                print(error_msg)
                            return ''
                    elif response.status_code in [400, 401]:
                        # 只有400和401错误不需要重试
                        error_msg = f"Client error: {response.status_code}. Detail: {response.text}"
                        if logger:
                            logger.error(error_msg)
                        else:
                            print(error_msg)
                        return ''
                    else:
                        # 其他所有错误状态码都需要重试
                        error_msg = f"API error: {response.status_code}. Retry {retry+1}/{max_retries}."
                        if logger:
                            logger.warning(error_msg)
                        else:
                            print(error_msg)
                except httpx.RequestError as e:
                    error_msg = f"请求错误: {str(e)}. Retry {retry+1}/{max_retries}."
                    if logger:
                        logger.error(error_msg)
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
        logger.error(error_msg)
    else:
        print(error_msg)
    return ''


# 为了保持向后兼容，提供一个同步版本的包装函数
def sfa_llm(messages: List, model: str, logger=None, **kwargs) -> str:
    """
    同步版本的SiliconFlow API调用函数，内部使用异步实现
    
    Args:
        messages: 消息列表
        model: 模型名称
        logger: 日志记录器
        **kwargs: 其他参数
        
    Returns:
        str: API返回的内容
    """
    return asyncio.run(sfa_llm_async(messages, model, logger, **kwargs))


# 批量处理多个请求的函数
async def batch_process(requests_data: List[Dict[str, Any]], model: str, logger=None) -> List[str]:
    """
    批量处理多个请求
    
    Args:
        requests_data: 包含多个请求数据的列表，每个元素是一个字典，包含messages和其他参数
        model: 模型名称
        logger: 日志记录器
        
    Returns:
        List[str]: 所有请求的结果列表
    """
    tasks = []
    for data in requests_data:
        messages = data.pop("messages", [])
        task = sfa_llm_async(messages, model, logger, **data)
        tasks.append(task)
    
    return await asyncio.gather(*tasks)
