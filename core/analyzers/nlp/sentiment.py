"""
Sentiment analyzer.

Uses TextBlob for basic sentiment analysis.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class SentimentAnalyzer(Analyzer):
    """Analyzes text sentiment using TextBlob."""

    name = "nlp_sentiment"
    category = "nlp"
    description = "Calculates sentiment polarity and subjectivity"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        text = context.body_text or ""
        if not text.strip():
            return self._build_response(
                context.url,
                0.0,
                "failed",
                ["No body text available for sentiment analysis"],
            )

        issues: List[str] = []
        recommendations: List[str] = []

        try:
            from textblob import TextBlob

            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            if subjectivity > 0.9:
                issues.append("Content is highly subjective — consider adding factual evidence")
                score = 50.0
            elif polarity < -0.5:
                issues.append("Content is very negative — consider a more positive tone")
                score = 60.0
            else:
                recommendations.append("Content tone is balanced")
                score = 100.0

            metrics = {
                "polarity": round(polarity, 4),
                "subjectivity": round(subjectivity, 4),
            }
        except Exception as exc:
            return self._build_response(
                context.url,
                0.0,
                "failed",
                [f"Sentiment analysis failed: {exc}"],
            )

        return self._build_response(
            context.url,
            score,
            "passed" if score >= 75 else "warning" if score >= 50 else "failed",
            issues,
            recommendations,
            metrics=metrics,
        )
