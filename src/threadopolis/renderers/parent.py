from __future__ import annotations

from pathlib import Path

from ..models import Conversation


def render_parent(conversation: Conversation, *, parent_name: str) -> str:
    lines = []

    title = (conversation.title or "").strip()
    parent_stem = Path(parent_name).stem if parent_name else ""

    if title and title.casefold() != parent_stem.casefold():
        lines.append(f"# {title}")
        lines.append("")

    lines.append("## Turns")
    lines.append("")

    for turn in conversation.turns:
        filename = f"turn{turn.turn_index:03d}_{turn.mnemonic}.md"
        lines.append(f"-[[{filename}]]")
    lines.append("")
    return "\n".join(lines).strip() + "\n"
