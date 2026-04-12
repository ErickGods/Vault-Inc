# Vault Inc.

Software house multi-agente orquestrada pelo Claude Code.

## Estrutura

```
vault-inc/
├── CLAUDE.md                    ← Orquestração principal (leia primeiro)
├── .claude/
│   └── agents/                  ← System prompts dos agentes
│       ├── pm.md
│       ├── lead-engineer.md
│       ├── ui-ux.md
│       ├── frontend.md
│       ├── backend.md
│       ├── devops.md
│       ├── qa.md
│       ├── security.md
│       ├── data-engineer.md
│       └── ml-engineer.md
├── vault/                       ← Obsidian vault (memória persistente)
│   ├── projects/intake/         ← Coloque aqui os escopos de novos projetos
│   ├── decisions/               ← ADRs
│   ├── specs/                   ← UI/UX e API specs
│   ├── reports/                 ← QA, Security, Data
│   └── standups/                ← Logs diários
└── projects/                    ← Código dos projetos
    └── <nome-projeto>/
```

## Time

| Agente | Especialidade |
|--------|--------------|
| PM | Intake, planejamento, distribuição |
| Lead Engineer | Arquitetura, revisão técnica, ADRs |
| UI/UX Designer | Design system, specs visuais, fluxos |
| Frontend Engineer | React/Next.js, TypeScript, Tailwind |
| Backend Engineer | APIs, banco de dados, autenticação |
| DevOps Engineer | Docker, CI/CD, infra, cloud |
| QA Engineer | Testes automatizados, bug reports |
| Security Engineer | Auditorias OWASP, compliance |
| Data Engineer | Pipelines ETL, modelagem de dados |
| ML Engineer | Modelos, LLMs, RAG, MLOps |

## Iniciando um projeto

1. Crie um arquivo de escopo baseado em `vault/projects/intake/PROJECT_INTAKE_TEMPLATE.md`
2. Salve em `vault/projects/intake/<nome>.md`
3. No Claude Code, execute:

```
PM, leia o intake em vault/projects/intake/<nome>.md e inicie o projeto
```

## Documentação
Veja `vault/README.md` para convenções de documentação.
Veja `CLAUDE.md` para o fluxo completo de orquestração.
