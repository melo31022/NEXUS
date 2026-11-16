# NEXUS 1.1 — Development progress

Last updated: 2026-11-16

## Branch and safety boundary

- Working branch: `dev-1.1`.
- Do not modify `main` during 1.1 development.
- Do not declare release readiness until CI and Windows acceptance tests pass.

## Implementation batch

- [x] Add `/modeltest` for live chat, JSON, Planner, short-context and multiple tool-call emission checks.
- [x] Inspect tool-call requests without executing them.
- [x] Require confirmation before API tests and separate consent before sending a screenshot.
- [x] Add provider/model/mode/workspace context and a bounded workspace filename snapshot to agent requests.
- [x] Fix sensitive-text redaction regex escaping and directory-listing line separators.
- [x] Add mocked regression tests for ModelTest and secret redaction.
- [x] Add bounded workspace-scoped text-file reading and omit file/PowerShell output from persistent logs.
- [x] Enable exact OpenRouter Nemotron 3.5 Super VL model IDs for opt-in vision.
- [x] Add `/resume <id>` with explicit confirmation, completed/uncertain action summary and linked follow-up journal.
- [x] Strengthen Token Guard for oversized recent turns, compact tool/assistant outputs, enforce the context budget and display provider usage when returned.
- [x] Configure CI matrix for Ubuntu, Windows x64 and Windows ARM64 runners.
- [x] Align DeepSeek endpoint/model defaults with its current API and preserve reasoning continuation fields for DeepSeek/OpenRouter.
- [ ] Confirm GitHub Actions results for the current CI matrix.
- [ ] Run manual acceptance tests on Windows 10/11 ARM64.
- [ ] Complete remaining Token Guard, Task Recovery, Computer Use, Vision, provider compatibility and documentation work.

## Verification rules

- Mocked tests do not prove live provider compatibility.
- Tool-call emission does not prove that every NEXUS desktop tool works.
- Vision is only considered tested when an approved screenshot is sent and the model returns a non-empty description.
- Linux CI does not prove Windows ARM64 compatibility.
- Never commit API keys, private screenshots, runtime logs or local task data.
