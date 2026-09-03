"""
Result models. `EvaluationResult.to_dict()` produces exactly the JSON
schema shown in the Design Brief §6:

    {
      "schema_version": "1.0",
      "url": "...",
      "timestamp": "...",
      "overall_score": 88.0,
      "status": "passed",
      "analyzers": [...],
      "metadata": {}
    }
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0"

# Per-analyzer status is threshold-based (see .uibench.toml [thresholds]),
# with a soft "warning" band below the pass threshold before it's a fail.
WARNING_BAND = 15.0


def status_for(score: float, threshold: float) -> str:
    if score >= threshold:
        return "passed"
    if score >= threshold - WARNING_BAND:
        return "warning"
    return "failed"


@dataclass
class Issue:
    message: str
    severity: str = "warning"  # "warning" | "error"


@dataclass
class AnalyzerResult:
    name: str
    score: float
    threshold: float
    status: str = field(init=False)
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0

    def __post_init__(self) -> None:
        self.status = status_for(self.score, self.threshold)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": round(self.score, 1),
            "status": self.status,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
            "details": self.details,
            "execution_time_ms": round(self.execution_time_ms, 1),
        }


@dataclass
class EvaluationResult:
    target: str
    analyzers: list[AnalyzerResult]
    overall_threshold: float = 75.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def overall_score(self) -> float:
        if not self.analyzers:
            return 0.0
        return sum(a.score for a in self.analyzers) / len(self.analyzers)

    @property
    def status(self) -> str:
        return status_for(self.overall_score, self.overall_threshold)

    @property
    def all_issues(self) -> list[tuple[str, str]]:
        """[(analyzer_name, issue_message), ...] across every analyzer."""
        return [(a.name, msg) for a in self.analyzers for msg in a.issues]

    @property
    def all_recommendations(self) -> list[tuple[str, str]]:
        return [(a.name, msg) for a in self.analyzers for msg in a.recommendations]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "url": self.target,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
            "overall_score": round(self.overall_score, 1),
            "status": self.status,
            "analyzers": [a.to_dict() for a in self.analyzers],
            "metadata": self.metadata,
        }
