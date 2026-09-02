"""
Readability analyzer.

Uses textstat to compute readability metrics.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class ReadabilityAnalyzer(Analyzer):
    """Analyzes text readability using textstat."""

    name = "nlp_readability"
    category = "nlp"
    description = "Calculates Flesch-Kincaid, SMOG, and other readability scores"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        text = context.body_text or ""
        if not text.strip():
            return self._build_response(
                context.url,
                0.0,
                "failed",
                ["No body text available for readability analysis"],
            )

        issues: List[str] = []
        recommendations: List[str] = []

        try:
            import textstat

            flesch = textstat.flesch_reading_ease(text)
            smog = textstat.smog_index(text)
            coleman = textstat.coleman_liau_index(text)

            if flesch < 30:
                issues.append(f"Text is very difficult to read (Flesch: {flesch:.1f})")
                recommendations.append("Simplify sentence structure and use shorter words")
                score = 25.0
            elif flesch < 60:
                issues.append(f"Text is fairly difficult to read (Flesch: {flesch:.1f})")
                score = 50.0
            else:
                recommendations.append(f"Text is easy to read (Flesch: {flesch:.1f})")
                score = 100.0

            metrics = {
                "flesch_reading_ease": round(flesch, 2),
                "smog_index": round(smog, 2),
                "coleman_liau_index": round(coleman, 2),
            }
        except Exception as exc:
            return self._build_response(
                context.url,
                0.0,
                "failed",
                [f"Readability analysis failed: {exc}"],
            )

        return self._build_response(
            context.url,
            score,
            "passed" if score >= 75 else "warning" if score >= 50 else "failed",
            issues,
            recommendations,
            metrics=metrics,
        )
