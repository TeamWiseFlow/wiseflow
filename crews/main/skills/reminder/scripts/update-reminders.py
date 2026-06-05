#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRESERVED_FIELDS = {"status", "lastNotifiedAt", "snoozedUntil", "dismissedAt"}


def config_path() -> Path:
    return Path(
        os.environ.get(
            "OPENCLAW_CONFIG_PATH",
            Path.home() / ".openclaw" / "openclaw.json",
        )
    ).expanduser()


def workspace_path() -> Path:
    return Path(os.environ.get("MAIN_AGENT_WORKSPACE", Path.home() / ".openclaw" / "workspace-main")).expanduser()


def reminder_path() -> Path:
    return workspace_path() / "reminder.json"


def pending_followup_path() -> Path:
    return workspace_path() / "pending-followup.json"


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def load_config() -> dict[str, Any]:
    path = config_path()
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_existing_items(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in payload["items"]:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            result[item["id"]] = item
    return result


def merge_item(item: dict[str, Any], existing: dict[str, dict[str, Any]]) -> dict[str, Any]:
    previous = existing.get(item["id"], {})
    merged = dict(item)
    for field in PRESERVED_FIELDS:
        if field in previous:
            merged[field] = previous[field]
    if "createdAt" in previous:
        merged["createdAt"] = previous["createdAt"]
    else:
        merged["createdAt"] = item["updatedAt"]
    return merged


def main() -> None:
    config = load_config()
    now = datetime.now(timezone.utc).isoformat()
    agents = config.get("agents", {}).get("list", []) if config else []
    if not isinstance(agents, list):
        agents = []
    agent_ids = {agent.get("id") for agent in agents if isinstance(agent, dict) and agent.get("id")}
    bindings = config.get("bindings") if isinstance(config.get("bindings"), list) else []
    work_channels = {"feishu", "wecom"}

    def has_work_binding(agent_id: str) -> bool:
        return any(
            isinstance(binding, dict)
            and binding.get("agentId") == agent_id
            and isinstance(binding.get("match"), dict)
            and binding["match"].get("channel") in work_channels
            for binding in bindings
        )

    items: list[dict[str, Any]] = []
    internal_count = len([agent_id for agent_id in agent_ids if agent_id != "main"])
    if internal_count > 3:
        items.append({
            "id": "work-channel-needed-internal-team",
            "type": "work-channel",
            "severity": "suggestion",
            "status": "open",
            "title": "建议启用工作 channel",
            "message": "内部 crew 数量已经较多，建议为关键成员配置 Feishu 或 WeCom。",
            "reason": "internal crew count excluding main is greater than 3",
            "updatedAt": now,
        })
    if not has_work_binding("it-engineer"):
        items.append({
            "id": "it-engineer-no-work-binding",
            "type": "work-channel",
            "severity": "info",
            "status": "open",
            "title": "IT Engineer 尚无工作 channel",
            "message": "首次配置工作 channel 时，建议顺手给 IT Engineer 也配置 direct binding。",
            "reason": "it-engineer has no Feishu/WeCom binding",
            "updatedAt": now,
        })
    if "hrbp" in agent_ids and not has_work_binding("hrbp"):
        items.append({
            "id": "hrbp-no-work-binding",
            "type": "work-channel",
            "severity": "info",
            "status": "open",
            "title": "HRBP 尚无工作 channel",
            "message": "HRBP 已启用但没有 Feishu/WeCom binding，建议配置。",
            "reason": "hrbp enabled without work binding",
            "updatedAt": now,
        })

    if pending_followup_path().exists():
        items.append({
            "id": "pending-gateway-restart-followup",
            "type": "followup",
            "severity": "warning",
            "status": "open",
            "title": "Gateway 重启后待确认",
            "message": "存在 Gateway restart followup，请确认服务和 channel binding 是否恢复正常。",
            "reason": "pending-followup.json exists",
            "updatedAt": now,
        })

    path = reminder_path()
    existing = load_existing_items(path)
    merged_items = [merge_item(item, existing) for item in items]
    output = {"version": 1, "updatedAt": now, "items": merged_items}
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, output)
    print(json.dumps({"reminderPath": str(path), "itemCount": len(merged_items)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
