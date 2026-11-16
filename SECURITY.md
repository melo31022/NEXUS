# Security Policy

## Reporting a vulnerability

Do not publish API keys, tokens, passwords, private screenshots, or personal data in an issue.

For a security concern, open a private vulnerability report through GitHub's **Security** tab when that feature is enabled for this repository. If private reporting is unavailable, contact the repository maintainer privately before disclosing details publicly.

## Safe use

- Keep provider API keys in `.env`; never commit that file.
- Enable GitHub secret scanning and push protection where available.
- Do not run NEXUS as Administrator unless strictly necessary.
- Review PowerShell commands before approving them. The built-in checks are heuristic and are not a security sandbox.
- Screenshots are sent to the selected cloud provider only when `/vision on` is enabled and a compatible model is selected.
