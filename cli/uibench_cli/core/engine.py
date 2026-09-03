"""
This module is the *only* place the CLI talks to an evaluation engine.
Everything upstream (commands/, ui/, output.py) works against the
`AnalyzerEngine` protocol below, not against any concrete implementation.

To wire in the real UIBench core, implement this protocol against your
existing evaluation pipeline and pass it into AppContext in cli.py —
see CORE_INTEGRATION.md for the full walkthrough. Until then, MockEngine
(core/mock_engine.py) lets every command run end-to-end for UX review,
demos, and writing tests against the CLI layer in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from uibench_cli.models import EvaluationResult

DEFAULT_ANALYZERS = ["seo", "performance", "accessibility", "design", "nlp"]


@dataclass
class EvaluateOptions:
    analyzers: list[str] = field(default_factory=lambda: list(DEFAULT_ANALYZERS))
    skip: list[str] = field(default_factory=list)
    browser: bool = False
    zap: bool = False
    lighthouse: bool = False
    depth: int = 0
    max_pages: int = 10
    timeout: int = 30
    design: str = "none"  # "none" | "figma:<key>" | "sketch:<url>"
    thresholds: dict[str, float] = field(default_factory=dict)

    def resolved_analyzers(self) -> list[str]:
        wanted = [a for a in self.analyzers if a not in self.skip]
        # de-dupe, preserve order
        seen: set[str] = set()
        out = []
        for a in wanted:
            if a not in seen:
                seen.add(a)
                out.append(a)
        return out


class AnalyzerEngine(Protocol):
    """Implement this against the real UIBench core.

    `target` is either a URL (https://example.com) or a local path
    (./my-project), exactly as typed on the command line — the engine
    decides how to dispatch based on that shape.

    Raise uibench_cli.core.exceptions.NetworkError for unreachable hosts,
    CoreEngineError for missing dependencies or analyzer crashes. Any
    other exception is treated by the CLI as an unexpected core error
    (exit code 4) and surfaced with --verbose tracebacks.
    """

    def evaluate(self, target: str, options: EvaluateOptions) -> EvaluationResult:
        ...
