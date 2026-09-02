"""
Accessibility headings analyzer.

Checks heading structure for accessibility (landmarks + hierarchy).
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class AccessibilityHeadingsAnalyzer(Analyzer):
    """Analyzes heading structure for accessibility."""

    name = "a11y_headings"
    category = "accessibility"
    description = "Validates heading hierarchy and landmarks for screen readers"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        soup = context.soup
        if soup is None:
            raise ValueError("AccessibilityHeadingsAnalyzer requires a parsed soup object")

        issues: List[str] = []
        recommendations: List[str] = []

        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        if not headings:
            issues.append("No heading tags found — screen reader users lose structure")
            return self._build_response(context.url, 0.0, "failed", issues, recommendations)

        # Check for H1
        h1_count = sum(1 for h in headings if h.name == "h1")
        if h1_count == 0:
            issues.append("Missing H1 heading — page has no main heading")
            h1_score = 0.0
        elif h1_count > 1:
            issues.append(f"Multiple H1 headings ({h1_count}) — use exactly one per page")
            h1_score = 50.0
        else:
            recommendations.append("Single H1 heading present")
            h1_score = 100.0

        # Check hierarchy
        last_level = 0
        hierarchy_ok = True
        skipped = []
        for h in headings:
            level = int(h.name[1])
            if last_level and level > last_level + 1:
                hierarchy_ok = False
                skipped.append(f"H{last_level}→H{level}")
            last_level = level

        if not hierarchy_ok:
            issues.append(f"Skipped heading levels: {', '.join(skipped)}")
            hierarchy_score = 50.0
        else:
            recommendations.append("Heading hierarchy is sequential")
            hierarchy_score = 100.0

        scores = [h1_score, hierarchy_score]
        overall_score = sum(scores) / len(scores) if scores else 0.0

        return self._build_response(
            context.url,
            overall_score,
            "passed" if overall_score >= 75 else "warning" if overall_score >= 50 else "failed",
            issues,
            recommendations,
            metrics={
                "h1_score": h1_score,
                "hierarchy_score": hierarchy_score,
                "heading_count": len(headings),
                "h1_count": h1_count,
            },
        )
