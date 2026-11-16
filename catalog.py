"""Provider model-catalog parsing helpers."""
from __future__ import annotations

from typing import Any


def extract_model_ids(payload: Any, provider: str = "") -> list[str]:
    """Extract model IDs from OpenAI /models or Ollama /api/tags payloads."""
    if not isinstance(payload, dict):
        return []

    entries: Any = payload.get("data")
    if not isinstance(entries, list) or not entries:
        entries = payload.get("models")
    if not isinstance(entries, list):
        return []

    model_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        value = entry.get("id") or entry.get("model") or entry.get("name")
        if not isinstance(value, str):
            continue
        model_id = value.strip()
        if not model_id:
            continue
        # Ollama's /api/tags may show CLI tags like "beam:cloud";
        # its hosted OpenAI-compatible endpoint uses "beam" as the model ID.
        if provider.lower() == "ollama" and model_id.endswith(":cloud"):
            model_id = model_id[:-6]
        model_ids.add(model_id)
    return sorted(model_ids, key=str.casefold)
