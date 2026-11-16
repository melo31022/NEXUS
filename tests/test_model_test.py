import unittest
from types import SimpleNamespace
from unittest.mock import patch

from model_test import run_model_test


class FakeResponse:
    def __init__(self, payload, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._payload


class ModelTestTests(unittest.TestCase):
    def setUp(self):
        self.provider = SimpleNamespace(
            name="test", label="Test provider", api_key="test-key",
            normalized_base_url=lambda: "https://example.invalid/v1",
            supports_vision=lambda model: False,
        )

    @patch("model_test.request_with_retry", side_effect=lambda request, retries: request())
    @patch("model_test.requests.post")
    def test_chat_json_context_and_tool_call(self, post, _retry):
        post.side_effect = [
            FakeResponse({"choices": [{"message": {"content": "NEXUS_OK"}}]}),
            FakeResponse({"choices": [{"message": {"content": '{"ok": true}'}}]}),
            FakeResponse({"choices": [{"message": {"content": "entendido"}}]}),
            FakeResponse({"choices": [{"message": {"content": "NEXUS-7319-ORBIT"}}]}),
            FakeResponse({"choices": [{"message": {"tool_calls": [
                {"function": {"name": "nexus_modeltest_probe", "arguments": '{"value":"NEXUS_TEST"}'}}
            ]}}]}),
        ]
        results = run_model_test(self.provider, "test-model")
        self.assertEqual([item["status"] for item in results], ["PASS", "PASS", "PASS", "PASS", "SKIP"])
        self.assertEqual(post.call_count, 5)

    @patch("model_test.request_with_retry", side_effect=lambda request, retries: request())
    @patch("model_test.requests.post")
    def test_probe_tool_is_only_inspected_and_never_executed(self, post, _retry):
        post.side_effect = [
            FakeResponse({"choices": [{"message": {"content": "ok"}}]}),
            FakeResponse({"choices": [{"message": {"content": '{"ok": true}'}}]}),
            FakeResponse({"choices": [{"message": {"content": "entendido"}}]}),
            FakeResponse({"choices": [{"message": {"content": "NEXUS-7319-ORBIT"}}]}),
            FakeResponse({"choices": [{"message": {"tool_calls": [
                {"function": {"name": "nexus_modeltest_probe", "arguments": "{}"}}
            ]}}]}),
        ]
        run_model_test(self.provider, "test-model")
        self.assertEqual(post.call_count, 5)


if __name__ == "__main__":
    unittest.main()
