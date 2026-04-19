---
tags: [template, docs, project-management]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Project Intake Template, Intake Template]
---

# Project Intake Template

> [!template] Como Usar
> Use este template para iniciar qualquer novo projeto na Vault Inc. Preencha o máximo de campos possível e deposite em `vault/projects/intake/`. O PM agent lê o intake e cria o breakdown de tarefas.

> [!info] Template Original
> Versão estendida do template em `.claude/agents/PROJECT_INTAKE_TEMPLATE.md`. Esta versão inclui instruções e exemplos para cada seção.

---

## Template

```markdown
# Project Intake — {{Nome do Projeto}}

> Deposite em `vault/projects/intake/` e instrua o PM:
> "PM, leia o intake em vault/projects/intake/{{nome}}.md e inicie o projeto"

---

## 1. Visão Geral

**Nome do projeto:** {{nome}}
**Data de criação:** {{YYYY-MM-DD}}
**Solicitante:** {{quem pediu o projeto}}

**Descrição em uma frase:**
> {{Ex: "Uma plataforma web para gestão de contratos com assinatura digital."}}

**Problema que resolve:**
> {{Qual dor ou oportunidade este projeto endereça?}}

---

## 2. Objetivos

**O que é sucesso para este projeto?**
- {{Critério de sucesso mensurável 1}}
- {{Critério de sucesso mensurável 2}}

**O que está fora do escopo (explicitamente)?**
- {{Exclusão 1}}
- {{Exclusão 2}}

---

## 3. Usuários e Personas

| Persona | Perfil | Necessidade Principal |
|---------|--------|----------------------|
| {{Persona 1}} | {{descrição}} | {{necessidade}} |
| {{Persona 2}} | {{descrição}} | {{necessidade}} |

---

## 4. Funcionalidades

### Must Have (obrigatório para MVP)
- [ ] {{Feature 1}} — {{descrição}}
- [ ] {{Feature 2}} — {{descrição}}

### Should Have (importante, mas não bloqueante)
- [ ] {{Feature 3}} — {{descrição}}

### Nice to Have (futuro)
- [ ] {{Feature 4}} — {{descrição}}

---

## 5. Stack e Tecnologias

> Deixe em branco para o Lead Engineer decidir.

| Layer | Tecnologia | Notas |
|-------|-----------|-------|
| Frontend | {{ou vazio}} | |
| Backend | {{ou vazio}} | |
| Database | {{ou vazio}} | |
| Auth | {{ou vazio}} | |
| Infra | {{ou vazio}} | |
| Integrações | {{APIs externas}} | |

---

## 6. Dados e IA

**Envolve dados?** {{sim/não}}
- Fontes: {{de onde vêm os dados}}
- Volume: {{estimativa}}

**Envolve ML/IA?** {{sim/não}}
- Tipo: {{classificação / geração / recomendação / RAG / outro}}
- Dados para treino: {{disponibilidade}}

---

## 7. Segurança e Compliance

**Dados sensíveis:** {{PII, financeiros, saúde?}}
**Regulamentações:** {{LGPD, GDPR, PCI-DSS, HIPAA?}}
**Criticidade:** {{Baixo | Médio | Alto | Crítico}}

---

## 8. Restrições

**Prazo:** {{data ou "sem prazo definido"}}
**Budget:** {{se aplicável}}
**Dependências:** {{sistemas existentes, APIs, equipes}}

---

## 9. Referências

- {{Link para inspiração/produto similar}}
- {{Link para documento relacionado}}
- {{Link para design/Figma}}

---

## 10. Notas Adicionais

> {{Contexto extra para o PM e agentes.}}
```

## Related

- [[new-project-workflow]] — workflow completo após intake
- [[agent-template]] — como os agentes são configurados
- [[🗺️ Docs-Home]] — índice de templates
