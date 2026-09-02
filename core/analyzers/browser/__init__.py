"""
Browser analyzers package (opt-in).

These require Playwright and are only loaded when explicitly enabled.
"""
from .axe_accessibility import AxeAccessibilityAnalyzer
from .performance import BrowserPerformanceAnalyzer

__all__ = ["AxeAccessibilityAnalyzer", "BrowserPerformanceAnalyzer"]
