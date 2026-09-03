from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from cli.context import AppContext
from cli.core.engine import DEFAULT_ANALYZERS, EvaluateOptions
from cli.core.exceptions import ThresholdBreachError, UIBenchError
from cli.models import EvaluationResult
from cli.output import (
    render_cards,
    render_html,
    render_json,
    render_pdf,
    render_text,
    validate_format,
    write_or_print,
)
from cli.ui.icons import RenderOptions
from cli.ui.picker import pick_analyzers
from cli.ui.spinner import spinner


def build_options(
    ctx: AppContext,
    analyzer: Optional[str],
    skip: Optional[str],
    browser: bool,
    zap: bool,
    lighthouse: bool,
    depth: int,
    max_pages: int,
    timeout: int,
    design: str,
) -> EvaluateOptions:
    analyzers = analyzer.split(",") if analyzer else list(DEFAULT_ANALYZERS)
    skip_list = skip.split(",") if skip else []
    return EvaluateOptions(
        analyzers=[a.strip() for a in analyzers if a.strip()],
        skip=[s.strip() for s in skip_list if s.strip()],
        browser=browser,
        zap=zap,
        lighthouse=lighthouse,
        depth=depth,
        max_pages=max_pages,
        timeout=timeout,
        design=design,
        thresholds={k: float(v) for k, v in ctx.config.get("thresholds", {}).items()},
    )


def run_evaluation(ctx: AppContext, target: str, options: EvaluateOptions) -> EvaluationResult:
    """Shared by evaluate / batch / watch. Raises UIBenchError subclasses
    on failure — callers decide how to present/aggregate them."""
    show_spinner = ctx.config.get("output", {}).get("show_spinner", True) and not ctx.quiet
    with spinner(ctx.console, f"Evaluating {target}\u2026", enabled=show_spinner):
        return ctx.engine.evaluate(target, options)


def render_result(
    ctx: AppContext,
    result: EvaluationResult,
    output_format: str,
    save: Optional[Path],
) -> str:
    opts = RenderOptions(unicode=ctx.unicode_enabled)
    if output_format == "json":
        text = render_json(result, ctx.console, pretty=ctx.console.is_terminal and save is None)
        write_or_print(text, ctx.console, save)
        return text
    if output_format == "text":
        if save is not None:
            # capture rendered text to a string for file writing, plain
            # (no ANSI codes) since it's headed to disk, not a TTY
            from io import StringIO

            from rich.console import Console as _Console

            from cli.theme import UIBENCH_THEME

            buf = StringIO()
            capture_console = _Console(file=buf, theme=UIBENCH_THEME, no_color=True, width=100)
            render_text(result, capture_console, opts)
            save.write_text(buf.getvalue(), encoding="utf-8")
            ctx.console.print(f"[dim]Written to {save}[/dim]")
        else:
            render_text(result, ctx.console, opts)
        return ""
    if output_format == "cards":
        if save is not None:
            ctx.console.print(
                "[warn]WARNING: cards output requires a terminal, falling back to text.[/warn]"
            )
            from io import StringIO
            from rich.console import Console as _Console
            from cli.theme import UIBENCH_THEME

            buf = StringIO()
            capture_console = _Console(file=buf, theme=UIBENCH_THEME, no_color=True, width=100)
            render_text(result, capture_console, opts)
            save.write_text(buf.getvalue(), encoding="utf-8")
            ctx.console.print(f"[dim]Written to {save}[/dim]")
        elif ctx.console.is_terminal:
            render_cards(result, ctx.console, opts)
        else:
            ctx.console.print(
                "[warn]WARNING: cards output requires a terminal, falling back to text.[/warn]"
            )
            render_text(result, ctx.console, opts)
        return ""
    if output_format == "html":
        html = render_html(result)
        write_or_print(html, ctx.console, save)
        return html
    if output_format == "pdf":
        target_path = save or Path("report.pdf")
        render_pdf(result, target_path)
        ctx.console.print(f"[dim]Written to {target_path}[/dim]")
        return ""
    raise AssertionError(f"unreachable: {output_format}")


def evaluate_command(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="URL or local project path to evaluate."),
    analyzer: Optional[str] = typer.Option(None, "--analyzer", help="Comma-separated analyzer list."),
    skip: Optional[str] = typer.Option(None, "--skip", help="Comma-separated analyzers to skip."),
    browser: bool = typer.Option(False, "--browser", help="Enable Playwright-based analyzers."),
    zap: bool = typer.Option(False, "--zap", help="Enable ZAP security scan."),
    lighthouse: bool = typer.Option(False, "--lighthouse", help="Enable Lighthouse audit."),
    depth: int = typer.Option(0, "--depth", help="Crawl depth for subpages."),
    max_pages: int = typer.Option(10, "--max-pages", help="Max pages to evaluate."),
    timeout: int = typer.Option(30, "--timeout", help="Request timeout in seconds."),
    design: str = typer.Option("none", "--design", help="figma:<key> | sketch:<url> | none"),
    output: Optional[str] = typer.Option(None, "--output", help="json | html | pdf | text | cards"),
    fail_below: Optional[float] = typer.Option(None, "--fail-below", help="Exit 1 if overall score < N."),
    save: Optional[Path] = typer.Option(None, "--save", help="Write output to file instead of stdout."),
    all_flag: bool = typer.Option(False, "--all", help="Run all analyzers without prompting."),
    yes_flag: bool = typer.Option(False, "-y", "--yes", help="Accept default analyzer selection without prompting."),
) -> None:
    """Evaluate a URL or local project."""
    app_ctx: AppContext = ctx.obj

    if analyzer is None and not yes_flag:
        picked = pick_analyzers(app_ctx.console)
        if picked:
            analyzer = ",".join(picked)

    if output is None:
        if app_ctx.console.is_terminal:
            output = app_ctx.config.get("output", {}).get("tty_format", "cards")
        else:
            output = app_ctx.config.get("output", {}).get("default_format", "json")

    try:
        output_format = validate_format(output)
        options = build_options(app_ctx, analyzer, skip, browser, zap, lighthouse, depth, max_pages, timeout, design)
        result = run_evaluation(app_ctx, target, options)
        render_result(app_ctx, result, output_format, save)
    except UIBenchError as err:
        from cli.ui.errors import print_error

        print_error(app_ctx.console, err)
        raise typer.Exit(code=err.exit_code)

    if fail_below is not None and result.overall_score < fail_below:
        raise typer.Exit(code=ThresholdBreachError.exit_code)
    raise typer.Exit(code=0)
