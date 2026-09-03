from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

import typer

from cli.commands.evaluate import build_options, render_result, run_evaluation
from cli.context import AppContext
from cli.core.exceptions import InvalidArgumentsError, UIBenchError
from cli.output import validate_format
from cli.ui.icons import RenderOptions
from cli.ui.picker import pick_analyzers


def _snapshot(path: Path) -> dict[str, float]:
    """path -> mtime for every file under `path`, used by the polling
    fallback when watchdog isn't installed."""
    snap: dict[str, float] = {}
    if path.is_file():
        snap[str(path)] = path.stat().st_mtime
        return snap
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for name in files:
            fp = Path(root) / name
            try:
                snap[str(fp)] = fp.stat().st_mtime
            except OSError:
                continue
    return snap


def _run_once(app_ctx: AppContext, path: Path, options, output_format: str, save: Optional[Path]) -> None:
    try:
        result = run_evaluation(app_ctx, str(path), options)
        render_result(app_ctx, result, output_format, save)
    except UIBenchError as err:
        from cli.ui.errors import print_error

        print_error(app_ctx.console, err)


def watch_command(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Local project directory to watch."),
    debounce: int = typer.Option(1000, "--debounce", help="Debounce interval in ms."),
    analyzer: Optional[str] = typer.Option(None, "--analyzer"),
    output: Optional[str] = typer.Option(None, "--output"),
    save: Optional[Path] = typer.Option(None, "--save"),
    all_flag: bool = typer.Option(False, "--all", help="Run all analyzers without prompting."),
    yes_flag: bool = typer.Option(False, "-y", "--yes", help="Accept default analyzer selection without prompting."),
) -> None:
    """Watch a local project directory and re-evaluate on file changes."""
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
        if not path.exists():
            raise InvalidArgumentsError(f"Path not found: {path}")
    except UIBenchError as err:
        from cli.ui.errors import print_error

        print_error(app_ctx.console, err)
        raise typer.Exit(code=err.exit_code)

    options = build_options(app_ctx, analyzer, None, False, False, False, 0, 10, 30, "none")

    app_ctx.console.print(f"[dim]Watching {path} \u00b7 debounce {debounce}ms \u00b7 Ctrl+C to stop[/dim]\n")
    _run_once(app_ctx, path, options, output_format, save)

    try:
        _watch_with_watchdog(app_ctx, path, debounce, options, output_format, save)
    except ImportError:
        _watch_with_polling(app_ctx, path, debounce, options, output_format, save)
    except KeyboardInterrupt:
        pass

    app_ctx.console.print("\n[dim]Stopped watching.[/dim]")
    raise typer.Exit(code=0)


def _watch_with_watchdog(app_ctx, path, debounce, options, output_format, save) -> None:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    last_run = [0.0]

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):  # noqa: ANN001
            now = time.time()
            if now - last_run[0] < debounce / 1000:
                return
            last_run[0] = now
            app_ctx.console.print(f"\n[teal]\u21bb[/teal] change detected \u2014 re-evaluating\n")
            _run_once(app_ctx, path, options, output_format, save)

    observer = Observer()
    observer.schedule(Handler(), str(path), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.25)
    finally:
        observer.stop()
        observer.join()


def _watch_with_polling(app_ctx, path, debounce, options, output_format, save) -> None:
    """Fallback when the optional `watchdog` dependency isn't installed:
    poll mtimes at the debounce interval. Fine for small projects; install
    `uibench-cli[watch]` for real filesystem events on larger ones."""
    last = _snapshot(path)
    interval = max(debounce, 250) / 1000
    while True:
        time.sleep(interval)
        current = _snapshot(path)
        if current != last:
            last = current
            app_ctx.console.print(f"\n[teal]\u21bb[/teal] change detected \u2014 re-evaluating\n")
            _run_once(app_ctx, path, options, output_format, save)
