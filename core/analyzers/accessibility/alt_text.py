"""
Alt text accessibility analyzer.

Checks that all images have meaningful alt text.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class AltTextAnalyzer(Analyzer):
    """Analyzes image alt text for accessibility."""

    name = "a11y_alt_text"
    category = "accessibility"
    description = "Validates that images have meaningful alt text"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        soup = context.soup
        if soup is None:
            raise ValueError("AltTextAnalyzer requires a parsed soup object")

        images = soup.find_all("img")
        if not images:
            return self._build_response(
                context.url,
                100.0,
                "passed",
                [],
                ["No images found — nothing to check"],
            )

        issues: List[str] = []
        recommendations: List[str] = []

        missing_alt = 0
        empty_alt = 0
        short_alt = 0

        for img in images:
            alt = img.get("alt", "")
            if not alt:
                missing_alt += 1
                issues.append(f"Image missing alt text: {img.get('src', '(no src)')}")
            elif len(alt.strip()) < 3:
                short_alt += 1
                issues.append(f"Alt text too short: '{alt}'")
            else:
                recommendations.append(f"Image has alt text: '{alt}'")

        total = len(images)
        score = 100.0 - ((missing_alt + short_alt) / total * 100.0) if total else 100.0

        return self._build_response(
            context.url,
            score,
            "passed" if score >= 75 else "warning" if score >= 50 else "failed",
            issues,
            recommendations,
            metrics={
                "total_images": total,
                "missing_alt": missing_alt,
                "empty_alt": empty_alt,
                "short_alt": short_alt,
            },
        )
