# app.py
#
# This is the Streamlit web application file.
# It is responsible ONLY for the user interface (UI): showing text,
# buttons, and inputs, and reacting to clicks.
#
# All the actual "research logic" lives in research_agent.py, and all
# the demo data lives in mock_data.py. This keeps app.py simple and
# easy to read, even though the workflow it displays has many steps.

import datetime
import html

import streamlit as st
import streamlit.components.v1 as components

import openrouter_client
import pdf_export
import research_agent
import storage


# ---------------------------------------------------------------------
# Basic page setup + visual identity ("ResearchOS")
# ---------------------------------------------------------------------
st.set_page_config(page_title="ResearchOS", page_icon="✦", layout="wide")


# ---------------------------------------------------------------------
# Global styling: dark futuristic theme, animated ambient background,
# glassmorphism cards, sidebar dashboard chrome. Presentation only --
# nothing here touches the research pipeline.
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root{
        --bg:#05060d;
        --bg-soft:#0a0c18;
        --panel:rgba(255,255,255,0.035);
        --panel-strong:rgba(255,255,255,0.055);
        --border:rgba(255,255,255,0.09);
        --border-soft:rgba(255,255,255,0.06);
        --text:#eceefb;
        --muted:#8d90ad;
        --muted-soft:#6b6e8a;
        --blue:#5b7cfa;
        --indigo:#7c6cf0;
        --violet:#a35bf0;
        --ok:#3ddc97;
        --warn:#f0b45b;
        --radius:16px;
    }

    @media (prefers-reduced-motion: reduce){
        *{ animation-duration:0.001ms !important; animation-iteration-count:1 !important;
           transition-duration:0.001ms !important; }
    }

    #MainMenu, footer, header[data-testid="stHeader"]{ visibility:hidden; height:0; }

    .stApp{
        background:var(--bg);
        color:var(--text);
        position:relative;
        overflow-x:hidden;
    }

    /* ---- Ambient animated background (pure CSS, no images) ---- */
    /* position:absolute (not fixed) so these stay anchored inside
       .stApp's own stacking context -- fixed elements can get trapped
       behind backdrop-filter/transform ancestors (the card wrappers
       below use backdrop-filter), which was hiding real content. */
    .stApp::before, .stApp::after{
        content:"";
        position:absolute;
        z-index:0;
        border-radius:50%;
        filter:blur(90px);
        opacity:0.55;
        pointer-events:none;
    }
    .stApp::before{
        width:46vw; height:46vw;
        top:-14vw; left:-10vw;
        background:radial-gradient(circle at 30% 30%, rgba(91,124,250,0.55), rgba(91,124,250,0) 70%);
        animation:ros-drift-a 26s ease-in-out infinite;
    }
    .stApp::after{
        width:40vw; height:40vw;
        bottom:-16vw; right:-8vw;
        background:radial-gradient(circle at 60% 60%, rgba(163,91,240,0.5), rgba(163,91,240,0) 70%);
        animation:ros-drift-b 32s ease-in-out infinite;
    }
    @keyframes ros-drift-a{
        0%,100%{ transform:translate(0,0) scale(1); }
        50%{ transform:translate(4vw,3vw) scale(1.08); }
    }
    @keyframes ros-drift-b{
        0%,100%{ transform:translate(0,0) scale(1); }
        50%{ transform:translate(-3vw,-4vw) scale(1.1); }
    }

    .ros-grid-layer{
        position:absolute; inset:0; z-index:0; pointer-events:none;
        background-image:
            linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
        background-size:42px 42px;
        mask-image:radial-gradient(ellipse 80% 60% at 50% 20%, #000 40%, transparent 85%);
        opacity:0.5;
    }

    /* attribute selector only (no tag qualifier) so this still matches
       if the underlying element tag differs across Streamlit versions */
    [data-testid="stMain"], [data-testid="stAppViewContainer"]{ position:relative; z-index:1; }
    .block-container{ padding-top:1.6rem; padding-bottom:3rem; max-width:1180px; }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"]{
        background:linear-gradient(180deg, #090a15 0%, #06070f 100%);
        border-right:1px solid var(--border-soft);
    }
    [data-testid="stSidebar"] > div{ padding-top:1.4rem; }

    .ros-logo{ display:flex; align-items:center; gap:0.6rem; padding:0 0.2rem 0.2rem 0.2rem; }
    .ros-logo-mark{
        width:34px; height:34px; border-radius:10px; flex-shrink:0;
        background:linear-gradient(135deg, var(--blue), var(--violet));
        display:flex; align-items:center; justify-content:center;
        font-size:1.05rem; color:#fff; box-shadow:0 0 18px rgba(124,108,240,0.55);
    }
    .ros-logo-text{ font-size:1.08rem; font-weight:700; letter-spacing:-0.01em; color:var(--text); }
    .ros-logo-sub{ font-size:0.72rem; color:var(--muted); letter-spacing:0.02em; margin-top:-2px; }

    .ros-nav-label{ font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase;
        color:var(--muted-soft); margin:1.5rem 0 0.5rem 0.2rem; }

    [data-testid="stSidebar"] .stButton button{
        width:100%; text-align:left; justify-content:flex-start;
        background:transparent; border:1px solid transparent; color:var(--text);
        font-weight:500; border-radius:10px; padding:0.5rem 0.7rem;
        box-shadow:none;
    }
    [data-testid="stSidebar"] .stButton button:hover{
        background:var(--panel-strong); border-color:var(--border);
        color:#fff;
    }
    .st-key-nav-new-research button{
        background:linear-gradient(90deg, rgba(91,124,250,0.18), rgba(163,91,240,0.18)) !important;
        border:1px solid rgba(124,108,240,0.4) !important;
        color:#fff !important;
        font-weight:600 !important;
    }

    .ros-nav-item{
        display:flex; align-items:center; justify-content:space-between;
        gap:0.5rem; padding:0.5rem 0.7rem; border-radius:10px;
        color:var(--muted-soft); font-size:0.88rem; font-weight:500;
        margin-bottom:0.15rem;
    }
    .ros-nav-item .ros-nav-icon{ opacity:0.7; margin-right:0.55rem; }
    .ros-nav-soon{
        font-size:0.6rem; letter-spacing:0.05em; text-transform:uppercase;
        color:var(--muted-soft); border:1px solid var(--border);
        border-radius:999px; padding:0.1rem 0.45rem;
    }

    .ros-sidebar-panel{
        border-top:1px solid var(--border-soft); margin-top:1.6rem; padding-top:1.1rem;
    }
    .ros-stat-row{ display:flex; align-items:center; justify-content:space-between;
        font-size:0.78rem; color:var(--muted); margin-bottom:0.55rem; }
    .ros-stat-label{ text-transform:uppercase; letter-spacing:0.06em; font-size:0.66rem; color:var(--muted-soft); }
    .ros-dot{ width:7px; height:7px; border-radius:50%; background:var(--ok); display:inline-block;
        margin-right:0.4rem; box-shadow:0 0 8px rgba(61,220,151,0.8); animation:ros-pulse 2.4s ease-in-out infinite; }
    .ros-dot.off{ background:#5c5f78; box-shadow:none; animation:none; }
    @keyframes ros-pulse{ 0%,100%{ opacity:1; } 50%{ opacity:0.45; } }

    .ros-usage-track{ width:100%; height:5px; border-radius:999px; background:rgba(255,255,255,0.07);
        overflow:hidden; margin:0.3rem 0 0.7rem 0; }
    .ros-usage-fill{ height:100%; border-radius:999px;
        background:linear-gradient(90deg, var(--blue), var(--violet)); }
    .ros-plan-tag{ display:inline-block; font-size:0.68rem; font-weight:600; letter-spacing:0.03em;
        color:#bcd0ff; background:rgba(91,124,250,0.14); border:1px solid rgba(91,124,250,0.35);
        border-radius:999px; padding:0.15rem 0.6rem; }

    /* ---- Top bar / status pill ---- */
    .ros-topbar{ display:flex; justify-content:flex-end; margin-bottom:0.6rem; }
    .ros-status-pill{
        display:inline-flex; align-items:center; gap:0.45rem;
        font-size:0.78rem; color:var(--text); background:var(--panel);
        border:1px solid var(--border); border-radius:999px; padding:0.35rem 0.85rem;
        backdrop-filter:blur(6px);
    }

    /* ---- Hero ---- */
    .ros-hero{ margin:0.6rem 0 1.8rem 0; }
    .ros-hero h1{ font-size:2.6rem; font-weight:750; letter-spacing:-0.03em; margin:0 0 0.5rem 0; color:var(--text); }
    .ros-hero .accent{
        background:linear-gradient(90deg, var(--blue), var(--violet));
        -webkit-background-clip:text; background-clip:text; color:transparent;
    }
    .ros-hero p{ color:var(--muted); font-size:1.05rem; margin:0; }

    /* ---- Generic glass card ---- */
    [data-testid="stVerticalBlockBorderWrapper"]{
        background:var(--panel) !important;
        border:1px solid var(--border) !important;
        border-radius:var(--radius) !important;
        backdrop-filter:blur(10px);
        transition:border-color 0.35s ease, box-shadow 0.35s ease, transform 0.35s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover{
        border-color:rgba(124,108,240,0.4) !important;
        box-shadow:0 0 28px rgba(91,124,250,0.12);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"]{
        padding:0;
    }

    .ros-card-title{ font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase;
        color:var(--muted-soft); margin-bottom:0.8rem; font-weight:600; }

    /* ---- Inputs ---- */
    div[data-testid="stTextInput"] input{
        border:1px solid var(--border); border-radius:12px; background:rgba(255,255,255,0.03);
        color:var(--text); font-size:1.05rem; padding:0.75rem 1rem;
    }
    div[data-testid="stTextInput"] input:focus{
        border-color:rgba(124,108,240,0.6); box-shadow:0 0 0 3px rgba(124,108,240,0.15);
    }
    div[data-testid="stTextInput"] input::placeholder{ color:var(--muted-soft); }

    /* Research question textarea -- Enter submits, Shift+Enter adds a line */
    .st-key-topic-input textarea{
        border:1px solid var(--border); border-radius:12px; background:rgba(255,255,255,0.03);
        color:var(--text); font-size:1.05rem; padding:0.75rem 1rem; resize:none;
    }
    .st-key-topic-input textarea:focus{
        border-color:rgba(124,108,240,0.6); box-shadow:0 0 0 3px rgba(124,108,240,0.15);
    }
    .st-key-topic-input textarea::placeholder{ color:var(--muted-soft); }
    .st-key-topic-input [data-testid="stWidgetInstructions"]{ display:none; }

    /* Depth pills (st.pills) */
    div[data-testid="stPills"] button{
        border-radius:999px !important; border:1px solid var(--border) !important;
        background:rgba(255,255,255,0.03) !important; color:var(--muted) !important;
    }
    div[data-testid="stPills"] button[aria-checked="true"]{
        background:linear-gradient(90deg, rgba(91,124,250,0.35), rgba(163,91,240,0.35)) !important;
        border-color:rgba(124,108,240,0.6) !important; color:#fff !important;
    }

    /* ---- Buttons ---- */
    .stButton button, .stDownloadButton button{
        border-radius:12px; border:1px solid var(--border);
        background:var(--panel-strong); color:var(--text); font-weight:600;
        transition:all 0.25s ease;
    }
    .st-key-start-research button{
        background:linear-gradient(90deg, var(--blue), var(--violet)) !important;
        border:none !important; color:#fff !important; font-size:1.02rem !important;
        box-shadow:0 6px 24px rgba(124,108,240,0.35);
    }
    .st-key-start-research button:hover{
        box-shadow:0 8px 32px rgba(124,108,240,0.55); transform:translateY(-1px);
    }
    .stDownloadButton button:hover, .stButton button:hover{
        border-color:rgba(124,108,240,0.5); color:#fff;
    }

    /* ---- Empty state ---- */
    .ros-empty{ text-align:center; padding:2rem 1rem; color:var(--muted); }
    .ros-empty h3{ color:var(--text); font-weight:600; margin-bottom:0.4rem; font-size:1.05rem; }
    .ros-empty p{ font-size:0.9rem; margin:0; }

    /* ---- Workflow ---- */
    .ros-workflow{ display:flex; align-items:flex-start; gap:0; flex-wrap:wrap; }
    .ros-wf-stage{ display:flex; flex-direction:column; align-items:center; text-align:center;
        min-width:100px; flex:1 1 100px; animation:ros-fade-in 0.5s ease both; }
    .ros-wf-connector{ flex:0.6 1 32px; height:2px; margin-top:19px; align-self:flex-start;
        background:var(--border); position:relative; top:0; }
    .ros-wf-connector.done{ background:linear-gradient(90deg, var(--blue), var(--violet)); }
    .ros-wf-circle{
        width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center;
        font-size:0.85rem; font-weight:700; margin-bottom:0.55rem;
        border:1.5px solid var(--border); color:var(--muted-soft); background:rgba(255,255,255,0.02);
    }
    .ros-wf-stage.active .ros-wf-circle{
        border-color:transparent; color:#fff;
        background:linear-gradient(135deg, var(--blue), var(--violet));
        box-shadow:0 0 0 5px rgba(124,108,240,0.16), 0 0 18px rgba(124,108,240,0.5);
        animation:ros-pulse-ring 1.8s ease-in-out infinite;
    }
    .ros-wf-stage.done .ros-wf-circle{
        border-color:rgba(61,220,151,0.5); color:var(--ok); background:rgba(61,220,151,0.08);
    }
    @keyframes ros-pulse-ring{
        0%,100%{ box-shadow:0 0 0 5px rgba(124,108,240,0.16), 0 0 18px rgba(124,108,240,0.5); }
        50%{ box-shadow:0 0 0 8px rgba(124,108,240,0.08), 0 0 26px rgba(124,108,240,0.65); }
    }
    @keyframes ros-fade-in{ from{ opacity:0; transform:translateY(6px); } to{ opacity:1; transform:translateY(0); } }
    .ros-wf-label{ font-size:0.78rem; font-weight:700; letter-spacing:0.03em; color:var(--text); }
    .ros-wf-stage:not(.active):not(.done) .ros-wf-label{ color:var(--muted-soft); }
    .ros-wf-desc{ font-size:0.7rem; color:var(--muted-soft); margin-top:0.15rem; }

    /* ---- Blueprint feature cards ---- */
    .ros-feature{
        border:1px solid var(--border-soft); border-radius:14px; padding:1rem 1.05rem;
        background:rgba(255,255,255,0.02); height:100%; transition:border-color 0.3s ease, transform 0.3s ease;
    }
    .ros-feature:hover{ border-color:rgba(124,108,240,0.4); transform:translateY(-2px); }
    .ros-feature-icon{ font-size:1.15rem; margin-bottom:0.5rem; }
    .ros-feature-title{ font-size:0.88rem; font-weight:650; color:var(--text); margin-bottom:0.25rem; }
    .ros-feature-desc{ font-size:0.78rem; color:var(--muted); line-height:1.45; }

    /* ---- Report sections ---- */
    .ros-report-meta{ font-size:0.85rem; color:var(--muted); line-height:1.6; margin-bottom:0.5rem; }
    .ros-report-meta blockquote{ border-left:2px solid var(--blue); background:rgba(91,124,250,0.08);
        padding:0.6rem 0.9rem; margin:0.3rem 0 0.6rem 0; border-radius:0 8px 8px 0; }
    .ros-section-heading{ font-size:0.72rem; letter-spacing:0.09em; text-transform:uppercase;
        color:#bcd0ff; font-weight:700; margin-bottom:0.7rem; }
    [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stVerticalBlockBorderWrapper"] li{ color:#d6d8ee; line-height:1.7; font-size:0.92rem; }

    /* ---- AI verification / warning notice ---- */
    .ros-ai-notice{
        display:flex; gap:0.65rem; align-items:flex-start;
        border:1px solid rgba(240,180,91,0.3); border-left:3px solid var(--warn);
        background:rgba(240,180,91,0.07); border-radius:10px;
        padding:0.75rem 1rem; margin-top:0.9rem;
    }
    .ros-ai-notice .ros-ai-notice-icon{ font-size:1rem; line-height:1.4; flex-shrink:0; }
    .ros-ai-notice-title{ font-size:0.82rem; font-weight:700; color:var(--warn); margin-bottom:0.2rem; }
    .ros-ai-notice-body{ font-size:0.78rem; color:var(--muted); line-height:1.55; }

    /* ---- Source cards ---- */
    .ros-source-card{
        border:1px solid var(--border-soft); border-radius:12px; padding:0.85rem 1rem;
        background:rgba(255,255,255,0.02); margin-bottom:0.65rem;
    }
    .ros-source-top{ display:flex; align-items:center; justify-content:space-between; gap:0.5rem; margin-bottom:0.3rem; }
    .ros-source-title{ font-weight:650; font-size:0.9rem; color:var(--text); }
    .ros-badge{ font-size:0.6rem; letter-spacing:0.04em; text-transform:uppercase; font-weight:700;
        border-radius:999px; padding:0.12rem 0.5rem; flex-shrink:0; white-space:nowrap; }
    .ros-badge.live{ color:#3ddc97; background:rgba(61,220,151,0.12); border:1px solid rgba(61,220,151,0.35); }
    .ros-badge.demo{ color:#f0b45b; background:rgba(240,180,91,0.12); border:1px solid rgba(240,180,91,0.35); }
    .ros-source-domain{ font-size:0.68rem; color:var(--muted-soft); text-transform:uppercase;
        letter-spacing:0.04em; margin-bottom:0.35rem; }
    .ros-source-summary{ font-size:0.82rem; color:var(--muted); line-height:1.55; margin-bottom:0.4rem; }
    .ros-source-card a{ font-size:0.78rem; color:#8fa8ff; text-decoration:none; word-break:break-all; }
    .ros-source-card a:hover{ text-decoration:underline; }

    .ros-section-label{ font-size:0.72rem; letter-spacing:0.08em; text-transform:uppercase;
        color:var(--muted); margin:1.6rem 0 0.6rem 0; font-weight:600; }

    /* ---- Responsive ---- */
    @media (max-width: 768px){
        .ros-hero h1{ font-size:1.9rem; }
        .ros-workflow{ overflow-x:auto; flex-wrap:nowrap; padding-bottom:0.4rem; }
        .ros-wf-stage{ min-width:84px; }
        .block-container{ padding-left:0.9rem; padding-right:0.9rem; }
    }
    </style>
    <div class="ros-grid-layer"></div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Session state defaults (all additive -- these never replace or alter
# the research pipeline's own data, only presentation bookkeeping).
# ---------------------------------------------------------------------
st.session_state.setdefault("usage_count", 0)
st.session_state.setdefault("view", "research")


# ---------------------------------------------------------------------
# Workflow stages shown in the Agent Workflow card. Purely presentational
# labels layered on top of the existing research pipeline stages.
# ---------------------------------------------------------------------
WORKFLOW_STAGES = [
    {"label": "Search", "desc": "Finding information"},
    {"label": "Sources", "desc": "Collecting data"},
    {"label": "Analysis", "desc": "AI analyzing"},
    {"label": "Synthesis", "desc": "Creating insights"},
    {"label": "Report", "desc": "Generating report"},
]


def render_workflow(placeholder, active_index):
    """
    Render the horizontal agent-workflow card.
    active_index == -1        -> nothing started yet, all stages pending
    0 <= active_index < len   -> that stage is currently running
    active_index >= len       -> every stage is complete
    """
    parts = ['<div class="ros-workflow">']
    total = len(WORKFLOW_STAGES)
    for index, stage in enumerate(WORKFLOW_STAGES):
        if active_index >= total or index < active_index:
            state = "done"
        elif index == active_index:
            state = "active"
        else:
            state = ""
        icon = "✓" if state == "done" else str(index + 1)
        parts.append(
            f'<div class="ros-wf-stage {state}" style="animation-delay:{index * 0.05}s">'
            f'<div class="ros-wf-circle">{icon}</div>'
            f'<div class="ros-wf-label">{html.escape(stage["label"])}</div>'
            f'<div class="ros-wf-desc">{html.escape(stage["desc"])}</div>'
            "</div>"
        )
        if index < total - 1:
            connector_state = "done" if (active_index >= total or index < active_index) else ""
            parts.append(f'<div class="ros-wf-connector {connector_state}"></div>')
    parts.append("</div>")
    placeholder.markdown("".join(parts), unsafe_allow_html=True)


def render_source_cards_html(sources, sources_are_real):
    """Build escaped HTML for a set of premium source cards."""
    badge_class = "live" if sources_are_real else "demo"
    badge_label = "LIVE SOURCE" if sources_are_real else "DEMO SOURCE"
    parts = []
    for source in sources:
        name = html.escape(source["name"])
        domain = html.escape(source["topic"])
        summary = html.escape(source["summary"])
        url = html.escape(source["url"], quote=True)
        url_label = html.escape(source["url"])
        parts.append(
            '<div class="ros-source-card">'
            '<div class="ros-source-top">'
            f'<div class="ros-source-title">{name}</div>'
            f'<span class="ros-badge {badge_class}">{badge_label}</span>'
            "</div>"
            f'<div class="ros-source-domain">{domain}</div>'
            f'<div class="ros-source-summary">{summary}</div>'
            f'<a href="{url}" target="_blank" rel="noopener">{url_label}</a>'
            "</div>"
        )
    return "".join(parts)


def render_report_cards(report_text, sources, sources_are_real):
    """Render the persisted final report as a set of clean, titled cards."""
    intro, sections = research_agent.parse_report_markdown(report_text)

    if intro:
        st.markdown(f'<div class="ros-report-meta">{intro}</div>'.replace("\n", "<br>"), unsafe_allow_html=True)

    for heading, body in sections:
        if heading == "Sources":
            continue
        with st.container(border=True, key=f"report-section-{heading}"):
            st.markdown(f'<div class="ros-section-heading">{html.escape(heading)}</div>', unsafe_allow_html=True)
            st.markdown(body if body else "_Not available._")

    with st.container(border=True):
        st.markdown(
            f'<div class="ros-section-heading">Sources ({len(sources)})</div>',
            unsafe_allow_html=True,
        )
        st.markdown(render_source_cards_html(sources, sources_are_real), unsafe_allow_html=True)

    st.markdown(
        '<div class="ros-ai-notice">'
        '<div class="ros-ai-notice-icon">⚠</div>'
        "<div>"
        f'<div class="ros-ai-notice-title">{html.escape(research_agent.VERIFICATION_NOTICE_TITLE)}</div>'
        f'<div class="ros-ai-notice-body">{html.escape(research_agent.VERIFICATION_NOTICE)}</div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _format_timestamp(iso_timestamp):
    """Render a stored ISO timestamp as a friendly date/time string."""
    try:
        return datetime.datetime.fromisoformat(iso_timestamp).strftime("%B %d, %Y · %I:%M %p")
    except (TypeError, ValueError):
        return iso_timestamp or ""


def _open_entry_for_viewing(entry):
    """Load a History/Saved entry into session_state as the active report."""
    st.session_state["report_text"] = entry["report_text"]
    st.session_state["report_topic"] = entry["question"]
    st.session_state["report_sources"] = entry["sources"]
    st.session_state["report_sources_are_real"] = entry["sources_are_real"]
    st.session_state["report_depth"] = entry["depth"]
    st.session_state["report_timestamp"] = entry["timestamp"]
    st.session_state["view"] = "research"


def _render_entry_card(entry, on_primary, primary_label, on_delete, key_prefix):
    """Shared card layout for one History or Saved Reports entry."""
    with st.container(border=True):
        title = entry.get("title") or entry["question"]
        st.markdown(
            f'<div class="ros-report-meta"><b>{html.escape(title)}</b><br>'
            f'{html.escape(_format_timestamp(entry["timestamp"]))} &middot; '
            f'{html.escape(entry["depth"])} &middot; {entry["source_count"]} source(s)</div>',
            unsafe_allow_html=True,
        )
        if entry.get("summary"):
            st.markdown(
                f'<div class="ros-source-summary">{html.escape(entry["summary"])}</div>',
                unsafe_allow_html=True,
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(primary_label, key=f"{key_prefix}-view-{entry['id']}", width="stretch"):
                on_primary(entry)
                st.rerun()
        with col2:
            pdf_bytes = pdf_export.generate_pdf(
                entry["question"],
                _format_timestamp(entry["timestamp"]),
                entry["depth"],
                entry["report_text"],
                entry["sources"],
                entry["sources_are_real"],
            )
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name="research_report.pdf",
                mime="application/pdf",
                key=f"{key_prefix}-pdf-{entry['id']}",
                width="stretch",
            )
        with col3:
            if st.button("Delete", key=f"{key_prefix}-del-{entry['id']}", width="stretch"):
                on_delete(entry["id"])
                st.rerun()


def render_history_view():
    st.markdown('<div class="ros-section-label">Research History</div>', unsafe_allow_html=True)
    entries = storage.list_history()
    if not entries:
        st.markdown(
            '<div class="ros-empty"><h3>No research history yet.</h3>'
            "<p>Every completed research run is automatically saved here, "
            "so you can revisit it later.</p></div>",
            unsafe_allow_html=True,
        )
        return
    for entry in entries:
        _render_entry_card(
            entry,
            on_primary=_open_entry_for_viewing,
            primary_label="View Report",
            on_delete=storage.delete_history_entry,
            key_prefix="hist",
        )


def render_saved_view():
    st.markdown('<div class="ros-section-label">Saved Reports</div>', unsafe_allow_html=True)
    entries = storage.list_saved_reports()
    if not entries:
        st.markdown(
            '<div class="ros-empty"><h3>No saved reports yet.</h3>'
            "<p>Use \"Save Report\" on a completed research report to keep it here.</p></div>",
            unsafe_allow_html=True,
        )
        return
    for entry in entries:
        _render_entry_card(
            entry,
            on_primary=_open_entry_for_viewing,
            primary_label="Open / View",
            on_delete=storage.delete_saved_report,
            key_prefix="saved",
        )


def _collect_all_sources():
    """
    Aggregate every real/demo source actually seen across Research History
    and Saved Reports (the only place source data is persisted), deduped
    by URL. No source is invented here -- every entry already came from
    the real research pipeline (web_search.py) or its documented demo
    fallback, exactly as recorded at the time that run completed.
    """
    seen = {}
    for entry in storage.list_history() + storage.list_saved_reports():
        for source in entry.get("sources", []):
            url = source.get("url")
            if not url or url in seen:
                continue
            seen[url] = {
                "name": source.get("name", ""),
                "domain": source.get("topic", ""),
                "summary": source.get("summary", ""),
                "url": url,
                "research_topic": entry.get("question", ""),
                "timestamp": entry.get("timestamp", ""),
                "is_real": entry.get("sources_are_real", False),
            }
    return sorted(seen.values(), key=lambda s: s["timestamp"], reverse=True)


def render_sources_library_view():
    st.markdown('<div class="ros-section-label">Sources Library</div>', unsafe_allow_html=True)
    all_sources = _collect_all_sources()

    if not all_sources:
        st.markdown(
            '<div class="ros-empty"><h3>No sources yet.</h3>'
            "<p>Sources collected during research runs (Research History and "
            "Saved Reports) will appear here automatically.</p></div>",
            unsafe_allow_html=True,
        )
        return

    query = st.text_input(
        "Search sources",
        placeholder="Filter by source name, domain, or research topic...",
        label_visibility="collapsed",
    ).strip().lower()

    if query:
        all_sources = [
            s for s in all_sources
            if query in s["name"].lower()
            or query in s["domain"].lower()
            or query in s["research_topic"].lower()
        ]

    if not all_sources:
        st.caption("No sources match that search.")
        return

    for source in all_sources:
        with st.container(border=True):
            badge_class = "live" if source["is_real"] else "demo"
            badge_label = "LIVE SOURCE" if source["is_real"] else "DEMO SOURCE"
            st.markdown(
                '<div class="ros-source-top">'
                f'<div class="ros-source-title">{html.escape(source["name"])}</div>'
                f'<span class="ros-badge {badge_class}">{badge_label}</span>'
                "</div>"
                f'<div class="ros-source-domain">{html.escape(source["domain"])}</div>'
                f'<div class="ros-source-summary">From research: '
                f'<i>{html.escape(source["research_topic"])}</i> &middot; '
                f'{html.escape(_format_timestamp(source["timestamp"]))}</div>',
                unsafe_allow_html=True,
            )
            link_col, _ = st.columns([1, 3])
            with link_col:
                st.link_button("Open Source ↗", source["url"], width="stretch")


def render_settings_view():
    st.markdown('<div class="ros-section-label">Settings</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="ros-card-title">Research Preferences</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ros-report-meta">Research depth controls how many sources '
            "are gathered per run. This is chosen per-research on the New Research "
            "screen; there is no separate saved default.</div>",
            unsafe_allow_html=True,
        )
        for depth_name, source_count in research_agent.SOURCE_COUNT_BY_DEPTH.items():
            st.markdown(
                f'<div class="ros-stat-row"><span>{html.escape(depth_name)}</span>'
                f'<span>{source_count} source(s)</span></div>',
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        st.markdown('<div class="ros-card-title">Connection Status</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ros-stat-row"><span>Live Web Search</span>'
            f'<span><span class="ros-dot"></span>Always available (no API key required)</span></div>'
            f'<div class="ros-stat-row"><span>OpenRouter AI Engine</span>'
            f'<span><span class="ros-dot{"" if _engine_online else " off"}"></span>'
            f'{"Connected" if _engine_online else "Not connected"}</span></div>',
            unsafe_allow_html=True,
        )
        if _engine_online:
            st.caption(f"Model: {_model_name}")
        else:
            st.caption("Add OPENROUTER_API_KEY to your .env file to enable AI analysis/synthesis.")

    with st.container(border=True):
        st.markdown('<div class="ros-card-title">About</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ros-report-meta">'
            "<b>ResearchOS</b> — Mini AI Research Agent<br>"
            "Combines real-time web search with AI-powered analysis and synthesis "
            "to generate structured research reports.<br><br>"
            f"<b>{html.escape(research_agent.VERIFICATION_NOTICE_TITLE)}:</b> "
            f"{html.escape(research_agent.VERIFICATION_NOTICE)}"
            "</div>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------
# Sidebar: branding, navigation, and real (derived, not fabricated)
# status information.
# ---------------------------------------------------------------------
_engine_online = openrouter_client.is_configured()
_model_name = openrouter_client.get_model_name()
_is_free_model = ":free" in _model_name

with st.sidebar:
    st.markdown(
        """
        <div class="ros-logo">
          <div class="ros-logo-mark">✦</div>
          <div>
            <div class="ros-logo-text">ResearchOS</div>
            <div class="ros-logo-sub">AI Research Agent</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ros-nav-label">Navigate</div>', unsafe_allow_html=True)

    if st.button("✦  New Research", key="nav-new-research", width="stretch"):
        for key in (
            "report_text", "report_topic", "report_sources",
            "report_sources_are_real", "report_depth", "report_timestamp",
        ):
            st.session_state.pop(key, None)
        st.session_state["view"] = "research"
        st.rerun()

    if st.button("⏱  Research History", key="nav-history", width="stretch"):
        st.session_state["view"] = "history"
        st.rerun()

    if st.button("▤  Saved Reports", key="nav-saved", width="stretch"):
        st.session_state["view"] = "saved"
        st.rerun()

    if st.button("◈  Sources Library", key="nav-sources", width="stretch"):
        st.session_state["view"] = "sources"
        st.rerun()

    if st.button("⚙  Settings", key="nav-settings", width="stretch"):
        st.session_state["view"] = "settings"
        st.rerun()

    usage_count = min(st.session_state["usage_count"], 50)
    usage_pct = round((usage_count / 50) * 100)
    plan_label = "Free Plan" if _is_free_model else "Custom Plan"

    st.markdown(
        f"""
        <div class="ros-sidebar-panel">
          <div class="ros-stat-row">
            <span class="ros-stat-label">AI Engine Status</span>
          </div>
          <div style="margin-bottom:1.1rem; font-size:0.85rem; color:var(--text);">
            <span class="ros-dot{'' if _engine_online else ' off'}"></span>
            {'Online' if _engine_online else 'Offline'}
          </div>

          <div class="ros-stat-row">
            <span class="ros-stat-label">Session Usage</span>
          </div>
          <div style="font-size:0.85rem; color:var(--text); margin-bottom:0.2rem;">
            {usage_count} / 50 requests
          </div>
          <div class="ros-usage-track">
            <div class="ros-usage-fill" style="width:{usage_pct}%;"></div>
          </div>
          <span class="ros-plan-tag">{plan_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Top bar: AI engine status pill (no API key ever displayed)
# ---------------------------------------------------------------------
st.markdown(
    f"""
    <div class="ros-topbar">
      <span class="ros-status-pill">
        <span class="ros-dot{'' if _engine_online else ' off'}"></span>
        {'AI Engine Online' if _engine_online else 'AI Engine Offline'}
      </span>
    </div>
    """,
    unsafe_allow_html=True,
)


if st.session_state["view"] == "history":
    render_history_view()
elif st.session_state["view"] == "saved":
    render_saved_view()
elif st.session_state["view"] == "sources":
    render_sources_library_view()
elif st.session_state["view"] == "settings":
    render_settings_view()
else:
    # -------------------------------------------------------------
    # Hero + research input (the visual focus of the page)
    # -------------------------------------------------------------
    st.markdown(
        """
        <div class="ros-hero">
          <h1>Research <span class="accent">anything.</span></h1>
          <p>Search the web. Analyze evidence. Synthesize insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="ros-card-title">Research Question</div>', unsafe_allow_html=True)
        topic_input = st.text_area(
            "Research Topic",
            placeholder="What would you like to research? (Enter to start, Shift+Enter for a new line)",
            label_visibility="collapsed",
            key="topic-input",
            height=68,
        )

        st.markdown('<div class="ros-card-title" style="margin-top:1rem;">Research Depth</div>', unsafe_allow_html=True)
        depth_choice = st.pills(
            "Research depth",
            options=["Quick", "Standard", "Detailed"],
            default="Standard",
            label_visibility="collapsed",
            help="Quick uses fewer sources, Detailed uses more sources.",
        )
        depth_choice = depth_choice or "Standard"

        st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
        start_button = st.button("✦  Start Research", key="start-research", type="primary", width="stretch")

        # Enter submits the research question (like clicking Start Research);
        # Shift+Enter still inserts a newline normally. Implemented via a tiny
        # injected script because Streamlit's own text_area has no built-in
        # "Enter submits" behavior -- it only supports Ctrl+Enter to apply.
        components.html(
            """
            <script>
            (function() {
                function attach() {
                    const doc = window.parent.document;
                    const textarea = doc.querySelector('.st-key-topic-input textarea');
                    const button = doc.querySelector('.st-key-start-research button');
                    if (!textarea || !button) { return false; }
                    if (textarea.dataset.enterSubmitAttached) { return true; }
                    textarea.dataset.enterSubmitAttached = "true";
                    textarea.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            textarea.blur();
                            setTimeout(function() { button.click(); }, 80);
                        }
                        // Shift+Enter: no special handling -- the browser's
                        // default textarea behavior inserts a newline.
                    });
                    return true;
                }
                if (!attach()) {
                    const interval = setInterval(function() {
                        if (attach()) { clearInterval(interval); }
                    }, 250);
                }
            })();
            </script>
            """,
            height=0,
        )

    # -------------------------------------------------------------
    # Agent workflow (always visible; reflects real pipeline progress only)
    # -------------------------------------------------------------
    st.markdown('<div class="ros-section-label">Agent Workflow</div>', unsafe_allow_html=True)
    with st.container(border=True):
        workflow_placeholder = st.empty()
        if "report_text" in st.session_state and not start_button:
            render_workflow(workflow_placeholder, active_index=len(WORKFLOW_STAGES))
        else:
            render_workflow(workflow_placeholder, active_index=-1)

    status_placeholder = st.empty()

    # -------------------------------------------------------------
    # Research Blueprint (static explainer -- visual only, no fake wiring)
    # -------------------------------------------------------------
    st.markdown('<div class="ros-section-label">Research Blueprint</div>', unsafe_allow_html=True)
    with st.container(border=True):
        bp_cols = st.columns(4)
        blueprint_items = [
            ("🔎", "Smart Search", "Search across real web sources"),
            ("📚", "Source Collection", "Gather relevant evidence"),
            ("🧠", "AI Analysis", "Analyze collected information"),
            ("📄", "Report Generation", "Create a structured research report"),
        ]
        for col, (icon, title, desc) in zip(bp_cols, blueprint_items):
            with col:
                st.markdown(
                    f"""
                    <div class="ros-feature">
                      <div class="ros-feature-icon">{icon}</div>
                      <div class="ros-feature-title">{title}</div>
                      <div class="ros-feature-desc">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # -------------------------------------------------------------
    # Helper function to run the whole agent workflow and display it
    # -------------------------------------------------------------
    def run_research_workflow(topic, depth):
        """
        Run every stage of the research agent, one after another, updating
        the workflow card as it goes. Stores the final report (and the
        sources used) in Streamlit's session_state so the results/download
        section can render them after the run finishes -- and again after
        any later rerun (e.g. clicking a download button). Also auto-saves
        the completed run to Research History.
        """

        # ---- Stage: Search (plan + live web search) ----
        render_workflow(workflow_placeholder, active_index=0)
        with st.spinner("Creating research plan and searching the web..."):
            plan_steps = research_agent.create_research_plan(topic, depth)
            sources, sources_are_real, source_error = research_agent.discover_sources(topic, depth)

        if sources_are_real:
            status_placeholder.caption(f"✓ Found {len(sources)} live source(s) via real-time web search.")
        elif source_error:
            status_placeholder.caption(f"⚠ Live search unavailable, using demo sources. ({source_error})")
        else:
            status_placeholder.caption("Using demo sources for this run.")

        # ---- Stage: Sources (collection) ----
        render_workflow(workflow_placeholder, active_index=1)
        with st.spinner("Collecting information from sources..."):
            collected_items = research_agent.collect_information(sources)

        # ---- Stage: Analysis ----
        render_workflow(workflow_placeholder, active_index=2)
        with st.spinner("Analyzing collected information..."):
            analysis = research_agent.analyze_information(topic, collected_items)

        if analysis.get("ai_powered") and not analysis.get("ai_error"):
            status_placeholder.caption("✓ Analysis generated by OpenRouter AI.")
        elif analysis.get("ai_powered") and analysis.get("ai_error"):
            status_placeholder.caption(f"⚠ Partially AI-generated analysis — {analysis['ai_error']}")
        elif analysis.get("ai_error"):
            status_placeholder.caption(f"⚠ Demo analysis — OpenRouter unavailable ({analysis['ai_error']})")
        else:
            status_placeholder.caption("Demo analysis — no API key configured.")

        # ---- Stage: Synthesis ----
        render_workflow(workflow_placeholder, active_index=3)
        with st.spinner("Synthesizing findings..."):
            synthesis = research_agent.synthesize_findings(topic, analysis, sources)

        if synthesis.get("ai_powered") and not synthesis.get("ai_error"):
            status_placeholder.caption("✓ Synthesis generated by OpenRouter AI.")
        elif synthesis.get("ai_powered") and synthesis.get("ai_error"):
            status_placeholder.caption(f"⚠ Partially AI-generated synthesis — {synthesis['ai_error']}")
        elif synthesis.get("ai_error"):
            status_placeholder.caption(f"⚠ Demo synthesis — OpenRouter unavailable ({synthesis['ai_error']})")
        else:
            status_placeholder.caption("Demo synthesis — no API key configured.")

        # ---- Stage: Report ----
        render_workflow(workflow_placeholder, active_index=4)
        with st.spinner("Generating final report..."):
            report_text = research_agent.generate_report(
                topic, depth, plan_steps, sources, analysis, synthesis, sources_are_real
            )

        render_workflow(workflow_placeholder, active_index=len(WORKFLOW_STAGES))
        status_placeholder.caption("✓ Research complete.")

        # Persist everything the results section needs, so it keeps
        # rendering correctly across later reruns (e.g. download clicks).
        st.session_state["report_text"] = report_text
        st.session_state["report_topic"] = topic
        st.session_state["report_sources"] = sources
        st.session_state["report_sources_are_real"] = sources_are_real
        st.session_state["report_depth"] = depth
        st.session_state["report_timestamp"] = datetime.datetime.now().isoformat(timespec="seconds")
        st.session_state["usage_count"] = st.session_state.get("usage_count", 0) + 1

        # Auto-save every successfully completed research run to History.
        storage.add_history_entry(topic, depth, sources, sources_are_real, report_text)

    # -------------------------------------------------------------
    # Main app logic: what happens when the button is clicked
    # -------------------------------------------------------------
    if start_button:
        # ---- Input validation, so the app never crashes on bad input ----
        if topic_input is None or topic_input.strip() == "":
            st.warning("Please enter a research topic before starting.")
        elif len(topic_input.strip()) < 3:
            st.warning("Please enter a more descriptive research topic (at least 3 characters).")
        else:
            try:
                run_research_workflow(topic_input.strip(), depth_choice)
            except Exception as error:
                # Catch-all so an unexpected issue never crashes the whole app.
                st.error(f"Something went wrong while running the research agent: {error}")

    # -------------------------------------------------------------
    # Results: the generated report, rendered as clean sectioned cards.
    # Shown whenever a report exists in session_state, so it stays the
    # visual focus even after later reruns (e.g. clicking a download button).
    # -------------------------------------------------------------
    if "report_text" in st.session_state:
        st.markdown('<div class="ros-section-label">Research Report</div>', unsafe_allow_html=True)
        render_report_cards(
            st.session_state["report_text"],
            st.session_state.get("report_sources", []),
            st.session_state.get("report_sources_are_real", False),
        )
    elif not start_button:
        st.markdown(
            '<div class="ros-empty"><h3>Your research starts here.</h3>'
            "<p>Ask a question above and let the agent search the web, "
            "analyze evidence, and build a structured report.</p></div>",
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------
    # Export buttons (only shown after a report has been generated)
    # -------------------------------------------------------------
    if "report_text" in st.session_state:
        st.markdown('<div class="ros-section-label">Export</div>', unsafe_allow_html=True)

        report_text = st.session_state["report_text"]
        report_topic = st.session_state["report_topic"]
        report_sources = st.session_state.get("report_sources", [])
        report_sources_are_real = st.session_state.get("report_sources_are_real", False)
        report_depth = st.session_state.get("report_depth", "Standard")
        report_timestamp = st.session_state.get(
            "report_timestamp", datetime.datetime.now().isoformat(timespec="seconds")
        )
        plain_text_report = research_agent.markdown_to_plain_text(report_text)

        with st.container(border=True):
            download_col1, download_col2 = st.columns(2)
            with download_col1:
                st.download_button(
                    label="⬇  Download Markdown",
                    data=report_text,
                    file_name="research_report.md",
                    mime="text/markdown",
                    width="stretch",
                )
            with download_col2:
                st.download_button(
                    label="⬇  Download Text",
                    data=plain_text_report,
                    file_name="research_report.txt",
                    mime="text/plain",
                    width="stretch",
                )

            pdf_col, save_col = st.columns(2)
            with pdf_col:
                pdf_bytes = pdf_export.generate_pdf(
                    report_topic,
                    _format_timestamp(report_timestamp),
                    report_depth,
                    report_text,
                    report_sources,
                    report_sources_are_real,
                )
                st.download_button(
                    label="⬇  Download PDF",
                    data=pdf_bytes,
                    file_name="research_report.pdf",
                    mime="application/pdf",
                    width="stretch",
                )
            with save_col:
                if st.button("★  Save Report", key="save-report", width="stretch"):
                    storage.add_saved_report(
                        report_topic, report_depth, report_sources, report_sources_are_real, report_text
                    )
                    st.success("Report saved. Find it under Saved Reports.")

            if st.button("Save report to reports/ folder", width="stretch"):
                try:
                    saved_path = research_agent.save_report_to_file(
                        report_text, report_topic, "md"
                    )
                    st.success(f"Report saved to: {saved_path}")
                except Exception as error:
                    st.error(f"Could not save report: {error}")
