# NEXUS

**An AI-powered computer-use agent for Windows, built with Python and cloud AI providers.**

NEXUS is a Windows desktop agent that connects to cloud-hosted AI models to interpret requests, plan tasks, and interact with the operating system through available tools.

NEXUS does not run language models locally. All AI inference is performed by the selected cloud provider.

[Português (Brasil)](README.pt-BR.md)

---

## Features

**Version 1.1.0**

- **Cloud AI providers:** Supports Ollama Cloud, Groq Cloud, OpenRouter, Cerebras, Together AI, and DeepSeek through hosted API endpoints.
- **Dynamic model catalog:** Retrieves available models from the selected provider.
- **Three operation modes:** Chat, Planner, and Operator.
- **PowerShell integration:** Executes supported PowerShell commands.
- **Workspace awareness:** Allows tasks to use a selected working directory.
- **Screenshot support:** Captures desktop screenshots when requested.
- **Optional vision:** Sends screenshots to compatible cloud models when enabled.
- **Windows metadata:** Retrieves information about the screen and active window.
- **Safety checks:** Uses heuristic checks and local confirmation for potentially destructive operations.
- **Multilingual interface:** Supports Portuguese (Brazil) and English.
- **Token Guard:** Estimates context size, compacts older conversation turns, and limits output tokens/tool calls.
- **Task checkpoints:** Saves task progress and action outcomes; `/tasks` lists recent records. Unsafe actions are never replayed automatically.
- **Provider retries:** Uses bounded retries for transient HTTP errors and honors `Retry-After`.

Some capabilities depend on the selected provider and model. Model availability does not guarantee tool-calling or image-input compatibility.

## Requirements

- Windows 10 or Windows 11.
- Python 3.11 or newer.
- Internet connection.
- API key from a supported cloud provider.

## Quick Start

1. Download the project from GitHub.
2. Extract the downloaded archive.
3. Open the extracted `nexus` folder.
4. Make sure Python 3.11 or newer is installed.
5. Open a terminal in the project folder.
6. Run:

   ```powershell
   py -3.11 iniciar.py
   ```

   Alternatively:

   ```powershell
   python iniciar.py
   ```

7. On the first launch, the launcher creates a virtual environment, installs dependencies, and creates `.env` from `.env.example` if necessary.
8. Open `.env` and add your API key.
9. Save the file and launch NEXUS again.

The first installation requires an internet connection and may take a few minutes.

Later launches reuse the existing virtual environment and only install dependencies when necessary.

## Manual Installation

If you prefer to configure the environment manually:

```powershell
py -3.11 -m venv .venv

.\.venv\Scripts\python.exe -m pip install --upgrade pip

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Copy-Item .env.example .env

.\.venv\Scripts\python.exe main.py
```

## Provider Configuration

Configure your provider in the `.env` file. Supported provider names: `ollama`, `groq`, `openrouter`, `cerebras`, `together`, and `deepseek`. See [provider details](docs/PROVIDERS.md).

Never publish or share this file.

### Groq Cloud

```env
NEXUS_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

### Ollama Cloud

```env
NEXUS_PROVIDER=ollama
OLLAMA_API_KEY=your_ollama_api_key
OLLAMA_MODEL=beam
```

The available models depend on provider availability and account access.

Some models may not support all NEXUS tools or image input.

## Operation Modes

### Chat

Conversational mode without computer-operation tools.

### Planner

Analyzes requests and creates plans without executing computer operations.

### Operator

Uses the available tools to perform supported computer operations.

## Commands

| Command | Description |
|---|---|
| `/providers` | Lists supported providers. |
| `/provider <name>` | Selects any configured cloud provider. |
| `/tasks` | Lists recent task checkpoints. |
| `/agents` | Retrieves available models. |
| `/models` | Alternative model catalog command. |
| `/agent <number or id>` | Selects a model. |
| `/modes` | Lists operation modes. |
| `/mode chat` | Activates Chat mode. |
| `/mode planner` | Activates Planner mode. |
| `/mode operator` | Activates Operator mode. |
| `/language auto` | Automatically detects language. |
| `/language pt` | Selects Portuguese. |
| `/language en` | Selects English. |
| `/vision on` | Enables screenshot sharing with compatible models. |
| `/vision off` | Disables screenshot sharing. |
| `/workspace` | Displays the current workspace. |
| `/workspace <folder>` | Sets the working directory. |
| `/workspace off` | Disables the selected workspace. |
| `/status` | Displays current configuration. |
| `/init` | Creates a starter NEXUS.md file. |
| `/help` | Displays available commands. |
| `/clear` | Clears the terminal. |
| `/exit` | Exits NEXUS. |

## Task Recovery

NEXUS writes JSON checkpoints to `nexus_tasks/`. Use `/tasks` to inspect recent task status and recorded actions. The journal does not automatically replay clicks, typing, PowerShell commands, or file writes after interruption. Review the computer's current state before continuing a task. See [Task Recovery](docs/TASK_RECOVERY.md).

## Workspace

NEXUS supports selecting a working directory for project-related tasks.

Example:

```text
/workspace C:\Users\You\Desktop\MyProject
```

The selected directory must already exist.

The workspace remains active for the current process only. Task checkpoints preserve the workspace path for review.

If no workspace is selected, the dedicated text-file writer uses the Windows Desktop by default.

The text-file writer creates new files without overwriting existing ones.

## Vision and Desktop Information

Vision is disabled by default.

When enabled, screenshots may be sent to the selected cloud provider if the selected model supports image input.

Screenshots can contain private information. Close sensitive applications and documents before enabling vision.

NEXUS can also retrieve Windows desktop metadata, including screen dimensions and foreground-window information.

## Security and Privacy

- Keep API keys inside `.env`.
- Never commit `.env` to GitHub.
- Do not run NEXUS as Administrator without a clear reason.
- Review PowerShell commands before relying on their results.
- Potentially destructive operations use heuristic safety checks and local confirmation.
- These checks are not a sandbox or a complete security boundary.
- Screenshots are shared with the cloud provider only when vision is enabled and the selected model supports image input.
- Conversation history and workspace state are held in process memory.
- Restarting NEXUS starts a new session.

NEXUS operates with the permissions of the current Windows account.

## Known Limitations

- AI model capabilities vary between providers.
- Tool-calling compatibility is not guaranteed for every model.
- Vision requires a compatible image-input model.
- Safety checks are heuristic.
- Session history is not persistent between restarts.
- Provider rate limits can interrupt requests.
- Computer operations should be reviewed and verified.

## Project Structure

```text
nexus/
├── .env.example
├── .gitattributes
├── .gitignore
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── GITHUB_RELEASE_CHECKLIST.md
├── README.md
├── README.pt-BR.md
├── ROADMAP.md
├── SECURITY.md
├── VERSION
├── agent.py
├── catalog.py
├── config.py
├── i18n.py
├── iniciar.py
├── main.py
├── requirements.txt
├── run_nexus.bat
├── safety.py
├── text_utils.py
└── tools.py
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned improvements and future development.

## License

No license has been selected yet.

Until a license is added, the default copyright rules apply. Public repository visibility does not automatically grant permission to reuse, modify, or redistribute this project.

---

**NEXUS 1.0**

Built with Python and cloud AI.
