from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..models import Conversation, Turn


BACKLINK_TEMPLATE = "[← Back to Conversation](Conversation.md)"


def render_turn(turn: Turn, conversation: Conversation, *, parent_name: str) -> str:
    lines = [f"# Turn {turn.turn_index}"]
    lines.append("")
    header = []
    if turn.created_at:
        header.append(turn.created_at.isoformat())
    if turn.role:
        header.append(turn.role.title())
    if turn.author and turn.author.lower() != turn.role.lower():
        header.append(f"as {turn.author}")
    if header:
        lines.append(" | ".join(header))
        lines.append("")

    lines.append(BACKLINK_TEMPLATE.replace("Conversation.md", parent_name))

    prev_turn = _get_turn(conversation, turn.turn_index - 1)
    next_turn = _get_turn(conversation, turn.turn_index + 1)

    if prev_turn or next_turn:
        if prev_turn:
            lines.append(f"← [[turn{prev_turn.turn_index:03d}_{prev_turn.mnemonic}.md]]")
        else:
            lines.append("← Start")
        if next_turn:
            lines.append(f"  [[turn{next_turn.turn_index:03d}_{next_turn.mnemonic}.md]] →")
        else:
            lines.append("  End →")

    lines.append("")

    lines.append(turn.content)
    lines.append("")

    if turn.links:
        lines.append("## Links")
        lines.append("")
        for link in turn.links:
            lines.append(f"- [{link.text}]({link.href})")
        lines.append("")

    lines.append("**Related:**")

    document = "\n".join(lines)
    if not document.endswith("\n"):
        document += "\n"
    return document


def _get_turn(conversation: Conversation, index: int) -> Optional[Turn]:
    if index < 1 or index > len(conversation.turns):
        return None
    return conversation.turns[index - 1]
