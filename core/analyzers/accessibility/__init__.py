"""
Accessibility analyzers package.
"""
from .alt_text import AltTextAnalyzer
from .headings import AccessibilityHeadingsAnalyzer

__all__ = ["AltTextAnalyzer", "AccessibilityHeadingsAnalyzer"]
