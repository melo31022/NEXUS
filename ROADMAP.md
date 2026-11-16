# NEXUS — Development Roadmap

This document tracks planned improvements and development goals for NEXUS.

## Version 1.0 — Initial Release

The first version establishes the core architecture of NEXUS.

- [x] Cloud AI integration
- [x] Groq Cloud support
- [x] Ollama Cloud support
- [x] Chat mode
- [x] Planner mode
- [x] Operator mode
- [x] PowerShell integration
- [x] File and workspace operations
- [x] Screenshot support
- [x] Basic safety checks
- [x] Portuguese and English interface

## Version 1.1 — Reliability and Computer Use

### 1. Token Guard
- [ ] Estimate token usage before requests.
- [ ] Monitor provider rate limits.
- [ ] Automatically summarize older conversation history.
- [ ] Preserve recent messages and important task state.
- [ ] Limit response token usage.
- [ ] Limit tool calls and execution steps.
- [ ] Compress long PowerShell outputs.
- [ ] Implement automatic retries for HTTP 429.
- [ ] Respect provider retry delays.

### 2. Task Recovery
- [ ] Save task checkpoints.
- [ ] Track completed and pending operations.
- [ ] Resume interrupted tasks.
- [ ] Avoid repeating completed operations.
- [ ] Preserve workspace and task context.
- [ ] Generate execution reports.

### 3. Computer Use
- [ ] Reliable mouse movement.
- [ ] Mouse clicks.
- [ ] Keyboard input and shortcuts.
- [ ] Multi-step visual interaction.
- [ ] Immediate task interruption.
- [ ] Verify actions after execution.
- [ ] Integrate computer interaction into Operator mode.

### 4. Improved Vision
- [ ] Better screenshot interpretation.
- [ ] Combine visual information with Windows metadata.
- [ ] Identify active windows and processes.
- [ ] Verify visual changes after actions.

### 5. Safety and Stability
- [ ] Improved confirmation system.
- [ ] Better error handling.
- [ ] Protection against excessive tool loops.
- [ ] More reliable execution reports.
- [ ] Improved session management.

## Long-term goals

NEXUS aims to become a lightweight, extensible AI computer-use agent for Windows, powered entirely by cloud-hosted models.

**Status:** Version 1.1 is planned and under development.
