from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from uibench_cli.core.engine import AnalyzerEngine


@dataclass
class AppContext:
    console: Console
    engine: AnalyzerEngine
    config: dict[str, Any]
    config_path: Path | None
    output_format: str
    quiet: bool
    verbose: bool
    no_color: bool
    unicode_enabled: bool
    core_url: str
    token: str | None
