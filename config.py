"""Cloud-only provider configuration for NEXUS."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

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
    ),
    "groq": ProviderConfig(
        name="groq",
        label="Groq Cloud",
        base_url="https://api.groq.com/openai/v1",
        api_key=_env("GROQ_API_KEY"),
        default_model=_env("GROQ_MODEL", "openai/gpt-oss-120b"),
        requires_api_key=True,
        vision_models=("qwen/qwen3.8-27b",),
    ),
}

DEFAULT_PROVIDER = _env("NEXUS_PROVIDER", "ollama").lower()
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


def get_provider(name: str) -> ProviderConfig:
    try:
        return PROVIDERS[name.lower()]
    except KeyError as exc:
        raise ValueError(f"Provedor em nuvem desconhecido: {name}. Use ollama ou groq.") from exc
