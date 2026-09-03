from __future__ import annotations

from rich.console import Console

from cli.core.exceptions import UIBenchError


def print_error(console: Console, err: UIBenchError) -> None:
    console.print(f"[fail]ERROR:[/fail] {err.short}")
    if err.detail:
        console.print(f"       [dim]{err.detail}[/dim]")
    if err.suggestion:
        console.print(f"       [dim]Run:[/dim] {err.suggestion}")


def print_warning(console: Console, message: str) -> None:
    console.print(f"[warn]WARNING:[/warn] {message}")


def print_info(console: Console, message: str) -> None:
    console.print(f"[dim]INFO:[/dim] {message}")
