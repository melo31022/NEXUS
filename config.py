"""Cloud-only provider configuration for NEXUS."""
from __future__ import annotations

import os
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path

from secure_store import load_settings as load_secure_settings, save_settings as save_secure_settings

BASE_DIR = Path(__file__).resolve().parent


def load_env_file(path: Path | None = None) -> None:
    """Load a simple .env file without overriding real environment variables."""
    env_path = path or BASE_DIR / ".env"
    if not env_path.is_file():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if value and value[0:1] in {"'", '"'} and value[-1:] == value[0:1]:
                value = value[1:-1]
            if key and key not in os.environ:
                os.environ[key] = value
    except OSError:
        return


load_env_file()


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    label: str
    base_url: str
    api_key: str
    default_model: str
    requires_api_key: bool = True
    vision_models: tuple[str, ...] = ()
    api_key_env: str = ""
    supports_tools: bool = True

    def normalized_base_url(self) -> str:
        return self.base_url.strip().rstrip("/")

    def supports_vision(self, model: str) -> bool:
        model_lower = model.lower()
        return any(model_lower == item.lower() for item in self.vision_models)


def _env(name: str, fallback: str = "") -> str:
    return os.getenv(name, fallback).strip()


# Endpoints are intentionally fixed to hosted services. NEXUS RC3 does not
# support local inference or arbitrary OpenAI-compatible endpoints.
PROVIDERS: dict[str, ProviderConfig] = {
    "ollama": ProviderConfig(
        name="ollama",
        label="Ollama Cloud",
        base_url="https://ollama.com/v1",
        api_key=_env("OLLAMA_API_KEY"),
        default_model=_env("OLLAMA_MODEL", "beam"),
        requires_api_key=True,
        vision_models=tuple(x.strip() for x in _env("OLLAMA_VISION_MODELS").split(",") if x.strip()),
        api_key_env="OLLAMA_API_KEY",
    ),
    "groq": ProviderConfig(
        name="groq",
        label="Groq Cloud",
        base_url="https://api.groq.com/openai/v1",
        api_key=_env("GROQ_API_KEY"),
        default_model=_env("GROQ_MODEL", "openai/gpt-oss-120b"),
        requires_api_key=True,
        vision_models=("qwen/qwen3.8-27b",),
        api_key_env="GROQ_API_KEY",
    ),
    "openrouter": ProviderConfig(name="openrouter", label="OpenRouter", base_url="https://openrouter.ai/api/v1", api_key=_env("OPENROUTER_API_KEY"), default_model=_env("OPENROUTER_MODEL", "openai/gpt-4o-mini"), api_key_env="OPENROUTER_API_KEY", vision_models=tuple(x.strip() for x in _env("OPENROUTER_VISION_MODELS").split(",") if x.strip())),
    "cerebras": ProviderConfig(name="cerebras", label="Cerebras Cloud", base_url="https://api.cerebras.ai/v1", api_key=_env("CEREBRAS_API_KEY"), default_model=_env("CEREBRAS_MODEL", "llama-3.3-70b"), api_key_env="CEREBRAS_API_KEY", vision_models=tuple(x.strip() for x in _env("CEREBRAS_VISION_MODELS").split(",") if x.strip())),
    "together": ProviderConfig(name="together", label="Together AI", base_url="https://api.together.xyz/v1", api_key=_env("TOGETHER_API_KEY"), default_model=_env("TOGETHER_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo"), api_key_env="TOGETHER_API_KEY", vision_models=tuple(x.strip() for x in _env("TOGETHER_VISION_MODELS").split(",") if x.strip())),
    "deepseek": ProviderConfig(name="deepseek", label="DeepSeek", base_url="https://api.deepseek.com/v1", api_key=_env("DEEPSEEK_API_KEY"), default_model=_env("DEEPSEEK_MODEL", "deepseek-chat"), api_key_env="DEEPSEEK_API_KEY", vision_models=tuple(x.strip() for x in _env("DEEPSEEK_VISION_MODELS").split(",") if x.strip())),
}

# Secure settings override .env values. API keys are protected with Windows DPAPI.
SECURE_STORE_ERROR = ""
try:
    _SAVED_SETTINGS = load_secure_settings()
except RuntimeError as exc:
    _SAVED_SETTINGS = {}
    SECURE_STORE_ERROR = str(exc)

_saved_providers = _SAVED_SETTINGS.get("providers", {})
if isinstance(_saved_providers, dict):
    for _name, _values in _saved_providers.items():
        if _name not in PROVIDERS or not isinstance(_values, dict):
            continue
        _current = PROVIDERS[_name]
        PROVIDERS[_name] = replace(
            _current,
            api_key=str(_values.get("api_key", _current.api_key) or ""),
            default_model=str(_values.get("model", _current.default_model) or _current.default_model),
            base_url=str(_values.get("base_url", _current.base_url) or _current.base_url),
        )

DEFAULT_PROVIDER = str(_SAVED_SETTINGS.get("default_provider") or _env("NEXUS_PROVIDER", "ollama")).lower()
if DEFAULT_PROVIDER not in PROVIDERS:
    # Older RC2 .env files may still say "remote". Fall back to a hosted
    # provider instead of accidentally trying localhost.
    DEFAULT_PROVIDER = "ollama"


def _positive_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(_env(name, str(default)))
    except ValueError:
        return default
    return value if minimum <= value <= maximum else default


MAX_STEPS_PER_TASK = _positive_int("NEXUS_MAX_STEPS", 18, 1, 60)
REQUEST_TIMEOUT = _positive_int("NEXUS_REQUEST_TIMEOUT", 75, 10, 300)
MAX_CONTEXT_TOKENS = _positive_int("NEXUS_MAX_CONTEXT_TOKENS", 16000, 2000, 200000)
MAX_OUTPUT_TOKENS = _positive_int("NEXUS_MAX_OUTPUT_TOKENS", 2048, 128, 16000)
MAX_TOOL_CALLS_PER_STEP = _positive_int("NEXUS_MAX_TOOL_CALLS_PER_STEP", 6, 1, 20)


def get_provider(name: str) -> ProviderConfig:
    try:
        return PROVIDERS[name.lower()]
    except KeyError as exc:
        available = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Provedor em nuvem desconhecido: {name}. Disponíveis: {available}.") from exc

_UNSET = object()


def save_provider_settings(
    name: str,
    *,
    api_key: str | object = _UNSET,
    model: str | object = _UNSET,
    base_url: str | object = _UNSET,
) -> ProviderConfig:
    """Persist provider settings securely and refresh the live configuration."""
    provider_name = name.strip().lower()
    if provider_name not in PROVIDERS:
        raise ValueError(f"Provedor desconhecido: {provider_name}")
    current = PROVIDERS[provider_name]
    candidate = deepcopy(_SAVED_SETTINGS)
    values = candidate.setdefault("providers", {}).setdefault(provider_name, {})
    if api_key is not _UNSET:
        key = str(api_key).strip()
        if key:
            values["api_key"] = key
        else:
            values.pop("api_key", None)
    if model is not _UNSET:
        selected_model = str(model).strip()
        if not selected_model:
            raise ValueError("O ID do modelo não pode ficar vazio.")
        values["model"] = selected_model
    if base_url is not _UNSET:
        endpoint = str(base_url).strip().rstrip("/")
        if not endpoint.startswith("https://") or len(endpoint) > 300:
            raise ValueError("O endpoint precisa ser uma URL HTTPS válida.")
        values["base_url"] = endpoint
    if not values:
        candidate.get("providers", {}).pop(provider_name, None)
    # Save first. A failed DPAPI write must not partially update live settings.
    save_secure_settings(candidate)
    _SAVED_SETTINGS.clear()
    _SAVED_SETTINGS.update(candidate)
    if api_key is not _UNSET and current.api_key_env:
        os.environ.pop(current.api_key_env, None)
    updated = replace(
        current,
        api_key=(
            str(values.get("api_key", current.api_key) or "")
            if api_key is _UNSET
            else str(values.get("api_key", "") or "")
        ),
        default_model=str(values.get("model", current.default_model)),
        base_url=str(values.get("base_url", current.base_url)),
    )
    PROVIDERS[provider_name] = updated
    return updated

def save_default_provider(name: str) -> None:
    global DEFAULT_PROVIDER
    provider_name = name.strip().lower()
    if provider_name not in PROVIDERS:
        raise ValueError(f"Provedor desconhecido: {provider_name}")
    _SAVED_SETTINGS["default_provider"] = provider_name
    save_secure_settings(_SAVED_SETTINGS)
    DEFAULT_PROVIDER = provider_name
