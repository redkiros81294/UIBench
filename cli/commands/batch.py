from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from cli.commands.evaluate import build_options, run_evaluation
from cli.context import AppContext
from cli.core.exceptions import InvalidArgumentsError, UIBenchError
from cli.output import render_json_batch, validate_format, write_or_print
from cli.ui.icons import RenderOptions, status_glyph


def _read_targets(file: Path) -> list[str]:
    if not file.exists():
        raise InvalidArgumentsError(f"Batch file not found: {file}")
    lines = file.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def batch_command(
    ctx: typer.Context,
    file: Path = typer.Argument(..., help="File with one URL per line."),
    analyzer: Optional[str] = typer.Option(None, "--analyzer"),
    skip: Optional[str] = typer.Option(None, "--skip"),
    browser: bool = typer.Option(False, "--browser"),
    zap: bool = typer.Option(False, "--zap"),
    lighthouse: bool = typer.Option(False, "--lighthouse"),
    depth: int = typer.Option(0, "--depth"),
    max_pages: int = typer.Option(10, "--max-pages"),
    timeout: int = typer.Option(30, "--timeout"),
    design: str = typer.Option("none", "--design"),
    output: Optional[str] = typer.Option(None, "--output"),
    fail_below: Optional[float] = typer.Option(None, "--fail-below"),
    save: Optional[Path] = typer.Option(None, "--save"),
) -> None:
    """Evaluate multiple URLs from a file (one per line)."""
    app_ctx: AppContext = ctx.obj
    try:
        if output is None:
            if app_ctx.console.is_terminal:
                output = app_ctx.config.get("output", {}).get("tty_format", "cards")
            else:
                output = app_ctx.config.get("output", {}).get("default_format", "json")
        output_format = validate_format(output)
        targets = _read_targets(file)
    except UIBenchError as err:
        from cli.ui.errors import print_error

        print_error(app_ctx.console, err)
        raise typer.Exit(code=err.exit_code)

    options = build_options(app_ctx, analyzer, skip, browser, zap, lighthouse, depth, max_pages, timeout, design)
    opts = RenderOptions(unicode=app_ctx.unicode_enabled)

    results = []
    show_progress = not app_ctx.quiet and app_ctx.console.is_terminal
    progress_cm = Progress(
        SpinnerColumn(spinner_name="dots", style="teal"),
        TextColumn("[dim]{task.description}[/dim]"),
        BarColumn(complete_style="teal", finished_style="pass"),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=app_ctx.console,
        disable=not show_progress,
    )

    worst_breach = False
    with progress_cm as progress:
        task = progress.add_task(f"Evaluating {len(targets)} sites", total=len(targets))
        for target in targets:
            progress.update(task, description=target)
            try:
                result = run_evaluation(app_ctx, target, options)
                results.append(result)
                glyph, style = status_glyph(result.status, opts)
                if not app_ctx.quiet:
                    progress.console.print(f"[{style}]{glyph}[/{style}] {target} [dim]{result.overall_score:.0f}[/dim]")
                if fail_below is not None and result.overall_score < fail_below:
                    worst_breach = True
            except UIBenchError as err:
                worst_breach = True
                if not app_ctx.quiet:
                    progress.console.print(f"[fail]\u274c[/fail] {target} [dim]{err.short}[/dim]")
            progress.advance(task)

    if output_format == "json":
        text = render_json_batch(results, pretty=app_ctx.console.is_terminal and save is None)
        write_or_print(text, app_ctx.console, save)
    elif output_format == "text":
        from cli.output import render_text

        for result in results:
            render_text(result, app_ctx.console, opts)
            app_ctx.console.print()
    # html/pdf batch export intentionally left as a follow-up — see README

    raise typer.Exit(code=1 if worst_breach else 0)
