# Changelog

## 1.0.0 — 2026-11-15

### Added
- Automatic interface-language detection from Windows/user locale.
- Portuguese and English interface translations, plus `/language auto|pt|en`.
- Per-message language recognition guidance for cloud-model responses.
- First-run Windows bootstrap through `run_nexus.bat`: create a virtual environment, install dependencies, and initialize `.env`.
- Windows GitHub Actions workflow for unit tests.
- Dependabot configuration for Python dependencies and GitHub Actions.
- `SECURITY.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`.

### Improved
- Welcome screen and session status surface language, provider, model, vision, and workspace more clearly.
- `.gitignore` excludes local environment files, logs, screenshots, virtual environments, editor metadata, and caches while retaining `.env.example`.
- English and Brazilian Portuguese README documentation.
- First-run script checks for Python 3.11+ and pauses with an actionable message when setup fails.

### Preserved from the release candidates
- Cloud-only Ollama Cloud and Groq providers with fixed HTTPS endpoints.
- Dynamic model catalog and distinct provider, model, and operation-mode selection.
- Operator, Planner, and Chat modes.
- Workspace-aware `.txt` creation without overwriting existing files.
- Optional screenshot vision and measured Windows foreground-window/display metadata.
- Local confirmation for PowerShell commands classified as potentially destructive.

### Validation
- Python compilation checked.
- 12 unit tests passed in the development environment.
- Live provider authentication, tool calling, and interactive Windows desktop behavior still require acceptance testing on Windows.

## 1.0.0-rc3 — 2026-11-15
- Fixed terminal logo rendering and Ollama Cloud tool-call compatibility.
- Separated model selection (`/agent`) from operation mode (`/mode`).
- Added provider model-catalog parsing and removed generic/local provider endpoints.

## 1.0.0-rc2 — 2026-11-15
- Added the supplied NEXUS logo, initial model catalog lookup, Desktop text-file creation, and same-process conversation context.

## 1.0.0-rc1 — 2026-11-15
- Initial release candidate with Windows desktop tools, safety confirmations, optional screenshot vision, provider configuration, and tests.
