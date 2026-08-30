# Mini AI Research Agent — ResearchOS

## Overview

ResearchOS is a Python/Streamlit research agent that takes a real question,
searches the live web for sources, and uses an OpenRouter-hosted AI model to
analyze and synthesize the findings into a structured report.

**Live app:** https://mini-ai-research-os.streamlit.app

If no OpenRouter API key is configured, or live web search / the AI request
is temporarily unavailable, the app falls back to curated demo data instead
of crashing — every report clearly states whether it used live sources, live
AI, or a demo fallback, so the output is never presented as something it
isn't.

## Features

- Real-time web search (Wikipedia's public API) with real, clickable source URLs
- OpenRouter AI-powered analysis and synthesis, with automatic demo fallback
  if no API key is configured or a request fails
- The user's exact research question is preserved everywhere — session state,
  the report body, and every saved/reopened copy
- Clear AI/source verification notice on every report (live vs. demo, per
  stage)
- **Useful Insights** — every report includes a dedicated, mandatory section
  of takeaways synthesized from the findings, distinct from the Key Findings
  list rather than a repeat of it
- On mobile, the page automatically scrolls to the newly generated report as
  soon as research finishes
- Download the report as Markdown, plain text, or PDF
- Save a report to the local `reports/` folder for later
- **Research History** — every completed run is auto-saved and can be
  reopened without re-running research
- **Saved Reports** — manually saved reports, listed with open/delete
- **Sources Library** — every source collected across History and Saved
  Reports, de-duplicated and searchable
- **Settings** — AI engine status with a live "Test Connection" button,
  default research depth, session usage reset, and data management
  (clear History / Saved Reports)
- Press Enter in the research box to start research, or click the button —
  both work the same way
- Friendly error handling and input validation — the app will not crash on
  unusual input, a missing API key, or a failed search

## How the Agent Works

```
User Input
   -> Research Planning        (create_research_plan)
   -> Source Discovery         (discover_sources -- live web search, demo fallback)
   -> Information Collection   (collect_information)
   -> Analysis                 (analyze_information -- OpenRouter AI, demo fallback)
   -> Synthesis                (synthesize_findings -- OpenRouter AI, demo fallback)
   -> Final Report             (generate_report)
```

Each stage is a separate function in `research_agent.py`. `app.py` calls
these functions in order and displays the result of each stage in the
Streamlit UI, so the user can see the research process happening step by
step, rather than getting one big report all at once.

## Tech Stack

- Python 3
- Streamlit (web UI)
- `requests` — live web search (Wikipedia API) and OpenRouter API calls
- `python-dotenv` — local `.env` configuration
- `reportlab` — PDF report generation
- OpenRouter API — AI analysis and synthesis (any OpenRouter-hosted model)

## Project Structure

```
mini-ai-research-agent/
│
├── app.py                 # Streamlit UI: input, navigation, all page views
├── research_agent.py       # Core pipeline: planning, sources, analysis,
│                            # synthesis, report generation, History/Saved
│                            # Reports/Sources Library storage
├── openrouter_client.py    # The only module that talks to OpenRouter
├── web_search.py           # The only module that performs live web search
├── pdf_export.py           # PDF report generation
├── mock_data.py             # Demo/fallback research data
├── requirements.txt         # Python dependencies
├── .env.example              # Template for local configuration
├── README.md                  # This file
├── .gitignore
│
├── reports/                   # Saved reports (generated, gitignored)
└── history/                   # Auto-saved research history (generated, gitignored)
```

## Installation (local)

1. **Create a virtual environment:**

   ```
   python -m venv venv
   ```

2. **Activate the virtual environment (Windows):**

   ```
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

4. **Configure your OpenRouter API key:**

   Copy `.env.example` to `.env` and fill in your own key (get one at
   https://openrouter.ai/keys). This step is optional — the app works
   without it, using demo analysis instead of live AI.

5. **Run the application:**

   ```
   streamlit run app.py
   ```

   Streamlit will open the app automatically in your browser (usually at
   `http://localhost:8501`).

## Deployment

The live app is deployed on Streamlit Community Cloud from this repository's
`app.py`. Configuration is provided via Streamlit Secrets (never committed):

```
OPENROUTER_API_KEY = "your-key-here"
OPENROUTER_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
```

`.env` and `.streamlit/secrets.toml` are both git-ignored — API keys are
never stored in the repository.

## Future Development

- Source credibility checking to flag unreliable sources
- Automatic citations formatted in standard citation styles
- Additional live search providers beyond Wikipedia
- n8n automation to trigger research runs from external workflows

## Disclaimer

When live web search and OpenRouter AI are both available, reports are built
from real sources and real AI analysis. When either is unavailable, the app
falls back to demo data and labels the report accordingly — always check the
verification notice at the top of a report before treating it as real,
verified research.
