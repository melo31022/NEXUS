# Security Policy

## Protect credentials and private data

- Never commit .env files, API keys, passwords, access tokens, private screenshots, task journals or runtime logs.
- Prefer /setup and /key set on Windows. NEXUS stores saved provider keys encrypted for the current Windows user with DPAPI.
- If a key is exposed, revoke/rotate it at the provider. Deleting the local file alone does not invalidate a leaked key.
- Do not paste credentials into GitHub issues, pull requests, chat logs or screenshots.
- Desktop screenshots are sent to a cloud provider only after an explicit user confirmation in ModelTest. Review the visible desktop before approving.
- File reading is scoped to the active workspace/project directory and blocks common credential-file names, but users should still avoid selecting directories containing private data.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature on the repository's Security tab if it is enabled. If it is unavailable, open a minimal issue without exploit details, credentials or personal data and ask the maintainer for a private reporting channel.

## Scope

NEXUS can control a Windows desktop. Review commands before approving destructive operations, do not run it with elevated privileges unless required, and test automation on non-sensitive files and applications first.
