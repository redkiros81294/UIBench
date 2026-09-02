"""
Analysis orchestrator service.

Thin wrapper over core that normalizes output into the backend contract.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """Orchestrates core analysis and normalizes output for the API layer."""

    def __init__(self, analysis_collection, project_collection) -> None:
        self.analysis_collection = analysis_collection
        self.project_collection = project_collection

    async def evaluate_and_store_async(self, url: str, project_id: str, owner_id: str) -> Dict[str, Any]:
        result_id = str(uuid.uuid4())
        now = datetime.utcnow()

        self.analysis_collection.insert_one({
            "result_id": result_id,
            "project_id": project_id,
            "user_id": owner_id,
            "url": url,
            "status": "in_progress",
            "score": None,
            "details": None,
            "analysis_date": now,
        })

        self.project_collection.update_one(
            {"project_id": project_id},
            {"$push": {"analysis_result_ids": result_id}, "$set": {"last_updated": datetime.utcnow()}},
        )

        import asyncio
        asyncio.create_task(self._run_evaluation(result_id, url, project_id, owner_id))
        return {"message": "Evaluation started in background", "result_id": result_id, "queued_at": now}

    async def _run_evaluation(self, result_id: str, url: str, project_id: str, owner_id: str) -> None:
        try:
            from playwright.async_api import async_playwright
            from core.engine import WebsiteEvaluator

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=60000)
                html = await page.content()
                body_text = await page.inner_text("body")

                evaluator = WebsiteEvaluator(
                    root_url=url,
                    max_subpages=5,
                    max_depth=2,
                    concurrency=2,
                    custom_criteria={},
                    page=page,
                )
                raw = await evaluator.evaluate_page(html, body_text)

                # Normalize to core contract if evaluator returns legacy format
                normalized = self._normalize(raw)

                self.analysis_collection.update_one(
                    {"result_id": result_id},
                    {"$set": {"status": "completed", "result": normalized, "analysis_date": datetime.utcnow()}},
                )
        except Exception as exc:
            logger.exception("Evaluation failed for result_id=%s", result_id)
            self.analysis_collection.update_one(
                {"result_id": result_id},
                {"$set": {"status": "failed", "error": str(exc)}},
            )

    def _normalize(self, raw: Any) -> Dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        return {"raw": str(raw)}

    def get_analysis_by_id(self, result_id: str) -> Dict[str, Any]:
        result = self.analysis_collection.find_one({"result_id": result_id}, {"_id": 0})
        if result:
            return result
        return {"error": f"Analysis result with ID {result_id} not found"}

    def get_all_analyses_for_project(self, project_id: str) -> list[Dict[str, Any]]:
        results = list(self.analysis_collection.find({"project_id": project_id}, {"_id": 0}))
        if results:
            return results
        return [{"error": "No analyses found for this project"}]

    def delete_analysis(self, result_id: str) -> Dict[str, Any]:
        result = self.analysis_collection.delete_one({"result_id": result_id})
        if result.deleted_count == 1:
            return {"message": "Analysis result deleted"}
        return {"error": "Analysis result not found"}
