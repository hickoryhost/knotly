from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Link:
    text: str
    href: str


@dataclass
class Turn:
    turn_index: int
    turn_id: Optional[str]
    role: str
    author: Optional[str]
    content: str
    raw_content: Optional[str]
    created_at: Optional[datetime]
    links: List[Link] = field(default_factory=list)
    mnemonic: str = ""


@dataclass
class Conversation:
    title: str
    model: Optional[str]
    conversation_id: Optional[str]
    exported_at: Optional[datetime]
    participants: List[str]
    turns: List[Turn]
