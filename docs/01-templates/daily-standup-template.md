---
tags: [template, docs, standup]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Daily Standup Template, Standup Template]
---

# Daily Standup Template

> [!template] Como Usar
> Use este template para registrar o standup diário. Cada agente da Vault Inc documenta seu trabalho do dia neste formato. Standups são salvos em `vault/standups/YYYY-MM-DD.md`.

---

## Template

```yaml
---
tags: [standup, {{YYYY-MM-DD}}]
date: {{YYYY-MM-DD}}
created: {{YYYY-MM-DD}}
---
```

```markdown
# Standup — {{YYYY-MM-DD}}

---

## {{Nome do Agente / Pessoa}}

### ✅ O que fiz (ontem/hoje)
- {{Tarefa concluída 1}}
- {{Tarefa concluída 2}}

### 🔄 O que vou fazer (hoje/amanhã)
- {{Próxima tarefa 1}}
- {{Próxima tarefa 2}}

### 🚧 Blockers
- {{Bloqueio 1 — quem pode ajudar: @{{responsável}}}}
- {{Nenhum blocker}}

---

## {{Próximo Agente / Pessoa}}

### ✅ O que fiz
- {{...}}

### 🔄 O que vou fazer
- {{...}}

### 🚧 Blockers
- {{...}}
```

---

## Convenções

- Um arquivo por dia, todos os agentes/pessoas no mesmo arquivo
- Salvar em `vault/standups/YYYY-MM-DD.md`
- Blockers devem mencionar quem pode desbloquear
- Se não há blocker, escrever "Nenhum blocker"

## Related

- [[weekly-review-template]] — consolida standups da semana
- [[new-project-workflow]] — workflow onde standups acontecem
