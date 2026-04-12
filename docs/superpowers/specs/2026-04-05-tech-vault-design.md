# Tech Knowledge Vault — Design Spec

## Resumo

Repositório de conhecimento técnico estruturado para Obsidian, integrado ao vault existente `Vault-Inc-Library`. Funciona como segundo cérebro para desenvolvimento full-stack, DevOps, IA/ML, data engineering e arquitetura de sistemas. Conteúdo de nível avançado, otimizado para o ecossistema completo de plugins Obsidian (Dataview, Templater, Canvas, Excalidraw, Tasks).

## Decisões de Design

| Decisão | Escolha | Razão |
|---|---|---|
| Localização | Subdiretório `tech-vault/` dentro de `Vault-Inc-Library` | Integração com vault existente, wikilinks compartilhados |
| Nível de conteúdo | Avançado | Usuário full-stack com alto grau de conhecimento |
| Idioma | Misto pragmático | Overview/Gotchas em PT-BR, Snippets/Core Concepts em EN quando fizer sentido |
| Filenames | kebab-case, sem emojis | Emojis causam problemas em git/scripts; emojis ficam dentro do conteúdo |
| Numeração de pastas | Prefixos `00-` a `09-` | Ordenação explícita no file explorer do Obsidian |
| CSS snippet | `.obsidian/snippets/vault-styles.css` no root | Vault compartilha `.obsidian/` — CSS fica no nível correto |
| Plugins alvo | Dataview, Templater, Canvas, Excalidraw, Tasks | Power user de Obsidian |

## Estrutura de Diretórios

```
tech-vault/
├── 00-moc/
│   ├── home.md
│   ├── engineering-moc.md
│   ├── devops-moc.md
│   ├── ai-ml-moc.md
│   ├── architecture-moc.md
│   ├── data-engineering-moc.md
│   └── infrastructure-moc.md
├── 01-skills/
│   ├── languages/
│   │   ├── python.md
│   │   ├── typescript.md
│   │   └── rust.md
│   ├── frameworks/
│   │   ├── fastapi.md
│   │   ├── nextjs.md
│   │   ├── langchain.md
│   │   ├── react.md
│   │   ├── svelte.md
│   │   ├── astro.md
│   │   ├── htmx.md
│   │   └── django.md
│   ├── databases/
│   │   ├── postgresql.md
│   │   ├── redis.md
│   │   ├── vector-dbs.md
│   │   ├── supabase.md
│   │   ├── mongodb.md
│   │   ├── planetscale.md
│   │   └── database-optimization.md
│   └── tools/
│       ├── git-advanced.md
│       ├── docker.md
│       └── claude-code.md
├── 02-devops/
│   ├── ci-cd/
│   │   ├── github-actions.md
│   │   ├── deployment-strategies.md
│   │   ├── gitlab-ci.md
│   │   ├── argocd.md
│   │   └── feature-flags.md
│   ├── containers/
│   │   ├── docker-compose-patterns.md
│   │   └── kubernetes-basics.md
│   ├── monitoring/
│   │   └── observability.md
│   ├── iac/
│   │   ├── terraform.md
│   │   └── pulumi.md
│   ├── networking/
│   │   ├── vpn-setup.md
│   │   ├── reverse-proxy.md
│   │   └── dns-and-cdn.md
│   └── security/
│       └── secrets-management.md
├── 03-ai-ml/
│   ├── llm-patterns/
│   │   ├── prompt-engineering.md
│   │   ├── multi-agent-systems.md
│   │   └── rag-architecture.md
│   ├── ai-frameworks/
│   │   ├── claude-code-superpowers.md
│   │   ├── openai-agents-sdk.md
│   │   ├── crewai.md
│   │   ├── autogen.md
│   │   └── vercel-ai-sdk.md
│   ├── mcp/
│   │   └── mcp-servers-guide.md
│   └── tools/
│       └── claude-api.md
├── 04-architecture/
│   ├── patterns/
│   │   ├── microservices.md
│   │   ├── event-driven.md
│   │   └── clean-architecture.md
│   ├── decisions/
│   │   └── adr-template.md
│   ├── cloud-services/
│   │   ├── cloudinary.md
│   │   ├── s3-storage-patterns.md
│   │   └── media-pipeline.md
│   └── messaging/
│       ├── rabbitmq.md
│       ├── sqs-sns.md
│       ├── nats.md
│       └── messaging-patterns.md
├── 05-data-engineering/
│   ├── pipelines/
│   │   ├── apache-airflow.md
│   │   ├── dagster.md
│   │   └── prefect.md
│   ├── streaming/
│   │   ├── kafka.md
│   │   └── flink.md
│   ├── storage/
│   │   ├── data-lake-patterns.md
│   │   ├── delta-lake.md
│   │   └── duckdb.md
│   └── transformation/
│       ├── dbt.md
│       └── spark.md
├── 06-snippets/
│   ├── python-snippets.md
│   ├── bash-snippets.md
│   ├── docker-snippets.md
│   └── sql-snippets.md
├── 07-references/
│   ├── git-cheatsheet.md
│   ├── regex-cheatsheet.md
│   └── big-o-notation.md
├── 08-templates/
│   ├── skill-template.md
│   ├── project-template.md
│   ├── adr-template.md
│   └── weekly-review.md
└── 09-canvas/
    ├── tech-stack-overview.canvas
    ├── learning-paths.canvas
    └── data-pipeline-map.canvas
```

**Total: ~81 arquivos markdown + 3 canvas + 1 CSS snippet = ~85 arquivos**

## Padrão de Conteúdo

### Frontmatter YAML

Todos os arquivos de conteúdo (skills, docs, references, snippets) usam:

```yaml
---
tags: [skill, {categoria}, {tecnologia}]
status: draft | active | deprecated
level: beginner | intermediate | advanced
updated: 2026-04-05
aliases: [{nome alternativo}]
created: 2026-04-05
---
```

- `created` + `updated` — suportam queries Dataview temporais
- `aliases` — permitem referência por nome alternativo no Obsidian
- `tags` — hierarquia: tipo + categoria + tecnologia

### Seções por Tipo de Arquivo

**Skills e Docs (`01-skills/`, `02-devops/`, `03-ai-ml/`, `04-architecture/`, `05-data-engineering/`):**

```markdown
## Overview       — O que é, quando usar, quando NÃO usar (2-3 parágrafos)
## Core Concepts  — Conceitos fundamentais com code blocks reais
## Patterns       — Padrões recorrentes de produção com exemplos
## Gotchas        — Armadilhas comuns com callouts [!warning]
## Snippets       — Blocos de código prontos para copiar
## References     — Links para docs oficiais
## Related        — Mínimo 5 wikilinks [[skill]] para outros arquivos
```

**MOCs (`00-moc/`):**

```markdown
## Dashboard      — Visão geral + Dataview queries dinâmicas
## Skills Map     — Lista categorizada com status emoji (✅ active, 🚧 draft, ⚠️ deprecated)
## Quick Access   — Top links mais usados da categoria
```

**Snippets (`06-snippets/`):**

```markdown
## {Categoria}    — Blocos de código agrupados por uso
                    Cada snippet com comentário de contexto
                    Code blocks com linguagem especificada
```

**References (`07-references/`):**

```markdown
## Cheatsheet     — Tabelas e exemplos compactos
## Examples       — Uso real com contexto
## Related        — Wikilinks para skills relacionadas
```

**Templates (`08-templates/`):**

```markdown
Sintaxe Templater nativa (<% %>) com:
- Prompts interativos (<% tp.system.prompt() %>)
- Datas dinâmicas (<% tp.date.now("YYYY-MM-DD") %>)
- Frontmatter gerado automaticamente
```

### Callouts Obsidian

```markdown
> [!tip] Performance / Dica prática
> [!warning] Armadilha / Gotcha
> [!example] Exemplo prático
> [!info] Conceito explicativo
> [!danger] Anti-pattern
```

Callouts customizados (estilizados via CSS):

```markdown
> [!skill] Skill highlight
> [!devops] DevOps context
> [!ai] AI/ML context
> [!data] Data engineering context
> [!infra] Infrastructure context
```

### Wikilinks — Regra de Densidade

- Mínimo 5 wikilinks por arquivo para garantir graph view denso
- Wikilinks inline no texto (não apenas na seção Related)
- Formato: `[[nome-do-arquivo]]` ou `[[nome-do-arquivo|texto display]]`

### Idioma

- **Português:** Overview, Gotchas, explicações contextuais
- **Inglês:** Core Concepts, Snippets, code blocks, termos técnicos, nomes de seções
- **Pragmático:** Onde inglês é mais natural (ex: documentação de API), usa inglês integralmente

## Home.md — Dashboard

O arquivo `00-moc/home.md` serve como entry point do vault:

1. **Header** — Título com visão geral do vault (emoji no H1: `# 🗺️ Tech Knowledge Vault`)
2. **MOC Links** — Cards para os 7 MOCs:
   - Engineering, DevOps, AI/ML, Architecture, Data Engineering, Infrastructure
3. **Dataview: Recently Updated** — Skills atualizadas nos últimos 30 dias:
   ```dataview
   TABLE status, level, updated
   FROM "tech-vault"
   WHERE updated >= date(today) - dur(30 days)
   SORT updated DESC
   LIMIT 15
   ```
4. **Quick Access** — 10 comandos/snippets/referências mais usados
5. **Dataview: Stats** — Contagem de skills por status:
   ```dataview
   TABLE length(rows) AS "Count"
   FROM "tech-vault"
   GROUP BY status
   ```
6. **Dataview: By Level** — Skills agrupadas por nível

## CSS Snippet

Localização: `.obsidian/snippets/vault-styles.css`

### Callouts customizados por categoria

```css
.callout[data-callout="skill"]  → background verde (#2ecc71 / 10% opacity)
.callout[data-callout="devops"] → background azul (#3498db / 10% opacity)
.callout[data-callout="ai"]     → background roxo (#9b59b6 / 10% opacity)
.callout[data-callout="data"]   → background laranja (#e67e22 / 10% opacity)
.callout[data-callout="infra"]  → background cyan (#00bcd4 / 10% opacity)
```

### Badges de status

```css
Tags de status (active/draft/deprecated) renderizadas como badges coloridos:
- active     → verde
- draft      → amarelo
- deprecated → vermelho
```

### Code blocks

```css
- Borda esquerda colorida (4px) para destaque visual
- Background levemente diferenciado
- Font-size otimizado para legibilidade técnica
```

### Typography

```css
- Hierarquia clara de headers (H1 > H2 > H3)
- Line-height otimizado para leitura técnica
- Espaçamento consistente entre seções
```

## Canvas Files

### `tech-stack-overview.canvas`
Mapa visual das tecnologias organizadas por camada:
```
Frontend (React, Next.js, Svelte, Astro, HTMX)
    ↓
Backend (FastAPI, Django, Node.js)
    ↓
Database (PostgreSQL, Redis, Supabase, MongoDB, Vector DBs)
    ↓
Infrastructure (Docker, K8s, Terraform, VPN)
    ↓
Monitoring (Observability stack)
```
Cada node é um group com links para os `.md` correspondentes.

### `learning-paths.canvas`
Trilhas de aprendizado:
- Full-Stack Path
- DevOps Path
- AI/ML Path
- Data Engineering Path

Nodes conectados por edges com labels de progressão.

### `data-pipeline-map.canvas`
Fluxo de pipeline de dados:
```
Sources → Ingestion (Kafka, Airflow) → Processing (Spark, Flink) → Storage (Delta Lake, S3) → Serving (dbt, DuckDB)
```
Cada node linka para o arquivo correspondente.

## Qualidade e Requisitos

- Cada arquivo `.md` deve ter conteúdo real e substancial (mínimo 80 linhas)
- Prioridade: profundidade > quantidade
- Conteúdo de nível avançado — sem explicações básicas desnecessárias
- Todos os code blocks com linguagem especificada
- Graph view deve mostrar rede densa de conhecimento interligado
- Compatível com Dataview, Templater, Canvas, Excalidraw, Tasks plugin
