from __future__ import annotations

from datetime import datetime
from typing import Iterable

from ..models import Conversation


def render_parent(conversation: Conversation, *, parent_name: str) -> str:
    lines = [f"# {conversation.title}"]
    lines.append("")
    lines.extend(_metadata_block(conversation))
    lines.append("")
    lines.append("## Turns")
    lines.append("")
    for turn in conversation.turns:
        filename = f"turn{turn.turn_index:03d}_{turn.mnemonic}.md"
        lines.append(f"- [Turn {turn.turn_index}]({filename})")
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def _metadata_block(conversation: Conversation) -> Iterable[str]:
    yield "**Model:** " + (conversation.model or "unknown")
    yield "**Conversation ID:** " + (conversation.conversation_id or "n/a")
    if conversation.exported_at:
        yield "**Exported:** " + _format_datetime(conversation.exported_at)
    if conversation.participants:
        yield "**Participants:** " + ", ".join(conversation.participants)


def _format_datetime(dt: datetime) -> str:
    return dt.isoformat()
