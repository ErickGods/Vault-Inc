---
tags: [template, docs, claude-code, skill]
status: active
type: template
updated: 2026-04-10
created: 2026-04-10
aliases: [Skill Template, Claude Skill Template]
---

# Skill Template — Claude Code

> [!template] Como Usar
> Use este template para criar novas skills do Claude Code. Skills são arquivos Markdown com frontmatter especial que definem comportamentos acionados por comandos `/skill-name`. Salve o resultado em `.claude/skills/` (global) ou `.claude/skills/` do projeto.

> [!tip] Templater Version
> Para criar skills diretamente no Obsidian com prompts interativos, use o template Templater em `tech-vault/08-templates/skill-template.md`.

---

## Template — Skill Rígida (Checklist Obrigatório)

```yaml
---
name: {{nome-da-skill}}
description: {{Descrição em uma linha — usada para matching}}
---
```

```markdown
# {{Nome da Skill}}

## Instruções

{{Descreva o que a skill faz, quando deve ser usada, e qual é o objetivo final.
Seja específico — o agente seguirá estas instruções literalmente.}}

## Checklist Obrigatório

- [ ] {{Step 1}}: {{descrição do que verificar/fazer}}
- [ ] {{Step 2}}: {{descrição do que verificar/fazer}}
- [ ] {{Step 3}}: {{descrição do que verificar/fazer}}
- [ ] {{Step 4}}: {{descrição do que verificar/fazer}}
- [ ] {{Step 5}}: {{descrição do que verificar/fazer}}

## Formato do Output

\```
{{formato esperado do output — exemplo concreto}}
\```

## Exemplos

### Input
{{exemplo de input/trigger}}

### Output Esperado
{{exemplo de output correto}}

## Gotchas

> [!warning] Cuidados
> - {{Gotcha 1}}
> - {{Gotcha 2}}
```

---

## Template — Skill Flexível (Fluxo Adaptativo)

```yaml
---
name: {{nome-da-skill}}
description: {{Descrição em uma linha}}
---
```

```markdown
# {{Nome da Skill}}

## Contexto

{{Quando esta skill deve ser invocada. Quais sinais indicam que ela é relevante.}}

## Processo

### Fase 1: {{Nome}}
{{Instruções para a primeira fase. O agente decide a ordem baseado no contexto.}}

### Fase 2: {{Nome}}
{{Instruções para a segunda fase.}}

### Fase 3: {{Nome}}
{{Instruções para a terceira fase.}}

## Princípios

- {{Princípio 1}} — {{por que importa}}
- {{Princípio 2}} — {{por que importa}}
- {{Princípio 3}} — {{por que importa}}

## Output Esperado

{{Descrição do que a skill deve produzir ao final.}}
```

---

## Campos do Frontmatter de Skills

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| name | Sim | Identificador único da skill |
| description | Sim | Linha usada para matching — seja específico |

## Onde Salvar Skills

| Local | Escopo | Prioridade |
|-------|--------|------------|
| `~/.claude/skills/` | Global (todas as sessões) | Normal |
| `.claude/skills/` (projeto) | Apenas este projeto | Alta (sobrescreve global) |

## Dicas para Skills Eficazes

1. **Seja específico no description** — é o campo que o Claude usa para decidir se a skill se aplica
2. **Rigid para processos** — use checklist quando a ordem importa (deploy, review, TDD)
3. **Flexible para criatividade** — use fases quando o agente precisa adaptar (brainstorming, design)
4. **Teste antes de deployar** — invoque a skill com `/skill-name` e veja se o comportamento é o esperado
5. **Mantenha curto** — skills longas (>200 linhas) consomem contexto; divida em sub-skills

## Related

- [[agent-template]] — template para definir agentes
- [[skills-system]] — guia completo do sistema de skills (claude-vault)
- [[hook-snippets]] — snippets de hooks que complementam skills
