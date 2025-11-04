from __future__ import annotations

from datetime import datetime
from ..models import Conversation, Turn


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
