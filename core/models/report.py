"""
Standardized output models for UIBench core analysis.

Every public analyzer entrypoint must return an AnalysisResponse.
This module defines the non-negotiable contract that backend and frontend depend on.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AnalyzerResult:
    """Normalized result from a single analyzer."""

    name: str
    score: float
    status: str  # "passed" | "warning" | "failed" | "skipped"
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "status": self.status,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
            "details": self.details,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
        }


@dataclass
class AnalysisResponse:
    """Top-level response returned by every core analysis entrypoint."""

    schema_version: str = "1.0"
    url: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    overall_score: float = 0.0
    status: str = "needs_review"  # "passed" | "warning" | "failed" | "skipped"
    analyzers: List[AnalyzerResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "url": self.url,
            "timestamp": self.timestamp,
            "overall_score": self.overall_score,
            "status": self.status,
            "analyzers": [a.to_dict() for a in self.analyzers],
            "metadata": self.metadata,
        }
