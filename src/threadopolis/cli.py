from __future__ import annotations

import argparse
from pathlib import Path

from .console import Console
from .pipeline import build_conversation

console = Console()


def build_command(args: argparse.Namespace) -> None:
    in_path = Path(args.in_path)
    if not in_path.exists():
        raise SystemExit(f"Input path {in_path} does not exist")

    output_dir = Path(args.out)
    if args.vault_root:
        output_dir = Path(args.vault_root) / output_dir

    result = build_conversation(
        input_path=in_path,
        output_dir=output_dir,
        title=args.title,
        parent_name=args.parent_name,
        force=args.force,
        dry_run=args.dry_run,
        timezone=args.timezone,
        by_title=args.by_title,
        verbose=args.verbose,
    )

    if args.dry_run:
        console.print("Dry run. Files that would be written:")
        console.print(result.plan.summary())
    else:
        console.print(f"Wrote {len(result.plan.files)} files to {output_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Threadopolis conversation exporter for saved ChatGPT HTML pages"
    )
    parser.add_argument(
        "--in",
        dest="in_path",
        required=True,
        help="Input file path (saved ChatGPT HTML page)",
    )
    parser.add_argument("--out", dest="out", required=True, help="Output directory")
    parser.add_argument("--title", dest="title", help="Override conversation title")
    parser.add_argument("--vault-root", dest="vault_root", help="Optional Obsidian vault root")
    parser.add_argument(
        "--parent-name",
        dest="parent_name",
        default="Conversation.md",
        help="Parent index filename",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite non-empty directory")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without writing")
    parser.add_argument(
        "--timezone",
        dest="timezone",
        help="Normalize timestamps to timezone (e.g. UTC, America/New_York)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--by-title",
        action="store_true",
        help="When parsing HTML, derive title from page <title>",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    build_command(args)


if __name__ == "__main__":
    main()
