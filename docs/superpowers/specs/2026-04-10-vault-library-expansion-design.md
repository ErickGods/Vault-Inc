---
tags: [spec, design, vault-inc-library]
status: approved
created: 2026-04-10
updated: 2026-04-10
---

# Vault Inc Library — Expansion Design Spec

## Objetivo

Expandir a Vault-Inc-Library para funcionar como o cérebro central completo da Vault Inc, preenchendo as áreas vazias (claude-vault, docs) e conectando os vaults existentes (tech-vault, finance-vault) através de links cruzados e arquivos-ponte.

## Contexto

### Estado Atual (2026-04-10)

| Vault | Arquivos | Status |
|-------|----------|--------|
| finance-vault | ~80 | Muito completo |
| tech-vault | ~70 | Bem preenchido |
| claude-vault | 0 | Vazio |
| docs | 2 (apenas planos superpowers) | Vazio |

### Decisões de Design

- **Abordagem:** Layered (camadas progressivas)
- **Público:** Híbrido (humanos + agentes de IA)
- **Escopo claude-vault:** Ecossistema Anthropic/Claude Code + extensões (MCPs, plugins terceiros)
- **Escopo docs:** Templates operacionais + templates para agentes
- **Profundidade:** Enciclopédica (~400-800+ linhas por arquivo)
- **Links cruzados:** Wikilinks + arquivos-ponte para temas na interseção
- **Prioridade:** docs primeiro → claude-vault core → claude-vault completo → integração

## Padrão de Arquivos

Todos os arquivos seguem o padrão já estabelecido no vault:

```yaml
---
tags: [tag1, tag2]
status: active | draft | review
level: basic | intermediate | advanced
updated: YYYY-MM-DD
created: YYYY-MM-DD
aliases: [Alias 1, Alias 2]
---
```

### Estrutura Interna (claude-vault — nível enciclopédico)

1. **O que é** — conceito explicado para humanos
2. **Como funciona** — arquitetura/mecânica
3. **Como configurar/usar** — passo a passo prático
4. **Exemplos completos** — código funcional, não fragmentos
5. **Catálogo/Comparativo** — quando aplicável
6. **Gotchas** — callouts `> [!warning]` com armadilhas
7. **Snippets** — blocos prontos para copiar
8. **Related** — wikilinks para arquivos relacionados

### Estrutura Interna (docs — templates)

1. Frontmatter YAML com `type: template`
2. Seção "Como Usar" — quando e como usar o template
3. Placeholders com `{{variavel}}`
4. Callout `> [!template]` indicando template

### Estrutura Interna (docs — workflows)

1. Diagrama de fluxo em mermaid
2. Steps numerados com checkboxes
3. Links para templates relevantes em cada step
4. Seção "Quando usar" e "Output esperado"

### Canvas

- Layout pré-definido com cards placeholder
- Cores padronizadas: azul = tech, verde = finance, roxo = agentes
- Instruções embutidas nos cards

---

## Camada 1 — Fundação (docs/)

### Estrutura

```
docs/
├── 00-moc/
│   └── 🗺️ Docs-Home.md
├── 01-templates/
│   ├── note-template.md
│   ├── moc-template.md
│   ├── skill-template.md
│   ├── agent-template.md
│   ├── adr-template.md
│   ├── project-intake-template.md
│   ├── equity-research-template.md
│   ├── meeting-notes-template.md
│   ├── weekly-review-template.md
│   └── daily-standup-template.md
├── 02-canvas/
│   ├── project-kickoff.canvas
│   ├── brainstorm-board.canvas
│   ├── tech-architecture.canvas
│   ├── pitchbook-layout.canvas
│   └── agent-workflow.canvas
├── 03-workflows/
│   ├── new-project-workflow.md
│   ├── equity-research-workflow.md
│   ├── agent-creation-workflow.md
│   ├── vault-maintenance-workflow.md
│   └── code-review-workflow.md
└── superpowers/ (já existe, manter)
    ├── plans/
    └── specs/
```

### Arquivos: 21 (10 templates + 5 canvas + 5 workflows + 1 MOC)

### Descrição dos Templates

| Template | Propósito | Consumido por |
|----------|-----------|---------------|
| note-template | Base para qualquer nota nova no vault | Humanos |
| moc-template | Criar novos Maps of Content | Humanos |
| skill-template | Criar skills do Claude Code | Humanos + Agentes |
| agent-template | Definir novos agentes em .claude/agents/ | Humanos + Agentes |
| adr-template | Architecture Decision Records | Lead Engineer agent |
| project-intake-template | Intake de novo projeto | PM agent |
| equity-research-template | Relatório de equity research | Financial Research agents |
| meeting-notes-template | Atas de reunião | Humanos |
| weekly-review-template | Review semanal da empresa | Humanos + PM agent |
| daily-standup-template | Standup diário dos agentes | Agentes |

### Descrição dos Canvas

| Canvas | Propósito |
|--------|-----------|
| project-kickoff | Visão geral de um novo projeto: stakeholders, timeline, riscos, deliverables |
| brainstorm-board | Board livre para brainstorming com áreas: ideias, prós/contras, decisão |
| tech-architecture | Diagrama de arquitetura: services, databases, APIs, infra |
| pitchbook-layout | Layout para pitchbooks financeiros: capa, tese, números, projeções |
| agent-workflow | Fluxo visual dos 10 agentes: quem chama quem, dependências |

### Descrição dos Workflows

| Workflow | Propósito |
|----------|-----------|
| new-project-workflow | Passo a passo completo: intake → PM → agentes → entrega → closure |
| equity-research-workflow | Fluxo de análise de ação: screening → fundamentals → valuation → report |
| agent-creation-workflow | Como criar e configurar um novo agente na Vault Inc |
| vault-maintenance-workflow | Manutenção periódica: revisar arquivos, atualizar links, limpar drafts |
| code-review-workflow | Processo de review com agentes: implementer → reviewer → approval |

---

## Camada 2 — Claude Vault Core

### Estrutura

```
claude-vault/
├── 00-moc/
│   └── 🗺️ Claude-Home.md
├── 01-fundamentals/
│   ├── what-is-claude-code.md
│   ├── claude-models-overview.md
│   ├── claude-code-vs-api-vs-chat.md
│   ├── context-window-management.md
│   └── pricing-and-tokens.md
├── 02-core-features/
│   ├── skills-system.md
│   ├── hooks-system.md
│   ├── mcp-servers.md
│   ├── subagents.md
│   ├── agent-teams.md
│   ├── worktrees.md
│   ├── slash-commands.md
│   └── permissions-and-safety.md
├── 03-advanced/
│   ├── ultrathink.md
│   ├── prompt-engineering-for-claude.md
│   ├── claude-md-guide.md
│   ├── memory-system.md
│   ├── plan-mode.md
│   └── settings-and-config.md
└── 04-api-and-sdk/
    ├── claude-api-reference.md
    ├── anthropic-sdk-python.md
    ├── anthropic-sdk-typescript.md
    ├── claude-agent-sdk.md
    └── batch-api.md
```

### Arquivos: 21 (1 MOC + 5 fundamentals + 8 core + 6 advanced + 5 API)

### Prioridade de Escrita (dentro da Camada 2)

1. `🗺️ Claude-Home.md` — MOC primeiro, serve de índice
2. `skills-system.md` — recurso mais usado no dia a dia
3. `mcp-servers.md` — extensibilidade central
4. `hooks-system.md` — automação de eventos
5. `subagents.md` + `agent-teams.md` — orquestração
6. `claude-md-guide.md` — configuração do projeto
7. `what-is-claude-code.md` + demais fundamentals
8. `worktrees.md` + `ultrathink.md` + demais advanced
9. `claude-api-reference.md` + demais API/SDK

---

## Camada 3 — Claude Vault Completo

### Estrutura (continuação do claude-vault)

```
claude-vault/
├── 05-plugins-and-extensions/
│   ├── mcp-catalog.md
│   ├── ide-integrations.md
│   ├── superpowers-plugin.md
│   ├── third-party-tools.md
│   └── building-plugins.md
├── 06-patterns-and-recipes/
│   ├── tdd-with-claude.md
│   ├── code-review-with-agents.md
│   ├── project-scaffolding.md
│   ├── financial-analysis-with-claude.md    ← arquivo-ponte
│   ├── debugging-workflow.md
│   └── documentation-generation.md
├── 07-snippets/
│   ├── skill-snippets.md
│   ├── hook-snippets.md
│   ├── mcp-server-snippets.md
│   ├── api-snippets.md
│   └── claude-md-snippets.md
├── 08-troubleshooting/
│   ├── common-errors.md
│   ├── performance-tips.md
│   ├── context-overflow.md
│   └── debugging-agents.md
└── 09-glossary/
    └── claude-glossary.md
```

### Arquivos: 21 (5 plugins + 6 recipes + 5 snippets + 4 troubleshooting + 1 glossary)

### Destaques

- `mcp-catalog.md` — arquivo mais extenso, catálogo vivo organizado por categoria (dados, filesystem, APIs, dev tools, finance) com descrição, install, exemplo, rating
- `financial-analysis-with-claude.md` — arquivo-ponte principal claude↔finance (projeções, relatórios, pitchbooks com IA)
- Snippets otimizados para consulta rápida e copy-paste por agentes

---

## Camada 4 — Integração

### Wikilinks a Adicionar

| De | Para | Tipo |
|----|------|------|
| finance-vault/10-snippets/python-finance-snippets.md | tech-vault/01-skills/languages/python.md | Wikilink |
| finance-vault/03-analysis/quantitative/backtesting-basics.md | tech-vault/05-data-engineering/ | Wikilink |
| tech-vault/03-ai-ml/* | claude-vault/ equivalentes | Wikilinks (migrar referências) |
| tech-vault/01-skills/tools/claude-code.md | claude-vault/01-fundamentals/what-is-claude-code.md | Wikilink |
| finance-vault/agents/ | claude-vault/02-core-features/agent-teams.md | Wikilink |

### Arquivos-Ponte (novos)

| Arquivo | Localização | Conecta |
|---------|-------------|---------|
| financial-analysis-with-claude.md | claude-vault/06-patterns/ | claude ↔ finance |
| fintech-automation.md | tech-vault/06-snippets/ | tech ↔ finance |
| python-projections-finance.md | tech-vault/06-snippets/ | tech ↔ finance |
| pitchbook-generation.md | claude-vault/06-patterns/ | claude ↔ finance ↔ docs |
| ai-for-equity-research.md | claude-vault/06-patterns/ | claude ↔ finance |

### MOCs a Atualizar

| MOC | Ação |
|-----|------|
| tech-vault/00-moc/ | Criar MOC Home (não existe) |
| tech-vault/00-moc/ai-ml-moc.md | Adicionar links para claude-vault |
| finance-vault/00-MOC/🗺️ Home.md | Adicionar seção "Tech & Automação" |
| claude-vault/00-moc/🗺️ Claude-Home.md | Seção "Integrações" com links para outros vaults |

---

## Resumo de Entregas

| Camada | Escopo | Arquivos | Dependência |
|--------|--------|----------|-------------|
| 1 — Fundação | docs/ (templates, canvas, workflows) | ~21 | Nenhuma |
| 2 — Claude Core | claude-vault/ pastas 01-04 | ~21 | Camada 1 (usa templates como base) |
| 3 — Claude Completo | claude-vault/ pastas 05-09 | ~21 | Camada 2 (conteúdo core já existe) |
| 4 — Integração | Links, pontes, MOCs | ~10 | Camadas 1-3 (todos os arquivos existem) |
| **Total** | | **~73** | |

## Critérios de Qualidade

- Todo arquivo tem frontmatter YAML válido
- Todo arquivo tem pelo menos 1 wikilink para arquivo relacionado
- Templates têm placeholders `{{variavel}}` documentados
- Workflows têm diagrama mermaid + checkboxes
- Canvas têm cores padronizadas (azul/verde/roxo)
- Conteúdo em Português BR, termos técnicos em inglês quando padrão da indústria
- Callouts Obsidian usados consistentemente (tip, warning, info, example, template)
- Cada MOC tem dataview query para dashboard automático
