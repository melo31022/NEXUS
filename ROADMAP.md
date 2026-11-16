# NEXUS — Development Roadmap

This roadmap distinguishes implemented work from items that still require development or acceptance testing. Checkboxes describe the current code state, not a guarantee that every provider or Windows environment has been validated.

## Current development version: 1.1.0

### Version 1.0.0 — Initial foundation

- [x] Python application architecture for Windows.
- [x] Groq Cloud and Ollama Cloud integrations.
- [x] Dynamic model catalog.
- [x] Chat, Planner, and Operator modes.
- [x] PowerShell and workspace-aware file tools.
- [x] Screenshot capture and optional vision configuration.
- [x] Initial desktop metadata and heuristic safety checks.
- [x] Portuguese and English interface.
- [x] Windows launcher and virtual-environment setup.

## Version 1.1.0 — Reliability, Provider Expansion, and Computer Use

### ModelTest

- [x] Add `/modeltest` for live chat, JSON, short-context and tool-call emission checks.
- [x] Inspect tool-call requests without executing them.
- [x] Require separate user consent before sending a desktop screenshot for vision testing.
- [ ] Validate every provider/model combination with live accounts and record results.

### 1. Token Guard

- [x] Estimate prompt/context size before requests using a conservative heuristic.
- [x] Compact older conversation turns while retaining system instructions and recent context.
- [x] Configure context and output budgets.
- [x] Limit tool calls and execution steps.
- [x] Apply bounded retries for selected transient HTTP failures and honor `Retry-After`.
- [ ] Use exact provider tokenizers where available.
- [ ] Surface token estimates and usage feedback in the interface.
- [ ] Further optimize oversized tool outputs and logs.

### 2. Task Recovery

- [x] Persist task journals and atomic checkpoints.
- [x] Record task progress, action outcomes, and workspace path.
- [x] Redact common credential-like values from recorded action data.
- [x] Provide the `/tasks` command to inspect recent records.
- [x] Avoid automatically replaying uncertain desktop or file-changing actions.
- [ ] Add explicit user-reviewed continuation workflow.
- [ ] Improve task summaries and completed/pending action reporting.

### 3. Computer Use

- [x] Retain mouse movement, keyboard typing, and keyboard shortcuts.
- [x] Support left/right click and double-click.
- [x] Add bounded scrolling.
- [x] Add window activation by title.
- [x] Expose desktop controls to the Operator tool loop.
- [ ] Verify action results using post-action observation.
- [ ] Improve interruption controls and active-window handling.
- [ ] Complete Windows 10/11 and Windows ARM64 acceptance testing.

### 4. Vision

- [x] Retain screenshot capture and optional image submission.
- [x] Gate image submission through provider/model compatibility configuration.
- [ ] Improve visual grounding and screenshot-based action verification.
- [ ] Validate image-input behavior for each supported provider/model combination.

### 5. Multi-Provider Support and Compatibility

- [x] Add configuration for Groq Cloud and Ollama Cloud.
- [x] Add OpenRouter, Cerebras, Together AI, and DeepSeek configurations.
- [x] Centralize provider request/retry handling.
- [x] Document provider settings and known compatibility differences.
- [ ] Verify live authentication and model catalogs for every provider.
- [ ] Verify tool calling in Chat/Planner/Operator-compatible model combinations.
- [ ] Verify provider-specific vision support and error cases.
- [ ] Expand integration tests against live provider APIs where practical.

### 6. Security and Stability

- [x] Bound transient request retries.
- [x] Sanitize provider error details.
- [x] Redact common secrets in task journal data.
- [x] Keep task recovery conservative for uncertain actions.
- [ ] Expand destructive-operation validation and confirmation coverage.
- [ ] Add broader tests for malformed provider responses and failure paths.
- [ ] Validate behavior under Windows-specific errors and interruptions.

### 7. Interface and Documentation

- [x] Update version branding and command help.
- [x] Document supported providers and task recovery.
- [x] Maintain English and Brazilian Portuguese README files.
- [ ] Further refine terminal presentation and progress reporting.
- [ ] Add clearer runtime token and task progress feedback.

### 8. Testing and Release Readiness

- [x] Add automated reliability regression tests.
- [x] Run unit tests in GitHub Actions on Ubuntu/Python 3.11.
- [x] Run Python compilation checks in CI.
- [ ] Test on Windows 10/11, including ARM64.
- [ ] Test live provider authentication, catalogs, tool calls, and vision.
- [ ] Complete end-to-end multi-step task acceptance testing.
- [ ] Review all remaining limitations before a stable release.


### 9. CMD Configuration and Credential Management

- [x] Add an interactive provider setup wizard for API key, HTTPS endpoint, and model.
- [x] Add hidden-input commands to add/remove API keys without displaying them.
- [x] Encrypt saved provider settings for the current Windows user with DPAPI.
- [x] Add endpoint inspection/update and a short connection/authentication test.
- [ ] Validate DPAPI storage and recovery behavior on Windows 10/11 ARM64.
- [ ] Test setup, key rotation/removal, and provider switching with each live provider.
- [ ] Add an explicit migration flow for users who want to move existing .env keys into encrypted storage.

## Known 1.1.0 limitations

- Token accounting is heuristic and may differ from provider-reported usage.
- Additional providers use compatible API conventions where possible; feature parity is not guaranteed.
- Task journals record state but do not automatically replay desktop actions.
- A model being listed does not guarantee tool-calling or vision support.
- CI on Ubuntu does not establish Windows or Windows ARM64 compatibility.

## Future Versions

Potential work beyond 1.1.0:

- Persistent conversation memory across sessions.
- Configurable automation profiles.
- A more advanced graphical interface.
- Plugin and extension architecture.
- More sophisticated planning and workflow automation.

## Development Principles

1. Reliability over unnecessary complexity.
2. Efficient cloud token usage.
3. Provider-independent architecture where practical.
4. User control and transparency.
5. Safe, observable computer interaction.
6. Lightweight operation on Windows.
7. Modular code and automated testing.
