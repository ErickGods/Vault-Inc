---
tags: [claude-code, core-features, hooks, automation]
house: shared
domain: claude/core-features
level: intermediate
status: active
created: 2026-04-19
updated: 2026-08-01
---

# Sistema de Hooks — Claude Code

## O que são Hooks

Hooks são callbacks automáticos que executam comandos shell em resposta a eventos específicos do ciclo de vida do Claude Code. São o mecanismo de automação do lado do *ambiente* — enquanto skills definem comportamentos do Claude, hooks definem reações do seu sistema.

A diferença fundamental: hooks rodam fora do contexto do Claude, executados diretamente pelo harness (o runtime do Claude Code). Isso significa que hooks podem fazer coisas que o Claude não pode fazer sozinho — executar linters, rodar formatadores, enviar notificações via ferramentas externas, disparar webhooks.

Hooks são configurados em `settings.json` e são completamente transparentes ao usuário final — rodam silenciosamente em background, exceto quando produzem saída que o harness decide exibir.

---

## Eventos Disponíveis

O Claude Code expõe cinco eventos de hook:

### PreToolUse

Disparado **antes** de qualquer invocação de ferramenta pelo Claude. Recebe informações sobre a ferramenta que será executada.

Casos de uso:
- Validar que um arquivo existe antes de o Claude tentar editá-lo
- Verificar permissões antes de executar um comando Bash
- Logar todas as operações para auditoria
- Bloquear operações em determinados paths

```json
{
  "event": "PreToolUse",
  "tool": "Bash",
  "input": {
    "command": "rm -rf /tmp/build"
  }
}
```

### PostToolUse

Disparado **após** cada invocação de ferramenta, independente do resultado (sucesso ou falha).

Casos de uso:
- Auto-lint após edição de arquivo
- Auto-format após escrita de código
- Rodar testes após mudanças em arquivos específicos
- Notificar sobre operações completadas

```json
{
  "event": "PostToolUse",
  "tool": "Write",
  "input": {
    "file_path": "/src/components/Button.tsx"
  },
  "output": {
    "success": true
  }
}
```

### Notification

Disparado quando o Claude Code precisa notificar o usuário sobre algo — normalmente quando está aguardando input em modo interativo.

Casos de uso:
- Enviar push notification mobile quando Claude está aguardando resposta
- Tocar som de alerta
- Enviar mensagem no Slack/Discord

### Stop

Disparado quando o Claude Code termina uma sessão completa (o agente principal finaliza).

Casos de uso:
- Notificar que a tarefa foi concluída
- Gerar relatório de sessão
- Limpar arquivos temporários
- Commitar mudanças automaticamente após revisão

### SubagentStop

Disparado quando um subagente específico termina, antes do agente principal finalizar.

Casos de uso:
- Notificar sobre conclusão de tarefas paralelas
- Agregar resultados de múltiplos agentes
- Disparar o próximo agente numa pipeline

---

## Como Configurar Hooks

Hooks são configurados no arquivo `settings.json`. Pode ser:
- `~/.claude/settings.json` — global, aplica a todos os projetos
- `.claude/settings.json` — local, aplica apenas ao projeto atual (tem precedência)

### Estrutura Básica

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": "comando-shell aqui"
          }
        ]
      }
    ]
  }
}
```

### Campos do Hook

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `matcher` | string | Nome da ferramenta que dispara o hook. Use `"*"` para todas as ferramentas. |
| `type` | string | Sempre `"command"` por enquanto. |
| `command` | string | Comando shell a executar. Suporta shell completo com pipes, &&, etc. |

> [!info] O campo `matcher` é case-sensitive. Os nomes corretos das ferramentas são: `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebFetch`, `WebSearch`, `TodoWrite`, `mcp__[server]__[tool]`.

---

## Settings.json Completo com Hooks

Exemplo de configuração real de projeto com múltiplos hooks:

```json
{
  "model": "claude-sonnet-4-6",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run format)",
      "Bash(npm run test:unit)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "file=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')\" && case \"$file\" in *.ts|*.tsx) cd /workspace && npx eslint \"$file\" --fix --quiet 2>&1 | head -20 ;; *.py) cd /workspace && python -m black \"$file\" --quiet ;; *.go) gofmt -w \"$file\" ;; esac"
          }
        ]
      },
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "file=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')\" && case \"$file\" in *.ts|*.tsx|*.js|*.jsx) cd /workspace && npx eslint \"$file\" --fix --quiet 2>&1 | head -20 ;; esac"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "cmd=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.command')\" && echo \"[AUDIT $(date -u +%Y-%m-%dT%H:%M:%SZ)] $cmd\" >> ~/.claude/audit.log"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code terminou a tarefa\" with title \"Claude Code\" sound name \"Glass\"' 2>/dev/null || notify-send 'Claude Code' 'Tarefa concluída' 2>/dev/null || true"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code precisa da sua atenção\" with title \"Claude Code\" sound name \"Ping\"' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

---

## Variáveis de Ambiente nos Hooks

O harness injeta variáveis de ambiente quando executa os hooks:

| Variável | Conteúdo |
|----------|---------|
| `CLAUDE_TOOL_NAME` | Nome da ferramenta que disparou o evento |
| `CLAUDE_TOOL_INPUT` | JSON com os inputs da ferramenta (parseable com `jq`) |
| `CLAUDE_TOOL_OUTPUT` | JSON com o output da ferramenta (disponível em PostToolUse) |
| `CLAUDE_EVENT` | Nome do evento (`PreToolUse`, `PostToolUse`, etc.) |
| `CLAUDE_SESSION_ID` | ID único da sessão atual |

Exemplo de como extrair dados do input:

```bash
# Extrair o file_path de uma operação Write
file="$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')"

# Extrair o command de uma operação Bash
cmd="$(echo $CLAUDE_TOOL_INPUT | jq -r '.command')"

# Verificar se a ferramenta teve sucesso (PostToolUse)
success="$(echo $CLAUDE_TOOL_OUTPUT | jq -r '.success // true')"
```

---

## Exemplos Práticos

### Auto-lint no Save (TypeScript/ESLint)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "file=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')\" && [[ \"$file\" =~ \\.(ts|tsx|js|jsx)$ ]] && npx eslint \"$file\" --fix --max-warnings=0 2>&1 || true"
          }
        ]
      }
    ]
  }
}
```

### Auto-format com Prettier

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "file=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')\" && [[ \"$file\" =~ \\.(ts|tsx|js|jsx|json|css|md)$ ]] && npx prettier --write \"$file\" --log-level=warn 2>&1 || true"
          }
        ]
      },
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "file=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')\" && [[ \"$file\" =~ \\.(ts|tsx|js|jsx|json|css|md)$ ]] && npx prettier --write \"$file\" --log-level=warn 2>&1 || true"
          }
        ]
      }
    ]
  }
}
```

### Notificação no Terminal (macOS)

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Tarefa concluída\" with title \"Claude Code\" subtitle \"Sessão finalizada\" sound name \"Glass\"'"
          }
        ]
      }
    ]
  }
}
```

### Notificação no Terminal (Linux com notify-send)

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send --urgency=normal --icon=terminal 'Claude Code' 'Tarefa concluída! Confira os resultados.'"
          }
        ]
      }
    ]
  }
}
```

### Pre-commit Check Automático

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "cmd=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.command')\"; if echo \"$cmd\" | grep -qE '^git commit'; then npm run test:unit 2>&1 | tail -5 && npm run lint 2>&1 | tail -5; fi"
          }
        ]
      }
    ]
  }
}
```

### Auto-test Após Mudança em Arquivo de Source

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "file=\"$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')\"; if [[ \"$file\" =~ src/.*\\.(ts|js)$ ]] && [[ ! \"$file\" =~ \\.test\\. ]]; then testfile=\"${file/src/src}\"; testfile=\"${testfile/.ts/.test.ts}\"; [ -f \"$testfile\" ] && npx jest \"$testfile\" --passWithNoTests 2>&1 | tail -10 || true; fi"
          }
        ]
      }
    ]
  }
}
```

### Auditoria de Comandos Bash

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[$(date -u +%Y-%m-%dT%H:%M:%SZ)] SESSION=$CLAUDE_SESSION_ID CMD=$(echo $CLAUDE_TOOL_INPUT | jq -r '.command' | head -c 200)\" >> ~/.claude/bash-audit.log"
          }
        ]
      }
    ]
  }
}
```

### Hook de Notificação via Slack Webhook

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "curl -s -X POST \"$SLACK_WEBHOOK_URL\" -H 'Content-type: application/json' -d '{\"text\":\"Claude Code finalizou uma sessão em '\"$(pwd | xargs basename)\"'\"}' > /dev/null 2>&1 || true"
          }
        ]
      }
    ]
  }
}
```

---

## Hooks Bloqueantes vs Non-bloqueantes

Esta é uma das distinções mais importantes do sistema de hooks:

### Hooks Bloqueantes (PreToolUse)

Hooks no evento `PreToolUse` são **bloqueantes** — o Claude Code aguarda a execução do hook antes de prosseguir com a ferramenta. Se o hook falhar (exit code != 0), a ferramenta **não é executada**.

Isso permite usar hooks como guardrails:

```bash
# Hook que bloqueia rm -rf em paths protegidos
cmd="$(echo $CLAUDE_TOOL_INPUT | jq -r '.command')"
if echo "$cmd" | grep -qE 'rm\s+-rf\s+/(home|usr|etc|var)'; then
  echo "BLOQUEADO: operação destrutiva em path protegido"
  exit 1
fi
exit 0
```

> [!warning] Um hook bloqueante com bug pode travar o Claude Code completamente. Sempre termine hooks PreToolUse com `exit 0` no caminho feliz e teste exaustivamente antes de ativar.

### Hooks Non-bloqueantes (PostToolUse, Stop, Notification)

Hooks nos demais eventos são **non-bloqueantes** — o Claude Code continua sua execução independente do resultado do hook. Falhas são logadas mas não interrompem o fluxo.

Isso é importante para hooks de notificação e formatting: se o `notify-send` não estiver instalado no sistema, o hook falha silenciosamente sem afetar o trabalho do Claude.

O padrão `|| true` no final dos comandos garante exit code 0 mesmo quando o hook falha:

```bash
notify-send "Tarefa concluída" || true
```

---

## Debugging de Hooks

### Ver Output dos Hooks

Por padrão, hooks bem-sucedidos não mostram output. Para debugar, redirecione para um arquivo de log:

```bash
# No comando do hook, adicione logging:
"command": "meu-comando 2>&1 | tee -a ~/.claude/hook-debug.log"
```

```bash
# Acompanhe em tempo real:
tail -f ~/.claude/hook-debug.log
```

### Testar Hook Manualmente

Simule a execução do hook com as variáveis de ambiente que o harness injetaria:

```bash
export CLAUDE_TOOL_NAME="Write"
export CLAUDE_TOOL_INPUT='{"file_path": "/workspace/src/Button.tsx"}'
export CLAUDE_EVENT="PostToolUse"

# Execute o comando do hook diretamente
file="$(echo $CLAUDE_TOOL_INPUT | jq -r '.file_path')"
echo "Arquivo: $file"
```

### Verificar se jq está instalado

Muitos hooks dependem de `jq` para parsear JSON. Se `jq` não estiver disponível:

```bash
which jq || (echo "jq não encontrado. Instale: brew install jq / apt install jq" && exit 1)
```

### Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| Hook não executa | Event name com typo | Verificar capitalização exata: `PostToolUse` não `postToolUse` |
| `jq: command not found` | jq não instalado | `brew install jq` ou `apt-get install jq` |
| Hook bloqueia Claude | PreToolUse com exit != 0 | Adicionar `|| true` ou corrigir a lógica |
| Output não aparece | PostToolUse é non-bloqueante | Redirecionar para arquivo de log |
| Paths não encontrados | Hook roda em diretório diferente | Usar paths absolutos ou `cd /workspace &&` |

---

## Boas Práticas

> [!tip] Sempre use `|| true` em hooks PostToolUse e Stop. Evita que falhas opcionais (notificações, formatadores) interfiram no trabalho.

> [!tip] Use paths absolutos no working directory. Hooks podem rodar com `cwd` diferente do esperado.

> [!warning] Evite hooks PreToolUse complexos em produção. Qualquer bug bloqueia o Claude Code completamente. Prefira PostToolUse para operações não-críticas.

> [!info] Hooks são executados com as mesmas variáveis de ambiente do shell que iniciou o Claude Code. Se precisar de variáveis específicas (como `SLACK_WEBHOOK_URL`), certifique-se de que estão no seu `.bashrc` ou `.zshrc`.

> [!example] Padrão recomendado para hooks robustos:
> ```bash
> set -e  # Falha rápido em erros inesperados
> file="$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')"
> [ -z "$file" ] && exit 0  # Sem arquivo, nada a fazer
> [ -f "$file" ] || exit 0  # Arquivo não existe, skip
> # Sua lógica aqui
> exit 0
> ```

---

## Hooks em Repositórios de Equipe

Para compartilhar hooks com a equipe, use `.claude/settings.json` (local ao projeto, versionado no Git):

```bash
# Adicionar ao repo
git add .claude/settings.json
git commit -m "feat(claude): adiciona hooks de auto-lint e notificação"
```

> [!warning] Cuidado com hooks que referenciam ferramentas não universais (como `osascript` que é exclusivo do macOS). Use detecção de OS ou `|| true` para garantir portabilidade:
> ```bash
> # Multiplataforma
> osascript -e '...' 2>/dev/null || notify-send '...' 2>/dev/null || true
> ```

---

## Related

- [[skills-system]] — Skills são comportamentos do Claude; hooks são reações do ambiente
- [[permissions-and-safety]] — Hooks PreToolUse podem ser usados como guardrails de permissão
- [[slash-commands]] — Slash commands podem disparar workflows que hooks monitoram
- [[subagents]] — SubagentStop permite reagir à conclusão de subagentes individuais
- [[00-moc/claude-code-moc]] — Índice geral do Claude Code
