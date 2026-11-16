@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title NEXUS 1.0

set "PYTHON="
where py >nul 2>nul
if not errorlevel 1 (
    py -3.11 --version >nul 2>nul
    if not errorlevel 1 set "PYTHON=py -3.11"
)
if not defined PYTHON (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON=python"
    )
)
if not defined PYTHON (
    echo [NEXUS] Python 3.11 ou mais recente nao foi encontrado.
    echo Instale Python 3.11+ em https://www.python.org/downloads/ e marque Add Python to PATH.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [NEXUS] Criando ambiente virtual...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" >nul 2>nul
if errorlevel 1 (
    echo [NEXUS] O ambiente .venv usa Python antigo. Apague .venv e execute novamente.
    goto :error
)

if not exist ".venv\nexus-deps-installed" (
    echo [NEXUS] Instalando dependencias (primeira inicializacao)...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto :error
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :error
    type nul > ".venv\nexus-deps-installed"
)

if not exist ".env" if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo [NEXUS] Arquivo .env criado. Configure sua chave de API antes de consultar os modelos.
)

".venv\Scripts\python.exe" main.py
if errorlevel 1 goto :error
endlocal
exit /b 0

:error
echo.
echo [NEXUS] A inicializacao encontrou um erro. Confira as mensagens acima.
pause
endlocal
exit /b 1
