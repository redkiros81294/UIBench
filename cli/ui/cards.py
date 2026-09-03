from __future__ import annotations

from typing import Any

from rich.columns import Columns
from rich.panel import Panel

from cli.models import AnalyzerResult
from cli.ui.icons import ANALYZER_ICONS, RenderOptions, status_glyph


def _status_style(status: str) -> str:
    status = (status or "").lower()
    if status == "passed":
        return "pass"
    if status == "warning":
        return "warn"
    if status == "failed":
        return "fail"
    return "dim"


def build_analyzer_cards(
    analyzers: list[AnalyzerResult],
    console_width: int,
    opts: RenderOptions,
) -> Any:
    """Build a card grid for analyzer results.

    Returns a ``rich.columns.Columns`` when the grid has multiple columns,
    otherwise a list of ``Panel`` objects for stacked rendering.
    """
    cols = 3 if console_width >= 120 else 2 if console_width >= 80 else 1
    panels = []
    for a in analyzers:
        glyph, style = status_glyph(a.status, opts)
        cat_icon, cat_ascii, _cat_style = ANALYZER_ICONS.get(a.name, ("", "[???]", "dim"))
        cat_display = cat_icon if opts.unicode else cat_ascii

        lines: list[str] = []
        lines.append(f"[bold]{a.score:.0f}/100[/bold]")
        lines.append(f"[{style}]{glyph} {a.status}[/{style}]")

        if a.issues:
            lines.append("")
            lines.append("[dim]Issues[/dim]")
            for issue in a.issues:
                lines.append(f"[warn]\u26a0[/warn] {issue}")

        if a.recommendations:
            lines.append("")
            lines.append("[dim]Recommendations[/dim]")
            for rec in a.recommendations:
                lines.append(f"[info]\u2192[/info] {rec}")

        body = "\n".join(lines)
        border = _status_style(a.status)
        title = f"{cat_display} {a.name.title()}"
        panels.append(Panel(body, title=title, border_style=border, width=34))

    if cols > 1:
        return Columns(panels, equal=True, column_first=True)
    return panels
