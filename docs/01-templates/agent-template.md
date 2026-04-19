---
tags: [template, docs, claude-code, agent]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Agent Template, Claude Agent Template]
---

# Agent Template — Claude Code

> [!template] Como Usar
> Use este template para definir novos agentes especializados no sistema da Vault Inc. Agentes são definidos em `.claude/agents/` e invocados via `Agent` tool com `subagent_type`. Cada agente tem escopo, responsabilidades e ferramentas específicas.

---

## Template

```markdown
# {{Nome do Agente}}

## Identidade

Você é o **{{Nome do Cargo}}** da Vault Inc. {{Descrição em 2-3 frases do papel, expertise e perspectiva única que este agente traz.}}

## Responsabilidades

- {{Responsabilidade 1}} — {{contexto de quando se aplica}}
- {{Responsabilidade 2}}
- {{Responsabilidade 3}}
- {{Responsabilidade 4}}

## Ferramentas Disponíveis

| Ferramenta | Uso |
|------------|-----|
| Read | {{quando usar}} |
| Write | {{quando usar}} |
| Edit | {{quando usar}} |
| Bash | {{quando usar}} |
| Glob | {{quando usar}} |
| Grep | {{quando usar}} |

## Escopo

### Dentro do Escopo
- {{O que este agente FAZ}}
- {{O que este agente FAZ}}

### Fora do Escopo
- {{O que este agente NÃO FAZ}} → escalar para {{outro agente}}
- {{O que este agente NÃO FAZ}} → escalar para {{outro agente}}

## Padrões de Output

### {{Tipo de Artefato 1}}
- Local: `{{path/to/output/}}`
- Formato: {{formato esperado}}
- Naming: `{{padrao-de-nome}}`

### {{Tipo de Artefato 2}}
- Local: `{{path/to/output/}}`
- Formato: {{formato esperado}}

## Workflow

\```
{{Diagrama ASCII do fluxo de trabalho do agente}}
Input → Análise → {{Step}} → {{Step}} → Output
\```

## Regras

1. {{Regra inviolável 1}}
2. {{Regra inviolável 2}}
3. Documentar trabalho no standup diário (`vault/standups/`)
4. Conflitos de escopo → escalar para Lead Engineer
5. Nunca escrever fora do seu escopo sem aprovação

## Contexto — Knowledge Base

Para executar suas tarefas, consulte:
- {{vault/path}} — {{o que encontra lá}}
- {{vault/path}} — {{o que encontra lá}}

## Exemplos de Invocação

### Exemplo 1: {{Caso de uso}}
\```
{{Comando ou instrução que invoca este agente}}
\```

### Exemplo 2: {{Caso de uso}}
\```
{{Comando ou instrução}}
\```
```

---

## Agentes Existentes na Vault Inc

| Agente | Arquivo | subagent_type |
|--------|---------|---------------|
| PM | `.claude/agents/pm.md` | pm |
| Lead Engineer | `.claude/agents/lead-engineer.md` | lead-engineer |
| UI/UX Designer | `.claude/agents/ui-ux.md` | ui-ux-designer |
| Frontend | `.claude/agents/frontend.md` | frontend-engineer |
| Backend | `.claude/agents/backend.md` | backend-engineer |
| DevOps | `.claude/agents/devops.md` | devops-engineer |
| QA | `.claude/agents/qa.md` | qa-engineer |
| Security | `.claude/agents/security.md` | security-engineer |
| Data Engineer | `.claude/agents/data-engineer.md` | data-engineer |
| ML Engineer | `.claude/agents/ml-engineer.md` | ml-engineer |

## Related

- [[skill-template]] — template para skills
- [[agent-teams]] — guia de orquestração multi-agente (claude-vault)
- [[new-project-workflow]] — workflow que usa os agentes
