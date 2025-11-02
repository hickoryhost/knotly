from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional

from zoneinfo import ZoneInfo

STOP_CHARS_RE = re.compile(r"[^a-z0-9]+")


@dataclass
class SlugResult:
    slug: str
    collision_suffix: str = ""


def slugify(text: str, max_length: int = 60) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = STOP_CHARS_RE.sub("-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-+", "-", normalized)
    if len(normalized) > max_length:
        normalized = normalized[:max_length].rstrip("-")
    return normalized or "turn"


def words_from_markdown(markdown_text: str) -> Iterable[str]:
    stripped = re.sub(r"```.*?```", "", markdown_text, flags=re.DOTALL)
    stripped = re.sub(r"`[^`]+`", "", stripped)
    stripped = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", stripped)
    stripped = re.sub(r"[\W_]+", " ", stripped)
    for word in stripped.split():
        yield word


def mnemonic_from_content(content: str, word_limit: int = 6) -> str:
    words = list(words_from_markdown(content))
    mnemonic = " ".join(words[:word_limit])
    return slugify(mnemonic)


def ensure_timezone(dt: Optional[datetime], timezone: Optional[str]) -> Optional[datetime]:
    if dt is None:
        return None
    if timezone:
        try:
            tz = ZoneInfo(timezone)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            return dt.astimezone(tz)
        except Exception:  # pragma: no cover - fallback on error
            pass
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    value = value.strip()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
