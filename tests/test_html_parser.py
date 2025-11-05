from __future__ import annotations

from pathlib import Path

from threadopolis.parsers.html_input import parse_html_export


def test_collect_text_preserves_ordered_list_paragraphs(tmp_path: Path) -> None:
    html = """
    <div class=\"conversation-turn\" data-role=\"assistant\" data-author-name=\"GPT\">
      <div class=\"message-content\">
        <ol>
          <li>
            <p>Day 1-2:</p>
            <p>Start by softening the wax.</p>
          </li>
          <li>
            <p>Day 3-4:</p>
            <p>Apply gentle heat.</p>
          </li>
        </ol>
      </div>
    </div>
    """

    html_path = tmp_path / "sample.html"
    html_path.write_text(html, encoding="utf-8")

    conversation = parse_html_export(html_path)

    expected = "\n".join(
        [
            "1. Day 1-2:",
            "    ",
            "    Start by softening the wax.",
            "2. Day 3-4:",
            "    ",
            "    Apply gentle heat.",
        ]
    )

    assert conversation.turns[0].content == expected
