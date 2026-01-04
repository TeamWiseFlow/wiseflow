import asyncio
import json
import time
import uuid
from typing import Dict, Set, Optional, List
from fastapi import WebSocket


class WSHub:
    """Simple broadcast hub for single-user local app.

    Holds active WebSocket connections and supports broadcast to all.
    """

    def __init__(self) -> None:
        self.connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self.connections.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self.connections.discard(ws)

    async def broadcast(self, data: dict) -> None:
        message = json.dumps(data, ensure_ascii=False)
        async with self._lock:
            conns = list(self.connections)
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                await self.disconnect(ws)


hub = WSHub()


class PromptResult:
    def __init__(self) -> None:
        # Future resolves to action_id string
        self.future: asyncio.Future[str] = asyncio.get_event_loop().create_future()


class PingResult:
    def __init__(self) -> None:
        loop = asyncio.get_event_loop()
        self.future: asyncio.Future[None] = loop.create_future()


class PromptBus:
    """Manages prompt lifecycle for user-required confirmations via WS.

    - request(): broadcast prompt and await user_ack
    - resolve(): fulfill the waiting future when user acknowledges
    - notify(): send non-blocking notifications
    """

    def __init__(self, ws_hub: WSHub, db_manager = None) -> None:
        self.hub = ws_hub
        self.db_manager = db_manager
        self._pending: Dict[str, PromptResult] = {}
        self._lock = asyncio.Lock()

    async def notify(self, code: int, params: List[str] = None, timeout: int = 30) -> None:
        payload = {
            "type": "notify",
            "code": code,
            "params": params or [],
            "timeout": timeout,
            "ts": time.time(),
        }
        await self.hub.broadcast(payload)
        if self.db_manager:
            try:
                await self.db_manager.add_ws_history(
                    type="notify",
                    code=code,
                    params=params or [],
                    timeout=timeout,
                    ts=payload["ts"],
                )
            except Exception:
                pass

    async def request(
        self,
        code: int,
        params: List[str] = None,
        timeout: int = 30,
        actions: Optional[List[dict]] = None,
    ) -> Optional[str]:

        prompt_id = uuid.uuid4().hex
        result = PromptResult()
        async with self._lock:
            self._pending[prompt_id] = result

        payload = {
            "type": "prompt",
            "prompt_id": prompt_id,
            "code": code,
            "params": params or [],
            "actions": actions or [{"id": "done", "label": "我已完成"}],
            "timeout": timeout,
            "ts": time.time(),
        }
        await self.hub.broadcast(payload)
        if self.db_manager:
            try:
                await self.db_manager.add_ws_history(
                    type="prompt",
                    prompt_id=prompt_id,
                    code=code,
                    params=params or [],
                    actions=payload["actions"],
                    timeout=timeout,
                    ts=payload["ts"],
                )
            except Exception:
                pass

        try:
            choice = await asyncio.wait_for(result.future, timeout=timeout)
            resolved_payload = {
                "type": "prompt_resolved",
                "prompt_id": prompt_id,
                "action_id": choice,
                "ts": time.time(),
            }
            await self.hub.broadcast(resolved_payload)
            if self.db_manager:
                try:
                    await self.db_manager.add_ws_history(
                        type="prompt_resolved",
                        prompt_id=prompt_id,
                        action_id=choice,
                        ts=resolved_payload["ts"],
                    )
                except Exception:
                    pass
            return choice
        except asyncio.TimeoutError:
            return None
        except asyncio.CancelledError:
            return None
        finally:
            async with self._lock:
                self._pending.pop(prompt_id, None)

    async def resolve(self, prompt_id: str, action_id: str) -> None:
        async with self._lock:
            pr = self._pending.get(prompt_id)
        if pr and not pr.future.done():
            pr.future.set_result(action_id)


class PingManager:
    """Lightweight ping/pong helper to ensure frontend WS presence."""

    def __init__(self, ws_hub: WSHub) -> None:
        self.hub = ws_hub
        self._pending: Dict[str, PingResult] = {}
        self._lock = asyncio.Lock()

    async def ping(self, timeout: int = 3) -> bool:
        timeout = max(1, timeout)
        ping_id = uuid.uuid4().hex
        result = PingResult()
        async with self._lock:
            self._pending[ping_id] = result

        payload = {
            "type": "ding",
            "ping_id": ping_id,
            "timeout": timeout,
            "ts": time.time(),
        }
        await self.hub.broadcast(payload)

        try:
            await asyncio.wait_for(result.future, timeout=timeout)
            return True
        except (asyncio.TimeoutError, asyncio.CancelledError):
            return False
        finally:
            async with self._lock:
                self._pending.pop(ping_id, None)

    async def resolve(self, ping_id: str) -> None:
        async with self._lock:
            result = self._pending.get(ping_id)
        if result and not result.future.done():
            result.future.set_result(None)


# prompt_bus = PromptBus(hub)
