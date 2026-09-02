"""
Meta tags SEO analyzer.

Checks title, meta description, Open Graph, Twitter Cards, canonical, and robots tags.
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..base import Analyzer
from ...models.report import AnalysisResponse, AnalyzerResult
from ...models.context import AnalysisContext


class MetaTagsAnalyzer(Analyzer):
    """Analyzes meta tags for SEO."""

    name = "seo_meta_tags"
    category = "seo"
    description = "Validates title, meta description, OG, Twitter, canonical, and robots tags"

    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        soup = context.soup
        if soup is None:
            raise ValueError("MetaTagsAnalyzer requires a parsed soup object")

        issues: List[str] = []
        recommendations: List[str] = []

        # Title
        title = soup.find("title")
        if not title:
            issues.append("Missing title tag")
            title_score = 0.0
        else:
            title_text = title.text.strip()
            if len(title_text) < 30:
                issues.append(f"Title tag too short: {len(title_text)} chars (min 30)")
                title_score = 50.0
            elif len(title_text) > 60:
                issues.append(f"Title tag too long: {len(title_text)} chars (max 60)")
                title_score = 75.0
            else:
                recommendations.append(f"Title length optimal: {len(title_text)} chars")
                title_score = 100.0

        # Meta description
        meta_desc = soup.find("meta", {"name": "description"})
        if not meta_desc:
            issues.append("Missing meta description")
            desc_score = 0.0
        else:
            desc_text = meta_desc.get("content", "").strip()
            if len(desc_text) < 50:
                issues.append(f"Meta description too short: {len(desc_text)} chars (min 50)")
                desc_score = 50.0
            elif len(desc_text) > 160:
                issues.append(f"Meta description too long: {len(desc_text)} chars (max 160)")
                desc_score = 75.0
            else:
                recommendations.append(f"Meta description length optimal: {len(desc_text)} chars")
                desc_score = 100.0

        # Open Graph
        og_tags = soup.find_all("meta", {"property": lambda x: x and x.startswith("og:")})
        required_og = {"og:title", "og:description", "og:image", "og:url"}
        present_og = {t.get("property") for t in og_tags}
        missing_og = required_og - present_og
        if missing_og:
            issues.append(f"Missing Open Graph tags: {', '.join(sorted(missing_og))}")
            og_score = 0.0
        else:
            recommendations.append("All required Open Graph tags present")
            og_score = 100.0

        # Twitter Card
        twitter_tags = soup.find_all("meta", {"name": lambda x: x and x.startswith("twitter:")})
        required_twitter = {"twitter:card", "twitter:title", "twitter:description", "twitter:image"}
        present_twitter = {t.get("name") for t in twitter_tags}
        missing_twitter = required_twitter - present_twitter
        if missing_twitter:
            issues.append(f"Missing Twitter Card tags: {', '.join(sorted(missing_twitter))}")
            twitter_score = 0.0
        else:
            recommendations.append("All required Twitter Card tags present")
            twitter_score = 100.0

        # Canonical
        canonical = soup.find("link", {"rel": "canonical"})
        canonical_score = 100.0 if canonical else 0.0
        if canonical_score == 0.0:
            issues.append("Missing canonical URL tag")
        else:
            recommendations.append("Canonical URL tag present")

        # Robots
        robots = soup.find("meta", {"name": "robots"})
        if robots:
            content = robots.get("content", "").lower()
            if "noindex" in content or "nofollow" in content:
                issues.append("Page is not indexable or followable")
                robots_score = 50.0
            else:
                recommendations.append("Robots meta tag properly configured")
                robots_score = 100.0
        else:
            issues.append("Missing robots meta tag")
            robots_score = 0.0

        scores = [title_score, desc_score, og_score, twitter_score, canonical_score, robots_score]
        overall_score = sum(scores) / len(scores) if scores else 0.0

        result = AnalyzerResult(
            name=self.name,
            score=overall_score,
            status="passed" if overall_score >= 75 else "warning" if overall_score >= 50 else "failed",
            issues=issues,
            recommendations=recommendations,
            metrics={
                "title_score": title_score,
                "description_score": desc_score,
                "og_score": og_score,
                "twitter_score": twitter_score,
                "canonical_score": canonical_score,
                "robots_score": robots_score,
            },
        )
        return AnalysisResponse(
            url=context.url,
            overall_score=overall_score,
            status=result.status,
            analyzers=[result],
            metadata={"analyzer": self.name, "category": self.category},
        )
