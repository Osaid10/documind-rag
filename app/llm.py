import os
import json
import requests
from typing import Generator

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


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
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
    except requests.exceptions.RequestException:
        pass
    return []


def chat(messages: list[dict], stream: bool = False) -> str:
    """
    Send a list of chat messages to Ollama and return the assistant response text.

    Args:
        messages: List of dicts with 'role' ('system'|'user'|'assistant') and 'content'.
        stream:   If True, streams the response and returns the full concatenated text.

    Returns:
        The assistant's response as a plain string.

    Raises:
        requests.exceptions.ConnectionError: if Ollama is not reachable.
        RuntimeError: on non-200 HTTP responses.
    """
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": stream,
    }

    if stream:
        full_response = ""
        with requests.post(url, json=payload, stream=True, timeout=120) as resp:
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
                full_response += delta
                if chunk.get("done", False):
                    break
        return full_response
    else:
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code != 200:
            raise RuntimeError(
                f"Ollama returned HTTP {resp.status_code}: {resp.text[:300]}"
            )
        data = resp.json()
        return data.get("message", {}).get("content", "")


def stream_chat(messages: list[dict]) -> Generator[str, None, None]:
    """
    Generator that yields text chunks from Ollama as they arrive.

    Yields:
        str: Incremental text delta from the assistant.
    """
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
    }

    with requests.post(url, json=payload, stream=True, timeout=120) as resp:
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
