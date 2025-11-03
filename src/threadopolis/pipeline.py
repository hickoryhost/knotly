from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import Conversation
from .parsers import parse_html_export
from .utils import mnemonic_from_content
from .writers import OutputWriter, Plan
from .console import Console

console = Console()


class BuildResult:
    def __init__(self, conversation: Conversation, plan: Plan, writer: OutputWriter):
        self.conversation = conversation
        self.plan = plan
        self.writer = writer


def build_conversation(
    *,
    input_path: Path,
    output_dir: Path,
    title: Optional[str] = None,
    parent_name: str = "Conversation.md",
    force: bool = False,
    dry_run: bool = False,
    timezone: Optional[str] = None,
    by_title: bool = False,
    verbose: bool = False,
) -> BuildResult:
    if verbose:
        console.log(f"Loading conversation from {input_path} (html)")

    conversation = parse_html_export(
        input_path,
        timezone=timezone,
        title=title,
        by_title=by_title,
    )

    _stabilize_mnemonics(conversation)

    writer = OutputWriter(output_dir, parent_name=parent_name)
    plan = writer.plan(conversation)
    writer.prepare(plan, force=force)

    if verbose:
        console.log("Plan prepared:")
        console.print(plan.summary())

    if not dry_run:
        writer.write(plan)
        if verbose:
            console.log("Files written.")
    else:
        if verbose:
            console.log("Dry run complete; no files written.")

    return BuildResult(conversation, plan, writer)


def _stabilize_mnemonics(conversation: Conversation) -> None:
    seen = {}
    for turn in conversation.turns:
        base = turn.mnemonic or mnemonic_from_content(turn.content)
        suffix = ""
        counter = 0
        slug = base
        while slug in seen:
            counter += 1
            if counter <= 26:
                suffix = f"-{chr(ord('a') + counter - 1)}"
            else:
                suffix = f"-{counter:02d}"
            slug = base
            if len(base) + len(suffix) > 60:
                slug = base[: 60 - len(suffix)].rstrip("-")
            slug = f"{slug}{suffix}"
        seen[slug] = True
        turn.mnemonic = slug
