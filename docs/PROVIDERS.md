# NEXUS 1.1 — Cloud provider configuration

NEXUS sends inference requests to hosted APIs. It does not run local language models.

| Provider | Base URL | API key environment variable |
|---|---|---|
| Ollama Cloud | https://ollama.com/v1 | OLLAMA_API_KEY |
| Groq Cloud | https://api.groq.com/openai/v1 | GROQ_API_KEY |
| OpenRouter | https://openrouter.ai/api/v1 | OPENROUTER_API_KEY |
| Cerebras Cloud | https://api.cerebras.ai/v1 | CEREBRAS_API_KEY |
| Together AI | https://api.together.xyz/v1 | TOGETHER_API_KEY |
| DeepSeek | https://api.deepseek.com/v1 | DEEPSEEK_API_KEY |

Set `NEXUS_PROVIDER` and the corresponding key/model variables in `.env`. Then use `/provider <name>`, `/agents`, and `/agent <model-id>`.

The additional providers use OpenAI-compatible Chat Completions and model-list conventions. This is an integration baseline, not a guarantee that every model supports tool calling, images, or the same parameter set. Tool calling and vision vary by provider and model. NEXUS only enables image input for models explicitly listed in that provider's `vision_models` configuration.

Do not commit `.env`, paste API keys into issues, or include them in logs. If a provider returns an authentication, quota, unsupported-feature, or model error, verify its current account/model documentation and select a model that supports the requested feature.

## Runtime limits

- `NEXUS_MAX_CONTEXT_TOKENS`: estimated context budget (default 16000).
- `NEXUS_MAX_OUTPUT_TOKENS`: requested output ceiling (default 2048).
- `NEXUS_MAX_TOOL_CALLS_PER_STEP`: maximum tool calls processed per model turn (default 6).
- `NEXUS_MAX_STEPS`: maximum model/tool cycles per task.
- `NEXUS_REQUEST_TIMEOUT`: request timeout in seconds.

Token estimates are conservative heuristics, not exact provider tokenization. Leave headroom for provider-specific message and image accounting.
