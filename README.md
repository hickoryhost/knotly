# Threadopolis

Threadopolis converts long-form AI assistant conversations into Obsidian-friendly markdown bundles. It ingests ChatGPT/GPT-5 JSON exports or saved HTML pages, produces a parent conversation index, and splits every turn into a deterministic `turnNNN_<mnemonic>.md` file with backlinks, navigation, and metadata. A Playwright-assisted capture flow is also included for advanced users who want to snapshot live conversations.

## Features

- Deterministic parent index with model, conversation, and participant metadata.
- Per-turn files with backlinks, previous/next navigation, timestamp headers, and space for future related links.
- Filename mnemonics generated from the first content words with collision-safe suffixes.
- JSON and HTML parsers with timezone normalization.
- Optional Playwright capture utility for harvesting conversations directly from a logged-in browser session.
- Thorough pytest suite with golden-file snapshots and parser edge cases.

## Quickstart

Threadopolis is pure Python 3.11+ with no external dependencies required for the core build flow.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The package exposes a console script at `bin/threadopolis`. You can also invoke the module directly:

```bash
python -m threadopolis.cli build --help
```

## CLI Usage

### Build a bundle from a JSON export

```bash
bin/threadopolis build \
  --in examples/json/chatgpt_sample.json \
  --format json \
  --out output/json-sample
```

### Build from a saved HTML page

```bash
bin/threadopolis build \
  --in examples/html/conversation.html \
  --format html \
  --out output/html-sample \
  --by-title
```

### Dry run a build

```bash
bin/threadopolis build --in export.json --format json --out my-convo --dry-run -v
```

### Capture a live conversation to JSON

```bash
bin/threadopolis capture \
  --user-data-dir ~/.config/chromium-profile \
  --conv-url "https://chat.openai.com/c/abc123" \
  --out-json capture.json
```

> **Tip:** The capture command requires a working Playwright installation (`pip install playwright` + `playwright install chromium`) and a logged-in profile directory.

## Library Usage

```python
from pathlib import Path
from threadopolis import build_conversation

result = build_conversation(
    input_path=Path("conversation.json"),
    input_format="json",
    output_dir=Path("vault/My Conversation"),
    force=True,
)
print(f"Wrote {len(result.plan.files)} markdown files")
```

## Examples

The `examples/` folder contains:

- `json/chatgpt_sample.json` and the corresponding generated bundle in `json/output/`.
- `html/conversation.html` and its generated bundle in `html/output/`.

These are used in snapshot tests and act as small reference exports.

## Testing

```bash
pytest
```

All golden snapshots live in `tests/golden/`. To update them, regenerate the example outputs (see `examples/` instructions) and copy the files over.

## Obsidian Tips

- Place the generated output folder directly inside your vault or use `--vault-root /path/to/vault` to let Threadopolis do it for you.
- The parent index (`Conversation.md` by default) links to every turn. Use Obsidian’s graph view to visualize the conversation links.
- Each turn file reserves a **Related:** section for future semantic cross-links or manual notes.

## Limitations & Roadmap

- HTML parsing targets common ChatGPT export structures; extremely custom DOMs may need tweaks.
- Semantic link inference, embeddings, and Obsidian plugin integrations are reserved for future work (`--infer-links` flag).
- Playwright capture is optional and relies on local browser state; understand the security implications of reusing logged-in profiles.

## Headless Capture Safety Notes

Running Playwright against your logged-in browser profile keeps all data on disk but still grants code automation access to that profile. Ensure you:

- Use a dedicated profile directory.
- Revoke access immediately if you suspect credential compromise.
- Avoid sharing captured JSON files that may contain sensitive data.

## License

Threadopolis is released under the [MIT License](LICENSE).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
