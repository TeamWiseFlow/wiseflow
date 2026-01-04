import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from .ws import hub, PromptBus, PingManager
import os
# 导入数据库管理器
from core.async_database import AsyncDatabaseManager
from .config import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize resources
    try:
        await db_manager.initialize()
        yield
    except asyncio.CancelledError:
        # Suppress noisy cancellation during Ctrl+C shutdown
        pass
    finally:
        try:
            await db_manager.cleanup()
        except Exception as e:
            logger.warning(f"Error during database cleanup: {e}")

app = FastAPI(title="wiseflow backend", lifespan=lifespan)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加私有网络访问支持（解决从 HTTPS 访问本地地址的问题）
# Chrome 114+ 全面实施了私有网络访问（PNA）策略，要求从 HTTPS 站点访问本地地址（如 127.0.0.1）
# 时，服务器必须明确返回 Access-Control-Allow-Private-Network: true 响应头
# Edge 浏览器可能使用较早的 Chromium 版本或不同的默认策略，因此可能不会触发此限制
# 这个修复确保所有浏览器（包括 Chrome 114+）都能正常访问本地后端服务
@app.middleware("http")
async def add_pna_header(request: Request, call_next):
    response = await call_next(request)
    # 添加 Access-Control-Allow-Private-Network 头以允许从 HTTPS 访问本地地址
    # 这个头需要在所有响应中（包括预检请求）都设置，才能解决 Chrome 114+ 的问题
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response

# 创建数据库管理器实例
db_manager = AsyncDatabaseManager(logger=logger)
# 让 prompt_bus 能够直接写库
prompt_bus = PromptBus(hub, db_manager=db_manager)
ping_manager = PingManager(hub)

# 响应模型
class APIResponse(BaseModel):
    success: bool
    msg: str
    data: Any = None


# 请求模型
class UserIdRequest(BaseModel):
    user_id: str


# 任务字段允许值
ALLOWED_SEARCH = {"bing", "github", "arxiv"}
ALLOWED_SOURCE_TYPES = {"web", "rss"}
ALLOWED_TIME_SLOTS = {'first', 'second', 'third', 'fourth'}

def _validate_task_inputs(search: Optional[List[str]] = None,
                          sources: Optional[List[Dict]] = None,
                          time_slots: Optional[List[str]] = None) -> Optional[str]:
    # search 校验
    if search is not None:
        if not isinstance(search, list) or any(not isinstance(s, str) for s in search):
            return "search 必须为字符串列表"
        for s in search:
            if s not in ALLOWED_SEARCH:
                return f"search 包含非法值: {s}"

    # sources 校验
    if sources is not None:
        for src in sources:
            if not isinstance(src, dict):
                return "sources 列表元素必须为对象"
            src_type = src.get("type")
            if src_type not in ALLOWED_SOURCE_TYPES:
                return f"sources.type 非法: {src_type}"
            # detail 必须是列表
            if "detail" not in src:
                return "sources 每项必须包含 detail 字段"
            detail = src.get("detail")
            if not isinstance(detail, list):
                return "sources.detail 必须为列表"
            if any(not isinstance(item, str) for item in detail):
                return "sources.detail 列表元素必须为字符串"

    # time_slots 校验
    if time_slots is not None:
        if not isinstance(time_slots, list) or any(not isinstance(t, str) for t in time_slots):
            return "time_slots 必须为字符串列表"
        for t in time_slots:
            if t not in ALLOWED_TIME_SLOTS:
                return f"time_slots 包含非法值: {t}"

    return None


class TaskRequest(BaseModel):
    focuses: List[Dict | int] = []
    search: Optional[List[str]] = None  # bing、github、arxiv
    sources: List[Dict] = []  # type: web/rss, detail: List[str]
    activated: Optional[bool] = True
    time_slots: Optional[List[str]] = None  # morning、afternoon、evening、dawn
    title: Optional[str] = None  # 任务标题，可选


class TaskUpdateRequest(BaseModel):
    task_id: int
    focuses: Optional[List[Dict | int]] = None
    search: Optional[List[str]] = None
    sources: Optional[List[Dict]] = None
    activated: Optional[bool] = None
    time_slots: Optional[List[str]] = None
    title: Optional[str] = None


class ProxyRequest(BaseModel):
    ip: str
    port: int
    user: Optional[str] = None
    password: Optional[str] = None
    apply_to: List[str] = []
    life_time: Optional[int] = 0


class KdlProxyRequest(BaseModel):
    SECERT_ID: str
    SIGNATURE: str
    USER_NAME: str
    USER_PWD: str
    apply_to: List[str] = []


class UserNotifyRequest(BaseModel):
    code: int
    params: List[str] = []
    timeout: int = 30


class UserPromptRequest(BaseModel):
    code: int
    params: List[str] = []
    timeout: int = 30
    actions: Optional[List[Dict]] = None


class FrontendPingRequest(BaseModel):
    timeout: Optional[int] = 3

# 2. list_task
@app.get("/list_task")
async def list_task():
    tasks = await db_manager.list_tasks()
    if tasks is not None:
        return APIResponse(success=True, msg="", data=tasks)
    else:
        return APIResponse(success=False, msg="获取任务列表失败", data=[])

# 3. del_task
@app.delete("/del_task")
async def del_task(task_id: int):
    result = await db_manager.delete_task(task_id)
    if result is not None:
        return APIResponse(success=True, msg="", data=None)
    else:
        return APIResponse(success=False, msg=f"task {task_id} 删除失败", data=None)

# 4. read_task
@app.get("/read_task")
async def read_task(task_id: int):
    tasks = await db_manager.list_tasks()
    if tasks is not None:
        for t in tasks:
            if t['id'] == task_id:
                return APIResponse(success=True, msg="", data=t)
        return APIResponse(success=False, msg=f"task {task_id} 不存在", data=None)
    else:
        return APIResponse(success=False, msg="获取任务列表失败", data=None)  

# 5. add_task
@app.post("/add_task")
async def add_task(request: TaskRequest):
    # 严格校验输入
    error = _validate_task_inputs(
        search=request.search if request.search is not None else [],
        sources=request.sources or [],
        time_slots=request.time_slots if request.time_slots is not None else []
    )
    if error:
        return APIResponse(success=False, msg=error, data=None)

    task_id = await db_manager.add_task(
        focuses=request.focuses or [],
        search=request.search or [],
        sources=request.sources or [],
        activated=request.activated if request.activated is not None else True,
        time_slots=request.time_slots or [],
        title=(request.title or "").strip(),
    )
        
    if task_id is not None:
        # 返回创建成功的task_id
        return APIResponse(success=True, msg="", data=task_id)
    else:
        return APIResponse(success=False, msg="task创建失败", data=None)

# 6. update_task
@app.put("/update_task")
async def update_task(request: TaskUpdateRequest):
    """
    特别注意：
    这个接口中对应的内容要填入更新后的内容，比如 focuses中，新增或修改的focus 传入 完整的 dict，没有改变的传入 focus_id
    search time_slot 这些也是这样，
    本质上，backend 接受后，会按提供的内容进行覆盖写
    """
    # 构建更新字段字典
    update_fields = {}
        
    if request.focuses is not None:
        update_fields['focuses'] = request.focuses
    if request.search is not None:
        update_fields['search'] = request.search  
    if request.sources is not None:
        update_fields['sources'] = request.sources
    if request.activated is not None:
        update_fields['activated'] = request.activated
    if request.time_slots is not None:
        update_fields['time_slots'] = request.time_slots
    if request.title is not None:
        update_fields['title'] = request.title
    
    # 仅校验传入的字段
    error = _validate_task_inputs(
        search=update_fields.get('search', None),
        sources=update_fields.get('sources', None),
        time_slots=update_fields.get('time_slots', None)
    )
    if error:
        return APIResponse(success=False, msg=error, data=None)
            
    # 执行更新
    result = await db_manager.update_task(request.task_id, **update_fields)
        
    if result is not None:
        # 返回更新结果，获取focus_ids用于返回
        return APIResponse(success=True, msg="", data=request.task_id)
    else:
        return APIResponse(success=False, msg="任务更新失败", data=None)

# 27. clear_task_errors
@app.get("/clear_task_errors")
async def clear_task_errors(task_id: int):
    """清除指定任务的错误信息并将状态重置为正常"""
    result = await db_manager.clear_task_error(task_id)
    if result is not None:
        return APIResponse(success=True, msg="", data=result)
    else:
        return APIResponse(success=False, msg=f"清除任务 {task_id} 错误信息失败", data=None)

# 7. read_focus
@app.get("/read_focus")
async def read_focus():
    focuses = await db_manager.list_all_focuses()
    if focuses is not None:
        return APIResponse(success=True, msg="", data=focuses)
    else:
        return APIResponse(success=False, msg="获取 focus 列表失败", data=[])

# 8. list_info
@app.get("/list_info")
async def list_info(start_time: Optional[str] = None, max_items_per_focus: int = 0):
    """
    按所有 focus_id 分组返回 start_time 之后的最新信息；
    每个 focus 最多返回 max_items_per_focus 条（<=0 时默认最多 12 条）。
    start_time 建议使用 ISO 8601 UTC（如 2025-01-01T00:00:00Z）。
    """
    focuses = await db_manager.list_all_focuses()
    if focuses is None:
        return APIResponse(success=False, msg="获取 focus 列表失败", data={})

    per_focus_limit = 12 if max_items_per_focus <= 0 else min(max_items_per_focus, 12)

    # 1) 批量查询所有 focus 的信息，按每个 focus 限制数量
    focus_ids = [int(f.get("id")) for f in focuses if f.get("id") is not None]
    infos = await db_manager.filter_infos(
        focus_ids=focus_ids,
        start_time=(start_time or None),
        per_focus_limit=per_focus_limit,
    )

    # 2) 组装为 { focus_id: [infos...] }，保证所有 focus_id 都存在键
    grouped: Dict[int, list] = {fid: [] for fid in focus_ids}
    for item in infos or []:
        fid = item.get("focus_id")
        if isinstance(fid, int) and fid in grouped:
            grouped[fid].append(item)

    return APIResponse(success=True, msg="", data=grouped)

# 9. del_info
@app.delete("/del_info")
async def del_info(info_id: str):
    result = await db_manager.delete_info(info_id)
    if result is not None:
        logger.info(f"info {info_id} deleted as user request")
        return APIResponse(success=True, msg="", data=None)
    else:
        return APIResponse(success=False, msg="信息删除失败", data=None)

# 10. info_stat
@app.get("/info_stat")
async def info_stat(focus_id: Optional[int] = None):
    """
    统计 infos 数量，按 focus_id 分组
    如果提供 focus_id，则只返回该 focus_id 的数量
    如果不提供 focus_id，则返回所有 focus_id 的数量
    返回格式：{focus_id: count}
    """
    result = await db_manager.count_infos_by_focus(focus_id=focus_id)
    if result is not None:
        return APIResponse(success=True, msg="", data=result)
    else:
        return APIResponse(success=False, msg="统计信息失败", data={})

# 11. read_info
class ReadInfoRequest(BaseModel):
    focuses: Optional[List[int]] = None
    per_focus_limit: Optional[int] = 50
    limit: Optional[int] = 20
    offset: Optional[int] = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    source_url: Optional[str] = None
    info_id: Optional[str] = None


@app.post("/read_info")
async def read_info(request: ReadInfoRequest):
    """
    按条件读取 infos：支持 focus 列表、时间范围、分页。
    返回符合条件的 infos 列表（按 created 降序）。
    """
    if request.per_focus_limit and request.limit and (request.per_focus_limit + request.limit) < 1:
        if not request.source_url and not request.info_id:
            return APIResponse(success=False, msg="per_focus_limit 和 limit 不能同时为0", data=[])
    
    infos = await db_manager.filter_infos(
        source_url=(request.source_url or None),
        id=(request.info_id or None),
        focus_ids=request.focuses or None,
        start_time=(request.start_time or None),
        end_time=(request.end_time or None),
        per_focus_limit=(request.per_focus_limit if request.per_focus_limit is not None else 50),
        limit=(request.limit if request.limit is not None else 20),
        offset=(request.offset if request.offset is not None else 0),
    )
    if infos is not None:
        return APIResponse(success=True, msg="", data=infos)
    else:
        return APIResponse(success=False, msg="查询信息失败", data=[])

# 12-15. local_proxies CRUD
@app.get("/list_local_proxies")
async def list_local_proxies():
    proxies = await db_manager.list_local_proxies()
    if proxies is not None:
        return APIResponse(success=True, msg="", data=proxies)
    else:
        return APIResponse(success=False, msg="获取代理列表失败", data=[])

@app.delete("/del_local_proxies")
async def del_local_proxies(proxy_id: int):
    result = await db_manager.delete_local_proxy(proxy_id)
    if result is not None:
        return APIResponse(success=True, msg="", data=None)
    else:
        return APIResponse(success=False, msg="代理删除失败", data=None)

@app.post("/add_local_proxies")
async def add_local_proxies(request: ProxyRequest):
    proxy_id = await db_manager.add_local_proxy(
        ip=request.ip,
        port=request.port,
        user=request.user or "",
        password=request.password or "",
        apply_to=request.apply_to or [],
        life_time=request.life_time or 0
    )
    
    if proxy_id is not None:
        return APIResponse(success=True, msg="", data=proxy_id)
    else:
        return APIResponse(success=False, msg="代理创建失败", data=None)

@app.put("/update_local_proxies")
async def update_local_proxies(proxy_id: int, request: ProxyRequest):
    result = await db_manager.update_local_proxy(
        proxy_id=proxy_id,
        ip=request.ip,
        port=request.port,
        user=request.user or "",
        password=request.password or "",
        apply_to=request.apply_to or [],
        life_time=request.life_time or 0
    )
    
    if result is not None:
        return APIResponse(success=True, msg="", data=proxy_id)
    else:
        return APIResponse(success=False, msg="代理更新失败", data=None)

# 16-19. kdl_proxies CRUD
@app.get("/list_kdl_proxies")
async def list_kdl_proxies():
    proxies = await db_manager.list_kdl_proxies()
    if proxies is not None:
        return APIResponse(success=True, msg="", data=proxies)
    else:
        return APIResponse(success=False, msg="获取KDL代理列表失败", data=[])

@app.delete("/del_kdl_proxies")
async def del_kdl_proxies(proxy_id: int):
    result = await db_manager.delete_kdl_proxy(proxy_id)
    if result is not None:
        return APIResponse(success=True, msg="", data=None)
    else:
        return APIResponse(success=False, msg="KDL代理删除失败", data=None)

@app.post("/add_kdl_proxies")
async def add_kdl_proxies(request: KdlProxyRequest):
    proxy_id = await db_manager.add_kdl_proxy(
        SECERT_ID=request.SECERT_ID,
        SIGNATURE=request.SIGNATURE,
        USER_NAME=request.USER_NAME,
        USER_PWD=request.USER_PWD,
        apply_to=request.apply_to or []
    )
    
    if proxy_id is not None:
        return APIResponse(success=True, msg="", data=proxy_id)
    else:
        return APIResponse(success=False, msg="KDL代理创建失败", data=None)

@app.put("/update_kdl_proxies")
async def update_kdl_proxies(proxy_id: int, request: KdlProxyRequest):
    result = await db_manager.update_kdl_proxy(
        proxy_id=proxy_id,
        SECERT_ID=request.SECERT_ID,
        SIGNATURE=request.SIGNATURE,
        USER_NAME=request.USER_NAME,
        USER_PWD=request.USER_PWD,
        apply_to=request.apply_to or []
    )
    
    if result is not None:
        return APIResponse(success=True, msg="", data=proxy_id)
    else:
        return APIResponse(success=False, msg="KDL代理更新失败", data=None)

# 24. list_config
@app.get("/list_config")
def list_config():
    load_runtime_overrides()
    return APIResponse(success=True, msg="", data=config)

# 25. reset_config
@app.get("/reset_config")
def reset_config():
    success = restore_default_config()
    if success:
        return APIResponse(success=True, msg="", data=None)
    else:
        return APIResponse(success=False, msg="配置重置失败", data=None)

# 26. update_config
@app.post("/update_config")
def update_config(config_updates: Dict[str, Any]):
    success = save_config(config_updates)
    if success:
        return APIResponse(success=True, msg="", data=None)
    else:
        return APIResponse(success=False, msg="配置保存失败", data=None)

@app.post("/user_notify")
async def user_notify(request: UserNotifyRequest):
    await prompt_bus.notify(request.code, request.params, request.timeout)
    return {"success": True}

@app.post("/user_prompt")
async def user_prompt(request: UserPromptRequest):
    result = await prompt_bus.request(
        code=request.code,
        params=request.params,
        timeout=request.timeout,
        actions=request.actions,
    )
    return {"result": result}

@app.post("/ws_ping")
async def ws_ping(request: FrontendPingRequest):
    timeout = request.timeout if request.timeout is not None else 3
    timeout = max(1, min(30, timeout))
    alive = await ping_manager.ping(timeout=timeout)
    return {"alive": alive}

# 28. ws_history
@app.get("/ws_history")
async def ws_history(limit: int = 10, offset: int = 0):
    records = await db_manager.list_ws_history(limit=limit, offset=offset)
    if records is not None:
        return APIResponse(success=True, msg="", data=records)
    else:
        return APIResponse(success=False, msg="获取消息历史失败", data=[])

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await hub.connect(ws)
    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            msg_type = data.get("type")
            if msg_type == "user_ack":
                await prompt_bus.resolve(
                    prompt_id=str(data.get("prompt_id", "")),
                    action_id=str(data.get("action_id", "")),
                )
            elif msg_type == "dong":
                await ping_manager.resolve(str(data.get("ping_id", "")))
            # 可扩展更多入站消息类型
    except WebSocketDisconnect:
        pass
    finally:
        await hub.disconnect(ws)
