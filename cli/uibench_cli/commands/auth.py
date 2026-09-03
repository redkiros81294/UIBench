"""
Auth is only relevant when pointing the CLI at a remote UIBench backend
(--core-url something other than localhost). Credentials are cached at
~/.config/uibench/credentials.json, mode 0600.

The actual login request against the backend is a placeholder — swap
`_request_token` for a real call into your auth endpoint once the core
is wired up (see CORE_INTEGRATION.md).
"""

from __future__ import annotations

import json
import stat
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

import typer

from uibench_cli.context import AppContext
from uibench_cli.core.exceptions import AuthError, NetworkError

CREDENTIALS_PATH = Path.home() / ".config" / "uibench" / "credentials.json"


def _save_credentials(core_url: str, token: str, email: str) -> None:
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(
        json.dumps({"core_url": core_url, "token": token, "email": email}, indent=2),
        encoding="utf-8",
    )
    CREDENTIALS_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600 — token is a secret


def _load_credentials() -> Optional[dict]:
    if not CREDENTIALS_PATH.exists():
        return None
    return json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))


def _request_token(core_url: str, email: str, password: str) -> str:
    """Placeholder network call — replace with the real auth endpoint."""
    req = urllib.request.Request(
        f"{core_url.rstrip('/')}/api/auth/login",
        data=json.dumps({"email": email, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            return body["token"]
    except urllib.error.URLError as exc:
        raise NetworkError(
            f"Could not reach {core_url}",
            detail=str(exc),
            suggestion=f"uibench login {core_url} {email} --core-url {core_url}",
        ) from exc
    except (KeyError, json.JSONDecodeError) as exc:
        raise AuthError("Login failed", detail="Backend did not return a token.") from exc


def login_command(
    ctx: typer.Context,
    url: str = typer.Argument(..., help="Remote UIBench backend URL."),
    email: str = typer.Argument(..., help="Account email."),
    password: Optional[str] = typer.Option(None, "--password", help="Omit to be prompted (recommended)."),
) -> None:
    """Authenticate with a remote UIBench backend."""
    app_ctx: AppContext = ctx.obj
    pw = password or typer.prompt("Password", hide_input=True)
    try:
        token = _request_token(url, email, pw)
    except (NetworkError, AuthError) as err:
        from uibench_cli.ui.errors import print_error

        print_error(app_ctx.console, err)
        raise typer.Exit(code=err.exit_code)
    _save_credentials(url, token, email)
    app_ctx.console.print(f"[pass]\u2705[/pass] Logged in as {email} \u2192 {url}")


def logout_command(ctx: typer.Context) -> None:
    """Clear stored credentials."""
    app_ctx: AppContext = ctx.obj
    if CREDENTIALS_PATH.exists():
        CREDENTIALS_PATH.unlink()
    app_ctx.console.print("[dim]Logged out.[/dim]")


def whoami_command(ctx: typer.Context) -> None:
    """Show current user."""
    app_ctx: AppContext = ctx.obj
    creds = _load_credentials()
    if creds is None:
        err = AuthError(
            "Not authenticated",
            detail=f"No valid token for {app_ctx.core_url}.",
            suggestion=f"uibench login {app_ctx.core_url} you@example.com",
        )
        from uibench_cli.ui.errors import print_error

        print_error(app_ctx.console, err)
        raise typer.Exit(code=err.exit_code)
    app_ctx.console.print(f"{creds['email']}  [dim]({creds['core_url']})[/dim]")
