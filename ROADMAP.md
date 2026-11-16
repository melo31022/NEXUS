# NEXUS — Development Roadmap

This document describes the development direction of NEXUS.

The roadmap is subject to change as the project evolves.

## Current Version: 1.0

NEXUS 1.0 establishes the initial architecture for a Windows computer-use agent powered by cloud AI providers.

### Version 1.0 — Initial Release

- [x] Python-based application architecture.
- [x] Groq Cloud integration.
- [x] Ollama Cloud integration.
- [x] Dynamic provider model catalog.
- [x] Chat mode.
- [x] Planner mode.
- [x] Operator mode.
- [x] PowerShell integration.
- [x] Workspace selection.
- [x] Screenshot support.
- [x] Optional vision configuration.
- [x] Windows desktop metadata.
- [x] Basic heuristic safety checks.
- [x] Portuguese and English interface.
- [x] Initial GitHub documentation.
- [x] Python launcher and virtual environment setup.

## Version 1.1 — Reliability and Computer Control

The main objective of NEXUS 1.1 is to improve reliability, context management, and desktop interaction.

### 1. Token Guard

Improve token consumption and provider rate-limit handling.

- [ ] Estimate token usage before sending requests.
- [ ] Monitor provider token and request limits.
- [ ] Implement intelligent conversation compression.
- [ ] Preserve recent messages and important task state.
- [ ] Configure maximum output tokens.
- [ ] Limit tool calls and execution steps.
- [ ] Compress large PowerShell outputs.
- [ ] Reduce unnecessary context sent to providers.
- [ ] Respect Retry-After and provider retry instructions.
- [ ] Implement controlled retry handling for HTTP 429 errors.
- [ ] Display estimated token usage.

### 2. Task Recovery

Improve continuity when tasks are interrupted.

- [ ] Implement task checkpoints.
- [ ] Track completed and pending operations.
- [ ] Preserve task state during interruptions.
- [ ] Resume interrupted tasks when possible.
- [ ] Avoid repeating completed operations.
- [ ] Improve execution reports.
- [ ] Preserve workspace information during recovery.

### 3. Computer Use

Improve interaction with the Windows desktop.

- [ ] Reliable mouse movement.
- [ ] Left and right mouse clicks.
- [ ] Keyboard typing.
- [ ] Keyboard shortcuts.
- [ ] Multi-step desktop interaction.
- [ ] Improved Operator integration.
- [ ] Immediate task interruption.
- [ ] Verify actions after execution.
- [ ] Improve handling of active windows.

### 4. Improved Vision

Improve the agent's understanding of the desktop.

- [ ] Improve screenshot interpretation.
- [ ] Combine screenshots with Windows metadata.
- [ ] Improve active-window identification.
- [ ] Verify visual changes after operations.
- [ ] Improve compatibility with image-capable models.

### 5. Safety and Stability

Improve execution reliability and operational safety.

- [ ] Improve destructive-operation detection.
- [ ] Expand confirmation mechanisms.
- [ ] Improve provider error handling.
- [ ] Prevent excessive tool-call loops.
- [ ] Improve session management.
- [ ] Improve execution verification.
- [ ] Produce clearer failure reports.

## Future Versions

Potential improvements for versions beyond 1.1:

- [ ] Persistent conversation memory.
- [ ] Configurable automation profiles.
- [ ] Improved graphical interface.
- [ ] Expanded provider compatibility.
- [ ] Better task planning and execution.
- [ ] More robust application control.
- [ ] Plugin and extension architecture.
- [ ] Improved documentation and testing.

## Development Principles

NEXUS development prioritizes:

1. Reliability over unnecessary complexity.
2. Efficient cloud token usage.
3. Transparent task execution.
4. User control over computer operations.
5. Safety and clear confirmation.
6. Compatibility with lightweight Windows computers.
7. Provider-independent architecture.

## Contributing

Suggestions, bug reports, and contributions are welcome.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

---

**NEXUS Development Roadmap**
