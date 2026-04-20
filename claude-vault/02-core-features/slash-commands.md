---
tags: [claude-code, core-features, slash-commands, commands]
status: active
level: intermediate
updated: 2026-04-19
created: 2026-04-19
---

# Slash Commands — Claude Code

## O que são Slash Commands

Slash commands são atalhos de texto que executam ações específicas no Claude Code. Começam com `/` e são invocados digitando o comando na interface de chat. Existem dois tipos:

1. **Built-in commands**: Comandos nativos do Claude Code, sempre disponíveis
2. **Custom commands**: Comandos definidos por você em arquivos Markdown, dentro de `.claude/commands/`

A diferença conceitual com Skills é importante: skills definem *comportamentos contínuos* do Claude (como ele age, que processo segue). Slash commands são *ações pontuais* — fazem uma coisa específica quando invocados e terminam. Um comando pode invocar uma skill, mas a skill em si não é um slash command.

---

## Comandos Built-in do Claude Code

### /help

Exibe ajuda contextual sobre o Claude Code e os comandos disponíveis.

```
/help
```

Mostra:
- Lista de built-in commands com descrições curtas
- Custom commands disponíveis no projeto atual
- Dicas de uso e atalhos de teclado

**Quando usar:** Quando você esqueceu um comando ou quer descobrir o que está disponível.

---

### /clear

Limpa o histórico da conversa atual, iniciando uma sessão nova com contexto limpo.

```
/clear
```

> [!warning] `/clear` descarta TUDO do contexto atual. O Claude esquece tudo que foi dito e feito na sessão. Use quando o contexto está poluído com informações irrelevantes ou quando quer iniciar uma nova tarefa do zero.

**Quando usar:**
- Após completar uma tarefa e iniciar outra completamente diferente
- Quando o contexto ficou muito longo e o Claude está "esquecendo" informações importantes
- Para resetar após um erro confuso que poluiu a sessão

---

### /compact

Compacta o contexto da conversa atual, resumindo o histórico para liberar espaço sem perder o estado essencial.

```
/compact
```

Diferente de `/clear`, `/compact` mantém um resumo do que foi feito, preservando o estado atual do trabalho. O Claude resume o histórico em pontos-chave antes de continuar.

**Quando usar:**
- Em sessões longas onde o contexto está crescendo (risco de context overflow)
- Quando quer continuar trabalhando na mesma tarefa mas o histórico está grande demais
- Para reduzir custo de tokens em sessões longas

> [!tip] Use `/compact` regularmente em tarefas longas (mais de 1h de trabalho). Mantém o Claude focado e reduz custo.

---

### /model

Muda o modelo de linguagem em uso para a sessão atual.

```
/model claude-opus-4
/model claude-haiku-4
/model claude-sonnet-4-6
```

| Modelo | Velocidade | Custo | Melhor Para |
|--------|-----------|-------|------------|
| claude-haiku-4 | Muito rápido | Baixo | Tarefas simples, formatação |
| claude-sonnet-4-6 | Rápido | Médio | Desenvolvimento geral |
| claude-opus-4 | Mais lento | Alto | Raciocínio complexo, arquitetura |

**Quando usar:**
- Para tasks rápidas e simples: mude para Haiku e economize
- Para análise de arquitetura ou decisões complexas: mude para Opus
- Volta ao Sonnet para desenvolvimento normal

---

### /cost

Exibe o custo atual da sessão em tokens e estimativa de custo em dólares.

```
/cost
```

Output típico:
```
Session Cost
Input tokens:  45,231
Output tokens:  8,943
Cache read:    23,100
Cache write:    4,500

Estimated cost: ~$0.47

Breakdown:
  Claude Sonnet 4.6: $0.47
```

**Quando usar:** Ao final de sessões longas para monitorar gasto. Útil para calibrar uso de subagentes e modelos.

---

### /status

Exibe o status atual do Claude Code: modelo em uso, permissões ativas, MCP servers conectados, configurações relevantes.

```
/status
```

Output típico:
```
Claude Code Status
Model: claude-sonnet-4-6
Mode: default
MCP Servers: filesystem (connected), github (connected)
Permissions: 12 allowed, 3 denied
Project: /workspace/meu-projeto
Branch: feature/oauth2
```

**Quando usar:** Para verificar rapidamente a configuração atual antes de iniciar uma tarefa importante.

---

### /quit (ou /exit)

Encerra a sessão do Claude Code.

```
/quit
/exit
```

**Quando usar:** Para sair limpo, garantindo que a sessão seja encerrada corretamente e os hooks de Stop sejam disparados.

---

### /bug

Abre o GitHub Issues do Claude Code para reportar um bug. Inclui automaticamente informações de diagnóstico da sessão.

```
/bug
```

**Quando usar:** Quando você encontrar comportamento inesperado do Claude Code que parece ser um bug do produto, não do seu código.

---

### /doctor

Executa diagnóstico do ambiente do Claude Code, verificando configurações, permissões e dependências.

```
/doctor
```

Verifica:
- Versão do Claude Code
- Conexão com a API da Anthropic
- MCP servers configurados e seu status
- Problemas comuns de configuração
- Permissões de filesystem

**Quando usar:** Quando algo está funcionando de forma estranha, antes de iniciar debugging manual.

---

### /pr-comments

Carrega e exibe os comentários de um Pull Request aberto para o Claude revisar e responder.

```
/pr-comments
/pr-comments https://github.com/org/repo/pull/123
```

Com este comando, o Claude pode:
- Ler todos os comentários do PR
- Entender o feedback dos revisores
- Implementar as mudanças solicitadas
- Responder aos comentários com as mudanças feitas

**Quando usar:** Quando você recebe feedback em um PR e quer que o Claude ajude a implementar as mudanças solicitadas.

---

### /init

Inicializa o CLAUDE.md do projeto atual, gerando documentação automática do codebase.

```
/init
```

O Claude analisa o projeto (estrutura de diretórios, package.json, arquivos principais) e gera um CLAUDE.md com:
- Visão geral do projeto
- Tech stack detectado
- Comandos importantes
- Convenções de código encontradas

**Quando usar:** Para novos projetos ou projetos que ainda não têm CLAUDE.md.

---

### /review

Inicia um code review da sessão atual ou do diff atual.

```
/review
/review --pr 123
```

**Quando usar:** Para revisão rápida antes de submeter um PR.

---

## Custom Commands — Criando seus Próprios

Custom commands são arquivos Markdown em `.claude/commands/`. O nome do arquivo é o nome do comando.

```
.claude/
└── commands/
    ├── criar-pr.md
    ├── rodar-testes.md
    ├── gerar-changelog.md
    └── deploy-staging.md
```

### Estrutura de um Custom Command

```markdown
---
description: Cria um Pull Request para a branch atual com título e descrição gerados automaticamente
---

# Criar Pull Request

Analise as mudanças da branch atual e crie um Pull Request completo.

## Passos

1. Execute `git diff main...HEAD --stat` para ver os arquivos modificados
2. Execute `git log main...HEAD --oneline` para ver os commits
3. Com base nas mudanças, gere:
   - **Título**: Máximo 72 caracteres, imperativo, descritivo
   - **Descrição**: Seções Summary, Changes, Testing, Screenshots (se UI)
4. Execute:
   ```bash
   gh pr create --title "[TÍTULO]" --body "[DESCRIÇÃO]"
   ```
5. Retorne a URL do PR criado

## Formato da Descrição

```markdown
## Summary
[2-3 bullet points do que foi feito]

## Changes
[Lista de arquivos principais modificados e o que mudou]

## Testing
- [ ] Testes unitários passando
- [ ] Testado manualmente em development
- [ ] Sem regressões conhecidas
```

$ARGUMENTS
```

### Parâmetro $ARGUMENTS

`$ARGUMENTS` captura qualquer texto que o usuário digitar após o nome do comando:

```
/criar-pr fix/critical-bug -- hotfix urgente para produção
```

O texto após o comando é passado para `$ARGUMENTS`. Use para passar contexto adicional ao comando.

---

## Exemplos de Custom Commands

### Comando: `/rodar-testes`

```markdown
---
description: Executa a suite completa de testes e reporta o resultado formatado
---

# Rodar Testes

Execute a suite completa de testes do projeto e gere um relatório.

## Execução

```bash
npm run test:all 2>&1
```

Se falhar, também execute:
```bash
npm run test:unit 2>&1
npm run test:integration 2>&1
```

## Relatório

Apresente o resultado no formato:

```
RESULTADO DOS TESTES — [data]
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Testes Unitários:    ✓ 142 passing / ✗ 0 failing
Testes Integração:  ✓ 23 passing / ✗ 2 failing
Tempo Total:         4.2s

FALHAS:
[Lista detalhada de falhas]

STATUS: APROVADO / BLOQUEADO
```

$ARGUMENTS
```

---

### Comando: `/gerar-changelog`

```markdown
---
description: Gera o CHANGELOG.md a partir do histórico de commits entre duas tags ou desde a última tag até HEAD
---

# Gerar Changelog

Gere uma entrada de CHANGELOG para a versão atual.

## Coletar Informações

1. Execute `git tag --sort=-version:refname | head -5` para ver as últimas tags
2. Execute `git log [ULTIMA_TAG]..HEAD --oneline` para ver os commits
3. Classifique os commits por tipo (feat, fix, chore, docs, etc.)

## Formato do Changelog

```markdown
## [X.Y.Z] — YYYY-MM-DD

### Novidades (feat)
- [descrição da feature] ([#PR](link))

### Correções (fix)
- [descrição do fix] ([#PR](link))

### Melhorias (refactor/perf)
- [descrição da melhoria]

### Outros (chore/docs)
- [descrição]
```

4. Adicione a nova entrada no topo do CHANGELOG.md existente (após o cabeçalho)

$ARGUMENTS
```

---

### Comando: `/deploy-staging`

```markdown
---
description: Executa o checklist completo de pré-deploy e faz deploy para o ambiente de staging
---

# Deploy para Staging

## Checklist Pré-Deploy

1. **Testes**: Execute `npm run test:all` — se falhar, PARE
2. **Lint**: Execute `npm run lint` — corrija erros, PARE se não conseguir
3. **Build**: Execute `npm run build` — se falhar, PARE
4. **Migrations**: Execute `npx prisma migrate status` — liste migrations pendentes

## Deploy

Se todos os checks passaram:

```bash
git push origin $(git branch --show-current)
gh workflow run deploy-staging.yml --ref $(git branch --show-current)
```

## Monitoramento

Aguarde 2 minutos e verifique:
```bash
curl -f https://staging.minhaapp.com/health | jq .
```

Se o health check falhar, verifique os logs:
```bash
aws logs tail /ecs/minha-app-staging --follow --since 5m
```

## Relatório Final

```
DEPLOY STAGING — [timestamp]
Branch: [branch]
Commit: [hash]
Status: SUCESSO / FALHOU
Health check: ✓ / ✗
```

$ARGUMENTS
```

---

### Comando: `/novo-agente`

```markdown
---
description: Cria o arquivo de system prompt para um novo agente especializado no diretório .claude/agents/
---

# Criar Novo Agente

Crie um novo arquivo de agente em `.claude/agents/`.

## Informações Necessárias

$ARGUMENTS

Se os argumentos não especificarem, pergunte:
1. Nome do agente (ex: "Data Analyst")
2. Missão em 1-2 frases
3. Responsabilidades principais (lista)
4. Ferramentas necessárias
5. Formato de relatório esperado

## Criar o Arquivo

Crie `.claude/agents/[nome-em-kebab-case].md` com o template padrão da Vault Inc:

```markdown
# [Nome] — Vault Inc

## Identidade e Missão
Você é o [Nome] da Vault Inc. [Missão].

## Responsabilidades
- [lista]

## Ferramentas Disponíveis
[lista]

## Padrões e Convenções
[específicos do domínio]

## Formato de Relatório
[estrutura esperada]

## Limites
[o que está fora do escopo]
```

Após criar o arquivo, confirme o path e mostre uma prévia do conteúdo.
```

---

## Diferença: Commands vs Skills

| Característica | Slash Commands | Skills |
|----------------|---------------|--------|
| Invocação | `/nome-do-comando` | Por nome, semanticamente, ou via Skill tool |
| Propósito | Ação pontual específica | Comportamento contínuo ou processo |
| Contexto | Recebe `$ARGUMENTS` | Recebe contexto completo da conversa |
| Persistência | Executa e termina | Define como o Claude age em situações |
| Armazenamento | `.claude/commands/*.md` | `~/.claude/skills/` ou `.claude/skills/` |
| Reutilização | Explícita (usuário invoca) | Automática (matching semântico) ou explícita |

> [!example] **Exemplo prático**: A skill `conventional-commit` define *como* o Claude escreve commits (seu processo, seu formato, suas regras). O slash command `/criar-pr` é uma *ação* que o Claude executa quando invocado — analisa o diff, gera título e descrição, cria o PR. O command pode usar a skill internamente.

---

## Keyboard Shortcuts

| Atalho | Ação |
|--------|------|
| `Ctrl+C` | Interrompe a execução atual do Claude |
| `Ctrl+L` | Limpa a tela (sem descartar o contexto) |
| `↑` / `↓` | Navega pelo histórico de mensagens enviadas |
| `Ctrl+R` | Busca no histórico de mensagens |
| `Tab` | Autocompleta comandos slash disponíveis |
| `Esc` | Cancela a mensagem atual (antes de enviar) |
| `Shift+Enter` | Quebra de linha sem enviar a mensagem |

---

## Global vs Local Commands

Custom commands podem ser globais ou locais:

```
~/.claude/commands/     # Global — disponível em todos os projetos
.claude/commands/       # Local — disponível apenas neste projeto
```

Quando há conflito de nome, o comando local tem prioridade.

Para descobrir todos os commands disponíveis:

```
/help
```

ou examine os diretórios:

```bash
ls ~/.claude/commands/
ls .claude/commands/
```

---

## Boas Práticas para Custom Commands

> [!tip] Escreva o `description` no frontmatter pensando em como o usuário pesquisaria pelo comando. O `/help` exibe essas descriptions para ajudar na descoberta.

> [!tip] Use `$ARGUMENTS` para tornar commands versáteis sem precisar criar múltiplos commands similares. Um `/deploy $ARGUMENTS` pode receber "staging", "production" ou "preview" e adaptar o comportamento.

> [!warning] Commands que executam ações destrutivas (deploy, drop de banco, push force) devem ter confirmações explícitas dentro do command, perguntando ao usuário antes de prosseguir.

> [!info] Mantenha commands concisos e focados em UMA ação. Se o command está crescendo muito, considere transformá-lo em uma skill (processo reutilizável) ou quebrar em múltiplos commands menores.

---

## Related

- [[skills-system]] — Skills vs commands: comportamentos vs ações
- [[hooks-system]] — Hooks que disparam em eventos, diferente de commands invocados manualmente
- [[agent-teams]] — Commands que despacham agentes especializados
- [[permissions-and-safety]] — Permissões necessárias para commands que executam bash
- [[00-moc/claude-code-moc]] — Índice geral do Claude Code
