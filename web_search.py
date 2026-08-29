# web_search.py
#
# This is the ONLY file in the project that performs real, live web
# research. It has two jobs: search the real internet for a topic, and
# fetch a short real-content excerpt for each result.
#
# It uses Wikipedia's public, key-free JSON APIs (search + page
# summary) reached over plain HTTPS with `requests` -- already a
# project dependency. No browser automation, no extra packages, no
# API key required. Errors here are always raised as WebSearchError so
# callers can fall back to demo data safely.

import re
from urllib.parse import quote

import requests

WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
REQUEST_TIMEOUT_SECONDS = 10
USER_AGENT = "Mini-AI-Research-Agent/1.0 (Streamlit research demo project)"

# Matches generic conversational wrappers around a question (e.g. "Tell me
# something about ...", "What is ...?"), regardless of topic. Wikipedia's
# search ranks on keyword relevance across the whole query string, so these
# filler words get scored right alongside the actual topic -- for topics
# whose real keywords are common/strong (e.g. "generative AI") the correct
# page still wins, but for narrower topics (e.g. "thallium scan") the filler
# words can outweigh the one or two words that actually matter, burying the
# relevant page under unrelated results that happen to match "tell", "me",
# "about", etc. Stripping the wrapper before searching fixes this generically
# for any topic, without hardcoding topic-specific logic.
_CONVERSATIONAL_PREFIX_RE = re.compile(
    r"^(?:please\s+)?(?:"
    r"tell me (?:something )?about|"
    r"can you tell me about|"
    r"could you tell me about|"
    r"i want to know about|"
    r"give me (?:some )?information (?:on|about)|"
    r"what (?:is|are|was|were)|"
    r"who (?:is|are|was|were)|"
    r"explain|"
    r"describe|"
    r"define"
    r")\s+",
    re.IGNORECASE,
)


class WebSearchError(Exception):
    """
    Raised whenever a live web search or page fetch can't be completed.
    Callers should catch this and fall back to demo data.
    """


def _clean_search_query(topic):
    """
    Strip a generic conversational wrapper and trailing punctuation from a
    raw user question before sending it to the search engine's relevance
    ranking. Falls back to the original topic if cleaning would leave
    nothing behind.
    """
    cleaned = topic.strip()
    stripped = _CONVERSATIONAL_PREFIX_RE.sub("", cleaned, count=1).strip()
    stripped = stripped.rstrip("?").strip()
    return stripped or cleaned


def search_web(query, max_results=3):
    """
    Search the live web via Wikipedia's public search API (no API key
    needed) and return a list of {title, url} dicts for real, live
    pages. Raises WebSearchError on any network problem or if no
    results are found.
    """
    search_query = _clean_search_query(query)
    try:
        response = requests.get(
            WIKI_SEARCH_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": search_query,
                "format": "json",
                "srlimit": max_results,
            },
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException as error:
        raise WebSearchError(f"Could not reach the search engine ({type(error).__name__}).")

    if response.status_code != 200:
        raise WebSearchError(f"Search engine returned HTTP {response.status_code}.")

    try:
        results = response.json()["query"]["search"]
    except (KeyError, ValueError, TypeError):
        raise WebSearchError("Unexpected response format from the search engine.")

    if not results:
        raise WebSearchError("No live web results were found for this topic.")

    sources = []
    for item in results[:max_results]:
        # Each entry should be {"title": str, ...}. Skip anything that
        # isn't shaped that way instead of indexing it blindly.
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        if not isinstance(title, str) or not title:
            continue
        sources.append(
            {
                "title": title,
                "url": "https://en.wikipedia.org/wiki/" + title.replace(" ", "_"),
            }
        )

    if not sources:
        raise WebSearchError("No usable live web results were found for this topic.")

    return sources


def fetch_page_excerpt(title, max_chars=600):
    """
    Fetch a real, live page summary and return a short plain-text
    excerpt of its actual content. Returns None (does not raise) on
    any failure, so a single unreachable page doesn't take down the
    whole search -- the caller just skips that source.
    """
    try:
        response = requests.get(
            WIKI_SUMMARY_URL.format(title=quote(title.replace(" ", "_"))),
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        extract = response.json().get("extract", "")
    except (ValueError, AttributeError, TypeError):
        return None

    extract = extract.strip()
    return extract[:max_chars] if extract else None


def discover_real_sources(topic, max_results=3):
    """
    Search the live web for the topic and collect a short real-content
    excerpt for each result. Returns a list of source dicts shaped to
    match the rest of the research pipeline:
    {name, topic, summary, url} -- with `url` always a real, live link.
    Raises WebSearchError if the search itself fails or nothing usable
    could be collected.
    """
    results = search_web(topic, max_results)

    sources = []
    for result in results:
        excerpt = fetch_page_excerpt(result["title"])
        if not excerpt:
            continue
        sources.append(
            {
                "name": result["title"],
                "topic": "en.wikipedia.org",
                "summary": excerpt,
                "url": result["url"],
            }
        )

    if not sources:
        raise WebSearchError("Live web results could not be read for this topic.")

    return sources
