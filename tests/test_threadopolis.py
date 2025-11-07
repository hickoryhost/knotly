from __future__ import annotations

from pathlib import Path

from threadopolis.models import Conversation, Turn
from threadopolis.pipeline import build_conversation
from threadopolis.renderers.parent import render_parent
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


def test_parent_skips_duplicate_conversation_heading():
    convo = Conversation(
        title="Conversation",
        model=None,
        conversation_id=None,
        exported_at=None,
        participants=[],
        turns=[
            Turn(
                turn_index=1,
                turn_id="t1",
                role="user",
                author="Tester",
                content="Hello",
                raw_content=None,
                created_at=None,
                links=[],
                mnemonic="hello",
            )
        ],
    )

    rendered = render_parent(convo, parent_name="Conversation.md")

    assert "# Conversation" not in rendered
    lines = rendered.splitlines()
    assert lines[0] == "## Turns"
    assert lines[2] == "-[[turn001_hello.md]]"


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
    <div class='conversation-turn' data-message-id='a1' data-role='user' data-turn='user' data-author-name='Tester' data-timestamp='2024-01-01T00:00:00Z'>
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
    turn = result.conversation.turns[0]
    assert "Cell" in turn.content
    assert turn.data_turn == "user"


def test_turn_content_preserves_line_breaks(tmp_path: Path):
    html = """
    <html><body>
    <div class='conversation-turn' data-message-id='b1' data-role='user' data-turn='user' data-author-name='Tester'>
        <div class='message-content'>
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
            <ul>
                <li>List item one.</li>
                <li>List item two.</li>
            </ul>
            <ol>
                <li>Numbered item one.</li>
                <li>Numbered item two.</li>
            </ol>
            <p>Final line.</p>
        </div>
    </div>
    </body></html>
    """
    source = tmp_path / "linebreaks.html"
    source.write_text(html, encoding="utf-8")

    result = build_conversation(
        input_path=source,
        output_dir=tmp_path / "out-lines",
        force=True,
    )

    expected = """First paragraph.\n\nSecond paragraph.\n\n- List item one.\n- List item two.\n\n1. Numbered item one.\n2. Numbered item two.\n\nFinal line."""
    turn = result.conversation.turns[0]
    assert turn.content == expected
    assert turn.data_turn == "user"
