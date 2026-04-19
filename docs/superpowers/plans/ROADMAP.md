---
tags: [roadmap, meta, plans]
status: active
updated: 2026-04-19
---

# 🗺️ Roadmap — Vault Inc Library

Visão consolidada de todos os planos de implementação da Vault Inc Library.

> [!info] Para que serve este arquivo?
> Este é o índice central dos planos de execução. Cada plano representa uma expansão ou melhoria da livraria. Os planos ficam exclusivamente em `docs/superpowers/plans/` — eles **não aparecem** nos vaults de conhecimento (tech-vault, finance-vault) para não criar ruído na navegação principal.

> [!tip] Como usar
> - Para **executar** um plano pendente: abra o arquivo do plan e use a skill `superpowers:subagent-driven-development`
> - Para **criar** um novo plano: use a skill `superpowers:brainstorming` → `superpowers:writing-plans`
> - Para **atualizar** o status aqui: edite o campo `progress` do frontmatter do plan e atualize a tabela abaixo

---

## 📊 Status dos Planos

| Plano | Objetivo | Status | Progresso | Layer |
|-------|----------|--------|-----------|-------|
| [Tech Vault Setup](2026-04-05-tech-vault.md) | Setup inicial da estrutura do tech-vault | ✅ Concluído | 100% | tech-vault |
| [Vault Library Expansion](2026-04-10-vault-library-expansion.md) | ~73 arquivos: docs, claude-vault, integrações | 🔄 Em andamento | 15% | multi-vault |
| [AI Fundamentals](2026-04-14-ai-fundamentals.md) | 13 arquivos deep-technical LLM/AI | ✅ Concluído | 100% | tech-vault |

---

## 🧭 Direção Estratégica

A Vault Inc Library evolui em ondas concêntricas — cada onda consolida uma camada antes de expandir para a próxima.

### Onda 1 — Fundação (✅ Concluída)
Estrutura base do tech-vault: MOCs, pastas numeradas, snippets, templates Templater, canvas de data pipeline.

### Onda 2 — Profundidade Técnica (🔄 Em andamento)
- **AI/ML Fundamentals** (✅): 13 arquivos deep-technical sobre como LLMs funcionam internamente
- **Data Engineering** (✅ canvas corrigido, conteúdo pendente): kafka, airflow, spark, flink, delta lake, duckdb, dbt
- **Docs layer** (🔄 parcial): templates plain-markdown para humanos e agentes, canvas de arquitetura, workflows de processo

### Onda 3 — Claude Vault (⏳ Planejada)
Documentação dos próprios agentes e skills da Vault Inc — como o sistema multi-agente funciona, como criar novos agentes, padrões de uso do Claude Code.

### Onda 4 — Integração (⏳ Planejada)
Wikilinks cruzados entre os três vaults (tech ↔ finance ↔ claude), arquivos-ponte que conectam conhecimento técnico com aplicação financeira e execução de projetos.

---

## 🔄 Próximas Entregas

Em ordem de prioridade:

1. **Conteúdo do Data Engineering** — preencher os arquivos que o canvas data-pipeline-map.canvas referencia: kafka, airflow, spark, flink, delta lake, data lake patterns, duckdb, dbt
2. **Completar Vault Library Expansion** — Templates pendentes (moc-template, skill-template, agent-template, project-intake-template, equity-research-template, meeting-notes, weekly-review, daily-standup), workflows (03-workflows/), claude-vault (Tasks 9–17), wikilinks (Tasks 18–21)
3. **Finance Vault** — Expandir o vault financeiro com análise de ativos, modelos de valuation, teses de investimento

---

## 📁 Estrutura dos Planos

```
docs/superpowers/
├── plans/
│   ├── ROADMAP.md          ← você está aqui
│   ├── 2026-04-05-tech-vault.md
│   ├── 2026-04-10-vault-library-expansion.md
│   └── 2026-04-14-ai-fundamentals.md
└── specs/
    ├── 2026-04-05-tech-vault-design.md
    ├── 2026-04-10-vault-library-expansion-design.md
    └── 2026-04-14-ai-fundamentals-design.md
```

> [!note] Convenção de nomenclatura
> Plans: `YYYY-MM-DD-<feature-name>.md`
> Specs: `YYYY-MM-DD-<feature-name>-design.md`
> Todo novo plano começa com brainstorming → spec → plan.
