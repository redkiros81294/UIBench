"""
Axe-core accessibility analyzer.

Runs axe-core via Playwright to detect WCAG violations.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import BrowserAnalyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class AxeAccessibilityAnalyzer(BrowserAnalyzer):
    """Runs axe-core accessibility audit via Playwright."""

    name = "a11y_axe"
    category = "accessibility"
    description = "Runs axe-core to detect WCAG violations"

    def is_available(self) -> bool:
        try:
            from axe_playwright_python.sync_playwright import Axe  # noqa: F401
            return True
        except ImportError:
            return False

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        if not context.page:
            return AnalysisResponse(
                url=context.url,
                overall_score=0.0,
                status="skipped",
                analyzers=[],
                metadata={"reason": "No Playwright page provided"},
            )

        try:
            from axe_playwright_python.sync_playwright import Axe

            axe = Axe()
            results = axe.run(context.page)

            violations = results.violations
            score = max(100 - len(violations) * 5, 0)

            issues = [v["help"] for v in violations]
            recommendations = [v["help"] for v in violations]

            return self._build_response(
                context.url,
                score,
                "passed" if score >= 75 else "warning" if score >= 50 else "failed",
                issues,
                recommendations,
                metrics={"violation_count": len(violations)},
            )
        except Exception as exc:
            return self._build_response(
                context.url,
                0.0,
                "failed",
                [f"Axe analysis failed: {exc}"],
            )
