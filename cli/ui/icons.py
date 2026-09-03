from __future__ import annotations

from dataclasses import dataclass

STATUS_ICONS = {
    "passed": ("\u2705", "[PASS]", "pass"),   # checkmark
    "warning": ("\u26a0\ufe0f", "[WARN]", "warn"),  # warning sign
    "failed": ("\u274c", "[FAIL]", "fail"),   # cross mark
}
REPORT_ICON = ("\U0001F4CA", "[REPORT]", "info")   # bar chart
START_ICON = ("\U0001F680", "[START]", "accent")   # rocket


@dataclass
class RenderOptions:
    unicode: bool = True


def status_glyph(status: str, opts: RenderOptions) -> tuple[str, str]:
    """Returns (glyph_or_ascii, style_name)."""
    glyph, ascii_fallback, style = STATUS_ICONS.get(status, ("?", "[?]", "dim"))
    return (glyph if opts.unicode else ascii_fallback), style


def status_label(status: str, opts: RenderOptions) -> str:
    glyph, style = status_glyph(status, opts)
    return f"{glyph} {status}"
