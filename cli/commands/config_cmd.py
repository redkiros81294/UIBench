from __future__ import annotations

from pathlib import Path

import typer

from cli import config as config_module
from cli.context import AppContext
from cli.core.exceptions import UIBenchError

config_app = typer.Typer(help="Manage configuration (.uibench.toml).")


@config_app.command("list")
def config_list(ctx: typer.Context) -> None:
    """Show all config values with their source."""
    app_ctx: AppContext = ctx.obj
    source = str(app_ctx.config_path) if app_ctx.config_path else "built-in defaults"
    app_ctx.console.print(f"[dim]source:[/dim] {source}\n")

    def walk(node, prefix=""):
        for key, value in node.items():
            full = f"{prefix}{key}"
            if isinstance(value, dict):
                walk(value, prefix=f"{full}.")
            else:
                shown = "***" if "token" in full and value else value
                app_ctx.console.print(f"{full:<28} [teal]{shown}[/teal]")

    walk(app_ctx.config)


@config_app.command("get")
def config_get(ctx: typer.Context, key: str = typer.Argument(..., help="Dotted key, e.g. core.max_workers")) -> None:
    """Show a single config value."""
    app_ctx: AppContext = ctx.obj
    try:
        value = config_module.get_value(app_ctx.config, key)
    except UIBenchError as err:
        from cli.ui.errors import print_error

        print_error(app_ctx.console, err)
        raise typer.Exit(code=err.exit_code)
    app_ctx.console.print(str(value))


@config_app.command("set")
def config_set(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="Dotted key, e.g. core.max_workers"),
    value: str = typer.Argument(..., help="New value (bool/int/float auto-detected)."),
) -> None:
    """Set a value in .uibench.toml (project file, created if missing)."""
    app_ctx: AppContext = ctx.obj
    target_path = app_ctx.config_path or config_module.PROJECT_CONFIG_PATH
    try:
        config_module.set_value_in_file(target_path, key, value)
    except UIBenchError as err:
        from cli.ui.errors import print_error

        print_error(app_ctx.console, err)
        raise typer.Exit(code=err.exit_code)
    app_ctx.console.print(f"[pass]\u2705[/pass] {key} = {value}  [dim]({target_path})[/dim]")
