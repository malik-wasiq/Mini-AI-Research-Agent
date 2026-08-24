# storage.py
#
# Simple JSON-file persistence for Research History and Saved Reports.
# Deliberately not a database -- this is an MVP feature, and plain JSON
# files under data/ are enough to survive reruns and app restarts while
# keeping the change surface small.

import datetime
import json
import os
import uuid

import research_agent

DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
SAVED_FILE = os.path.join(DATA_DIR, "saved_reports.json")


def _load(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _save(file_path, items):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=2)


def _make_summary(report_text, max_chars=220):
    """Pull a short, real excerpt from the report's Executive Summary."""
    _, sections = research_agent.parse_report_markdown(report_text)
    for heading, body in sections:
        if heading == "Executive Summary" and body:
            summary = " ".join(body.split())
            return summary[:max_chars].rstrip() + ("..." if len(summary) > max_chars else "")
    return ""


def _make_entry(topic, depth, sources, sources_are_real, report_text):
    return {
        "id": uuid.uuid4().hex,
        "question": topic,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "depth": depth,
        "source_count": len(sources),
        "summary": _make_summary(report_text),
        "report_text": report_text,
        "sources": sources,
        "sources_are_real": sources_are_real,
    }


# ---------------------------------------------------------------------
# Research History -- every successfully completed research run
# ---------------------------------------------------------------------
def add_history_entry(topic, depth, sources, sources_are_real, report_text):
    entry = _make_entry(topic, depth, sources, sources_are_real, report_text)
    items = _load(HISTORY_FILE)
    items.insert(0, entry)
    _save(HISTORY_FILE, items)
    return entry


def list_history():
    return _load(HISTORY_FILE)


def delete_history_entry(entry_id):
    items = [item for item in _load(HISTORY_FILE) if item["id"] != entry_id]
    _save(HISTORY_FILE, items)


# ---------------------------------------------------------------------
# Saved Reports -- explicitly saved by the user from a completed report
# ---------------------------------------------------------------------
def add_saved_report(topic, depth, sources, sources_are_real, report_text):
    entry = _make_entry(topic, depth, sources, sources_are_real, report_text)
    entry["title"] = topic
    items = _load(SAVED_FILE)
    items.insert(0, entry)
    _save(SAVED_FILE, items)
    return entry


def list_saved_reports():
    return _load(SAVED_FILE)


def delete_saved_report(entry_id):
    items = [item for item in _load(SAVED_FILE) if item["id"] != entry_id]
    _save(SAVED_FILE, items)
