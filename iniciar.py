"""NEXUS first-run setup and launcher (Windows-friendly, no BAT required)."""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
VENV_PY = VENV / "Scripts" / "python.exe" if os.name == "nt" else VENV / "bin" / "python"
REQUIREMENTS = ROOT / "requirements.txt"
MARKER = VENV / ".nexus_requirements_hash"

def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("\n[NEXUS]", " ".join(f'"{part}"' if " " in part else part for part in command))
    return subprocess.run(command, cwd=ROOT, check=check)

def main() -> int:
    if sys.version_info < (3, 11):
        print("[NEXUS] Python 3.11 ou mais recente é necessário.")
        print("Instale em https://www.python.org/downloads/ e execute: py -3.11 iniciar.py")
        return 1
    if not REQUIREMENTS.is_file() or not (ROOT / "main.py").is_file():
        print("[NEXUS] Arquivos do projeto não encontrados. Extraia o ZIP inteiro antes de iniciar.")
        return 1

    if not VENV_PY.is_file():
        print("[NEXUS] Criando ambiente virtual isolado...")
        run([sys.executable, "-m", "venv", str(VENV)])

    digest = hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()
    installed = MARKER.read_text(encoding="utf-8").strip() if MARKER.is_file() else ""
    if installed != digest:
        print("[NEXUS] Instalando/atualizando dependências...")
        run([str(VENV_PY), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(REQUIREMENTS)])
        MARKER.write_text(digest, encoding="utf-8")

    env_file = ROOT / ".env"
    example = ROOT / ".env.example"
    if not env_file.exists() and example.is_file():
        shutil.copy2(example, env_file)
        print("[NEXUS] .env criado. Configure sua chave de API nesse arquivo.")

    print("\n[NEXUS] Iniciando...\n")
    result = subprocess.run([str(VENV_PY), str(ROOT / "main.py")], cwd=ROOT)
    return result.returncode

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"\n[NEXUS] Um comando terminou com código {exc.returncode}.")
        raise SystemExit(exc.returncode)
    except KeyboardInterrupt:
        print("\n[NEXUS] Inicialização interrompida.")
        raise SystemExit(130)
