from __future__ import annotations


class Console:
    """Minimal console compatible with the subset of Rich we use."""

    def log(self, message: str) -> None:
        print(f"[threadopolis] {message}")

    def print(self, message: str) -> None:
        print(message)
