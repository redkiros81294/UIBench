"""
Image SEO analyzer.

Checks alt text, src format, dimensions, and lazy loading.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class ImageSEOAnalyzer(Analyzer):
    """Analyzes images for SEO optimization."""

    name = "seo_images"
    category = "seo"
    description = "Validates image alt text, src format, dimensions, and lazy loading"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        soup = context.soup
        if soup is None:
            raise ValueError("ImageSEOAnalyzer requires a parsed soup object")

        images = soup.find_all("img")
        if not images:
            return self._build_response(
                context.url,
                100.0,
                "passed",
                [],
                ["No images found — nothing to optimize"],
            )

        issues: List[str] = []
        recommendations: List[str] = []
        image_scores: List[float] = []

        for img in images:
            src = img.get("src", "")
            alt = img.get("alt", "")
            width = img.get("width")
            height = img.get("height")
            loading = img.get("loading", "")

            img_issues: List[str] = []

            # Alt text
            if not alt:
                img_issues.append("Missing alt text")
            elif len(alt.strip()) < 3:
                img_issues.append("Alt text too short")

            # Src format
            if not src:
                img_issues.append("Missing src attribute")
            elif not src.startswith(("http://", "https://", "/")):
                img_issues.append(f"Invalid src URL format: {src}")

            # Dimensions
            if not width or not height:
                img_issues.append("Missing width or height attributes")

            # Lazy loading
            if loading != "lazy":
                img_issues.append("Missing lazy loading attribute")

            if img_issues:
                issues.extend([f"Image {src or '(no src)'}: {issue}" for issue in img_issues])
                image_scores.append(0.0)
            else:
                recommendations.append(f"Image optimized: {src}")
                image_scores.append(100.0)

        overall_score = sum(image_scores) / len(image_scores) if image_scores else 0.0
        if overall_score == 100.0:
            recommendations.append("All images are properly optimized")
        else:
            optimized = sum(1 for s in image_scores if s == 100.0)
            issues.append(f"Only {optimized}/{len(image_scores)} images optimized")

        return self._build_response(
            context.url,
            overall_score,
            "passed" if overall_score >= 75 else "warning" if overall_score >= 50 else "failed",
            issues,
            recommendations,
            metrics={
                "total_images": len(images),
                "optimized_images": sum(1 for s in image_scores if s == 100.0),
            },
        )
