# NEXUS — Development Roadmap

This document describes the development direction of NEXUS.

The roadmap is subject to change as the project evolves.

## Current Version: 1.1.0

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

- [x] Estimate token usage before sending requests (conservative character-based estimate).
- [ ] Monitor provider token and request limits.
- [x] Implement bounded conversation compaction at user-turn boundaries.
- [x] Preserve system instructions and recent conversation turns.
- [x] Configure maximum output tokens.
- [x] Limit tool calls per step and retain the overall step cap.
- [ ] Compress large PowerShell outputs.
- [ ] Reduce unnecessary context sent to providers.
- [x] Respect Retry-After for transient HTTP errors.
- [x] Implement bounded retries for 429 and selected transient HTTP statuses.
- [ ] Display estimated token usage.

### 2. Task Recovery

Improve continuity when tasks are interrupted.

- [x] Implement persistent atomic task checkpoints.
- [x] Record action outcomes and step state.
- [x] Persist interrupted/failed task state.
- [ ] Add explicit, user-reviewed continuation of interrupted tasks (no automatic action replay).
- [ ] Avoid repeating completed operations.
- [ ] Improve execution reports.
- [ ] Preserve workspace information during recovery.

### 3. Computer Use

Improve interaction with the Windows desktop.

- [x] Reliable mouse movement with coordinate validation (existing implementation retained).
- [x] Left and right mouse clicks.
- [x] Keyboard typing (existing implementation retained).
- [x] Keyboard shortcuts (existing implementation retained).
- [x] Multi-step desktop interaction through the Operator tool loop.
- [x] Expanded Operator tools for right/double click, scrolling, and window activation.
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
- [x] Add bounded transient retries and sanitized error summaries.
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
