import tempfile
import copy
from unittest.mock import patch
import unittest
from pathlib import Path

import requests

import config
from providers import request_with_retry, sanitized_api_error
from task_recovery import TaskJournal, resumable_actions, redact_sensitive_text, redact_sensitive_dict
from token_guard import compact_messages, estimate_messages_tokens


class TokenGuardTests(unittest.TestCase):
    def test_estimates_and_preserves_recent_context(self):
        messages = [{"role": "system", "content": "rules"}]
        messages += [{"role": "user", "content": f"old message {i} " + ("x" * 300)} for i in range(10)]
        messages += [{"role": "user", "content": "latest request"}]
        compacted, estimate, changed = compact_messages(messages, budget=500, preserve_recent=3)
        self.assertTrue(changed)
        self.assertLess(estimate, estimate_messages_tokens(messages))
        self.assertEqual(compacted[0]["role"], "system")
        self.assertIn("latest request", str(compacted[-1]["content"]))

    def test_oversized_recent_window_compacts_tool_output_and_keeps_latest_request(self):
        messages = [
            {"role": "system", "content": "rules"},
            {"role": "user", "content": "latest request must remain visible"},
            {"role": "assistant", "tool_calls": [{"id": "call-1", "type": "function"}]},
            {"role": "tool", "tool_call_id": "call-1", "name": "list_directory", "content": "b" * 5000},
            {"role": "assistant", "content": "a" * 2500},
        ]
        compacted, estimate, changed = compact_messages(messages, budget=450, preserve_recent=12)
        self.assertTrue(changed)
        self.assertLess(estimate, estimate_messages_tokens(messages))
        self.assertIn("latest request must remain visible", str(compacted))
        self.assertTrue(any("[resultado compactado" in str(item.get("content", "")) for item in compacted))

    def test_small_context_is_unchanged(self):
        messages = [{"role": "system", "content": "rules"}, {"role": "user", "content": "hello"}]
        result, _, changed = compact_messages(messages, budget=1000)
        self.assertFalse(changed)
        self.assertEqual(result, messages)


class TaskRecoveryTests(unittest.TestCase):
    def test_recursive_argument_redaction_handles_nested_credentials(self):
        cleaned = redact_sensitive_dict({
            "options": {"OPENROUTER_API_KEY": "sk-or-v1-012345678901234567890123"},
            "note": "Bearer gsk_012345678901234567890123456789",
        })
        self.assertNotIn("sk-or-v1-012345678901234567890123", str(cleaned))
        self.assertNotIn("gsk_012345678901234567890123456789", str(cleaned))
        self.assertIn("[redacted", str(cleaned))

    def test_journal_omits_sensitive_tool_argument_values(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = TaskJournal("privacy test", root=Path(temp))
            journal.record_action(
                "write_text_file",
                {"path": "C:/private/notes.txt", "text": "private note body"},
                "Arquivo salvo em C:/private/notes.txt",
                success=True,
            )
            action = journal.state["actions"][-1]
            self.assertNotIn("private note body", str(action))
            self.assertNotIn("C:/private/notes.txt", str(action))
            self.assertTrue(action["arguments"]["values_omitted"])

    def test_resumed_journal_links_to_parent_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = TaskJournal("resume task", root=Path(temp), parent_task_id="parent-task-123")
            self.assertEqual(journal.state["resumed_from"], "parent-task-123")
            records = TaskJournal.recent(Path(temp))
            self.assertEqual(records[0]["resumed_from"], "parent-task-123")

    def test_checkpoint_persists_and_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = TaskJournal("test task", root=Path(temp))
            journal.begin_step(2)
            journal.record_action("powershell_execute", {"command": "echo secret"}, "api_key=abc123", success=False)
            journal.finish("interrupted")
            records = TaskJournal.recent(Path(temp))
            self.assertEqual(records[0]["status"], "interrupted")
            self.assertIn("[output omitted", records[0]["actions"][0]["result"])
            self.assertNotIn("abc123", str(records[0]["actions"][0]))
            self.assertEqual(len(resumable_actions(records[0])), 0)

    def test_sensitive_text_redaction_handles_bearer_and_key_patterns(self):
        value = redact_sensitive_text("Authorization: Bearer abc123 api_key=secret456")
        value += redact_sensitive_text('{"OPENROUTER_API_KEY": "sk-or-v1-012345678901234567890123"}')
        self.assertNotIn("abc123", value)
        self.assertNotIn("secret456", value)
        self.assertIn("[redacted]", value)
        self.assertNotIn("sk-or-v1-012345678901234567890123", value)

    def test_only_read_only_operations_are_retry_safe(self):
        with tempfile.TemporaryDirectory() as temp:
            journal = TaskJournal("read test", root=Path(temp))
            journal.record_action("get_screen_info", {}, "{}", success=False)
            journal.record_action("left_click", {"x": 10, "y": 10}, "clicked", success=False)
            record = TaskJournal.recent(Path(temp))[0]
            self.assertEqual([a["name"] for a in resumable_actions(record)], ["get_screen_info"])



class ProviderSettingsTests(unittest.TestCase):
    def test_provider_key_model_and_endpoint_can_be_saved(self):
        original_providers = config.PROVIDERS.copy()
        original_settings = copy.deepcopy(config._SAVED_SETTINGS)
        try:
            with patch("config.save_secure_settings") as save:
                updated = config.save_provider_settings(
                    "groq",
                    api_key="test-secret-value",
                    model="openai/gpt-oss-120b",
                    base_url="https://api.groq.com/openai/v1",
                )
                self.assertEqual(updated.api_key, "test-secret-value")
                self.assertEqual(updated.default_model, "openai/gpt-oss-120b")
                self.assertEqual(updated.normalized_base_url(), "https://api.groq.com/openai/v1")
                save.assert_called_once()
        finally:
            config.PROVIDERS.clear()
            config.PROVIDERS.update(original_providers)
            config._SAVED_SETTINGS.clear()
            config._SAVED_SETTINGS.update(original_settings)

    def test_insecure_endpoint_is_rejected(self):
        with patch("config.save_secure_settings") as save:
            with self.assertRaises(ValueError):
                config.save_provider_settings("groq", base_url="http://example.invalid/v1")
            save.assert_not_called()

class ProviderRetryTests(unittest.TestCase):
    def test_retry_after_header_is_honored(self):
        first = requests.Response()
        first.status_code = 429
        first.headers["Retry-After"] = "2"
        second = requests.Response()
        second.status_code = 200
        responses = iter([first, second])
        delays = []
        result = request_with_retry(lambda: next(responses), sleep=delays.append)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(delays, [2.0])

    def test_non_transient_error_is_not_retried(self):
        response = requests.Response()
        response.status_code = 401
        calls = []
        result = request_with_retry(lambda: calls.append(1) or response, sleep=lambda _: None)
        self.assertEqual(result.status_code, 401)
        self.assertEqual(len(calls), 1)

    def test_api_error_redacts_credentials(self):
        detail = sanitized_api_error(401, "api_key=secret123 bearer abc.def")
        self.assertNotIn("secret123", detail)
        self.assertNotIn("abc.def", detail)
        self.assertIn("[redacted]", detail)


if __name__ == "__main__":
    unittest.main()
