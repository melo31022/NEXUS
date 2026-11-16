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


## Interactive CMD setup and credential storage

Use `/setup [provider]` inside NEXUS to configure a provider without editing files. The API key is collected through hidden terminal input and saved encrypted for the current Windows user with Windows DPAPI under `%LOCALAPPDATA%\\NEXUS\\settings.dat`. It cannot be decrypted by another Windows user account on the same computer.

Other commands:

- `/key status [provider]`: show whether a key is configured; never prints the secret.
- `/key set [provider]`: securely enter and save a key without echoing it.
- `/key remove [provider]`: remove the saved key after confirmation.
- `/endpoint`: show the current provider endpoint.
- `/endpoint https://...`: change the endpoint; HTTPS is required.
- `/test`: send a short, low-token chat request to verify endpoint, authentication and selected model. This request may count against the provider's quota.

Existing `.env` configurations remain supported. Secure settings saved through the CMD take precedence over `.env`. Never paste keys into ordinary commands, chat messages, logs, screenshots, or source files.
