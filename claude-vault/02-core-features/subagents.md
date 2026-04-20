---
tags: [claude-code, core-features, subagents, agents]
status: active
level: intermediate
updated: 2026-04-19
created: 2026-04-19
---

# Subagentes — Agent Tool no Claude Code

## O que é o Agent Tool

O Agent Tool é o mecanismo pelo qual o Claude Code pode criar e despachar subagentes — instâncias separadas do Claude que executam tarefas em paralelo ou em sequência, com contexto isolado e acesso a ferramentas configuráveis.

A distinção fundamental: o agente principal (orquestrador) é quem conversa com você. Subagentes são trabalhadores silenciosos que o orquestrador cria para delegar trabalho. Cada subagente tem seu próprio contexto, seu próprio ciclo de vida, e reporta seus resultados de volta ao orquestrador via texto.

O conceito de "fresh context" é central: quando um subagente é criado, ele começa com um contexto limpo — não herda o histórico de conversa do agente principal, não conhece as decisões anteriores, não sabe o que outros subagentes estão fazendo. Isso é intencional: cada subagente recebe um prompt self-contained com todas as informações necessárias.

---

## Parâmetros do Agent Tool

```typescript
// Schema simplificado da chamada ao Agent tool
{
  "description": "Descrição curta do que este agente vai fazer (aparece nos logs)",
  "prompt": "Prompt completo e self-contained com todas as instruções",
  "subagent_type": "general" | "claude-sonnet-4-6" | "claude-opus-4" | "claude-haiku-4",
  "tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep"],  // subset de ferramentas
  "isolation": "none" | "worktree",
  "run_in_background": false | true
}
```

### Parâmetro `subagent_type`

Define qual modelo será usado para o subagente:

| Valor | Modelo | Uso Ideal |
|-------|--------|-----------|
| `general` | Mesmo modelo do orquestrador | Padrão — a maioria dos casos |
| `claude-sonnet-4-6` | Claude Sonnet 4.6 | Tarefas de implementação, velocidade + qualidade |
| `claude-opus-4` | Claude Opus 4 | Raciocínio complexo, decisões críticas |
| `claude-haiku-4` | Claude Haiku 4 | Tarefas simples, alta velocidade, menor custo |

> [!tip] Use `claude-haiku-4` para tarefas mecânicas (renomear arquivos, gerar boilerplate, formatar dados). Reserve `claude-opus-4` para análises complexas onde raciocínio profundo importa. Na maioria dos casos, `general` ou `claude-sonnet-4-6` são ideais.

### Parâmetro `isolation`

| Valor | Comportamento |
|-------|---------------|
| `none` | Subagente trabalha no mesmo diretório de trabalho. Mudanças em arquivos afetam o repo diretamente. |
| `worktree` | Subagente recebe um git worktree isolado — branch separada, diretório separado. Mudanças não afetam o repo principal até merge explícito. |

### Parâmetro `run_in_background`

| Valor | Comportamento |
|-------|---------------|
| `false` (padrão) | Agente principal aguarda o subagente terminar (síncrono). |
| `true` | Agente principal continua executando enquanto o subagente roda em paralelo (assíncrono). |

---

## Foreground vs Background

### Subagente em Foreground (Síncrono)

O orquestrador bloqueia até o subagente terminar e recebe o resultado diretamente:

```
Orquestrador → cria Subagente A
Orquestrador → [AGUARDA]
               Subagente A executa...
               Subagente A retorna resultado
Orquestrador ← recebe resultado
Orquestrador → usa resultado para próximo passo
```

Uso ideal: quando o resultado do subagente é necessário para continuar. Exemplos:
- Research agent que deve encontrar informação antes de implementar
- Review agent que valida antes de commitar
- Análise de dependências antes de instalar

### Subagente em Background (Assíncrono/Paralelo)

O orquestrador despacha múltiplos subagentes e continua, esperando os resultados ao final:

```
Orquestrador → cria Subagente A (background)
Orquestrador → cria Subagente B (background)
Orquestrador → cria Subagente C (background)
               [A, B e C executam em paralelo]
Orquestrador → aguarda todos completarem
Orquestrador ← recebe resultados de A, B, C
Orquestrador → agrega e consolida resultados
```

Uso ideal: tarefas independentes que não têm dependências entre si. Exemplos:
- Refatorar 5 módulos diferentes em paralelo
- Escrever testes para 3 serviços diferentes simultaneamente
- Gerar documentação de múltiplos endpoints em paralelo

---

## Como Comunicar Resultados de Volta

Subagentes não têm uma API de retorno estruturada — comunicam via **texto**. O orquestrador lê o output do subagente e processa.

### Padrão 1: Relatório Textual

```
# Resultado da Análise de Segurança

## Status: APROVADO

## Vulnerabilidades Encontradas
- Nenhuma vulnerabilidade crítica ou alta
- 2 vulnerabilidades médias (detalhadas abaixo)

## Detalhes
### [MEDIUM] src/auth/jwt.ts:45
Algoritmo HS256 com secret de apenas 32 bytes. Recomendado: 64+ bytes ou RS256.

### [MEDIUM] src/api/users.ts:123
Rate limiting não implementado no endpoint de login.

## Recomendações
1. Aumentar tamanho do secret JWT para mínimo 64 bytes
2. Implementar rate limiting no endpoint /auth/login (máx 5 req/min por IP)
```

### Padrão 2: JSON Estruturado

Para subagentes que precisam retornar dados que o orquestrador vai processar programaticamente:

```
RESULTADO_JSON:
{
  "status": "success",
  "arquivos_criados": ["src/auth.ts", "src/auth.test.ts"],
  "arquivos_modificados": ["src/index.ts"],
  "testes_passando": 12,
  "testes_falhando": 0,
  "tempo_execucao": "2m 34s"
}
```

### Padrão 3: Arquivo no Filesystem

O subagente escreve seus resultados em um arquivo, e o orquestrador lê esse arquivo:

```
# No prompt do subagente:
"Ao finalizar, salve um relatório completo em /workspace/.claude/reports/security-report.md"

# O orquestrador depois lê:
# Read("/workspace/.claude/reports/security-report.md")
```

---

## Patterns de Subagentes

### Research Agent

Coleta informações antes da implementação:

```
Prompt do Research Agent:
"Você é um agente de pesquisa. Sua tarefa é analisar o codebase atual e responder:

1. Qual é a estrutura atual do módulo de autenticação? (liste os arquivos principais)
2. Quais são as dependências de autenticação no package.json?
3. Há testes de autenticação existentes? Onde estão?
4. Qual é o padrão de error handling usado no projeto?

Examine os arquivos relevantes e forneça um relatório detalhado.
Não faça nenhuma mudança — apenas pesquise e reporte."
```

### Implementation Agent

Implementa uma feature isolada:

```
Prompt do Implementation Agent:
"Implemente um sistema de refresh token para o módulo de autenticação.

Contexto do projeto:
- Framework: Express.js com TypeScript
- Banco de dados: PostgreSQL via Prisma
- Auth atual: JWT com access token de 1h em src/auth/jwt.ts
- Padrão de error handling: throw AppError com código e mensagem

O que implementar:
1. Adicionar campo refresh_token na tabela User (migration Prisma)
2. Gerar refresh token no login (64 bytes, válido por 30 dias)
3. Endpoint POST /auth/refresh que valida refresh token e retorna novo access token
4. Revogar refresh token no logout
5. Testes unitários para toda a nova lógica

Arquivos a modificar/criar:
- prisma/schema.prisma (adicionar campo)
- src/auth/jwt.ts (gerar refresh token)
- src/auth/routes.ts (novo endpoint)
- src/auth/jwt.test.ts (testes)

Ao finalizar, retorne um relatório com os arquivos criados/modificados e o resultado dos testes."
```

### Review Agent

Revisa código implementado:

```
Prompt do Review Agent:
"Você é um revisor de código sênior especializado em segurança.

Revise as seguintes mudanças para implementação de refresh tokens:
[Cole aqui o diff ou lista de arquivos a revisar]

Analise especificamente:
1. Segurança da implementação do refresh token
2. Possíveis race conditions no refresh
3. Tratamento correto de tokens expirados
4. Cobertura de testes

Formato de saída:
- Liste cada issue com: [SEVERIDADE] localização — descrição
- Termine com: APROVADO / APROVADO COM RESSALVAS / NECESSITA REVISÃO"
```

### Coordinator Pattern

O orquestrador coordena múltiplos agentes em sequência:

```
1. Orquestrador → Research Agent (foreground)
   └─ Research Agent retorna: estrutura do projeto, dependências, padrões

2. Orquestrador → Implementation Agent (foreground, usa resultado do Research)
   └─ Implementation Agent retorna: arquivos criados, testes rodados

3. Orquestrador → Review Agent (foreground, usa diff do Implementation)
   └─ Review Agent retorna: aprovação com observações

4. Orquestrador consolida → apresenta resultado ao usuário
```

---

## Custo de Subagentes

Cada subagente consome tokens de forma independente. O custo total de uma sessão com subagentes é:

```
custo_total = custo_orquestrador + Σ custo_subagente_i
```

Para cada subagente:
- O prompt self-contained é enviado como contexto inicial (= tokens de input)
- A execução gera output (= tokens de output)
- Ferramentas chamadas pelo subagente geram seus próprios tokens

> [!warning] Subagentes com contextos grandes multiplicam o custo. Um orquestrador que despacha 5 subagentes com prompts de 10k tokens cada resulta em 50k tokens apenas de input antes de qualquer execução.

### Estratégias para Controle de Custo

| Estratégia | Como Implementar |
|------------|-----------------|
| Prompts concisos | Não copie todo o código no prompt — referencie paths de arquivos |
| Modelo certo para a tarefa | Use Haiku para tarefas simples, não Opus |
| Subagente apenas quando necessário | Tasks simples não precisam de subagente |
| Limitar ferramentas disponíveis | Não dê acesso a todas as ferramentas se não precisar |
| Background apenas quando há paralelismo real | Não use background se as tasks têm dependências |

---

## Prompts Self-Contained: A Regra Mais Importante

Subagentes não herdam contexto. O prompt deve conter TUDO que o subagente precisa saber.

### Prompt Ruim (Sem Contexto)

```
"Implemente a autenticação OAuth2 como discutimos."
```

O subagente não sabe o que foi discutido, qual framework usar, qual provider OAuth2, nada.

### Prompt Bom (Self-Contained)

```
"Implemente autenticação OAuth2 com Google para uma aplicação Express.js/TypeScript.

CONTEXTO DO PROJETO:
- Framework: Express.js 4.18 com TypeScript 5
- Banco de dados: PostgreSQL via Prisma 5
- Arquivo principal: src/index.ts
- Auth existente: JWT em src/auth/jwt.ts (access token HS256, 1h)
- Padrão de errors: throw new AppError(message, statusCode) de src/utils/errors.ts
- ENV vars disponíveis: DATABASE_URL, JWT_SECRET, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

O QUE IMPLEMENTAR:
1. Instalar passport e passport-google-oauth20
2. Configurar estratégia OAuth2 em src/auth/oauth.ts
3. Endpoints: GET /auth/google, GET /auth/google/callback
4. Criar ou atualizar User no banco com dados do Google
5. Retornar JWT ao final do flow OAuth2
6. Testes em src/auth/oauth.test.ts

CONVENÇÕES:
- Funções exportadas nomeadas (não default exports)
- Async/await, nunca callbacks
- Validação de env vars no início dos módulos

ENTREGA:
Liste os arquivos criados/modificados e execute npm test para confirmar que tudo passa."
```

---

## Quando NÃO Usar Subagentes

Subagentes têm overhead real — setup de contexto, latência, custo. Não use quando:

| Situação | Por quê Evitar | Alternativa |
|----------|---------------|-------------|
| Tarefa simples de 1-2 arquivos | Overhead maior que o benefício | Fazer diretamente |
| Tasks com muitas dependências sequenciais | Subagentes paralelos são ineficientes | Loop sequencial simples |
| Budget de tokens limitado | Cada subagente multiplica o custo | Fazer em sequência no mesmo contexto |
| Tarefas que precisam de contexto da conversa | Subagentes não herdam contexto | Manter no agente principal |
| Debugging interativo | Subagentes não comunicam em tempo real | Debugar no agente principal |
| Quando você não sabe o que o agente vai fazer | Subagentes obscurecem o processo | Fazer transparentemente |

---

## Gotchas e Armadilhas Comuns

> [!warning] Subagentes não herdam configurações de permissão do agente principal. Defina explicitamente quais ferramentas o subagente pode usar via parâmetro `tools`.

> [!warning] Resultados de subagentes background chegam em ordem não determinística. Não assuma que o primeiro subagente despacho é o primeiro a terminar.

> [!warning] Subagentes com `isolation: "worktree"` trabalham em branches separadas. As mudanças precisam de merge explícito — não aparecem automaticamente no branch principal.

> [!info] Subagentes com `isolation: "none"` compartilham o filesystem. Dois subagentes modificando o mesmo arquivo em paralelo criarão conflitos. Planeje tasks para não conflitar.

> [!tip] Use `description` descritivo no Agent tool. Aparece nos logs e torna o debugging muito mais fácil quando você tem múltiplos subagentes rodando.

---

## Exemplo Completo: Deploy Pipeline com Subagentes

```
Orquestrador recebe: "Faça deploy da feature de refresh tokens para staging"

Passo 1 — Research Agent (foreground):
  Prompt: "Examine o pipeline de CI/CD atual, identifique:
           1. Comando de deploy para staging
           2. Checklist de pré-deploy (testes, linting)
           3. Como verificar que o deploy foi bem-sucedido
           Reporta em formato estruturado."
  → Resultado: detalhes do pipeline

Passo 2 — Parallel Quality Agents (background):
  Agent A - Tests: "Execute npm run test:all e reporte o resultado"
  Agent B - Lint: "Execute npm run lint e reporte o resultado"
  Agent C - Build: "Execute npm run build e reporte o resultado"
  → Aguarda todos terminarem

Passo 3 — Se todos aprovaram:
  Deploy Agent (foreground):
  Prompt: "Execute o deploy para staging usando o comando [do Passo 1].
           Monitore por 60s e confirme que o health check responde 200."
  → Resultado: status do deploy

Passo 4 — Orquestrador reporta ao usuário com consolidação dos resultados
```

---

## Related

- [[agent-teams]] — Times de agentes especializados como extensão do padrão de subagentes
- [[worktrees]] — Isolamento de subagentes via git worktrees
- [[skills-system]] — Skills que definem comportamentos reutilizáveis para subagentes
- [[permissions-and-safety]] — Permissões por subagente com allowedTools
- [[00-moc/claude-code-moc]] — Índice geral do Claude Code
