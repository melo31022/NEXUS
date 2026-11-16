# Checklist before publishing

- [ ] Choose a license (for example, MIT if you want broad reuse with attribution) and add the complete `LICENSE` file. Do not describe the project as open source until a license is present.
- [ ] Confirm `.env` is not present in the files being uploaded. Keep `.env.example` with empty values.
- [ ] Search the repository and Git history for API keys, tokens, passwords, private screenshots, and personal data. Revoke any credential that was accidentally exposed.
- [ ] Test `run_nexus.bat` on a clean Windows 10/11 account with Python 3.11+.
- [ ] Test Ollama Cloud and Groq Cloud using your own credentials; do not put credentials in screenshots or issue reports.
- [ ] Test Operator, Planner, Chat, language selection, workspace, screenshots, and confirmation prompts.
- [ ] In GitHub repository settings, enable Dependabot alerts, secret scanning, and push protection where available.
- [ ] Check the Actions tab after the first push and resolve any CI failures.
- [ ] Review the repository page, README images, links, release notes, and selected license.


## Windows startup fallback
- [ ] Verify `py -3.11 iniciar.py` from PowerShell as an alternative to the optional BAT launcher.
- [ ] Confirm first-run venv creation, dependency installation, `.env` creation, and subsequent launch.
