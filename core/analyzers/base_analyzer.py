"""
Base analyzer class enforcing the UIBench output contract.

All analyzers must inherit from BaseAnalyzer and return an AnalysisResponse.
"""
from __future__ import annotations

import json
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.report import AnalysisResponse, AnalyzerResult


class BaseAnalyzer(ABC):
    """Abstract base class for all UIBench analyzers.

    Enforces a stable output contract so backend and frontend can rely on
    a consistent schema regardless of which analyzers are enabled.
    """

    name: str = "base"
    description: str = "Base analyzer"
    output_dir: str = "analysis_results"

    def __init__(self, output_dir: str = "analysis_results") -> None:
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @abstractmethod
    def analyze(self, url: str, html: str, **kwargs: Any) -> AnalysisResponse:
        """Run analysis and return a normalized AnalysisResponse.

        Args:
            url: The URL being analyzed.
            html: Raw HTML content.
            **kwargs: Analyzer-specific options.

        Returns:
            AnalysisResponse with at least one AnalyzerResult.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Response builders
    # ------------------------------------------------------------------

    def _build_response(
        self,
        url: str,
        score: float,
        status: str,
        issues: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        execution_time_ms: float = 0.0,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AnalysisResponse:
        """Build a single-analyzer AnalysisResponse."""
        result = AnalyzerResult(
            name=self.name,
            score=score,
            status=status,
            issues=issues or [],
            recommendations=recommendations or [],
            metrics=metrics or {},
            details=details or {},
            execution_time_ms=execution_time_ms,
            error=error,
        )
        merged_metadata = {
            "analyzer": self.name,
            "description": self.description,
        }
        if metadata:
            merged_metadata.update(metadata)

        return AnalysisResponse(
            url=url,
            overall_score=score if not error else 0.0,
            status=status if not error else "failed",
            analyzers=[result],
            metadata=merged_metadata,
        )

    # ------------------------------------------------------------------
    # JSON persistence helpers
    # ------------------------------------------------------------------

    def _generate_json_filename(self, url: str, analyzer_name: str) -> str:
        """Generate a unique filename for the JSON output."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_url = url.replace("://", "_").replace("/", "_").replace(".", "_")
        return os.path.join(self.output_dir, f"{analyzer_name}_{safe_url}_{timestamp}.json")

    def save_to_json(self, data: Dict[str, Any], url: str, analyzer_name: str) -> str:
        """Save analysis results to a JSON file."""
        filename = self._generate_json_filename(url, analyzer_name)
        payload = {
            "metadata": {
                "analyzer": analyzer_name,
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            },
            "results": data,
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return filename

    # ------------------------------------------------------------------
    # Legacy normalization helpers
    # ------------------------------------------------------------------

    def _standardize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize the results structure for JSON output."""
        standardized = {
            "score": results.get("overall_score", 0),
            "issues": results.get("issues", []),
            "passes": results.get("passes", []),
            "details": results.get("details", {}),
            "recommendations": results.get("recommendations", []),
            "metrics": results.get("metrics", {}),
        }
        return {k: v for k, v in standardized.items() if v is not None}

    def _time_execution(self, func, *args, **kwargs):
        """Time an analyzer call and return (result, elapsed_ms)."""
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result, (time.perf_counter() - start) * 1000.0
        except Exception as exc:
            raise exc
