"""
Headings SEO analyzer.

Checks H1-H6 hierarchy and content length.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class HeadingsAnalyzer(Analyzer):
    """Analyzes heading structure for SEO."""

    name = "seo_headings"
    category = "seo"
    description = "Validates heading hierarchy and content length"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        soup = context.soup
        if soup is None:
            raise ValueError("HeadingsAnalyzer requires a parsed soup object")

        issues: List[str] = []
        recommendations: List[str] = []

        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        if not headings:
            issues.append("No heading tags found")
            return self._build_response(context.url, 0.0, "failed", issues, recommendations)

        h1_count = sum(1 for h in headings if h.name == "h1")
        if h1_count == 0:
            issues.append("Missing H1 heading")
            h1_score = 0.0
        elif h1_count > 1:
            issues.append(f"Multiple H1 headings found: {h1_count}")
            h1_score = 50.0
        else:
            recommendations.append("Single H1 heading present")
            h1_score = 100.0

        # Check hierarchy
        last_level = 0
        hierarchy_ok = True
        for h in headings:
            level = int(h.name[1])
            if last_level and level > last_level + 1:
                hierarchy_ok = False
                issues.append(f"Skipped heading level: H{last_level} to H{level}")
            last_level = level

        hierarchy_score = 100.0 if hierarchy_ok else 50.0

        # Content length
        body = soup.find("body")
        text_length = len(body.get_text().strip()) if body else 0
        if text_length < 300:
            issues.append(f"Content too short: {text_length} chars (min 300)")
            length_score = 0.0
        else:
            recommendations.append(f"Content length adequate: {text_length} chars")
            length_score = 100.0

        scores = [h1_score, hierarchy_score, length_score]
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
                "length_score": length_score,
                "heading_count": len(headings),
                "h1_count": h1_count,
            },
        )
