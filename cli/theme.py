from __future__ import annotations

import sys

from rich.console import Console
from rich.theme import Theme

# Same hex values as the palette in the design spec (section 03).
UIBENCH_THEME = Theme(
    {
        "pass": "#3FB950",
        "warn": "#D29922",
        "fail": "#F85149",
        "info": "#58A6FF",
        "accent": "#FF9D4D",
        "teal": "#3FD1C0",
        "dim": "#6B7280",
    }
)


def build_console(no_color: bool = False, quiet: bool = False) -> Console:
    return Console(
        theme=UIBENCH_THEME,
        no_color=no_color,
        force_terminal=None,  # let rich auto-detect the TTY
        highlight=False,
        quiet=quiet,
        stderr=False,
    )


def is_tty() -> bool:
    return sys.stdout.isatty()
