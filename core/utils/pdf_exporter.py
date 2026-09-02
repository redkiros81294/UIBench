"""
PDF export for UIBench evaluation reports.

Design:
- Body text: Nyala font
- Logo / titles: system font (DejaVu Sans)
- Brand colors matching UIBench tokens
- 4-page structure: Cover, Executive Summary, Detailed Analysis, Appendix
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from core.models.report import AnalysisResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Brand tokens
# ---------------------------------------------------------------------------
BG_PRIMARY = colors.HexColor("#0A0F1E")
BG_SECONDARY = colors.HexColor("#0D1B3E")
BG_TERTIARY = colors.HexColor("#111827")
BORDER = colors.HexColor("#1E3A5F")
BORDER_BRIGHT = colors.HexColor("#2563EB")
TEXT_PRIMARY = colors.HexColor("#F1F5F9")
TEXT_SECONDARY = colors.HexColor("#94A3B8")
TEXT_MUTED = colors.HexColor("#475569")
CYAN = colors.HexColor("#06B6D4")
BLUE = colors.HexColor("#2563EB")
GREEN = colors.HexColor("#10B981")
AMBER = colors.HexColor("#F59E0B")
RED = colors.HexColor("#EF4444")
PURPLE = colors.HexColor("#8B5CF6")

STATUS_COLORS = {
    "passed": GREEN,
    "warning": AMBER,
    "failed": RED,
    "skipped": TEXT_MUTED,
    "needs_review": TEXT_SECONDARY,
}

# ---------------------------------------------------------------------------
# Font setup
# ---------------------------------------------------------------------------
NYALA_PATH = Path.home() / ".fonts" / "nyala.ttf"
SYSTEM_FONT_PATHS = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
]

_BODY_FONT = "Nyala"
_LOGO_FONT = "DejaVu-Sans"


def _register_fonts() -> tuple[str, str]:
    """Register Nyala for body and a system font for logo/titles."""
    body_font = "Helvetica"
    logo_font = "Helvetica"

    if NYALA_PATH.exists():
        try:
            pdfmetrics.registerFont(TTFont("Nyala", str(NYALA_PATH)))
            body_font = "Nyala"
        except Exception as exc:
            logger.warning("Failed to register Nyala font: %s", exc)
    else:
        logger.warning("Nyala font not found at %s", NYALA_PATH)

    for path in SYSTEM_FONT_PATHS:
        if path.exists():
            try:
                pdfmetrics.registerFont(TTFont("DejaVu-Sans", str(path)))
                logo_font = "DejaVu-Sans"
                break
            except Exception as exc:
                logger.warning("Failed to register system font %s: %s", path, exc)

    return body_font, logo_font


BODY_FONT, LOGO_FONT = _register_fonts()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _status_badge(status: str) -> tuple[str, colors.Color]:
    """Return (label, color) for a status value."""
    status = (status or "needs_review").lower().strip()
    color = STATUS_COLORS.get(status, TEXT_SECONDARY)
    label = status.replace("_", " ").title()
    return label, color


def _normalize_input(
    data: Union[Dict[str, Any], AnalysisResponse],
) -> Dict[str, Any]:
    """Accept AnalysisResponse or dict and return a plain dict."""
    if isinstance(data, AnalysisResponse):
        return data.to_dict()
    if isinstance(data, dict):
        return data
    raise TypeError(f"Unsupported report type: {type(data).__name__}")


# ---------------------------------------------------------------------------
# PDFExporter
# ---------------------------------------------------------------------------

class PDFExporter:
    """Export UIBench evaluation results to a branded PDF."""

    @staticmethod
    def export_results(
        results: Union[Dict[str, Any], AnalysisResponse],
        filename: Optional[str] = None,
    ) -> bytes:
        """Generate PDF bytes from evaluation results.

        Args:
            results: AnalysisResponse or compatible dict.
            filename: Ignored; retained for backward compatibility.

        Returns:
            PDF content as bytes.
        """
        data = _normalize_input(results)
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        page_width = doc.width
        story: List[Any] = []

        # Page 1: Cover
        PDFExporter._add_cover(story, data, page_width)
        story.append(PageBreak())

        # Page 2: Executive Summary
        PDFExporter._add_executive_summary(story, data, page_width)
        story.append(PageBreak())

        # Page 3+: Detailed Analysis
        PDFExporter._add_detailed_analysis(story, data, page_width)
        story.append(PageBreak())

        # Final page: Appendix
        PDFExporter._add_appendix(story, data, page_width)

        doc.build(story)
        return buffer.getvalue()

    # ------------------------------------------------------------------
    # Page 1 — Cover
    # ------------------------------------------------------------------

    @staticmethod
    def _add_cover(story: List[Any], data: Dict[str, Any], page_width: float) -> None:
        logo_style = ParagraphStyle(
            "Logo",
            fontName=LOGO_FONT,
            fontSize=32,
            leading=36,
            alignment=TA_CENTER,
            textColor=CYAN,
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "CoverSubtitle",
            fontName=BODY_FONT,
            fontSize=13,
            leading=17,
            alignment=TA_CENTER,
            textColor=TEXT_SECONDARY,
            spaceAfter=24,
        )
        meta_label_style = ParagraphStyle(
            "MetaLabel",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_SECONDARY,
        )
        meta_value_style = ParagraphStyle(
            "MetaValue",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_PRIMARY,
        )
        score_value_style = ParagraphStyle(
            "CoverScoreValue",
            fontName=LOGO_FONT,
            fontSize=44,
            leading=48,
            alignment=TA_CENTER,
            textColor=TEXT_PRIMARY,
            spaceAfter=6,
        )
        score_status_style = ParagraphStyle(
            "CoverScoreStatus",
            fontName=BODY_FONT,
            fontSize=12,
            leading=15,
            alignment=TA_CENTER,
            textColor=TEXT_SECONDARY,
            spaceAfter=20,
        )

        story.append(Spacer(1, 50))

        # Logo / brand
        story.append(Paragraph("UIBench", logo_style))
        story.append(Paragraph("Website Evaluation Report", subtitle_style))
        story.append(Spacer(1, 30))

        # Overall score callout
        overall_score = float(data.get("overall_score", 0) or 0)
        status_label, status_color = _status_badge(data.get("status", "needs_review"))

        score_table_data = [
            [Paragraph(f"{overall_score:.1f}/100", score_value_style)],
            [Paragraph(status_label, score_status_style)],
        ]
        score_table = Table(score_table_data, colWidths=[page_width])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_SECONDARY),
            ("LEFTPADDING", (0, 0), (-1, -1), 24),
            ("RIGHTPADDING", (0, 0), (-1, -1), 24),
            ("TOPPADDING", (0, 0), (-1, -1), 18),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
            ("LINEBELOW", (0, 0), (-1, 0), 2, BORDER_BRIGHT),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 26))

        # Meta info
        url = data.get("url", "N/A")
        timestamp = data.get("timestamp", "N/A")
        analyzers = data.get("analyzers", [])
        analyzer_names = [
            a.get("name", a) if isinstance(a, dict) else str(a) for a in analyzers
        ]
        analyzers_used = ", ".join(analyzer_names) if analyzer_names else "N/A"

        meta_data = [
            [Paragraph("Target URL", meta_label_style), Paragraph(str(url), meta_value_style)],
            [Paragraph("Timestamp", meta_label_style), Paragraph(str(timestamp), meta_value_style)],
            [Paragraph("Analyzers", meta_label_style), Paragraph(analyzers_used, meta_value_style)],
        ]
        meta_table = Table(
            meta_data, colWidths=[page_width * 0.28, page_width * 0.72]
        )
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), BG_SECONDARY),
            ("BACKGROUND", (1, 0), (1, -1), BG_TERTIARY),
            ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_PRIMARY),
            ("FONTNAME", (0, 0), (-1, -1), BODY_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(meta_table)

    # ------------------------------------------------------------------
    # Page 2 — Executive Summary
    # ------------------------------------------------------------------

    @staticmethod
    def _add_executive_summary(
        story: List[Any], data: Dict[str, Any], page_width: float
    ) -> None:
        header_style = ParagraphStyle(
            "ESHeader",
            fontName=LOGO_FONT,
            fontSize=18,
            leading=22,
            alignment=TA_LEFT,
            textColor=CYAN,
            spaceAfter=14,
        )
        section_style = ParagraphStyle(
            "ESSection",
            fontName=LOGO_FONT,
            fontSize=13,
            leading=16,
            alignment=TA_LEFT,
            textColor=TEXT_PRIMARY,
            spaceAfter=8,
            spaceBefore=14,
        )
        body_style = ParagraphStyle(
            "ESBody",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_SECONDARY,
        )
        bullet_style = ParagraphStyle(
            "ESBullet",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_PRIMARY,
            leftIndent=12,
            spaceAfter=4,
        )

        story.append(Paragraph("Executive Summary", header_style))

        # Overall score card
        overall_score = float(data.get("overall_score", 0) or 0)
        status_label, status_color = _status_badge(data.get("status", "needs_review"))

        score_rows = [
            [Paragraph(f"<b>Overall Score:</b> {overall_score:.1f}/100", body_style)],
            [Paragraph(f"<b>Status:</b> {status_label}", body_style)],
        ]
        score_table = Table(score_rows, colWidths=[page_width])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_SECONDARY),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINEBELOW", (0, 0), (-1, 0), 2, BORDER_BRIGHT),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 14))

        # Analyzer breakdown
        story.append(Paragraph("Analyzer Breakdown", section_style))

        analyzers: List[Dict[str, Any]] = data.get("analyzers", [])
        if not analyzers:
            story.append(Paragraph("No analyzer results available.", body_style))
            return

        table_data: List[List[Any]] = [
            [
                Paragraph("<b>Analyzer</b>", body_style),
                Paragraph("<b>Score</b>", body_style),
                Paragraph("<b>Status</b>", body_style),
                Paragraph("<b>Issues</b>", body_style),
            ]
        ]
        for item in analyzers:
            name = item.get("name", "Unknown") if isinstance(item, dict) else str(item)
            score = float(item.get("score", 0) or 0) if isinstance(item, dict) else 0.0
            status = item.get("status", "needs_review") if isinstance(item, dict) else "needs_review"
            issues_count = len(item.get("issues", [])) if isinstance(item, dict) else 0
            label, _ = _status_badge(status)

            table_data.append([
                Paragraph(str(name), body_style),
                Paragraph(f"{score:.1f}/100", body_style),
                Paragraph(label, body_style),
                Paragraph(str(issues_count), body_style),
            ])

        col_widths = [page_width * 0.40, page_width * 0.18, page_width * 0.22, page_width * 0.20]
        analyzer_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        analyzer_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_SECONDARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), CYAN),
            ("FONTNAME", (0, 0), (-1, 0), LOGO_FONT),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), BG_TERTIARY),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_PRIMARY),
            ("FONTNAME", (0, 1), (-1, -1), BODY_FONT),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_TERTIARY, BG_SECONDARY]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(analyzer_table)
        story.append(Spacer(1, 16))

        # Top issues
        story.append(Paragraph("Top Issues", section_style))
        all_issues: List[str] = []
        for item in analyzers:
            if isinstance(item, dict):
                for issue in item.get("issues", [])[:3]:
                    all_issues.append(f"• {issue}")
        if all_issues:
            for issue_text in all_issues[:10]:
                story.append(Paragraph(issue_text, bullet_style))
        else:
            story.append(Paragraph("No issues detected.", body_style))

        story.append(Spacer(1, 12))

        # Top recommendations
        story.append(Paragraph("Top Recommendations", section_style))
        all_recs: List[str] = []
        for item in analyzers:
            if isinstance(item, dict):
                for rec in item.get("recommendations", [])[:3]:
                    all_recs.append(f"• {rec}")
        if all_recs:
            for rec_text in all_recs[:10]:
                story.append(Paragraph(rec_text, bullet_style))
        else:
            story.append(Paragraph("No recommendations at this time.", body_style))

    # ------------------------------------------------------------------
    # Page 3+ — Detailed Analysis
    # ------------------------------------------------------------------

    @staticmethod
    def _add_detailed_analysis(
        story: List[Any], data: Dict[str, Any], page_width: float
    ) -> None:
        header_style = ParagraphStyle(
            "DAHeader",
            fontName=LOGO_FONT,
            fontSize=18,
            leading=22,
            alignment=TA_LEFT,
            textColor=CYAN,
            spaceAfter=14,
        )
        section_header_style = ParagraphStyle(
            "DASectionHeader",
            fontName=LOGO_FONT,
            fontSize=13,
            leading=16,
            alignment=TA_LEFT,
            textColor=TEXT_PRIMARY,
            spaceAfter=8,
            spaceBefore=12,
        )
        body_style = ParagraphStyle(
            "DABody",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_SECONDARY,
        )
        bullet_style = ParagraphStyle(
            "DABullet",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_PRIMARY,
            leftIndent=12,
            spaceAfter=4,
        )
        metric_label_style = ParagraphStyle(
            "DAMetricLabel",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_SECONDARY,
        )
        metric_value_style = ParagraphStyle(
            "DAMetricValue",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_PRIMARY,
        )

        story.append(Paragraph("Detailed Analysis", header_style))
        story.append(Spacer(1, 6))

        analyzers: List[Dict[str, Any]] = data.get("analyzers", [])
        if not analyzers:
            story.append(Paragraph("No detailed analysis available.", body_style))
            return

        for item in analyzers:
            if not isinstance(item, dict):
                continue

            name = item.get("name", "Unknown")
            score = float(item.get("score", 0) or 0)
            status = item.get("status", "needs_review")
            issues: List[str] = item.get("issues", []) or []
            recommendations: List[str] = item.get("recommendations", []) or []
            metrics: Dict[str, Any] = item.get("metrics", {}) or {}
            error = item.get("error")

            status_label, status_color = _status_badge(status)

            section: List[Any] = []

            # Section header with score pill
            score_pill_style = ParagraphStyle(
                "ScorePill",
                fontName=LOGO_FONT,
                fontSize=10,
                leading=12,
                alignment=TA_CENTER,
                textColor=colors.white,
            )
            header_data = [
                [
                    Paragraph(f"<b>{name}</b>", section_header_style),
                    Paragraph(
                        f'<font color="white">{score:.1f}/100</font>',
                        score_pill_style,
                    ),
                ]
            ]
            header_table = Table(header_data, colWidths=[page_width * 0.78, page_width * 0.22])
            header_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), BG_SECONDARY),
                ("BACKGROUND", (1, 0), (1, 0), status_color),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, 0), 1, BORDER),
            ]))
            section.append(header_table)
            section.append(Spacer(1, 6))

            # Status + error
            info_rows = [
                [Paragraph("<b>Status:</b>", metric_label_style), Paragraph(status_label, metric_value_style)],
            ]
            if error:
                info_rows.append([
                    Paragraph("<b>Error:</b>", metric_label_style),
                    Paragraph(str(error), metric_value_style),
                ])
            info_table = Table(info_rows, colWidths=[page_width * 0.22, page_width * 0.78])
            info_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BG_TERTIARY),
                ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_PRIMARY),
                ("FONTNAME", (0, 0), (-1, -1), BODY_FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            section.append(info_table)
            section.append(Spacer(1, 8))

            # Issues
            if issues:
                section.append(Paragraph("<b>Issues</b>", body_style))
                for issue in issues:
                    section.append(Paragraph(f"• {issue}", bullet_style))
                section.append(Spacer(1, 6))

            # Recommendations
            if recommendations:
                section.append(Paragraph("<b>Recommendations</b>", body_style))
                for rec in recommendations:
                    section.append(Paragraph(f"• {rec}", bullet_style))
                section.append(Spacer(1, 6))

            # Metrics
            if metrics:
                section.append(Paragraph("<b>Metrics</b>", body_style))
                metric_rows = []
                for k, v in metrics.items():
                    metric_rows.append([
                        Paragraph(str(k), metric_label_style),
                        Paragraph(str(v), metric_value_style),
                    ])
                m_table = Table(metric_rows, colWidths=[page_width * 0.45, page_width * 0.55])
                m_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), BG_TERTIARY),
                    ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_PRIMARY),
                    ("FONTNAME", (0, 0), (-1, -1), BODY_FONT),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BG_TERTIARY, BG_SECONDARY]),
                ]))
                section.append(m_table)
                section.append(Spacer(1, 8))

            story.append(KeepTogether(section))
            story.append(Spacer(1, 4))

    # ------------------------------------------------------------------
    # Final page — Appendix
    # ------------------------------------------------------------------

    @staticmethod
    def _add_appendix(
        story: List[Any], data: Dict[str, Any], page_width: float
    ) -> None:
        header_style = ParagraphStyle(
            "AppHeader",
            fontName=LOGO_FONT,
            fontSize=18,
            leading=22,
            alignment=TA_LEFT,
            textColor=CYAN,
            spaceAfter=14,
        )
        section_style = ParagraphStyle(
            "AppSection",
            fontName=LOGO_FONT,
            fontSize=13,
            leading=16,
            alignment=TA_LEFT,
            textColor=TEXT_PRIMARY,
            spaceAfter=8,
            spaceBefore=14,
        )
        body_style = ParagraphStyle(
            "AppBody",
            fontName=BODY_FONT,
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=TEXT_SECONDARY,
        )

        story.append(Paragraph("Appendix", header_style))

        # Methodology
        story.append(Paragraph("Methodology", section_style))
        methodology = (
            "Scores are calculated as the normalized weighted result of each enabled analyzer. "
            "Each analyzer returns a score from 0 to 100, a status label, issues, and recommendations. "
            "The overall score is the arithmetic mean of all analyzer scores. "
            "Status thresholds: passed >= 75, warning >= 50, failed < 50."
        )
        story.append(Paragraph(methodology, body_style))
        story.append(Spacer(1, 10))

        # Analyzers used
        analyzers: List[Dict[str, Any]] = data.get("analyzers", [])
        story.append(Paragraph("Analyzers Executed", section_style))
        if analyzers:
            table_data = [
                [
                    Paragraph("<b>Analyzer</b>", body_style),
                    Paragraph("<b>Score</b>", body_style),
                    Paragraph("<b>Status</b>", body_style),
                    Paragraph("<b>Duration</b>", body_style),
                ]
            ]
            for item in analyzers:
                if not isinstance(item, dict):
                    continue
                name = item.get("name", "Unknown")
                score = float(item.get("score", 0) or 0)
                status = item.get("status", "needs_review")
                exec_time = item.get("execution_time_ms")
                time_str = f"{exec_time:.1f} ms" if exec_time is not None else "N/A"
                label, _ = _status_badge(status)
                table_data.append([
                    Paragraph(str(name), body_style),
                    Paragraph(f"{score:.1f}/100", body_style),
                    Paragraph(label, body_style),
                    Paragraph(time_str, body_style),
                ])

            col_widths = [page_width * 0.38, page_width * 0.20, page_width * 0.22, page_width * 0.20]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BG_SECONDARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), CYAN),
                ("FONTNAME", (0, 0), (-1, 0), LOGO_FONT),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), BG_TERTIARY),
                ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_PRIMARY),
                ("FONTNAME", (0, 1), (-1, -1), BODY_FONT),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_TERTIARY, BG_SECONDARY]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No analyzers were executed.", body_style))

        story.append(Spacer(1, 12))

        # Technical details
        story.append(Paragraph("Technical Details", section_style))
        meta = data.get("metadata", {}) or {}
        schema_version = data.get("schema_version", "1.0")
        tech_rows = [
            ["Schema Version", str(schema_version)],
            ["Evaluation ID", str(meta.get("evaluation_id", "N/A"))],
            ["Mode", str(meta.get("evaluation_mode", meta.get("mode", "N/A")))],
            ["Target", str(meta.get("target", meta.get("url", "N/A")))],
            ["Framework", str(meta.get("framework", meta.get("frameworks", "N/A")))],
        ]
        tech_data = [
            [Paragraph("<b>Key</b>", body_style), Paragraph("<b>Value</b>", body_style)]
        ]
        for key, value in tech_rows:
            tech_data.append([
                Paragraph(str(key), body_style),
                Paragraph(str(value), body_style),
            ])
        tech_table = Table(tech_data, colWidths=[page_width * 0.35, page_width * 0.65])
        tech_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_SECONDARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), CYAN),
            ("FONTNAME", (0, 0), (-1, 0), LOGO_FONT),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), BG_TERTIARY),
            ("TEXTCOLOR", (0, 1), (-1, -1), TEXT_PRIMARY),
            ("FONTNAME", (0, 1), (-1, -1), BODY_FONT),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_TERTIARY, BG_SECONDARY]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(tech_table)
