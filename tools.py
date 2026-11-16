"""Windows desktop tools used by the NEXUS operator agent."""
from __future__ import annotations

import base64
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import pyautogui
from task_recovery import redact_sensitive_text
import pygetwindow as gw

try:
    import pyperclip
except ImportError:  # Clipboard paste is optional; ASCII typing still works.
    pyperclip = None

from config import BASE_DIR
from text_utils import normalize_text_content

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15

SCREENSHOT_DIR = BASE_DIR / "nexus_screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


class DesktopTools:
    """Narrow, validated wrappers around PyAutoGUI and Windows process APIs."""

    @staticmethod
    def _check_coordinates(x: int, y: int) -> tuple[int, int]:
        width, height = pyautogui.size()
        x, y = int(x), int(y)
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(f"Coordenadas fora da tela ({width}x{height}): {x}, {y}")
        return x, y

    @staticmethod
    def mouse_move(x: int, y: int) -> str:
        x, y = DesktopTools._check_coordinates(x, y)
        pyautogui.moveTo(x, y, duration=0.2)
        actual = pyautogui.position()
        if (int(actual.x), int(actual.y)) != (x, y):
            return f"Movimento solicitado para ({x}, {y}), mas a posição observada foi ({int(actual.x)}, {int(actual.y)})."
        return f"Cursor confirmado em ({x}, {y})."

    @staticmethod
    def left_click(x: int, y: int) -> str:
        x, y = DesktopTools._check_coordinates(x, y)
        pyautogui.click(x, y, button="left")
        return f"Evento de clique esquerdo enviado para ({x}, {y}); o efeito no aplicativo não foi verificado."

    @staticmethod
    def right_click(x: int, y: int) -> str:
        x, y = DesktopTools._check_coordinates(x, y)
        pyautogui.click(x, y, button="right")
        return f"Evento de clique direito enviado para ({x}, {y}); o efeito no aplicativo não foi verificado."

    @staticmethod
    def double_click(x: int, y: int) -> str:
        x, y = DesktopTools._check_coordinates(x, y)
        pyautogui.doubleClick(x, y, button="left")
        return f"Evento de duplo clique enviado para ({x}, {y}); o efeito no aplicativo não foi verificado."

    @staticmethod
    def scroll(amount: int, x: int | None = None, y: int | None = None) -> str:
        if not -20 <= int(amount) <= 20 or int(amount) == 0:
            raise ValueError("A rolagem precisa estar entre -20 e 20 linhas e não pode ser zero.")
        if x is not None and y is not None:
            x, y = DesktopTools._check_coordinates(x, y)
            pyautogui.moveTo(x, y, duration=0.1)
        pyautogui.scroll(int(amount))
        return f"Evento de rolagem enviado: {int(amount)} linhas; o efeito na janela não foi verificado."

    @staticmethod
    def activate_window(title: str) -> str:
        query = str(title).strip()
        if not query or len(query) > 200:
            raise ValueError("Informe parte do título da janela (até 200 caracteres).")
        normalized = query.casefold()
        aliases = {
            "notepad": ("notepad", "bloco de notas"),
            "notepad.exe": ("notepad", "bloco de notas"),
            "bloco de notas": ("notepad", "bloco de notas"),
            "calculator": ("calculator", "calculadora", "calc"),
            "calculadora": ("calculator", "calculadora", "calc"),
            "calc": ("calculator", "calculadora", "calc"),
            "calc.exe": ("calculator", "calculadora", "calc"),
            "explorer": ("explorer", "file explorer", "explorador de arquivos"),
            "explorer.exe": ("explorer", "file explorer", "explorador de arquivos"),
            "explorador de arquivos": ("explorer", "file explorer", "explorador de arquivos"),
        }
        search_terms = aliases.get(normalized, (normalized,))
        matches = [
            window for window in gw.getAllWindows()
            if any(term in (window.title or "").casefold() for term in search_terms)
        ]
        if not matches:
            return f"Nenhuma janela corresponde ao título: {query}"
        try:
            matches[0].activate()
        except Exception as exc:
            raise RuntimeError(f"Não foi possível ativar a janela: {type(exc).__name__}") from exc
        return f"Solicitação de foco enviada para: {(matches[0].title or query)[:200]}. Verifique a janela ativa."

    @staticmethod
    def type_text(text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("O texto precisa ser uma string.")
        if len(text) > 12000:
            raise ValueError("Texto muito longo (limite: 12.000 caracteres por chamada).")
        if pyperclip and ("\n" in text or any(ord(char) > 127 for char in text)):
            try:
                pyperclip.copy(text)
            except Exception as exc:
                raise RuntimeError("Não foi possível acessar a área de transferência para digitar texto Unicode/multilinha.") from exc
            pyautogui.hotkey("ctrl", "v")
        else:
            pyautogui.write(text, interval=0.01)
        return f"Texto enviado ao campo ativo ({len(text)} caracteres); o conteúdo no aplicativo não foi lido de volta para verificação."

    @staticmethod
    def press_key(key: str) -> str:
        key = str(key).strip().lower()
        if key not in pyautogui.KEYBOARD_KEYS:
            raise ValueError(f"Tecla não reconhecida pelo PyAutoGUI: {key}")
        pyautogui.press(key)
        return f"Tecla pressionada: {key}."

    @staticmethod
    def key_combination(keys: list[str]) -> str:
        if not isinstance(keys, list) or not 1 <= len(keys) <= 5:
            raise ValueError("Informe uma lista com 1 a 5 teclas.")
        normalized = [str(key).strip().lower() for key in keys]
        unknown = [key for key in normalized if key not in pyautogui.KEYBOARD_KEYS]
        if unknown:
            raise ValueError(f"Teclas não reconhecidas: {', '.join(unknown)}")
        pyautogui.hotkey(*normalized)
        return f"Combinação pressionada: {' + '.join(normalized)}."

    @staticmethod
    def _desktop_directory() -> Path:
        """Resolve the actual Windows Desktop folder, including redirected folders."""
        if os.name == "nt":
            try:
                import ctypes
                from ctypes import wintypes
                path = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
                result = ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, path)
                if result == 0 and path.value:
                    return Path(path.value)
            except Exception:
                pass
        return Path.home() / "Desktop"

    @staticmethod
    def write_text_file(filename: str, content: str, directory: str | None = None) -> str:
        """Create a new UTF-8 text file in the workspace (or Desktop) without overwriting."""
        if os.name != "nt":
            raise OSError("A criação de arquivos na Área de Trabalho está disponível nesta versão para Windows.")
        raw_name = str(filename or "").strip()
        if not raw_name or len(raw_name) > 120 or Path(raw_name).name != raw_name or any(ch in raw_name for ch in '<>:\"/\\|?*'):
            raise ValueError("Informe apenas um nome de arquivo válido, sem caminhos ou caracteres especiais.")
        if not raw_name.lower().endswith(".txt"):
            raw_name += ".txt"
        if not isinstance(content, str):
            raise TypeError("O conteúdo do arquivo precisa ser texto.")
        if len(content) > 100_000:
            raise ValueError("O conteúdo excede o limite de 100.000 caracteres.")
        content = normalize_text_content(content)
        if directory:
            target_dir = Path(directory).expanduser().resolve()
            if not target_dir.exists() or not target_dir.is_dir():
                raise NotADirectoryError(f"Workspace não existe ou não é uma pasta: {target_dir}")
        else:
            target_dir = DesktopTools._desktop_directory()
            target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / raw_name
        if destination.exists():
            raise FileExistsError(f"O arquivo {raw_name} já existe. Não foi sobrescrito.")
        with destination.open("x", encoding="utf-8-sig", newline="") as handle:
            handle.write(content.replace("\r\n", "\n").replace("\r", "\n").replace("\n", os.linesep))
        return f"Arquivo criado em: {destination} ({len(content)} caracteres)."

    @staticmethod
    def list_directory(path: str = "", limit: int = 100) -> str:
        """List one directory without invoking a shell or changing files."""
        raw_path = str(path or "").strip().strip('"')
        target = Path(raw_path).expanduser() if raw_path else DesktopTools._desktop_directory()
        if not target.is_absolute():
            target = Path.cwd() / target
        target = target.resolve()
        if not target.exists():
            return f"A pasta não existe: {target}"
        if not target.is_dir():
            return f"O caminho informado não é uma pasta: {target}"
        limit = max(1, min(int(limit), 200))
        try:
            entries = sorted(target.iterdir(), key=lambda item: (not item.is_dir(), item.name.casefold()))
        except OSError as exc:
            return f"Não foi possível listar a pasta: {type(exc).__name__}: {exc}"
        if not entries:
            return f"Pasta vazia: {target}"
        lines = [f"Conteúdo de: {target}"]
        for item in entries[:limit]:
            try:
                kind = "PASTA" if item.is_dir() else "ARQUIVO"
                size = "" if item.is_dir() else f" • {item.stat().st_size} bytes"
                lines.append(f"- [{kind}] {item.name}{size}")
            except OSError:
                lines.append(f"- [INDISPONÍVEL] {item.name}")
        if len(entries) > limit:
            lines.append(f"... mais {len(entries) - limit} itens omitidos (limite {limit}).")
        return "\n".join(lines)

    @staticmethod
    def read_text_file(path: str, directory: str | None = None, max_chars: int = 5500) -> str:
        """Read a bounded text file inside the active workspace or project directory."""
        raw_path = str(path or "").strip().strip('"')
        if not raw_path or len(raw_path) > 1000:
            raise ValueError("Informe um caminho de arquivo válido (até 1.000 caracteres).")
        target = Path(raw_path).expanduser()
        root = Path(directory).expanduser().resolve() if directory else Path.cwd().resolve()
        if not target.is_absolute():
            target = root / target
        target = target.resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise PermissionError("Por segurança, a leitura está limitada ao workspace/diretório do projeto. Defina /workspace para mudar o escopo.") from exc
        lower_name = target.name.casefold()
        protected = (
            lower_name == ".env" or (lower_name.startswith(".env.") and lower_name != ".env.example")
            or any(token in lower_name for token in ("apikey", "api_key", "api-key", "credential", "password", "secret"))
            or lower_name in {"token", "token.txt", "access_token.txt", "refresh_token.txt"}
            or target.suffix.casefold() in {".pem", ".key", ".p12", ".pfx"}
        )
        if protected:
            raise PermissionError("Arquivo com nome associado a credenciais/segredos bloqueado pela leitura automática.")
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"Arquivo não encontrado: {target}")
        if target.stat().st_size > 1_000_000:
            raise ValueError("Arquivo maior que 1 MB; leitura bloqueada para evitar consumo excessivo de memória/contexto.")
        limit = max(200, min(int(max_chars), 5500))
        raw = target.read_bytes()
        if b"\x00" in raw[:4096]:
            raise ValueError("O arquivo parece ser binário; a ferramenta aceita apenas texto.")
        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            content = raw.decode("cp1252")
        truncated = len(content) > limit
        excerpt = redact_sensitive_text(content[:limit])
        suffix = f"\n[conteúdo truncado; {len(content) - limit} caracteres omitidos]" if truncated else ""
        return f"Arquivo: {target}\n{excerpt}{suffix}"

    @staticmethod
    def screen_info() -> dict[str, Any]:
        """Return measured display dimensions and foreground-window metadata."""
        width, height = pyautogui.size()
        result: dict[str, Any] = {
            "screen": {"width": int(width), "height": int(height)},
            "active_window": None,
            "source": "PyAutoGUI + Windows API",
        }
        if os.name != "nt":
            result["source"] = "PyAutoGUI (non-Windows)"
            return result
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            user32.GetForegroundWindow.restype = wintypes.HWND
            user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
            user32.GetWindowTextLengthW.restype = ctypes.c_int
            user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
            user32.GetWindowTextW.restype = ctypes.c_int
            user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
            user32.GetWindowRect.restype = wintypes.BOOL
            user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
            user32.GetWindowThreadProcessId.restype = wintypes.DWORD
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                length = user32.GetWindowTextLengthW(hwnd)
                title_buffer = ctypes.create_unicode_buffer(max(1, length + 1))
                user32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))
                rect = wintypes.RECT()
                has_rect = bool(user32.GetWindowRect(hwnd, ctypes.byref(rect)))
                process_id = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                result["active_window"] = {
                    "title": title_buffer.value or "(sem título)",
                    "process_id": int(process_id.value),
                    "rect": ({"left": rect.left, "top": rect.top, "right": rect.right,
                              "bottom": rect.bottom, "width": rect.right - rect.left,
                              "height": rect.bottom - rect.top} if has_rect else None),
                }
        except Exception as exc:
            result["windows_api_warning"] = f"Não foi possível consultar a janela ativa: {type(exc).__name__}: {exc}"
        return result

    @staticmethod
    def active_window() -> dict[str, Any]:
        info = DesktopTools.screen_info()
        return {"active_window": info.get("active_window"), "screen": info.get("screen"),
                "source": info.get("source"), "windows_api_warning": info.get("windows_api_warning")}

    @staticmethod
    def screenshot(filename: str = "", include_image: bool = False) -> dict[str, Any]:
        requested = Path(str(filename)).name if filename else f"screen_{time.time_ns()}.png"
        requested = re.sub(r"[^A-Za-z0-9._-]", "_", requested)
        if not requested.lower().endswith((".png", ".jpg", ".jpeg")):
            requested += ".png"
        if requested in {".", ".."}:
            requested = f"screen_{time.time_ns()}.png"
        destination = SCREENSHOT_DIR / requested
        image = pyautogui.screenshot()
        image.save(destination)
        metadata = DesktopTools.screen_info()
        result: dict[str, Any] = {
            "path": str(destination),
            "message": f"Captura salva em {destination.relative_to(BASE_DIR)}.",
            "metadata": metadata,
            "image_dimensions": {"width": int(image.width), "height": int(image.height)},
        }
        if include_image:
            preview = image.convert("RGB")
            preview.thumbnail((1440, 900))
            from io import BytesIO
            buffer = BytesIO()
            preview.save(buffer, format="JPEG", quality=78, optimize=True)
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
            result["image_data_url"] = f"data:image/jpeg;base64,{encoded}"
        return result

    @staticmethod
    def list_windows() -> str:
        titles: list[str] = []
        for window in gw.getAllWindows():
            title = (window.title or "").strip()
            if title and title not in titles:
                titles.append(title)
        if not titles:
            return "Nenhuma janela com título foi encontrada."
        return "Janelas abertas (até 25):\n" + "\n".join(f"- {title}" for title in titles[:25])

    @staticmethod
    def open_application(path: str) -> str:
        target = str(path).strip().strip('"')
        if not target:
            raise ValueError("Informe o nome ou caminho do aplicativo.")
        if len(target) > 500:
            raise ValueError("Caminho muito longo.")
        aliases = {
            "notepad": "notepad.exe",
            "notepad.exe": "notepad.exe",
            "bloco de notas": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "calc.exe": "calc.exe",
            "calculadora": "calc.exe",
            "explorer": "explorer.exe",
            "explorer.exe": "explorer.exe",
            "explorador de arquivos": "explorer.exe",
        }
        target = aliases.get(target.casefold(), target)
        if os.name != "nt":
            raise OSError("A abertura de aplicativos desta ferramenta está disponível no Windows.")
        # Resolve common Windows apps explicitly; System32 is not guaranteed to be
        # present in PATH on every Windows installation.
        title_hints = {
            "notepad.exe": ("bloco de notas", "notepad"),
            "calc.exe": ("calculadora", "calculator"),
            "explorer.exe": ("explorador de arquivos", "file explorer"),
        }
        for window in gw.getAllWindows():
            title = (window.title or "").strip()
            if title and any(hint in title.casefold() for hint in title_hints.get(target.casefold(), ())):
                try:
                    window.activate()
                    return f"Aplicativo já estava aberto e a janela foi ativada: {title}."
                except Exception:
                    break
        system_root = Path(os.environ.get("SystemRoot", r"C:\\Windows"))
        system_apps = {"notepad.exe", "calc.exe", "explorer.exe"}
        if target.casefold() in system_apps:
            system_candidate = system_root / "System32" / target
            executable = str(system_candidate) if system_candidate.is_file() else (shutil.which(target) or target)
        else:
            executable = shutil.which(target) or target
        if not Path(executable).exists() and not shutil.which(executable):
            raise FileNotFoundError(f"Aplicativo/caminho não encontrado: {target}")
        before = {getattr(window, "_hWnd", None) for window in gw.getAllWindows()}
        process = subprocess.Popen([executable], close_fds=True)
        # Give the Windows shell/app a moment to create or activate its window.
        deadline = time.monotonic() + 5.0
        focused_title = ""
        while time.monotonic() < deadline:
            windows = gw.getAllWindows()
            new_windows = [window for window in windows if getattr(window, "_hWnd", None) not in before and (window.title or "").strip()]
            if new_windows:
                try:
                    new_windows[-1].activate()
                    focused_title = (new_windows[-1].title or "").strip()
                except Exception:
                    pass
                break
            time.sleep(0.25)
        if focused_title:
            return f"Aplicativo aberto e janela ativada: {focused_title}. O campo/janela está pronto para interação."
        return f"Solicitação de abertura enviada para {target} (PID {process.pid}). Se a janela não aparecer, consulte as janelas abertas."

    @staticmethod
    def powershell_execute(command: str) -> str:
        command = str(command).strip()
        if not command:
            raise ValueError("O comando PowerShell está vazio.")
        if len(command) > 8000:
            raise ValueError("Comando muito longo (limite: 8.000 caracteres).")
        if os.name != "nt":
            raise OSError("A execução do PowerShell está disponível somente no Windows.")
        powershell = shutil.which("pwsh.exe") or shutil.which("powershell.exe")
        if not powershell:
            system_root = os.environ.get("SystemRoot", r"C:\Windows")
            candidate = Path(system_root) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
            if candidate.is_file():
                powershell = str(candidate)
        if not powershell:
            raise FileNotFoundError("PowerShell não encontrado (pwsh.exe/powershell.exe).")
        try:
            completed = subprocess.run(
                [powershell, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("O comando excedeu o limite de 30 segundos.") from exc
        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()
        output_parts = [part for part in (stdout, stderr) if part]
        output = "\n[stderr]\n".join(output_parts) if output_parts else "Comando concluído sem saída textual."
        if completed.returncode != 0:
            return f"PowerShell retornou código {completed.returncode}.\n{output[:6000]}"
        return f"PowerShell concluído (código 0).\n{output[:6000]}"
