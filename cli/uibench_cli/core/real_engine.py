"""
Real engine adapter bridging the CLI protocol to the UIBench core.

Implements `AnalyzerEngine` using:
- `RegistryPageEvaluator` for live URL evaluation
- `ProjectAnalyzer` for local project analysis
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from uibench_cli.core.engine import EvaluateOptions
from uibench_cli.core.exceptions import CoreEngineError, NetworkError
from uibench_cli.models import AnalyzerResult, EvaluationResult

try:
    from core.evaluators import RegistryPageEvaluator
    from core.project_analyzer import ProjectAnalyzer
    from core.models.report import AnalysisResponse
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


class RealEngine:
    """Real UIBench core engine adapter."""

    def __init__(self, playwright_timeout: int = 60000) -> None:
        self.playwright_timeout = playwright_timeout

    def evaluate(self, target: str, options: EvaluateOptions) -> EvaluationResult:
        if not CORE_AVAILABLE:
            raise CoreEngineError(
                "UIBench core is not installed.",
                suggestion="pip install -e .[cli]",
            )

        if target.startswith("http://") or target.startswith("https://"):
            return asyncio.run(self._evaluate_url(target, options))
        else:
            return self._evaluate_project(target, options)

    async def _evaluate_url(self, url: str, options: EvaluateOptions) -> EvaluationResult:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise CoreEngineError(
                "Playwright is not installed.",
                detail="Browser-based analysis requires Playwright.",
                suggestion="pip install playwright && playwright install chromium",
            ) from exc

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=self.playwright_timeout)
                html = await page.content()
                body_text = await page.inner_text("body")
                await page.close()
                await browser.close()

            evaluator = RegistryPageEvaluator(url, html, None, body_text)
            response = await evaluator.evaluate()
            return self._map_response(response, url)
        except Exception as exc:
            raise NetworkError(
                f"Could not reach {url}",
                detail=str(exc),
                suggestion=f"uibench evaluate {url} --timeout {options.timeout * 2}",
            ) from exc

    def _evaluate_project(self, path: str, options: EvaluateOptions) -> EvaluationResult:
        project_path = Path(path)
        if not project_path.exists():
            raise CoreEngineError(
                f"Project path does not exist: {path}",
                suggestion="Check the path and try again.",
            )

        try:
            analyzer = ProjectAnalyzer(project_path)
            result = asyncio.run(analyzer.analyze_project())
            return self._map_project_result(result, path)
        except Exception as exc:
            raise CoreEngineError(
                f"Project analysis failed: {exc}",
                suggestion="Ensure the project path is valid and dependencies are installed.",
            ) from exc

    def _map_response(self, response: AnalysisResponse, target: str) -> EvaluationResult:
        analyzers = []
        for item in response.analyzers:
            analyzers.append(
                AnalyzerResult(
                    name=item.name,
                    score=item.score,
                    threshold=75.0,  # default threshold
                    issues=item.issues or [],
                    recommendations=item.recommendations or [],
                    metrics=item.metrics or {},
                    details=item.details or {},
                    execution_time_ms=item.execution_time_ms or 0.0,
                )
            )
        return EvaluationResult(
            target=target,
            analyzers=analyzers,
            metadata=response.metadata or {},
        )

    def _map_project_result(self, result: dict, target: str) -> EvaluationResult:
        analyzers = []
        static = result.get("current", {}).get("static", {})
        for category, data in static.items():
            if isinstance(data, dict) and "score" in data:
                analyzers.append(
                    AnalyzerResult(
                        name=category,
                        score=float(data.get("score", 0)),
                        threshold=75.0,
                        issues=data.get("issues", []),
                        recommendations=data.get("recommendations", []),
                        metrics=data.get("metrics", {}),
                        details=data.get("details", {}),
                    )
                )
        return EvaluationResult(
            target=target,
            analyzers=analyzers,
            metadata={"source": "project_analyzer"},
        )
