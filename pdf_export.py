# pdf_export.py
#
# Turns an already-generated report (from research_agent.generate_report)
# into a professional-looking PDF. Reuses the same parsed report data the
# on-screen cards use (research_agent.parse_report_markdown) instead of
# re-deriving or re-generating anything from the research pipeline.

from fpdf import FPDF

import research_agent

BRAND_COLOR = (91, 76, 220)
HEADING_COLOR = (50, 50, 120)
MUTED_COLOR = (110, 110, 110)
TEXT_COLOR = (25, 25, 25)
LINK_COLOR = (70, 90, 200)
NOTICE_COLOR = (140, 100, 15)


def _latin1_safe(text):
    """
    fpdf2's built-in core fonts only support latin-1. Real web content
    (smart quotes, em-dashes, checkmarks, etc.) can contain characters
    outside that range, so degrade those gracefully instead of crashing
    the PDF export.
    """
    return text.encode("latin-1", "replace").decode("latin-1")


def _soft_wrap_long_tokens(text, max_token_len=45):
    """
    Insert a zero-width break opportunity into any unbroken run of
    characters longer than max_token_len (e.g. a long URL) so fpdf2's
    default word-wrap can still lay it out.

    fpdf2 2.8.8's wrapmode="CHAR" can loop indefinitely on a single very
    long unbreakable token in a multi_cell -- this sidesteps that bug
    entirely by never asking for CHAR wrapping in the first place.
    """
    words = text.split(" ")
    wrapped_words = []
    for word in words:
        if len(word) <= max_token_len:
            wrapped_words.append(word)
            continue
        chunks = [word[i:i + max_token_len] for i in range(0, len(word), max_token_len)]
        wrapped_words.append("\n".join(chunks))
    return " ".join(wrapped_words)


def _pdf_text(text):
    """Sanitize + soft-wrap any string before handing it to multi_cell/cell."""
    return _soft_wrap_long_tokens(_latin1_safe(text))


def _multicell(pdf, h, text):
    """
    multi_cell() defaults to new_x=XPos.RIGHT, which leaves the cursor at
    the right margin after a full-width (w=0) cell. A second multi_cell
    called right after -- with no cell()/ln() in between to reset it --
    then computes its own width as (page width - right margin - cursor x),
    which collapses to ~0 and raises "not enough horizontal space to
    render a single character". Always resetting to the left margin here
    keeps every call safe regardless of what ran immediately before it.
    """
    pdf.multi_cell(0, h, _pdf_text(text), new_x="LMARGIN", new_y="NEXT")


class ReportPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED_COLOR)
        self.cell(0, 10, f"ResearchOS - Page {self.page_no()}", align="C")


def generate_pdf(topic, date_str, depth, report_text, sources, sources_are_real):
    """Build the PDF and return it as raw bytes, ready for a download button."""
    _, sections = research_agent.parse_report_markdown(report_text)

    pdf = ReportPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(18, 16, 18)
    pdf.add_page()

    # ---- Branding header ----
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*BRAND_COLOR)
    pdf.cell(0, 12, "ResearchOS", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MUTED_COLOR)
    pdf.cell(0, 6, "AI Research Agent - Research Report", ln=1)
    pdf.ln(3)
    pdf.set_draw_color(*BRAND_COLOR)
    pdf.set_line_width(0.6)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)

    # ---- Research question + meta ----
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*TEXT_COLOR)
    _multicell(pdf, 7, f"Research Question: {topic}")
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*MUTED_COLOR)
    source_label = "live web sources" if sources_are_real else "demo sources"
    _multicell(
        pdf,
        5.5,
        f"Date: {date_str}    |    Depth: {depth}    |    Sources: {len(sources)} ({source_label})",
    )
    pdf.ln(4)

    # ---- Report sections (Executive Summary, Key Findings, Analysis, etc.) ----
    for heading, body in sections:
        if heading == "Sources":
            continue
        pdf.set_font("Helvetica", "B", 12.5)
        pdf.set_text_color(*HEADING_COLOR)
        _multicell(pdf, 7, heading)
        pdf.ln(0.5)

        pdf.set_font("Helvetica", "", 10.5)
        pdf.set_text_color(*TEXT_COLOR)
        clean_body = research_agent.markdown_to_plain_text(body) if body else "Not available."
        _multicell(pdf, 5.8, clean_body)
        pdf.ln(3)

    # ---- Sources with URLs ----
    pdf.set_font("Helvetica", "B", 12.5)
    pdf.set_text_color(*HEADING_COLOR)
    _multicell(pdf, 7, f"Sources ({len(sources)})")
    pdf.ln(0.5)

    for index, source in enumerate(sources, start=1):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*TEXT_COLOR)
        _multicell(pdf, 5.5, f"{index}. {source['name']} ({source['topic']})")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*LINK_COLOR)
        _multicell(pdf, 5, source["url"])
        pdf.set_text_color(*MUTED_COLOR)
        pdf.set_font("Helvetica", "", 9)
        _multicell(pdf, 5, research_agent.markdown_to_plain_text(source["summary"]))
        pdf.ln(2)

    # ---- AI verification / warning notice (professional boxed callout) ----
    pdf.ln(3)
    notice_text = (
        f"**{_pdf_text(research_agent.VERIFICATION_NOTICE_TITLE)}**\n"
        f"{_pdf_text(research_agent.VERIFICATION_NOTICE)}"
    )
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*NOTICE_COLOR)
    pdf.set_draw_color(225, 180, 90)
    pdf.set_fill_color(255, 248, 232)
    pdf.set_line_width(0.3)
    pdf.multi_cell(
        0, 5.5, notice_text,
        border=1, fill=True, markdown=True,
        new_x="LMARGIN", new_y="NEXT",
        padding=3,
    )

    return bytes(pdf.output())
