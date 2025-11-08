# 🪢 knotly

Turn long rambling GPT-5 chats into a tidy set of interlinked Markdown files ready for Obsidian. One knotty conversation in, a navigable network of thoughts out.

## Requirements

- **Git** — installed and working on your command line.  
- **Python 3.9+** — installed and working on your command line.  
- Ability to install Python packages for your user (no admin required).  
- Your shell’s **PATH** should include where Python places console scripts (see notes per OS below).

> This project assumes Git and Python are already installed and set up. (No installation instructions for those are included here.)

---

## Quick Start (Command Line)

After following the steps for your OS, you should be able to run `knotly` from **any** terminal window.

### Windows

1. Open **Command Prompt** or **PowerShell**.
2. Clone the repo:
   ```powershell
   git clone https://github.com/hickoryhost/knotly.git
   ```
3. Change into the folder:
   ```powershell
   cd knotly
   ```
4. Install the app for your current user:
   ```powershell
   python -m pip install .
   ```
5. Test it:
   ```powershell
   knotly --help
   ```

**PATH note (Windows):** Python typically places console scripts in a path like:
```
%LocalAppData%\Programs\Python\Python3xx\Scripts
```
Ensure that directory is on your PATH so `knotly` is available in any new terminal.

---

### macOS

1. Open **Terminal**.
2. Clone the repo:
   ```bash
   git clone https://github.com/hickoryhost/knotly.git
   ```
3. Change into the folder:
   ```bash
   cd knotly
   ```
4. Install the app for your current user:
   ```bash
   python3 -m pip install --user .
   ```
5. Test it:
   ```bash
   knotly --help
   ```

**PATH note (macOS):** With `--user`, Python typically places console scripts in:
```
~/Library/Python/3.x/bin
```
Make sure that directory is on your PATH so `knotly` is recognized in new terminals.

---

### Linux

1. Open your shell.
2. Clone the repo:
   ```bash
   git clone https://github.com/hickoryhost/knotly.git
   ```
3. Change into the folder:
   ```bash
   cd knotly
   ```
4. Install the app for your current user:
   ```bash
   python3 -m pip install --user .
   ```
5. Test it:
   ```bash
   knotly --help
   ```

**PATH note (Linux):** With `--user`, Python typically places console scripts in:
```
~/.local/bin
```
Ensure that directory is on your PATH so `knotly` runs from any terminal.

---

## Verify

- Show help:
  ```bash
  knotly --help
  ```
- (Optional) Module form (works regardless of PATH):
  ```bash
  python -m knotly.cli --help
  ```

---

## Development Install (Optional)

If you plan to modify the code and want edits to take effect immediately:

```bash
# from the cloned repository folder
python -m venv .venv            # use: python3 -m venv .venv on macOS/Linux
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows CMD:       .venv\Scripts\activate.bat
# macOS/Linux:       source .venv/bin/activate
python -m pip install -e .
knotly --help
```

Deactivate later with `deactivate`.

---

## Troubleshooting

- **`knotly: command not found` / `'knotly' is not recognized`**  
  Ensure your OS-specific *console scripts* directory is on your PATH (see the notes in each OS section).  
  As a fallback, the module form always works:
  ```bash
  python -m knotly.cli --help
  ```

- **Multiple Python versions**  
  Use the explicit interpreter you intend (e.g., `py -3.11 -m pip install .` on Windows, or `python3.11 -m pip install .` on macOS/Linux).

---

## What knotly does (in one sentence)

Parses a GPT-5 conversation and emits a parent index file plus one Markdown file per turn, with bidirectional links that play nicely with Obsidian’s graph/backlinks.

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

- Place the generated output folder directly inside your vault or use `--vault-root /path/to/vault` to let knotly do it for you.
- The parent index (`Conversation.md` by default) links to every turn. Use Obsidian’s graph view to visualize the conversation links.
- Each turn file reserves a **Related:** section for future semantic cross-links or manual notes.

## Limitations & Roadmap

- Semantic link inference, embeddings, and Obsidian plugin integrations are reserved for future work (`--infer-links` flag).

## License

knotly is released under the [MIT License](LICENSE).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.
