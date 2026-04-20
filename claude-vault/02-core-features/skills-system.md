---
tags: [claude-code, core-features, skills]
status: active
level: intermediate
updated: 2026-04-19
created: 2026-04-19
---

# Sistema de Skills — Claude Code

## O que são Skills

Skills são comportamentos reutilizáveis que você ensina ao Claude Code. Uma skill é basicamente um arquivo Markdown com instruções estruturadas que o Claude executa automaticamente quando invocada — seja pelo nome direto, por um slash command, ou por matching semântico baseado na descrição.

O conceito central é separar "o que fazer" (a skill) de "quando fazer" (o contexto da conversa). Em vez de reexplicar um processo toda vez, você escreve uma vez e reutiliza indefinidamente.

Skills são armazenadas como arquivos `.md` e lidas pelo Claude Code no início de cada sessão. São diferentes de CLAUDE.md (que define contexto geral do projeto) e de comandos slash (que são ações pontuais). Uma skill define um *comportamento contínuo* ou um *processo step-by-step* com profundidade técnica.

---

## Tipos de Skills: Rigid vs Flexible

### Skills Rígidas (Rigid Skills)

Skills rígidas definem um processo exato, com passos numerados, verificações mandatórias e critérios de saída claros. Não há margem para interpretação — o Claude segue o script.

Usadas quando:
- O processo tem consequências sérias (deploy, migração de banco, push para main)
- Há auditoria ou compliance envolvido
- A consistência é mais importante que a flexibilidade

Características:
- Passos numerados obrigatórios
- Critérios de entrada e saída explícitos
- Seção de "nunca faça X" para guardrails
- Verificações de estado antes de avançar

### Skills Flexíveis (Flexible Skills)

Skills flexíveis definem um estilo, abordagem ou conjunto de princípios. O Claude adapta a execução ao contexto. Usadas para code review, escrita de documentação, geração de commits.

Usadas quando:
- O processo muda dependendo do contexto
- A qualidade da saída importa mais que o processo exato
- Requer julgamento situacional

---

## Frontmatter de uma Skill

Todo arquivo de skill começa com frontmatter YAML que o Claude Code usa para indexação e matching:

```yaml
---
name: conventional-commit
description: Gera mensagens de commit seguindo o padrão Conventional Commits com escopo, tipo e breaking changes
version: 1.0
tags: [git, commits, workflow]
---
```

Campos disponíveis:

| Campo | Obrigatório | Descrição |
|-------|-------------|-----------|
| `name` | Sim | Identificador único da skill. Usado para invocação direta. |
| `description` | Sim | Descrição semântica. O Claude usa este campo para matching automático. |
| `version` | Não | Versão da skill para controle de mudanças. |
| `tags` | Não | Categorização para filtros e descoberta. |
| `author` | Não | Identificação do autor para skills compartilhadas em equipe. |
| `requires` | Não | Dependências (outras skills, ferramentas externas). |

> [!warning] O campo `description` é o mais crítico para matching automático. Uma description vaga resulta em a skill nunca ser invocada automaticamente. Seja ultra-específico: descreva a situação exata em que a skill deve ser usada.

---

## Como o Claude Faz Matching de Skills

O Claude Code carrega todas as skills disponíveis no início da sessão e mantém um índice semântico baseado nas descriptions. O matching acontece em três cenários:

### 1. Invocação Explícita

O usuário digita o nome da skill diretamente:

```
Use the conventional-commit skill to write this commit message
```

ou via slash command se a skill estiver configurada como tal:

```
/conventional-commit
```

### 2. Matching Semântico Automático

O Claude analisa o request do usuário e compara semanticamente com as descriptions das skills disponíveis. Se a similarity score for suficientemente alta, a skill é invocada automaticamente.

Exemplo: o usuário diz "preciso fazer commit dessas mudanças" — o Claude faz matching com a skill `conventional-commit` pela description "Gera mensagens de commit seguindo o padrão Conventional Commits".

### 3. Skill Tool

O Claude pode invocar outras skills programaticamente usando a `Skill tool`, passando o `name` da skill como parâmetro. Isso é usado em skills de orquestração (coordinator patterns).

---

## Onde Salvar Skills

Skills podem ser salvas em dois locais, com prioridade diferente:

### Global: `~/.claude/skills/`

Skills globais ficam disponíveis em **todos os projetos** do usuário. Ideal para:
- Workflows pessoais (seu estilo de commit, seu padrão de PR)
- Skills de produtividade genéricas
- Skills que não são específicas de um projeto

```
~/.claude/
  skills/
    conventional-commit.md
    pr-review.md
    daily-standup.md
```

### Local: `.claude/skills/`

Skills locais ficam disponíveis apenas no projeto atual. Ideal para:
- Workflows específicos do projeto
- Skills com conhecimento do domínio do produto
- Skills que referenciam paths ou convenções específicas do repo

```
.claude/
  skills/
    deploy-check.md
    api-endpoint-review.md
    database-migration.md
```

### Prioridade

Quando há conflito de nome entre uma skill global e uma local, a **skill local tem prioridade**. Isso permite que projetos sobrescrevam comportamentos globais sem afetar outros projetos.

> [!info] A estrutura de diretórios `skills/` dentro de `.claude/` é a convenção padrão. O Claude Code descobre skills automaticamente nestes paths — não é necessário registrá-las em nenhum arquivo de configuração.

---

## Estrutura Completa de uma Skill

Uma skill bem estruturada tem as seguintes seções:

```markdown
---
name: deploy-check
description: Executa checklist completo antes de qualquer deploy para produção, verificando testes, migrations pendentes, variáveis de ambiente e aprovações necessárias
version: 2.1
tags: [deploy, production, checklist]
---

# Deploy Check

## Objetivo
Garantir que nenhum deploy para produção aconteça sem verificação completa de pré-condições.

## Quando Usar
Antes de qualquer merge para main que resulte em deploy automático, ou antes de deploy manual via CI/CD.

## Critérios de Entrada
- [ ] Todas as mudanças estão commitadas e pushed
- [ ] PR está aberto e code review foi solicitado

## Passos

### 1. Verificar Suite de Testes
Execute e confirme que todos os testes passam:
```bash
npm run test:all
npm run test:e2e
```
Se qualquer teste falhar, PARE. Não continue.

### 2. Verificar Migrations Pendentes
```bash
npx prisma migrate status
```
Se houver migrations pendentes, liste-as e pergunte ao usuário se devem ser executadas agora.

### 3. Verificar Variáveis de Ambiente
Compare `.env.example` com as variáveis configuradas no ambiente de produção.
Liste qualquer variável presente em `.env.example` mas ausente no ambiente de produção.

### 4. Verificar Dependências
```bash
npm audit --audit-level=high
```
Vulnerabilidades HIGH ou CRITICAL bloqueiam o deploy.

### 5. Verificar Bundle Size
```bash
npm run build:analyze
```
Se o bundle cresceu mais de 20% em relação ao último deploy, gere um relatório.

## Critérios de Saída
- [ ] Todos os testes passando
- [ ] Nenhuma migration pendente bloqueante
- [ ] Todas as env vars presentes
- [ ] Nenhuma vulnerabilidade crítica
- [ ] Bundle size dentro do limite

## Relatório Final
Ao concluir, gere um relatório no formato:

```
DEPLOY CHECK — [data]
Status: APROVADO / BLOQUEADO
Testes: ✓ / ✗
Migrations: ✓ / ✗
Env Vars: ✓ / ✗
Segurança: ✓ / ✗
Bundle: ✓ / ✗

[Observações]
```

## Nunca Faça
- Nunca marque o deploy como aprovado se qualquer item estiver ✗
- Nunca ignore falhas de teste "temporárias"
- Nunca pule a verificação de variáveis de ambiente
```

---

## Catálogo de Skills por Categoria

### Git & Workflow

**conventional-commit**
Gera mensagens de commit seguindo Conventional Commits. Analisa o diff, identifica o tipo (feat/fix/chore/docs/refactor), sugere escopo baseado nos arquivos modificados, detecta breaking changes.

**pr-review**
Revisão estruturada de pull requests. Verifica lógica, segurança, performance, testes, documentação e convenções do projeto.

**changelog-generator**
Gera CHANGELOG.md a partir do histórico de commits convencionais entre duas tags.

**branch-cleanup**
Lista branches merged e propõe limpeza segura, preservando branches com PRs abertos.

### Code Quality

**api-endpoint-review**
Revisão específica para endpoints de API REST/GraphQL. Verifica autenticação, autorização, validação de input, rate limiting, documentação OpenAPI.

**security-scan**
Analisa código em busca de vulnerabilidades comuns: SQL injection, XSS, secrets hardcoded, dependências vulneráveis.

**performance-review**
Analisa código com foco em performance: N+1 queries, missing indexes, caching opportunities, bundle size.

### Documentação

**docstring-writer**
Escreve docstrings no formato do projeto (JSDoc, Python docstrings, Go doc comments) para funções sem documentação.

**readme-update**
Atualiza o README do projeto com base nas mudanças recentes, mantendo seções existentes e adicionando novas funcionalidades.

### DevOps

**deploy-check**
Checklist pré-deploy para produção (ver exemplo completo acima).

**incident-response**
Guia estruturado para resposta a incidentes: identificação, comunicação, mitigação, postmortem.

**rollback-procedure**
Procedimento de rollback seguro com verificações de estado antes e depois.

---

## Exemplos de Skills Completas

### Skill: conventional-commit

```markdown
---
name: conventional-commit
description: Analisa o git diff atual e gera uma mensagem de commit seguindo o padrão Conventional Commits (feat, fix, chore, docs, refactor, test, style, perf), com escopo baseado nos arquivos modificados e detecção automática de breaking changes
version: 1.2
tags: [git, commits]
---

# Conventional Commit Generator

## Processo

### 1. Analisar o Diff
Execute `git diff --staged` e `git status` para entender todas as mudanças.

### 2. Identificar o Tipo
Mapeie as mudanças para o tipo correto:
- `feat`: nova funcionalidade visível ao usuário
- `fix`: correção de bug
- `docs`: apenas documentação
- `style`: formatação, sem mudança de lógica
- `refactor`: reestruturação sem mudar comportamento
- `test`: adição ou correção de testes
- `chore`: build, dependências, configuração
- `perf`: melhoria de performance

### 3. Identificar o Escopo
O escopo deve refletir o módulo/área afetada. Use os nomes dos diretórios principais como guia. Exemplos:
- Arquivos em `src/auth/` → escopo `auth`
- Arquivos em `src/api/users/` → escopo `users`
- Arquivos em `components/Button/` → escopo `Button`

### 4. Escrever a Mensagem
Formato: `tipo(escopo): descrição em imperativo`

Regras:
- Descrição em português, imperativo ("adiciona" não "adicionado")
- Máximo 72 caracteres na primeira linha
- Se houver breaking change: adicione `!` após o escopo e `BREAKING CHANGE:` no corpo
- Body opcional para contexto adicional

### 5. Apresentar Opções
Apresente 2-3 variações da mensagem para o usuário escolher.

## Exemplos de Saída

```
feat(auth): adiciona autenticação via OAuth2 com Google

Implementa fluxo completo de OAuth2 incluindo refresh token e
revogação. Usuários existentes não são afetados.
```

```
fix(api): corrige race condition no endpoint de pagamento
```

```
feat(auth)!: remove autenticação por senha em favor de OAuth2

BREAKING CHANGE: O endpoint /auth/login com password não é mais suportado.
Todos os clientes devem migrar para /auth/oauth2/google.
```
```

---

### Skill: pr-review

```markdown
---
name: pr-review
description: Realiza revisão técnica completa de pull request analisando lógica, segurança, performance, cobertura de testes, documentação e aderência às convenções do projeto
version: 1.0
tags: [git, code-review, quality]
---

# PR Review

## Dimensões de Análise

### 1. Correctude Lógica
- A implementação resolve o problema descrito no PR?
- Há edge cases não tratados?
- Os error states são tratados corretamente?
- Há condições de race condition?

### 2. Segurança
- Input validation em todos os pontos de entrada?
- Autenticação e autorização corretas?
- Dados sensíveis não expostos em logs?
- Queries parameterizadas (sem SQL injection)?

### 3. Performance
- Queries N+1?
- Loops desnecessários?
- Caching onde aplicável?
- Impacto no bundle size (frontend)?

### 4. Testes
- Novos features têm testes unitários?
- Edge cases cobertos?
- Testes de integração quando necessário?
- Mocks excessivos que escondem problemas reais?

### 5. Documentação
- Funções públicas documentadas?
- README atualizado se necessário?
- Changelog atualizado?
- Comentários em código complexo?

### 6. Convenções
- Naming conventions do projeto?
- Estrutura de diretórios consistente?
- Padrões de commit respeitados?

## Formato de Saída

Para cada issue encontrada, use o formato:

```
[SEVERITY] Arquivo:linha — Descrição
SEVERITY: BLOCKER / MAJOR / MINOR / SUGGESTION
```

Ao final, um sumário:
```
RESULTADO: APROVADO / APROVADO COM RESSALVAS / NECESSITA REVISÃO
Blockers: N
Majors: N  
Minors: N
Suggestions: N
```
```

---

## Dicas para Skills Eficazes

> [!tip] Seja ultra-específico na description. O matching semântico usa a description para decidir quando invocar a skill. "Gera commits" é fraco. "Analisa o git diff staged e gera mensagem de commit no padrão Conventional Commits com tipo, escopo e breaking change detection" é forte.

> [!tip] Mantenha skills curtas e focadas. Uma skill que tenta fazer tudo faz tudo mal. Prefira várias skills pequenas com responsabilidades claras a uma skill monolítica.

> [!warning] Teste antes de publicar. Invoque a skill manualmente, observe o comportamento, ajuste o wording dos passos. Skills com instruções ambíguas produzem resultados inconsistentes.

> [!tip] Use critérios de entrada e saída explícitos para skills rígidas. O Claude precisa saber quando parar, quando pedir confirmação e quando reportar falha.

> [!info] Versione suas skills. À medida que o projeto evolui, as skills precisam evoluir também. O campo `version` no frontmatter ajuda a rastrear mudanças.

### Anti-patterns a Evitar

| Anti-pattern | Problema | Solução |
|--------------|----------|---------|
| Description genérica | Nunca invocada automaticamente | Describe o contexto exato de uso |
| Skill monolítica | Difícil de manter e adaptar | Decomponha em skills menores |
| Passos ambíguos | Comportamento inconsistente | Use linguagem imperativa clara |
| Sem critérios de parada | Claude não sabe quando terminar | Adicione critérios de saída |
| Sem exemplos de saída | Output imprevisível | Inclua exemplos no formato esperado |

---

## Compartilhamento de Skills em Equipe

Skills no diretório `.claude/skills/` (local ao projeto) são versionadas junto com o código e compartilhadas com toda a equipe via Git.

Workflow recomendado:

```bash
# Criar nova skill
touch .claude/skills/minha-skill.md
# Editar a skill
# Testar manualmente
# Commitar
git add .claude/skills/minha-skill.md
git commit -m "feat(skills): adiciona skill para [propósito]"
```

Para skills pessoais que não devem ser compartilhadas:

```bash
# Adicionar ao .gitignore local (não o .gitignore do projeto)
echo ".claude/skills/personal-*.md" >> .git/info/exclude
```

---

## Skills vs Outros Mecanismos

| Mecanismo | Propósito | Persistência | Escopo |
|-----------|-----------|--------------|--------|
| Skill | Comportamento reutilizável com processo | Permanente (arquivo) | Global ou por projeto |
| CLAUDE.md | Contexto e instruções gerais | Permanente (arquivo) | Por projeto |
| Slash command | Ação pontual com argumentos | Permanente (arquivo) | Por projeto |
| Hook | Ação automática em eventos | Configuração | Por projeto ou global |
| Memory | Fatos e preferências | Por sessão ou persistente | Por projeto |

---

## Debugging de Skills

Quando uma skill não está sendo invocada como esperado:

**1. Verificar se o arquivo está no path correto**
```bash
ls ~/.claude/skills/
ls .claude/skills/
```

**2. Verificar o frontmatter**
```bash
head -20 .claude/skills/minha-skill.md
```
O YAML deve ser válido — erros de sintaxe impedem o carregamento.

**3. Testar a description**
Pergunte ao Claude: "Quais skills você tem disponíveis?" e veja se a sua skill aparece.

**4. Invocar explicitamente**
```
Use the [nome-da-skill] skill
```
Se funcionar explicitamente mas não automaticamente, o problema é na description.

---

## Related

- [[hooks-system]] — Automatizar execução de skills em eventos do Claude Code
- [[slash-commands]] — Diferença entre slash commands e skills
- [[agent-teams]] — Skills como base para comportamentos de agentes especializados
- [[permissions-and-safety]] — Permissões necessárias para skills que executam comandos
- [[00-moc/claude-code-moc]] — Índice geral do Claude Code
