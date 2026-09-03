"""
rich's built-in "dots" spinner already uses the exact ten-frame braille
cycle (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏) at ~80ms/frame specified in the design spec, so we
just point Status at it with our teal accent style. It's automatically
suppressed by rich when stdout isn't a TTY - no separate --quiet check
needed there, though we still gate it explicitly so --quiet is honored
even when someone forces --output text > file on a TTY.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from rich.console import Console


class NullStatus:
    def update(self, *_args, **_kwargs) -> None:
        pass


@contextmanager
def spinner(console: Console, message: str, *, enabled: bool = True) -> Iterator[object]:
    if not enabled:
        yield NullStatus()
        return
    with console.status(f"[teal]{message}[/teal]", spinner="dots", spinner_style="teal") as status:
        yield status
