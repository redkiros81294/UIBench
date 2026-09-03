"""
A fake but deterministic engine: same target + analyzer always produces
the same score, so demos and screenshots are reproducible. Delete this
file once the real core is wired in via CORE_INTEGRATION.md — nothing
else in the CLI imports it directly except cli.py's default context.
"""

from __future__ import annotations

import hashlib
import time

from cli.core.engine import DEFAULT_ANALYZERS, EvaluateOptions
from cli.core.exceptions import CoreEngineError, NetworkError
from cli.models import AnalyzerResult, EvaluationResult

DEFAULT_THRESHOLDS = {
    "seo": 75.0,
    "performance": 75.0,
    "accessibility": 90.0,
    "security": 80.0,
    "design": 75.0,
    "nlp": 75.0,
}

_SAMPLE_ISSUES = {
    "performance": ["Large page size: 2.4MB, target <1MB"],
    "seo": [],
    "accessibility": [],
    "design": ["Token drift on 4 pages"],
    "security": ["Missing Content-Security-Policy header"],
    "nlp": [],
}
_SAMPLE_RECS = {
    "seo": ["Add a meta description", "Add a canonical URL"],
    "performance": ["Compress hero image", "Defer non-critical JS"],
    "accessibility": [],
    "design": ["Align button radius with token scale"],
    "security": [],
    "nlp": ["Simplify reading level on landing copy"],
}


def _score_for(target: str, analyzer: str) -> float:
    digest = hashlib.sha256(f"{target}:{analyzer}".encode()).hexdigest()
    # spread scores across 55-98 so the demo shows pass/warn/fail states
    return 55 + (int(digest[:4], 16) % 44)


class MockEngine:
    """In-memory stand-in for the real UIBench evaluation core."""

    def evaluate(self, target: str, options: EvaluateOptions) -> EvaluationResult:
        if not target:
            raise CoreEngineError("No target given", suggestion="uibench evaluate <url|path>")

        if target.startswith("http") and "unreachable" in target:
            # lets `uibench evaluate https://unreachable.example` demo the
            # network-error path without a real network dependency
            raise NetworkError(
                f"Could not reach {target}",
                detail=f"Connection timed out after {options.timeout}s.",
                suggestion=f"uibench evaluate {target} --timeout {options.timeout * 2}",
            )

        if options.browser:
            # demonstrates the missing-dependency error path; the real
            # engine should raise this from wherever it imports playwright
            try:
                import playwright  # noqa: F401
            except ImportError as exc:
                raise CoreEngineError(
                    "Playwright is not installed",
                    detail="Browser-based analyzers require Playwright.",
                    suggestion="pip install playwright && playwright install chromium",
                ) from exc

        analyzers = options.resolved_analyzers() or list(DEFAULT_ANALYZERS)
        thresholds = {**DEFAULT_THRESHOLDS, **options.thresholds}

        results = []
        for name in analyzers:
            start = time.perf_counter()
            score = float(_score_for(target, name))
            elapsed_ms = (time.perf_counter() - start) * 1000 + 40  # simulate work
            results.append(
                AnalyzerResult(
                    name=name,
                    score=score,
                    threshold=thresholds.get(name, 75.0),
                    issues=list(_SAMPLE_ISSUES.get(name, [])) if score < thresholds.get(name, 75.0) else [],
                    recommendations=list(_SAMPLE_RECS.get(name, [])),
                    execution_time_ms=elapsed_ms,
                )
            )

        return EvaluationResult(
            target=target,
            analyzers=results,
            overall_threshold=thresholds.get("overall", 75.0),
            metadata={"engine": "mock", "analyzers_run": analyzers},
        )
