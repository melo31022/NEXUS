"""Lightweight token budgeting and conversation compaction for NEXUS."""
from __future__ import annotations

from typing import Any

DEFAULT_CONTEXT_BUDGET = 16_000
DEFAULT_OUTPUT_TOKENS = 2_048


def estimate_text_tokens(text: str) -> int:
    """Conservative, dependency-free estimate; not a provider tokenizer."""
    if not text:
        return 0
    # Four characters/token is a common rough estimate; add a safety margin.
    return max(1, (len(text) + 2) // 3)


def estimate_messages_tokens(messages: list[dict[str, Any]], tool_schema: Any = None) -> int:
    total = 8
    for message in messages:
        total += 12
        content = message.get("content", "")
        if isinstance(content, str):
            total += estimate_text_tokens(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    total += estimate_text_tokens(str(part.get("text", "")))
                    # Image payloads are provider-dependent; reserve a conservative budget.
                    if part.get("type") == "image_url":
                        total += 1_000
        total += estimate_text_tokens(str(message.get("tool_calls", "")))
    if tool_schema:
        total += estimate_text_tokens(str(tool_schema))
    return total


def compact_messages(
    messages: list[dict[str, Any]],
    *,
    budget: int = DEFAULT_CONTEXT_BUDGET,
    tool_schema: Any = None,
    preserve_recent: int = 12,
) -> tuple[list[dict[str, Any]], int, bool]:
    """Drop complete older conversation turns while preserving system and recent state."""
    copied = list(messages)
    estimate = estimate_messages_tokens(copied, tool_schema)
    if estimate <= budget:
        return copied, estimate, False

    systems = [m for m in copied if m.get("role") == "system"]
    conversation = [m for m in copied if m.get("role") != "system"]
    if len(conversation) <= preserve_recent:
        return copied, estimate, False

    # Start at a user boundary so assistant tool calls and their tool replies stay together.
    start = max(0, len(conversation) - preserve_recent)
    while start < len(conversation) and conversation[start].get("role") != "user":
        start += 1
    if start >= len(conversation):
        start = max(0, len(conversation) - preserve_recent)
    removed = conversation[:start]
    kept = conversation[start:]
    summary_parts: list[str] = []
    for item in removed:
        role = str(item.get("role", "message"))
        content = item.get("content", "")
        if isinstance(content, str) and content.strip():
            summary_parts.append(f"{role}: {content[:500]}")
        elif role == "assistant" and item.get("tool_calls"):
            summary_parts.append("assistant: ações/ferramentas anteriores foram solicitadas.")
    summary = "Resumo compacto do histórico anterior (estimado; preserve as instruções e o estado recente):\n"
    summary += "\n".join(summary_parts[-12:]) or "Histórico anterior omitido para respeitar o orçamento."
    compacted = systems + [{"role": "system", "content": summary}] + kept
    new_estimate = estimate_messages_tokens(compacted, tool_schema)
    # If still too large, remove oldest complete turns, never system messages or the newest user turn.
    while new_estimate > budget and len(kept) > 2:
        next_user = next((i for i in range(1, len(kept)) if kept[i].get("role") == "user"), None)
        if next_user is None:
            break
        kept = kept[next_user:]
        compacted = systems + [{"role": "system", "content": summary}] + kept
        new_estimate = estimate_messages_tokens(compacted, tool_schema)
    return compacted, new_estimate, True
