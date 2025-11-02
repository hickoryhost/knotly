from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ..console import Console

console = Console()


def capture_conversation(*, user_data_dir: Path, conv_url: str, out_json: Path, wait_for: float = 5.0) -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Playwright is not installed. Install with `pip install playwright` and run `playwright install`." ) from exc

    console.log("Starting headless capture via Playwright…")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(user_data_dir=str(user_data_dir), headless=True)
        try:
            page = browser.new_page()
            page.goto(conv_url)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(wait_for * 1000)
            data = page.evaluate("""
                () => {
                    const nodes = Array.from(document.querySelectorAll('[data-message-id], .conversation-turn'));
                    return {
                        title: document.title,
                        messages: nodes.map((node, index) => {
                            const content = node.innerText || '';
                            return {
                                id: node.getAttribute('data-message-id') || `auto-${index+1}`,
                                role: node.getAttribute('data-role') || node.getAttribute('data-author-role') || 'unknown',
                                author: node.getAttribute('data-author-name') || null,
                                create_time: node.getAttribute('data-timestamp') || node.getAttribute('data-created') || null,
                                content: content,
                            };
                        }),
                    };
                }
            """)
        finally:
            browser.close()

    out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
    console.log(f"Conversation saved to {out_json}")
    return out_json
