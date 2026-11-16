# NEXUS 1.0

<p align="center"><img src="assets/nexus_logo.png" alt="NEXUS" width="520"></p>

[Leia esta documentação em Português (Brasil)](README.pt-BR.md).

**NEXUS** is a Windows computer-use agent powered by cloud-hosted AI models. It can inspect the desktop, plan tasks, operate mouse and keyboard, run PowerShell commands, and verify results. Model inference is performed by the selected cloud provider; NEXUS does not run local language models.

> Interface language is detected automatically from the Windows/user locale. Portuguese (Brazil) and English are included. Change it at any time with `/language pt`, `/language en`, or `/language auto`.

## Highlights

- **Cloud providers:** Ollama Cloud and Groq Cloud, using fixed HTTPS API endpoints.
- **Dynamic model catalog:** query provider models with `/agents` and select with `/agent`.
- **Three modes:** `operator`, `planner`, and `chat`.
- **Desktop tools:** mouse, keyboard, screenshots, window listing, application launching, and PowerShell.
- **Optional vision:** screenshots are sent to the selected provider only when `/vision on` is enabled and the selected model is configured for image input.
- **Workspace awareness:** keep project files in a selected workspace during the current session.
- **Windows metadata:** screen dimensions and foreground-window information are measured separately from model visual interpretation.
- **Safety checks:** potentially destructive PowerShell commands require local confirmation. These checks are heuristic, not a sandbox.

## Requirements

- Windows 10 or Windows 11 with an interactive user session.
- Python 3.11 or newer.
- Internet connection and an API key for the selected provider.

## Quick start

1. Download and extract the project.
2. Open the extracted `nexus` folder.
3. Double-click **`run_nexus.bat`**.
4. On first launch, the script creates a virtual environment, installs dependencies, and creates `.env` from `.env.example`.
5. Open `.env`, add the API key for your provider, save, and launch `run_nexus.bat` again.

The first installation needs an internet connection and may take a few minutes. Later launches reuse the virtual environment and do not reinstall dependencies unless you remove `.venv`.

### Manual setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe main.py
```

## Provider configuration

Edit `.env`. Never commit this file or share its contents.

### Ollama Cloud

```dotenv
NEXUS_PROVIDER=ollama
OLLAMA_API_KEY=your_ollama_api_key
OLLAMA_MODEL=beam
```

### Groq Cloud

```dotenv
NEXUS_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

The model catalog depends on provider availability and account access. A model appearing in `/agents` does not guarantee tool-calling or image-input support.

## Language

`NEXUS_LANGUAGE=auto` detects the operating-system locale. You can set `NEXUS_LANGUAGE=pt` or `NEXUS_LANGUAGE=en` in `.env`, or change the language for the current run with:

```text
/language auto
/language pt
/language en
```

The selected language is used as the interface preference. The agent also detects the language of each user message and normally replies in that same language; an explicit language request takes priority. The application currently ships with Portuguese and English translations.

## Commands

| Command | Description |
|---|---|
| `/providers` | List supported cloud providers. |
| `/provider ollama` or `/provider groq` | Select a provider. |
| `/agents` or `/models` | Fetch the provider's model catalog. |
| `/agent <number\|id>` | Select a model. |
| `/modes` | List NEXUS operation modes. |
| `/mode operator` | Enable computer-use tools. |
| `/mode planner` | Plan without executing tools. |
| `/mode chat` | Chat without computer tools. |
| `/language auto\|pt\|en` | Detect or change the interface and response language. |
| `/vision on` / `/vision off` | Enable or disable screenshot sharing with the cloud model. |
| `/workspace` | Show the current workspace. |
| `/workspace <folder>` | Set an existing folder as the session workspace. |
| `/workspace off` | Return `.txt` creation to the Desktop default. |
| `/status` | Show current configuration. |
| `/init` | Create a starter `NEXUS.md` without overwriting an existing file. |
| `/help` | Show command help. |
| `/clear` | Clear the terminal and redraw the welcome screen. |
| `/exit` | Exit NEXUS. |

## Workspace behavior

Set a folder with `/workspace C:\Users\You\Desktop\MyProject`. The folder must already exist. During a task, the agent may also set the workspace after creating or identifying the project root. The workspace remains active for the current process only. If none is set, the dedicated `.txt` writer uses the Windows Desktop. It accepts a filename rather than an arbitrary path and creates files exclusively, refusing to overwrite existing files.

## Vision and Windows metadata

Vision is off by default. With `/vision on`, a screenshot requested by the agent is saved locally and sent to the configured provider only if the selected model is configured as image-capable. Screenshots may contain private information; close sensitive pages and documents before enabling this feature.

The `get_active_window` tool queries the Windows foreground window, title, process ID, and rectangle. `get_screen_info` returns measured display dimensions and foreground-window metadata. The model still interprets the screenshot pixels; Windows metadata is provided as separate measured context.

Beam is a text model and should not be used for image analysis. Verify image-input and tool-calling support with the provider before selecting a model for Operator mode.

## Security and privacy

- Keep API keys in `.env`. The repository ignores `.env`, logs, screenshots, virtual environments, and Python cache files.
- NEXUS runs with the permissions of the current Windows account. Do not run it as Administrator without a clear need.
- PyAutoGUI fail-safe is enabled; moving the pointer to the top-left corner interrupts PyAutoGUI actions.
- Potentially destructive PowerShell commands require local confirmation, but pattern checks are heuristic and are not a security boundary or sandbox.
- Screenshots are sent to the cloud provider only when vision is enabled and the model is configured for image input.
- Conversation history and workspace are held in process memory. Restarting NEXUS starts a new session.
- Review commands and outputs before relying on them. A tool call alone is not proof that an action succeeded.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

GitHub Actions also runs the unit suite on Windows with Python 3.11. Automated unit tests do not replace acceptance testing with real provider credentials, tool calls, and an interactive Windows desktop.

## Project structure

```text
nexus/
├── agent.py
├── catalog.py
├── config.py
├── i18n.py
├── main.py
├── tools.py
├── safety.py
├── text_utils.py
├── assets/nexus_logo.png
├── tests/test_core.py
├── .github/workflows/tests.yml
├── .env.example
├── run_nexus.bat
├── requirements.txt
├── SECURITY.md
├── CONTRIBUTING.md
└── VERSION
```

## License

No license has been selected yet. Until a license is added, the default copyright rules apply; public visibility alone does not grant permission to reuse or redistribute the code. Choose and add a license before describing the project as open source.
