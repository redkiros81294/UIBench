"""
Base analyzer classes following Interface Segregation Principle.

All analyzers implement `Analyzer`. Browser-based analyzers additionally
implement `BrowserAnalyzer`. Persistence-aware analyzers implement `Persistable`.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models.report import AnalysisResponse, AnalyzerResult
from ..models.context import AnalysisContext


class Analyzer(ABC):
    """Core analyzer interface.

    Every analyzer in the system must implement this ABC.
    """

    name: str = "base"
    category: str = "general"
    description: str = ""

    @abstractmethod
    def analyze(self, context: AnalysisContext) -> AnalysisResponse:
        """Run analysis and return a normalized AnalysisResponse.

        Args:
            context: Shared analysis context with URL, HTML, soup, etc.

        Returns:
            AnalysisResponse containing at least one AnalyzerResult.
        """
        raise NotImplementedError

    def is_available(self) -> bool:
        """Return True if this analyzer can run in the current environment.

        Override to check for optional dependencies like Playwright, ZAP, etc.
        """
        return True


class BrowserAnalyzer(Analyzer):
    """Optional interface for analyzers that require a Playwright page.

    The evaluation service will only invoke these when `context.page` is set
    and `config.enable_browser` is true.
    """

    def requires_browser(self) -> bool:
        return True


class Persistable(ABC):
    """Optional interface for analyzers that can persist results."""

    @abstractmethod
    def save(self, response: AnalysisResponse, path: str) -> str:
        """Save analysis results to disk.

        Args:
            response: The analysis response to save.
            path: Destination file path.

        Returns:
            The path where results were saved.
        """
        raise NotImplementedError
