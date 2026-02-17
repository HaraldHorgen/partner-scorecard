"""
API key management and Anthropic AI integration for ChannelPRO™.

Key resolution order:
  1. ``ANTHROPIC_API_KEY`` environment variable (preferred for production).
  2. Session-cached key (survives page navigations within a session).
  3. User-provided key via ``st.text_input`` (fallback for local dev).
"""
import json
import os
import re

import streamlit as st


# ── Key resolution ──────────────────────────────────────────────────────

def resolve_api_key() -> str:
    """Return an Anthropic API key, prompting the user only as a last resort.

    Resolution order:
      1. ``ANTHROPIC_API_KEY`` environment variable.
      2. Value already stored in ``st.session_state["_anthropic_api_key"]``.
      3. Interactive ``st.text_input`` (password field).

    If a valid key is obtained it is cached in session state so that
    subsequent page navigations within the same session do not re-prompt.

    Calls ``st.stop()`` if no key is available.
    """
    # 1. Environment variable (set on Render dashboard or .env)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

    # 2. Session state cache
    if not api_key:
        api_key = st.session_state.get("_anthropic_api_key", "")

    # 3. User input (only shown when env var is missing)
    if not api_key:
        api_key = st.text_input(
            "Enter your Anthropic API key",
            type="password",
            key="ai_api_key",
            help=(
                "Set ANTHROPIC_API_KEY in Render → Environment → Environment "
                "Variables, then **redeploy** the service. Or enter it here for "
                "this session."
            ),
        )

    # Persist for the remainder of this session
    if api_key:
        st.session_state["_anthropic_api_key"] = api_key
        return api_key

    st.info(
        "An Anthropic API key is required. Set `ANTHROPIC_API_KEY` in your "
        "Render environment variables (then redeploy), or paste one above."
    )
    st.stop()
    return ""  # unreachable


# ── AI call ─────────────────────────────────────────────────────────────

def call_ai(messages: list[dict], api_key: str, system_prompt: str) -> dict:
    """Call the Anthropic Messages API and return a parsed JSON response.

    Parameters
    ----------
    messages : list[dict]
        Conversation history in ``[{"role": ..., "content": ...}, ...]`` form.
    api_key : str
        Anthropic API key.
    system_prompt : str
        System-level prompt containing partner data context.

    Returns
    -------
    dict
        Parsed response with keys ``answer``, ``table``, ``chart``, ``updates``.
    """
    import requests as req

    try:
        resp = req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": messages,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            return {
                "answer": f"API error ({resp.status_code}): {resp.text}",
                "table": None,
                "chart": None,
                "updates": None,
            }
        data = resp.json()
        text = "".join(
            b.get("text", "")
            for b in data.get("content", [])
            if b.get("type") == "text"
        )
        # Strip markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "answer": text if "text" in dir() else "Could not parse AI response.",
            "table": None,
            "chart": None,
            "updates": None,
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "table": None,
            "chart": None,
            "updates": None,
        }
