---
tags: [claude-code, fundamentals]
aliases: [Claude Code, CLI Anthropic, Agente de Desenvolvimento]
house: shared
domain: claude/fundamentals
level: intro
status: active
created: 2026-04-19
updated: 2026-08-01
---

# O que é Claude Code

## Overview

Claude Code é a CLI oficial da Anthropic para desenvolvimento agentico — um agente de linha de comando que roda no seu terminal e executa tarefas complexas de engenharia de software de forma autônoma. A diferença fundamental entre Claude Code e um chatbot comum como claude.ai é que ele **age**, não apenas responde: lê arquivos reais, executa comandos bash, edita código, cria commits e navega em repositórios completos.

Enquanto um chatbot responde dentro de uma janela de chat e você copia-cola resultados manualmente, o Claude Code opera diretamente no seu ambiente de desenvolvimento. Ele tem acesso ao sistema de arquivos, pode rodar testes, executar builds, fazer git operations e encadear dezenas de ações para completar tarefas multi-step sem intervenção manual.

> [!info] Definição Técnica
> Claude Code é um **agente de software**: um sistema de IA que percebe o ambiente (lê arquivos, executa comandos), raciocina sobre o estado atual, e age (edita, cria, deleta, commita) em loops iterativos até completar o objetivo.

Integra com [[claude-models-overview]], [[context-window-management]], [[pricing-and-tokens]], e [[claude-code-vs-api-vs-chat]].

---

## Instalação

### Pré-requisitos

- **Node.js 18+** — o Claude Code é distribuído via npm
- **Conta Anthropic** — necessário para autenticação via API key ou plano Claude Code (Pro/Max/Team)
- **Git** — recomendado para a maioria dos workflows

### npm (método principal)

```bash
npm install -g @anthropic-ai/claude-code
```

Após instalação:

```bash
claude --version
# claude-code/1.x.x ...
```

> [!tip] Atualização
> O Claude Code verifica atualizações automaticamente. Para forçar:
> ```bash
> npm update -g @anthropic-ai/claude-code
> ```

### macOS via Homebrew

```bash
brew install anthropic/tap/claude-code
```

### Windows (via WSL)

O Claude Code no Windows funciona melhor via **WSL 2** (Windows Subsystem for Linux):

```bash
# 1. Instalar WSL 2 (PowerShell como admin)
wsl --install

# 2. Abrir Ubuntu/Debian no WSL
wsl

# 3. Instalar Node.js no WSL
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. Instalar Claude Code
npm install -g @anthropic-ai/claude-code
```

> [!warning] Windows Nativo
> O Claude Code pode rodar no Windows nativo via PowerShell ou Command Prompt, mas algumas funcionalidades de bash podem ser limitadas. WSL é fortemente recomendado para desenvolvimento sério.

---

## Setup Inicial

### Primeiro uso

```bash
# Iniciar o Claude Code no diretório do projeto
cd /meu/projeto
claude
```

Na primeira execução, o Claude Code solicita autenticação. Você tem duas opções:

**Opção 1: Autenticação via conta Anthropic (Claude.ai)**
- O browser abre automaticamente para login
- Requer plano Pro ($20/mês) ou Max ($100/mês)
- Inclui limites de uso mensais

**Opção 2: API Key direta**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
claude
```

> [!info] API Key vs Conta
> Usar API key direta cobra por token (pay-as-you-go). A conta Pro/Max tem limites mensais fixos mas é mais previsível em custo para uso pesado. Veja [[pricing-and-tokens]] para comparativo.

### Configuração de projeto com CLAUDE.md

O arquivo `CLAUDE.md` na raiz do projeto é automaticamente incluído no contexto de toda sessão. É o mecanismo principal de customização:

```bash
# Claude Code pode criar o CLAUDE.md para você
claude
> /init
```

Exemplo de `CLAUDE.md`:

```markdown
# Projeto: Meu SaaS

## Tech Stack
- Backend: FastAPI (Python 3.11)
- Frontend: Next.js 14 (TypeScript)
- Database: PostgreSQL + SQLAlchemy
- Deploy: AWS ECS

## Comandos essenciais
- `make test` — roda pytest
- `make lint` — black + ruff
- `make dev` — sobe docker-compose

## Convenções
- Commits em inglês, formato Conventional Commits
- PR sempre com testes cobrindo o novo código
- Branches: feat/, fix/, chore/
```

> [!tip] CLAUDE.md e Contexto
> O CLAUDE.md consome tokens em toda sessão. Mantenha-o conciso e focado nas informações que o Claude realmente precisa para tomar decisões corretas no projeto. Veja [[context-window-management]].

---

## Como Funciona Internamente

### Loop de Tool Use

O Claude Code opera em um loop de **percepcão → raciocínio → ação**:

```
Usuário: "Adicione autenticação JWT ao endpoint /api/users"
    ↓
Claude lê: ls, cat app/routes/users.py, cat app/models/user.py
    ↓
Claude raciocina: "preciso de PyJWT, criar middleware, modificar endpoint"
    ↓
Claude age: edita requirements.txt, cria auth/middleware.py, modifica users.py
    ↓
Claude verifica: cat app/routes/users.py (confirma mudança), roda make test
    ↓
Claude reporta: "Implementei JWT auth. Testes passando."
```

Internamente, o Claude usa a **Tool Use API** da Anthropic: o modelo recebe uma lista de ferramentas disponíveis (bash, read_file, write_file, etc.) e escolhe qual invocar a cada passo. O CLI executa a ferramenta, retorna o resultado, e o loop continua.

### Ferramentas disponíveis para o Claude Code

| Ferramenta | O que faz | Exemplo de uso |
|-----------|-----------|----------------|
| `Bash` | Executa comandos shell | `ls -la`, `git status`, `pytest` |
| `Read` | Lê arquivos com controle de offset/limit | Lê `app/main.py` linhas 50-100 |
| `Write` | Cria/sobrescreve arquivos | Cria novo arquivo de configuração |
| `Edit` | Edições precisas via string replacement | Substitui bloco de código específico |
| `Glob` | Busca arquivos por padrão | `**/*.py`, `src/**/*.ts` |
| `Grep` | Busca conteúdo em arquivos | `ripgrep` patterns |
| `WebFetch` | Busca documentação na web | Lê páginas de docs |
| `TodoWrite` | Gerencia lista de tarefas | Planeja execução de tarefas complexas |

### Leitura seletiva de arquivos

O Claude Code usa `offset` e `limit` para ler apenas partes relevantes de arquivos grandes, preservando contexto:

```bash
# Internamente o Claude executa algo como:
# Read file: path=app/models.py, offset=200, limit=100
# → lê apenas as linhas 200-300
```

### Execução de Bash

Quando o Claude executa um comando bash, ele:
1. Solicita permissão (na primeira vez para comandos potencialmente destrutivos)
2. Executa o comando no shell do processo
3. Captura stdout + stderr
4. Inclui o output no contexto para raciocinar sobre o resultado

```
Claude: "Vou rodar os testes para verificar"
[Executa: pytest tests/ -v --tb=short]
[Output capturado e incluído no contexto]
Claude: "3 testes falhando em test_auth.py linha 47..."
```

---

## Modos de Operação

### Modo Interativo (REPL)

O modo padrão — um loop de conversa onde você descreve tarefas:

```bash
cd /meu/projeto
claude
```

```
> Refatore a função calculate_price para aceitar cupons de desconto
> Adicione testes para os edge cases
> Gere um PR description para essas mudanças
```

Atalhos do modo interativo:

| Atalho | Ação |
|--------|------|
| `Ctrl+C` | Interrompe execução atual |
| `Ctrl+D` | Sai do Claude Code |
| `/help` | Lista todos os slash commands |
| `/clear` | Limpa histórico da sessão |
| `/compact` | Compacta contexto (reduz tokens) |
| `/init` | Cria CLAUDE.md no projeto |
| `↑` / `↓` | Navega histórico de comandos |

### Modo Headless (`--print`)

Executa uma tarefa sem interação, imprime o resultado e sai. Ideal para scripts e CI:

```bash
# Executa e imprime resultado
claude --print "Liste todos os endpoints da API neste projeto"

# Com pipe
echo "Explique este código: $(cat app/utils.py)" | claude --print

# Em scripts bash
RESULT=$(claude --print "Gere um changelog baseado nos últimos 10 commits")
echo "$RESULT" > CHANGELOG.md
```

### Modo Pipe

Recebe input via stdin:

```bash
# Análise de código
cat app/models.py | claude --print "Identifique potenciais SQL injections"

# Processamento em lote
for file in tests/*.py; do
    echo "=== $file ===" 
    claude --print "Analise a cobertura de edge cases em: $(cat $file)"
done
```

### Agentes em Background (Subagentes)

O Claude Code suporta lançar subagentes — instâncias paralelas do Claude com contexto isolado — para executar tarefas independentes simultaneamente:

```bash
# O Claude principal pode lançar subagentes via bash:
# claude --print "Refatore auth module" &
# claude --print "Otimize queries do relatório" &
```

Veja [[../03-advanced/subagents-parallel-execution]] para o padrão completo.

### Modo com Worktrees

Para trabalhar em branches isoladas sem afetar o workspace principal:

```bash
# Criar worktree para feature
git worktree add ../feature-auth feat/jwt-auth

# Rodar Claude Code na worktree
cd ../feature-auth
claude
```

---

## Integração com IDEs

### VS Code

O Claude Code pode ser invocado diretamente do terminal integrado do VS Code. Para uma experiência mais fluida:

```bash
# Abre o terminal integrado (Ctrl+`)
# Navega ao projeto
cd /workspace/meu-projeto
claude
```

A extensão oficial **Claude Code** (quando disponível na marketplace) oferece:
- Painel lateral com histórico de sessão
- Diff viewer integrado para mudanças propostas
- Atalhos de teclado para operações comuns

### JetBrains (IntelliJ, PyCharm, GoLand, etc.)

Similar ao VS Code — use o terminal integrado:

```bash
# Terminal integrado: Alt+F12 (Windows/Linux) ou Option+F12 (macOS)
claude
```

> [!tip] Dica JetBrains
> Mantenha o painel de VCS aberto enquanto trabalha com Claude Code. As mudanças feitas pelo Claude aparecem em tempo real no diff viewer do JetBrains.

### Vim / Neovim

Configure um mapping para abrir o Claude Code em split:

```vim
" ~/.vimrc ou ~/.config/nvim/init.vim
nnoremap <leader>cc :terminal claude<CR>
```

Com Neovim + toggleterm.nvim:

```lua
-- ~/.config/nvim/lua/plugins/claude.lua
vim.keymap.set("n", "<leader>cc", function()
    require("toggleterm.terminal").Terminal:new({
        cmd = "claude",
        direction = "vertical",
        size = 80,
    }):toggle()
end)
```

---

## Comandos Essenciais do Dia a Dia

### Slash Commands

```bash
/help          # Lista todos os comandos disponíveis
/clear         # Limpa contexto da sessão atual
/compact       # Compacta contexto para economizar tokens
/init          # Cria/atualiza CLAUDE.md no projeto
/review        # Faz code review das mudanças atuais
/status        # Mostra status do contexto (tokens usados)
/exit          # Sai do Claude Code
```

### Flags da CLI

```bash
# Especificar modelo
claude --model claude-sonnet-4-5

# Modo headless
claude --print "sua tarefa aqui"

# Continuar sessão anterior
claude --continue

# Arquivo de configuração específico
claude --config /path/to/claude.json

# Desabilitar confirmações (cuidado!)
claude --dangerously-skip-permissions

# Output em formato JSON
claude --output-format json --print "sua tarefa"
```

---

## Gotchas Comuns de Setup

### Problema: `claude: command not found`

```bash
# Verificar se npm global está no PATH
echo $PATH | grep -o '[^:]*npm[^:]*'

# Adicionar ao PATH (bash)
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# macOS com nvm
echo 'export PATH="$HOME/.nvm/versions/node/$(node -v)/bin:$PATH"' >> ~/.zshrc
```

### Problema: Permissão negada ao executar comandos

O Claude pede confirmação antes de executar comandos potencialmente destrutivos. Para comandos frequentes que você confia, adicione ao `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(make:*)",
      "Bash(pytest:*)",
      "Bash(git:*)",
      "Bash(npm run:*)"
    ]
  }
}
```

### Problema: Contexto estourando em projetos grandes

```bash
# Use /compact para comprimir o histórico
> /compact

# Ou inicie nova sessão focada
claude --print "Apenas analise src/auth/middleware.py e sugira melhorias"
```

Veja [[context-window-management]] para estratégias completas.

### Problema: API Key não reconhecida

```bash
# Verificar se está setada
echo $ANTHROPIC_API_KEY

# Testar conexão
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Problema: Claude não encontra arquivos do projeto

Certifique-se de estar no diretório correto:
```bash
pwd  # deve ser a raiz do projeto
ls   # deve mostrar CLAUDE.md, src/, etc.
claude
```

---

## Comparação: Claude Code vs Alternativas

### Claude Code vs GitHub Copilot

| Aspecto | Claude Code | GitHub Copilot |
|---------|------------|----------------|
| Interface | Terminal (CLI) | IDE (inline suggestions) |
| Granularidade | Tarefas completas end-to-end | Completions linha por linha |
| Acesso ao sistema | Sim (arquivos, bash, git) | Limitado |
| Context window | 200K+ tokens | ~128K tokens |
| Multi-file | Sim, navega o projeto inteiro | Sim (Chat) |
| Autonomia | Alta — executa ações | Baixa — sugere código |
| Custo | $20-100/mês (plano) ou por token | $10-19/mês |
| **Melhor para** | Implementações complexas, refatorações, automações | Autocompletion rápido no dia a dia |

### Claude Code vs Cursor

| Aspecto | Claude Code | Cursor |
|---------|------------|--------|
| Interface | Terminal | IDE completa (fork do VS Code) |
| Setup | Qualquer editor | Requer usar o Cursor como IDE |
| Contexto do projeto | Via CLAUDE.md + navegação | Indexação do codebase |
| Autonomia | Alta | Alta (Composer) |
| Custo | $20-100/mês | $20/mês |
| Modelos | Claude exclusivamente | Claude, GPT-4, Gemini |
| **Melhor para** | Quem prefere seu editor atual | Quem quer trocar de IDE |

### Claude Code vs Aider

| Aspecto | Claude Code | Aider |
|---------|------------|-------|
| Interface | Terminal (próprio) | Terminal (open source) |
| Modelo | Claude exclusivamente | Multi-provider (Claude, GPT, Gemini) |
| Git integration | Sim | Sim (commits automáticos) |
| Custo ferramenta | Incluído no plano | Grátis (paga só o modelo) |
| Maturidade | Oficial Anthropic | Projeto OSS ativo |
| **Melhor para** | Usuário já no ecossistema Anthropic | Flexibilidade de provider |

### Quando usar cada um

```
Tarefa de autocompletion rápida enquanto código
→ GitHub Copilot (inline, sem friction)

Implementar feature complexa em múltiplos arquivos
→ Claude Code ou Cursor Composer

Refatoração grande em base de código legada
→ Claude Code (melhor navegação via bash/grep)

Quero ficar no VS Code/JetBrains que já uso
→ Claude Code (terminal integrado)

Quero trocar de IDE por algo mais AI-native
→ Cursor

Preciso de flexibilidade de modelo (GPT, Claude, Gemini)
→ Aider
```

---

## Segurança e Boas Práticas

### O que o Claude Code pode fazer

- Ler e escrever qualquer arquivo que seu usuário unix possa acessar
- Executar qualquer comando bash
- Fazer requisições HTTP
- Modificar arquivos de configuração do sistema

> [!warning] Cuidado com Projetos Críticos
> Em repositórios de produção, revise sempre as mudanças propostas antes de confirmar. Use `git diff` depois de sessões do Claude Code antes de commitar.

### Boas práticas de segurança

```bash
# 1. Sempre trabalhe em branches separadas
git checkout -b feat/claude-refactor

# 2. Revise diffs antes de commitar
git diff --stat
git diff

# 3. Configure permissões restritivas no projeto
# .claude/settings.json
{
  "permissions": {
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(sudo:*)"
    ]
  }
}

# 4. Use .claudeignore para arquivos sensíveis
echo ".env\nsecrets/\n*.key" > .claudeignore
```

---

## Related

- [[claude-models-overview]] — Qual modelo usar no Claude Code
- [[claude-code-vs-api-vs-chat]] — Quando usar CLI vs API vs chat
- [[context-window-management]] — Como gerenciar contexto eficientemente
- [[pricing-and-tokens]] — Custos do Claude Code (Pro vs Max vs API)
- [[../02-core-features/slash-commands]] — Referência completa de slash commands
- [[../02-core-features/claude-md-configuration]] — CLAUDE.md em profundidade
- [[../03-advanced/subagents-parallel-execution]] — Agentes paralelos
- [[../03-advanced/worktrees-workflow]] — Workflow com git worktrees
