---
tags: [skill, ai-ml, claude-code-superpowers]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Superpowers, Claude Code Superpowers]
---

# Claude Code Superpowers

## Overview

Claude Code Superpowers é um sistema de skills (habilidades codificadas) que transforma Claude Code de um assistente reativo em um agente de desenvolvimento estruturado. Skills são arquivos Markdown especiais com frontmatter YAML que definem comportamentos acionados por comandos `/skill-name`. O sistema distingue entre **rigid skills** (comportamento determinístico com checklists obrigatórios) e **flexible skills** (fluxos adaptativos baseados em contexto).

> [!important] Skill Priority
> Skills definidas no projeto (`.claude/skills/`) sobrescrevem skills globais (`~/.claude/skills/`). Skills com `priority: high` no frontmatter têm precedência durante conflitos de nome.

Veja [[claude-code]] para configuração base e [[mcp-servers-guide]] para integração com servidores externos.

## Core Concepts

### Rigid vs Flexible Skills

**Rigid Skills** — usadas quando consistência é crítica. Implementam checklists com checkboxes que o agente deve marcar antes de avançar:

```markdown
<!-- skill: deploy-check -->
## Pre-deploy Checklist
- [ ] Tests passing (>80% coverage)
- [ ] No console.log in production code
- [ ] Environment variables documented
- [ ] Rollback plan defined
```

**Flexible Skills** — fornecem estrutura sem impor sequência rígida. Úteis para fluxos criativos como brainstorming e design. O agente decide a ordem das etapas com base no contexto.

### Skill Frontmatter Structure

```yaml
---
name: tdd
version: "1.2"
trigger: /tdd
priority: high
mode: rigid          # rigid | flexible
requires: []         # outras skills necessárias
outputs: [test-file, implementation]
---
```

### Brainstorming Flow: Idea → Design → Spec

O fluxo de três etapas para transformar ideias vagas em especificações acionáveis:

```
/brainstorm "sistema de notificações em tempo real"
  → Fase 1: Expansão (10+ variações da ideia)
  → Fase 2: Design (arquitetura, trade-offs)
  → Fase 3: Spec (documento estruturado com critérios de aceitação)
```

A skill brainstorm opera em modo **flexible** porque cada ideia exige abordagem diferente. O output é sempre um arquivo `spec.md` padronizado consumível pela planning skill.

## Patterns

### Planning Skill: Spec → Implementation Plan

A planning skill recebe um `spec.md` e produz um plano de implementação com tasks atômicas:

```markdown
/plan spec.md

Output gerado:
## Implementation Plan
### Phase 1: Foundation (2h)
- [ ] Task 1.1: Criar schema do banco (30min)
  - Arquivo: `db/schema.sql`
  - Critério: migrations rodando sem erros
- [ ] Task 1.2: Models com validação (45min)
  - Arquivo: `src/models/notification.ts`
  - Critério: testes unitários passando
```

Cada task tem: estimativa de tempo, arquivo alvo, critério de conclusão mensurável. Isso permite que [[multi-agent-systems]] paralelizem trabalho sem conflitos.

### TDD Skill: Red-Green-Refactor Enforcement

```markdown
/tdd src/services/notification.ts

Ciclo obrigatório:
1. RED: Escrever teste que falha
   → Claude DEVE mostrar output do teste falhando
2. GREEN: Implementação mínima para passar
   → Proibido implementar além do necessário
3. REFACTOR: Melhorar sem quebrar testes
   → Claude verifica cobertura antes de avançar
```

O enforcement é feito via checklist rígido — Claude não pode pular para a próxima iteração sem confirmar cada etapa.

```typescript
// Exemplo: Red phase obrigatório
describe('NotificationService', () => {
  it('should queue notification when user is offline', async () => {
    const service = new NotificationService(mockDb);
    const result = await service.send('user-123', { type: 'alert' });
    expect(result.queued).toBe(true); // FALHA — método não existe ainda
  });
});
```

### Subagent-Driven Development

Padrão de 3 agentes para implementação de alta qualidade:

```
Orchestrator
├── Implementer Agent → produz código
├── Reviewer Agent 1 → revisa lógica e arquitetura
└── Reviewer Agent 2 → revisa segurança e performance
```

Configuração via [[claude-api]] com model sampling:

```python
# Orchestrator lança subagentes em paralelo
implementer = await claude.messages.create(
    model="claude-opus-4-5",
    system="You are an expert implementer. Focus on correctness.",
    messages=[{"role": "user", "content": spec}]
)

reviewer_1 = await claude.messages.create(
    model="claude-sonnet-4-5",
    system="Review for architecture and logic flaws.",
    messages=[{"role": "user", "content": implementer.content}]
)
```

### Executing-Plans Skill

```markdown
/execute-plan plan.md

Comportamento:
- Lê tasks em ordem (ou paralelas se marcadas como [parallel])
- Executa cada task usando ferramentas disponíveis
- Atualiza checkboxes: [ ] → [x] após conclusão
- Para e reporta se task falhar (não pula silenciosamente)
- Salva progresso a cada task concluída
```

### Worktrees for Isolation

Git worktrees permitem que múltiplos agentes trabalhem simultaneamente sem conflitos:

```bash
# Setup para desenvolvimento paralelo
git worktree add ../feature-auth feature/auth
git worktree add ../feature-notif feature/notifications

# Cada agente opera em seu worktree
claude --worktree ../feature-auth /execute-plan auth-plan.md
claude --worktree ../feature-notif /execute-plan notif-plan.md
```

> [!tip] Worktree + Subagents
> Combine worktrees com subagent-driven development: o orchestrator cria os worktrees e lança implementers em cada um. Ao final, faz merge das branches.

## Gotchas

> [!warning] Skill Trigger Collision
> Dois skills com o mesmo trigger causam comportamento indefinido. Sempre verifique com `claude --list-skills` antes de criar novas skills.

> [!bug] Rigid Skills e Context Window
> Checklists muito longos (>50 items) podem ser truncados se o contexto for longo. Divida em sub-skills chamadas em sequência.

> [!caution] Subagent Cost
> Cada subagente é uma chamada separada à API. Um fluxo implementer + 2 reviewers pode custar 3-5x o custo de uma única chamada. Use [[prompt-engineering]] para minimizar tokens.

## Snippets

### Escrever uma Custom Skill

```markdown
---
name: conventional-commit
trigger: /commit
mode: rigid
priority: normal
---

# Conventional Commit Skill

## Instruções
Gere uma mensagem de commit seguindo Conventional Commits.

## Checklist Obrigatório
- [ ] Analisar git diff completo
- [ ] Identificar tipo: feat|fix|docs|refactor|test|chore
- [ ] Verificar escopo (opcional)
- [ ] Confirmar breaking changes (BREAKING CHANGE:)
- [ ] Gerar mensagem no formato correto

## Formato
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```
```

### Skill com Outputs Estruturados

```yaml
---
name: api-design
trigger: /api-design
mode: flexible
outputs:
  - openapi.yaml
  - implementation-plan.md
  - test-plan.md
---
```

### Skill Priority Rules

```
Ordem de precedência (maior → menor):
1. Project skills com priority: critical
2. Project skills com priority: high
3. Project skills com priority: normal
4. Global skills com priority: high
5. Global skills com priority: normal
6. Built-in Claude Code behaviors
```

## References

- [Claude Code Docs](https://docs.anthropic.com/claude-code)
- [Skill System RFC](https://github.com/anthropics/claude-code/discussions)
- [[prompt-engineering]] — otimizar instruções nas skills
- [[multi-agent-systems]] — orquestrar múltiplos agentes

## Related

- [[claude-code]] — base do sistema
- [[mcp-servers-guide]] — integrar ferramentas externas via MCP
- [[claude-api]] — API subjacente usada pelos subagentes
- [[multi-agent-systems]] — padrões de orquestração
- [[prompt-engineering]] — escrever melhores instruções de skill
