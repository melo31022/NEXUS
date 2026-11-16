# NEXUS — Roadmap

## NEXUS 1.0.0 — Initial Release

**Status:** Released

The first public release of NEXUS, establishing its initial architecture as a cloud-powered AI computer-use agent.

### Implemented Features

- Initial Groq Cloud and Ollama Cloud integrations.
- Chat, Planner and Operator modes.
- Windows tool execution.
- PowerShell integration.
- File management.
- Screenshot capture.
- Initial vision capabilities.
- Initial safety system.
- Provider and model configuration.

---

# NEXUS 1.1.0 — Reliability, Intelligence & Computer Use

**Status:** Planned

## Main Objective

Transform NEXUS into a more reliable, efficient, extensible and visually polished AI computer-use agent.

Version 1.1.0 will focus on intelligent token management, task recovery, desktop interaction, visual understanding, multi-provider support, interface improvements, security and stability.

## 1. Token Guard — Intelligent Token Management

- [ ] Estimate token usage before each request.
- [ ] Monitor context limits and tokens-per-minute limits.
- [ ] Implement automatic conversation history compaction.
- [ ] Preserve recent messages and important information.
- [ ] Preserve the current task objective and execution state.
- [ ] Set configurable output token limits.
- [ ] Limit execution steps and tool calls.
- [ ] Summarize large PowerShell outputs.
- [ ] Compact logs and oversized tool responses.
- [ ] Implement intelligent retries respecting Retry-After.
- [ ] Prevent unnecessary retry attempts.
- [ ] Display estimated token consumption.

**Expected Result:** Reduce context waste, provider limit errors and interruptions during long-running tasks.

## 2. Task Recovery — Task Continuity and Recovery

- [ ] Create execution checkpoints.
- [ ] Record completed operations.
- [ ] Record pending operations.
- [ ] Identify the stage at which a task was interrupted.
- [ ] Allow interrupted tasks to resume.
- [ ] Prevent unnecessary repetition of completed operations.
- [ ] Preserve the working directory.
- [ ] Restore the original task objective.
- [ ] Generate execution reports.
- [ ] Clearly communicate completed and remaining operations.

**Expected Result:** NEXUS should recover interrupted tasks after errors, API limits or execution interruptions without unnecessarily restarting the entire workflow.

## 3. Improved Computer Use — Desktop Interaction

- [ ] Implement reliable mouse movement.
- [ ] Implement mouse clicking.
- [ ] Implement keyboard typing.
- [ ] Implement keyboard shortcuts.
- [ ] Enable interaction with windows and applications.
- [ ] Integrate desktop interaction tools into Operator mode.
- [ ] Support multi-step interaction sequences.
- [ ] Verify whether actions were successfully executed.
- [ ] Implement task interruption controls.
- [ ] Prevent accidental repeated actions.
- [ ] Improve active window detection.

**Expected Result:** NEXUS should interact with Windows applications through mouse and keyboard, rather than relying exclusively on PowerShell commands.

## 4. Improved Vision — Visual Understanding

- [ ] Improve screenshot interpretation.
- [ ] Identify relevant visual elements.
- [ ] Combine visual information with Windows metadata.
- [ ] Identify the active window.
- [ ] Use screenshots to verify executed actions.
- [ ] Improve user interface understanding.
- [ ] Avoid decisions based on insufficient visual information.

**Expected Result:** NEXUS should better understand the desktop environment and use visual feedback to verify its actions.

## 5. Multi-Provider Support — Additional AI Providers

- [ ] Add support for AI providers beyond Groq Cloud and Ollama Cloud.
- [ ] Create a standardized provider integration architecture.
- [ ] Make adding new providers easier.
- [ ] Improve model discovery and selection.
- [ ] Support different API endpoints and request formats.
- [ ] Standardize provider responses and error handling.
- [ ] Improve provider switching.
- [ ] Test compatibility between providers, models and tools.
- [ ] Document all supported providers.

**Expected Result:** NEXUS should support multiple AI providers through an extensible architecture without requiring major changes to its core.

## 6. Provider Compatibility — Groq Cloud and Ollama Cloud

- [ ] Review the existing Groq integration.
- [ ] Review the existing Ollama Cloud integration.
- [ ] Improve compatibility with different models.
- [ ] Fix request and response handling issues.
- [ ] Improve HTTP error handling.
- [ ] Improve rate-limit handling.
- [ ] Ensure compatibility with Chat, Planner and Operator modes.
- [ ] Improve tool calling when supported by the model and provider.
- [ ] Detect provider and model incompatibilities.
- [ ] Improve provider-specific error messages.
- [ ] Add integration tests.

**Expected Result:** Groq Cloud and Ollama Cloud should operate consistently across supported models and NEXUS modes.

## 7. Interface & Visual Identity

- [ ] Redesign the overall NEXUS interface.
- [ ] Improve colors, spacing and visual organization.
- [ ] Standardize interface components.
- [ ] Improve message and log presentation.
- [ ] Refine the project's visual identity.
- [ ] Fix the ASCII logo displayed in CMD.
- [ ] Ensure logo compatibility with different terminals.
- [ ] Fix character encoding issues.
- [ ] Improve the startup presentation.
- [ ] Improve command-line usability.

**Expected Result:** NEXUS should have a more polished, consistent and readable interface, including a properly displayed terminal logo.

## 8. Security & Stability

- [ ] Improve destructive command detection.
- [ ] Improve confirmation mechanisms for potentially dangerous operations.
- [ ] Improve provider error handling.
- [ ] Prevent infinite tool execution loops.
- [ ] Improve session management.
- [ ] Improve error messages.
- [ ] Record important execution operations.
- [ ] Ensure users can interrupt running tasks.
- [ ] Prevent API key exposure in logs.
- [ ] Improve input and command validation.

**Expected Result:** Make task execution safer, more predictable and more resistant to failures.

## 9. Testing & Quality Assurance

- [ ] Create automated tests for Token Guard.
- [ ] Test task recovery after interruptions.
- [ ] Test mouse and keyboard interaction tools.
- [ ] Test screenshot interpretation.
- [ ] Test Groq Cloud compatibility.
- [ ] Test Ollama Cloud compatibility.
- [ ] Test additional provider integrations.
- [ ] Test HTTP 429 errors and connection failures.
- [ ] Test multi-step tasks.
- [ ] Test operations requiring user confirmation.
- [ ] Test integration between Chat, Planner and Operator.
- [ ] Update documentation and changelog.

**Expected Result:** Ensure that individual features and the complete system work reliably together.

---

## Development Order

1. Token Guard.
2. Task Recovery.
3. Provider Compatibility.
4. Multi-Provider Support.
5. Improved Computer Use.
6. Improved Vision.
7. Interface & Visual Identity.
8. Security & Stability.
9. Testing & Quality Assurance.
10. Final integration and release preparation.

---

## Release Requirements

NEXUS 1.1.0 will be considered ready when:

- Token management reliably handles context usage and provider limits.
- Interrupted tasks can be recovered without unnecessarily repeating completed operations.
- Operator can interact with mouse, keyboard and desktop applications.
- Vision can interpret the screen and help verify actions.
- Groq Cloud and Ollama Cloud integrations work consistently.
- Additional providers can be integrated through the standardized architecture.
- The interface and terminal logo display correctly.
- Security and stability improvements have been tested.
- Critical automated tests pass.
- Documentation and changelog are updated.

---

## Future Versions

The following features are reserved for future releases:

- Persistent memory across sessions.
- Plugin system.
- Automation profiles.
- More advanced graphical interface.
- More sophisticated autonomous planning.
- Complex workflow automation.
- Additional customization features.

---

## Development Principles

- Reliability over unnecessary complexity.
- Efficient token usage.
- Provider independence.
- User control and transparency.
- Safe computer interaction.
- Lightweight operation on Windows.
- Modular and maintainable architecture.
- Automated testing whenever practical.
