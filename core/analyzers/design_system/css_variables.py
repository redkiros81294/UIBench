"""
CSS variables analyzer.

Extracts and validates CSS custom properties from inline styles and style tags.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class CSSVariablesAnalyzer(Analyzer):
    """Analyzes CSS custom properties for design system consistency."""

    name = "design_css_variables"
    category = "design_system"
    description = "Extracts and counts CSS custom properties"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        soup = context.soup
        if soup is None:
            raise ValueError("CSSVariablesAnalyzer requires a parsed soup object")

        issues: List[str] = []
        recommendations: List[str] = []

        # Find style tags
        style_tags = soup.find_all("style")
        inline_styles = soup.find_all(style=True)

        css_vars: List[str] = []
        for tag in style_tags:
            for line in tag.text.splitlines():
                line = line.strip()
                if line.startswith("--"):
                    css_vars.append(line.split(":")[0].strip())

        # Also check inline styles for CSS vars (rare but possible)
        for tag in inline_styles:
            style = tag.get("style", "")
            for part in style.split(";"):
                part = part.strip()
                if part.startswith("--"):
                    css_vars.append(part.split(":")[0].strip())

        unique_vars = sorted(set(css_vars))

        if not unique_vars:
            issues.append("No CSS custom properties found — consider implementing a design token system")
            score = 0.0
        else:
            recommendations.append(f"Found {len(unique_vars)} CSS custom properties")
            score = min(100.0, len(unique_vars) * 10.0)

        return self._build_response(
            context.url,
            score,
            "passed" if score >= 75 else "warning" if score >= 50 else "failed",
            issues,
            recommendations,
            metrics={
                "css_variable_count": len(unique_vars),
                "css_variables": unique_vars[:50],  # Limit for payload size
            },
        )
