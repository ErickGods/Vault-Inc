---
tags: [template, docs, review]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Weekly Review Template, Review Semanal Template]
---

# Weekly Review Template

> [!template] Como Usar
> Use este template toda sexta-feira (ou início da semana seguinte) para revisar o progresso, consolidar aprendizados e planejar a próxima semana. O PM agent pode gerar este review automaticamente.

> [!tip] Templater Version
> Para gerar com prompts interativos no Obsidian, use `tech-vault/08-templates/weekly-review.md`.

---

## Template

```yaml
---
tags: [weekly-review, {{YYYY}}]
week: {{W##}}
period_start: {{YYYY-MM-DD}}
period_end: {{YYYY-MM-DD}}
energy: {{1-5}}
focus: {{1-5}}
created: {{YYYY-MM-DD}}
---
```

```markdown
# Weekly Review — {{W##}} ({{start}} → {{end}})

> **Highlight:** {{Uma frase sobre o destaque da semana}}
> **Energy:** {{N}}/5 | **Focus:** {{N}}/5

---

## Wins

- {{O que deu certo 1}}
- {{O que deu certo 2}}
- {{O que deu certo 3}}

## Challenges

- {{O que foi difícil ou bloqueou 1}}
- {{O que foi difícil 2}}

## Learnings

- {{Insight técnico, pessoal, ou de processo 1}}
- {{Insight 2}}

## Next Week Goals

- [ ] {{Goal 1}} 📅 {{YYYY-MM-DD}}
- [ ] {{Goal 2}} 📅 {{YYYY-MM-DD}}
- [ ] {{Goal 3}} 📅 {{YYYY-MM-DD}}

---

## Tasks Completed This Week

\```dataview
TASK
FROM ""
WHERE completed = true
  AND completion >= date("{{period_start}}")
  AND completion <= date("{{period_end}}")
SORT completion ASC
\```

---

## Metrics

| Metric | Value |
|--------|-------|
| Commits / PRs | {{N}} |
| New notes created | {{N}} |
| Deep-work hours | {{N}} |
```

## Related

- [[daily-standup-template]] — standups diários que alimentam o review
- [[meeting-notes-template]] — meetings da semana
