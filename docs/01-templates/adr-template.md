---
tags: [template, docs, architecture]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [ADR Template, Architecture Decision Record Template]
---

# ADR Template — Architecture Decision Record

> [!template] Como Usar
> Use este template para documentar decisões arquiteturais significativas. Toda decisão que afeta a estrutura do sistema, escolha de tecnologia, ou trade-off importante deve ser registrada como ADR. O Lead Engineer agent usa este template automaticamente.

> [!tip] Templater Version
> Para criar ADRs diretamente no Obsidian com prompts interativos, use `tech-vault/08-templates/adr-template.md`.

---

## Template

```yaml
---
tags: [adr, architecture]
adr_number: {{NNNN}}
status: {{proposed | accepted | deprecated | superseded}}
created: {{YYYY-MM-DD}}
updated: {{YYYY-MM-DD}}
---
```

```markdown
# ADR-{{NNNN}}: {{Título da Decisão}}

**Date:** {{YYYY-MM-DD}}
**Status:** {{proposed | accepted | deprecated | superseded}}
**Deciders:** {{quem participou da decisão}}

---

## Context

### Problem Statement
{{Descreva o problema ou necessidade que exige uma decisão arquitetural.}}

### Forces & Constraints
- **Technical:** {{restrição técnica}}
- **Business:** {{restrição de negócio}}
- **Time:** {{restrição de prazo}}
- **Team:** {{restrição de equipe/skills}}

### Options Considered

| Option | Summary | Pros | Cons |
|--------|---------|------|------|
| A — {{nome}} | {{resumo}} | {{prós}} | {{contras}} |
| B — {{nome}} | {{resumo}} | {{prós}} | {{contras}} |
| C — {{nome}} ✅ | {{resumo}} | {{prós}} | {{contras}} |

---

## Decision

**We will** {{declaração da decisão em uma frase}}.

**Rationale:**
- {{Razão 1 — por que esta opção foi escolhida}}
- {{Razão 2}}
- {{Razão 3}}

---

## Consequences

### Positive
- {{Benefício direto 1}}
- {{Benefício direto 2}}

### Negative
- {{Trade-off ou risco 1}}
- {{Trade-off ou risco 2}}

### Neutral
- {{Mudança notável mas neutra}}

---

## Implementation Notes

- [ ] {{Step de implementação 1}}
- [ ] {{Step de implementação 2}}
- [ ] {{Step de implementação 3}}

---

## Related Decisions

- [[adr-{{NNNN}}]] — {{relação: builds on / supersedes / related to}}

## References

- {{Links para docs, RFCs, artigos que informaram a decisão}}
```

---

## Quando Criar um ADR

- Escolha de linguagem, framework, ou banco de dados
- Mudança de arquitetura (monolito → microservices, etc.)
- Adoção ou remoção de dependência significativa
- Trade-off de segurança, performance, ou custo
- Qualquer decisão que alguém perguntaria "por que fizeram assim?"

## Lifecycle

```
proposed → accepted → [deprecated | superseded]
```

- **proposed** — em discussão, ainda não decidido
- **accepted** — decisão tomada, em vigor
- **deprecated** — não mais relevante (tecnologia removida)
- **superseded** — substituído por ADR mais recente (linkar)

## Related

- [[project-intake-template]] — intake que pode gerar ADRs
- [[new-project-workflow]] — workflow onde ADRs são criados
