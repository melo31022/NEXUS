# NEXUS 1.0

<p align="center"><img src="assets/nexus_logo.png" alt="NEXUS" width="520"></p>

**NEXUS** é um agente de uso do computador para Windows, com IA executada exclusivamente em provedores hospedados na nuvem. Ele pode observar a área de trabalho, planejar tarefas, operar mouse e teclado, executar comandos PowerShell e verificar resultados. Nenhum modelo de linguagem é executado localmente.

[Read this documentation in English](README.md).

## Destaques

- **Provedores em nuvem:** Ollama Cloud e Groq Cloud, com endpoints HTTPS fixos.
- **Catálogo dinâmico:** consulta os modelos disponíveis com `/agents` e seleciona com `/agent`.
- **Três modos:** `operator`, `planner` e `chat`.
- **Ferramentas do Windows:** mouse, teclado, capturas de tela, janelas, abertura de aplicativos e PowerShell.
- **Visão opcional:** capturas só são enviadas ao provedor quando `/vision on` está ativo e o modelo selecionado aceita imagens.
- **Workspace:** mantém os arquivos do projeto na pasta escolhida durante a sessão.
- **Metadados do Windows:** resolução e janela em primeiro plano são consultadas separadamente da interpretação visual do modelo.
- **Confirmações de segurança:** comandos PowerShell potencialmente destrutivos exigem confirmação local. As verificações são heurísticas, não um sandbox.

## Requisitos

- Windows 10 ou Windows 11 com sessão de usuário aberta.
- Python 3.11 ou mais recente.
- Conexão com a internet e chave de API do provedor escolhido.

## Início rápido

1. Baixe e extraia o projeto.
2. Abra a pasta `nexus`.
3. Se o Windows bloquear o arquivo `.bat`, use o método Python abaixo: abra o PowerShell nessa pasta e execute `py -3.11 iniciar.py`.
4. Na primeira execução, o inicializador Python cria o ambiente virtual, instala as dependências e cria `.env` a partir de `.env.example`.
5. Abra `.env`, adicione a chave do provedor e execute `py -3.11 iniciar.py` novamente.

O arquivo `run_nexus.bat` continua disponível como alternativa, mas não é necessário.

A primeira instalação precisa de internet e pode levar alguns minutos. Nas próximas inicializações, o ambiente virtual será reutilizado.

### Inicialização pelo Python (recomendada se o Windows bloquear o BAT)

Abra o PowerShell na pasta `nexus` e execute:

```powershell
py -3.11 iniciar.py
```

Se o comando `py` não existir, use `python iniciar.py` (desde que `python --version` mostre 3.11 ou mais recente). O inicializador não precisa de permissões de administrador nem de alterar a política de execução do PowerShell.

### Instalação manual

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe main.py
```

## Configuração dos provedores

Edite `.env`. Nunca envie esse arquivo ao GitHub nem compartilhe seu conteúdo.

### Ollama Cloud

```dotenv
NEXUS_PROVIDER=ollama
OLLAMA_API_KEY=sua_chave_ollama
OLLAMA_MODEL=beam
```

### Groq Cloud

```dotenv
NEXUS_PROVIDER=groq
GROQ_API_KEY=sua_chave_groq
GROQ_MODEL=openai/gpt-oss-120b
```

O catálogo depende da disponibilidade do provedor e do acesso da conta. Um modelo aparecer em `/agents` não garante suporte a chamadas de ferramentas ou entrada de imagens.

## Idioma automático

`NEXUS_LANGUAGE=auto` detecta o idioma das configurações regionais do Windows. Também é possível definir `NEXUS_LANGUAGE=pt` ou `NEXUS_LANGUAGE=en` no `.env`, ou alterar o idioma durante a execução:

```text
/language auto
/language pt
/language en
```

A interface possui traduções em português e inglês. O agente usa o idioma da interface como preferência, mas também detecta o idioma de cada mensagem e normalmente responde no mesmo idioma. Um pedido explícito de outro idioma tem prioridade.

## Comandos

| Comando | Função |
|---|---|
| `/providers` | Lista os provedores em nuvem. |
| `/provider ollama` ou `/provider groq` | Seleciona o provedor. |
| `/agents` ou `/models` | Consulta o catálogo de modelos. |
| `/agent <número\|id>` | Seleciona o modelo. |
| `/modes` | Lista os modos de operação. |
| `/mode operator` | Habilita ferramentas do computador. |
| `/mode planner` | Planeja sem executar ações. |
| `/mode chat` | Conversa sem ferramentas. |
| `/language auto\|pt\|en` | Detecta ou altera o idioma. |
| `/vision on` / `/vision off` | Liga/desliga o envio de capturas ao modelo. |
| `/workspace` | Mostra a pasta de trabalho atual. |
| `/workspace <pasta>` | Define uma pasta existente como workspace. |
| `/workspace off` | Volta a usar a Área de Trabalho como destino padrão. |
| `/status` | Mostra a configuração atual. |
| `/init` | Cria um `NEXUS.md` sem sobrescrever um existente. |
| `/help` | Mostra a ajuda. |
| `/clear` | Limpa o terminal e redesenha a tela inicial. |
| `/exit` | Encerra o NEXUS. |

## Workspace

Defina uma pasta com `/workspace C:\Users\Voce\Desktop\MeuProjeto`. Ela precisa existir. Durante uma tarefa, o agente também pode definir o workspace após criar ou identificar a pasta principal do projeto. A configuração dura até o encerramento do processo. Se nenhum workspace estiver definido, a ferramenta dedicada de arquivos `.txt` usa a Área de Trabalho. Ela recebe apenas um nome de arquivo e se recusa a sobrescrever arquivos existentes.

## Visão e metadados do Windows

A visão começa desligada. Com `/vision on`, uma captura solicitada pelo agente é salva localmente e enviada ao provedor somente se o modelo estiver configurado como compatível com imagens. Capturas podem conter informações privadas; feche páginas e documentos sensíveis antes de ativar esse recurso.

A ferramenta `get_active_window` consulta a janela em primeiro plano, seu título, PID e retângulo. `get_screen_info` retorna a resolução medida e os metadados da janela ativa. O modelo ainda interpreta os pixels; os metadados do Windows são fornecidos separadamente.

Beam é um modelo de texto e não deve ser usado para análise de imagens. Confirme o suporte a imagens e chamadas de ferramentas com o provedor antes de selecionar um modelo para Operator.

## Segurança e privacidade

- Mantenha as chaves em `.env`. O repositório ignora `.env`, logs, capturas, ambientes virtuais e arquivos de cache.
- O NEXUS opera com as permissões da conta Windows atual. Não execute como Administrador sem necessidade.
- O fail-safe do PyAutoGUI permanece ativo; mover o cursor ao canto superior esquerdo interrompe ações do PyAutoGUI.
- Comandos PowerShell classificados como potencialmente destrutivos exigem confirmação local, mas as regras são heurísticas e não constituem uma fronteira de segurança ou sandbox.
- Capturas são enviadas ao provedor somente com visão ativada e modelo compatível.
- Histórico e workspace ficam na memória do processo. Reiniciar o NEXUS inicia uma nova sessão.
- Revise comandos e resultados. Uma chamada de ferramenta, sozinha, não prova que uma ação foi concluída.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O GitHub Actions também executa os testes no Windows com Python 3.11. Testes automatizados não substituem a validação com credenciais reais, chamadas aos provedores e uma sessão gráfica do Windows.

## Licença

Ainda não foi escolhida uma licença. Até que uma seja adicionada, aplicam-se as regras padrão de direitos autorais; tornar o repositório público não concede automaticamente permissão de reutilização ou redistribuição. Escolha uma licença antes de apresentar o projeto como open source.
