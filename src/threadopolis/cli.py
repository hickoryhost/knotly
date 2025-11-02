from __future__ import annotations

import argparse
from pathlib import Path

from .capture import capture_conversation
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
        input_format=args.format,
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


def capture_command(args: argparse.Namespace) -> None:
    try:
        capture_conversation(
            user_data_dir=Path(args.user_data_dir),
            conv_url=args.conv_url,
            out_json=Path(args.out_json),
        )
    except RuntimeError as exc:
        console.print(f"Capture failed: {exc}")
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Threadopolis conversation exporter")
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("build", help="Build a Threadopolis bundle")
    build_parser.add_argument("--in", dest="in_path", required=True, help="Input file path")
    build_parser.add_argument("--format", dest="format", choices=["json", "html"], required=True, help="Input format")
    build_parser.add_argument("--out", dest="out", required=True, help="Output directory")
    build_parser.add_argument("--title", dest="title", help="Override conversation title")
    build_parser.add_argument("--vault-root", dest="vault_root", help="Optional Obsidian vault root")
    build_parser.add_argument("--parent-name", dest="parent_name", default="Conversation.md", help="Parent index filename")
    build_parser.add_argument("--force", action="store_true", help="Overwrite non-empty directory")
    build_parser.add_argument("--dry-run", action="store_true", help="Show plan without writing")
    build_parser.add_argument("--timezone", dest="timezone", help="Normalize timestamps to timezone")
    build_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    build_parser.add_argument("--by-title", action="store_true", help="Derive title from HTML page title")
    build_parser.add_argument("--strict", action="store_true", help="Reserved for future use")
    build_parser.add_argument("--infer-links", action="store_true", help="Reserved for future semantic crosslinks")
    build_parser.set_defaults(func=build_command)

    capture_parser = subparsers.add_parser("capture", help="Capture a conversation via Playwright")
    capture_parser.add_argument("--user-data-dir", dest="user_data_dir", required=True, help="Chromium user data dir")
    capture_parser.add_argument("--conv-url", dest="conv_url", required=True, help="Conversation URL")
    capture_parser.add_argument("--out-json", dest="out_json", required=True, help="Output JSON path")
    capture_parser.set_defaults(func=capture_command)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.print_help()
        raise SystemExit(1)
    args.func(args)


if __name__ == "__main__":
    main()
