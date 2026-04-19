---
tags: [plan, completed, tech-vault]
status: completed
progress: 100
goal: Setup inicial da estrutura do tech-vault com MOCs, pastas e arquivos base
layer: tech-vault
created: 2026-04-05
updated: 2026-04-05
---

# Tech Knowledge Vault — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a comprehensive Obsidian knowledge vault (`tech-vault/`) with ~85 content files covering full-stack development, DevOps, AI/ML, data engineering, and system architecture.

**Architecture:** Content-only project — all output is Markdown files with YAML frontmatter, Obsidian wikilinks, Dataview queries, and Templater syntax. One CSS snippet for custom styling. Three Canvas files for visual navigation. All files live under `tech-vault/` inside the existing `Vault-Inc-Library` Obsidian vault.

**Tech Stack:** Obsidian Markdown, YAML frontmatter, Dataview queries, Templater syntax, Obsidian Canvas JSON, CSS3.

**Spec:** `docs/superpowers/specs/2026-04-05-tech-vault-design.md`

---

## Quality Rules (apply to ALL tasks)

Every `.md` content file MUST:
1. Have valid YAML frontmatter with: `tags`, `status`, `level`, `updated`, `aliases`, `created`
2. Have minimum 80 lines of real, substantive content
3. Include minimum 5 `[[wikilinks]]` to other vault files (inline + Related section)
4. Use Obsidian callouts (`> [!tip]`, `> [!warning]`, `> [!example]`, etc.)
5. Specify language on all code blocks (` ```python `, ` ```bash `, ` ```yaml `, etc.)
6. Follow idioma rules: PT-BR for Overview/Gotchas, EN for Core Concepts/Snippets/code, pragmatic mix elsewhere

**Frontmatter template for skills/docs:**
```yaml
---
tags: [skill, {categoria}, {tecnologia}]
status: active
level: advanced
updated: 2026-04-05
aliases: [{nome alternativo}]
created: 2026-04-05
---
```

**Section template for skills/docs:**
```markdown
## Overview
## Core Concepts
## Patterns
## Gotchas
## Snippets
## References
## Related
```

---

### Task 1: Directory Structure + CSS Snippet

**Files:**
- Create: all directories under `tech-vault/`
- Create: `.obsidian/snippets/vault-styles.css`

- [ ] **Step 1: Create full directory tree**

```bash
mkdir -p tech-vault/00-moc
mkdir -p tech-vault/01-skills/languages
mkdir -p tech-vault/01-skills/frameworks
mkdir -p tech-vault/01-skills/databases
mkdir -p tech-vault/01-skills/tools
mkdir -p tech-vault/02-devops/ci-cd
mkdir -p tech-vault/02-devops/containers
mkdir -p tech-vault/02-devops/monitoring
mkdir -p tech-vault/02-devops/iac
mkdir -p tech-vault/02-devops/networking
mkdir -p tech-vault/02-devops/security
mkdir -p tech-vault/03-ai-ml/llm-patterns
mkdir -p tech-vault/03-ai-ml/ai-frameworks
mkdir -p tech-vault/03-ai-ml/mcp
mkdir -p tech-vault/03-ai-ml/tools
mkdir -p tech-vault/04-architecture/patterns
mkdir -p tech-vault/04-architecture/decisions
mkdir -p tech-vault/04-architecture/cloud-services
mkdir -p tech-vault/04-architecture/messaging
mkdir -p tech-vault/05-data-engineering/pipelines
mkdir -p tech-vault/05-data-engineering/streaming
mkdir -p tech-vault/05-data-engineering/storage
mkdir -p tech-vault/05-data-engineering/transformation
mkdir -p tech-vault/06-snippets
mkdir -p tech-vault/07-references
mkdir -p tech-vault/08-templates
mkdir -p tech-vault/09-canvas
```

- [ ] **Step 2: Create CSS snippet**

Create `.obsidian/snippets/vault-styles.css` with these styles:

```css
/* ============================================
   TECH VAULT — Custom Obsidian Styles
   ============================================ */

/* --- Custom Callouts by Category --- */

.callout[data-callout="skill"] {
  --callout-color: 46, 204, 113;
  --callout-icon: lucide-code-2;
}

.callout[data-callout="devops"] {
  --callout-color: 52, 152, 219;
  --callout-icon: lucide-server;
}

.callout[data-callout="ai"] {
  --callout-color: 155, 89, 182;
  --callout-icon: lucide-brain;
}

.callout[data-callout="data"] {
  --callout-color: 230, 126, 34;
  --callout-icon: lucide-database;
}

.callout[data-callout="infra"] {
  --callout-color: 0, 188, 212;
  --callout-icon: lucide-network;
}

/* --- Status Badges via Tags --- */

.tag[href*="active"] {
  background-color: rgba(46, 204, 113, 0.2);
  color: #27ae60;
  border: 1px solid rgba(46, 204, 113, 0.4);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.85em;
}

.tag[href*="draft"] {
  background-color: rgba(241, 196, 15, 0.2);
  color: #f39c12;
  border: 1px solid rgba(241, 196, 15, 0.4);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.85em;
}

.tag[href*="deprecated"] {
  background-color: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.4);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.85em;
}

/* --- Code Blocks Enhancement --- */

.markdown-preview-view pre {
  border-left: 4px solid rgba(139, 92, 246, 0.5);
  border-radius: 6px;
}

.markdown-preview-view pre code {
  font-size: 0.9em;
  line-height: 1.6;
}

/* --- Typography --- */

.markdown-preview-view h1 {
  font-weight: 700;
  margin-top: 2em;
  margin-bottom: 0.8em;
  border-bottom: 2px solid var(--background-modifier-border);
  padding-bottom: 0.3em;
}

.markdown-preview-view h2 {
  font-weight: 600;
  margin-top: 1.6em;
  margin-bottom: 0.6em;
  color: var(--text-accent);
}

.markdown-preview-view h3 {
  font-weight: 600;
  margin-top: 1.2em;
  margin-bottom: 0.4em;
}

/* --- Frontmatter styling --- */

.frontmatter-container {
  border-radius: 8px;
  border: 1px solid var(--background-modifier-border);
  padding: 8px 12px;
  margin-bottom: 1.5em;
}

/* --- Wikilinks --- */

.internal-link {
  text-decoration-style: dotted;
  text-underline-offset: 3px;
}

.internal-link:hover {
  text-decoration-style: solid;
}
```

- [ ] **Step 3: Verify structure**

Run: `find tech-vault -type d | sort`
Expected: 27 directories listed.

Run: `ls .obsidian/snippets/vault-styles.css`
Expected: file exists.

- [ ] **Step 4: Commit**

```bash
git add tech-vault/ .obsidian/snippets/vault-styles.css
git commit -m "feat(tech-vault): scaffold directory structure and CSS snippet"
```

---

### Task 2: Home + MOCs (7 files)

**Files:**
- Create: `tech-vault/00-moc/home.md`
- Create: `tech-vault/00-moc/engineering-moc.md`
- Create: `tech-vault/00-moc/devops-moc.md`
- Create: `tech-vault/00-moc/ai-ml-moc.md`
- Create: `tech-vault/00-moc/architecture-moc.md`
- Create: `tech-vault/00-moc/data-engineering-moc.md`
- Create: `tech-vault/00-moc/infrastructure-moc.md`

**Context:** MOCs are the navigation layer. `home.md` is the vault entry point with Dataview dashboard. Each MOC lists all skills in its category with status emojis and Dataview queries. These files must link to ALL files in their category — build them referencing the full file list from the spec.

**home.md must contain:**
1. H1 with emoji: `# 🗺️ Tech Knowledge Vault`
2. Overview paragraph about the vault
3. Links to all 6 MOCs (Engineering, DevOps, AI/ML, Architecture, Data Engineering, Infrastructure)
4. Dataview query: recently updated skills (last 30 days)
5. Quick Access section: 10 most-used snippets/references
6. Dataview query: skill count by status
7. Dataview query: skills grouped by level

**Each category MOC must contain:**
1. Frontmatter with `tags: [moc, {categoria}]`, `status: active`
2. Dashboard section with Dataview query filtering `FROM "tech-vault/{section}"`
3. Skills Map section listing ALL files in that category with status emojis (✅ active, 🚧 draft, ⚠️ deprecated)
4. Quick Access section with top links
5. Minimum 5 wikilinks to skills in that category

- [ ] **Step 1: Create home.md**

Write `tech-vault/00-moc/home.md` with full dashboard content as specified above. Must include all 3 Dataview queries and links to every MOC.

- [ ] **Step 2: Create engineering-moc.md**

Write `tech-vault/00-moc/engineering-moc.md` covering: `01-skills/` (languages, frameworks, databases, tools). List all 20 files in that section.

- [ ] **Step 3: Create devops-moc.md**

Write `tech-vault/00-moc/devops-moc.md` covering: `02-devops/` (ci-cd, containers, monitoring, iac). List all 13 files.

- [ ] **Step 4: Create ai-ml-moc.md**

Write `tech-vault/00-moc/ai-ml-moc.md` covering: `03-ai-ml/` (llm-patterns, ai-frameworks, mcp, tools). List all 11 files.

- [ ] **Step 5: Create architecture-moc.md**

Write `tech-vault/00-moc/architecture-moc.md` covering: `04-architecture/` (patterns, decisions, cloud-services, messaging). List all 11 files.

- [ ] **Step 6: Create data-engineering-moc.md**

Write `tech-vault/00-moc/data-engineering-moc.md` covering: `05-data-engineering/` (pipelines, streaming, storage, transformation). List all 10 files.

- [ ] **Step 7: Create infrastructure-moc.md**

Write `tech-vault/00-moc/infrastructure-moc.md` covering: networking, security, cloud-services, and cross-cutting infra topics. Links to files across `02-devops/networking/`, `02-devops/security/`, `04-architecture/cloud-services/`.

- [ ] **Step 8: Verify**

Run: `find tech-vault/00-moc -name "*.md" | wc -l`
Expected: 7

Run: `grep -c "\[\[" tech-vault/00-moc/home.md`
Expected: >= 10 wikilinks

- [ ] **Step 9: Commit**

```bash
git add tech-vault/00-moc/
git commit -m "feat(tech-vault): add home dashboard and all MOCs"
```

---

### Task 3: Languages (3 files)

**Files:**
- Create: `tech-vault/01-skills/languages/python.md`
- Create: `tech-vault/01-skills/languages/typescript.md`
- Create: `tech-vault/01-skills/languages/rust.md`

**Context:** Advanced-level language skills. Focus on production patterns, performance gotchas, and advanced features — not introductory tutorials. Each file follows the standard skill template (Overview → Core Concepts → Patterns → Gotchas → Snippets → References → Related).

**python.md wikilinks to:** `[[fastapi]]`, `[[django]]`, `[[langchain]]`, `[[postgresql]]`, `[[docker]]`, `[[python-snippets]]`
**typescript.md wikilinks to:** `[[nextjs]]`, `[[react]]`, `[[svelte]]`, `[[astro]]`, `[[vercel-ai-sdk]]`, `[[node]]`
**rust.md wikilinks to:** `[[docker]]`, `[[python]]`, `[[typescript]]`, `[[database-optimization]]`, `[[big-o-notation]]`

- [ ] **Step 1: Create python.md**

Write `tech-vault/01-skills/languages/python.md`. Advanced content: type hints, async/await patterns, dataclasses vs pydantic, GIL implications, memory profiling, packaging (uv/rye). Min 80 lines. Min 5 wikilinks.

- [ ] **Step 2: Create typescript.md**

Write `tech-vault/01-skills/languages/typescript.md`. Advanced content: generics, conditional types, template literal types, type narrowing, declaration merging, module augmentation, strict mode patterns. Min 80 lines. Min 5 wikilinks.

- [ ] **Step 3: Create rust.md**

Write `tech-vault/01-skills/languages/rust.md`. Advanced content: ownership/borrowing, lifetimes, trait objects vs generics, async runtime (tokio), error handling (thiserror/anyhow), FFI with Python/Node. Min 80 lines. Min 5 wikilinks.

- [ ] **Step 4: Verify**

Run: `find tech-vault/01-skills/languages -name "*.md" | wc -l`
Expected: 3

Run: `wc -l tech-vault/01-skills/languages/*.md`
Expected: each file >= 80 lines

- [ ] **Step 5: Commit**

```bash
git add tech-vault/01-skills/languages/
git commit -m "feat(tech-vault): add language skills — python, typescript, rust"
```

---

### Task 4: Frameworks (8 files)

**Files:**
- Create: `tech-vault/01-skills/frameworks/fastapi.md`
- Create: `tech-vault/01-skills/frameworks/nextjs.md`
- Create: `tech-vault/01-skills/frameworks/langchain.md`
- Create: `tech-vault/01-skills/frameworks/react.md`
- Create: `tech-vault/01-skills/frameworks/svelte.md`
- Create: `tech-vault/01-skills/frameworks/astro.md`
- Create: `tech-vault/01-skills/frameworks/htmx.md`
- Create: `tech-vault/01-skills/frameworks/django.md`

**Context:** Production-grade framework knowledge. Each follows standard skill template. Focus on architecture decisions, performance optimization, common pitfalls in production.

**Wikilink map:**
- fastapi.md → `[[python]]`, `[[postgresql]]`, `[[docker]]`, `[[supabase]]`, `[[deployment-strategies]]`, `[[clean-architecture]]`
- nextjs.md → `[[react]]`, `[[typescript]]`, `[[vercel-ai-sdk]]`, `[[docker]]`, `[[deployment-strategies]]`
- langchain.md → `[[python]]`, `[[rag-architecture]]`, `[[vector-dbs]]`, `[[claude-api]]`, `[[prompt-engineering]]`
- react.md → `[[typescript]]`, `[[nextjs]]`, `[[svelte]]`, `[[htmx]]`, `[[astro]]`
- svelte.md → `[[typescript]]`, `[[react]]`, `[[astro]]`, `[[nextjs]]`, `[[htmx]]`
- astro.md → `[[react]]`, `[[svelte]]`, `[[typescript]]`, `[[nextjs]]`, `[[deployment-strategies]]`
- htmx.md → `[[django]]`, `[[fastapi]]`, `[[react]]`, `[[astro]]`, `[[deployment-strategies]]`
- django.md → `[[python]]`, `[[postgresql]]`, `[[docker]]`, `[[htmx]]`, `[[fastapi]]`, `[[clean-architecture]]`

- [ ] **Step 1: Create fastapi.md** — Dependency injection, async handlers, Pydantic v2, middleware, background tasks, WebSocket. Min 80 lines.

- [ ] **Step 2: Create nextjs.md** — App Router, Server Components, Server Actions, ISR/SSG/SSR, middleware, image optimization. Min 80 lines.

- [ ] **Step 3: Create langchain.md** — Chains, agents, retrieval, output parsers, callbacks, LangSmith, LCEL. Min 80 lines.

- [ ] **Step 4: Create react.md** — Server Components, Suspense, use() hook, React Compiler, concurrent features, state management patterns. Min 80 lines.

- [ ] **Step 5: Create svelte.md** — Runes, SvelteKit, server-side rendering, form actions, load functions. Min 80 lines.

- [ ] **Step 6: Create astro.md** — Island architecture, content collections, View Transitions, SSR adapters, integration ecosystem. Min 80 lines.

- [ ] **Step 7: Create htmx.md** — hx-attributes, boosting, WebSocket/SSE, response headers, Django/FastAPI integration. Min 80 lines.

- [ ] **Step 8: Create django.md** — ORM advanced (Q objects, prefetch), DRF, signals, middleware, async views, Django Ninja. Min 80 lines.

- [ ] **Step 9: Verify**

Run: `find tech-vault/01-skills/frameworks -name "*.md" | wc -l`
Expected: 8

Run: `wc -l tech-vault/01-skills/frameworks/*.md`
Expected: each >= 80 lines

- [ ] **Step 10: Commit**

```bash
git add tech-vault/01-skills/frameworks/
git commit -m "feat(tech-vault): add framework skills — fastapi, nextjs, langchain, react, svelte, astro, htmx, django"
```

---

### Task 5: Databases (7 files)

**Files:**
- Create: `tech-vault/01-skills/databases/postgresql.md`
- Create: `tech-vault/01-skills/databases/redis.md`
- Create: `tech-vault/01-skills/databases/vector-dbs.md`
- Create: `tech-vault/01-skills/databases/supabase.md`
- Create: `tech-vault/01-skills/databases/mongodb.md`
- Create: `tech-vault/01-skills/databases/planetscale.md`
- Create: `tech-vault/01-skills/databases/database-optimization.md`

**Context:** Advanced database knowledge. Focus on production operation, optimization, scaling patterns.

**Wikilink map:**
- postgresql.md → `[[database-optimization]]`, `[[supabase]]`, `[[django]]`, `[[fastapi]]`, `[[redis]]`, `[[docker]]`
- redis.md → `[[postgresql]]`, `[[docker]]`, `[[messaging-patterns]]`, `[[rabbitmq]]`, `[[database-optimization]]`
- vector-dbs.md → `[[rag-architecture]]`, `[[langchain]]`, `[[postgresql]]`, `[[claude-api]]`, `[[prompt-engineering]]`
- supabase.md → `[[postgresql]]`, `[[nextjs]]`, `[[react]]`, `[[fastapi]]`, `[[secrets-management]]`
- mongodb.md → `[[postgresql]]`, `[[database-optimization]]`, `[[docker]]`, `[[fastapi]]`, `[[mongoose]]`
- planetscale.md → `[[database-optimization]]`, `[[postgresql]]`, `[[deployment-strategies]]`, `[[supabase]]`, `[[docker]]`
- database-optimization.md → `[[postgresql]]`, `[[redis]]`, `[[mongodb]]`, `[[supabase]]`, `[[big-o-notation]]`, `[[observability]]`

- [ ] **Step 1: Create postgresql.md** — Advanced indexing (GIN, GiST, BRIN), CTEs, window functions, partitioning, JSONB, pg_stat, extensions (pgvector, TimescaleDB). Min 80 lines.

- [ ] **Step 2: Create redis.md** — Data structures, pub/sub, Lua scripting, clustering, persistence (RDB/AOF), Streams, rate limiting patterns. Min 80 lines.

- [ ] **Step 3: Create vector-dbs.md** — Pinecone, Weaviate, Chroma, pgvector comparison. Embedding strategies, similarity metrics, indexing (HNSW, IVF). Min 80 lines.

- [ ] **Step 4: Create supabase.md** — Auth, Realtime, Edge Functions, Storage, Row Level Security, PostgREST, migrations, self-hosting. Min 80 lines.

- [ ] **Step 5: Create mongodb.md** — Aggregation pipeline, indexes (compound, text, geospatial), replica sets, sharding, transactions, Atlas. Min 80 lines.

- [ ] **Step 6: Create planetscale.md** — Vitess, schema branching, deploy requests, connection strings, serverless driver, schema design. Min 80 lines.

- [ ] **Step 7: Create database-optimization.md** — Query plans (EXPLAIN ANALYZE), index strategies, connection pooling (PgBouncer), partitioning, vacuuming, read replicas, caching layers. Min 80 lines.

- [ ] **Step 8: Verify**

Run: `find tech-vault/01-skills/databases -name "*.md" | wc -l`
Expected: 7

- [ ] **Step 9: Commit**

```bash
git add tech-vault/01-skills/databases/
git commit -m "feat(tech-vault): add database skills — postgresql, redis, vector-dbs, supabase, mongodb, planetscale, optimization"
```

---

### Task 6: Tools (3 files)

**Files:**
- Create: `tech-vault/01-skills/tools/git-advanced.md`
- Create: `tech-vault/01-skills/tools/docker.md`
- Create: `tech-vault/01-skills/tools/claude-code.md`

**Wikilink map:**
- git-advanced.md → `[[github-actions]]`, `[[gitlab-ci]]`, `[[deployment-strategies]]`, `[[git-cheatsheet]]`, `[[docker]]`
- docker.md → `[[docker-compose-patterns]]`, `[[kubernetes-basics]]`, `[[github-actions]]`, `[[deployment-strategies]]`, `[[docker-snippets]]`
- claude-code.md → `[[claude-api]]`, `[[claude-code-superpowers]]`, `[[mcp-servers-guide]]`, `[[prompt-engineering]]`, `[[multi-agent-systems]]`

- [ ] **Step 1: Create git-advanced.md** — Interactive rebase, worktrees, bisect, reflog, subtree/submodule, hooks, cherry-pick strategies, monorepo patterns. Min 80 lines.

- [ ] **Step 2: Create docker.md** — Multi-stage builds, layer caching, BuildKit, security scanning, rootless, distroless images, healthchecks, signals. Min 80 lines.

- [ ] **Step 3: Create claude-code.md** — CLI commands, slash commands, MCP integration, hooks, settings, agent mode, Superpowers plugin, worktrees, parallel agents. Min 80 lines.

- [ ] **Step 4: Verify and Commit**

```bash
find tech-vault/01-skills/tools -name "*.md" | wc -l  # Expected: 3
git add tech-vault/01-skills/tools/
git commit -m "feat(tech-vault): add tool skills — git-advanced, docker, claude-code"
```

---

### Task 7: DevOps — CI/CD (5 files)

**Files:**
- Create: `tech-vault/02-devops/ci-cd/github-actions.md`
- Create: `tech-vault/02-devops/ci-cd/deployment-strategies.md`
- Create: `tech-vault/02-devops/ci-cd/gitlab-ci.md`
- Create: `tech-vault/02-devops/ci-cd/argocd.md`
- Create: `tech-vault/02-devops/ci-cd/feature-flags.md`

**Wikilink map:**
- github-actions.md → `[[docker]]`, `[[deployment-strategies]]`, `[[git-advanced]]`, `[[argocd]]`, `[[secrets-management]]`
- deployment-strategies.md → `[[github-actions]]`, `[[gitlab-ci]]`, `[[argocd]]`, `[[kubernetes-basics]]`, `[[feature-flags]]`, `[[docker]]`
- gitlab-ci.md → `[[github-actions]]`, `[[docker]]`, `[[deployment-strategies]]`, `[[argocd]]`, `[[secrets-management]]`
- argocd.md → `[[kubernetes-basics]]`, `[[github-actions]]`, `[[gitlab-ci]]`, `[[deployment-strategies]]`, `[[terraform]]`
- feature-flags.md → `[[deployment-strategies]]`, `[[github-actions]]`, `[[observability]]`, `[[fastapi]]`, `[[nextjs]]`

- [ ] **Step 1: Create github-actions.md** — Workflow syntax, matrix builds, reusable workflows, composite actions, self-hosted runners, caching, secrets, OIDC. Min 80 lines.

- [ ] **Step 2: Create deployment-strategies.md** — Blue/green, canary, rolling, A/B testing, feature toggles, rollback strategies, zero-downtime. Min 80 lines.

- [ ] **Step 3: Create gitlab-ci.md** — Pipeline syntax, stages, DAG, includes, templates, Auto DevOps, container registry, environments. Min 80 lines.

- [ ] **Step 4: Create argocd.md** — GitOps principles, Application CRDs, sync policies, health checks, rollbacks, multi-cluster, Helm/Kustomize. Min 80 lines.

- [ ] **Step 5: Create feature-flags.md** — LaunchDarkly, Unleash, Flagsmith, trunk-based development, gradual rollouts, kill switches, experimentation. Min 80 lines.

- [ ] **Step 6: Verify and Commit**

```bash
find tech-vault/02-devops/ci-cd -name "*.md" | wc -l  # Expected: 5
git add tech-vault/02-devops/ci-cd/
git commit -m "feat(tech-vault): add CI/CD skills — github-actions, deployment-strategies, gitlab-ci, argocd, feature-flags"
```

---

### Task 8: DevOps — Containers + Monitoring + IaC (5 files)

**Files:**
- Create: `tech-vault/02-devops/containers/docker-compose-patterns.md`
- Create: `tech-vault/02-devops/containers/kubernetes-basics.md`
- Create: `tech-vault/02-devops/monitoring/observability.md`
- Create: `tech-vault/02-devops/iac/terraform.md`
- Create: `tech-vault/02-devops/iac/pulumi.md`

**Wikilink map:**
- docker-compose-patterns.md → `[[docker]]`, `[[kubernetes-basics]]`, `[[docker-snippets]]`, `[[postgresql]]`, `[[redis]]`
- kubernetes-basics.md → `[[docker]]`, `[[argocd]]`, `[[terraform]]`, `[[observability]]`, `[[deployment-strategies]]`
- observability.md → `[[kubernetes-basics]]`, `[[docker]]`, `[[github-actions]]`, `[[fastapi]]`, `[[deployment-strategies]]`
- terraform.md → `[[pulumi]]`, `[[kubernetes-basics]]`, `[[docker]]`, `[[github-actions]]`, `[[secrets-management]]`
- pulumi.md → `[[terraform]]`, `[[typescript]]`, `[[python]]`, `[[kubernetes-basics]]`, `[[github-actions]]`

- [ ] **Step 1: Create docker-compose-patterns.md** — Multi-service orchestration, profiles, health checks, volumes, networks, override files, production patterns. Min 80 lines.

- [ ] **Step 2: Create kubernetes-basics.md** — Pods, Services, Deployments, ConfigMaps, Secrets, Ingress, HPA, namespaces, RBAC, Helm charts. Min 80 lines.

- [ ] **Step 3: Create observability.md** — Three pillars (logs, metrics, traces), OpenTelemetry, Prometheus, Grafana, Loki, Jaeger, alerting strategies. Min 80 lines.

- [ ] **Step 4: Create terraform.md** — HCL syntax, state management, modules, workspaces, providers, import, drift detection, CI integration. Min 80 lines.

- [ ] **Step 5: Create pulumi.md** — TypeScript/Python SDKs, stack management, state backends, automation API, Crosswalk, policy-as-code. Min 80 lines.

- [ ] **Step 6: Verify and Commit**

```bash
find tech-vault/02-devops/containers tech-vault/02-devops/monitoring tech-vault/02-devops/iac -name "*.md" | wc -l  # Expected: 5
git add tech-vault/02-devops/containers/ tech-vault/02-devops/monitoring/ tech-vault/02-devops/iac/
git commit -m "feat(tech-vault): add devops skills — containers, monitoring, IaC"
```

---

### Task 9: DevOps — Networking + Security (4 files)

**Files:**
- Create: `tech-vault/02-devops/networking/vpn-setup.md`
- Create: `tech-vault/02-devops/networking/reverse-proxy.md`
- Create: `tech-vault/02-devops/networking/dns-and-cdn.md`
- Create: `tech-vault/02-devops/security/secrets-management.md`

**Wikilink map:**
- vpn-setup.md → `[[reverse-proxy]]`, `[[dns-and-cdn]]`, `[[kubernetes-basics]]`, `[[terraform]]`, `[[secrets-management]]`
- reverse-proxy.md → `[[docker]]`, `[[kubernetes-basics]]`, `[[dns-and-cdn]]`, `[[vpn-setup]]`, `[[deployment-strategies]]`
- dns-and-cdn.md → `[[reverse-proxy]]`, `[[cloudinary]]`, `[[s3-storage-patterns]]`, `[[deployment-strategies]]`, `[[vpn-setup]]`
- secrets-management.md → `[[github-actions]]`, `[[gitlab-ci]]`, `[[kubernetes-basics]]`, `[[terraform]]`, `[[docker]]`, `[[vpn-setup]]`

- [ ] **Step 1: Create vpn-setup.md** — WireGuard, Tailscale, OpenVPN comparison. Site-to-site, remote access, mesh networking, split tunneling, Docker integration. Min 80 lines.

- [ ] **Step 2: Create reverse-proxy.md** — Nginx, Traefik, Caddy comparison. SSL/TLS termination, load balancing, rate limiting, WebSocket proxying, Docker auto-discovery. Min 80 lines.

- [ ] **Step 3: Create dns-and-cdn.md** — Cloudflare, Route53, DNS records, CNAME flattening, CDN caching strategies, edge functions, DDoS protection. Min 80 lines.

- [ ] **Step 4: Create secrets-management.md** — HashiCorp Vault, SOPS, doppler, AWS Secrets Manager, env management strategies, rotation, audit. Min 80 lines.

- [ ] **Step 5: Verify and Commit**

```bash
find tech-vault/02-devops/networking tech-vault/02-devops/security -name "*.md" | wc -l  # Expected: 4
git add tech-vault/02-devops/networking/ tech-vault/02-devops/security/
git commit -m "feat(tech-vault): add networking and security skills — vpn, reverse-proxy, dns-cdn, secrets"
```

---

### Task 10: AI/ML — LLM Patterns (3 files)

**Files:**
- Create: `tech-vault/03-ai-ml/llm-patterns/prompt-engineering.md`
- Create: `tech-vault/03-ai-ml/llm-patterns/multi-agent-systems.md`
- Create: `tech-vault/03-ai-ml/llm-patterns/rag-architecture.md`

**Wikilink map:**
- prompt-engineering.md → `[[claude-api]]`, `[[langchain]]`, `[[multi-agent-systems]]`, `[[rag-architecture]]`, `[[claude-code]]`
- multi-agent-systems.md → `[[crewai]]`, `[[autogen]]`, `[[openai-agents-sdk]]`, `[[claude-code-superpowers]]`, `[[prompt-engineering]]`
- rag-architecture.md → `[[vector-dbs]]`, `[[langchain]]`, `[[postgresql]]`, `[[prompt-engineering]]`, `[[claude-api]]`

- [ ] **Step 1: Create prompt-engineering.md** — System prompts, few-shot, chain-of-thought, tool use, structured output, temperature/top-p, prompt injection defense, evaluation. Min 80 lines.

- [ ] **Step 2: Create multi-agent-systems.md** — Orchestrator patterns, message passing, tool delegation, supervisor/worker, swarm, consensus, state management. Min 80 lines.

- [ ] **Step 3: Create rag-architecture.md** — Chunking strategies, embedding models, hybrid search, re-ranking, contextual compression, evaluation (RAGAS), production patterns. Min 80 lines.

- [ ] **Step 4: Verify and Commit**

```bash
find tech-vault/03-ai-ml/llm-patterns -name "*.md" | wc -l  # Expected: 3
git add tech-vault/03-ai-ml/llm-patterns/
git commit -m "feat(tech-vault): add LLM pattern skills — prompt-engineering, multi-agent, RAG"
```

---

### Task 11: AI/ML — AI Frameworks + MCP + Tools (7 files)

**Files:**
- Create: `tech-vault/03-ai-ml/ai-frameworks/claude-code-superpowers.md`
- Create: `tech-vault/03-ai-ml/ai-frameworks/openai-agents-sdk.md`
- Create: `tech-vault/03-ai-ml/ai-frameworks/crewai.md`
- Create: `tech-vault/03-ai-ml/ai-frameworks/autogen.md`
- Create: `tech-vault/03-ai-ml/ai-frameworks/vercel-ai-sdk.md`
- Create: `tech-vault/03-ai-ml/mcp/mcp-servers-guide.md`
- Create: `tech-vault/03-ai-ml/tools/claude-api.md`

**Wikilink map:**
- claude-code-superpowers.md → `[[claude-code]]`, `[[multi-agent-systems]]`, `[[mcp-servers-guide]]`, `[[claude-api]]`, `[[prompt-engineering]]`
- openai-agents-sdk.md → `[[multi-agent-systems]]`, `[[prompt-engineering]]`, `[[crewai]]`, `[[autogen]]`, `[[claude-api]]`
- crewai.md → `[[python]]`, `[[multi-agent-systems]]`, `[[langchain]]`, `[[autogen]]`, `[[prompt-engineering]]`
- autogen.md → `[[python]]`, `[[multi-agent-systems]]`, `[[crewai]]`, `[[openai-agents-sdk]]`, `[[prompt-engineering]]`
- vercel-ai-sdk.md → `[[nextjs]]`, `[[react]]`, `[[typescript]]`, `[[claude-api]]`, `[[prompt-engineering]]`
- mcp-servers-guide.md → `[[claude-code]]`, `[[claude-code-superpowers]]`, `[[claude-api]]`, `[[typescript]]`, `[[python]]`
- claude-api.md → `[[python]]`, `[[typescript]]`, `[[prompt-engineering]]`, `[[langchain]]`, `[[mcp-servers-guide]]`

- [ ] **Step 1: Create claude-code-superpowers.md** — Skill system, brainstorming/planning/execution flow, TDD skill, subagent-driven development, worktrees, writing custom skills. Min 80 lines.

- [ ] **Step 2: Create openai-agents-sdk.md** — Agent class, Runner, handoffs, tools, guardrails, tracing, multi-agent orchestration. Min 80 lines.

- [ ] **Step 3: Create crewai.md** — Agents, Tasks, Crews, Process types, tools, memory, delegation, async execution. Min 80 lines.

- [ ] **Step 4: Create autogen.md** — ConversableAgent, GroupChat, code execution, nested conversations, teachability, custom agents. Min 80 lines.

- [ ] **Step 5: Create vercel-ai-sdk.md** — useChat, useCompletion, streamText, generateText, tool calling, provider registry, middleware. Min 80 lines.

- [ ] **Step 6: Create mcp-servers-guide.md** — Protocol overview, server implementation, tools/resources/prompts, transport (stdio/SSE), security, existing servers ecosystem. Min 80 lines.

- [ ] **Step 7: Create claude-api.md** — Messages API, tool use, vision, streaming, batches, prompt caching, system prompts, Anthropic SDK (Python/TS). Min 80 lines.

- [ ] **Step 8: Verify and Commit**

```bash
find tech-vault/03-ai-ml -name "*.md" | wc -l  # Expected: 10 (3 from Task 10 + 7)
git add tech-vault/03-ai-ml/ai-frameworks/ tech-vault/03-ai-ml/mcp/ tech-vault/03-ai-ml/tools/
git commit -m "feat(tech-vault): add AI frameworks, MCP guide, and Claude API skills"
```

---

### Task 12: Architecture — Patterns + Decisions (4 files)

**Files:**
- Create: `tech-vault/04-architecture/patterns/microservices.md`
- Create: `tech-vault/04-architecture/patterns/event-driven.md`
- Create: `tech-vault/04-architecture/patterns/clean-architecture.md`
- Create: `tech-vault/04-architecture/decisions/adr-template.md`

**Wikilink map:**
- microservices.md → `[[event-driven]]`, `[[clean-architecture]]`, `[[kubernetes-basics]]`, `[[messaging-patterns]]`, `[[docker]]`, `[[observability]]`
- event-driven.md → `[[kafka]]`, `[[rabbitmq]]`, `[[sqs-sns]]`, `[[nats]]`, `[[microservices]]`, `[[messaging-patterns]]`
- clean-architecture.md → `[[fastapi]]`, `[[django]]`, `[[microservices]]`, `[[typescript]]`, `[[python]]`
- adr-template.md → `[[clean-architecture]]`, `[[microservices]]`, `[[event-driven]]`, `[[adr-template|07 template]]`, `[[deployment-strategies]]`

- [ ] **Step 1: Create microservices.md** — Service decomposition, communication (sync/async), saga pattern, API gateway, service mesh, distributed tracing, data consistency. Min 80 lines.

- [ ] **Step 2: Create event-driven.md** — Event sourcing, CQRS, event bus, eventual consistency, dead letter queues, idempotency, ordering guarantees. Min 80 lines.

- [ ] **Step 3: Create clean-architecture.md** — Layers (entities, use cases, adapters, frameworks), dependency rule, ports & adapters, DI patterns, testing boundaries. Min 80 lines.

- [ ] **Step 4: Create adr-template.md** — ADR format (context, decision, consequences), numbering, status tracking, lightweight ADRs, examples. Note: this is the reference doc, not the Templater template (that's in 08-templates). Min 80 lines.

- [ ] **Step 5: Verify and Commit**

```bash
find tech-vault/04-architecture/patterns tech-vault/04-architecture/decisions -name "*.md" | wc -l  # Expected: 4
git add tech-vault/04-architecture/patterns/ tech-vault/04-architecture/decisions/
git commit -m "feat(tech-vault): add architecture patterns and ADR reference"
```

---

### Task 13: Architecture — Cloud Services + Messaging (7 files)

**Files:**
- Create: `tech-vault/04-architecture/cloud-services/cloudinary.md`
- Create: `tech-vault/04-architecture/cloud-services/s3-storage-patterns.md`
- Create: `tech-vault/04-architecture/cloud-services/media-pipeline.md`
- Create: `tech-vault/04-architecture/messaging/rabbitmq.md`
- Create: `tech-vault/04-architecture/messaging/sqs-sns.md`
- Create: `tech-vault/04-architecture/messaging/nats.md`
- Create: `tech-vault/04-architecture/messaging/messaging-patterns.md`

**Wikilink map:**
- cloudinary.md → `[[media-pipeline]]`, `[[s3-storage-patterns]]`, `[[nextjs]]`, `[[fastapi]]`, `[[dns-and-cdn]]`
- s3-storage-patterns.md → `[[cloudinary]]`, `[[media-pipeline]]`, `[[terraform]]`, `[[data-lake-patterns]]`, `[[secrets-management]]`
- media-pipeline.md → `[[cloudinary]]`, `[[s3-storage-patterns]]`, `[[dns-and-cdn]]`, `[[fastapi]]`, `[[nextjs]]`, `[[docker]]`
- rabbitmq.md → `[[messaging-patterns]]`, `[[sqs-sns]]`, `[[nats]]`, `[[docker]]`, `[[event-driven]]`, `[[microservices]]`
- sqs-sns.md → `[[messaging-patterns]]`, `[[rabbitmq]]`, `[[nats]]`, `[[terraform]]`, `[[event-driven]]`
- nats.md → `[[messaging-patterns]]`, `[[rabbitmq]]`, `[[sqs-sns]]`, `[[kubernetes-basics]]`, `[[event-driven]]`
- messaging-patterns.md → `[[rabbitmq]]`, `[[sqs-sns]]`, `[[nats]]`, `[[kafka]]`, `[[event-driven]]`, `[[microservices]]`

- [ ] **Step 1: Create cloudinary.md** — Upload API, transformations, signed URLs, auto-format/quality, folders, webhooks, SDKs (Node/Python), CDN delivery. Min 80 lines.

- [ ] **Step 2: Create s3-storage-patterns.md** — Presigned URLs, lifecycle policies, multi-region replication, versioning, encryption, event notifications, cost optimization. Min 80 lines.

- [ ] **Step 3: Create media-pipeline.md** — End-to-end flow: upload → validate → process → store → CDN → serve. Covers image optimization, video transcoding, thumbnail generation, lazy loading. Min 80 lines.

- [ ] **Step 4: Create rabbitmq.md** — Exchanges (direct, topic, fanout, headers), queues, bindings, DLQ, TTL, prefetch, clustering, shovel/federation. Min 80 lines.

- [ ] **Step 5: Create sqs-sns.md** — Standard vs FIFO, visibility timeout, DLQ, fan-out pattern, SNS filtering, batch operations, cost. Min 80 lines.

- [ ] **Step 6: Create nats.md** — Core NATS, JetStream, key-value store, object store, subjects, queue groups, leaf nodes. Min 80 lines.

- [ ] **Step 7: Create messaging-patterns.md** — Pub/sub, request-reply, saga, outbox, competing consumers, message deduplication, ordering, dead letter handling. Min 80 lines.

- [ ] **Step 8: Verify and Commit**

```bash
find tech-vault/04-architecture/cloud-services tech-vault/04-architecture/messaging -name "*.md" | wc -l  # Expected: 7
git add tech-vault/04-architecture/cloud-services/ tech-vault/04-architecture/messaging/
git commit -m "feat(tech-vault): add cloud services and messaging skills"
```

---

### Task 14: Data Engineering (10 files)

**Files:**
- Create: `tech-vault/05-data-engineering/pipelines/apache-airflow.md`
- Create: `tech-vault/05-data-engineering/pipelines/dagster.md`
- Create: `tech-vault/05-data-engineering/pipelines/prefect.md`
- Create: `tech-vault/05-data-engineering/streaming/kafka.md`
- Create: `tech-vault/05-data-engineering/streaming/flink.md`
- Create: `tech-vault/05-data-engineering/storage/data-lake-patterns.md`
- Create: `tech-vault/05-data-engineering/storage/delta-lake.md`
- Create: `tech-vault/05-data-engineering/storage/duckdb.md`
- Create: `tech-vault/05-data-engineering/transformation/dbt.md`
- Create: `tech-vault/05-data-engineering/transformation/spark.md`

**Wikilink map:**
- apache-airflow.md → `[[dagster]]`, `[[prefect]]`, `[[docker]]`, `[[kubernetes-basics]]`, `[[python]]`, `[[dbt]]`
- dagster.md → `[[apache-airflow]]`, `[[prefect]]`, `[[python]]`, `[[dbt]]`, `[[docker]]`
- prefect.md → `[[apache-airflow]]`, `[[dagster]]`, `[[python]]`, `[[docker]]`, `[[kubernetes-basics]]`
- kafka.md → `[[flink]]`, `[[event-driven]]`, `[[messaging-patterns]]`, `[[docker]]`, `[[kubernetes-basics]]`, `[[spark]]`
- flink.md → `[[kafka]]`, `[[spark]]`, `[[python]]`, `[[docker]]`, `[[data-lake-patterns]]`
- data-lake-patterns.md → `[[delta-lake]]`, `[[s3-storage-patterns]]`, `[[dbt]]`, `[[spark]]`, `[[duckdb]]`
- delta-lake.md → `[[data-lake-patterns]]`, `[[spark]]`, `[[dbt]]`, `[[s3-storage-patterns]]`, `[[duckdb]]`
- duckdb.md → `[[postgresql]]`, `[[python]]`, `[[delta-lake]]`, `[[data-lake-patterns]]`, `[[dbt]]`
- dbt.md → `[[postgresql]]`, `[[spark]]`, `[[data-lake-patterns]]`, `[[apache-airflow]]`, `[[dagster]]`
- spark.md → `[[python]]`, `[[kafka]]`, `[[flink]]`, `[[delta-lake]]`, `[[data-lake-patterns]]`, `[[dbt]]`

- [ ] **Step 1: Create apache-airflow.md** — DAGs, operators, sensors, XCom, connections/pools, TaskFlow API, dynamic DAGs, KubernetesExecutor. Min 80 lines.

- [ ] **Step 2: Create dagster.md** — Assets, ops, jobs, resources, IO managers, schedules, sensors, Dagit UI, software-defined assets. Min 80 lines.

- [ ] **Step 3: Create prefect.md** — Flows, tasks, deployments, work pools, blocks, artifacts, automations, Prefect Cloud. Min 80 lines.

- [ ] **Step 4: Create kafka.md** — Topics, partitions, consumer groups, exactly-once semantics, Schema Registry, Connect, Streams API, KRaft. Min 80 lines.

- [ ] **Step 5: Create flink.md** — DataStream API, windowing, state management, checkpointing, Table API, CEP, deployment modes. Min 80 lines.

- [ ] **Step 6: Create data-lake-patterns.md** — Medallion architecture (bronze/silver/gold), partitioning strategies, file formats (Parquet, ORC, Avro), schema evolution, lakehouse. Min 80 lines.

- [ ] **Step 7: Create delta-lake.md** — ACID transactions, time travel, schema enforcement/evolution, OPTIMIZE, Z-ORDER, Change Data Feed, Unity Catalog. Min 80 lines.

- [ ] **Step 8: Create duckdb.md** — In-process OLAP, Parquet/CSV/JSON reading, extensions, Python API, integration with pandas/polars, remote files. Min 80 lines.

- [ ] **Step 9: Create dbt.md** — Models, sources, tests, macros, snapshots, incremental models, packages, dbt Cloud, semantic layer. Min 80 lines.

- [ ] **Step 10: Create spark.md** — RDDs, DataFrames, Spark SQL, structured streaming, MLlib basics, PySpark, cluster management, optimization (catalyst, tungsten). Min 80 lines.

- [ ] **Step 11: Verify and Commit**

```bash
find tech-vault/05-data-engineering -name "*.md" | wc -l  # Expected: 10
git add tech-vault/05-data-engineering/
git commit -m "feat(tech-vault): add data engineering skills — pipelines, streaming, storage, transformation"
```

---

### Task 15: Snippets + References (7 files)

**Files:**
- Create: `tech-vault/06-snippets/python-snippets.md`
- Create: `tech-vault/06-snippets/bash-snippets.md`
- Create: `tech-vault/06-snippets/docker-snippets.md`
- Create: `tech-vault/06-snippets/sql-snippets.md`
- Create: `tech-vault/07-references/git-cheatsheet.md`
- Create: `tech-vault/07-references/regex-cheatsheet.md`
- Create: `tech-vault/07-references/big-o-notation.md`

**Context:** Snippets are copy-paste-ready code blocks. References are compact cheatsheets with tables. Both follow simplified templates (no Overview/Patterns/Gotchas — just the content).

**Wikilink map:**
- python-snippets.md → `[[python]]`, `[[fastapi]]`, `[[django]]`, `[[bash-snippets]]`, `[[docker-snippets]]`
- bash-snippets.md → `[[git-advanced]]`, `[[docker]]`, `[[python-snippets]]`, `[[git-cheatsheet]]`, `[[docker-snippets]]`
- docker-snippets.md → `[[docker]]`, `[[docker-compose-patterns]]`, `[[bash-snippets]]`, `[[kubernetes-basics]]`, `[[python-snippets]]`
- sql-snippets.md → `[[postgresql]]`, `[[database-optimization]]`, `[[dbt]]`, `[[supabase]]`, `[[python-snippets]]`
- git-cheatsheet.md → `[[git-advanced]]`, `[[github-actions]]`, `[[bash-snippets]]`, `[[regex-cheatsheet]]`, `[[deployment-strategies]]`
- regex-cheatsheet.md → `[[python]]`, `[[typescript]]`, `[[bash-snippets]]`, `[[git-cheatsheet]]`, `[[big-o-notation]]`
- big-o-notation.md → `[[database-optimization]]`, `[[python]]`, `[[rust]]`, `[[regex-cheatsheet]]`, `[[git-cheatsheet]]`

- [ ] **Step 1: Create python-snippets.md** — File I/O, async patterns, decorators, context managers, dataclass/pydantic, httpx, pathlib, itertools. Min 80 lines.

- [ ] **Step 2: Create bash-snippets.md** — File operations, process management, text processing, networking, loops, conditionals, ssh, cron. Min 80 lines.

- [ ] **Step 3: Create docker-snippets.md** — Dockerfile patterns, compose templates, multi-stage, health checks, volume mounts, network configs. Min 80 lines.

- [ ] **Step 4: Create sql-snippets.md** — CTEs, window functions, upserts, JSON queries, aggregations, performance patterns, migrations. Min 80 lines.

- [ ] **Step 5: Create git-cheatsheet.md** — Branches, stash, rebase, cherry-pick, reflog, bisect, aliases, common workflows. Table format. Min 80 lines.

- [ ] **Step 6: Create regex-cheatsheet.md** — Quantifiers, groups, lookahead/behind, character classes, common patterns (email, URL, IP, semver). Table format. Min 80 lines.

- [ ] **Step 7: Create big-o-notation.md** — Time/space complexities, common algorithms, data structure operations table, amortized analysis, practical implications. Min 80 lines.

- [ ] **Step 8: Verify and Commit**

```bash
find tech-vault/06-snippets tech-vault/07-references -name "*.md" | wc -l  # Expected: 7
git add tech-vault/06-snippets/ tech-vault/07-references/
git commit -m "feat(tech-vault): add snippets and reference cheatsheets"
```

---

### Task 16: Templates (4 files)

**Files:**
- Create: `tech-vault/08-templates/skill-template.md`
- Create: `tech-vault/08-templates/project-template.md`
- Create: `tech-vault/08-templates/adr-template.md`
- Create: `tech-vault/08-templates/weekly-review.md`

**Context:** These use Templater syntax (`<% %>`) for interactive prompts and dynamic dates. They are NOT regular skill files — they are templates that generate new files when invoked via Templater.

- [ ] **Step 1: Create skill-template.md**

Templater template that generates a new skill file with:
- Frontmatter with `<% tp.system.prompt("Skill name") %>`, `<% tp.date.now("YYYY-MM-DD") %>`
- All standard sections pre-filled with placeholder prompts
- Tag prompt: `<% tp.system.prompt("Tags (comma-separated)") %>`
- Level prompt: `<% tp.system.suggester(["beginner","intermediate","advanced"], ["beginner","intermediate","advanced"]) %>`

- [ ] **Step 2: Create project-template.md**

Templater template for new project files:
- Project name prompt, date, status
- Sections: Objective, Stack, Architecture, Tasks (with Tasks plugin checkboxes), Timeline, Notes

- [ ] **Step 3: Create adr-template.md**

Templater template for Architecture Decision Records:
- ADR number prompt, title, date
- Sections: Context, Decision, Consequences (positive/negative/neutral), Status

- [ ] **Step 4: Create weekly-review.md**

Templater template for weekly reviews:
- Auto-generated date range (current week)
- Sections: Wins, Challenges, Learnings, Next Week Goals
- Dataview query to show tasks completed this week

- [ ] **Step 5: Verify and Commit**

```bash
find tech-vault/08-templates -name "*.md" | wc -l  # Expected: 4
git add tech-vault/08-templates/
git commit -m "feat(tech-vault): add Templater templates — skill, project, ADR, weekly-review"
```

---

### Task 17: Canvas Files (3 files)

**Files:**
- Create: `tech-vault/09-canvas/tech-stack-overview.canvas`
- Create: `tech-vault/09-canvas/learning-paths.canvas`
- Create: `tech-vault/09-canvas/data-pipeline-map.canvas`

**Context:** Canvas files are JSON. Each node can be a `text` node or a `file` node (linking to a `.md` file). Nodes have `x`, `y`, `width`, `height`. Edges connect nodes by `id`.

- [ ] **Step 1: Create tech-stack-overview.canvas**

JSON canvas with 5 groups (Frontend, Backend, Database, Infrastructure, Monitoring) arranged top-to-bottom. Each group contains file nodes linking to relevant `.md` files. Edges connect layers.

- [ ] **Step 2: Create learning-paths.canvas**

JSON canvas with 4 horizontal paths (Full-Stack, DevOps, AI/ML, Data Engineering). Each path has 4-5 nodes progressing from foundational to advanced, linked by edges.

- [ ] **Step 3: Create data-pipeline-map.canvas**

JSON canvas showing: Sources → Ingestion → Processing → Storage → Serving. Each stage has file nodes linking to the corresponding data engineering `.md` files.

- [ ] **Step 4: Verify and Commit**

```bash
find tech-vault/09-canvas -name "*.canvas" | wc -l  # Expected: 3
git add tech-vault/09-canvas/
git commit -m "feat(tech-vault): add canvas files — tech-stack, learning-paths, data-pipeline"
```

---

### Task 18: Final Verification + Wikilink Audit

- [ ] **Step 1: Count all files**

```bash
find tech-vault -name "*.md" | wc -l
```
Expected: ~81 markdown files

```bash
find tech-vault -name "*.canvas" | wc -l
```
Expected: 3 canvas files

- [ ] **Step 2: Verify minimum line count**

```bash
find tech-vault -name "*.md" -exec sh -c 'lines=$(wc -l < "$1"); if [ "$lines" -lt 80 ]; then echo "SHORT: $1 ($lines lines)"; fi' _ {} \;
```
Expected: no output (all files >= 80 lines). Template files in `08-templates/` are exempt if shorter.

- [ ] **Step 3: Verify wikilink density**

```bash
find tech-vault -name "*.md" -exec sh -c 'count=$(grep -o "\[\[" "$1" | wc -l); if [ "$count" -lt 5 ]; then echo "LOW LINKS: $1 ($count)"; fi' _ {} \;
```
Expected: no output (all files >= 5 wikilinks). Template files exempt.

- [ ] **Step 4: Verify frontmatter**

```bash
find tech-vault -name "*.md" -exec sh -c 'head -1 "$1" | grep -q "^---" || echo "NO FRONTMATTER: $1"' _ {} \;
```
Expected: no output (all files have frontmatter). Template files use Templater syntax for frontmatter so they still start with `---`.

- [ ] **Step 5: Final commit if any fixes needed**

```bash
git add -A tech-vault/
git commit -m "fix(tech-vault): wikilink and quality audit fixes"
```

Only run if fixes were made in previous steps.
