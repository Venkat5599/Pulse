"""DeepSeek V4 Flash client (OpenAI-compatible, via the AICredits gateway).

Thin wrapper over /chat/completions using `requests` only — no SDK dependency.
Supports both a blocking `complete()` and a streaming `stream()` generator that
yields ("reasoning"|"answer", text) deltas for live SSE relay.
"""
from __future__ import annotations

import json
import os
from typing import Iterator

import requests

DEFAULT_BASE_URL = "https://api.aicredits.in/v1"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash"


class LLMConfigError(RuntimeError):
    pass


def _config() -> tuple[str, str, str]:
    base = os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("PULSE_LLM_MODEL", DEFAULT_MODEL)
    key = os.environ.get("LLM_API_KEY", "")
    if not key:
        raise LLMConfigError("LLM_API_KEY is not set (put it in .env or the environment).")
    return base, model, key


def _payload(messages: list[dict], stream: bool, max_tokens: int, temperature: float) -> dict:
    return {
        "model": _config()[1],
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def complete(messages: list[dict], *, max_tokens: int = 1200, temperature: float = 0.3,
             timeout: int = 60) -> str:
    """Blocking completion. Returns the visible answer text."""
    base, _, key = _config()
    r = requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=_payload(messages, False, max_tokens, temperature),
        timeout=timeout,
    )
    r.raise_for_status()
    return (r.json()["choices"][0]["message"]["content"] or "").strip()


def stream(messages: list[dict], *, max_tokens: int = 1200, temperature: float = 0.3,
           timeout: int = 90) -> Iterator[tuple[str, str]]:
    """Streaming completion. Yields ('reasoning'|'answer', delta_text)."""
    base, _, key = _config()
    with requests.post(
        f"{base}/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=_payload(messages, True, max_tokens, temperature),
        stream=True,
        timeout=timeout,
    ) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                delta = json.loads(data)["choices"][0]["delta"]
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
            if delta.get("reasoning_content"):
                yield "reasoning", delta["reasoning_content"]
            if delta.get("content"):
                yield "answer", delta["content"]
