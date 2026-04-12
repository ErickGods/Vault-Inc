---
tags: [moc, home, docs]
status: active
complexity: basic
context: global
updated: 2026-04-10
created: 2026-04-10
aliases: [Docs Home, Templates Home]
---

# 🗺️ Docs — Central de Templates & Workflows

## Visão Geral

Este vault é o repositório central de **templates, canvas e workflows** da Vault Inc. Aqui vivem os artefatos de processo que padronizam como criamos notas, definimos agentes, documentamos decisões e estruturamos o conhecimento em todos os vaults.

O `docs/` foi projetado para ser consumido tanto por **humanos** (usando os templates diretamente no Obsidian) quanto por **agentes Claude Code** (que leem e seguem os padrões aqui definidos para gerar artefatos consistentes).

> [!info] Templater vs. Plain Markdown
> O vault `tech-vault/08-templates/` contém versões dos templates com **Templater** — elas usam `<%* ... %>` para prompts interativos no Obsidian e renomeiam arquivos automaticamente. As versões aqui em `docs/01-templates/` são **plain markdown** com placeholders `{{como-este}}`, pensadas para agentes Claude Code que não executam Templater. Use a versão certa para o contexto certo:
> - **Humano no Obsidian** → use `tech-vault/08-templates/`
> - **Agente Claude Code** → use `docs/01-templates/`

---

## 📄 Templates

| Template | Link | Finalidade | Consumido por |
|----------|------|-----------|---------------|
| Note Template | [[note-template]] | Base para qualquer nota de conhecimento | Humanos + Agentes |
| MOC Template | [[moc-template]] | Criar Maps of Content para um domínio | Humanos + Agentes |
| Skill Template | [[skill-template]] | Documentar uma skill técnica no tech-vault | Humanos + Agentes |
| Agent Template | [[agent-template]] | Definir um agente Claude Code em `.claude/agents/` | Agentes |
| ADR Template | [[adr-template]] | Registrar uma Architecture Decision Record | Humanos + Agentes |
| Project Template | [[project-template]] | Criar estrutura inicial de projeto | Agentes |
| Stock Analysis Template | [[stock-analysis-template]] | Análise fundamentalista de ação | Humanos |
| Weekly Review Template | [[weekly-review]] | Revisão semanal de progresso | Humanos |
| QA Report Template | [[qa-report-template]] | Relatório de testes e qualidade | Agentes |
| Security Audit Template | [[security-audit-template]] | Relatório de auditoria de segurança | Agentes |

---

## 🖼️ Canvas

| Canvas | Link | Finalidade |
|--------|------|-----------|
| Vault Inc Architecture | [[vault-inc-architecture]] | Visão macro da estrutura de agentes e vaults |
| Agent Workflow | [[agent-workflow-canvas]] | Fluxo de execução de projetos entre agentes |
| Knowledge Map | [[knowledge-map-canvas]] | Mapa visual das conexões entre os três vaults |
| Finance Decision Tree | [[finance-decision-canvas]] | Árvore de decisão para seleção de investimentos |
| Tech Stack Canvas | [[tech-stack-canvas]] | Stack tecnológico padrão da Vault Inc |

---

## ⚙️ Workflows

| Workflow | Link | Finalidade |
|----------|------|-----------|
| Novo Projeto End-to-End | [[workflow-novo-projeto]] | Passo a passo desde intake até fechamento |
| Criação de Nota de Conhecimento | [[workflow-nova-nota]] | Como criar e categorizar novas notas nos vaults |
| Code Review com Agentes | [[workflow-code-review]] | Fluxo de revisão usando Lead Engineer + QA |
| Deploy com DevOps | [[workflow-deploy]] | Processo de deploy com Docker e CI/CD |
| Pesquisa de Investimento | [[workflow-research-investimento]] | Pipeline de análise fundamentalista de ativos |

---

## 📊 Dashboard — Notas Recentes

```dataview
TABLE status, type, updated
FROM "docs"
WHERE updated >= date(today) - dur(30 days)
SORT updated DESC
LIMIT 20
```

---

## 🔗 Conexões com Outros Vaults

| Vault | Home | Domínio |
|-------|------|---------|
| Tech Vault | [[tech-vault/00-moc/🗺️ Home\|🖥️ Tech Home]] | Skills técnicas, snippets, arquitetura, DevOps, AI/ML |
| Finance Vault | [[finance-vault/00-MOC/🗺️ Home\|💰 Finance Home]] | Investimentos, análise, finanças pessoais, macroeconomia |

---

*Docs vault criado em 2026-04-10. Templates são artefatos vivos — atualize-os conforme os padrões da Vault Inc evoluem.*
