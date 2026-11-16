# NEXUS

[![NEXUS 1.1 validation](https://github.com/melo31022/NEXUS/actions/workflows/tests.yml/badge.svg?branch=dev-1.1)](https://github.com/melo31022/NEXUS/actions/workflows/tests.yml?query=branch%3Adev-1.1)

**An AI-powered computer-use agent for Windows, built with Python and cloud AI providers.**

NEXUS connects to cloud-hosted AI models to interpret requests, plan tasks, and interact with Windows through local tools. Language-model inference runs in the selected cloud provider; NEXUS does not run models locally.

[Português (Brasil)](README.pt-BR.md)

---

## Version 1.1.0

NEXUS 1.1 is the development line that extends the 1.0 foundation with reliability, task checkpoints, additional provider configurations, and expanded desktop controls.

### Features

- **Cloud AI providers:** Groq Cloud, Ollama Cloud, OpenRouter, Cerebras, Together AI, and DeepSeek.
- **Model catalog:** Retrieves available models from the selected provider.
- **Operation modes:** Chat, Planner, and Operator.
- **Windows tools:** Mouse, keyboard, window activation, screenshots, file operations, and PowerShell.
- **Workspace:** Selects a working directory for project tasks.
- **Optional vision:** Sends screenshots only when enabled and when the selected model is configured for image input.
- **Token Guard:** Estimates context size, compacts older conversation turns, and applies configurable output and tool-call limits.
- **Task checkpoints:** Persists task progress and action outcomes; `/tasks` lists recent records.
- **Provider retries:** Uses bounded retries for selected transient HTTP errors and honors `Retry-After`.
- **Safety checks:** Applies heuristic checks and local confirmation to potentially destructive operations.
- **Languages:** Portuguese (Brazil) and English.

Provider and model capabilities vary. A model appearing in a catalog does not guarantee tool-calling or image-input compatibility. The current DeepSeek default is `deepseek-flash`, which supports image input; OpenRouter's configured vision defaults include Nemotron 3.5 Super VL.

## Requirements

- Windows 10 or Windows 11.
- Python 3.11 or newer.
- Internet connection.
- API key for a supported cloud provider.

## Quick Start (CMD)

The commands below are intended for **Command Prompt (CMD)**, not PowerShell.

1. Download the `dev-1.1` branch archive from GitHub and extract it.
2. Open CMD in the extracted project folder.
3. Run:

   ```cmd
   py -3.11 iniciar.py
   ```

   Alternatively, use `python iniciar.py`.
4. On first launch, the launcher creates a virtual environment, installs dependencies, and creates `.env` from `.env.example` when needed.
5. Launch NEXUS and run `/setup` to configure provider, API key, HTTPS endpoint and model in the terminal. The key is entered without echo and encrypted for the current Windows user with DPAPI. Existing `.env` settings remain supported.
6. Run `/test` to verify the connection, then `/agents` and `/agent <id>` to select a model.

The first installation requires an internet connection. Later launches reuse the virtual environment.

## Manual Installation (CMD)

Run these commands from the project folder:

```cmd
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python.exe main.py
```

## Provider Configuration

Set `NEXUS_PROVIDER` in `.env` to one of: `groq`, `ollama`, `openrouter`, `cerebras`, `together`, or `deepseek`. Configure the corresponding API key and optional model variable. See [docs/PROVIDERS.md](docs/PROVIDERS.md) for provider-specific settings and limitations.

Example:

```env
NEXUS_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Never publish or share `.env` or API keys.

## Commands

| Command | Description |
|---|---|
| `/providers` | Lists supported providers. |
| `/setup [provider]` | Configures provider, key, endpoint and model in the terminal. |
| `/key status`, `/key set`, `/key remove` | Checks, saves or removes an API key without displaying it. |
| `/endpoint [https://...]` | Shows or changes the active provider endpoint. |
| `/test` | Tests authentication and a short model response. |
| `/modeltest` | Runs live chat, JSON, context, tool-call and optional vision checks. |
| `/resume <id>` | Starts a user-reviewed continuation linked to an interrupted task checkpoint. |
| `/provider <name>` | Selects a provider. |
| `/tasks` | Lists recent task checkpoints. |
| `/agents` or `/models` | Retrieves available models. |
| `/agent <number or id>` | Selects a model. |
| `/modes` | Lists operation modes. |
| `/mode chat`, `/mode planner`, `/mode operator` | Selects an operation mode. |
| `/language auto`, `/language pt`, `/language en` | Selects the interface language. |
| `/vision on` / `/vision off` | Enables or disables screenshot sharing. |
| `/workspace` | Displays the current workspace. |
| `/workspace <folder>` | Selects an existing working directory. |
| `/workspace off` | Disables the selected workspace. |
| `/status` | Displays current configuration. |
| `/init` | Creates a starter NEXUS.md file. |
| `/help` | Displays available commands. |
| `/clear` | Clears the terminal. |
| `/exit` | Exits NEXUS. |

## Task Recovery

NEXUS writes JSON checkpoints to `nexus_tasks/`. Use `/tasks` to inspect recent task states and recorded actions. The journal does **not** automatically replay clicks, typing, PowerShell commands, or file writes after an interruption. Review the current computer state before manually continuing. See [docs/TASK_RECOVERY.md](docs/TASK_RECOVERY.md).

## Vision and Privacy

Vision is disabled by default. When enabled, screenshots may be sent to the selected cloud provider if the selected model supports image input. Screenshots can contain private information; close sensitive applications and documents before enabling vision.

Keep API keys in `.env`, never commit that file, and avoid running NEXUS as Administrator without a clear reason. NEXUS operates with the permissions of the current Windows account. Its safety checks are heuristic and are not a sandbox or a complete security boundary.

## Testing and acceptance

See [docs/TESTING.md](docs/TESTING.md) for the CI matrix, local CMD test commands, Windows desktop acceptance checklist and live-provider validation matrix. Development status is tracked in [DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md).

## Known Limitations and Validation

- Token counts are estimates, not exact provider tokenization.
- Provider API compatibility, tool calling, and vision vary by provider and model.
- Task checkpoints preserve state for review but do not automatically replay uncertain actions.
- Session conversation history is not restored after restarting NEXUS.
- GitHub Actions is configured to run unit tests and compilation on Ubuntu, Windows x64, and Windows ARM64 (`windows-11-arm`). This does not replace manual desktop acceptance tests or live provider checks.

## Project Structure

```text
nexus/
├── .env.example
├── .github/workflows/tests.yml
├── docs/
│   ├── PROVIDERS.md
│   ├── TASK_RECOVERY.md
│   ├── MODELTEST.md
│   └── TESTING.md
├── agent.py
├── model_test.py
├── catalog.py
├── config.py
├── i18n.py
├── iniciar.py
├── main.py
├── providers.py
├── task_recovery.py
├── token_guard.py
├── tools.py
├── tests/
│   ├── test_core.py
│   ├── test_reliability.py
│   └── test_model_test.py
├── README.md
├── README.pt-BR.md
├── ROADMAP.md
├── CHANGELOG.md
├── DEVELOPMENT_PROGRESS.md
└── VERSION
```

## Roadmap and Changelog

See [ROADMAP.md](ROADMAP.md) for implemented work and remaining items. See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

No license has been selected yet. Until a license is added, the default copyright rules apply. Public repository visibility does not automatically grant permission to reuse, modify, or redistribute this project.

---

**NEXUS 1.1.0 — Development branch**


## ModelTest

Run `/modeltest` to make live, non-destructive capability checks against the selected provider/model. It asks for confirmation because the six checks may consume API quota. Planner output and two tool calls are tested; tool calls are inspected but never executed. Sending a desktop screenshot requires a separate explicit confirmation. Model self-identification is not treated as proof of provider/model identity. See [docs/MODELTEST.md](docs/MODELTEST.md).
