# NEXUS 1.1 — Task checkpoints and recovery

Each Operator task receives a JSON journal under `nexus_tasks/`. Checkpoints are written atomically and include the goal, workspace, current step, action names, bounded results, and completion status.

Use `/tasks` to inspect recent task records. The journal is a recovery aid, not an execution replay engine.

NEXUS deliberately does **not** replay clicks, typing, file writes, application launches, or PowerShell commands after a crash. The computer may have changed after the last checkpoint, and blindly repeating a non-idempotent action could cause duplicate or destructive effects. Only read-only observation tools are marked retry-safe; review the current desktop and the saved task record before starting a continuation manually.

Credentials and common secret fields are redacted from persisted action arguments/results. Checkpoint files may still contain user task text and other operational metadata, so keep the `nexus_tasks/` directory private and do not upload it with bug reports.
