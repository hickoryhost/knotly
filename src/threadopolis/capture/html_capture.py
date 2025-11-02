from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..parsers.html_input import parse_html_export
from ..models import Conversation


def html_to_json(
    *,
    html_path: Path,
    out_json: Path,
    timezone: Optional[str] = None,
    title: Optional[str] = None,
    by_title: bool = False,
) -> Path:
    """Parse a saved ChatGPT-style HTML export and write a normalized JSON conversation."""
    conversation = parse_html_export(
        html_path,
        timezone=timezone,
        title=title,
        by_title=by_title,
    )

    payload = _conversation_to_payload(conversation)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, ensure_ascii=False)
    out_json.write_text(serialized + "\n", encoding="utf-8")
    return out_json


def _conversation_to_payload(conversation: Conversation) -> Dict[str, Any]:
    messages = []
    for turn in conversation.turns:
        content: Dict[str, Any] = {
            "content_type": "text",
            "parts": [turn.content] if turn.content else [],
        }
        if turn.links:
            content["links"] = [
                {"text": link.text, "href": link.href}
                for link in turn.links
            ]

        author: Dict[str, Any] = {"role": turn.role or "unknown"}
        if turn.author:
            author["name"] = turn.author

        message: Dict[str, Any] = {
            "id": turn.turn_id or f"turn-{turn.turn_index}",
            "author": author,
            "content": content,
        }
        if turn.created_at:
            message["create_time"] = turn.created_at.isoformat()

        messages.append(message)

    payload: Dict[str, Any] = {
        "title": conversation.title,
        "model": conversation.model,
        "conversation_id": conversation.conversation_id,
        "exported_at": conversation.exported_at.isoformat() if conversation.exported_at else None,
        "participants": conversation.participants,
        "messages": messages,
    }
    return payload
