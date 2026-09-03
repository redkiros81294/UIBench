from __future__ import annotations

from rich.table import Table

from uibench_cli.models import AnalyzerResult
from uibench_cli.ui.icons import RenderOptions, status_glyph


def build_analyzer_table(analyzers: list[AnalyzerResult], opts: RenderOptions) -> Table:
    """Analyzer | Score | Status | Findings — widths and truncation per
    the table layout spec (design doc section 05)."""
    table = Table(show_header=True, header_style="dim", box=None, pad_edge=False)
    table.add_column("Analyzer", width=18, no_wrap=True, overflow="ellipsis")
    table.add_column("Score", width=8, justify="right")
    table.add_column("Status", width=14)
    table.add_column("Findings", overflow="fold")

    for a in analyzers:
        glyph, style = status_glyph(a.status, opts)
        n_issues = len(a.issues)
        n_recs = len(a.recommendations)
        if n_issues:
            findings = f"{n_issues} issue{'s' if n_issues != 1 else ''}"
        elif n_recs:
            findings = f"{n_recs} recommendation{'s' if n_recs != 1 else ''}"
        else:
            findings = "0 issues"

        table.add_row(
            a.name,
            f"{a.score:.0f}/100",
            f"[{style}]{glyph} {a.status}[/{style}]",
            findings,
        )
    return table
