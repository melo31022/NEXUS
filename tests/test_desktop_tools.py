import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class DesktopToolsTests(unittest.TestCase):
    def _load_tools(self):
        if os.name != "nt":
            self.skipTest("DesktopTools integration imports are validated on Windows runners.")
        from tools import DesktopTools
        return DesktopTools

    def test_read_text_file_is_scoped_and_rejects_common_secrets(self):
        DesktopTools = self._load_tools()
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            sample = root / "sample.txt"
            sample.write_text("NEXUS test content", encoding="utf-8")
            result = DesktopTools.read_text_file(str(sample), directory=str(root))
            self.assertIn("NEXUS test content", result)

            with self.assertRaises(PermissionError):
                DesktopTools.read_text_file(str(Path(outside) / "outside.txt"), directory=str(root))

            secret = root / "apikeyopenrouter.txt"
            secret.write_text("not a real key", encoding="utf-8")
            with self.assertRaises(PermissionError):
                DesktopTools.read_text_file(str(secret), directory=str(root))

            env_file = root / ".env"
            env_file.write_text("TOKEN=not-a-real-token", encoding="utf-8")
            with self.assertRaises(PermissionError):
                DesktopTools.read_text_file(str(env_file), directory=str(root))

    def test_read_text_file_rejects_binary_and_truncates_large_text(self):
        DesktopTools = self._load_tools()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / "image.bin"
            binary.write_bytes(b"\x00\x01\x02")
            with self.assertRaises(ValueError):
                DesktopTools.read_text_file(str(binary), directory=str(root))

            long_text = root / "long.txt"
            long_text.write_text("x" * 600, encoding="utf-8")
            result = DesktopTools.read_text_file(str(long_text), directory=str(root), max_chars=200)
            self.assertIn("conteúdo truncado", result)

    def test_activate_window_resolves_portuguese_and_english_aliases(self):
        DesktopTools = self._load_tools()

        class FakeWindow:
            title = "Sem título - Bloco de notas"
            activated = False

            def activate(self):
                self.activated = True

        window = FakeWindow()
        with patch("tools.gw.getAllWindows", return_value=[window]):
            result = DesktopTools.activate_window("notepad")
        self.assertTrue(window.activated)
        self.assertIn("Solicitação de foco enviada", result)

    def test_mouse_move_reports_observed_cursor_position(self):
        DesktopTools = self._load_tools()

        class Point:
            x = 120
            y = 240

        with patch("tools.pyautogui.size", return_value=(1920, 1080)), \
             patch("tools.pyautogui.moveTo") as move, \
             patch("tools.pyautogui.position", return_value=Point()):
            result = DesktopTools.mouse_move(120, 240)
        move.assert_called_once()
        self.assertIn("Cursor confirmado em (120, 240)", result)


if __name__ == "__main__":
    unittest.main()
