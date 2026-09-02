"""
Page size performance analyzer.

Checks HTML size and resource count from static HTML.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class PageSizeAnalyzer(Analyzer):
    """Analyzes page size and resource count."""

    name = "perf_page_size"
    category = "performance"
    description = "Measures HTML size and resource count"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        html = context.html
        if not html:
            return self._build_response(
                context.url,
                0.0,
                "failed",
                ["No HTML content provided"],
            )

        size_bytes = len(html.encode("utf-8"))
        size_kb = size_bytes / 1024

        issues: List[str] = []
        recommendations: List[str] = []

        if size_kb > 500:
            issues.append(f"Large page size: {size_kb:.1f} KB (recommended < 500KB)")
            score = 0.0
        elif size_kb > 200:
            issues.append(f"Moderate page size: {size_kb:.1f} KB")
            score = 50.0
        else:
            recommendations.append(f"Page size is optimal: {size_kb:.1f} KB")
            score = 100.0

        return self._build_response(
            context.url,
            score,
            "passed" if score >= 75 else "warning" if score >= 50 else "failed",
            issues,
            recommendations,
            metrics={
                "size_bytes": size_bytes,
                "size_kb": round(size_kb, 2),
            },
        )
