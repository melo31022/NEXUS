"""Crash-safe task journal. It records progress but never replays uncertain desktop actions."""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SAFE_TO_RETRY = {"get_active_window", "get_screen_info", "list_windows", "screenshot"}


class TaskJournal:
    def __init__(self, goal: str, workspace: str | None = None, root: Path | None = None, parent_task_id: str | None = None) -> None:
        self.root = root or Path(__file__).resolve().parent / "nexus_tasks"
        self.root.mkdir(parents=True, exist_ok=True)
        self.task_id = uuid.uuid4().hex
        self.path = self.root / f"{self.task_id}.json"
        self.state: dict[str, Any] = {
            "schema": 1, "task_id": self.task_id, "goal": str(goal)[:4000],
            "workspace": workspace, "status": "running", "created_at": self._now(),
            "updated_at": self._now(), "step": 0, "actions": [],
            "recovery_policy": "manual_review_only",
        }
        if parent_task_id:
            self.state["resumed_from"] = str(parent_task_id)[:64]
        self.save()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def save(self) -> None:
        self.state["updated_at"] = self._now()
        temporary = self.path.with_suffix(".tmp")
        data = json.dumps(self.state, ensure_ascii=False, indent=2)
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(self.path)

    def set_workspace(self, workspace: str | None) -> None:
        self.state["workspace"] = workspace
        self.save()

    def begin_step(self, step: int) -> None:
        self.state["step"] = int(step)
        self.state["status"] = "running"
        self.save()

    def record_action(self, name: str, arguments: dict[str, Any], result: str, *, success: bool) -> None:
        if name in {"type_text", "write_text_file", "read_text_file", "powershell_execute", "screenshot"}:
            safe_args = {"fields": sorted(str(key)[:80] for key in arguments), "values_omitted": True}
        else:
            safe_args = redact_sensitive_dict(arguments)
        if name in {"type_text", "write_text_file", "read_text_file", "powershell_execute", "screenshot"}:
            safe_result = f"[output omitted; {len(str(result))} chars]"
        else:
            safe_result = redact_sensitive_text(str(result))[:1500]
        self.state["actions"].append({
            "name": str(name)[:100], "arguments": safe_args,
            "result": safe_result, "success": bool(success),
            "retry_safe": name in SAFE_TO_RETRY, "completed_at": self._now(),
        })
        self.save()

    def finish(self, status: str = "completed", note: str = "") -> None:
        self.state["status"] = status if status in {"completed", "interrupted", "failed", "step_limit"} else "failed"
        self.state["note"] = str(note)[:1000]
        self.save()

    @classmethod
    def recent(cls, root: Path | None = None, limit: int = 10) -> list[dict[str, Any]]:
        directory = root or Path(__file__).resolve().parent / "nexus_tasks"
        if not directory.is_dir():
            return []
        found: list[dict[str, Any]] = []
        for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                item = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(item, dict):
                    item["file"] = path.name
                    found.append(item)
            except (OSError, ValueError):
                continue
            if len(found) >= max(1, min(int(limit), 50)):
                break
        return found


def redact_sensitive_text(value: str) -> str:
    text = str(value)
    text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]+=*", r"\1[redacted]", text)
    text = re.sub(r"""(?i)(["']?(?:api[_ -]?key|token|password|secret)["']?\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[^\s,;}]+)""", r"\1[redacted]", text)
    return re.sub(r"(?i)\b(?:gsk_|sk-or-v1-|sk-)[A-Za-z0-9_-]{20,}", "[redacted]", text)


def redact_sensitive_dict(value: Any) -> Any:
    """Recursively redact secret-bearing keys and token-like values before journaling."""
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            name = str(key)
            if re.search(r"(?i)(?:api[_ -]?key|token|password|secret|credential|authorization|text|content|command)", name):
                cleaned[name] = f"[redacted; {len(str(item))} chars]"
            else:
                cleaned[name] = redact_sensitive_dict(item)
        return cleaned
    if isinstance(value, list):
        return [redact_sensitive_dict(item) for item in value]
    if isinstance(value, str):
        return redact_sensitive_text(value)
    return value


def resumable_actions(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only read-only operations eligible for an explicit user-reviewed retry."""
    return [a for a in state.get("actions", []) if a.get("retry_safe") and not a.get("success")]
