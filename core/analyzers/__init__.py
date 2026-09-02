"""
Core analyzers package.

Analyzers are organized by category for maintainability.
The registry auto-discovers analyzers from subpackages.
"""
from .base import Analyzer, BrowserAnalyzer, Persistable
from .registry import AnalyzerRegistry

__all__ = [
    "Analyzer",
    "BrowserAnalyzer",
    "Persistable",
    "AnalyzerRegistry",
]


def build_default_registry() -> AnalyzerRegistry:
    """Build and return the default analyzer registry.

    This imports analyzers lazily to avoid heavy dependency loading
    at startup time.
    """
    registry = AnalyzerRegistry()

    # Static analyzers (pure Python, no browser required)
    from .seo.meta_tags import MetaTagsAnalyzer
    from .seo.headings import HeadingsAnalyzer
    from .seo.images import ImageSEOAnalyzer
    from .accessibility.alt_text import AltTextAnalyzer
    from .accessibility.headings import AccessibilityHeadingsAnalyzer
    from .performance.page_size import PageSizeAnalyzer
    from .design_system.css_variables import CSSVariablesAnalyzer
    from .nlp.readability import ReadabilityAnalyzer
    from .nlp.sentiment import SentimentAnalyzer

    for analyzer_cls in [
        MetaTagsAnalyzer,
        HeadingsAnalyzer,
        ImageSEOAnalyzer,
        AltTextAnalyzer,
        AccessibilityHeadingsAnalyzer,
        PageSizeAnalyzer,
        CSSVariablesAnalyzer,
        ReadabilityAnalyzer,
        SentimentAnalyzer,
    ]:
        registry.register(analyzer_cls())

    # Browser analyzers (opt-in via --browser or config)
    try:
        from .browser.axe_accessibility import AxeAccessibilityAnalyzer
        from .browser.performance import BrowserPerformanceAnalyzer

        for analyzer_cls in [
            AxeAccessibilityAnalyzer,
            BrowserPerformanceAnalyzer,
        ]:
            registry.register(analyzer_cls())
    except ImportError:
        pass

    return registry
