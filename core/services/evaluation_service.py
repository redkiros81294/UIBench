"""
Evaluation service.

Orchestrates analyzers from the registry and returns a normalized AnalysisResponse.
This is the new replacement for PageEvaluator and WebsiteEvaluator.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from ..analyzers.registry import AnalyzerRegistry
from ..models.context import AnalysisContext
from ..models.report import AnalysisResponse, AnalyzerResult
from ..config import Settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Orchestrates analysis using the analyzer registry."""

    def __init__(
        self,
        registry: Optional[AnalyzerRegistry] = None,
        config: Optional[Settings] = None,
    ):
        self.registry = registry
        self.config = config or Settings()

    async def evaluate(self, context: AnalysisContext) -> AnalysisResponse:
        """Run all available analyzers and return a combined AnalysisResponse.

        Args:
            context: Analysis context with URL, HTML, soup, page, etc.

        Returns:
            AnalysisResponse with results from all analyzers.
        """
        if self.registry is None:
            from ..analyzers import build_default_registry
            self.registry = build_default_registry()

        available = self.registry.available(context)
        if not available:
            return AnalysisResponse(
                url=context.url,
                overall_score=0.0,
                status="failed",
                analyzers=[],
                metadata={"error": "No analyzers available"},
            )

        results = await asyncio.gather(
            *[self._run_analyzer(analyzer, context) for analyzer in available],
            return_exceptions=True,
        )

        normalized: List[AnalyzerResult] = []
        for analyzer, result in zip(available, results):
            if isinstance(result, Exception):
                logger.error("Analyzer %s failed: %s", analyzer.name, result)
                normalized.append(AnalyzerResult(
                    name=analyzer.name,
                    score=0.0,
                    status="failed",
                    error=str(result),
                ))
            elif isinstance(result, AnalysisResponse):
                # If analyzer returned full response, extract its first result
                if result.analyzers:
                    normalized.append(result.analyzers[0])
                else:
                    normalized.append(AnalyzerResult(
                        name=analyzer.name,
                        score=0.0,
                        status="failed",
                        error="Analyzer returned empty results",
                    ))
            else:
                normalized.append(result)

        overall_score = sum(r.score for r in normalized) / len(normalized) if normalized else 0.0
        status = "passed" if overall_score >= 75 else "warning" if overall_score >= 50 else "failed"

        return AnalysisResponse(
            url=context.url,
            overall_score=overall_score,
            status=status,
            analyzers=normalized,
            metadata={
                "analyzer_count": len(normalized),
                "available_count": len(available),
            },
        )

    async def _run_analyzer(self, analyzer: Any, context: AnalysisContext) -> AnalyzerResult:
        """Run a single analyzer and return its result."""
        import time

        start = time.perf_counter()
        try:
            response = analyzer.analyze(context)
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            if isinstance(response, AnalysisResponse):
                # Attach execution time to first analyzer result
                if response.analyzers:
                    response.analyzers[0].execution_time_ms = elapsed_ms
                return response.analyzers[0] if response.analyzers else AnalyzerResult(
                    name=analyzer.name,
                    score=0.0,
                    status="failed",
                    error="Analyzer returned no results",
                )
            return AnalyzerResult(
                name=analyzer.name,
                score=0.0,
                status="failed",
                error="Analyzer returned unexpected type",
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            logger.error("Analyzer %s failed after %.2fms: %s", analyzer.name, elapsed_ms, exc)
            return AnalyzerResult(
                name=analyzer.name,
                score=0.0,
                status="failed",
                error=str(exc),
                execution_time_ms=elapsed_ms,
            )
