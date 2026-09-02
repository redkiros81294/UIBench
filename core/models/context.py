"""
Analysis context DTO.

All analyzers receive an AnalysisContext instead of raw parameters.
This decouples analyzers from Playwright, spaCy, and other heavy dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .report import AnalysisResponse


@dataclass
class AnalysisContext:
    """Shared input object for all analyzers.

    Attributes:
        url: The URL being analyzed.
        html: Raw HTML content.
        soup: Parsed BeautifulSoup object. Created from html if not provided.
        page: Playwright Page object, if available.
        body_text: Extracted visible text from the page.
        design_data: Optional design system data (Figma/Sketch).
        config: Core settings.
    """

    url: str = ""
    html: str = ""
    soup: Any = None
    page: Any = None
    body_text: str = ""
    design_data: Dict[str, Any] = field(default_factory=dict)
    config: Any = None

    def __post_init__(self):
        if self.soup is None and self.html:
            from bs4 import BeautifulSoup

            self.soup = BeautifulSoup(self.html, "html.parser")
