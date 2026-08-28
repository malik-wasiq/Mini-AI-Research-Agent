# research_agent.py
#
# This file contains the "brain" of our demo research agent.
# Every function here simulates one step of a research workflow:
#   Planning -> Source Discovery -> Collection -> Analysis -> Synthesis -> Report
#
# IMPORTANT: None of these functions call a real AI model or a real
# search engine. They use the demo data from mock_data.py instead.
# Later versions of this project can replace the *inside* of these
# functions with real API calls, while keeping the same function
# names and structure, so app.py will not need to change much.

import datetime
import json
import os
import re
import uuid

import openrouter_client
import web_search
from mock_data import find_topic_data

_BULLET_PREFIX_RE = re.compile(r"^(?:[-*•]|\d+[.)])\s*")


def _strip_bullet_prefix(text):
    return _BULLET_PREFIX_RE.sub("", text, count=1).strip()

# How many sources to use, based on the research depth the user picked.
# This is just a simple lookup dictionary.
SOURCE_COUNT_BY_DEPTH = {
    "Quick": 2,
    "Standard": 3,
    "Detailed": 4,
}


def create_research_plan(topic, depth):
    """
    Build a simple, human-readable research plan.
    In a real system, an AI model might generate this plan dynamically.
    Here, we use a fixed list of steps that applies to any topic.
    """
    plan_steps = [
        f"Define the research question for '{topic}'",
        "Identify important subtopics",
        "Find relevant sources",
        "Compare information across sources",
        "Identify key findings",
        "Generate final report",
    ]

    # "Detailed" research does a little more work, so we mention that.
    if depth == "Detailed":
        plan_steps.insert(3, "Look for contradictions and research gaps")

    return plan_steps


def discover_sources(topic, depth):
    """
    Discover real, live web sources for the topic via a real internet
    search. Falls back to the static demo sources only as an error
    fallback -- if the live search fails (network issue, no results,
    etc.) -- so the app keeps working either way.

    Returns a tuple: (sources, sources_are_real, error_message).
    error_message is None unless the live search failed.
    """
    max_sources = SOURCE_COUNT_BY_DEPTH.get(depth, 3)

    try:
        real_sources = web_search.discover_real_sources(topic, max_sources)
        return real_sources, True, None
    except web_search.WebSearchError as error:
        return _discover_demo_sources(topic, depth), False, str(error)


def _discover_demo_sources(topic, depth):
    """
    Return a list of demo sources for the given topic. Used only as an
    error fallback when live web search is unavailable.
    """
    topic_data = find_topic_data(topic)
    all_sources = topic_data["sources"]

    # Decide how many sources to use based on depth (default to Standard).
    max_sources = SOURCE_COUNT_BY_DEPTH.get(depth, 3)

    # Don't try to return more sources than we actually have.
    max_sources = min(max_sources, len(all_sources))

    return all_sources[:max_sources]


def collect_information(sources):
    """
    Simulate "collecting" information from each source.
    In a real agent, this is where we would fetch and read web pages.
    Here, we just package each source's summary as "collected text".
    """
    collected_items = []

    for source in sources:
        collected_items.append(
            {
                "source_name": source["name"],
                "collected_text": source["summary"],
            }
        )

    return collected_items


def _parse_labeled_bullet_sections(ai_text, section_labels):
    """
    Parse an AI response formatted as "LABEL:\n- item\n- item" sections
    into a dict of {label: [items]}. Tolerant of minor formatting drift
    that real AI models produce (markdown emphasis/headings around the
    label, "1." or "•" bullets instead of "-", a first item appended on
    the same line as the label) since a model that answered the question
    correctly shouldn't be discarded over cosmetic formatting.

    Always returns a dict, even if some (or all) labels end up with zero
    items -- callers decide how to handle missing sections, so genuinely
    empty/garbage responses can still be rejected upstream.
    """
    sections = {label: [] for label in section_labels}
    current_label = None

    for raw_line in ai_text.splitlines():
        line = raw_line.replace("**", "").strip().lstrip("#").strip()
        if not line:
            continue

        normalized = line.upper().replace(" ", "_")
        matched_label = None
        remainder = ""
        for label in section_labels:
            prefix = label + ":"
            if normalized.startswith(prefix):
                matched_label = label
                remainder = line[len(prefix):].strip()
                break

        if matched_label:
            current_label = matched_label
            item_text = _strip_bullet_prefix(remainder)
            if item_text:
                sections[current_label].append(item_text)
            continue

        if current_label and _BULLET_PREFIX_RE.match(line):
            item_text = _strip_bullet_prefix(line)
            if item_text:
                sections[current_label].append(item_text)

    return sections


def analyze_information(topic, collected_items):
    """
    Analyze the collected demo source text.

    If an OpenRouter API key is configured, this asks the AI model to read
    the collected demo source summaries and produce real key findings and
    research questions. If no key is configured, or the request fails for
    any reason, it falls back to the static demo analysis so the app keeps
    working without crashing.
    """
    topic_data = find_topic_data(topic)

    fallback_analysis = {
        "key_findings": topic_data["key_findings"],
        "research_questions": topic_data["research_questions"],
        "ai_powered": False,
        "ai_error": None,
    }

    if not openrouter_client.is_configured():
        return fallback_analysis

    source_text = "\n".join(
        f"- {item['source_name']}: {item['collected_text']}"
        for item in collected_items
    )

    prompt = (
        f'You are a research analyst. Topic: "{topic}".\n\n'
        f"Here are summaries collected from a few demo sources:\n{source_text}\n\n"
        "Based only on this information, respond in EXACTLY this format "
        "(no extra headings, no extra commentary):\n\n"
        "KEY_FINDINGS:\n- finding 1\n- finding 2\n- finding 3\n- finding 4\n\n"
        "RESEARCH_QUESTIONS:\n- question 1\n- question 2\n- question 3\n\n"
        "Keep each bullet to a single concise sentence."
    )

    try:
        ai_text = openrouter_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=900,
        )
        parsed = _parse_labeled_bullet_sections(
            ai_text, ["KEY_FINDINGS", "RESEARCH_QUESTIONS"]
        )
        if not parsed["KEY_FINDINGS"] and not parsed["RESEARCH_QUESTIONS"]:
            raise openrouter_client.OpenRouterError(
                "AI response did not contain any usable content."
            )

        # Preserve whatever the AI actually produced. Only the specific
        # section(s) it left empty (e.g. cut off by a token limit) fall
        # back to demo content, instead of discarding the whole response.
        missing = [
            label
            for label, key in (("KEY_FINDINGS", "key_findings"), ("RESEARCH_QUESTIONS", "research_questions"))
            if not parsed[label]
        ]

        return {
            "key_findings": parsed["KEY_FINDINGS"] or fallback_analysis["key_findings"],
            "research_questions": parsed["RESEARCH_QUESTIONS"] or fallback_analysis["research_questions"],
            "ai_powered": True,
            "ai_error": (
                f"AI response was incomplete; demo data filled in: {', '.join(missing)}."
                if missing else None
            ),
        }
    except openrouter_client.OpenRouterError as error:
        fallback_analysis["ai_error"] = str(error)
        return fallback_analysis


def synthesize_findings(topic, analysis, sources):
    """
    Synthesize (combine) the findings into higher-level insights: themes,
    benefits, challenges, contradictions, and research gaps.

    Uses OpenRouter AI when a key is configured and the request succeeds;
    otherwise falls back to the static demo synthesis.
    """
    topic_data = find_topic_data(topic)

    fallback_synthesis = {
        "themes": topic_data["themes"],
        "benefits": topic_data["benefits"],
        "challenges": topic_data["challenges"],
        "gaps": topic_data["gaps"],
        "contradictions": topic_data["contradictions"],
        "ai_powered": False,
        "ai_error": None,
    }

    if not openrouter_client.is_configured():
        return fallback_synthesis

    findings_text = "\n".join(f"- {finding}" for finding in analysis["key_findings"])
    source_names = ", ".join(source["name"] for source in sources)

    prompt = (
        f'You are a research analyst synthesizing findings about "{topic}".\n\n'
        f"Key findings from the analysis stage:\n{findings_text}\n\n"
        f"Demo sources used: {source_names}\n\n"
        "Based only on this information, respond in EXACTLY this format "
        "(no extra headings, no extra commentary):\n\n"
        "THEMES:\n- theme 1\n- theme 2\n\n"
        "BENEFITS:\n- benefit 1\n- benefit 2\n\n"
        "CHALLENGES:\n- challenge 1\n- challenge 2\n\n"
        "GAPS:\n- gap 1\n- gap 2\n\n"
        'CONTRADICTIONS:\n- contradiction 1 (write "- None noted" if there are none)\n\n'
        "Keep each bullet to a single concise sentence."
    )

    try:
        ai_text = openrouter_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1100,
        )
        labels = ["THEMES", "BENEFITS", "CHALLENGES", "GAPS", "CONTRADICTIONS"]
        parsed = _parse_labeled_bullet_sections(ai_text, labels)
        if not any(parsed[label] for label in labels):
            raise openrouter_client.OpenRouterError(
                "AI response did not contain any usable content."
            )

        # Preserve whatever the AI actually produced. Only the specific
        # section(s) it left empty (e.g. cut off by a token limit) fall
        # back to demo content, instead of discarding the whole response.
        field_by_label = {
            "THEMES": "themes",
            "BENEFITS": "benefits",
            "CHALLENGES": "challenges",
            "GAPS": "gaps",
            "CONTRADICTIONS": "contradictions",
        }
        missing = [label for label in labels if not parsed[label]]

        # "- None noted" is a valid, intentional answer for CONTRADICTIONS,
        # so filter it out of AI-sourced results only (not demo fallback,
        # which is already curated real content, not a placeholder).
        raw_contradictions = parsed["CONTRADICTIONS"]
        contradictions = (
            [item for item in raw_contradictions if "none" not in item.lower()]
            if raw_contradictions
            else fallback_synthesis["contradictions"]
        )

        return {
            "themes": parsed["THEMES"] or fallback_synthesis["themes"],
            "benefits": parsed["BENEFITS"] or fallback_synthesis["benefits"],
            "challenges": parsed["CHALLENGES"] or fallback_synthesis["challenges"],
            "gaps": parsed["GAPS"] or fallback_synthesis["gaps"],
            "contradictions": contradictions,
            "ai_powered": True,
            "ai_error": (
                f"AI response was incomplete; demo data filled in: "
                f"{', '.join(field_by_label[label] for label in missing)}."
                if missing else None
            ),
        }
    except openrouter_client.OpenRouterError as error:
        fallback_synthesis["ai_error"] = str(error)
        return fallback_synthesis


def generate_report(topic, depth, plan, sources, analysis, synthesis, sources_are_real=False):
    """
    Combine everything we generated in the previous steps into one
    final Markdown research report (as a single text string).
    """
    report_date = datetime.date.today().strftime("%B %d, %Y")

    # Build the Markdown report piece by piece using a list of lines,
    # then join them together at the end. This is easier to read than
    # one giant string.
    lines = []

    ai_powered = bool(analysis.get("ai_powered")) and bool(synthesis.get("ai_powered"))

    lines.append("# Research Report")
    lines.append("")
    if sources_are_real and ai_powered:
        lines.append(
            "> ✅ **Live Research Report** — Sources were found via a real-time "
            "web search, and analysis/synthesis were generated by OpenRouter AI."
        )
    elif sources_are_real:
        lines.append(
            "> 🌐 **Live Sources, Demo Analysis** — Sources were found via a "
            "real-time web search, but OpenRouter AI was unavailable for this "
            "run, so demo analysis/synthesis were used instead."
        )
    elif ai_powered:
        lines.append(
            "> 🤖 **AI-Assisted, Demo Sources** — Live web search was unavailable "
            "for this run, so demo source data was used. Analysis and synthesis "
            "were still generated by OpenRouter AI."
        )
    else:
        lines.append(
            "> ⚠️ **DEMO MODE** — Live web search and OpenRouter AI were both "
            "unavailable for this run, so demo data was used throughout."
        )
    lines.append("")
    lines.append(f"*Generated on {report_date} | Research depth: {depth}*")
    lines.append("")

    # Always show the user's own question here, not a mock-data label:
    # find_topic_data() matches by loose substring, which can pick an
    # unrelated canned topic_data entry for longer, free-form questions.
    lines.append("## Research Topic")
    lines.append("")
    lines.append(topic)
    lines.append("")

    lines.append("## Executive Summary")
    lines.append("")
    lines.append(
        f"This report explores '{topic}' using "
        f"{'real, live web sources' if sources_are_real else 'simulated demo sources'} "
        f"and {'AI-generated' if ai_powered else 'demo'} analysis. It follows a "
        f"{depth.lower()} research process covering planning, source discovery, "
        "analysis, and synthesis of key findings."
    )
    lines.append("")

    lines.append("## Research Questions")
    lines.append("")
    for question in analysis["research_questions"]:
        lines.append(f"- {question}")
    lines.append("")

    lines.append("## Key Findings")
    lines.append("")
    for finding in analysis["key_findings"]:
        lines.append(f"- {finding}")
    lines.append("")

    lines.append("## Major Themes")
    lines.append("")
    for theme in synthesis["themes"]:
        lines.append(f"- {theme}")
    lines.append("")

    lines.append("## Benefits / Opportunities")
    lines.append("")
    for benefit in synthesis["benefits"]:
        lines.append(f"- {benefit}")
    lines.append("")

    lines.append("## Challenges / Limitations")
    lines.append("")
    for challenge in synthesis["challenges"]:
        lines.append(f"- {challenge}")
    lines.append("")

    lines.append("## Research Gaps")
    lines.append("")
    for gap in synthesis["gaps"]:
        lines.append(f"- {gap}")
    lines.append("")

    if synthesis["contradictions"]:
        lines.append("## Contradictions Found")
        lines.append("")
        for contradiction in synthesis["contradictions"]:
            lines.append(f"- {contradiction}")
        lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        f"Based on this research process, '{topic}' "
        "shows clear opportunities alongside real challenges."
        + ("" if (sources_are_real and ai_powered) else
           " A fully live version of this agent would confirm these findings "
           "using real-world sources and AI-powered analysis throughout.")
    )
    lines.append("")

    lines.append("## Sources")
    lines.append("")
    if sources_are_real:
        lines.append(
            "*These are REAL sources found via a live web search — the links "
            "below go to the actual pages used.*"
        )
    else:
        lines.append(
            "*Live web search was unavailable for this run, so these are demo "
            "sources for illustration purposes only.*"
        )
    lines.append("")
    for index, source in enumerate(sources, start=1):
        lines.append(f"{index}. **{source['name']}** — {source['topic']}")
        lines.append(f"   - Summary: {source['summary']}")
        if sources_are_real:
            lines.append(f"   - URL: {source['url']}")
        else:
            lines.append(f"   - URL (demo): {source['url']}")
    lines.append("")

    report_text = "\n".join(lines)
    return report_text


def parse_report_markdown(report_text):
    """
    Split a generated report markdown string into an intro block
    (title/status line/date) and a list of (heading, body) sections, so
    the exact same content can be reused across the UI cards and other
    export formats (e.g. PDF) without re-deriving it.
    """
    intro_lines = []
    sections = []
    current_heading = None
    current_lines = []

    for line in report_text.split("\n"):
        if line.startswith("## "):
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line[3:].strip()
            current_lines = []
        elif line.startswith("# "):
            continue
        else:
            if current_heading is None:
                intro_lines.append(line)
            else:
                current_lines.append(line)

    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    return "\n".join(intro_lines).strip(), sections


def markdown_to_plain_text(markdown_text):
    """
    Turn our Markdown report into a simpler plain-text version for the
    .txt download option. This is a very basic conversion: it just
    removes common Markdown symbols like #, *, and >.
    """
    plain_lines = []

    for line in markdown_text.split("\n"):
        clean_line = line
        clean_line = clean_line.replace("# ", "")
        clean_line = clean_line.replace("## ", "")
        clean_line = clean_line.replace("### ", "")
        clean_line = clean_line.replace("**", "")
        clean_line = clean_line.replace("> ", "")
        clean_line = clean_line.replace("*", "")
        plain_lines.append(clean_line)

    return "\n".join(plain_lines)


REPORTS_FOLDER = "reports"


def save_report_to_file(report_text, topic, file_extension, depth=None, sources=None, sources_are_real=False):
    """
    Save the generated report inside the reports/ folder, plus a JSON
    metadata sidecar (same base file name) recording the topic, depth,
    sources and a summary excerpt -- this is what lets the Saved Reports
    feature list and reopen this exact report later with no re-research.
    Returns the full file path of the saved report file.
    """
    # Make sure the reports folder exists before saving into it.
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)

    # Build a simple, safe file name from the topic and current time.
    safe_topic = "".join(
        character if character.isalnum() else "_" for character in topic
    ).strip("_")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{safe_topic}_{timestamp}"
    file_name = f"{base_name}.{file_extension}"
    file_path = os.path.join(REPORTS_FOLDER, file_name)

    with open(file_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_text)

    _, sections = parse_report_markdown(report_text)
    summary = dict(sections).get("Executive Summary", "")
    metadata = {
        "id": base_name,
        "topic": topic,
        "depth": depth,
        "created_at": datetime.datetime.now().isoformat(),
        "source_count": len(sources) if sources else 0,
        "sources_are_real": sources_are_real,
        "summary": summary,
        "sources": sources or [],
        "report_text": report_text,
        "report_file": file_name,
    }
    metadata_path = os.path.join(REPORTS_FOLDER, f"{base_name}.json")
    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, ensure_ascii=False, indent=2)

    return file_path


def list_saved_reports():
    """
    Return lightweight metadata (no full report text) for every report
    saved via save_report_to_file, most recent first.
    """
    if not os.path.exists(REPORTS_FOLDER):
        return []

    entries = []
    for file_name in os.listdir(REPORTS_FOLDER):
        if not file_name.endswith(".json"):
            continue
        try:
            with open(os.path.join(REPORTS_FOLDER, file_name), "r", encoding="utf-8") as metadata_file:
                data = json.load(metadata_file)
        except (OSError, ValueError):
            continue

        entries.append({
            "id": data.get("id", file_name[:-5]),
            "topic": data.get("topic", ""),
            "depth": data.get("depth"),
            "created_at": data.get("created_at", ""),
            "source_count": data.get("source_count", 0),
            "sources_are_real": data.get("sources_are_real", False),
            "summary": data.get("summary", ""),
        })

    entries.sort(key=lambda entry: entry["created_at"], reverse=True)
    return entries


def load_saved_report(report_id):
    """Load a single saved report's full data (including report_text and sources)."""
    path = os.path.join(REPORTS_FOLDER, f"{report_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def delete_saved_report(report_id):
    """
    Delete a saved report: its JSON metadata sidecar and the underlying
    report file it points to. Returns True if the metadata file existed
    and was removed.
    """
    metadata_path = os.path.join(REPORTS_FOLDER, f"{report_id}.json")
    if not os.path.exists(metadata_path):
        return False

    try:
        with open(metadata_path, "r", encoding="utf-8") as metadata_file:
            data = json.load(metadata_file)
    except (OSError, ValueError):
        data = None

    os.remove(metadata_path)

    if data and data.get("report_file"):
        report_file_path = os.path.join(REPORTS_FOLDER, data["report_file"])
        if os.path.exists(report_file_path):
            os.remove(report_file_path)

    return True


# ---------------------------------------------------------------------
# Research History: automatically persists every completed research run
# (as one JSON file per run inside history/) so it can be listed and
# reopened later without re-running the research pipeline. This mirrors
# the same simple file-based storage pattern used by save_report_to_file
# above, just with structured data instead of raw report text.
# ---------------------------------------------------------------------
HISTORY_FOLDER = "history"


def _history_file_path(entry_id):
    return os.path.join(HISTORY_FOLDER, f"{entry_id}.json")


def save_history_entry(topic, depth, sources, sources_are_real, report_text):
    """
    Persist a completed research run to history/. Returns the new
    entry's id. The full report text and sources are stored so the
    report can be reopened exactly as generated, with no re-research.
    """
    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)

    _, sections = parse_report_markdown(report_text)
    summary = dict(sections).get("Executive Summary", "")

    entry_id = uuid.uuid4().hex
    entry = {
        "id": entry_id,
        "topic": topic,
        "depth": depth,
        "created_at": datetime.datetime.now().isoformat(),
        "source_count": len(sources),
        "sources_are_real": sources_are_real,
        "summary": summary,
        "sources": sources,
        "report_text": report_text,
    }

    with open(_history_file_path(entry_id), "w", encoding="utf-8") as history_file:
        json.dump(entry, history_file, ensure_ascii=False, indent=2)

    return entry_id


def list_history_entries():
    """
    Return lightweight metadata (no full report text) for every saved
    history entry, most recent first.
    """
    if not os.path.exists(HISTORY_FOLDER):
        return []

    entries = []
    for file_name in os.listdir(HISTORY_FOLDER):
        if not file_name.endswith(".json"):
            continue
        try:
            with open(os.path.join(HISTORY_FOLDER, file_name), "r", encoding="utf-8") as history_file:
                data = json.load(history_file)
        except (OSError, ValueError):
            continue

        entries.append({
            "id": data.get("id", file_name[:-5]),
            "topic": data.get("topic", ""),
            "depth": data.get("depth", ""),
            "created_at": data.get("created_at", ""),
            "source_count": data.get("source_count", 0),
            "sources_are_real": data.get("sources_are_real", False),
            "summary": data.get("summary", ""),
        })

    entries.sort(key=lambda entry: entry["created_at"], reverse=True)
    return entries


def load_history_entry(entry_id):
    """Load a single history entry's full data (including report_text and sources)."""
    path = _history_file_path(entry_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as history_file:
        return json.load(history_file)


def delete_history_entry(entry_id):
    """Delete a history entry. Returns True if a file was actually removed."""
    path = _history_file_path(entry_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
