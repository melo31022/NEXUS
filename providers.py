"""Provider-neutral HTTP retry and capability helpers for cloud chat APIs."""
from __future__ import annotations

import random
import re
import time
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

import requests

T = TypeVar("T")
TRANSIENT_STATUS = {408, 425, 429, 500, 502, 503, 504}


def retry_delay(response: requests.Response | None, attempt: int, *, maximum: float = 30.0) -> float:
    if response is not None:
        raw = response.headers.get("Retry-After", "").strip()
        if raw:
            try:
                return min(maximum, max(0.0, float(raw)))
            except ValueError:
                try:
                    when = parsedate_to_datetime(raw)
                    if when.tzinfo is None:
                        when = when.replace(tzinfo=timezone.utc)
                    return min(maximum, max(0.0, (when - datetime.now(timezone.utc)).total_seconds()))
                except (TypeError, ValueError, OverflowError):
                    pass
    return min(maximum, 1.5 * (2 ** max(0, attempt - 1)) + random.uniform(0, 0.4))


def adapt_chat_payload(provider_name: str, model: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize provider-specific Chat Completions parameters without mutating the caller."""
    adapted = dict(payload)
    if provider_name == "cerebras":
        if "max_tokens" in adapted:
            adapted["max_completion_tokens"] = adapted.pop("max_tokens")
        if model == "zai-glm-4.7":
            adapted["temperature"] = 1.0
            adapted["top_p"] = 0.95
            adapted["clear_thinking"] = False
    return adapted


def request_with_retry(
    request: Callable[[], requests.Response],
    *,
    retries: int = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> requests.Response:
    """Retry network errors and transient HTTP statuses; never retry ordinary 4xx errors."""
    last_error: Exception | None = None
    for attempt in range(1, max(1, retries) + 1):
        response: requests.Response | None = None
        try:
            response = request()
            if response.status_code not in TRANSIENT_STATUS or attempt >= retries:
                return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt >= retries:
                raise
        delay = retry_delay(response, attempt)
        sleep(delay)
    if last_error:
        raise last_error
    raise RuntimeError("Falha de rede sem resposta do provedor.")


def sanitized_api_error(status: int, body: str) -> str:
    detail = " ".join(str(body).split())[:500]
    detail = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]+=*", r"\1[redacted]", detail)
    detail = re.sub(r"(?i)((?:api[_ -]?key|token|password|secret)\s*[:=]\s*)[^\s,;]+", r"\1[redacted]", detail)
    return f"API retornou HTTP {status}. Detalhe sanitizado: {detail or 'sem detalhes'}"
