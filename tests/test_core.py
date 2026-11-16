import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalog import extract_model_ids  # noqa: E402
from config import PROVIDERS, get_provider  # noqa: E402
from safety import command_needs_confirmation  # noqa: E402
from text_utils import normalize_text_content  # noqa: E402
from i18n import detect_language, language_name, tr  # noqa: E402


class NexusCoreTests(unittest.TestCase):
    def test_only_cloud_providers_are_available(self):
        self.assertEqual(set(PROVIDERS), {"groq", "ollama", "openrouter", "cerebras", "together", "deepseek"})
        with self.assertRaises(ValueError):
            get_provider("remote")

    def test_provider_endpoints_are_hosted(self):
        self.assertEqual(PROVIDERS["ollama"].normalized_base_url(), "https://ollama.com/v1")
        self.assertEqual(PROVIDERS["groq"].normalized_base_url(), "https://api.groq.com/openai/v1")
        self.assertEqual(PROVIDERS["openrouter"].normalized_base_url(), "https://openrouter.ai/api/v1")
        self.assertEqual(PROVIDERS["cerebras"].normalized_base_url(), "https://api.cerebras.ai/v1")

    def test_read_only_command_does_not_require_confirmation(self):
        self.assertFalse(command_needs_confirmation("Get-ChildItem $HOME"))

    def test_format_list_is_read_only(self):
        self.assertFalse(command_needs_confirmation("Get-ChildItem -Path $HOME | Format-List Name, Length"))
        self.assertFalse(command_needs_confirmation("Get-ChildItem | Format-Table Name"))
        self.assertTrue(command_needs_confirmation("format C:"))

    def test_destructive_commands_require_confirmation(self):
        self.assertTrue(command_needs_confirmation("Remove-Item .\\temp -Recurse"))
        self.assertTrue(command_needs_confirmation("Restart-Computer"))
        self.assertTrue(command_needs_confirmation("Clear-Disk -Number 1"))
        self.assertTrue(command_needs_confirmation("Set-Content .\\config.txt 'value'"))
        self.assertTrue(command_needs_confirmation("reg add HKCU\\Software\\Example"))

    def test_download_and_execute_is_flagged(self):
        self.assertTrue(command_needs_confirmation("Invoke-Expression $command"))
        self.assertTrue(command_needs_confirmation("Invoke-WebRequest https://example.invalid"))

    def test_ollama_default_model_is_beam(self):
        self.assertEqual(PROVIDERS["ollama"].default_model, "beam")

    def test_openai_model_list_payload(self):
        payload = {"object": "list", "data": [{"id": "openai/gpt-oss-120b"}, {"id": "qwen/qwen3.8-27b"}]}
        self.assertEqual(extract_model_ids(payload, "groq"), ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"])

    def test_ollama_cloud_tags_normalize_cli_cloud_suffix(self):
        payload = {"models": [{"name": "beam:cloud"}, {"name": "deepseek-v4.1-flash:cloud"}]}
        self.assertEqual(extract_model_ids(payload, "ollama"), ["beam", "deepseek-v4.1-flash"])

    def test_empty_openai_catalog_falls_back_to_ollama_models_array(self):
        payload = {"data": [], "models": [{"name": "beam:cloud"}]}
        self.assertEqual(extract_model_ids(payload, "ollama"), ["beam"])

    def test_language_detection_respects_explicit_preference(self):
        self.assertEqual(detect_language("pt-BR"), "pt")
        self.assertEqual(detect_language("en-US"), "en")

    def test_translations_have_fallback_and_formatting(self):
        self.assertEqual(tr("welcome", "pt"), "Bem-vindo ao NEXUS 1.1")
        self.assertEqual(tr("unknown_command", "en", command="/oops"), "Unknown command: /oops. Type /help.")
        self.assertEqual(language_name("en"), "English")

    def test_escaped_newlines_are_converted(self):
        normalized = normalize_text_content("linha 1\\nlinha 2\\n- item")
        self.assertEqual(normalized, "linha 1\nlinha 2\n- item")


if __name__ == "__main__":
    unittest.main()
