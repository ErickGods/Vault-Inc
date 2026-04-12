---
tags: [moc, engineering]
status: active
level: advanced
updated: 2026-04-05
aliases: [Engineering MOC]
created: 2026-04-05
---

# 🛠️ Engineering MOC

## Visão Geral

Este MOC cobre o domínio de engenharia de software: linguagens de programação, frameworks web, bancos de dados e ferramentas de desenvolvimento. É a seção mais abrangente do vault, refletindo a amplitude das tecnologias utilizadas em projetos modernos de software.

O foco está em profundidade técnica — não apenas "como usar", mas "por que usar", trade-offs, padrões de produção e integração entre tecnologias. Cada arquivo tem exemplos reais, não apenas documentação de referência.

> [!info] Cobertura
> Esta seção (`01-skills/`) contém 20+ arquivos cobrindo o stack completo de engenharia moderna, desde linguagens de sistema até frameworks full-stack e infraestrutura de dados.

---

## 📊 Dashboard

```dataview
TABLE status, level, updated
FROM "tech-vault/01-skills"
SORT updated DESC
```

---

## 🗺️ Skills Map

### Languages

| Arquivo | Tecnologia | Status |
|---------|-----------|--------|
| [[python]] | Python 3.12+ | ✅ active |
| [[typescript]] | TypeScript 5.x | ✅ active |
| [[rust]] | Rust — sistemas e WASM | ✅ active |

### Web Frameworks

| Arquivo | Tecnologia | Status |
|---------|-----------|--------|
| [[fastapi]] | FastAPI — APIs Python async | ✅ active |
| [[django]] | Django — web full-stack Python | ✅ active |
| [[nextjs]] | Next.js — React SSR/SSG | ✅ active |
| [[react]] | React 19 — UI library | ✅ active |
| [[svelte]] | Svelte/SvelteKit | ✅ active |
| [[astro]] | Astro — static-first | 🚧 draft |
| [[htmx]] | HTMX — hypermedia | 🚧 draft |

### AI & LLM Frameworks

| Arquivo | Tecnologia | Status |
|---------|-----------|--------|
| [[langchain]] | LangChain — LLM orchestration | ✅ active |
| [[claude-code]] | Claude Code CLI | ✅ active |

### Databases

| Arquivo | Tecnologia | Status |
|---------|-----------|--------|
| [[postgresql]] | PostgreSQL — relacional | ✅ active |
| [[redis]] | Redis — cache e filas | ✅ active |
| [[mongodb]] | MongoDB — document store | ✅ active |
| [[supabase]] | Supabase — BaaS | ✅ active |
| [[planetscale]] | PlanetScale — MySQL serverless | 🚧 draft |
| [[vector-dbs]] | Bancos vetoriais (Pinecone, Weaviate, Chroma) | ✅ active |
| [[database-optimization]] | Otimização de queries e índices | ✅ active |

### DevTools

| Arquivo | Tecnologia | Status |
|---------|-----------|--------|
| [[git-advanced]] | Git avançado — rebase, bisect, hooks | ✅ active |
| [[docker]] | Docker — containerização | ✅ active |

---

## ⚡ Quick Access

Referências mais utilizadas nesta categoria:

- [[python]] — Linguagem principal para backend e scripts
- [[typescript]] — Tipagem estática para projetos Node/frontend
- [[fastapi]] — Framework preferido para APIs Python
- [[postgresql]] — Banco relacional de produção
- [[docker]] — Containerização e ambientes isolados
- [[redis]] — Cache, pub/sub e filas leves
- [[git-advanced]] — Workflows avançados de versionamento

---

## 🧠 Conceitos Transversais

> [!tip] Python + FastAPI + PostgreSQL
> O stack mais comum para APIs de produção. Combina tipagem com Pydantic, validação automática, async nativo e um banco relacional robusto. Veja [[fastapi]] para padrões de projeto e [[database-optimization]] para queries eficientes.

> [!tip] TypeScript Full-Stack
> Para projetos full-stack, [[nextjs]] + [[typescript]] + [[postgresql]] (via [[supabase]]) oferece tipagem end-to-end com excelente DX. Considere [[svelte]] para projetos menores onde a reatividade do React é overkill.

> [!info] Rust para Performance
> [[rust]] é indicado para componentes que exigem performance extrema, segurança de memória ou integração via WASM com o frontend. Não é a primeira escolha para CRUD, mas é excelente para processamento de dados e CLIs.

---

## 📐 Padrões de Projeto

### API Design Patterns

```python
# FastAPI — estrutura recomendada para projetos médios/grandes
# Ver [[fastapi]] para detalhes completos
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   └── router.py
├── core/
│   ├── config.py
│   └── security.py
├── models/
├── schemas/
└── services/
```

### Database Patterns
- **Repository Pattern** — abstração da camada de dados (ver [[database-optimization]])
- **CQRS** — separação de leituras e escritas para alta escala
- **Event Sourcing** — auditoria e replay de estado (integra com [[data-engineering-moc]])

---

## 🔗 Integrações com Outros Domínios

- **DevOps** → [[devops-moc]] — como deployar e monitorar as aplicações
- **AI/ML** → [[ai-ml-moc]] — integrar LLMs nos backends com [[langchain]]
- **Architecture** → [[architecture-moc]] — padrões como [[microservices]] e [[clean-architecture]]
- **Data** → [[data-engineering-moc]] — pipelines que consomem dados das aplicações

---

## 📅 Roadmap de Aprendizado

| Prioridade | Tecnologia | Arquivo | Motivo |
|-----------|-----------|---------|--------|
| Alta | Rust | [[rust]] | Performance e WASM |
| Alta | Astro | [[astro]] | Sites estáticos modernos |
| Média | HTMX | [[htmx]] | Reduzir JS no frontend |
| Média | PlanetScale | [[planetscale]] | MySQL serverless escalonável |

> [!warning] Deprecações Previstas
> Monitorar a evolução do ecossistema JavaScript — frameworks como [[react]] estão em transição com React 19 e Server Components. Manter [[nextjs]] atualizado para aproveitar as melhorias de performance.
