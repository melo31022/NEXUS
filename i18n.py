"""Small, dependency-free language detection and UI translations for NEXUS."""
from __future__ import annotations

import locale
import os
import re
import sys

SUPPORTED = {"pt": "Português", "en": "English"}


def _windows_language() -> str | None:
    if os.name != "nt":
        return None
    try:
        import ctypes
        buffer = ctypes.create_unicode_buffer(85)
        if ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer)):
            match = re.match(r"([a-zA-Z]{2,3})", buffer.value)
            if match:
                return match.group(1).lower()
    except Exception:
        return None
    return None


def detect_language(preference: str | None = None) -> str:
    """Return 'pt' or 'en'; prefer explicit setting, then Windows/user locale."""
    requested = (preference or os.getenv("NEXUS_LANGUAGE", "auto")).strip().lower()
    if requested in {"pt", "pt-br", "pt_br", "portuguese", "português"}:
        return "pt"
    if requested in {"en", "en-us", "en_us", "english"}:
        return "en"
    candidates = [_windows_language()]
    for value in (os.getenv("LC_ALL"), os.getenv("LC_MESSAGES"), os.getenv("LANG")):
        if value:
            candidates.append(value.split(".", 1)[0].split("_", 1)[0].split("-", 1)[0].lower())
    try:
        current = locale.getlocale()[0]
        if current:
            candidates.append(current.split("_", 1)[0].lower())
    except (TypeError, ValueError):
        pass
    for language in candidates:
        if language == "pt":
            return "pt"
        if language == "en":
            return "en"
    # Windows defaults are often unavailable in headless environments.
    return "pt" if sys.platform == "win32" else "en"


TRANSLATIONS = {
    "pt": {
        "welcome": "Bem-vindo ao NEXUS 1.0",
        "tagline": "Agente de controle do computador para Windows",
        "subtitle": "Pesquisar • Planejar • Operar • Verificar",
        "getting_started": "Primeiros passos",
        "provider_step": "1. Escolha o provedor em nuvem:",
        "provider_list": "Listar provedores",
        "ollama": "Ollama Cloud (modelo padrão: Beam)",
        "groq": "Groq Cloud",
        "model_step": "2. Escolha o modelo oferecido pelo provedor:",
        "fetch_models": "Buscar modelos disponíveis",
        "select_number": "Selecionar modelo pelo número",
        "select_id": "Selecionar pelo ID do modelo",
        "mode_step": "3. Escolha o modo de operação:",
        "list_modes": "Listar modos",
        "operator": "Operar o computador",
        "planner": "Planejar sem executar",
        "chat": "Conversar sem ferramentas",
        "other_commands": "Outros comandos: /language, /vision, /workspace, /status, /help, /exit",
        "prompt": "Descreva uma tarefa ou digite / para ver os comandos",
        "mode": "Modo", "provider": "Provedor", "model": "Modelo", "api_key": "Chave de API",
        "vision": "Visão", "workspace": "Pasta de trabalho", "language": "Idioma",
        "configured": "configurada", "missing": "ausente", "on": "ATIVADA", "off": "DESATIVADA",
        "desktop_default": "Área de Trabalho (padrão)",
        "help_title": "Comandos do NEXUS", "command": "Comando", "description": "Descrição",
        "language_command": "Define o idioma: auto, pt ou en.",
        "language_auto": "Idioma detectado automaticamente",
        "language_set": "Idioma da interface definido como Português.",
        "language_invalid": "Use /language auto, /language pt ou /language en.",
        "session_ended": "Sessão do NEXUS encerrada.",
        "unknown_command": "Comando desconhecido: {command}. Digite /help.",
        "error": "Erro", "input_cancelled": "Entrada cancelada. Use /exit para encerrar.",
        "status_title": "Configuração da sessão", "modes_title": "Modos de operação do NEXUS",
        "providers_title": "Provedores disponíveis", "active": "ativo", "selected": "selecionado",
        "ready": "Pronto", "language_auto_status": "automático",
        "cmd_providers": "Lista os provedores em nuvem.",
        "cmd_provider": "Seleciona Ollama Cloud ou Groq Cloud.",
        "cmd_agents": "Consulta o catálogo de modelos do provedor.",
        "cmd_agent": "Seleciona o modelo pelo número ou ID.",
        "cmd_modes": "Lista os modos do NEXUS.",
        "cmd_mode": "Seleciona Operator, Planner ou Chat.",
        "cmd_model": "Atalho para /agent.",
        "cmd_vision": "Controla o envio de capturas ao modelo.",
        "cmd_workspace": "Mostra ou define a pasta de trabalho.",
        "cmd_status": "Mostra a configuração atual.",
        "cmd_clear": "Limpa e redesenha a tela inicial.",
        "cmd_help": "Mostra esta ajuda.",
        "cmd_exit": "Encerra o NEXUS.",
        "mode_operator": "Opera o computador com ferramentas.",
        "mode_planner": "Cria planos sem executar ações.",
        "mode_chat": "Conversa sem ferramentas do computador.",
        "status_selected": "selecionado", "status_column": "Estado",
        "provider_column": "Provedor", "endpoint_column": "Endpoint", "key_column": "Chave de API",
        "model_column": "ID do modelo", "number_column": "Nº",
    },
    "en": {
        "welcome": "Welcome to NEXUS 1.0",
        "tagline": "Windows computer-use agent",
        "subtitle": "Research • Plan • Operate • Verify",
        "getting_started": "Getting started",
        "provider_step": "1. Choose a cloud provider:",
        "provider_list": "List providers",
        "ollama": "Ollama Cloud (default model: Beam)",
        "groq": "Groq Cloud",
        "model_step": "2. Choose a model offered by the provider:",
        "fetch_models": "Fetch available models",
        "select_number": "Select model by number",
        "select_id": "Select by model ID",
        "mode_step": "3. Choose an operation mode:",
        "list_modes": "List modes",
        "operator": "Operate the computer",
        "planner": "Plan without executing",
        "chat": "Chat without tools",
        "other_commands": "Other commands: /language, /vision, /workspace, /status, /help, /exit",
        "prompt": "Describe a task or type / to see commands",
        "mode": "Mode", "provider": "Provider", "model": "Model", "api_key": "API key",
        "vision": "Vision", "workspace": "Workspace", "language": "Language",
        "configured": "configured", "missing": "missing", "on": "ON", "off": "OFF",
        "desktop_default": "Desktop (default)",
        "help_title": "NEXUS commands", "command": "Command", "description": "Description",
        "language_command": "Set the language: auto, pt or en.",
        "language_auto": "Language detected automatically",
        "language_set": "Interface language set to English.",
        "language_invalid": "Use /language auto, /language pt or /language en.",
        "session_ended": "NEXUS session ended.",
        "unknown_command": "Unknown command: {command}. Type /help.",
        "error": "Error", "input_cancelled": "Input cancelled. Use /exit to quit.",
        "status_title": "Session configuration", "modes_title": "NEXUS operation modes",
        "providers_title": "Available providers", "active": "active", "selected": "selected",
        "ready": "Ready", "language_auto_status": "auto",
        "cmd_providers": "List cloud providers.",
        "cmd_provider": "Select Ollama Cloud or Groq Cloud.",
        "cmd_agents": "Fetch the provider model catalog.",
        "cmd_agent": "Select a model by number or ID.",
        "cmd_modes": "List NEXUS operation modes.",
        "cmd_mode": "Select Operator, Planner, or Chat.",
        "cmd_model": "Alias for /agent.",
        "cmd_vision": "Control screenshot sharing with the model.",
        "cmd_workspace": "Show or set the workspace folder.",
        "cmd_status": "Show current configuration.",
        "cmd_clear": "Clear and redraw the welcome screen.",
        "cmd_help": "Show this help.",
        "cmd_exit": "Exit NEXUS.",
        "mode_operator": "Operate the computer using tools.",
        "mode_planner": "Create plans without taking action.",
        "mode_chat": "Chat without computer tools.",
        "status_selected": "selected", "status_column": "Status",
        "provider_column": "Provider", "endpoint_column": "Endpoint", "key_column": "API key",
        "model_column": "Model ID", "number_column": "#",
    },
}


def tr(key: str, language: str = "pt", **values: object) -> str:
    text = TRANSLATIONS.get(language, TRANSLATIONS["pt"]).get(key, key)
    return text.format(**values) if values else text


def language_name(language: str) -> str:
    return SUPPORTED.get(language, "Português")
