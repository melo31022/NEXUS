# Contributing to NEXUS

## Branch policy

- `main` is the stable/release line. Do not push development changes directly to it.
- Active NEXUS 1.1 development happens on `dev-1.1`.
- Open pull requests against `dev-1.1` unless the maintainer explicitly requests another target.

## Development environment

Use Python 3.11 or newer. Windows x64 and Windows ARM64 are supported targets. Keep dependencies compatible with ARM64 and avoid requiring local model inference; NEXUS uses cloud providers.

## Before submitting

From the repository root, run:

```cmd
py -3.11 -m unittest discover -s tests -v
py -3.11 -m compileall -q .
```

Also check the GitHub Actions matrix on Ubuntu, Windows x64 and Windows ARM64. CI unit tests must use mocked provider responses; do not require API keys or make billable live calls in automated tests.

## Safety and privacy

- Never add API keys, .env files, private screenshots, logs or task journals.
- Keep desktop automation tests mocked; do not click destructive UI controls in CI.
- ModelTest tool probes are fictitious and must never be executed.
- Any screenshot transmission must require explicit user consent.
- Update README files, ROADMAP, CHANGELOG and relevant docs when behavior or commands change.
- Do not mark a feature complete until tests support the claim.
