from __future__ import annotations

from pathlib import Path

from threadopolis.models import Conversation, Turn
from threadopolis.pipeline import build_conversation
from threadopolis.utils import ensure_timezone, parse_datetime


def read_folder(folder: Path) -> dict:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(folder.glob("*.md"))}


def test_html_build_matches_golden(tmp_path: Path):
    out_dir = tmp_path / "html"
    build_conversation(
        input_path=Path("examples/html/conversation.html"),
        output_dir=out_dir,
        force=True,
        by_title=True,
    )
    generated = read_folder(out_dir)
    golden = read_folder(Path("tests/golden/html"))
    assert generated == golden


def test_build_allows_non_empty_output_directory(tmp_path: Path):
    out_dir = tmp_path / "existing"
    out_dir.mkdir()
    marker = out_dir / "keep.txt"
    marker.write_text("do not remove", encoding="utf-8")

    build_conversation(
        input_path=Path("examples/html/conversation.html"),
        output_dir=out_dir,
        by_title=True,
    )

    generated = read_folder(out_dir)
    golden = read_folder(Path("tests/golden/html"))
    assert generated == golden
    assert marker.read_text(encoding="utf-8") == "do not remove"


def test_mnemonic_collision_suffixes():
    turns = [
        Turn(turn_index=i + 1, turn_id=str(i), role="user", author="Tester", content="Repeat text", raw_content=None, created_at=None, links=[], mnemonic="repeat-text")
        for i in range(3)
    ]
    convo = Conversation(
        title="Test",
        model=None,
        conversation_id=None,
        exported_at=None,
        participants=["Tester"],
        turns=turns,
    )
    from threadopolis.pipeline import _stabilize_mnemonics
    _stabilize_mnemonics(convo)
    mnemonics = [turn.mnemonic for turn in convo.turns]
    assert mnemonics[0] == "repeat-text"
    assert mnemonics[1] == "repeat-text-a"
    assert mnemonics[2].startswith("repeat-text")


def test_timezone_normalization():
    dt = parse_datetime("2024-03-01T10:00:00Z")
    normalized = ensure_timezone(dt, "Europe/London")
    assert normalized.tzinfo is not None
    assert normalized.isoformat().startswith("2024-03-01")


def test_html_parser_handles_nested_blocks(tmp_path: Path):
    html = """
    <html><body>
    <div class='conversation-turn' data-message-id='a1' data-role='user' data-author-name='Tester' data-timestamp='2024-01-01T00:00:00Z'>
        <div class='message-content'><p>Intro</p><table><tr><td>Cell</td></tr></table></div>
    </div>
    </body></html>
    """
    source = tmp_path / "nested.html"
    source.write_text(html, encoding="utf-8")
    result = build_conversation(
        input_path=source,
        output_dir=tmp_path / "out",
        force=True,
    )
    assert "Cell" in result.conversation.turns[0].content
