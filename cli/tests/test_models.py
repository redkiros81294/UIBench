from cli.models import AnalyzerResult, EvaluationResult, status_for


def test_status_for_pass():
    assert status_for(90, threshold=75) == "passed"
    assert status_for(75, threshold=75) == "passed"


def test_status_for_warning_band():
    # warning band is [threshold - 15, threshold)
    assert status_for(65, threshold=75) == "warning"
    assert status_for(60, threshold=75) == "warning"


def test_status_for_failed():
    assert status_for(59, threshold=75) == "failed"
    assert status_for(0, threshold=75) == "failed"


def test_analyzer_result_computes_status():
    a = AnalyzerResult(name="seo", score=88, threshold=75)
    assert a.status == "passed"


def test_evaluation_result_overall_score_is_average():
    result = EvaluationResult(
        target="https://example.com",
        analyzers=[
            AnalyzerResult(name="seo", score=80, threshold=75),
            AnalyzerResult(name="performance", score=60, threshold=75),
        ],
    )
    assert result.overall_score == 70.0


def test_evaluation_result_to_dict_matches_schema():
    result = EvaluationResult(
        target="https://example.com",
        analyzers=[AnalyzerResult(name="seo", score=88, threshold=75)],
    )
    payload = result.to_dict()
    assert payload["schema_version"] == "1.0"
    assert payload["url"] == "https://example.com"
    assert payload["status"] == "passed"
    assert payload["analyzers"][0]["name"] == "seo"


def test_empty_evaluation_has_zero_score():
    result = EvaluationResult(target="https://example.com", analyzers=[])
    assert result.overall_score == 0.0
