# NEXUS 1.0

**Agente de uso do computador para Windows, desenvolvido em Python e conectado a provedores de IA na nuvem.**

O NEXUS conecta-se a modelos de IA hospedados na nuvem para interpretar solicitações, planejar tarefas e interagir com o Windows por meio de ferramentas locais. A inferência dos modelos ocorre no provedor selecionado; o NEXUS não executa modelos localmente.

[English](README.md)

## Recursos

- Provedores de IA na nuvem: Groq Cloud e Ollama Cloud.
- Catálogo dinâmico de modelos do provedor selecionado.
- Três modos de operação: Chat, Planner e Operator.
- Integração com PowerShell e ferramentas de arquivos.
- Seleção de diretório de trabalho (workspace).
- Captura de screenshots e visão opcional para modelos compatíveis.
- Informações do Windows, incluindo tela e janela em primeiro plano.
- Verificações heurísticas e confirmação local para operações potencialmente destrutivas.
- Interface em português brasileiro e inglês.

A disponibilidade de um modelo não garante suporte a chamadas de ferramentas ou entrada de imagens.

## Requisitos

- Windows 10 ou Windows 11.
- Python 3.11 ou mais recente.
- Conexão com a internet.
- Chave de API de um provedor compatível.

## Instalação rápida

1. Baixe a branch `main` do repositório e extraia o arquivo.
2. Abra um terminal na pasta do projeto.
3. Execute:

   ```powershell
   py -3.11 iniciar.py
   ```

   Alternativamente, execute `python iniciar.py`.
4. Na primeira inicialização, o launcher cria um ambiente virtual, instala as dependências e cria `.env` a partir de `.env.example`, se necessário.
5. Abra `.env`, configure o provedor e adicione sua chave de API.
6. Salve o arquivo e inicie o NEXUS novamente.

A primeira instalação precisa de internet e pode levar alguns minutos.

## Instalação manual

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe main.py
```

## Configuração dos provedores

Configure o arquivo `.env`. Exemplo para Groq Cloud:

```env
NEXUS_PROVIDER=groq
GROQ_API_KEY=sua_chave_groq
GROQ_MODEL=openai/gpt-oss-120b
```

Para Ollama Cloud:

```env
NEXUS_PROVIDER=ollama
OLLAMA_API_KEY=sua_chave_ollama
OLLAMA_MODEL=beam
```

Os modelos disponíveis dependem do provedor e do acesso da conta. Alguns modelos podem não oferecer todas as ferramentas ou entrada de imagens.

Nunca publique ou compartilhe o arquivo `.env` ou suas chaves de API.

## Modos de operação

- **Chat:** conversa sem ferramentas de operação do computador.
- **Planner:** analisa solicitações e cria planos sem executar operações.
- **Operator:** utiliza as ferramentas disponíveis para realizar operações compatíveis no Windows.

## Comandos

| Comando | Descrição |
|---|---|
| `/providers` | Lista os provedores disponíveis. |
| `/provider groq` | Seleciona Groq Cloud. |
| `/provider ollama` | Seleciona Ollama Cloud. |
| `/agents` ou `/models` | Consulta os modelos disponíveis. |
| `/agent <número ou id>` | Seleciona um modelo. |
| `/modes` | Lista os modos. |
| `/mode chat`, `/mode planner`, `/mode operator` | Seleciona o modo de operação. |
| `/language auto`, `/language pt`, `/language en` | Define o idioma da interface. |
| `/vision on` / `/vision off` | Ativa ou desativa o envio de screenshots. |
| `/workspace` | Exibe o diretório de trabalho. |
| `/workspace <pasta>` | Seleciona uma pasta existente. |
| `/workspace off` | Desativa o workspace. |
| `/status` | Exibe a configuração atual. |
| `/init` | Cria um arquivo inicial NEXUS.md. |
| `/help` | Exibe os comandos disponíveis. |
| `/clear` | Limpa o terminal. |
| `/exit` | Encerra o NEXUS. |

## Workspace

Exemplo:

```text
/workspace C:\Users\Você\Desktop\MeuProjeto
```

A pasta selecionada precisa existir e permanece ativa apenas durante o processo atual. Se nenhum workspace for selecionado, a ferramenta dedicada de criação de arquivos de texto utiliza a Área de Trabalho do Windows. Ela cria novos arquivos sem sobrescrever os existentes.

## Visão e privacidade

A visão fica desativada por padrão. Quando ativada, screenshots podem ser enviados ao provedor selecionado se o modelo aceitar imagens. Screenshots podem conter informações privadas; feche documentos e aplicativos sensíveis antes de ativar o recurso.

Mantenha as chaves em `.env`, nunca envie esse arquivo ao GitHub e evite executar o NEXUS como Administrador sem necessidade. O NEXUS utiliza as permissões da conta atual do Windows.

## Limitações conhecidas

- Os recursos variam conforme o provedor e o modelo.
- Chamadas de ferramentas não são garantidas em todos os modelos.
- A visão exige um modelo compatível com entrada de imagens.
- As verificações de segurança são heurísticas e não constituem um sandbox.
- O histórico da conversa não é persistido entre reinicializações.
- Limites de uso do provedor podem interromper solicitações.
- Operações no computador devem ser revisadas e verificadas.

## Versão e roadmap

Esta branch contém a versão **1.0.0**. A linha de desenvolvimento 1.1 está na branch `dev-1.1` e não faz parte desta versão estável.

Consulte [ROADMAP.md](ROADMAP.md) para melhorias planejadas e [CHANGELOG.md](CHANGELOG.md) para o histórico de versões.

## Licença

Ainda não foi escolhida uma licença. Até que uma licença seja adicionada, aplicam-se as regras padrão de direitos autorais. A visibilidade pública do repositório não concede automaticamente permissão para reutilizar, modificar ou redistribuir o projeto.

---

**NEXUS 1.0.0**

Desenvolvido com Python e IA na nuvem.
