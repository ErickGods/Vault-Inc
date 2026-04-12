# Vault Inc. — Knowledge Base

Este é o Obsidian vault da Vault Inc. Toda a memória persistente da empresa vive aqui.

## Estrutura

```
vault/
├── projects/
│   ├── intake/          ← Coloque aqui os .md de escopo de novos projetos
│   └── <nome-projeto>/
│       ├── brief.md     ← Resumo executivo gerado pelo PM
│       ├── tasks.md     ← Breakdown de tarefas e status
│       └── summary.md   ← Fechamento do projeto
│
├── decisions/           ← ADRs (Architecture Decision Records)
│   └── ADR-XXX-titulo.md
│
├── specs/
│   ├── ui-ux/           ← Specs de componentes e design system
│   └── api/             ← Documentação de endpoints e schemas de dados
│
├── reports/
│   ├── qa/              ← Planos de teste, bugs e relatórios de QA
│   ├── security/        ← Auditorias de segurança
│   └── data/            ← Documentação de pipelines e avaliação de modelos
│
└── standups/            ← Log diário de atividades dos agentes
    └── YYYY-MM-DD.md
```

## Como iniciar um projeto

1. Copie `vault/projects/intake/PROJECT_INTAKE_TEMPLATE.md`
2. Renomeie para `vault/projects/intake/<nome-do-projeto>.md`
3. Preencha o template com o escopo do projeto
4. Execute no Claude Code:
   ```
   PM, leia o intake em vault/projects/intake/<nome>.md e inicie o projeto
   ```

## Convenções de nomenclatura

| Tipo | Formato |
|------|---------|
| ADR | `ADR-001-titulo-da-decisao.md` |
| Report QA | `<projeto>-<YYYY-MM-DD>.md` |
| Report Security | `<projeto>-<YYYY-MM-DD>.md` |
| Spec UI/UX | `<projeto>-<componente>.md` |
| Spec API | `<projeto>-<dominio>.md` |
| Standup | `<YYYY-MM-DD>.md` |
