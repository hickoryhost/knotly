# Threadopolis

Threadopolis converts long-form AI assistant conversations into Obsidian-friendly markdown bundles. It ingests saved ChatGPT HTML pages, produces a parent conversation index, and splits every turn into a deterministic `turnNNN_<mnemonic>.md` file with backlinks, navigation, and metadata.

## Features

- Deterministic parent index with model, conversation, and participant metadata.
- Per-turn files with backlinks, previous/next navigation, timestamp headers, and space for future related links.
- Filename mnemonics generated from the first content words with collision-safe suffixes.
- HTML parser with timezone normalization.
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
python -m threadopolis.cli --help
```

## CLI Usage

### Build from a saved HTML page

```bash
bin/threadopolis \
  --in examples/html/conversation.html \
  --out output/html-sample \
  --by-title
```

### Dry run a build

```bash
bin/threadopolis --in export.html --out my-convo --dry-run -v
```

## Library Usage

```python
from pathlib import Path
from threadopolis import build_conversation

result = build_conversation(
    input_path=Path("conversation.html"),
    output_dir=Path("vault/My Conversation"),
    force=True,
)
print(f"Wrote {len(result.plan.files)} markdown files")
```

## Examples

The `examples/` folder contains:

- `html/conversation.html` and the generated bundle in `html/output/`.

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
- Playwright capture utilities have been removed to streamline the application.

## License

Threadopolis is released under the [MIT License](LICENSE).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
