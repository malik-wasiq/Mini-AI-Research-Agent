# openrouter_client.py
#
# This is the ONLY file in the project that talks to OpenRouter over the
# network. It has one job: send chat messages, return the AI's reply text.
#
# Security notes:
#   - The API key is read from the OPENROUTER_API_KEY environment variable
#     (loaded from a local .env file). It is never hard-coded here.
#   - The key is only ever placed in the outgoing Authorization header.
#   - Errors raised by this module are safe to display in the UI: they
#     never include the API key or the request headers.

import os

import requests
from dotenv import load_dotenv

# Load variables from a local .env file into the process environment.
# This does not overwrite variables that are already set, and it never
# prints or returns their values.
load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
REQUEST_TIMEOUT_SECONDS = 60


class OpenRouterError(Exception):
    """
    Raised whenever an OpenRouter request can't be completed.
    Every message on this exception is safe to show in the UI or a
    report -- none of them ever contain the API key.
    """


def get_api_key():
    """Read the API key from the environment. Never log or return this elsewhere."""
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def get_model_name():
    """Read the configured model name, falling back to the free default model."""
    return os.environ.get("OPENROUTER_MODEL", "").strip() or DEFAULT_MODEL


def is_configured():
    """True if an API key is present, so callers can decide whether to try a real AI call."""
    return bool(get_api_key())


def chat_completion(messages, temperature=0.4, max_tokens=700):
    """
    Send a chat completion request to OpenRouter and return the assistant's
    reply text (a plain string). Raises OpenRouterError on any failure:
    missing key, network problem, timeout, or an API error response.
    """
    api_key = get_api_key()
    if not api_key:
        raise OpenRouterError(
            "No OpenRouter API key is configured. Add OPENROUTER_API_KEY to your .env file."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Optional identification headers OpenRouter uses for its public
        # rankings. Not secret, safe to keep fixed for this local demo.
        "HTTP-Referer": "http://localhost:8517",
        "X-Title": "Mini AI Research Agent",
    }

    payload = {
        "model": get_model_name(),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout:
        raise OpenRouterError("The OpenRouter request timed out. Please try again.")
    except requests.exceptions.RequestException as error:
        raise OpenRouterError(f"Could not reach OpenRouter ({type(error).__name__}).")

    if response.status_code != 200:
        # Surface OpenRouter's own error message when available, but never
        # the request itself (which carries the Authorization header).
        try:
            safe_detail = response.json().get("error", {}).get("message", "")
        except ValueError:
            safe_detail = response.text[:200]
        raise OpenRouterError(
            f"OpenRouter returned an error (HTTP {response.status_code}): {safe_detail}"
        )

    try:
        data = response.json()
    except ValueError as error:
        raise OpenRouterError(f"OpenRouter response was not valid JSON ({error}).")

    # OpenRouter's contract is a dict with a non-empty "choices" list, each
    # holding {"message": {"content": str}}. Free-tier models occasionally
    # return HTTP 200 with a malformed body (e.g. a bare string) instead,
    # so validate the shape explicitly rather than indexing blindly.
    choices = data.get("choices") if isinstance(data, dict) else None
    first_choice = choices[0] if isinstance(choices, list) and choices else None
    message = first_choice.get("message") if isinstance(first_choice, dict) else None
    content = message.get("content") if isinstance(message, dict) else None

    if not isinstance(content, str) or not content.strip():
        raise OpenRouterError("OpenRouter returned an unexpected response shape (no message content).")

    return content.strip()
