"""relay_sign.py — client 侧调用 relay sign 服务的统一入口（Python）

平台规则：relay 只计算签名，
实际平台调用（登录 / 抓取 / 互动 / 上传 / 发布）**必须 client 端完成**。本模块供
其他平台的 Python skill 共用。RELAY_BASE_URL + OFB_KEY 由 entrypoint 从 daemon.env 注入。

"""

import json
import os
from typing import Any

import requests

# 默认指向现有官方 relay，接入凭证由运行层配置。
# 仅当用户自建 relay 时才需要在 daemon.env 覆盖 RELAY_BASE_URL。
RELAY_BASE_URL = os.environ.get(
    "RELAY_BASE_URL", "https://relay.openclaw-for-business.com"
)
_TIMEOUT = 30


class RelaySignError(RuntimeError):
    def __init__(self, code: str, status: int | None = None):
        self.code = code
        self.status = status
        super().__init__(code)


def _ofb_key() -> str:
    key = os.environ.get("OFB_KEY")
    if not key:
        raise RuntimeError(
            "当前功能需要 relay 服务，OFB_KEY 尚未配置。请到 https://openclaw-for-business.com/ 查看接入说明，再通过 xiaobei-runtime 的私有配置流程继续。"
        )
    return key


def _post(path: str, body: dict) -> Any:
    resp = requests.post(
        f"{RELAY_BASE_URL}{path}",
        headers={"Content-Type": "application/json", "X-OFB-Key": _ofb_key()},
        json=body,
        timeout=_TIMEOUT,
    )
    try:
        env = resp.json()
    except ValueError as exc:
        raise RelaySignError("SIGN_UNAVAILABLE", resp.status_code) from exc
    if not isinstance(env, dict):
        raise RelaySignError("SIGN_UNAVAILABLE", resp.status_code)
    if not resp.ok or not env.get("success"):
        code = env.get("error")
        if not isinstance(code, str) or not code.isupper() or len(code) > 40:
            code = "SIGN_UNAVAILABLE"
        raise RelaySignError(code, resp.status_code)
    if "data" not in env:
        raise RelaySignError("INVALID_RELAY_RESPONSE", resp.status_code)
    return env["data"]


def douyin_v2(profile: str, operation: str, inputs: dict) -> dict:
    """Request per-operation dynamic fields; platform traffic stays on the client."""
    data = _post(
        "/api/v1/sign/douyin/v2",
        {"version": 2, "profile": profile, "operation": operation, "inputs": inputs},
    )
    if not isinstance(data, dict):
        raise RuntimeError("relay douyin v2 returned invalid data")
    return data


def douyin_health() -> dict:
    key = os.environ.get("OFB_KEY")
    if not key:
        raise RelaySignError("OFB_KEY_MISSING")
    try:
        response = requests.get(
            f"{RELAY_BASE_URL}/api/v1/sign/douyin/v2/health",
            headers={"X-OFB-Key": key},
            timeout=_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise RelaySignError("SIGN_UNAVAILABLE") from exc
    try:
        envelope = response.json()
    except ValueError as exc:
        raise RelaySignError("SIGN_UNAVAILABLE", response.status_code) from exc
    if not isinstance(envelope, dict):
        raise RelaySignError("INVALID_RELAY_RESPONSE", response.status_code)
    if not response.ok or not envelope.get("success"):
        code = envelope.get("error")
        raise RelaySignError(
            code if isinstance(code, str) and code.isupper() else "SIGN_UNAVAILABLE",
            response.status_code,
        )
    data = envelope.get("data")
    if not isinstance(data, dict):
        raise RelaySignError("INVALID_RELAY_RESPONSE")
    return {
        k: data[k]
        for k in ("version", "ready", "materialsLoaded", "profiles", "operations")
        if k in data
    }
