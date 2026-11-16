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
    def test_chat_json_planner_context_and_multiple_tool_calls(self, post, _retry):
        post.side_effect = [
            FakeResponse({"choices": [{"message": {"content": "NEXUS_OK"}}]}),
            FakeResponse({"choices": [{"message": {"content": '{"ok": true}'}}]}),
            FakeResponse({"choices": [{"message": {"content": "STEP-1: a\nSTEP-2: b\nSTEP-3: c"}}]}),
            FakeResponse({"choices": [{"message": {"content": "entendido"}}]}),
            FakeResponse({"choices": [{"message": {"content": "NEXUS-7319-ORBIT"}}]}),
            FakeResponse({"choices": [{"message": {"tool_calls": [
                {"function": {"name": "nexus_modeltest_probe_a", "arguments": '{"value":"NEXUS_TEST"}'}},
                {"function": {"name": "nexus_modeltest_probe_b", "arguments": '{"value":"NEXUS_TEST"}'}}
            ]}}]}),
        ]
        results = run_model_test(self.provider, "test-model")
        self.assertEqual([item["status"] for item in results],
                         ["PASS", "PASS", "PASS", "PASS", "PASS", "SKIP"])
        self.assertEqual(post.call_count, 6)

    @patch("model_test.request_with_retry", side_effect=lambda request, retries: request())
    @patch("model_test.requests.post")
    def test_vision_sends_approved_image_as_image_url_part(self, post, _retry):
        self.provider.supports_vision = lambda model: True
        post.side_effect = [
            FakeResponse({"choices": [{"message": {"content": "NEXUS_OK"}}]}),
            FakeResponse({"choices": [{"message": {"content": '{"ok": true}'}}]}),
            FakeResponse({"choices": [{"message": {"content": "STEP-1: a\nSTEP-2: b\nSTEP-3: c"}}]}),
            FakeResponse({"choices": [{"message": {"content": "entendido"}}]}),
            FakeResponse({"choices": [{"message": {"content": "NEXUS-7319-ORBIT"}}]}),
            FakeResponse({"choices": [{"message": {"tool_calls": [
                {"function": {"name": "nexus_modeltest_probe_a", "arguments": "{}"}},
                {"function": {"name": "nexus_modeltest_probe_b", "arguments": "{}"}}
            ]}}]}),
            FakeResponse({"choices": [{"message": {"content": "A captura mostra uma janela de teste."}}]}),
        ]
        image = "data:image/jpeg;base64,ZmFrZQ=="
        results = run_model_test(self.provider, "vision-model", image_data_url=image)
        self.assertEqual(results[-1]["status"], "PASS")
        payload = post.call_args_list[-1].kwargs["json"]
        image_part = payload["messages"][0]["content"][1]
        self.assertEqual(image_part["type"], "image_url")
        self.assertEqual(image_part["image_url"]["url"], image)
        self.assertEqual(post.call_count, 7)

    @patch("model_test.request_with_retry", side_effect=lambda request, retries: request())
    @patch("model_test.requests.post")
    def test_probe_tools_are_only_inspected_and_never_executed(self, post, _retry):
        post.side_effect = [
            FakeResponse({"choices": [{"message": {"content": "ok"}}]}),
            FakeResponse({"choices": [{"message": {"content": '{"ok": true}'}}]}),
            FakeResponse({"choices": [{"message": {"content": "STEP-1: a\nSTEP-2: b\nSTEP-3: c"}}]}),
            FakeResponse({"choices": [{"message": {"content": "entendido"}}]}),
            FakeResponse({"choices": [{"message": {"content": "NEXUS-7319-ORBIT"}}]}),
            FakeResponse({"choices": [{"message": {"tool_calls": [
                {"function": {"name": "nexus_modeltest_probe_a", "arguments": "{}"}},
                {"function": {"name": "nexus_modeltest_probe_b", "arguments": "{}"}}
            ]}}]}),
        ]
        run_model_test(self.provider, "test-model")
        self.assertEqual(post.call_count, 6)


if __name__ == "__main__":
    unittest.main()
