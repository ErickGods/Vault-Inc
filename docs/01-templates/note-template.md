---
tags: [template, docs]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Note Template]
---

# Note Template

> [!template] Como Usar
> Este template é a base para **qualquer nota de conhecimento** nos vaults da Vault Inc. Use-o sempre que criar uma nota nova em `tech-vault/`, `finance-vault/` ou `claude-vault/`. Substitua todos os `{{placeholders}}` pelo conteúdo real. Remova seções que não se aplicam — mas mantenha ao menos Overview, Core Concepts e References. Agentes Claude Code devem usar este template ao criar notas de conhecimento programaticamente.

---

## Template

```markdown
---
tags: [{{categoria}}, {{subcategoria}}]
status: {{draft | active | archived}}
level: {{beginner | intermediate | advanced}}
updated: {{YYYY-MM-DD}}
created: {{YYYY-MM-DD}}
aliases: [{{Alias Principal}}, {{Alias Alternativo}}]
---

# {{Título da Nota}}

> {{Uma frase resumindo o que é este conceito e por que ele importa.}}

## Overview

{{Descreva o conceito em 2-4 parágrafos. Responda: O que é? De onde vem? Qual problema resolve? Quem usa e em que contexto?}}

## Core Concepts

{{Liste os 3-7 fundamentos que qualquer praticante deve entender. Use subseções para conceitos que precisam de mais explicação.}}

### {{Conceito 1}}

{{Explicação do conceito 1. Inclua exemplos concretos quando possível. Use wikilinks para notas relacionadas.}}

### {{Conceito 2}}

{{Explicação do conceito 2.}}

### {{Conceito 3}}

{{Explicação do conceito 3.}}

## Practical Application

{{Descreva como aplicar este conhecimento na prática. Inclua:
- Quando usar
- Passo a passo básico
- Exemplos reais ou hipotéticos relevantes para o contexto da Vault Inc.}}

> [!warning] Gotchas
> {{Liste comportamentos surpreendentes, armadilhas comuns, ou erros frequentes que o leitor precisa evitar. Esta seção salva tempo de debug e de decisões erradas.}}
>
> - **{{Gotcha 1}}:** {{descrição}}
> - **{{Gotcha 2}}:** {{descrição}}

## Snippets

{{Cole exemplos mínimos e funcionais. Use blocos de código com a linguagem correta.}}

\`\`\`{{linguagem}}
# {{Descrição do snippet 1}}
{{código}}
\`\`\`

\`\`\`{{linguagem}}
# {{Descrição do snippet 2}}
{{código}}
\`\`\`

## References

{{Documentação oficial, RFCs, artigos autoritativos, links de cursos relevantes.}}

- [{{Título}}]({{URL}})
- [{{Título}}]({{URL}})

## Related

{{Wikilinks para notas que complementam ou estendem esta.}}

- [[{{nota-relacionada-1}}]] — {{como se relaciona}}
- [[{{nota-relacionada-2}}]] — {{como se relaciona}}
```

---

## Documentação dos Campos de Frontmatter

| Campo | Obrigatório | Valores | Descrição |
|-------|-------------|---------|-----------|
| `tags` | Sim | lista de strings | Primeira tag é a categoria principal (ex: `skill`, `concept`, `framework`); segunda é a subcategoria (ex: `backend`, `finance`, `devops`) |
| `status` | Sim | `draft`, `active`, `archived` | `draft` = em construção; `active` = nota madura e usável; `archived` = desatualizada mas mantida para referência |
| `level` | Não | `beginner`, `intermediate`, `advanced` | Nível de complexidade do conteúdo; omitir em notas que não são educacionais |
| `updated` | Sim | `YYYY-MM-DD` | Data da última atualização significativa do conteúdo |
| `created` | Sim | `YYYY-MM-DD` | Data de criação do arquivo |
| `aliases` | Recomendado | lista de strings | Nomes alternativos pelos quais esta nota pode ser referenciada com wikilinks |

---

## Related

- [[moc-template]] — Template para criar Maps of Content
- [[skill-template]] — Variante específica para notas de skill técnica
- [[🗺️ Docs-Home]] — Central de templates e workflows
