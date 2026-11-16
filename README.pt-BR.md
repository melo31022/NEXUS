# NEXUS 1.1

**Agente de uso do computador para Windows, desenvolvido em Python e conectado a provedores de IA na nuvem.**

O NEXUS interpreta pedidos, planeja tarefas e pode interagir com o Windows usando ferramentas locais. A inferência de IA é feita exclusivamente nos provedores em nuvem selecionados; o projeto não executa modelos localmente.

## Recursos

- Provedores em nuvem: Ollama Cloud, Groq Cloud, OpenRouter, Cerebras, Together AI e DeepSeek.
- Catálogo de modelos consultado no provedor selecionado.
- Modos Chat, Planner e Operator.
- Ferramentas de mouse, teclado, janelas, screenshots, listagem e leitura controlada de arquivos de texto e PowerShell.
- Workspace selecionável.
- Visão opcional para modelos explicitamente configurados como compatíveis.
- Token Guard: estimativa de contexto, compactação de histórico e limites de saída/chamadas de ferramentas.
- Checkpoints persistentes e comando `/tasks` para consultar tarefas recentes.
- Retentativas limitadas para erros HTTP transitórios, respeitando `Retry-After`.
- Interface em português brasileiro e inglês.

A compatibilidade com ferramentas e imagens varia por provedor e modelo. A presença de um modelo no catálogo não garante suporte a todas as funções.

## Requisitos

- Windows 10 ou Windows 11.
- Python 3.11 ou mais recente.
- Conexão com a internet.
- Chave de API de um provedor em nuvem compatível.

## Instalação rápida (CMD)

Os comandos abaixo são para o **Prompt de Comando (CMD)** do Windows.

1. Baixe o ZIP da branch `dev-1.1` no GitHub e extraia a pasta.
2. Abra o CMD dentro da pasta extraída.
3. Execute:

   ```cmd
   py -3.11 iniciar.py
   ```

4. Na primeira execução, o inicializador cria o ambiente virtual, instala as dependências e cria `.env` a partir de `.env.example`.
5. Inicie o NEXUS e execute `/setup` para configurar provedor, chave, endpoint e modelo diretamente no CMD. A chave é digitada sem aparecer na tela e armazenada criptografada pelo Windows.
6. Se preferir, use `/key set`, `/endpoint`, `/provider` e `/agent`. Execute `/test` para testar a conexão. O arquivo `.env` continua disponível como método alternativo para configurações antigas.

## Instalação manual (CMD)

Execute os comandos dentro da pasta do projeto:

```cmd
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python.exe main.py
```

## Provedores

Defina `NEXUS_PROVIDER` em `.env` com um dos nomes:

- `ollama`
- `groq`
- `openrouter`
- `cerebras`
- `together`
- `deepseek`

Configure a variável de chave correspondente, por exemplo `GROQ_API_KEY` ou `OPENROUTER_API_KEY`. Consulte [docs/PROVIDERS.md](docs/PROVIDERS.md) para endpoints, variáveis e limitações.

Nunca publique o arquivo `.env` nem compartilhe suas chaves de API.

## Comandos principais

| Comando | Função |
|---|---|
| `/providers` | Lista provedores disponíveis. |
| `/setup [provider]` | Configura chave, endpoint e modelo pelo CMD. |
| `/key status\|set\|remove [provider]` | Consulta, adiciona ou remove uma chave sem exibi-la. |
| `/endpoint [URL]` | Consulta ou altera o endpoint HTTPS. |
| `/test` | Testa autenticação e uma resposta curta do modelo selecionado. |
| `/modeltest` | Avalia chat, JSON, contexto, tool calling e visão opcional. |
| `/provider <nome>` | Seleciona um provedor. |
| `/agents` ou `/models` | Consulta o catálogo de modelos. |
| `/agent <número ou id>` | Seleciona um modelo. |
| `/mode operator` | Ativa o modo de operação do computador. |
| `/mode planner` | Planeja sem executar ações. |
| `/mode chat` | Conversa sem ferramentas do computador. |
| `/vision on` e `/vision off` | Controla o envio de screenshots. |
| `/workspace [pasta]` | Mostra ou seleciona o workspace. |
| `/tasks` | Lista checkpoints de tarefas recentes. |
| `/status` | Mostra a configuração atual. |
| `/help` | Exibe a ajuda. |
| `/exit` | Encerra o NEXUS. |

## ModelTest

Use `/modeltest` para executar chamadas reais de avaliação ao modelo ativo. O comando pede confirmação porque pode consumir a cota da API. Ele verifica chat, JSON, contexto curto e emissão de tool calls sem executar ferramentas. Se o modelo estiver cadastrado para visão, o NEXUS pede um segundo consentimento antes de capturar e enviar a tela. A autoidentificação verbal do modelo não é usada como prova de identidade. Consulte [docs/MODELTEST.md](docs/MODELTEST.md).

## Token Guard

O Token Guard utiliza uma estimativa aproximada baseada no tamanho das mensagens, não um tokenizer exato de cada provedor. Ajuste `NEXUS_MAX_CONTEXT_TOKENS`, `NEXUS_MAX_OUTPUT_TOKENS`, `NEXUS_MAX_TOOL_CALLS_PER_STEP`, `NEXUS_MAX_STEPS` e `NEXUS_REQUEST_TIMEOUT` no arquivo `.env`.

## Recuperação de tarefas

O NEXUS grava checkpoints JSON em `nexus_tasks/`. Use `/tasks` para consultar o estado e as ações registradas. Por segurança, cliques, digitação, comandos PowerShell e gravações de arquivos não são repetidos automaticamente após uma interrupção. Revise o estado atual do computador antes de continuar manualmente. Consulte [docs/TASK_RECOVERY.md](docs/TASK_RECOVERY.md).

## Testes e limitações

Os testes unitários e a compilação Python são executados pelo GitHub Actions em Ubuntu com Python 3.11. Isso não substitui testes de aceitação no Windows. Autenticação real, catálogo de modelos, chamadas de ferramentas, visão e automação da área de trabalho precisam ser validados com cada conta/provedor e em Windows, inclusive Windows ARM64.

O NEXUS prioriza segurança, transparência, baixo consumo local e controle do usuário.
