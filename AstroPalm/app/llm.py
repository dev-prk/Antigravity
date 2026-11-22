"""Shared Gemini Interactions API helper with fast failover across current models."""
from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
MODELS = ["gemini-4-hydrogen", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
_COOLDOWN_UNTIL: dict[str, float] = {}


def get_api_key() -> str | None:
    load_dotenv(ENV_PATH, override=True)
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    return key or None


def create_interaction(*, system_instruction: str, input_data, response_format=None, previous_interaction_id: str | None = None):
    """Call Gemini Interactions API with fast failover on 503/429/timeout."""
    api_key = get_api_key()
    if not api_key:
        return None, "missing_api_key"

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=20000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    last_err = None
    now = time.monotonic()
    candidates = [m for m in MODELS if _COOLDOWN_UNTIL.get(m, 0) <= now] or MODELS
    for idx, model in enumerate(candidates):
        kwargs = {
            "model": model,
            "system_instruction": system_instruction,
            "input": input_data,
            "timeout": 10.0 if model == "gemini-4-hydrogen" else 30.0,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format
        if previous_interaction_id:
            kwargs["previous_interaction_id"] = previous_interaction_id

        try:
            return client.interactions.create(**kwargs), None
        except Exception as exc:
            last_err = exc
            msg = str(exc).lower()
            retryable = any(k in msg for k in ("503", "429", "unavailable", "high demand", "rate limit", "too_many_requests", "timed out", "timeout"))
            if not retryable:
                raise
            _COOLDOWN_UNTIL[model] = time.monotonic() + 180
            # Do not reuse an interaction id across a model switch if it failed.
            if previous_interaction_id:
                raise
    raise last_err
