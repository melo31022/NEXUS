# Changelog

## Unreleased — NEXUS 1.1 development

- Added `/modeltest` for live, non-destructive checks of chat, JSON mode, Planner output, short-context retention, and multiple tool-call emission.
- Tool-call tests inspect model output but never execute the probe tool.
- Vision testing requires separate consent before a desktop screenshot is sent to the provider.
- Added explicit operational context for provider, model, mode, workspace and a bounded filename snapshot.
- Fixed secret-redaction regular expressions in task recovery and directory-listing line separators.
- Added regression tests for ModelTest behavior and secret redaction.
- Added workspace-scoped text-file reading with common credential-file protections.
- Added `/resume <id>` as a user-confirmed continuation linked to the prior journal; no desktop actions are replayed automatically.
- Strengthened Token Guard compaction for oversized recent turns, enforced the configured context budget, and displayed provider-reported token usage when available.
- Added GitHub Actions coverage for Ubuntu, Windows x64 and Windows ARM64.
- Redacted sensitive values from text-file reads and PowerShell output; omitted private tool arguments/results from logs and task journals.
- Added SECURITY.md, CONTRIBUTING.md and GitHub issue templates.
- Updated DeepSeek to the current base URL and `deepseek-flash` model, enabled its documented vision capability, and preserved provider reasoning fields across tool-call turns.

# Changelog

## 1.1.0 — 2026-11-16

### Added
- Interactive CMD provider setup with hidden API-key entry, endpoint/model configuration, and /test connection verification.
- Windows DPAPI-encrypted per-user settings storage; .env remains supported for backward compatibility.
- /key status|set|remove and /endpoint commands for provider credential and endpoint management.
- Lightweight Token Guard with heuristic token estimation, conversation compaction, configurable context/output budgets, and tool-call limits.
- Persistent task journals with atomic checkpoints, progress/action records, workspace persistence, credential redaction, and the `/tasks` command.
- Expanded desktop controls: right-click, double-click, bounded scrolling, and window activation by title.
- Bounded transient-request retries with `Retry-After` support and sanitized HTTP error details.
- Additional cloud provider configurations: OpenRouter, Cerebras, Together AI, and DeepSeek, alongside Groq Cloud and Ollama Cloud.
- Provider and task-recovery documentation.
- Regression tests for token budgeting, checkpoint persistence/redaction, and provider retry behavior.
- GitHub Actions workflow for unit tests and Python compilation.

### Improved
- Provider API-key environment variables are configured per provider.
- Task checkpoint arguments/results redact common credential fields.
- Terminal status, command help, and version branding updated to 1.1.

### Validation status
- 22 automated unit tests passed in GitHub Actions on Ubuntu with Python 3.11.
- Python `compileall` passed.
- CMD credential setup is implemented but DPAPI storage has not yet been manually validated on Windows 10/11 ARM64.
- Live provider authentication, model catalogs, tool calling, and vision remain provider/model-specific acceptance tests.
- Windows desktop automation and screenshots require manual validation on Windows.

### Known limitations
- Token counts are heuristic estimates, not exact provider tokenization.
- Task recovery records state but intentionally does not automatically replay desktop actions or file-changing operations.
- Additional providers use OpenAI-compatible conventions where applicable; feature parity is not guaranteed.
- A complete GUI redesign is not included in this release line.

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
