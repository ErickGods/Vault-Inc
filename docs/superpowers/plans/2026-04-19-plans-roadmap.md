# Plans Roadmap — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar um sistema de roadmap centralizado em `docs/superpowers/plans/ROADMAP.md` que consolida o status e direção de todos os planos de implementação da Vault Inc Library, sem poluir os vaults de conhecimento (tech-vault, finance-vault).

**Architecture:** Abordagem de documento estático + frontmatter. Cada plan file recebe metadados YAML padronizados (`status`, `goal`, `progress`, `layer`). O ROADMAP.md agrega esses planos manualmente em tabelas e seções de direção estratégica — sem Dataview (que requer plugin ativo) para máxima compatibilidade. O roadmap vive exclusivamente em `docs/superpowers/` e não cria links nos vaults de conhecimento.

**Tech Stack:** Obsidian Markdown, YAML frontmatter, Obsidian callouts

---

## File Structure

| Arquivo | Ação | Responsabilidade |
|---------|------|-----------------|
| `docs/superpowers/plans/ROADMAP.md` | Create | Índice central de todos os plans com status, progresso e direção estratégica |
| `docs/superpowers/plans/2026-04-05-tech-vault.md` | Modify (início) | Adicionar frontmatter com metadados de status |
| `docs/superpowers/plans/2026-04-10-vault-library-expansion.md` | Modify (início) | Adicionar frontmatter com metadados de status |
| `docs/superpowers/plans/2026-04-14-ai-fundamentals.md` | Modify (início) | Adicionar frontmatter com metadados de status + marcar checkboxes como concluídos |

---

## Task 1: Adicionar frontmatter ao plan tech-vault (2026-04-05)

**Files:**
- Modify: `docs/superpowers/plans/2026-04-05-tech-vault.md` (início do arquivo)

- [ ] **Step 1: Verificar o início atual do arquivo**

```bash
head -5 docs/superpowers/plans/2026-04-05-tech-vault.md
```

Expected: linha começando com `# Tech Vault` sem frontmatter YAML.

- [ ] **Step 2: Inserir frontmatter no início do arquivo**

Adicionar antes da primeira linha `# Tech Vault...`:

```yaml
---
tags: [plan, completed, tech-vault]
status: completed
progress: 100
goal: Setup inicial da estrutura do tech-vault com MOCs, pastas e arquivos base
layer: tech-vault
created: 2026-04-05
updated: 2026-04-05
---
```

- [ ] **Step 3: Verificar que o arquivo ficou correto**

```bash
head -12 docs/superpowers/plans/2026-04-05-tech-vault.md
```

Expected: frontmatter YAML seguido do título `# Tech Vault`.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-04-05-tech-vault.md
git commit -m "docs(plans): add status frontmatter to tech-vault plan"
```

---

## Task 2: Adicionar frontmatter ao plan vault-library-expansion (2026-04-10)

**Files:**
- Modify: `docs/superpowers/plans/2026-04-10-vault-library-expansion.md` (início do arquivo)

- [ ] **Step 1: Verificar o início atual do arquivo**

```bash
head -5 docs/superpowers/plans/2026-04-10-vault-library-expansion.md
```

Expected: linha começando com `# Vault Inc Library Expansion` sem frontmatter YAML.

- [ ] **Step 2: Inserir frontmatter no início do arquivo**

Adicionar antes da primeira linha `# Vault Inc Library Expansion...`:

```yaml
---
tags: [plan, in-progress, library-expansion]
status: in-progress
progress: 15
goal: Expandir a Vault-Inc-Library com ~73 novos arquivos em 4 camadas — docs, claude-vault core, claude-vault completo e integração entre vaults
layer: multi-vault
created: 2026-04-10
updated: 2026-04-19
tasks_total: 21
tasks_done: 3
---
```

> **Nota de progresso:** Tasks concluídas: Task 1 (estrutura de diretórios), Task 2 (Docs-Home.md), Task 7 (canvas files). Tasks parcialmente feitas: Task 3 (note-template), Task 5 (adr-template). Tasks pendentes: 3, 4, 6, 8-21.

- [ ] **Step 3: Verificar que o arquivo ficou correto**

```bash
head -15 docs/superpowers/plans/2026-04-10-vault-library-expansion.md
```

Expected: frontmatter YAML com 9 campos seguido do título e conteúdo do plan.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-04-10-vault-library-expansion.md
git commit -m "docs(plans): add status frontmatter to library-expansion plan"
```

---

## Task 3: Adicionar frontmatter ao plan ai-fundamentals (2026-04-14) e marcar como concluído

**Files:**
- Modify: `docs/superpowers/plans/2026-04-14-ai-fundamentals.md` (início do arquivo)

- [ ] **Step 1: Verificar o início atual do arquivo**

```bash
head -5 docs/superpowers/plans/2026-04-14-ai-fundamentals.md
```

Expected: linha começando com `# AI Fundamentals` sem frontmatter YAML.

- [ ] **Step 2: Inserir frontmatter no início do arquivo**

Adicionar antes da primeira linha `# AI Fundamentals...` (ou `# LLM/AI Fundamentals...`):

```yaml
---
tags: [plan, completed, ai-ml, fundamentals]
status: completed
progress: 100
goal: Criar 13 arquivos deep-technical sobre fundamentos de LLMs — transformers, tokenização, embeddings, pretraining, fine-tuning, RLHF, KV cache, quantização, inference engines, GPU, hardware especializado, VRAM estimation e benchmarks
layer: tech-vault
created: 2026-04-14
updated: 2026-04-19
tasks_total: 13
tasks_done: 13
---
```

- [ ] **Step 3: Verificar que o arquivo ficou correto**

```bash
head -16 docs/superpowers/plans/2026-04-14-ai-fundamentals.md
```

Expected: frontmatter YAML com os 11 campos seguido do título e conteúdo do plan.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-04-14-ai-fundamentals.md
git commit -m "docs(plans): add status frontmatter to ai-fundamentals plan, mark as completed"
```

---

## Task 4: Criar ROADMAP.md

**Files:**
- Create: `docs/superpowers/plans/ROADMAP.md`

- [ ] **Step 1: Criar o arquivo ROADMAP.md**

Criar `docs/superpowers/plans/ROADMAP.md` com o conteúdo abaixo:

```markdown
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
```

- [ ] **Step 2: Verificar que o arquivo foi criado**

```bash
head -20 docs/superpowers/plans/ROADMAP.md
```

Expected: frontmatter YAML seguido do título `# 🗺️ Roadmap — Vault Inc Library`.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/ROADMAP.md
git commit -m "docs(plans): create ROADMAP.md — central roadmap index for all implementation plans"
```

---

## Self-Review

**Cobertura do objetivo:**
- ✅ Visibilidade do que está sendo feito: tabela de status com progresso percentual
- ✅ Visibilidade da direção: seção "Direção Estratégica" com ondas
- ✅ Não polui os vaults de conhecimento: ROADMAP.md vive em `docs/superpowers/plans/`, nenhum link criado em tech-vault ou finance-vault
- ✅ Frontmatter padronizado nos plans: permite filtragem/busca futura via Dataview se desejado

**Placeholders:** Nenhum. Todo conteúdo é concreto e baseado no estado real dos planos.

**Consistência:** Os 3 planos existentes têm seus status avaliados com base no que foi realmente implementado na sessão.

**Escopo:** Focado — 4 tasks simples, sem over-engineering. O ROADMAP é um arquivo markdown estático que qualquer pessoa (ou agente) consegue manter atualizando manualmente.
