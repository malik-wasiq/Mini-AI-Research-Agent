# pdf_export.py
#
# This is the ONLY file in the project that builds a PDF. It has one
# job: turn an already-generated report (markdown text + its sources)
# into a clean, professional PDF -- no research, no network calls, no
# re-analysis. It just reformats data that already exists.

import re
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from research_agent import parse_report_markdown

BRAND_BLUE = colors.HexColor("#5b7cfa")
BRAND_VIOLET = colors.HexColor("#7c6cf0")
TEXT_DARK = colors.HexColor("#1c1e2b")
TEXT_MUTED = colors.HexColor("#6b6e8a")
NOTICE_BG = colors.HexColor("#f2f4fb")


def _safe_text(text):
    """Drop characters (e.g. emoji) that ReportLab's base fonts can't render."""
    return text.encode("latin-1", "ignore").decode("latin-1")


def _inline_markup(text):
    """Escape a plain/markdown-ish string and turn **bold** into <b> tags."""
    escaped = escape(_safe_text(text))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="BrandTitle", fontName="Helvetica-Bold", fontSize=22,
        textColor=BRAND_VIOLET, leading=26, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="BrandSubtitle", fontName="Helvetica", fontSize=9,
        textColor=TEXT_MUTED, leading=12, spaceAfter=14,
    ))
    styles.add(ParagraphStyle(
        name="ReportTitle", fontName="Helvetica-Bold", fontSize=16,
        textColor=TEXT_DARK, leading=20, spaceBefore=6, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="Meta", fontName="Helvetica", fontSize=9.5,
        textColor=TEXT_MUTED, spaceAfter=4, leading=13,
    ))
    styles.add(ParagraphStyle(
        name="Notice", fontName="Helvetica", fontSize=9.5,
        textColor=TEXT_DARK, leading=13,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", fontName="Helvetica-Bold", fontSize=12.5,
        textColor=BRAND_BLUE, leading=16, spaceBefore=14, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="Body", fontName="Helvetica", fontSize=10, textColor=TEXT_DARK,
        leading=14.5, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="ReportBullet", parent=styles["Body"], leftIndent=12, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="SourceName", fontName="Helvetica-Bold", fontSize=10.5,
        textColor=TEXT_DARK, leading=13, spaceBefore=8, spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="SourceMeta", fontName="Helvetica", fontSize=8.5,
        textColor=TEXT_MUTED, leading=11, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="SourceLink", fontName="Helvetica", fontSize=9,
        textColor=BRAND_BLUE, leading=12, spaceAfter=2,
    ))
    return styles


def _section_body_flowables(body_text, styles):
    """Turn a section's markdown body (paragraphs + "- " bullets) into flowables."""
    flowables = []
    for raw_line in body_text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ")):
            text = "&bull;&nbsp;&nbsp;" + _inline_markup(line[2:].strip())
            flowables.append(Paragraph(text, styles["ReportBullet"]))
        else:
            flowables.append(Paragraph(_inline_markup(line), styles["Body"]))
    return flowables


def generate_pdf(report_text, topic, sources, sources_are_real):
    """
    Build a PDF (as bytes) from an already-generated report. Reuses the
    exact same markdown report text, sources, and AI-verification
    notice that are shown in the app -- nothing is re-researched or
    re-generated here.
    """
    styles = _build_styles()
    intro, sections = parse_report_markdown(report_text)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title=f"ResearchOS Report - {topic}",
    )

    story = [
        Paragraph("&#10022; ResearchOS", styles["BrandTitle"]),
        Paragraph("AI Research Agent", styles["BrandSubtitle"]),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e4f0"), spaceAfter=12),
        Paragraph("Research Report", styles["ReportTitle"]),
        Paragraph(f"<b>Research Question:</b> {_inline_markup(topic)}", styles["Meta"]),
    ]

    # The intro block already contains the AI-verification notice line
    # and the "Generated on ... | Research depth: ..." line -- reuse it
    # verbatim instead of re-deriving the date/status logic here.
    for line in intro.split("\n"):
        line = line.strip()
        if line:
            story.append(Paragraph(_inline_markup(line), styles["Meta"]))
    story.append(Spacer(1, 10))

    for heading, body in sections:
        if heading == "Sources" or not body:
            continue
        story.append(Paragraph(_inline_markup(heading), styles["SectionHeading"]))
        story.extend(_section_body_flowables(body, styles))

    story.append(Paragraph(f"Sources ({len(sources)})", styles["SectionHeading"]))
    if not sources:
        story.append(Paragraph(
            "Insufficient live sources -- a live web search for this topic did "
            "not return any usable results. No demo/placeholder sources are "
            "shown in their place.",
            styles["Body"],
        ))
    for source in sources:
        story.append(Paragraph(_inline_markup(source["name"]), styles["SourceName"]))
        story.append(Paragraph(_inline_markup(source["topic"]), styles["SourceMeta"]))
        story.append(Paragraph(_inline_markup(source["summary"]), styles["Body"]))
        url = escape(source["url"])
        story.append(Paragraph(f'<link href="{url}" color="#5b7cfa">{url}</link>', styles["SourceLink"]))

    doc.build(story)
    return buffer.getvalue()
