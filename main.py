"""NEXUS interactive terminal interface."""
from __future__ import annotations

import os
import getpass
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

import requests
from PIL import Image
from rich.style import Style
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import config
from agent import MODES, NexusAgent
from catalog import extract_model_ids
from i18n import detect_language, language_name, tr
from task_recovery import TaskJournal
from model_test import run_model_test

console = Console()
BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "nexus_logo.png"


def render_logo(path: Path = LOGO_PATH, width: int = 82) -> None:
    """Render the prepared transparent pixel logo with true-color half blocks."""
    if not path.is_file():
        console.print(Align.center("[bold bright_blue]NEXUS[/bold bright_blue]"))
        return
    try:
        with Image.open(path) as source:
            image = source.convert("RGBA")
        terminal_width = max(30, console.size.width - 8)
        target_width = min(width, terminal_width)
        target_height = max(2, round(image.height * target_width / image.width))
        image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        pixels = image.load()

        for y in range(0, target_height, 2):
            line = Text()
            for x in range(target_width):
                top = pixels[x, y]
                bottom = pixels[x, y + 1] if y + 1 < target_height else (0, 0, 0, 0)
                top_visible = top[3] >= 24
                bottom_visible = bottom[3] >= 24
                if top_visible and bottom_visible:
                    style = Style(color=f"rgb({top[0]},{top[1]},{top[2]})", bgcolor=f"rgb({bottom[0]},{bottom[1]},{bottom[2]})")
                    line.append("▀", style=style)
                elif top_visible:
                    line.append("▀", style=Style(color=f"rgb({top[0]},{top[1]},{top[2]})"))
                elif bottom_visible:
                    line.append("▄", style=Style(color=f"rgb({bottom[0]},{bottom[1]},{bottom[2]})"))
                else:
                    line.append(" ")
            console.print(Align.center(line, vertical="middle"), soft_wrap=False)
    except Exception as exc:
        console.print(Align.center("[bold bright_blue]NEXUS[/bold bright_blue]"))
        console.print(f"[dim]Logo alternativa: {type(exc).__name__}[/dim]")


def read_hidden_secret(prompt: str) -> str:
    """Read a secret only from an interactive terminal, without echoing it."""
    if not sys.stdin.isatty():
        raise RuntimeError("A entrada segura exige um CMD/Terminal interativo. Abra o NEXUS diretamente no terminal.")
    return getpass.getpass(prompt)


class NexusSession:
    def __init__(self) -> None:
        self.language = detect_language()
        self.provider_name = config.DEFAULT_PROVIDER
        self.model = config.get_provider(self.provider_name).default_model
        self.mode_name = "operator"
        self.vision_enabled = False
        self.conversation: list[dict[str, Any]] | None = None
        self.workspace_dir: Path | None = None
        self.available_models: list[str] = []
        self.log_file = BASE_DIR / "nexus_logs" / "nexus_history.log"
        (BASE_DIR / "nexus_logs").mkdir(exist_ok=True)
        (BASE_DIR / "nexus_screenshots").mkdir(exist_ok=True)

    @property
    def provider(self):
        return config.get_provider(self.provider_name)

    def fetch_models(self) -> list[str]:
        provider = self.provider
        if provider.requires_api_key and not provider.api_key:
            raise RuntimeError("Configure a chave de API no arquivo .env antes de consultar os modelos.")
        headers = {"Accept": "application/json"}
        if provider.api_key:
            headers["Authorization"] = f"Bearer {provider.api_key}"
        endpoints = [provider.normalized_base_url() + "/models"]
        if provider.name == "ollama":
            # Ollama documents /api/tags as a cloud catalog endpoint too.
            # Use it only when the OpenAI-compatible catalog is unavailable/empty.
            endpoints.append("https://ollama.com/api/tags")

        errors: list[str] = []
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=(5, 12))
                if not response.ok:
                    errors.append(f"{endpoint}: HTTP {response.status_code}")
                    continue
                models = extract_model_ids(response.json(), provider.name)
                if models:
                    self.available_models = models
                    return models
                errors.append(f"{endpoint}: resposta sem IDs de modelos reconhecíveis")
            except (requests.RequestException, ValueError) as exc:
                errors.append(f"{endpoint}: {type(exc).__name__}: {exc}")

        self.available_models = []
        raise RuntimeError("Não foi possível obter o catálogo de modelos. " + " | ".join(errors))

    def render_welcome(self) -> None:
        console.clear()
        if config.SECURE_STORE_ERROR:
            console.print(Panel(
                "[yellow]As configurações protegidas não puderam ser lidas. "
                "As chaves salvas podem não estar disponíveis nesta sessão. "
                "Use /setup para reconfigurar após verificar sua conta do Windows.[/yellow]",
                title="Aviso de armazenamento seguro", border_style="yellow"
            ))
        render_logo()
        intro = Panel(
            Align.center(f"[bold white]{tr('tagline', self.language).upper()}[/bold white]\n[dim]{tr('subtitle', self.language)}[/dim]"),
            border_style="bright_blue", padding=(1, 4),
            title=f"[bold cyan]{tr('welcome', self.language)}[/bold cyan]",
            subtitle="[dim]NEXUS 1.1 • Cloud AI • Windows[/dim]",
        )
        console.print("\n", Align.center(intro))
        guide = (
            f"[bold]{tr('provider_step', self.language)}[/bold]\n"
            f"[cyan]/providers[/cyan]       {tr('provider_list', self.language)}\n"
            f"[cyan]/setup [provider][/cyan] {tr('setup_provider', self.language)}\n"
            f"[cyan]/provider <name>[/cyan] Select a cloud provider\n\n"
            f"[bold]{tr('model_step', self.language)}[/bold]\n"
            f"[cyan]/agents[/cyan]           {tr('fetch_models', self.language)}\n"
            f"[cyan]/agent 1[/cyan]          {tr('select_number', self.language)}\n"
            f"[cyan]/agent beam[/cyan]      {tr('select_id', self.language)}\n\n"
            f"[bold]{tr('mode_step', self.language)}[/bold]\n"
            f"[cyan]/modes[/cyan]            {tr('list_modes', self.language)}\n"
            f"[cyan]/mode operator[/cyan]   {tr('operator', self.language)}\n"
            f"[cyan]/mode planner[/cyan]    {tr('planner', self.language)}\n"
            f"[cyan]/mode chat[/cyan]       {tr('chat', self.language)}\n\n"
            f"[dim]{tr('other_commands', self.language)}[/dim]"
        )
        console.print(Panel(guide, title=f"[bold white]{tr('getting_started', self.language)}[/bold white]", border_style="dim blue"))
        self.render_status()
        console.print(f"\n[bold cyan]NEXUS[/bold cyan] [dim]· {tr('prompt', self.language)}[/dim]")

    def render_status(self) -> None:
        p = self.provider
        key_status = tr("configured", self.language) if p.api_key or not p.requires_api_key else tr("missing", self.language)
        vision = "available" if p.supports_vision(self.model) else "not supported by selected model"
        table = Table.grid(padding=(0, 2))
        table.add_column(style="dim")
        table.add_column()
        table.add_row(tr("mode", self.language), f"[cyan]{MODES[self.mode_name]['label']}[/cyan]")
        table.add_row(tr("provider", self.language), f"[cyan]{p.label}[/cyan]")
        table.add_row(tr("model", self.language), self.model)
        table.add_row(tr("api_key", self.language), f"[green]{key_status}[/green]" if p.api_key or not p.requires_api_key else f"[yellow]{key_status}[/yellow]")
        table.add_row(tr("vision", self.language), f"[green]{tr('on', self.language)}[/green]" if self.vision_enabled else f"[dim]{tr('off', self.language)}[/dim] ({vision})")
        table.add_row(tr("workspace", self.language), str(self.workspace_dir) if self.workspace_dir else tr("desktop_default", self.language))
        table.add_row(tr("language", self.language), f"{language_name(self.language)} ({self.language})")
        console.print(Panel(table, title=f"[bold]{tr('status_title', self.language)}[/bold]", border_style="blue"))

    def show_help(self) -> None:
        table = Table(title=tr("help_title", self.language), show_header=True, header_style="bold cyan")
        table.add_column(tr("command", self.language), style="cyan", no_wrap=True)
        table.add_column(tr("description", self.language))
        rows = [
            ("/providers", tr("cmd_providers", self.language)),
            ("/provider <name>", tr("cmd_provider", self.language)),
            ("/setup [provider]", "Configura chave, endpoint e modelo pelo CMD; a chave não aparece na tela."),
            ("/key set|remove [provider]", "Adiciona ou remove uma chave de API com entrada oculta."),
            ("/endpoint [https://...]", "Mostra ou altera o endpoint do provedor ativo."),
            ("/test", "Testa autenticação, endpoint e modelo com uma requisição curta."),
            ("/modeltest", "Avalia chat, JSON, contexto, tool calling e visão opcional sem executar ferramentas."),
            ("/agents", tr("cmd_agents", self.language)),
            ("/agent <number|id>", tr("cmd_agent", self.language)),
            ("/models", "Alias: /agents"),
            ("/modes", tr("cmd_modes", self.language)),
            ("/mode <name>", tr("cmd_mode", self.language)),
            ("/model <id>", tr("cmd_model", self.language)),
            ("/vision on|off", tr("cmd_vision", self.language)),
            ("/language auto|pt|en", tr("language_command", self.language)),
            ("/workspace [folder|off]", tr("cmd_workspace", self.language)),
            ("/status", tr("cmd_status", self.language)),
            ("/tasks", "Lista tarefas recentes e checkpoints salvos."),
            ("/resume <id>", "Retoma uma tarefa interrompida após revisão e confirmação; não repete ações automaticamente."),
            ("/clear", tr("cmd_clear", self.language)),
            ("/help", tr("cmd_help", self.language)),
            ("/exit", tr("cmd_exit", self.language)),
        ]
        for command, description in rows:
            table.add_row(command, description)
        console.print(table)

    def show_modes(self) -> None:
        table = Table(title=tr("modes_title", self.language), header_style="bold cyan")
        table.add_column(tr("mode", self.language))
        table.add_column(tr("description", self.language))
        table.add_column(tr("status_column", self.language))
        for name in MODES:
            description = tr(f"mode_{name}", self.language)
            table.add_row(name.title(), description, f"[green]{tr('status_selected', self.language)}[/green]" if name == self.mode_name else "")
        console.print(table)

    def show_providers(self) -> None:
        table = Table(title=tr("providers_title", self.language), header_style="bold cyan")
        table.add_column(tr("provider_column", self.language))
        table.add_column(tr("endpoint_column", self.language))
        table.add_column(tr("key_column", self.language))
        for name, provider in config.PROVIDERS.items():
            key_status = "OK" if provider.api_key or not provider.requires_api_key else "missing"
            table.add_row(f"{name}{'  ← active' if name == self.provider_name else ''}", provider.normalized_base_url(), "[green]OK[/green]" if key_status == "OK" else "[yellow]missing[/yellow]")
        console.print(table)

    def show_models(self) -> None:
        try:
            models = self.fetch_models()
        except Exception as exc:
            console.print(f"[yellow]Não foi possível consultar o catálogo: {exc}[/yellow]")
            console.print(f"Modelo configurado atualmente: [cyan]{self.model}[/cyan]")
            console.print("Confira a chave, endpoint e conexão; também é possível usar /agent <id-do-modelo>.")
            return
        table = Table(title=f"Modelos disponíveis • {self.provider.label}", header_style="bold cyan")
        table.add_column(tr("number_column", self.language), justify="right")
        table.add_column(tr("model_column", self.language))
        table.add_column(tr("status_column", self.language))
        for index, model_id in enumerate(models, 1):
            table.add_row(str(index), model_id, "[green]ativo[/green]" if model_id == self.model else "")
        console.print(table)
        console.print("Selecione com [cyan]/agent número[/cyan] ou [cyan]/agent model-id[/cyan].")

    def setup_provider(self, provider_name: str | None = None) -> None:
        name = (provider_name or self.provider_name).strip().lower()
        if name not in config.PROVIDERS:
            console.print("[yellow]Provedor desconhecido. Use /providers.[/yellow]")
            return
        current = config.get_provider(name)
        console.print(Panel(
            f"Provedor: [cyan]{current.label}[/cyan]\n"
            "A chave será digitada sem aparecer na tela e salva criptografada para sua conta do Windows.",
            title="Configuração segura do provedor", border_style="blue"
        ))
        try:
            entered_key = read_hidden_secret("Chave de API (Enter mantém a atual): ").strip()
            endpoint = console.input(f"Endpoint HTTPS [{current.normalized_base_url()}]: ").strip()
            model = console.input(f"ID do modelo [{current.default_model}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("[yellow]Configuração cancelada.[/yellow]")
            return
        except RuntimeError as exc:
            console.print(f"[yellow]{exc}[/yellow]")
            return
        endpoint = endpoint or current.normalized_base_url()
        model = model or current.default_model
        parsed = urlsplit(endpoint)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            console.print("[yellow]Endpoint inválido. Informe uma URL HTTPS sem usuário, senha, query ou fragmento.[/yellow]")
            return
        if not current.api_key and not entered_key:
            console.print("[yellow]Nenhuma chave informada. Use /key set para adicionar uma.[/yellow]")
            return
        try:
            settings = {"model": model, "base_url": endpoint}
            if entered_key:
                settings["api_key"] = entered_key
            updated = config.save_provider_settings(name, **settings)
            config.save_default_provider(name)
        except Exception as exc:
            console.print(f"[red]Não foi possível salvar a configuração: {type(exc).__name__}: {exc}[/red]")
            return
        self.provider_name = name
        self.model = updated.default_model
        self.available_models = []
        self.vision_enabled = False
        self.reset_conversation()
        console.print(f"[green]Configuração salva para {updated.label}. Chave: {'configurada' if updated.api_key else 'ausente'}.[/green]")
        console.print("Use [cyan]/test[/cyan] para verificar a conexão e [cyan]/agents[/cyan] para consultar os modelos.")

    def manage_key(self, argument: str) -> None:
        parts = argument.split()
        action = parts[0].lower() if parts else "status"
        name = parts[1].lower() if len(parts) > 1 else self.provider_name
        if name not in config.PROVIDERS:
            console.print("[yellow]Provedor desconhecido. Use /providers.[/yellow]")
            return
        current = config.get_provider(name)
        if action in {"status", "show"}:
            console.print(f"Chave de {current.label}: {'configurada' if current.api_key else 'ausente'}. O valor nunca é exibido.")
        elif action in {"set", "add"}:
            try:
                value = read_hidden_secret(f"Nova chave para {current.label} (entrada oculta): ").strip()
            except (KeyboardInterrupt, EOFError):
                console.print("[yellow]Operação cancelada.[/yellow]")
                return
            except RuntimeError as exc:
                console.print(f"[yellow]{exc}[/yellow]")
                return
            if not value:
                console.print("[yellow]Nenhuma chave foi informada; nada foi alterado.[/yellow]")
                return
            try:
                updated = config.save_provider_settings(name, api_key=value)
                console.print(f"[green]Chave salva com proteção do Windows para {updated.label}.[/green]")
            except Exception as exc:
                console.print(f"[red]Não foi possível salvar a chave: {type(exc).__name__}: {exc}[/red]")
        elif action in {"remove", "delete", "clear"}:
            answer = console.input(f"Remover a chave salva de {current.label}? [s/N]: ").strip().lower()
            if answer not in {"s", "sim", "y", "yes"}:
                console.print("[dim]Cancelado.[/dim]")
                return
            try:
                config.save_provider_settings(name, api_key="")
                console.print(f"[green]Chave salva removida de {current.label}.[/green]")
            except Exception as exc:
                console.print(f"[red]Não foi possível remover a chave: {type(exc).__name__}: {exc}[/red]")
        else:
            console.print("Use /key status, /key set [provider] ou /key remove [provider].")

    def manage_endpoint(self, argument: str) -> None:
        current = self.provider
        if not argument:
            console.print(f"Endpoint de {current.label}: [cyan]{current.normalized_base_url()}[/cyan]")
            return
        parsed = urlsplit(argument)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            console.print("[yellow]Informe uma URL HTTPS válida, sem credenciais, query ou fragmento.[/yellow]")
            return
        try:
            updated = config.save_provider_settings(self.provider_name, base_url=argument)
            self.available_models = []
            self.reset_conversation()
            console.print(f"[green]Endpoint atualizado: {updated.normalized_base_url()}[/green]")
        except Exception as exc:
            console.print(f"[red]Não foi possível salvar o endpoint: {type(exc).__name__}: {exc}[/red]")

    def test_connection(self) -> None:
        provider = self.provider
        if provider.requires_api_key and not provider.api_key:
            console.print("[yellow]Chave ausente. Use /key set ou /setup.[/yellow]")
            return
        url = provider.normalized_base_url() + "/chat/completions"
        headers = {"Authorization": f"Bearer {provider.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "Responda somente: OK"}],
            "max_tokens": 8,
            "temperature": 0,
        }
        console.print(f"Testando [cyan]{provider.label}[/cyan] • [dim]{self.model}[/dim]...")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=(8, 25))
            if not response.ok:
                from providers import sanitized_api_error
                console.print(f"[red]{sanitized_api_error(response.status_code, response.text)}[/red]")
                return
            data = response.json()
            answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            console.print(f"[green]Conexão e autenticação aprovadas.[/green] Resposta: {str(answer)[:120] or '(resposta vazia)'}")
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
            console.print(f"[red]Falha no teste: {type(exc).__name__}: {exc}[/red]")

    def run_modeltest(self) -> None:
        provider = self.provider
        if provider.requires_api_key and not provider.api_key:
            console.print("[yellow]Chave ausente. Use /key set ou /setup antes do ModelTest.[/yellow]")
            return
        console.print(Panel(
            "O ModelTest fará cinco verificações (até seis chamadas se a visão for aprovada) e pode consumir a cota da API. "
            "Chamadas de ferramentas serão apenas inspecionadas, nunca executadas.",
            title="ModelTest • confirmação", border_style="blue"
        ))
        if console.input("Continuar? [s/N]: ").strip().lower() not in {"s", "sim", "y", "yes"}:
            console.print("[dim]ModelTest cancelado.[/dim]")
            return
        image_data_url = None
        if provider.supports_vision(self.model):
            if console.input("Enviar uma captura da tela atual ao provedor para testar visão? Feche antes qualquer janela privada. [s/N]: ").strip().lower() in {"s", "sim", "y", "yes"}:
                try:
                    from tools import DesktopTools
                    screenshot = DesktopTools.screenshot(filename="modeltest_vision.jpg", include_image=True)
                    image_data_url = screenshot.get("image_data_url")
                except Exception as exc:
                    console.print(f"[yellow]Falha ao capturar a tela: {type(exc).__name__}[/yellow]")
        results = run_model_test(provider, self.model, image_data_url=image_data_url)
        table = Table(title=f"ModelTest • {provider.label} • {self.model}", header_style="bold cyan")
        table.add_column("Teste")
        table.add_column("Resultado")
        table.add_column("Tempo", justify="right")
        table.add_column("Detalhe")
        for item in results:
            status = item["status"]
            style = {"PASS": "green", "PARTIAL": "yellow", "FAIL": "red", "SKIP": "dim"}.get(status, "white")
            table.add_row(item["name"], f"[{style}]{status}[/{style}]", f"{item['latency']:.2f}s", item["detail"])
        console.print(table)
        passed = sum(item["status"] == "PASS" for item in results)
        partial = sum(item["status"] == "PARTIAL" for item in results)
        console.print(f"Resumo: {passed} aprovados • {partial} parciais • {len(results) - passed - partial} falhos/não testados.")
        console.print("[dim]A identidade do provedor/modelo vem da configuração local, não da autoidentificação verbal do modelo.[/dim]")

    def resume_task(self, task_id_prefix: str) -> None:
        prefix = task_id_prefix.strip().lower()
        if len(prefix) < 6:
            console.print("[yellow]Informe ao menos 6 caracteres do ID exibido por /tasks.[/yellow]")
            return
        records = TaskJournal.recent(limit=50)
        matches = [item for item in records if str(item.get("task_id", "")).lower().startswith(prefix)]
        if not matches:
            console.print("[yellow]Nenhuma tarefa corresponde a esse ID. Use /tasks para consultar os IDs recentes.[/yellow]")
            return
        if len(matches) > 1:
            console.print("[yellow]ID ambíguo. Informe mais caracteres do ID.[/yellow]")
            return
        record = matches[0]
        status = str(record.get("status", ""))
        if status not in {"running", "interrupted", "failed", "step_limit"}:
            console.print(f"[yellow]A tarefa está com estado '{status}' e não pode ser retomada por este fluxo.[/yellow]")
            return
        actions = record.get("actions", [])
        completed = [str(item.get("name", "ação")) for item in actions if isinstance(item, dict) and item.get("success")]
        uncertain = [str(item.get("name", "ação")) for item in actions if isinstance(item, dict) and not item.get("success")]
        console.print(Panel(
            f"Objetivo: {str(record.get('goal', ''))[:800]}\n"
            f"Estado: {status} • Etapa registrada: {record.get('step', 0)}\n"
            f"Ações concluídas registradas: {len(completed)}\n"
            f"Ações com resultado incerto: {len(uncertain)}",
            title=f"Revisão da tarefa {str(record.get('task_id', ''))[:8]}", border_style="yellow"
        ))
        if completed:
            console.print("[dim]Ações já registradas como concluídas: " + ", ".join(completed[-12:]) + "[/dim]")
        if uncertain:
            console.print("[yellow]Ações que precisam de inspeção antes de qualquer repetição: " + ", ".join(uncertain[-12:]) + "[/yellow]")
        workspace = record.get("workspace")
        if workspace and not Path(str(workspace)).is_dir():
            console.print("[yellow]O workspace salvo não existe mais; a retomada usará o workspace padrão.[/yellow]")
            workspace = None
        if console.input("Criar uma nova execução vinculada a esse checkpoint? [s/N]: ").strip().lower() not in {"s", "sim", "y", "yes"}:
            console.print("[dim]Retomada cancelada.[/dim]")
            return
        completed_summary = ", ".join(completed[-20:]) if completed else "nenhuma ação marcada como concluída"
        uncertain_summary = ", ".join(uncertain[-20:]) if uncertain else "nenhuma ação com resultado incerto"
        resume_goal = (
            "RETOMADA COM REVISÃO MANUAL. Não reinicie a tarefa do zero.\n"
            f"Objetivo original: {record.get('goal', '')}\n"
            f"Ações registradas como concluídas (não repetir): {completed_summary}.\n"
            f"Ações com resultado incerto (inspecionar o estado atual antes de qualquer decisão): {uncertain_summary}.\n"
            "Primeiro verifique o estado atual do computador e dos arquivos. Não repita cliques, digitação, gravações ou comandos "
            "apenas porque o checkpoint foi interrompido. Se uma ação puder ter ocorrido parcialmente, peça confirmação antes de refazê-la. "
            "Continue somente com etapas que ainda não foram concluídas. O histórico anterior é um resumo do journal, não uma restauração "
            "integral da conversa nem uma garantia sobre o estado atual do sistema."
        )
        agent = NexusAgent(
            goal=resume_goal,
            provider=self.provider,
            model=self.model,
            mode_name=self.mode_name,
            vision_enabled=False,
            log_file=self.log_file,
            conversation=None,
            workspace_dir=workspace,
            language=self.language,
            resume_from_task_id=str(record.get("task_id", "")),
        )
        self.conversation = agent.run()
        self.workspace_dir = Path(agent.workspace_dir) if agent.workspace_dir else None

    def initialize_project_instructions(self) -> None:
        target = BASE_DIR / "NEXUS.md"
        if target.exists():
            console.print("[yellow]NEXUS.md já existe. Nenhum arquivo foi sobrescrito.[/yellow]")
            return
        template = "# NEXUS project instructions\n\n## Working rules\n- Inspect relevant files before making changes.\n- Keep changes scoped to the requested task.\n- Run available tests after editing.\n- Never claim a test passed unless it was actually run.\n- Ask for local confirmation before destructive or irreversible actions.\n"
        target.write_text(template, encoding="utf-8")
        console.print(f"[green]Criado: {target.name}[/green]")

    def reset_conversation(self) -> None:
        self.conversation = None

    def handle_command(self, raw: str) -> bool:
        parts = raw.strip().split(maxsplit=1)
        command = parts[0].lower()
        argument = parts[1].strip() if len(parts) > 1 else ""
        if command in {"/exit", "/quit", "/sair"}:
            console.print(f"[dim]{tr('session_ended', self.language)}[/dim]")
            return False
        if command in {"/help", "/ajuda", "/?"}:
            self.show_help()
        elif command in {"/clear", "/cls", "/limpar"}:
            self.render_welcome()
        elif command in {"/agents", "/models"}:
            self.show_models()
        elif command == "/agent":
            if not argument:
                self.show_models()
            else:
                selected = argument
                if selected.isdigit():
                    if not self.available_models:
                        try:
                            self.fetch_models()
                        except Exception as exc:
                            console.print(f"[yellow]Não foi possível buscar a lista para seleção numérica: {exc}[/yellow]")
                            return True
                    index = int(selected) - 1
                    if not 0 <= index < len(self.available_models):
                        console.print("[yellow]Número fora da lista. Use /agents para consultar os modelos.[/yellow]")
                        return True
                    selected = self.available_models[index]
                elif self.available_models:
                    match = next((item for item in self.available_models if item.casefold() == selected.casefold()), None)
                    if match is None:
                        console.print("[yellow]Esse ID não aparece no catálogo atual. Digite /agents para conferir os IDs disponíveis.[/yellow]")
                        return True
                    selected = match
                self.model = selected
                try:
                    config.save_provider_settings(self.provider_name, model=selected)
                except Exception as exc:
                    console.print(f"[yellow]Modelo selecionado nesta sessão, mas não foi possível salvá-lo: {type(exc).__name__}[/yellow]")
                self.vision_enabled = False
                self.reset_conversation()
                console.print(f"[green]Modelo/agente selecionado: {self.model}[/green]")
        elif command in {"/model", "/modelo"}:
            self.handle_command("/agent" + (f" {argument}" if argument else ""))
        elif command in {"/modes", "/profiles"}:
            self.show_modes()
        elif command in {"/mode", "/profile"}:
            if argument not in MODES:
                console.print("[yellow]Use /mode operator, /mode planner ou /mode chat.[/yellow]")
            else:
                self.mode_name = argument
                self.reset_conversation()
                console.print(f"[green]Modo selecionado: {MODES[argument]['label']}[/green]")
        elif command == "/providers":
            self.show_providers()
        elif command == "/setup":
            self.setup_provider(argument or None)
        elif command == "/key":
            self.manage_key(argument)
        elif command == "/endpoint":
            self.manage_endpoint(argument)
        elif command == "/test":
            self.test_connection()
        elif command == "/modeltest":
            self.run_modeltest()
        elif command == "/provider":
            if argument.lower() not in config.PROVIDERS:
                console.print("[yellow]Use /providers para ver os provedores em nuvem disponíveis.[/yellow]")
            else:
                self.provider_name = argument.lower()
                self.model = self.provider.default_model
                try:
                    config.save_default_provider(self.provider_name)
                except Exception as exc:
                    console.print(f"[yellow]Provedor selecionado nesta sessão, mas não foi possível salvar como padrão: {type(exc).__name__}[/yellow]")
                self.available_models = []
                self.vision_enabled = False
                self.reset_conversation()
                console.print(f"[green]Provedor selecionado: {self.provider.label} • modelo padrão: {self.model}[/green]")
        elif command == "/resume":
            self.resume_task(argument)
        elif command == "/tasks":
            recent = TaskJournal.recent(limit=8)
            if not recent:
                console.print("[dim]Nenhum checkpoint de tarefa encontrado.[/dim]")
            else:
                table = Table(title="Tarefas recentes • checkpoints", header_style="bold cyan")
                table.add_column("ID")
                table.add_column("Estado")
                table.add_column("Etapa")
                table.add_column("Objetivo")
                for item in recent:
                    table.add_row(str(item.get("task_id", ""))[:8], str(item.get("status", "")), str(item.get("step", 0)), str(item.get("goal", ""))[:90])
                console.print(table)
                console.print("[dim]Ações de computador não são repetidas automaticamente. Revise o checkpoint antes de iniciar uma nova execução.[/dim]")
        elif command == "/vision":
            value = argument.lower()
            if value in {"on", "ativar", "1"}:
                if not self.provider.supports_vision(self.model):
                    console.print("[yellow]O modelo atual não está cadastrado como compatível com imagens. Troque o modelo primeiro.[/yellow]")
                else:
                    self.vision_enabled = True
                    console.print("[green]Visão ativada. Screenshots serão enviados ao provedor configurado quando a ferramenta screenshot for chamada.[/green]")
            elif value in {"off", "desativar", "0"}:
                self.vision_enabled = False
                console.print("[green]Visão desativada. Screenshots ficarão apenas no computador.[/green]")
            else:
                console.print(f"Visão: {'ON' if self.vision_enabled else 'OFF'}. Use /vision on ou /vision off.")
        elif command == "/workspace":
            if not argument:
                current = str(self.workspace_dir) if self.workspace_dir else "Área de Trabalho (padrão)"
                console.print(f"Workspace atual: [cyan]{current}[/cyan]")
            elif argument.lower() in {"off", "none", "default", "padrao", "padrão"}:
                self.workspace_dir = None
                console.print("[green]Workspace removido. Arquivos .txt voltarão para a Área de Trabalho.[/green]")
            else:
                raw_path = argument.strip().strip('"')
                candidate = Path(raw_path).expanduser()
                if not candidate.is_absolute():
                    candidate = (Path.cwd() / candidate)
                candidate = candidate.resolve()
                if not candidate.exists() or not candidate.is_dir():
                    console.print(f"[yellow]A pasta não existe ou não é um diretório: {candidate}[/yellow]")
                else:
                    self.workspace_dir = candidate
                    console.print(f"[green]Workspace definido: {candidate}[/green]")
        elif command in {"/language", "/lang", "/idioma"}:
            value = argument.lower().replace("_", "-")
            if value in {"pt", "pt-br", "português", "portugues"}:
                self.language = "pt"
                self.reset_conversation()
                console.print(f"[green]{tr('language_set', self.language)}[/green]")
            elif value in {"en", "en-us", "english"}:
                self.language = "en"
                self.reset_conversation()
                console.print(f"[green]{tr('language_set', self.language)}[/green]")
            elif value in {"auto", ""}:
                self.language = detect_language("auto")
                self.reset_conversation()
                console.print(f"[green]{tr('language_auto', self.language)}: {language_name(self.language)}[/green]")
            else:
                console.print(f"[yellow]{tr('language_invalid', self.language)}[/yellow]")
            self.render_status()
        elif command == "/status":
            self.render_status()
        elif command == "/init":
            self.initialize_project_instructions()
        else:
            console.print(f"[red]{tr('unknown_command', self.language, command=command)}[/red]")
        return True

    def run(self) -> None:
        self.render_welcome()
        while True:
            try:
                user_input = console.input("[bold cyan]› [/bold cyan]").strip()
                if not user_input:
                    continue
                if user_input.startswith("/"):
                    if not self.handle_command(user_input):
                        break
                    continue
                agent = NexusAgent(
                    goal=user_input,
                    provider=self.provider,
                    model=self.model,
                    mode_name=self.mode_name,
                    vision_enabled=self.vision_enabled,
                    log_file=self.log_file,
                    conversation=self.conversation,
                    workspace_dir=self.workspace_dir,
                    language=self.language,
                )
                self.conversation = agent.run()
                self.workspace_dir = Path(agent.workspace_dir) if agent.workspace_dir else None
            except KeyboardInterrupt:
                console.print(f"\n[yellow]{tr('input_cancelled', self.language)}[/yellow]")
            except EOFError:
                break
            except Exception as exc:
                console.print(f"[bold red]Erro: {type(exc).__name__}: {exc}[/bold red]")


def launch_in_windows_terminal() -> None:
    if os.name != "nt" or "WT_SESSION" in os.environ or "--no-wt" in sys.argv:
        return
    terminal = shutil.which("wt.exe") or shutil.which("wt")
    if not terminal:
        return
    script = str(Path(__file__).resolve())
    try:
        subprocess.Popen([terminal, "-w", "0", "nt", "--title", "NEXUS | Computer Use Agent", sys.executable, script, "--no-wt"], cwd=str(BASE_DIR))
        raise SystemExit(0)
    except OSError:
        return


def main() -> None:
    launch_in_windows_terminal()
    NexusSession().run()


if __name__ == "__main__":
    main()
