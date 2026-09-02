"""
UIBench Core Package

Heavy analyzers are exposed via lazy imports to keep startup cost low.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .analyzers import (
        AccessibilityAnalyzer,
        PerformanceAnalyzer,
        SEOAnalyzer,
        SecurityAnalyzer,
        UXAnalyzer,
        CodeAnalyzer,
        DesignSystemAnalyzer,
        NLPContentAnalyzer,
        InfrastructureAnalyzer,
        OperationalMetricsAnalyzer,
        ComplianceAnalyzer,
        MutationAnalyzer,
        ContractAnalyzer,
        FuzzAnalyzer,
    )
    from .evaluators import PageEvaluator, WebsiteEvaluator
    from .browser import BrowserManager
    from .config import Settings

__all__ = [
    "AccessibilityAnalyzer",
    "PerformanceAnalyzer",
    "SEOAnalyzer",
    "SecurityAnalyzer",
    "UXAnalyzer",
    "CodeAnalyzer",
    "DesignSystemAnalyzer",
    "NLPContentAnalyzer",
    "InfrastructureAnalyzer",
    "OperationalMetricsAnalyzer",
    "ComplianceAnalyzer",
    "MutationAnalyzer",
    "ContractAnalyzer",
    "FuzzAnalyzer",
    "PageEvaluator",
    "WebsiteEvaluator",
    "BrowserManager",
    "Settings",
]


def __getattr__(name: str):
    """Lazy-load heavy core symbols on first access."""
    _import_map = {
        "AccessibilityAnalyzer": (".analyzers", "AccessibilityAnalyzer"),
        "PerformanceAnalyzer": (".analyzers", "PerformanceAnalyzer"),
        "SEOAnalyzer": (".analyzers", "SEOAnalyzer"),
        "SecurityAnalyzer": (".analyzers", "SecurityAnalyzer"),
        "UXAnalyzer": (".analyzers", "UXAnalyzer"),
        "CodeAnalyzer": (".analyzers", "CodeAnalyzer"),
        "DesignSystemAnalyzer": (".analyzers", "DesignSystemAnalyzer"),
        "NLPContentAnalyzer": (".analyzers", "NLPContentAnalyzer"),
        "InfrastructureAnalyzer": (".analyzers", "InfrastructureAnalyzer"),
        "OperationalMetricsAnalyzer": (".analyzers", "OperationalMetricsAnalyzer"),
        "ComplianceAnalyzer": (".analyzers", "ComplianceAnalyzer"),
        "MutationAnalyzer": (".analyzers", "MutationAnalyzer"),
        "ContractAnalyzer": (".analyzers", "ContractAnalyzer"),
        "FuzzAnalyzer": (".analyzers", "FuzzAnalyzer"),
        "PageEvaluator": (".evaluators", "PageEvaluator"),
        "WebsiteEvaluator": (".evaluators", "WebsiteEvaluator"),
        "BrowserManager": (".browser", "BrowserManager"),
        "Settings": (".config", "Settings"),
    }
    if name in _import_map:
        module_name, attr = _import_map[name]
        import importlib

        module = importlib.import_module(module_name, __name__)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
