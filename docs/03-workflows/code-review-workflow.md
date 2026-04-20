---
tags: [workflow, docs, code-review]
status: active
type: workflow
updated: 2026-04-10
created: 2026-04-10
aliases: [Code Review Workflow, Workflow de Code Review]
---

# Code Review Workflow

> Workflow para realizar code review usando agentes da Vault Inc, garantindo qualidade, segurança e consistência.

## Quando Usar

- Após implementação de features
- Antes de merge para branch principal
- Quando há código complexo que precisa de validação

## Output Esperado

- Código revisado e aprovado
- Issues encontrados documentados
- Sugestões de melhoria aplicadas

## Diagrama de Fluxo

```mermaid
graph TD
    A[Código pronto para review] --> B[QA Agent - Review funcional]
    A --> C[Security Agent - Review segurança]
    B --> D{Issues encontrados?}
    C --> E{Vulnerabilidades?}
    D -->|Sim| F[Implementer corrige]
    D -->|Não| G[✅ QA Approved]
    E -->|Sim| H[Implementer corrige]
    E -->|Não| I[✅ Security Approved]
    F --> B
    H --> C
    G --> J{Ambos aprovaram?}
    I --> J
    J -->|Sim| K[Lead Engineer - Final review]
    K --> L[✅ Merge approved]
```

## Steps

### Fase 1: Submission

- [ ] **1.1** Implementer marca código como pronto para review
- [ ] **1.2** Garantir que testes estão passando
- [ ] **1.3** Garantir que não há console.log / debug code

### Fase 2: Parallel Reviews

- [ ] **2.1** QA Agent revisa: funcionalidade, edge cases, test coverage
- [ ] **2.2** Security Agent revisa: OWASP Top 10, injection, auth, secrets
- [ ] **2.3** Ambos documentam findings

### Fase 3: Fix & Re-review

- [ ] **3.1** Implementer corrige issues encontrados
- [ ] **3.2** Re-submit para re-review dos items corrigidos
- [ ] **3.3** Repeat até ambos aprovarem

### Fase 4: Final Approval

- [ ] **4.1** Lead Engineer faz review final (arquitetura, padrões)
- [ ] **4.2** Se aprovado: merge
- [ ] **4.3** Se necessário ADR: criar usando [[adr-template]]

## Review Checklist — QA

- [ ] Funcionalidade atende requirements
- [ ] Edge cases cobertos
- [ ] Error handling adequado
- [ ] Test coverage > 80%
- [ ] Sem código dead/debug

## Review Checklist — Security

- [ ] Sem SQL injection
- [ ] Sem XSS
- [ ] Input validation presente
- [ ] Auth/AuthZ corretos
- [ ] Secrets não hardcoded
- [ ] Dependencies sem CVEs conhecidas

## Related

- [[new-project-workflow]] — workflow pai
- [[adr-template]] — para decisões de arquitetura durante review
