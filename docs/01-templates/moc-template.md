---
tags: [template, docs, moc]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [MOC Template, Map of Content Template]
---

# MOC Template

> [!template] Como Usar
> Use este template ao criar um novo Map of Content (MOC). MOCs são índices temáticos que agrupam e organizam notas relacionadas. Cada vault/seção principal deve ter seu MOC.

---

## Template

```yaml
---
tags: [moc, {{dominio}}]
status: active
complexity: basic
context: global
updated: {{YYYY-MM-DD}}
created: {{YYYY-MM-DD}}
aliases: [{{Nome do MOC}}, {{Alias}}]
---
```

```markdown
# 🗺️ {{Nome do Domínio}} MOC

## Visão Geral

{{Descrição do domínio coberto por este MOC. O que o leitor encontra aqui?
Qual é o escopo e o propósito desta coleção de notas?}}

> [!info] Cobertura
> Esta seção (`{{path/}}`) contém {{N}} arquivos organizados em {{categorias}}.

---

## 📊 Dashboard

\```dataview
TABLE status, level, updated
FROM "{{path-do-vault/secao}}"
WHERE file.name != "🗺️ {{Nome}}"
SORT updated DESC
\```

---

## 🗺️ Skills Map

### {{Categoria 1}}

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[{{arquivo-1}}]] | {{descrição}} | ✅ active |
| [[{{arquivo-2}}]] | {{descrição}} | 🚧 draft |

### {{Categoria 2}}

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[{{arquivo-3}}]] | {{descrição}} | ✅ active |

---

## ⚡ Quick Access

- [[{{nota-essencial-1}}]] — {{por que é essencial}}
- [[{{nota-essencial-2}}]] — {{por que é essencial}}
- [[{{nota-essencial-3}}]] — {{por que é essencial}}

---

## 🔗 Conexões com Outros Vaults

- **{{Vault 1}}** → [[{{moc-relacionado}}]] — {{relação}}
- **{{Vault 2}}** → [[{{moc-relacionado}}]] — {{relação}}
```

---

## Boas Práticas para MOCs

1. **Mantenha atualizado** — adicione novas notas ao MOC quando criá-las
2. **Use dataview** — queries automáticas evitam MOCs desatualizados
3. **Link bidirecional** — cada nota listada no MOC deve linkar de volta ao MOC
4. **Seção Quick Access** — as 3-5 notas mais consultadas em destaque
5. **Conexões entre vaults** — sempre incluir links para MOCs de outros domínios

## Related

- [[note-template]] — template base para notas
- [[🗺️ Docs-Home]] — MOC principal do docs
