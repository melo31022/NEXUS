# Testing and acceptance

## Automated CI

The GitHub Actions workflow runs the unit-test suite and Python compilation on:

- Ubuntu x64
- Windows x64
- Windows ARM64 (windows-11-arm)

Windows jobs also install the full desktop dependency set and run mocked tests for text-file access, window-title aliases and cursor-position reporting. These jobs do not perform real clicks, type into applications or verify live API credentials.

## Local unit tests (CMD)

From the NEXUS project directory:

```cmd
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m compileall -q .
```

## Windows desktop acceptance

Run these checks on the target Windows installation, including Windows ARM64:

1. Start NEXUS with py -3.11 iniciar.py.
2. Run /test for the selected provider/model.
3. Run /modeltest; confirm the API-call prompt. Approve screenshot sharing only after closing private windows.
4. In Operator mode, use list_directory and read_text_file on a non-sensitive test folder.
5. Verify read_text_file rejects paths outside the active workspace and blocks common credential-file names.
6. Open Notepad, type harmless test text, and verify the active window.
7. Test mouse movement and clicks only on a harmless target.
8. Interrupt a harmless multi-step task, inspect it with /tasks, and use /resume <id>. Verify the new run inspects state before taking further action.

## Live provider matrix

For each configured provider/model, record:

- Provider authentication and model catalog result
- Chat response and latency
- JSON mode support
- Tool-call emission (the ModelTest probe is never executed)
- Vision result, only after explicit screenshot consent
- Rate-limit and error handling

A capability is not marked fully compatible just because a model appears in a catalog. Keep live-account results separate from mocked unit tests.

## Release gate

Do not mark NEXUS 1.1 as stable until automated CI is green, Windows desktop acceptance is complete, and provider/model limitations are documented. Never put API keys, private screenshots or runtime logs into test fixtures or commits.