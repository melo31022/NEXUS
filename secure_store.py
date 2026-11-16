"""Per-user encrypted settings storage for Windows using DPAPI."""
from __future__ import annotations

import ctypes
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def _settings_path() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    return root / "NEXUS" / "settings.dat"


def _crypt(data: bytes, *, decrypt: bool) -> bytes:
    if os.name != "nt":
        raise OSError("O armazenamento seguro de credenciais está disponível apenas no Windows.")
    class DataBlob(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    blob_pointer = ctypes.POINTER(DataBlob)
    crypt32.CryptProtectData.argtypes = [
        blob_pointer, ctypes.c_wchar_p, blob_pointer, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_uint32, blob_pointer
    ]
    crypt32.CryptProtectData.restype = ctypes.c_int
    crypt32.CryptUnprotectData.argtypes = [
        blob_pointer, ctypes.POINTER(ctypes.c_wchar_p), blob_pointer,
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, blob_pointer
    ]
    crypt32.CryptUnprotectData.restype = ctypes.c_int
    source = ctypes.create_string_buffer(data)
    source_blob = DataBlob(len(data), ctypes.cast(source, ctypes.POINTER(ctypes.c_ubyte)))
    output_blob = DataBlob()
    flags = 0x1  # CRYPTPROTECT_UI_FORBIDDEN
    if decrypt:
        ok = crypt32.CryptUnprotectData(
            ctypes.byref(source_blob), None, None, None, None, flags, ctypes.byref(output_blob)
        )
    else:
        ok = crypt32.CryptProtectData(
            ctypes.byref(source_blob), "NEXUS settings", None, None, None, flags, ctypes.byref(output_blob)
        )
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(output_blob.pbData, ctypes.c_void_p))


def load_settings() -> dict[str, Any]:
    """Load the current Windows user's encrypted NEXUS settings."""
    if os.name != "nt":
        return {}
    path = _settings_path()
    if not path.is_file():
        return {}
    try:
        raw = _crypt(path.read_bytes(), decrypt=True)
        value = json.loads(raw.decode("utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        raise RuntimeError(
            "Não foi possível ler as configurações protegidas do NEXUS. "
            "O arquivo pode estar corrompido ou ter sido criado por outra conta do Windows."
        )


def save_settings(settings: dict[str, Any]) -> None:
    """Atomically save settings encrypted for the current Windows user."""
    if os.name != "nt":
        raise OSError("A gravação segura de credenciais requer Windows.")
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(settings, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    encrypted = _crypt(payload, decrypt=False)
    temp_name = ""
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="settings-", suffix=".tmp", delete=False) as handle:
            temp_name = handle.name
            handle.write(encrypted)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            try:
                os.unlink(temp_name)
            except OSError:
                pass
