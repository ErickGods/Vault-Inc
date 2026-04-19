---
tags: [template, docs, meetings]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Meeting Notes Template, Ata de Reunião Template]
---

# Meeting Notes Template

> [!template] Como Usar
> Use este template para registrar qualquer reunião, call ou sync. Preencha durante ou imediatamente após a reunião. Action items com checkboxes aparecem automaticamente nos dashboards do Obsidian Tasks.

---

## Template

```yaml
---
tags: [meeting, {{tipo: sync | planning | review | 1on1 | client}}]
status: {{active | archived}}
date: {{YYYY-MM-DD}}
participants: [{{nome1}}, {{nome2}}]
project: {{nome-do-projeto ou "general"}}
created: {{YYYY-MM-DD}}
---
```

```markdown
# {{Título da Reunião}} — {{YYYY-MM-DD}}

**Tipo:** {{Sync | Planning | Review | 1:1 | Client Call}}
**Duração:** {{HH:MM - HH:MM}}
**Participantes:** {{lista}}

---

## Agenda

1. {{Tópico 1}}
2. {{Tópico 2}}
3. {{Tópico 3}}

---

## Notas

### {{Tópico 1}}
{{Anotações sobre o que foi discutido.}}

### {{Tópico 2}}
{{Anotações.}}

---

## Decisões

| # | Decisão | Responsável |
|---|---------|-------------|
| 1 | {{decisão tomada}} | {{quem}} |
| 2 | {{decisão tomada}} | {{quem}} |

---

## Action Items

- [ ] {{Ação 1}} — @{{responsável}} 📅 {{YYYY-MM-DD}}
- [ ] {{Ação 2}} — @{{responsável}} 📅 {{YYYY-MM-DD}}
- [ ] {{Ação 3}} — @{{responsável}} 📅 {{YYYY-MM-DD}}

---

## Follow-up

- Próxima reunião: {{data ou "a definir"}}
- Tópicos pendentes para próxima: {{lista}}
```

## Related

- [[weekly-review-template]] — consolidar meetings da semana
- [[daily-standup-template]] — standup diário
