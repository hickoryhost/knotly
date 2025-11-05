from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional

from ..models import Conversation, Link, Turn
from ..utils import ensure_timezone, mnemonic_from_content, parse_datetime


@dataclass
class Node:
    tag: str
    attrs: Dict[str, str]
    parent: Optional["Node"] = None
    children: List["Node"] = field(default_factory=list)
    _contents: List[object] = field(default_factory=list)

    def add_child(self, child: "Node") -> None:
        self.children.append(child)
        self._contents.append(child)

    def add_text(self, text: str) -> None:
        if text:
            self._contents.append(text)

    def iter_text(self) -> List[str]:
        pieces: List[str] = []
        for item in self._contents:
            if isinstance(item, str):
                pieces.append(item)
            elif isinstance(item, Node):
                pieces.extend(item.iter_text())
        return pieces

    def find_all(self, predicate) -> List["Node"]:
        matches = []
        if predicate(self):
            matches.append(self)
        for child in self.children:
            matches.extend(child.find_all(predicate))
        return matches

    def find_first(self, predicate) -> Optional["Node"]:
        if predicate(self):
            return self
        for child in self.children:
            found = child.find_first(predicate)
            if found:
                return found
        return None

    def get_attribute(self, name: str) -> Optional[str]:
        return self.attrs.get(name)


class SoupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node(tag="document", attrs={})
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attr_dict = {name: value for name, value in attrs}
        node = Node(tag=tag, attrs=attr_dict, parent=self.stack[-1])
        self.stack[-1].add_child(node)
        self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        while len(self.stack) > 1:
            node = self.stack.pop()
            if node.tag == tag:
                break

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.stack[-1].add_text(data)


def parse_html_export(path: Path, *, timezone: Optional[str] = None, title: Optional[str] = None, by_title: bool = False) -> Conversation:
    parser = SoupParser()
    parser.feed(path.read_text(encoding="utf-8"))

    conversation_title = title
    if not conversation_title and by_title:
        title_node = parser.root.find_first(lambda node: node.tag == "title")
        if title_node:
            conversation_title = "".join(title_node.iter_text()).strip()
    conversation_title = conversation_title or "Conversation"

    participants: List[str] = []
    turns: List[Turn] = []

    def is_message(node: Node) -> bool:
        if node.tag.lower() not in {"div", "article", "section"}:
            return False
        attrs = node.attrs
        if any(key.startswith("data-") for key in attrs):
            if attrs.get("data-message-id") or attrs.get("data-role") or attrs.get("data-author-role"):
                return True
        class_attr = attrs.get("class", "")
        return "conversation-turn" in class_attr.split()

    message_nodes = parser.root.find_all(is_message)

    if not message_nodes:
        def is_text_base(node: Node) -> bool:
            return node.tag.lower() == "div" and "text-base" in node.attrs.get("class", "").split()
        message_nodes = parser.root.find_all(is_text_base)

    for idx, node in enumerate(message_nodes, start=1):
        role = node.get_attribute("data-role") or node.get_attribute("data-author-role")
        if not role:
            role = node.attrs.get("class", "unknown").split()[0] if node.attrs.get("class") else "unknown"
        author = node.get_attribute("data-author-name")
        if not author and role:
            author = role.title()

        time_text = node.get_attribute("data-timestamp") or node.get_attribute("data-created")
        created_at = ensure_timezone(parse_datetime(time_text), timezone)

        content_node = node.find_first(lambda n: n is not node and n.tag.lower() == "div" and "message-content" in n.attrs.get("class", "").split())
        if not content_node:
            content_node = node
        content = _collect_text(content_node).strip()

        links = []
        link_nodes = content_node.find_all(lambda n: n.tag.lower() == "a" and n.get_attribute("href"))
        for link in link_nodes:
            links.append(Link(text=_collect_text(link).strip(), href=link.get_attribute("href") or ""))

        mnemonic = mnemonic_from_content(content)
        turn_id = node.get_attribute("data-message-id") or node.get_attribute("id")

        if author:
            participants.append(author)

        turns.append(
            Turn(
                turn_index=idx,
                turn_id=turn_id,
                role=role or "unknown",
                author=author,
                content=content,
                raw_content=None,
                created_at=created_at,
                links=links,
                mnemonic=mnemonic,
            )
        )

    participants = list(dict.fromkeys([p for p in participants if p]))

    return Conversation(
        title=conversation_title,
        model=None,
        conversation_id=None,
        exported_at=None,
        participants=participants,
        turns=turns,
    )


BLOCK_ELEMENTS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "div",
    "dl",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "noscript",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tbody",
    "thead",
    "tfoot",
    "tr",
    "ul",
}

LINE_BREAK_ELEMENTS = {"br"}
DOUBLE_BREAK_ELEMENTS = {
    "article",
    "aside",
    "blockquote",
    "div",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "ul",
}


def _collect_text(node: Node) -> str:
    def append_newlines(target: List[str], count: int) -> None:
        if count <= 0:
            return
        existing = 0
        idx = len(target) - 1
        while idx >= 0:
            segment = target[idx]
            if segment and set(segment) == {"\n"}:
                existing += len(segment)
                idx -= 1
                continue
            break
        needed = max(0, count - existing)
        if needed:
            target.append("\n" * needed)

    def render(current: Node) -> str:
        pieces: List[str] = []
        for item in current._contents:
            if isinstance(item, str):
                pieces.append(item)
                continue

            tag = item.tag.lower()

            if tag in LINE_BREAK_ELEMENTS:
                append_newlines(pieces, 1)
                continue

            rendered_child = render(item)

            if tag == "li":
                parent = item.parent
                prefix = "- "
                if parent and parent.tag.lower() == "ol":
                    position = 0
                    found = False
                    for child in parent.children:
                        if isinstance(child, Node) and child.tag.lower() == "li":
                            position += 1
                            if child is item:
                                prefix = f"{position}. "
                                found = True
                                break
                    if not found:
                        prefix = "1. "
                item_text = rendered_child.strip()
                if item_text:
                    append_newlines(pieces, 1)
                    lines = item_text.splitlines()
                    first_line = lines[0]
                    pieces.append(prefix + first_line)
                    if len(lines) > 1:
                        indent = " " * max(len(prefix), 4)
                        continuation_lines = []
                        for line in lines[1:]:
                            if line.strip():
                                continuation_lines.append(indent + line)
                            else:
                                continuation_lines.append("")
                        pieces.append("\n" + "\n".join(continuation_lines))
                append_newlines(pieces, 1)
                continue

            if tag in BLOCK_ELEMENTS:
                block_text = rendered_child.strip()
                if block_text:
                    newline_count = 2 if tag in DOUBLE_BREAK_ELEMENTS else 1
                    append_newlines(pieces, newline_count)
                    pieces.append(block_text)
                    append_newlines(pieces, newline_count)
                else:
                    append_newlines(pieces, 1 if tag not in DOUBLE_BREAK_ELEMENTS else 2)
                continue

            pieces.append(rendered_child)

        return "".join(pieces)

    text = render(node)

    # Collapse runs of more than two newlines while keeping intentional blank lines.
    normalized_lines: List[str] = []
    newline_run = 0
    for char in text:
        if char == "\n":
            newline_run += 1
            if newline_run <= 2:
                normalized_lines.append(char)
        else:
            newline_run = 0
            normalized_lines.append(char)

    normalized = "".join(normalized_lines)
    return normalized.strip()
