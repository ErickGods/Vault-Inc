# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Vault Inc. Library is a **multi-agent AI orchestration system** built on Claude Code, functioning as a lean software house. It combines three Obsidian knowledge vaults (tech, finance, project execution) with specialized AI agents that coordinate to deliver software projects.

**Primary language:** Portuguese (BR) for all documentation, agent prompts, and project artifacts.

## Agent System

The orchestrator coordinates 10 specialized agents defined in `.claude/agents/`. Each agent has scoped responsibilities and tools:

- **PM** — project intake, task breakdown, agent dispatch
- **Lead Engineer** — architecture, ADRs, technical review, conflict resolution
- **UI/UX Designer** — wireframes, design system, component specs (must run before Frontend)
- **Frontend Engineer** — React/Next.js, TypeScript, Tailwind implementation
- **Backend Engineer** — APIs, database modeling, auth, business logic
- **DevOps Engineer** — Docker, CI/CD, Kubernetes, infrastructure as code
- **QA Engineer** — test plans, automated tests, bug reports
- **Security Engineer** — OWASP audits, vulnerability scanning, compliance
- **Data Engineer** — ETL/ELT pipelines, data modeling, Airflow/Prefect
- **ML Engineer** — model training, LLM integration, RAG, MLOps

Agents are invoked via the `Agent` tool with `subagent_type` matching the agent name.

## Project Workflow

```
1. User creates intake doc → vault/projects/intake/<project>.md
2. PM reads intake → creates brief + task breakdown
3. Agents execute tasks in dependency order
4. Lead Engineer validates technical decisions
5. QA + Security generate reports
6. PM closes with summary
```

To start a project:
```
PM, leia o intake em vault/projects/intake/<nome>.md e inicie o projeto
```

## Directory Structure Conventions

| Path | Purpose |
|------|---------|
| `vault/projects/intake/` | New project scope documents |
| `vault/projects/<project>/tasks.md` | Task breakdown per project |
| `vault/projects/<project>/summary.md` | Project closure report |
| `vault/decisions/ADR-<n>-<title>.md` | Architecture Decision Records |
| `vault/specs/ui-ux/` | UI/UX specifications |
| `vault/specs/api/` | API specifications |
| `vault/reports/qa/<project>-<date>.md` | QA test reports |
| `vault/reports/security/<project>-<date>.md` | Security audit reports |
| `vault/standups/<YYYY-MM-DD>.md` | Daily standup logs |
| `projects/<project>/` | Actual project source code |

## Knowledge Vaults

- **tech-vault/** — Technical knowledge base: languages, frameworks, DevOps, AI/ML, architecture patterns, code snippets, references, templates
- **finance-vault/** — Financial knowledge base: investment analysis, asset classes, personal finance, market analysis
- **claude-vault/agents/financial-research-house/** — Specialized financial research agents (Equity Research Analyst, Private Banker)

## Collaboration Rules

- Each agent documents daily work in standups
- Architecture decisions always require an ADR
- Cross-scope conflicts escalate to Lead Engineer
- No agent writes outside its scope without Lead Engineer approval
- UI/UX Designer must run before Frontend Engineer
- Project intake uses the template at `.claude/agents/PROJECT_INTAKE_TEMPLATE.md`
