from __future__ import annotations

from ..models import Conversation


def render_parent(conversation: Conversation, *, parent_name: str) -> str:
    lines = [f"# {conversation.title}"]
    lines.append("")
    lines.append("## Turns")
    lines.append("")
    for turn in conversation.turns:
        filename = f"turn{turn.turn_index:03d}_{turn.mnemonic}.md"
        lines.append(f"-[[{filename}]]")
    lines.append("")
    return "\n".join(lines).strip() + "\n"
