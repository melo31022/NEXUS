# NEXUS 1.1

**Agente de uso do computador para Windows, desenvolvido em Python e conectado a provedores de IA na nuvem.**

O NEXUS interpreta pedidos, planeja tarefas e pode interagir com o Windows usando ferramentas locais. A inferência de IA é feita exclusivamente nos provedores em nuvem selecionados; o projeto não executa modelos localmente.

## Recursos

- Provedores em nuvem: Ollama Cloud, Groq Cloud, OpenRouter, Cerebras, Together AI e DeepSeek.
- Catálogo de modelos consultado no provedor selecionado.
- Modos Chat, Planner e Operator.
- Ferramentas de mouse, teclado, janelas, screenshots, arquivos e PowerShell.
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

## Instalação rápida

1. Baixe o ZIP da branch `nexus-1.1-work` no GitHub e extraia a pasta.
2. Abra o terminal dentro da pasta extraída.
3. Execute:

   ```powershell
   py -3.11 iniciar.py
   ```

4. Na primeira execução, o inicializador cria o ambiente virtual, instala as dependências e cria `.env` a partir de `.env.example`.
5. Abra `.env`, configure o provedor e a chave de API correspondente.
6. Salve o arquivo e inicie o NEXUS novamente.

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

## Token Guard

O Token Guard utiliza uma estimativa aproximada baseada no tamanho das mensagens, não um tokenizer exato de cada provedor. Ajuste `NEXUS_MAX_CONTEXT_TOKENS`, `NEXUS_MAX_OUTPUT_TOKENS`, `NEXUS_MAX_TOOL_CALLS_PER_STEP`, `NEXUS_MAX_STEPS` e `NEXUS_REQUEST_TIMEOUT` no arquivo `.env`.

## Recuperação de tarefas

O NEXUS grava checkpoints JSON em `nexus_tasks/`. Use `/tasks` para consultar o estado e as ações registradas. Por segurança, cliques, digitação, comandos PowerShell e gravações de arquivos não são repetidos automaticamente após uma interrupção. Revise o estado atual do computador antes de continuar manualmente. Consulte [docs/TASK_RECOVERY.md](docs/TASK_RECOVERY.md).

## Testes e limitações

Os testes unitários e a compilação Python são executados pelo GitHub Actions em Ubuntu com Python 3.11. Isso não substitui testes de aceitação no Windows. Autenticação real, catálogo de modelos, chamadas de ferramentas, visão e automação da área de trabalho precisam ser validados com cada conta/provedor e em Windows, inclusive Windows ARM64.

O NEXUS prioriza segurança, transparência, baixo consumo local e controle do usuário.
