from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.padding import Padding

from cli.core.exceptions import CoreEngineError, InvalidArgumentsError
from cli.models import EvaluationResult
from cli.ui.cards import build_analyzer_cards
from cli.ui.icons import RenderOptions, status_glyph
from cli.ui.table import build_analyzer_table

VALID_FORMATS = ("json", "text", "html", "pdf", "cards")


def validate_format(fmt: str) -> str:
    if fmt not in VALID_FORMATS:
        raise InvalidArgumentsError(
            f"Unknown output format: {fmt}",
            suggestion=f"--output {'|'.join(VALID_FORMATS)}",
        )
    return fmt


# ---------------------------------------------------------------- json ----

def render_json(result: EvaluationResult, console: Console, *, pretty: bool) -> str:
    payload: dict[str, Any] = result.to_dict()
    if pretty:
        text = json.dumps(payload, indent=2, ensure_ascii=False)
    else:
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return text


def render_json_batch(results: list[EvaluationResult], *, pretty: bool) -> str:
    payload = [r.to_dict() for r in results]
    if pretty:
        return json.dumps(payload, indent=2, ensure_ascii=False)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- text ----

def render_text(result: EvaluationResult, console: Console, opts: RenderOptions) -> None:
    glyph, style = status_glyph(result.status, opts)
    console.print("[accent]UIBench Evaluation Report[/accent]")
    console.print("[dim]" + "─" * 26 + "[/dim]")
    console.print(f"URL             {result.target}")
    console.print(f"Timestamp       {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(
        f"Overall Score   [{style}]{result.overall_score:.0f}/100[/{style}]  "
        f"[{style}]{glyph} {result.status}[/{style}]"
    )
    console.print()
    console.print(build_analyzer_table(result.analyzers, opts))

    if result.all_issues:
        console.print()
        console.print("[dim]Issues[/dim]")
        for analyzer_name, msg in result.all_issues:
            console.print(f"[warn]\u26a0\ufe0f  [{analyzer_name}][/warn] {msg}")

    if result.all_recommendations:
        console.print()
        console.print("[dim]Recommendations[/dim]")
        for analyzer_name, msg in result.all_recommendations:
            console.print(f"[info]\u2192[/info] [{analyzer_name}] {msg}")


def render_cards(result: EvaluationResult, console: Console, opts: RenderOptions) -> None:
    glyph, style = status_glyph(result.status, opts)
    summary = (
        f"[accent]UIBench[/accent] \u00b7 [accent]{result.target}[/accent] \u00b7 "
        f"[{style}]{result.overall_score:.0f}/100[/{style}] [{style}]{glyph} {result.status}[/{style}] "
        f"\u00b7 {len(result.analyzers)} analyzers"
    )
    console.print(summary)
    console.print()

    cards = build_analyzer_cards(result.analyzers, console.width or 80, opts)
    if isinstance(cards, list):
        for panel in cards:
            console.print(panel)
    else:
        console.print(Padding(cards, (0, 0)))


# ---------------------------------------------------------------- html ----

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UIBench Report — {target}</title>
<style>
  body {{ font-family: 'JetBrains Mono', ui-monospace, monospace; background:#0b0d11; color:#e9ebef; padding:40px; }}
  .score {{ font-size: 28px; font-weight:700; }}
  .pass {{ color:#3fb950; }} .warning {{ color:#d29922; }} .failed {{ color:#f85149; }}
  table {{ border-collapse: collapse; width:100%; margin-top:24px; }}
  th, td {{ text-align:left; padding:8px 12px; border-bottom:1px solid #2a2f3a; }}
  th {{ color:#6b7280; font-weight:500; font-size:12px; }}
</style>
</head>
<body>
  <h1>UIBench Evaluation Report</h1>
  <p>URL: {target}<br>Timestamp: {timestamp}</p>
  <p class="score {status}">{score:.0f}/100 &mdash; {status}</p>
  <table>
    <tr><th>Analyzer</th><th>Score</th><th>Status</th><th>Issues</th><th>Recommendations</th></tr>
    {rows}
  </table>
</body>
</html>
"""


def render_html(result: EvaluationResult) -> str:
    rows = "\n".join(
        f"<tr><td>{a.name}</td><td>{a.score:.0f}/100</td>"
        f"<td class='{a.status}'>{a.status}</td>"
        f"<td>{len(a.issues)}</td><td>{len(a.recommendations)}</td></tr>"
        for a in result.analyzers
    )
    return _HTML_TEMPLATE.format(
        target=result.target,
        timestamp=result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        status=result.status,
        score=result.overall_score,
        rows=rows,
    )


# ----------------------------------------------------------------- pdf ----

def render_pdf(result: EvaluationResult, path: Path) -> None:
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise CoreEngineError(
            "reportlab is not installed",
            detail="--output pdf requires the reportlab package.",
            suggestion="pip install 'uibench-cli[pdf]'",
        ) from exc

    c = canvas.Canvas(str(path), pagesize=LETTER)
    width, height = LETTER
    y = height - 72
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "UIBench Evaluation Report")
    y -= 24
    c.setFont("Helvetica", 10)
    c.drawString(72, y, f"URL: {result.target}")
    y -= 16
    c.drawString(72, y, f"Overall score: {result.overall_score:.0f}/100 ({result.status})")
    y -= 28
    for a in result.analyzers:
        c.drawString(72, y, f"{a.name:<16} {a.score:.0f}/100  {a.status}")
        y -= 16
    c.save()


# --------------------------------------------------------------- write ----

def write_or_print(content: str, console: Console, save_path: Path | None) -> None:
    if save_path is not None:
        save_path.write_text(content, encoding="utf-8")
        console.print(f"[dim]Written to {save_path}[/dim]")
    else:
        print(content)
