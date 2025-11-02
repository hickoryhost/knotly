from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from .models import Conversation
from .renderers.parent import render_parent
from .renderers.turn import render_turn


class Plan:
    def __init__(self, files: Dict[Path, str]):
        self.files = files

    def summary(self) -> str:
        return "\n".join(f"{path} ({len(content)} bytes)" for path, content in self.files.items())


class OutputWriter:
    def __init__(self, output_dir: Path, parent_name: str = "Conversation.md"):
        self.output_dir = output_dir
        self.parent_name = parent_name

    def prepare(self, force: bool = False) -> None:
        if self.output_dir.exists():
            existing = [p for p in self.output_dir.iterdir() if p.name != ".DS_Store"]
            if existing and not force:
                raise FileExistsError(f"Output directory {self.output_dir} is not empty; use --force to overwrite")
        else:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def plan(self, conversation: Conversation) -> Plan:
        files: Dict[Path, str] = {}
        parent_content = render_parent(conversation, parent_name=self.parent_name)
        files[self.output_dir / self.parent_name] = parent_content
        for turn in conversation.turns:
            filename = f"turn{turn.turn_index:03d}_{turn.mnemonic}.md"
            content = render_turn(turn, conversation, parent_name=self.parent_name)
            files[self.output_dir / filename] = content
        return Plan(files)

    def write(self, plan: Plan) -> None:
        for path, content in plan.files.items():
            path.write_text(content, encoding="utf-8", newline="\n")


def build_files(conversation: Conversation, output_dir: Path, parent_name: str = "Conversation.md") -> Tuple[Plan, OutputWriter]:
    writer = OutputWriter(output_dir, parent_name=parent_name)
    plan = writer.plan(conversation)
    return plan, writer
