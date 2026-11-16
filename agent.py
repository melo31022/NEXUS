"""NEXUS cloud-model loop with OpenAI-compatible APIs and local Windows tools."""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config import BASE_DIR, MAX_STEPS_PER_TASK, REQUEST_TIMEOUT, ProviderConfig, MAX_CONTEXT_TOKENS, MAX_OUTPUT_TOKENS, MAX_TOOL_CALLS_PER_STEP
from tools import DesktopTools
from safety import command_needs_confirmation
from token_guard import compact_messages
from providers import request_with_retry, sanitized_api_error
from task_recovery import TaskJournal, redact_sensitive_text

console = Console()

MODES: dict[str, dict[str, Any]] = {
    "operator": {
        "label": "Operator",
        "description": "Pode observar a tela e operar mouse, teclado e ferramentas do Windows.",
        "tools": True,
        "system": (
            "Você é o NEXUS Operator, um agente de computador para Windows. "
            "Transforme o pedido do usuário em ações pequenas e verificáveis. "
            "Use ferramentas somente quando forem necessárias. Após cada ação importante, confira o resultado. "
            "Nunca diga que algo foi feito sem evidência. Antes de comandos com efeitos destrutivos, explique o risco "
            "e aguarde a confirmação local do usuário. Não tente contornar confirmações, permissões ou controles de segurança. "
            "Não exponha raciocínio privado; forneça apenas atualizações breves sobre o plano e os resultados. "
            "Não invente arquivos, telas, resultados ou estados do sistema."
        ),
    },
    "planner": {
        "label": "Planner",
        "description": "Analisa o pedido e produz um plano; não executa ações no computador.",
        "tools": False,
        "system": (
            "Você é o NEXUS Planner. Analise o objetivo e crie um plano claro, ordenado e verificável. "
            "Não execute ações, não afirme ter inspecionado o computador e não invente o estado da máquina. "
            "Identifique riscos e peça confirmação quando uma etapa for destrutiva."
        ),
    },
    "chat": {
        "label": "Chat",
        "description": "Assistente conversacional sem acesso às ferramentas do computador.",
        "tools": False,
        "system": (
            "Você é o NEXUS Chat, um assistente útil e direto. Responda no idioma do usuário. "
            "Você não tem acesso ao computador nem pode afirmar que executou ações nele."
        ),
    },
}

TOOLS_SCHEMA = [
    {"type": "function", "function": {"name": "mouse_move", "description": "Move o cursor para coordenadas da tela.", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
    {"type": "function", "function": {"name": "left_click", "description": "Executa um clique esquerdo em coordenadas da tela.", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
    {"type": "function", "function": {"name": "right_click", "description": "Executa um clique direito em coordenadas da tela.", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
    {"type": "function", "function": {"name": "double_click", "description": "Executa um duplo clique esquerdo em coordenadas da tela.", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
    {"type": "function", "function": {"name": "scroll", "description": "Rola a página em até 20 linhas; x e y opcionais definem a posição.", "parameters": {"type": "object", "properties": {"amount": {"type": "integer"}, "x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["amount"]}}},
    {"type": "function", "function": {"name": "activate_window", "description": "Tenta trazer para frente uma janela cujo título contenha o texto informado.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}},
    {"type": "function", "function": {"name": "type_text", "description": "Digita texto no campo que estiver em foco.", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "press_key", "description": "Pressiona uma tecla, como enter, tab ou esc.", "parameters": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}}},
    {"type": "function", "function": {"name": "key_combination", "description": "Pressiona uma combinação de teclas, como ctrl+c.", "parameters": {"type": "object", "properties": {"keys": {"type": "array", "items": {"type": "string"}}}, "required": ["keys"]}}},
    {"type": "function", "function": {"name": "list_directory", "description": "Lista diretamente os arquivos e subpastas de uma pasta, sem PowerShell e sem alterar nada. Se path for omitido, lista o workspace atual ou a Área de Trabalho. Use para pedidos como listar arquivos, ver conteúdo de uma pasta ou conferir arquivos criados.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "read_text_file", "description": "Lê um arquivo de texto dentro do workspace/diretório do projeto. Não lê .env, nomes de arquivos associados a chaves, credenciais ou senhas, nem arquivos binários. Use somente quando o usuário pedir para ler/inspecionar o arquivo.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "max_chars": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "write_text_file", "description": "Cria um novo arquivo .txt no workspace atual (ou na Área de Trabalho se nenhum workspace estiver definido), sem sobrescrever arquivos existentes.", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}},
    {"type": "function", "function": {"name": "set_workspace", "description": "Define como workspace uma pasta existente escolhida pelo usuário ou recém-criada para o projeto. Use antes de criar arquivos do projeto nessa pasta.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "screenshot", "description": "Salva uma captura de tela. Com visão ativada e modelo compatível, a imagem também será enviada ao modelo para análise.", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}}}}},
    {"type": "function", "function": {"name": "list_windows", "description": "Lista títulos das janelas abertas no Windows. Use apenas quando precisar localizar uma janela existente; após open_application, a janela normalmente já é ativada.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_active_window", "description": "Obtém pela API do Windows a janela em primeiro plano, seu título, PID e posição real na tela.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_screen_info", "description": "Obtém a resolução real da tela e os metadados da janela ativa.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "open_application", "description": "Abre um aplicativo ou caminho executável do Windows. Opcionalmente, informe text para digitar no aplicativo assim que a janela abrir e receber foco; use isso quando o usuário pedir para abrir um app e escrever algo.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "text": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "powershell_execute", "description": "Executa um comando no PowerShell do Windows. Comandos potencialmente destrutivos exigem confirmação local.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
]

class NexusAgent:
    def __init__(
        self,
        goal: str,
        provider: ProviderConfig,
        model: str,
        mode_name: str = "operator",
        vision_enabled: bool = False,
        log_file: str | Path | None = None,
        conversation: list[dict[str, Any]] | None = None,
        workspace_dir: str | Path | None = None,
        language: str = "pt",
        resume_from_task_id: str | None = None,
    ) -> None:
        if mode_name not in MODES:
            raise ValueError(f"Modo de operação desconhecido: {mode_name}")
        self.goal = goal
        self.language = "English" if language == "en" else "Português brasileiro"
        self.provider = provider
        self.model = model.strip()
        self.mode_name = mode_name
        self.agent_profile = MODES[mode_name]
        self.vision_enabled = vision_enabled and provider.supports_vision(self.model)
        self.workspace_dir = str(Path(workspace_dir).expanduser().resolve()) if workspace_dir else None
        self.log_file = Path(log_file) if log_file else BASE_DIR / "nexus_logs" / "nexus_history.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.task_journal = TaskJournal(goal, self.workspace_dir, parent_task_id=resume_from_task_id)
        self._write_log(
            f"\n{'=' * 72}\n[SESSION {datetime.now().isoformat(timespec='seconds')}] "
            f"mode={mode_name} provider={provider.name} model={self.model}\n{'=' * 72}"
        )
        system_prompt = self.agent_profile["system"] + f"\nIdioma preferencial da interface: {self.language}. Detecte o idioma natural da mensagem mais recente do usuário e responda no mesmo idioma. Se não for possível inferir (por exemplo, uma mensagem muito curta), use o idioma preferencial da interface. Se o usuário pedir explicitamente outro idioma, siga o pedido.\n"
        if mode_name == "operator":
            system_prompt += (
                "\nFerramentas disponíveis: mouse, cliques esquerdo/direito/duplo, rolagem, digitação, teclado, foco de janelas, screenshot, janelas, "
                "abertura de aplicativos, criação de arquivos de texto no workspace e PowerShell. "
                "Para criar arquivos .txt, use sempre write_text_file; não use PowerShell ou Notepad para gravar o conteúdo. "
                "Se criar ou identificar a pasta principal de um projeto, use set_workspace com o caminho absoluto antes de criar os arquivos nela. "
                "Não altere o workspace para uma pasta não solicitada nem para um caminho inferido sem evidência. "
                "Se o usuário confirmar um nome de arquivo sugerido, preserve exatamente esse nome nas etapas seguintes; nunca o renomeie por conta própria. "
                "Gere o conteúdo solicitado quando o usuário disser que você pode inventá-lo. "
                "Mantenha contexto entre mensagens da sessão. "
                "Preserve quebras de linha reais no conteúdo; não escreva sequências literais \\n. "
                "Para listar arquivos e pastas, use list_directory; nunca use PowerShell para uma listagem simples. " 
                "Quando o usuário pedir para ler um arquivo de texto, use read_text_file; não tente ler .env, chaves ou arquivos de credenciais. "
                "Para 'abrir um aplicativo e escrever texto', use open_application com path e text opcionais na mesma chamada; isso abre a janela e digita o texto sem uma segunda rodada da IA. "
                "Para outras tarefas curtas de interface, emita chamadas ordenadas no mesmo lote quando possível. "
                "open_application já tenta ativar a janela; não chame list_windows ou activate_window depois, a menos que a abertura falhe ou a janela não esteja pronta. "
                "Use mouse_move e left_click/right_click/double_click para interagir com controles visuais; se as coordenadas não forem conhecidas, faça screenshot primeiro e use a resolução/metadados para localizar o controle. "
                "Não substitua interação visual solicitada por explicações textuais. "
                "Use PowerShell apenas para tarefas necessárias ao objetivo. "
                "Para tarefas que alterem arquivos, prefira limitar o escopo ao caminho informado pelo usuário. "
                "Não faça alterações irreversíveis sem explicar e obter confirmação local."
            )
        if conversation is None:
            self.messages = [{"role": "system", "content": system_prompt}]
        else:
            self.messages = conversation
            if not self.messages or self.messages[0].get("role") != "system":
                self.messages.insert(0, {"role": "system", "content": system_prompt})
        if mode_name == "operator":
            workspace_label = self.workspace_dir or str(DesktopTools._desktop_directory())
            workspace_context = (
                f"Contexto de diretório desta tarefa: workspace={workspace_label}. "
                "Ao criar arquivos .txt, use o workspace atual; não escolha outro diretório sem pedido explícito. "
                "Se o usuário mencionar 'a pasta do projeto' ou 'a pasta que criamos', use este workspace."
            )
            # Keep the current workspace explicit even when continuing an older conversation.
            self.messages.append({"role": "system", "content": workspace_context})
        context_marker = "[NEXUS_OPERATIONAL_CONTEXT]"
        self.messages = [
            item for item in self.messages
            if not (item.get("role") == "system" and str(item.get("content", "")).startswith(context_marker))
        ]
        workspace_label = self.workspace_dir or f"{DesktopTools._desktop_directory()} (workspace padrão)"
        directory_to_inspect = Path(self.workspace_dir) if self.workspace_dir else Path.cwd()
        if mode_name == "operator":
            try:
                visible_entries = sorted(
                    (f"{'[DIR]' if item.is_dir() else '[FILE]'} {item.name}" for item in directory_to_inspect.iterdir()),
                    key=str.casefold,
                )[:40]
                directory_snapshot = "\n".join(visible_entries) if visible_entries else "(pasta vazia)"
            except OSError as exc:
                directory_snapshot = f"(listagem indisponível: {type(exc).__name__})"
        else:
            directory_snapshot = "(não enumerado: este modo não possui ferramentas do computador)"
        tool_names = ", ".join((
            "mouse_move", "left_click", "right_click", "double_click", "scroll", "activate_window",
            "type_text", "press_key", "key_combination", "list_directory", "read_text_file", "write_text_file",
            "set_workspace", "screenshot", "list_windows", "get_active_window", "get_screen_info",
            "open_application", "powershell_execute"
        )) if self.agent_profile["tools"] else "nenhuma"
        operational_context = (
            f"{context_marker}\n"
            f"Provedor ativo: {provider.name} ({provider.label}). Modelo configurado: {self.model}. "
            f"Modo atual: {mode_name}. Visão habilitada: {self.vision_enabled}. "
            f"Diretório de execução: {Path.cwd()}. Workspace de arquivos: {workspace_label}. "
            f"Diretório listado: {directory_to_inspect if mode_name == 'operator' else 'nenhum'}. "
            f"Ferramentas disponíveis neste modo: {tool_names}.\n"
            f"Entradas visíveis (apenas nomes; não foram lidos):\n{directory_snapshot}\n"
            "Não afirme ter inspecionado o conteúdo de arquivos apenas porque seus nomes aparecem nesta lista. "
            "Use a ferramenta apropriada para ler ou verificar arquivos. Este snapshot é parcial e limitado a 40 entradas."
        )
        self.messages.append({"role": "system", "content": operational_context})
        self.messages.append({"role": "user", "content": f"Objetivo do usuário: {goal}"})

    def _write_log(self, text: str) -> None:
        try:
            with self.log_file.open("a", encoding="utf-8") as handle:
                handle.write(text + "\n")
        except OSError:
            console.print("[yellow]Aviso: não foi possível gravar o log desta sessão.[/yellow]")

    def call_ai(self) -> dict[str, Any]:
        if self.provider.requires_api_key and not self.provider.api_key:
            key_name = self.provider.api_key_env or f"{self.provider.name.upper()}_API_KEY"
            raise RuntimeError(f"Chave ausente. Configure {key_name} no arquivo .env ou nas variáveis do Windows.")
        headers = {"Content-Type": "application/json"}
        if self.provider.api_key:
            headers["Authorization"] = f"Bearer {self.provider.api_key}"
        self.messages, estimated_tokens, compacted = compact_messages(
            self.messages, budget=max(1000, MAX_CONTEXT_TOKENS - MAX_OUTPUT_TOKENS),
            tool_schema=TOOLS_SCHEMA if self.agent_profile["tools"] else None,
        )
        if compacted:
            self._write_log(f"[TokenGuard] Histórico compactado; estimativa pré-envio: {estimated_tokens} tokens.")
        if estimated_tokens > max(1000, MAX_CONTEXT_TOKENS - MAX_OUTPUT_TOKENS):
            raise RuntimeError("Token Guard não conseguiu reduzir o contexto abaixo do orçamento. Envie uma solicitação menor ou limpe o histórico com /clear.")
        console.print(f"[dim]Token Guard: estimativa ~{estimated_tokens} tokens[/dim]")
        payload: dict[str, Any] = {
            "model": self.model, "messages": self.messages,
            "temperature": 0.2, "max_tokens": MAX_OUTPUT_TOKENS,
        }
        if self.agent_profile["tools"] and self.provider.supports_tools:
            payload["tools"] = TOOLS_SCHEMA
            # Ollama Cloud's OpenAI-compatible endpoint supports `tools`, but
            # documents `tool_choice` as unsupported. Groq accepts `auto`.
            if self.provider.name != "ollama":
                payload["tool_choice"] = "auto"
        url = self.provider.normalized_base_url() + "/chat/completions"
        try:
            response = request_with_retry(lambda: requests.post(url, headers=headers, json=payload, timeout=(15, REQUEST_TIMEOUT)), retries=3)
        except requests.Timeout as exc:
            raise RuntimeError(f"A API não respondeu dentro de {REQUEST_TIMEOUT} segundos.") from exc
        except requests.RequestException as exc:
            raise RuntimeError(f"Não foi possível conectar ao provedor: {type(exc).__name__}.") from exc
        if not response.ok:
            raise RuntimeError(sanitized_api_error(response.status_code, response.text))
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError("O provedor retornou uma resposta que não é JSON válido.") from exc
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise RuntimeError("Resposta da API sem choices[0]. Verifique se o endpoint é compatível com Chat Completions.")
        return data

    def _confirm_risky_command(self, command: str) -> bool:
        console.print(Panel(Text(command), title="[bold yellow]Confirmação necessária[/bold yellow]", border_style="yellow"))
        console.print("[yellow]Este comando pode alterar ou interromper partes do sistema.[/yellow]")
        answer = console.input("Executar? [s/N]: ").strip().lower()
        return answer in {"s", "sim", "y", "yes"}

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if not isinstance(arguments, dict):
            return "Erro: argumentos da ferramenta precisam ser um objeto JSON."
        if name == "set_workspace":
            raw_path = str(arguments.get("path", "")).strip().strip('"')
            if not raw_path:
                return "Erro: informe o caminho da pasta de trabalho."
            target = Path(raw_path).expanduser().resolve()
            if not target.exists() or not target.is_dir():
                return f"Workspace não definido: a pasta não existe ou não é um diretório: {target}"
            self.workspace_dir = str(target)
            self.task_journal.set_workspace(self.workspace_dir)
            return f"Workspace definido para esta sessão: {target}"
        if name == "list_directory":
            return DesktopTools.list_directory(
                path=arguments.get("path") or (self.workspace_dir or str(DesktopTools._desktop_directory())),
                limit=arguments.get("limit", 100),
            )
        if name == "read_text_file":
            return DesktopTools.read_text_file(
                path=arguments.get("path", ""),
                directory=self.workspace_dir or str(Path.cwd()),
                max_chars=arguments.get("max_chars", 5500),
            )
        if name == "write_text_file":
            return DesktopTools.write_text_file(
                filename=arguments.get("filename", ""),
                content=arguments.get("content", ""),
                directory=self.workspace_dir,
            )
        if name == "get_active_window":
            return json.dumps(DesktopTools.active_window(), ensure_ascii=False)
        if name == "get_screen_info":
            return json.dumps(DesktopTools.screen_info(), ensure_ascii=False)
        if name == "screenshot":
            return DesktopTools.screenshot(
                filename=arguments.get("filename", ""),
                include_image=self.vision_enabled,
            )
        if name == "open_application":
            opened = DesktopTools.open_application(path=arguments.get("path", ""))
            text_to_type = arguments.get("text")
            if text_to_type is not None:
                if not isinstance(text_to_type, str):
                    return "Erro: o texto opcional precisa ser uma string."
                if "janela ativada" not in opened.casefold():
                    return f"{opened} Não digitei o texto porque não consegui confirmar que a janela do aplicativo recebeu foco."
                typed = DesktopTools.type_text(text=text_to_type)
                return f"{opened}\n{typed}"
            return opened
        if name == "powershell_execute":
            command = str(arguments.get("command", ""))
            if command_needs_confirmation(command) and not self._confirm_risky_command(command):
                return "Execução cancelada pelo usuário no terminal."
            return DesktopTools.powershell_execute(command)
        mapping = {
            "mouse_move": DesktopTools.mouse_move,
            "left_click": DesktopTools.left_click,
            "right_click": DesktopTools.right_click,
            "double_click": DesktopTools.double_click,
            "scroll": DesktopTools.scroll,
            "activate_window": DesktopTools.activate_window,
            "type_text": DesktopTools.type_text,
            "press_key": DesktopTools.press_key,
            "key_combination": DesktopTools.key_combination,
            "list_windows": DesktopTools.list_windows,
            "open_application": DesktopTools.open_application,
        }
        function = mapping.get(name)
        if not function:
            return f"Ferramenta desconhecida: {name}"
        try:
            return function(**arguments)
        except Exception as exc:
            return f"Falha em {name}: {type(exc).__name__}: {exc}"

    @staticmethod
    def _parse_arguments(raw_arguments: Any) -> dict[str, Any]:
        if isinstance(raw_arguments, dict):
            return raw_arguments
        if not isinstance(raw_arguments, str):
            raise ValueError("Argumentos ausentes ou em formato inválido.")
        parsed = json.loads(raw_arguments or "{}")
        if not isinstance(parsed, dict):
            raise ValueError("Os argumentos da ferramenta precisam ser um objeto JSON.")
        return parsed

    def run(self) -> list[dict[str, Any]]:
        console.print(Panel.fit(
            f"[bold cyan]Objetivo[/bold cyan]\n{self.goal}\n\n"
            f"[dim]Mode: {self.agent_profile['label']}  •  Provider: {self.provider.label}  •  Model: {self.model}[/dim]",
            border_style="cyan",
        ))
        for step in range(1, max(1, MAX_STEPS_PER_TASK) + 1):
            self.task_journal.begin_step(step)
            started = time.monotonic()
            try:
                with console.status(f"[bold cyan]NEXUS está analisando • etapa {step}/{MAX_STEPS_PER_TASK}[/bold cyan]", spinner="dots"):
                    response = self.call_ai()
                elapsed = time.monotonic() - started
                usage = response.get("usage")
                if isinstance(usage, dict):
                    input_tokens = usage.get("prompt_tokens", usage.get("input_tokens"))
                    output_tokens = usage.get("completion_tokens", usage.get("output_tokens"))
                    total_tokens = usage.get("total_tokens")
                    if input_tokens is not None or output_tokens is not None:
                        usage_line = f"Uso informado pelo provedor: entrada={input_tokens or '?'}, saída={output_tokens or '?'}, total={total_tokens or '?'} tokens."
                        console.print(f"[dim]{usage_line}[/dim]")
                        self._write_log(f"[TokenUsage] {usage_line}")
                message = response["choices"][0].get("message") or {}
                if not isinstance(message, dict):
                    raise RuntimeError("Formato de mensagem inválido recebido da API.")
                content = message.get("content")
                tool_calls = message.get("tool_calls") or []
                if len(tool_calls) > MAX_TOOL_CALLS_PER_STEP:
                    console.print(f"[yellow]Limite de {MAX_TOOL_CALLS_PER_STEP} chamadas por etapa; excedentes adiadas.[/yellow]")
                    tool_calls = tool_calls[:MAX_TOOL_CALLS_PER_STEP]
                    message["tool_calls"] = tool_calls
                # Preserve the assistant tool-call message exactly as returned by the provider.
                assistant_message = {key: value for key, value in message.items() if key in {"role", "content", "tool_calls", "refusal"}}
                assistant_message["role"] = "assistant"
                self.messages.append(assistant_message)
                console.print(f"[dim]NEXUS • resposta recebida em {elapsed:.1f}s • etapa {step}[/dim]")
                if content:
                    self._write_log(f"[NEXUS] {content}")
                    console.print(Panel(Text(str(content)), title="[bold green]NEXUS[/bold green]", border_style="green", padding=(0, 2)))
                if not tool_calls:
                    self._write_log("[Status] Turno concluído.")
                    self.task_journal.finish("completed", "Turno concluído sem ferramentas pendentes.")
                    return self.messages
                pending_images: list[str] = []
                for call in tool_calls:
                    function_info = call.get("function") or {}
                    name = function_info.get("name", "")
                    call_id = call.get("id")
                    try:
                        arguments = self._parse_arguments(function_info.get("arguments", "{}"))
                    except (ValueError, json.JSONDecodeError) as exc:
                        arguments = {}
                        result: Any = f"Argumentos inválidos para {name}: {exc}"
                    else:
                        if name == "type_text":
                            args_display = f"text=[oculto; {len(str(arguments.get('text', '')))} caracteres]"
                        elif name == "powershell_execute":
                            args_display = "command=[oculto por segurança]"
                        else:
                            args_display = json.dumps(arguments, ensure_ascii=False)
                        console.print(Text(f"  → {name} {args_display[:250]}"))
                        log_args = "[oculto]" if name in {"type_text", "powershell_execute"} else args_display
                        self._write_log(f"[Tool] {name}({log_args})")
                        try:
                            result = self.execute_tool(name, arguments)
                        except Exception as exc:
                            result = f"Erro ao executar {name}: {type(exc).__name__}: {exc}"
                    image_data_url = result.get("image_data_url") if isinstance(result, dict) else None
                    if isinstance(result, dict):
                        result_text = result.get("message", "Captura de tela concluída.")
                        if result.get("metadata"):
                            result_text += "\nMetadados medidos do Windows/tela: " + json.dumps(result["metadata"], ensure_ascii=False)
                        if result.get("image_dimensions"):
                            result_text += "\nDimensões reais da imagem: " + json.dumps(result["image_dimensions"], ensure_ascii=False)
                    else:
                        result_text = str(result)
                    console.print(Text(f"    ↳ {result_text[:700]}"))
                    private_output = name in {"read_text_file", "powershell_execute"}
                    logged_result = f"[saída omitida por privacidade; {len(result_text)} caracteres]" if private_output else redact_sensitive_text(result_text)
                    self._write_log(f"[Result] {logged_result}")
                    lowered_result = result_text.strip().lower()
                    action_ok = not lowered_result.startswith(("erro", "falha", "argumentos inválidos", "powershell retornou código"))
                    journal_result = logged_result if private_output else result_text
                    self.task_journal.record_action(name, arguments if isinstance(arguments, dict) else {}, journal_result, success=action_ok)
                    self.messages.append({
                        "role": "tool", "tool_call_id": call_id or f"nexus-{step}-{name}",
                        "name": name, "content": result_text[:6000],
                    })
                    if image_data_url:
                        pending_images.append(image_data_url)
                # All tool replies must immediately follow their assistant tool-call message.
                # Attach screenshots only after every tool reply has been added.
                if pending_images:
                    # Keep only the newest screenshot in the message history. This prevents
                    # large base64 payloads from accumulating and exceeding provider image limits.
                    self.messages = [
                        item for item in self.messages
                        if not (
                            item.get("role") == "user"
                            and isinstance(item.get("content"), list)
                            and any(part.get("type") == "image_url" for part in item["content"] if isinstance(part, dict))
                        )
                    ]
                    self.messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Imagem de tela capturada agora para análise visual, conforme /vision on. Os metadados textuais da ferramenta screenshot contêm medidas reais; use-os para distinguir janela ativa de janelas apenas visíveis."},
                            {"type": "image_url", "image_url": {"url": pending_images[-1]}},
                        ],
                    })
                self._write_log(f"[Step] {step} tool cycle completed.")
            except KeyboardInterrupt:
                self.task_journal.finish("interrupted", "Interrompida pelo usuário.")
                console.print("[yellow]Tarefa interrompida pelo usuário.[/yellow]")
                self._write_log("[Status] Interrompido pelo usuário.")
                return self.messages
            except Exception as exc:
                self.task_journal.finish("failed", f"{type(exc).__name__}: {exc}")
                console.print(Panel(Text(f"{type(exc).__name__}: {exc}"), title="[bold red]Erro no NEXUS[/bold red]", border_style="red"))
                self._write_log(f"[Error] {type(exc).__name__}: {exc}")
                return self.messages
        self.task_journal.finish("step_limit", "Limite de etapas atingido; revise o estado do computador antes de continuar.")
        console.print("[yellow]Limite de etapas atingido. Revise o estado do computador antes de continuar.[/yellow]")
        self._write_log("[Status] Limite de etapas atingido.")
        return self.messages
