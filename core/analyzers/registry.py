"""
Analyzer registry for discovery and composition.

The registry holds all available analyzers and provides filtering by
name, category, or availability. The evaluation service uses the registry
to determine which analyzers to run for a given context.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import Analyzer, BrowserAnalyzer


class AnalyzerRegistry:
    """Registry of all available analyzers."""

    def __init__(self) -> None:
        self._analyzers: Dict[str, Analyzer] = {}

    def register(self, analyzer: Analyzer) -> None:
        """Register an analyzer instance.

        Args:
            analyzer: An Analyzer implementation.
        """
        self._analyzers[analyzer.name] = analyzer

    def get(self, name: str) -> Optional[Analyzer]:
        """Get an analyzer by name."""
        return self._analyzers.get(name)

    def all(self) -> List[Analyzer]:
        """Return all registered analyzers."""
        return list(self._analyzers.values())

    def available(self, context: Any = None) -> List[Analyzer]:
        """Return analyzers that can run in the current environment.

        Args:
            context: Optional AnalysisContext to check browser availability.

        Returns:
            List of available analyzers.
        """
        result = []
        for analyzer in self._analyzers.values():
            if not analyzer.is_available():
                continue
            if isinstance(analyzer, BrowserAnalyzer) and not getattr(context, "page", None):
                continue
            result.append(analyzer)
        return result

    def by_category(self, category: str) -> List[Analyzer]:
        """Return analyzers matching a category."""
        return [a for a in self._analyzers.values() if a.category == category]

    def by_names(self, names: List[str]) -> List[Analyzer]:
        """Return analyzers matching a list of names."""
        return [self._analyzers[n] for n in names if n in self._analyzers]

    def categories(self) -> List[str]:
        """Return all unique category names."""
        return list({a.category for a in self._analyzers.values()})
