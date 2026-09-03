"""
Exit codes (see Design Brief §9):
  0  success
  1  evaluation completed but score below --fail-below
  2  invalid arguments / missing required flag
  3  network error (unreachable host, timeout)
  4  core engine error (missing dependency, analyzer crash)
  5  authentication / authorization failure (remote backend)
  6  configuration error (invalid TOML, missing file)

Every UIBenchError carries the three pieces the terminal UX spec requires
for an error message: a short one-line summary, an optional longer
explanation, and an optional suggested next command.
"""

from __future__ import annotations


class UIBenchError(Exception):
    exit_code: int = 1

    def __init__(self, short: str, detail: str | None = None, suggestion: str | None = None):
        super().__init__(short)
        self.short = short
        self.detail = detail
        self.suggestion = suggestion


class ThresholdBreachError(UIBenchError):
    """Evaluation ran fine, but the score fell below --fail-below."""
    exit_code = 1


class InvalidArgumentsError(UIBenchError):
    exit_code = 2


class NetworkError(UIBenchError):
    exit_code = 3


class CoreEngineError(UIBenchError):
    """Missing optional dependency (Playwright, reportlab, ...) or an
    analyzer crash inside the evaluation engine."""
    exit_code = 4


class AuthError(UIBenchError):
    exit_code = 5


class ConfigError(UIBenchError):
    exit_code = 6
