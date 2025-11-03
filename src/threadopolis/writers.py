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

    def prepare(self, plan: "Plan", force: bool = False) -> None:
        # Ensure all parent directories exist before attempting to write files.
        for path in plan.files:
            path.parent.mkdir(parents=True, exist_ok=True)

        if force:
            return

        collisions = [path for path in plan.files if path.exists()]
        if collisions:
            formatted = ", ".join(str(path) for path in collisions)
            raise FileExistsError(
                "Output would overwrite existing files: "
                f"{formatted}. Use --force to overwrite these files."
            )

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
