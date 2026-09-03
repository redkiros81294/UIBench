from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer

from cli import __version__, config as config_module
from cli.commands.auth import login_command, logout_command, whoami_command
from cli.commands.batch import batch_command
from cli.commands.config_cmd import config_app
from cli.commands.evaluate import evaluate_command
from cli.commands.watch import watch_command
from cli.context import AppContext
from cli.core.exceptions import UIBenchError
from cli.core.real_engine import RealEngine
from cli.theme import build_console

app = typer.Typer(
    name="uibench",
    help="Evaluate websites for aesthetics, accessibility, performance, SEO, security, and design system consistency.",
    add_completion=True,
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"uibench {__version__}")
        raise typer.Exit()


def _build_engine() -> object:
    try:
        return RealEngine()
    except Exception as exc:
        # Fallback to MockEngine when core is not installed
        from cli.core.mock_engine import MockEngine
        return MockEngine()


@app.callback()
def main_callback(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", help="Path to config file."),
    output: str = typer.Option("json", "--output", help="json | html | pdf | text"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress non-essential output."),
    verbose: bool = typer.Option(False, "--verbose", help="Enable debug logging."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colors."),
    no_unicode: bool = typer.Option(False, "--no-unicode", help="Use ASCII status markers instead of emoji."),
    core_url: str = typer.Option("http://localhost:8000", "--core-url", help="Remote core API endpoint."),
    token: Optional[str] = typer.Option(None, "--token", envvar="UIBENCH_TOKEN", help="Bearer token for remote core."),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """
    uibench [global-flags] <command> [args] [flags]

    Run `uibench <command> --help` for command-specific flags.
    """
    try:
        cfg, cfg_path = config_module.load_config(config)
    except UIBenchError as err:
        console = build_console(no_color=no_color)
        from cli.ui.errors import print_error

        print_error(console, err)
        raise typer.Exit(code=err.exit_code)

    resolved_no_color = config_module.resolve_no_color(no_color) or not cfg.get("output", {}).get("color", True)
    console = build_console(no_color=resolved_no_color, quiet=quiet)
    unicode_enabled = not no_unicode and os.environ.get("TERM") != "dumb"

    ctx.obj = AppContext(
        console=console,
        engine=_build_engine(),
        config=cfg,
        config_path=cfg_path,
        output_format=output,
        quiet=quiet,
        verbose=verbose,
        no_color=resolved_no_color,
        unicode_enabled=unicode_enabled,
        core_url=core_url,
        token=token or cfg.get("backend", {}).get("token") or None,
    )


app.command("evaluate")(evaluate_command)
app.command("batch")(batch_command)
app.command("watch")(watch_command)
app.add_typer(config_app, name="config")
app.command("login")(login_command)
app.command("logout")(logout_command)
app.command("whoami")(whoami_command)


@app.command("version")
def version_cmd() -> None:
    """Show version string."""
    typer.echo(f"uibench {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
