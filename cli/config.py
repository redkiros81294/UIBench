"""
Resolution order for config (first found wins for the *file*, then
values are layered over these defaults):

  1. --config <path>          (error if given but missing)
  2. ./.uibench.toml           (project-local)
  3. ~/.config/uibench/config.toml   (user-global)
  4. built-in defaults below

`get`/`set` use dotted keys, e.g. "core.max_workers", "thresholds.seo".
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from cli.core.exceptions import ConfigError

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

try:
    import tomli_w
except ModuleNotFoundError:  # pragma: no cover
    tomli_w = None  # type: ignore

DEFAULTS: dict[str, Any] = {
    "core": {
        "max_workers": 2,
        "max_concurrent": 2,
        "max_browsers": 1,
        "max_pages_per_browser": 2,
        "enable_browser": False,
        "enable_zap": False,
        "enable_lighthouse": False,
        "nlp_model": "en_core_web_sm",
        "cache_ttl": 3600,
    },
    "network": {
        "request_timeout": 20,
        "max_retries": 2,
        "user_agent": "UIBench/1.0",
    },
    "output": {
        "default_format": "json",
        "tty_format": "cards",
        "color": True,
        "show_spinner": True,
    },
    "thresholds": {
        "seo": 75,
        "performance": 75,
        "accessibility": 90,
        "security": 80,
        "overall": 75,
    },
    "backend": {
        "core_url": "http://localhost:8000",
        "token": "",
    },
}

USER_CONFIG_PATH = Path.home() / ".config" / "uibench" / "config.toml"
PROJECT_CONFIG_PATH = Path("./.uibench.toml")


def _deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_config_path(explicit: Path | None) -> Path | None:
    if explicit is not None:
        if not explicit.exists():
            raise ConfigError(
                f"Config file not found: {explicit}",
                suggestion=f"uibench config list  # to see what would load without it",
            )
        return explicit
    if PROJECT_CONFIG_PATH.exists():
        return PROJECT_CONFIG_PATH
    if USER_CONFIG_PATH.exists():
        return USER_CONFIG_PATH
    return None


def load_config(explicit_path: Path | None = None) -> tuple[dict[str, Any], Path | None]:
    """Returns (merged_config, path_actually_loaded_or_None)."""
    path = resolve_config_path(explicit_path)
    if path is None:
        return dict(DEFAULTS), None
    try:
        with open(path, "rb") as f:
            loaded = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(
            f"Invalid TOML in {path}",
            detail=str(exc),
            suggestion=f"uibench config list  # inspect current effective values",
        ) from exc
    return _deep_merge(DEFAULTS, loaded), path


def get_value(config: dict[str, Any], dotted_key: str) -> Any:
    node: Any = config
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ConfigError(f"Unknown config key: {dotted_key}")
        node = node[part]
    return node


def set_value_in_file(path: Path, dotted_key: str, value: str) -> None:
    """Writes a single value into the TOML file at `path`, creating it
    (with the parent directory) if it doesn't exist yet."""
    if tomli_w is None:
        raise ConfigError(
            "tomli-w is not installed",
            detail="Writing config requires the tomli-w package.",
            suggestion="pip install tomli-w",
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with open(path, "rb") as f:
            current = tomllib.load(f)
    else:
        current = {}

    parts = dotted_key.split(".")
    node = current
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = _coerce(value)

    with open(path, "wb") as f:
        tomli_w.dump(current, f)


def _coerce(raw: str) -> Any:
    """CLI values arrive as strings; coerce to bool/int/float where obvious."""
    low = raw.lower()
    if low in ("true", "false"):
        return low == "true"
    for cast in (int, float):
        try:
            return cast(raw)
        except ValueError:
            continue
    return raw


def resolve_no_color(flag_value: bool | None) -> bool:
    """--no-color > NO_COLOR env > TERM=dumb > TTY detection."""
    if flag_value:
        return True
    if os.environ.get("NO_COLOR") is not None:
        return True
    if os.environ.get("TERM") == "dumb":
        return True
    return False
