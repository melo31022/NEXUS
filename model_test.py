"""Non-destructive live capability checks for the selected NEXUS model."""
from __future__ import annotations

import json
import time
from typing import Any

import requests

from providers import request_with_retry, sanitized_api_error


def _request(provider: Any, model: str, messages: list[dict[str, Any]], **options: Any) -> tuple[dict[str, Any] | None, float, str]:
    headers = {"Content-Type": "application/json"}
    if provider.api_key:
        headers["Authorization"] = f"Bearer {provider.api_key}"
    payload: dict[str, Any] = {"model": model, "messages": messages, "temperature": 0, "max_tokens": 256}
    payload.update(options)
    started = time.monotonic()
    try:
        response = request_with_retry(
            lambda: requests.post(provider.normalized_base_url() + "/chat/completions",
                                  headers=headers, json=payload, timeout=(10, 40)),
            retries=2,
        )
    except requests.RequestException as exc:
        return None, time.monotonic() - started, f"Falha de rede: {type(exc).__name__}"
    elapsed = time.monotonic() - started
    if not response.ok:
        return None, elapsed, sanitized_api_error(response.status_code, response.text)
    try:
        data = response.json()
    except ValueError:
        return None, elapsed, "O provedor retornou JSON inválido."
    if not isinstance(data, dict):
        return None, elapsed, "Formato de resposta inesperado."
    return data, elapsed, ""


def _message(data: dict[str, Any] | None) -> dict[str, Any]:
    if not data:
        return {}
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return {}
    message = choices[0].get("message")
    return message if isinstance(message, dict) else {}


def _record(name: str, status: str, detail: str, elapsed: float = 0.0) -> dict[str, Any]:
    return {"name": name, "status": status, "detail": detail[:220], "latency": round(elapsed, 2)}


def run_model_test(provider: Any, model: str, image_data_url: str | None = None) -> list[dict[str, Any]]:
    """Probe chat, JSON, short-term context, tool-call emission and optional vision.

    Tool calls are inspected but never executed. A screenshot is tested only when
    the caller explicitly supplies an image data URL after user consent.
    """
    results: list[dict[str, Any]] = []
    system = {"role": "system", "content": "Responda de forma objetiva e siga exatamente as instruções."}

    data, elapsed, error = _request(provider, model, [system, {"role": "user", "content": "Responda somente NEXUS_OK."}], max_tokens=32)
    answer = _message(data).get("content", "")
    ok = isinstance(answer, str) and bool(answer.strip())
    results.append(_record("Chat", "PASS" if ok else "FAIL", "Resposta recebida." if ok else (error or "Resposta vazia."), elapsed))

    data, elapsed, error = _request(
        provider, model,
        [system, {"role": "user", "content": 'Retorne somente um objeto JSON válido com a propriedade "ok" igual a true.'}],
        response_format={"type": "json_object"}, max_tokens=64,
    )
    answer = _message(data).get("content", "")
    try:
        parsed = json.loads(answer) if isinstance(answer, str) else None
        json_ok = isinstance(parsed, dict) and parsed.get("ok") is True
    except (ValueError, TypeError):
        json_ok = False
    unsupported = any(f"HTTP {code}" in error for code in (400, 404, 422))
    json_status = "PASS" if json_ok else ("PARTIAL" if data is None and unsupported else "FAIL")
    results.append(_record("JSON mode", json_status, "Objeto JSON válido recebido." if json_ok else (error or "JSON solicitado não foi retornado."), elapsed))

    first, elapsed_first, error_first = _request(
        provider, model,
        [system, {"role": "user", "content": "Memorize este código: NEXUS-7319-ORBIT. Responda apenas entendido."}],
        max_tokens=24,
    )
    if first is not None:
        second, elapsed_second, error_second = _request(
            provider, model,
            [system,
             {"role": "user", "content": "Memorize este código: NEXUS-7319-ORBIT. Responda apenas entendido."},
             {"role": "assistant", "content": str(_message(first).get("content", ""))},
             {"role": "user", "content": "Qual código pedi para memorizar? Responda apenas o código."}],
            max_tokens=32,
        )
        remembered = str(_message(second).get("content", "")) if second is not None else ""
        context_ok = "NEXUS-7319-ORBIT" in remembered
        results.append(_record("Contexto curto", "PASS" if context_ok else "FAIL",
                               "Código recuperado na chamada seguinte." if context_ok else (error_second or "Código não recuperado."),
                               elapsed_first + elapsed_second))
    else:
        results.append(_record("Contexto curto", "FAIL", error_first, elapsed_first))

    probe_tool = [{
        "type": "function",
        "function": {
            "name": "nexus_modeltest_probe",
            "description": "Ferramenta fictícia de teste; nunca é executada.",
            "parameters": {"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
        },
    }]
    data, elapsed, error = _request(
        provider, model,
        [system, {"role": "user", "content": "Chame nexus_modeltest_probe uma vez com value=NEXUS_TEST. Não responda em texto."}],
        tools=probe_tool, tool_choice="auto", max_tokens=96,
    )
    calls = _message(data).get("tool_calls", []) if data else []
    tool_ok = isinstance(calls, list) and any(
        isinstance(call, dict) and isinstance(call.get("function"), dict)
        and call["function"].get("name") == "nexus_modeltest_probe" for call in calls
    )
    unsupported = any(f"HTTP {code}" in error for code in (400, 404, 422))
    tool_status = "PASS" if tool_ok else ("PARTIAL" if data is None and unsupported else "FAIL")
    results.append(_record("Tool calling", tool_status,
                           "Chamada fictícia emitida; ferramenta não executada." if tool_ok else (error or "Chamada não emitida."), elapsed))

    if not image_data_url:
        results.append(_record("Vision", "SKIP", "Nenhuma captura foi compartilhada para este teste."))
    elif not provider.supports_vision(model):
        results.append(_record("Vision", "SKIP", "Modelo não cadastrado como compatível com imagens."))
    else:
        data, elapsed, error = _request(
            provider, model,
            [{"role": "user", "content": [
                {"type": "text", "text": "Descreva em uma frase apenas elementos realmente visíveis nesta captura."},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ]}],
            max_tokens=128,
        )
        answer = _message(data).get("content", "")
        results.append(_record("Vision", "PASS" if isinstance(answer, str) and answer.strip() else "FAIL",
                               str(answer).strip()[:220] if answer else (error or "Descrição vazia."), elapsed))
    return results
