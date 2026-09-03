from __future__ import annotations

from typing import Optional

from cli.ui.icons import RenderOptions


def render_banner(console, opts: RenderOptions, *, version: str = "1.0.0") -> None:
    """Print the UIBench startup banner.

    Respects ``quiet`` and ``no_color`` via the console; does not print
    anything when output is not a terminal.
    """
    if not console.is_terminal:
        return

    if opts.unicode:
        logo = (
            "\U0001f4ca  UIBench \u2014 Web Interface Analysis & Design System Platform"
        )
    else:
        logo = "[UIBENCH] Web Interface Analysis & Design System Platform"

    console.print(f"[accent]{logo}[/accent]")
    console.print(f"[dim]version {version}[/dim]")
