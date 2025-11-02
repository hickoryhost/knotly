from __future__ import annotations

import json
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    import orjson  # type: ignore
except ImportError:  # pragma: no cover - fallback
    orjson = None

from ..models import Conversation, Link, Turn
from ..utils import ensure_timezone, mnemonic_from_content, parse_datetime


def _load_json(path: Path) -> Any:
    raw = path.read_bytes()
    if orjson is not None:
        try:
            return orjson.loads(raw)
        except Exception:
            pass
    return json.loads(raw.decode("utf-8"))


def _extract_messages(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "messages" in payload and isinstance(payload["messages"], list):
            return payload["messages"]
        if "mapping" in payload and isinstance(payload["mapping"], dict):
            ordered = OrderedDict()
            for key, node in payload["mapping"].items():
                if not isinstance(node, dict):
                    continue
                message = node.get("message")
                if not message:
                    continue
                create_time = message.get("create_time")
                ordered[(create_time or 0, key)] = message
            return [m for _, m in sorted(ordered.items())]
    raise ValueError("Unsupported JSON export format")


def parse_json_export(path: Path, *, timezone: Optional[str] = None, title: Optional[str] = None) -> Conversation:
    payload = _load_json(path)
    messages = _extract_messages(payload)

    meta = payload if isinstance(payload, dict) else {}
    model = meta.get("model_slug") or meta.get("model") if isinstance(meta, dict) else None
    conversation_id = meta.get("conversation_id") if isinstance(meta, dict) else None
    exported_at = None
    if isinstance(meta, dict):
        exported_at = parse_datetime(meta.get("exported_at")) or parse_datetime(meta.get("create_time"))

    participants: List[str] = []
    turns: List[Turn] = []

    for idx, message in enumerate(messages, start=1):
        role = message.get("author", {}).get("role") if isinstance(message.get("author"), dict) else message.get("role")
        author_name = message.get("author", {}).get("name") if isinstance(message.get("author"), dict) else message.get("author_name")
        content = _normalize_content(message.get("content"))
        created_raw = message.get("create_time") or message.get("created_at") or message.get("timestamp")
        created_at = parse_datetime(created_raw)
        created_at = ensure_timezone(created_at, timezone)
        message_id = message.get("id") or message.get("message_id")

        if author_name:
            participants.append(author_name)
        elif role:
            participants.append(role)

        links = [Link(text=link.get("text", link.get("href", "")), href=link.get("href", ""))
                 for link in _extract_links(message)]

        mnemonic = mnemonic_from_content(content)

        turns.append(
            Turn(
                turn_index=idx,
                turn_id=message_id,
                role=role or "unknown",
                author=author_name,
                content=content,
                raw_content=message.get("content"),
                created_at=created_at,
                links=links,
                mnemonic=mnemonic,
            )
        )

    participants = list(OrderedDict.fromkeys([p for p in participants if p]))

    conversation_title = title or meta.get("title") or meta.get("conversation_title") or "Conversation"

    return Conversation(
        title=conversation_title,
        model=model,
        conversation_id=conversation_id,
        exported_at=ensure_timezone(exported_at, timezone) if exported_at else None,
        participants=participants,
        turns=turns,
    )


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        if content.get("content_type") == "text" and "parts" in content:
            parts = content.get("parts")
            if isinstance(parts, list):
                return "\n\n".join(str(part) for part in parts if part)
        if "text" in content and isinstance(content["text"], str):
            return content["text"]
    if isinstance(content, list):
        return "\n\n".join(_normalize_content(item) for item in content if item)
    return ""


def _extract_links(message: Dict[str, Any]) -> List[Dict[str, str]]:
    links: List[Dict[str, str]] = []
    content = message.get("content")
    if isinstance(content, dict):
        if "links" in content and isinstance(content["links"], list):
            for link in content["links"]:
                if isinstance(link, dict) and link.get("href"):
                    links.append({"text": link.get("text", link.get("href")), "href": link.get("href")})
        if "parts" in content and isinstance(content["parts"], list):
            for part in content["parts"]:
                if isinstance(part, dict) and part.get("content_type") == "link":
                    href = part.get("href")
                    if href:
                        links.append({"text": part.get("text", href), "href": href})
    return links
