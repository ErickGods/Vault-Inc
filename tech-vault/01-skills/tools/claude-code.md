---
tags: [skill, tools, claude-code]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Claude Code, CC]
---

# Claude Code

## Overview

Claude Code é o CLI oficial da Anthropic que traz o modelo Claude diretamente para o terminal e editor. No nível avançado, o foco está em **automação via hooks**, **orquestração de múltiplos agentes**, **integração com MCP servers** e uso do ecossistema de **Superpowers** para fluxos de TDD, planejamento e brainstorming. A integração com [[prompt-engineering]] e [[multi-agent-systems]] eleva o Claude Code de assistente a parceiro de engenharia.

Para uso da API subjacente, consulte [[claude-api]]. Para servidores MCP disponíveis, veja [[mcp-servers-guide]]. Para o plugin de habilidades, consulte [[claude-code-superpowers]].

---

## Core Concepts

### CLI Commands and Flags

```bash
# Iniciar sessão interativa
claude

# Executar prompt único e sair (non-interactive)
claude -p "Explique o padrão Repository em TypeScript"

# Continuar a sessão mais recente
claude --continue

# Continuar sessão específica por ID
claude --resume <session-id>

# Modo verbose — mostra tokens, tool calls e raciocínio
claude --verbose

# Definir modelo explicitamente
claude --model claude-opus-4-5

# Output em JSON (para integração com scripts)
claude -p "list files" --output-format json

# Limitar uso máximo de tokens por sessão
claude --max-tokens 8000

# Adicionar arquivo de contexto na abertura da sessão
claude --context ./CLAUDE.md --context ./architecture.md

# Modo headless para CI/CD (sem interação, sem confirmações)
claude --headless -p "run all tests and fix failures"
```

### Slash Commands

Slash commands são atalhos para fluxos estruturados dentro de uma sessão.

| Command        | Description                                               |
|----------------|-----------------------------------------------------------|
| `/plan`        | Entra em modo de planejamento — esboça tarefas sem executar |
| `/review`      | Faz code review do diff atual ou arquivo especificado     |
| `/commit`      | Gera mensagem de commit e faz o commit git                |
| `/clear`       | Limpa o contexto da sessão atual                          |
| `/compact`     | Compacta o histórico de conversa para economizar tokens   |
| `/help`        | Lista todos os comandos disponíveis                       |
| `/cost`        | Exibe custo estimado da sessão atual                      |
| `/permissions` | Exibe e edita permissões de ferramentas da sessão         |

```bash
# Dentro da sessão interativa:
/plan implementar autenticação JWT com refresh tokens
/review src/auth/jwt.service.ts
/commit
```

> [!tip] /plan antes de implementar
> Use `/plan` em tasks complexas para validar a abordagem antes de deixar o agente executar. O plano pode ser editado antes de confirmar.

---

## Patterns

### MCP Server Integration

MCP (Model Context Protocol) permite que Claude Code se conecte a ferramentas externas como databases, APIs e sistemas de arquivos estendidos.

```json
// ~/.claude/settings.json — configuração de MCP servers
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
      "env": {}
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost/mydb"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "custom-internal": {
      "command": "node",
      "args": ["/path/to/my-mcp-server/dist/index.js"],
      "env": {
        "API_BASE_URL": "https://internal-api.company.com"
      }
    }
  }
}
```

**Criando um MCP server customizado:**

```typescript
// my-mcp-server/src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  { name: "internal-api", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler("tools/list", async () => ({
  tools: [{
    name: "get_feature_flags",
    description: "Fetch feature flags from internal API",
    inputSchema: {
      type: "object",
      properties: {
        environment: { type: "string", enum: ["dev", "staging", "prod"] }
      },
      required: ["environment"]
    }
  }]
}));

server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
  if (name === "get_feature_flags") {
    const data = await fetchFeatureFlags(args.environment);
    return { content: [{ type: "text", text: JSON.stringify(data) }] };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Hooks System

Hooks executam scripts shell **antes ou depois** de cada tool call do agente, permitindo auditoria, validação e automação.

```json
// ~/.claude/settings.json — hooks configuration
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "echo \"[HOOK] Bash cmd: $CLAUDE_TOOL_INPUT\" >> /tmp/claude-audit.log"
        }]
      },
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "scripts/validate-write.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "scripts/post-bash-hook.sh"
        }]
      }
    ]
  }
}
```

```bash
#!/usr/bin/env bash
# scripts/validate-write.sh — bloquear escrita fora de diretórios permitidos
TOOL_INPUT="$CLAUDE_TOOL_INPUT"
FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path')

ALLOWED_DIRS=("src/" "tests/" "docs/")
for dir in "${ALLOWED_DIRS[@]}"; do
  if [[ "$FILE_PATH" == "$dir"* ]]; then
    exit 0
  fi
done

echo "BLOCKED: Write to $FILE_PATH not allowed outside permitted directories"
exit 1  # exit 1 bloqueia o tool call
```

> [!warning] Exit codes em hooks
> Exit code `0` = permitir a ação. Exit code não-zero = **bloquear** o tool call e mostrar o stderr ao modelo como feedback. O modelo pode tentar uma abordagem diferente em resposta.

### Settings.json — Configuração Avançada

```json
// ~/.claude/settings.json — configuração completa
{
  "model": "claude-opus-4-5",
  "theme": "dark",
  "autoUpdates": true,
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(npm *)",
      "Bash(npx *)",
      "Read(**)",
      "Write(src/**)",
      "Write(tests/**)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl * | bash)",
      "Write(.env*)"
    ]
  },
  "env": {
    "NODE_ENV": "development"
  },
  "mcpServers": { }
}
```

> [!info] Settings hierárquicos
> Claude Code lê configurações em cascata: `~/.claude/settings.json` (global) → `.claude/settings.json` (projeto) → `.claude/settings.local.json` (local, não versionado). Configurações de projeto sobrescrevem global.

### Agent Mode e Subagents

No modo agente, Claude Code executa tarefas longas autonomamente, podendo criar **subagentes** para trabalho paralelo.

```bash
# Modo agente — execução autônoma com task complexa
claude --headless -p "
  Audit the entire codebase for security vulnerabilities.
  For each file in src/:
    1. Check for SQL injection risks
    2. Check for XSS vectors
    3. Check for hardcoded secrets
  Generate a report in security-audit.md with findings and severity.
"

# Dispatch paralelo via prompt de orquestrador
claude -p "
  Spawn 3 parallel agents:
  Agent 1: Run unit tests for src/auth/
  Agent 2: Run unit tests for src/api/
  Agent 3: Run integration tests
  Collect all results and summarize failures.
"
```

> [!example] Orquestrador + Trabalhadores
> Padrão de [[multi-agent-systems]]: um agente orquestrador lê o backlog de tasks e dispara subagentes especializados via `claude -p` em subprocessos, coletando resultados via arquivos ou stdout. Consulte [[multi-agent-systems]] para o padrão completo.

### Superpowers Plugin — Skills System

O plugin Superpowers (via [[claude-code-superpowers]]) adiciona um sistema de skills que são instruções estruturadas carregadas sob demanda via `/skill`.

```bash
# Invocar skill de TDD
/tdd UserAuthService

# Invocar skill de brainstorming
/brainstorm "sistema de notificações em tempo real"

# Invocar skill de plan estruturado
/plan "refatorar módulo de pagamentos para suportar múltiplos provedores"

# Invocar skill customizada do projeto
/review-pr 123
```

Skills são arquivos Markdown em `~/.claude/skills/` com instruções estruturadas:

```markdown
<!-- ~/.claude/skills/tdd.md -->
## TDD Skill
Given a class or module name, implement using Test-Driven Development:
1. Write failing tests first (Red)
2. Implement minimum code to pass (Green)
3. Refactor for quality (Refactor)
Follow the project's test patterns from existing test files.
```

### Worktrees para Trabalho Isolado

Combinar Git worktrees com Claude Code permite sessões paralelas isoladas por feature.

```bash
# Criar worktree para nova feature
git worktree add ../project-feat-auth feature/auth

# Iniciar Claude Code no worktree
cd ../project-feat-auth
claude

# Enquanto isso, sessão principal continua em main sem interferência
```

### CLAUDE.md — Convenções do Projeto

O arquivo `CLAUDE.md` na raiz do projeto é carregado automaticamente como contexto persistente em toda sessão.

```markdown
<!-- CLAUDE.md -->
# Project: My App

## Stack
- Runtime: Node.js 22, TypeScript 5.4
- Framework: Fastify 4
- ORM: Drizzle + PostgreSQL
- Testing: Vitest + Supertest

## Conventions
- All new services go in `src/services/`
- All routes in `src/routes/`, one file per domain
- Use Zod for ALL external input validation
- Commit format: Conventional Commits (feat/fix/chore/docs)
- Never use `any` in TypeScript

## Testing
- Unit tests: `npm run test:unit`
- Integration: `npm run test:integration` (requires Docker)
- Coverage threshold: 80%

## Forbidden
- Never commit directly to main
- Never use console.log in src/ (use the logger service)
- Never store secrets in env variables inside Docker images
```

### Permission Modes

```bash
# Ver permissões atuais da sessão
/permissions

# Modo "yolo" — aprovar tudo automaticamente (USE COM CUIDADO)
claude --dangerously-skip-permissions

# Modo restrito — aprovar cada tool call manualmente
claude --permission-mode manual

# No settings.json — listas de allow/deny por padrão glob
# "Bash(git *)" permite apenas comandos git via Bash
# "Write(src/**)" permite escrever apenas dentro de src/
```

> [!danger] --dangerously-skip-permissions
> Esse flag desativa todas as confirmações. Nunca use em repositórios com dados sensíveis ou em máquinas de produção. Reserve para ambientes de sandbox controlados.

---

## Gotchas

> [!warning] Contexto de sessão tem limite
> Sessões longas consomem contexto progressivamente. Use `/compact` periodicamente para comprimir o histórico mantendo as informações essenciais. Quando o contexto encher, o modelo começa a "esquecer" o início da conversa.

> [!warning] MCP servers são processos separados
> Cada MCP server roda como subprocesso independente. Se o server travar ou crashar, os tools ficam indisponíveis silenciosamente. Adicione logs e healthchecks nos servidores customizados.

> [!info] CLAUDE.md é incluído em TODOS os tokens
> O arquivo `CLAUDE.md` é injetado no início de cada mensagem. Mantenha-o conciso — arquivos grandes aumentam o custo de cada interação. Separe documentação longa em arquivos referenciados via `@` no momento certo.

---

## Snippets

```bash
# Sessão com múltiplos arquivos de contexto
claude --context CLAUDE.md --context docs/architecture.md --context .env.example

# Pipeline: Claude Code gerando e rodando testes automaticamente
claude --headless -p "Write unit tests for every exported function in src/utils/ and run them" \
  | tee claude-test-session.log

# Usar Claude Code para gerar PR description
git diff main...HEAD | claude -p "Write a GitHub PR description for this diff" --output-format text

# Exportar histórico da sessão para revisão
claude --list-sessions
claude --export-session <id> > session-$(date +%Y%m%d).json

# Verificar custo acumulado do mês
claude --usage
```

---

## References

- [Claude Code official docs](https://docs.anthropic.com/claude-code)
- [MCP Protocol specification](https://modelcontextprotocol.io)
- [Claude Code Superpowers plugin](https://github.com/badass-courses/claude-code-superpowers)
- [CLAUDE.md conventions — Anthropic guide](https://docs.anthropic.com/claude-code/memory)

---

## Related

- [[claude-api]]
- [[claude-code-superpowers]]
- [[mcp-servers-guide]]
- [[prompt-engineering]]
- [[multi-agent-systems]]
