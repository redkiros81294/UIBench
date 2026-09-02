"""
Contract tests for core output schemas.

Every analyzer and evaluator must return data compatible with AnalysisResponse.
"""
import pytest
from core.models.report import AnalysisResponse, AnalyzerResult


def test_analyzer_result_defaults():
    result = AnalyzerResult(
        name="test",
        score=85.0,
        status="passed",
    )
    assert result.name == "test"
    assert result.score == 85.0
    assert result.status == "passed"
    assert result.issues == []
    assert result.recommendations == []
    assert result.metrics == {}
    assert result.details == {}
    assert result.execution_time_ms == 0.0
    assert result.error is None


def test_analyzer_result_to_dict():
    result = AnalyzerResult(
        name="seo",
        score=72.5,
        status="warning",
        issues=["Missing meta description"],
        recommendations=["Add meta description"],
        metrics={"score": 72.5},
        details={"checks": 10},
        execution_time_ms=120.5,
        error=None,
    )
    data = result.to_dict()
    assert data["name"] == "seo"
    assert data["score"] == 72.5
    assert data["status"] == "warning"
    assert data["issues"] == ["Missing meta description"]
    assert data["execution_time_ms"] == 120.5


def test_analysis_response_defaults():
    response = AnalysisResponse(url="https://example.com")
    assert response.schema_version == "1.0"
    assert response.url == "https://example.com"
    assert response.overall_score == 0.0
    assert response.status == "needs_review"
    assert response.analyzers == []
    assert response.metadata == {}


def test_analysis_response_to_dict():
    response = AnalysisResponse(
        url="https://example.com",
        overall_score=88.0,
        status="passed",
        analyzers=[
            AnalyzerResult(name="seo", score=88.0, status="passed", issues=[])
        ],
        metadata={"source": "test"},
    )
    data = response.to_dict()
    assert data["schema_version"] == "1.0"
    assert data["url"] == "https://example.com"
    assert data["overall_score"] == 88.0
    assert data["status"] == "passed"
    assert len(data["analyzers"]) == 1
    assert data["analyzers"][0]["name"] == "seo"
    assert data["metadata"]["source"] == "test"


def test_analysis_response_status_failed_on_error():
    response = AnalysisResponse(
        url="https://example.com",
        overall_score=0.0,
        status="failed",
        analyzers=[
            AnalyzerResult(name="broken", score=0.0, status="failed", error="boom")
        ],
    )
    assert response.status == "failed"
    assert response.analyzers[0].error == "boom"
