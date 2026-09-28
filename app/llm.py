"""
llm.py — chat backend.

Two backends, same interface:

* ``ollama``  — the default. A local model over Ollama's HTTP API, so nothing
  leaves the machine.
* ``openai``  — any OpenAI-compatible chat endpoint (Groq, OpenRouter, vLLM,
  OpenAI itself). Used for the hosted demo, where there is no GPU to run a
  local model on.

The backend is chosen by ``LLM_BACKEND``; setting ``GROQ_API_KEY`` (or
``OPENAI_API_KEY``) selects the hosted path on its own, so the local default
still needs no configuration at all.
"""

import json
import os
from typing import Generator

import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
OPENAI_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = (os.getenv("GROQ_MODEL") or os.getenv("OPENAI_MODEL")
                or "openai/gpt-oss-120b")

_TIMEOUT = 120


def backend() -> str:
    """Which backend is active: ``"openai"`` or ``"ollama"``."""
    explicit = os.getenv("LLM_BACKEND", "").strip().lower()
    if explicit in ("openai", "groq"):
        return "openai"
    if explicit == "ollama":
        return "ollama"
    return "openai" if OPENAI_API_KEY else "ollama"


def backend_name() -> str:
    """Human-readable provider name, for the UI."""
    if backend() == "ollama":
        return "Ollama"
    host = OPENAI_BASE_URL.split("//")[-1].split("/")[0]
    return "Groq" if "groq" in host else host


def model_name() -> str:
    return OPENAI_MODEL if backend() == "openai" else OLLAMA_MODEL


def backend_ready() -> bool:
    """True when the active backend can actually serve a request."""
    if backend() == "openai":
        return bool(OPENAI_API_KEY)
    return is_ollama_running()


def is_ollama_running() -> bool:
    """Check if Ollama server is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_local_models() -> list[str]:
    """Return list of models available locally in Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if resp.status_code == 200:
            return [m["name"] for m in resp.json().get("models", [])]
    except requests.exceptions.RequestException:
        pass
    return []


# ── OpenAI-compatible transport ─────────────────────────────────────────────

def _openai_post(messages: list[dict], stream: bool):
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "No API key set for the hosted backend. Export GROQ_API_KEY, or "
            "unset LLM_BACKEND to fall back to a local Ollama model."
        )
    return requests.post(
        f"{OPENAI_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}",
                 "Content-Type": "application/json"},
        json={"model": OPENAI_MODEL, "messages": messages, "stream": stream},
        stream=stream,
        timeout=_TIMEOUT,
    )


def _openai_chat(messages: list[dict]) -> str:
    resp = _openai_post(messages, stream=False)
    if resp.status_code != 200:
        raise RuntimeError(
            f"{backend_name()} returned HTTP {resp.status_code}: {resp.text[:300]}"
        )
    return resp.json()["choices"][0]["message"]["content"]


def _openai_stream(messages: list[dict]) -> Generator[str, None, None]:
    with _openai_post(messages, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError(
                f"{backend_name()} returned HTTP {resp.status_code}: {resp.text[:300]}"
            )
        for raw_line in resp.iter_lines():
            if not raw_line or not raw_line.startswith(b"data: "):
                continue
            payload = raw_line[6:]
            if payload == b"[DONE]":
                break
            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue
            delta = chunk["choices"][0].get("delta", {}).get("content", "")
            if delta:
                yield delta


# ── Ollama transport ────────────────────────────────────────────────────────

def _ollama_stream(messages: list[dict]) -> Generator[str, None, None]:
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": True}
    with requests.post(f"{OLLAMA_HOST}/api/chat", json=payload,
                       stream=True, timeout=_TIMEOUT) as resp:
        if resp.status_code != 200:
            raise RuntimeError(
                f"Ollama returned HTTP {resp.status_code}: {resp.text[:300]}"
            )
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            try:
                chunk = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            delta = chunk.get("message", {}).get("content", "")
            if delta:
                yield delta
            if chunk.get("done", False):
                break


def _ollama_chat(messages: list[dict]) -> str:
    payload = {"model": OLLAMA_MODEL, "messages": messages, "stream": False}
    resp = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=_TIMEOUT)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Ollama returned HTTP {resp.status_code}: {resp.text[:300]}"
        )
    return resp.json().get("message", {}).get("content", "")


# ── Public interface ────────────────────────────────────────────────────────

def chat(messages: list[dict], stream: bool = False) -> str:
    """
    Send chat messages to the active backend and return the response text.

    Args:
        messages: List of dicts with 'role' ('system'|'user'|'assistant') and 'content'.
        stream:   If True, streams the response and returns the concatenated text.

    Returns:
        The assistant's response as a plain string.

    Raises:
        requests.exceptions.ConnectionError: if the backend is unreachable.
        RuntimeError: on non-200 HTTP responses, or a missing hosted API key.
    """
    if stream:
        return "".join(stream_chat(messages))
    return _openai_chat(messages) if backend() == "openai" else _ollama_chat(messages)


def stream_chat(messages: list[dict]) -> Generator[str, None, None]:
    """Yield text chunks from the active backend as they arrive."""
    source = _openai_stream if backend() == "openai" else _ollama_stream
    yield from source(messages)
