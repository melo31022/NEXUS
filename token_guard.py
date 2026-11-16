"""Lightweight token budgeting and conversation compaction for NEXUS."""
from __future__ import annotations

from typing import Any

DEFAULT_CONTEXT_BUDGET = 16_000
DEFAULT_OUTPUT_TOKENS = 2_048


def estimate_text_tokens(text: str) -> int:
    """Conservative, dependency-free estimate; not a provider tokenizer."""
    if not text:
        return 0
    # Three characters/token is a deliberately conservative, provider-neutral estimate.
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
        if message.get("reasoning_content") is not None:
            total += estimate_text_tokens(str(message.get("reasoning_content")))
        if message.get("reasoning_details") is not None:
            total += estimate_text_tokens(str(message.get("reasoning_details")))
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
    """Compact old turns and oversized outputs while preserving system and latest task state."""
    copied = [dict(message) for message in messages]
    estimate = estimate_messages_tokens(copied, tool_schema)
    if estimate <= budget:
        return copied, estimate, False

    systems = [message for message in copied if message.get("role") == "system"]
    conversation = [message for message in copied if message.get("role") != "system"]
    if not conversation:
        return copied, estimate, False

    keep_count = max(2, min(int(preserve_recent), 12))
    start = max(0, len(conversation) - keep_count)
    if start == 0 and len(conversation) > 4:
        start = len(conversation) - 4
    while start < len(conversation) and conversation[start].get("role") != "user":
        start += 1
    if start >= len(conversation):
        start = max(0, len(conversation) - min(4, len(conversation)))

    removed = conversation[:start]
    kept = conversation[start:]
    summary_parts: list[str] = []
    for item in removed:
        role = str(item.get("role", "message"))
        content = item.get("content", "")
        if isinstance(content, str) and content.strip():
            summary_parts.append(f"{role}: {content[:300]}")
        elif role == "assistant" and item.get("tool_calls"):
            summary_parts.append("assistant: uma ou mais ações/ferramentas foram solicitadas.")
    summary = ""
    if removed:
        summary = (
            "Resumo compacto do histórico anterior (estimado; não substitui o estado atual):\n"
            + ("\n".join(summary_parts[-8:]) or "Mensagens anteriores omitidas para respeitar o orçamento.")
        )[:1600]

    def build() -> list[dict[str, Any]]:
        result = list(systems)
        if summary:
            result.append({"role": "system", "content": summary})
        result.extend(kept)
        return result

    compacted = build()
    new_estimate = estimate_messages_tokens(compacted, tool_schema)

    while new_estimate > budget and len(kept) > 2:
        next_user = next((index for index in range(1, len(kept)) if kept[index].get("role") == "user"), None)
        if next_user is None:
            break
        dropped = kept[:next_user]
        for item in dropped:
            role = str(item.get("role", "message"))
            content = item.get("content", "")
            if isinstance(content, str) and content.strip():
                summary_parts.append(f"{role}: {content[:160]}")
        kept = kept[next_user:]
        if summary_parts:
            summary = (
                "Resumo compacto do histórico anterior (estimado; não substitui o estado atual):\n"
                + "\n".join(summary_parts[-8:])
            )[:1600]
        compacted = build()
        new_estimate = estimate_messages_tokens(compacted, tool_schema)

    for item in kept:
        if new_estimate <= budget:
            break
        role = item.get("role")
        content = item.get("content")
        if role in {"tool", "assistant"} and isinstance(content, str) and len(content) > 700:
            original_length = len(content)
            item["content"] = content[:600] + f"\n[resultado compactado; {original_length - 600} caracteres omitidos]"
            compacted = build()
            new_estimate = estimate_messages_tokens(compacted, tool_schema)

    if new_estimate > budget:
        for item in reversed(kept):
            if item.get("role") != "user" or not isinstance(item.get("content"), str):
                continue
            content = item["content"]
            fixed_messages = systems + ([{"role": "system", "content": summary}] if summary else [])
            available_chars = max(300, (budget - estimate_messages_tokens(fixed_messages, tool_schema) - 100) * 2)
            if len(content) > available_chars:
                side = max(120, available_chars // 2)
                omitted = len(content) - side * 2
                item["content"] = content[:side] + f"\n[parte central omitida pelo Token Guard: {omitted} caracteres]\n" + content[-side:]
                compacted = build()
                new_estimate = estimate_messages_tokens(compacted, tool_schema)
            break

    return compacted, new_estimate, True
