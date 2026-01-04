import os
from typing import Optional, Dict, List
import httpx
from core.async_logger import wis_logger


async def _post_json(path: str, payload: Dict, timeout_seconds: int) -> Optional[Dict]:
    base_url = f"http://127.0.0.1:{os.environ.get('WISEFLOW_BACKEND_PORT', 8077)}"
    url = f"{base_url}{path}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=timeout_seconds)
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        wis_logger.info(f"backend connenct timeout")
        return None
    except Exception as e:
        wis_logger.error(f"_post_json error: {str(e)}")
        return None

async def notify_user(msg_code: int, params: List[str] = []) -> None:
    """
    发送通知消息给用户（fire and forget方式，不等待响应）
    
    Args:
        msg_code: 整数状态码（语义由前后端约定）
        params: 消息参数列表，用于填充消息模板
    """
    payload = {"code": msg_code, "params": params, "timeout": 30}
    # 直接等待发送完成，避免在短生命周期事件循环中遗留后台任务
    await _post_json("/user_notify", payload, timeout_seconds=3)

async def ask_user(msg_code: int, params: List[str] = [], timeout: int = 30) -> bool:
    """
    请求用户确认操作（统一接口格式）
    
    Args:
        msg_code: 整数状态码（语义由前后端约定）
        params: 消息参数列表，用于填充消息模板
        timeout: 超时时间（秒），默认30秒
        
    Returns:
        bool: True表示用户确认，False表示超时或失败
    """
    # wis_logger.debug(f"Asking user for confirmation (code={msg_code}): {params}")
    payload = {"code": msg_code, "params": params, "timeout": timeout}
    data = await _post_json("/user_prompt", payload, timeout_seconds=timeout + 2)
    choice = None if data is None else data.get("result")
    if not choice:
        if timeout > 10 and msg_code < 180:
            # timeout 小于 10 代表这个通知仅仅为了弹窗，不依赖用户反馈，因此没必要发消息
            # 标号 180 以上的模板都无需回传
            wis_logger.info(f"ask_user timeout or failed, code={msg_code}, params={params}")
            await notify_user(12, [])
        return False
    return True

async def ask_user_with_input(msg_code: int, params: List[str], timeout: int = 30) -> Optional[str]:
    """
    请求用户确认（为未来扩展保留输入功能）
    
    Args:
        msg_code: 整数状态码（语义由前后端约定）
        params: 消息参数列表，用于填充消息模板
        timeout: 超时时间（秒），默认30秒
        
    Returns:
        Optional[str]: 用户输入的文本内容，None表示超时或失败
        注：未来版本可能返回用户输入的文本内容
    """
    wis_logger.debug(f"Asking user with input option (code={msg_code}): {params}")
    payload = {"code": msg_code, "params": params, "timeout": timeout}
    data = await _post_json("/user_prompt", payload, timeout_seconds=timeout + 5)
    if data is None:
        wis_logger.info(f"ask_user_with_input timeout or failed, code={msg_code}, params={params}")
        await notify_user(12, [])
        return None
    return data.get("result")


async def ping_frontend(timeout_seconds: int = 3) -> bool:
    """
    通过 WS 发送 ding 并等待 dong，检测前端页面是否在线。
    """
    timeout_seconds = max(1, timeout_seconds)
    payload = {"timeout": timeout_seconds}
    data = await _post_json("/ws_ping", payload, timeout_seconds=timeout_seconds + 1)
    return bool(data and data.get("alive"))


def notify_user_sync(msg_code: int, params: List[str]) -> None:
    """
    发送通知消息给用户（同步版本，纯同步 HTTP 调用）。
    避免在此阶段创建/关闭事件循环导致的 Loop is closed 提示。
    """
    base_url = f"http://127.0.0.1:{os.environ.get('WISEFLOW_BACKEND_PORT', 8077)}"
    url = f"{base_url}/user_notify"
    payload = {"code": msg_code, "params": params, "timeout": 30}
    try:
        with httpx.Client(timeout=3) as client:
            client.post(url, json=payload)
    except Exception as e:
        wis_logger.error(f"notify_user_sync error: {str(e)}")
        # 同步通知失败不阻断主流程
