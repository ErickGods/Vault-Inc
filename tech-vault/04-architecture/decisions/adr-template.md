---
tags: [skill, architecture, adr]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [ADR, Architecture Decision Record]
---

# Architecture Decision Records (ADR)

## Overview

Architecture Decision Records (ADRs) são documentos curtos que capturam decisões arquiteturais significativas junto com seu contexto e consequências. Criado por Michael Nygard (2011), o formato resolve o problema da "archaeology code": novo membro do time encontra uma escolha estranha e não sabe **por quê** ela foi feita.

> [!important] O Que Registrar
> Uma decisão merece um ADR quando: (1) é difícil de reverter, (2) afeta múltiplos times ou serviços, (3) envolve trade-offs não óbvios, ou (4) futuras equipes precisarão entender o raciocínio. Decisões triviais (qual lib de logging usar internamente) não precisam de ADR.

ADRs capturam o **raciocínio no momento da decisão** — com o contexto e as restrições daquele momento. Uma decisão pode estar errada hoje mas ter sido correta dado o que se sabia na época.

---

## Core Concepts

### Formato MADR vs Nygard

**Nygard (formato original, minimalista):**

```markdown
# ADR-001: Use PostgreSQL as Primary Database

## Status
Accepted

## Context
We need a relational database for transactional data. The team has strong
PostgreSQL expertise. Budget is constrained — managed services preferred.

## Decision
We will use PostgreSQL hosted on AWS RDS with Multi-AZ for high availability.

## Consequences
- **Good**: ACID transactions, JSONB support for semi-structured data, team expertise
- **Bad**: Vertical scaling has limits; sharding requires significant effort
- **Neutral**: AWS vendor lock-in for managed service
```

**MADR (Markdown Any Decision Records — formato estendido):**

```markdown
# ADR-002: Adopt Kafka for Event Streaming

## Status
Accepted

## Context and Problem Statement
We need async communication between microservices. Currently using direct
HTTP calls which creates tight coupling and cascade failures.

## Decision Drivers
- Must handle 50k events/sec at peak (Black Friday)
- Team needs operational experience with the chosen tool
- Replayability of events is required for audit and debugging

## Considered Options
- Apache Kafka
- RabbitMQ
- AWS SQS/SNS
- NATS JetStream

## Decision Outcome
Chosen option: **Apache Kafka**, because it satisfies throughput requirements
and provides event log replayability that RabbitMQ and SQS cannot.

### Positive Consequences
- Log-based storage enables replay for new consumers and debugging
- Consumer groups allow horizontal scaling per consumer independently
- Retained messages allow catching up after downtime

### Negative Consequences
- Kafka cluster operational complexity (ZooKeeper/KRaft mode)
- Higher learning curve vs RabbitMQ
- Overkill if throughput stays below 5k/sec

## Pros and Cons of Options

### Apache Kafka
- Good: Throughput 1M+ msg/sec, event log, replay
- Bad: Complex operations, no native dead-letter support

### RabbitMQ
- Good: Simple ops, native DLQ, AMQP protocol
- Bad: No log-based storage, throughput ceiling ~100k/sec

### AWS SQS/SNS
- Good: Fully managed, no ops, native AWS integration
- Bad: No replay, 256KB message limit, vendor lock-in
```

### Status Lifecycle

```
proposed ──► accepted ──► deprecated ──► superseded
              │                              ▲
              └──► rejected                 │
                                     (novo ADR referencia o antigo)
```

- **Proposed**: decisão em discussão, ainda não adotada
- **Accepted**: decisão aprovada e em vigor
- **Deprecated**: decisão ainda em vigor mas sendo descontinuada
- **Superseded by ADR-NNN**: substituída por nova decisão (com link)
- **Rejected**: considerada e descartada (manter para memória — não delete!)

> [!tip] Nunca Delete um ADR
> ADRs rejeitados são valiosos: evitam que a mesma ideia ruim seja proposta novamente. Marque como `rejected` com o motivo da rejeição.

### Convenções de Numeração

```
ADR-0001-use-postgresql.md           # Zero-padded para sort correto
ADR-0002-adopt-kafka-streaming.md
ADR-0003-migrate-to-kubernetes.md    # Sempre incrementar, nunca reutilizar
```

Prefixos por área (para repositórios com múltiplos domínios):
```
ADR-INFRA-001-kubernetes-cluster.md
ADR-AUTH-001-jwt-vs-sessions.md
ADR-DATA-001-database-selection.md
```

---

## Patterns

### Lightweight ADR para Decisões Menores

Nem toda decisão justifica o formato completo. Para decisões menores (dentro de um time, reversíveis em semanas):

```markdown
# ADR-0042: Use Pydantic v2 for Data Validation

**Status**: Accepted | **Date**: 2026-04-05 | **Author**: @team-backend

**Decision**: Migrate from Pydantic v1 to v2 across all FastAPI services.

**Reason**: 5–50x performance improvement in validation, native support for
Python dataclasses, better TypeScript-like type annotations.

**Trade-offs**: Breaking API changes require migration script. Estimated 2 days.

**Review date**: 2026-07-01 (revisit if migration issues arise)
```

### ADR de Seleção de Tecnologia (Template Executivo)

```markdown
# ADR-0015: Message Broker Selection

## Status
Accepted — 2026-03-15

## Context
Serviços de Order, Inventory e Notification precisam se comunicar
assincronamente. Picos de 30k mensagens/min durante promoções.

## Alternatives Evaluated

| Critério              | Kafka     | RabbitMQ  | SQS/SNS   |
|-----------------------|-----------|-----------|-----------|
| Throughput            | ★★★★★     | ★★★★☆     | ★★★☆☆    |
| Operacional           | ★★☆☆☆     | ★★★★☆     | ★★★★★    |
| Replay de eventos     | ★★★★★     | ★☆☆☆☆     | ★☆☆☆☆    |
| Custo mensal est.     | $800      | $400      | $200      |
| Expertise do time     | Baixa     | Média     | Alta      |

## Decision
**RabbitMQ** no curto prazo (já há expertise, ops simples, custo menor).
Migração para Kafka avaliada em 6 meses se volume crescer acima de 50k/min.

## Consequences
- Mensagens sem replay — compensar com retry logic e DLQ robusta
- Familiaridade do time reduz curva de adoção
- Revisão obrigatória em Q3 2026 se throughput ultrapassar threshold
```

### ADR de Estratégia de Autenticação

```markdown
# ADR-0008: JWT Stateless vs Session-Based Auth

## Status
Accepted — 2026-01-10 | Revisit: 2026-07-10

## Context
Sistema com 3 microservices que precisam autenticar requests. Arquitetura
distribuída sem estado compartilhado centralizado.

## Decision
JWT stateless com access token (15min) + refresh token (7 dias) em
HttpOnly cookie. Sem server-side session store.

## Rationale
- Microservices podem validar JWT sem chamar auth service (performance)
- Sem ponto único de falha (Redis session store seria SPOF)
- Revogação de tokens requer blacklist — trade-off aceito com TTL curto

## Consequences
- ✅ Horizontal scaling sem sticky sessions
- ✅ Validação offline (sem rede) dentro de cada serviço
- ⚠️ Revogação imediata impossível sem blacklist — mitigado por TTL de 15min
- ⚠️ Payload do JWT público (Base64) — nunca incluir dados sensíveis

## Related ADRs
- Supersedes: ADR-0003 (cookie session approach — deprecated)
- Related: ADR-0009 (API Gateway auth middleware)
```

---

## Gotchas

> [!danger] ADR como Justificativa Retroativa
> ADRs escritos **depois** da implementação para justificar decisões já tomadas são perigosos. O valor do ADR está em documentar as alternativas genuinamente consideradas e as restrições do momento. Se a decisão já foi tomada, escreva o ADR com honestidade — incluindo as alternativas que não foram exploradas.

> [!warning] ADRs Abandonados
> Um ADR em status `proposed` há 3 meses é pior que não ter ADR: cria ilusão de que a decisão está sendo considerada. Defina um prazo de decisão explícito no documento ou marque como `rejected` se a discussão esfriou.

> [!bug] Detalhes de Implementação em ADRs
> ADR captura **o quê** e **por quê**, não **como**. Detalhes de implementação mudam; o raciocínio da decisão geralmente não. Coloque detalhes técnicos no README do serviço ou wiki, não no ADR.

---

## Snippets

### Quando Escrever um ADR — Checklist

```markdown
Escreva um ADR quando a decisão:
- [ ] Afeta a estrutura de um ou mais serviços/sistemas
- [ ] Envolve escolha entre 2+ alternativas com trade-offs não triviais
- [ ] Será difícil de reverter (banco de dados, protocolo de comunicação, auth)
- [ ] Impacta mais de um time
- [ ] Tem implicações de custo, segurança ou compliance
- [ ] Futura equipe vai se perguntar "por que fizeram assim?"

Não precisa de ADR:
- Escolhas de libraries internas sem impacto cross-service
- Decisões de style/formatting (use um linter, não um ADR)
- Refactorings que não mudam comportamento externo
```

### Estrutura de Diretório para ADRs

```
docs/
└── architecture/
    ├── decisions/
    │   ├── ADR-0001-use-postgresql.md
    │   ├── ADR-0002-adopt-kafka.md
    │   └── ADR-0003-jwt-auth.md
    └── README.md   ← índice de ADRs com status atual
```

### Tooling: log4brains

```bash
# Instalar log4brains para visualização web dos ADRs
npm install -g log4brains

# Inicializar no repositório
log4brains init

# Criar novo ADR interativamente
log4brains adr new

# Preview web local
log4brains preview
# → http://localhost:4000 com histórico navegável
```

### Tooling: adr-tools (CLI)

```bash
# macOS
brew install adr-tools

# Inicializar diretório de ADRs
adr init docs/architecture/decisions

# Criar novo ADR
adr new "Use Redis for Rate Limiting"
# → cria docs/architecture/decisions/0042-use-redis-for-rate-limiting.md

# Superseder um ADR anterior
adr new -s 0015 "Migrate from RabbitMQ to Kafka"
# → cria novo ADR e atualiza ADR-0015 como superseded
```

---

## References

- **Documenting Architecture Decisions** — Michael Nygard, 2011 — [cognitect.com/blog](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- **MADR** — Markdown Any Decision Records — [adr.github.io/madr](https://adr.github.io/madr/)
- **log4brains** — ferramenta de visualização — [github.com/thomvaill/log4brains](https://github.com/thomvaill/log4brains)
- **adr-tools** — CLI para gerenciar ADRs — [github.com/npryce/adr-tools](https://github.com/npryce/adr-tools)
- [[clean-architecture]] — decisões de arquitetura interna de serviços
- [[microservices]] — decisões de decomposição e comunicação
- [[event-driven]] — decisões de mensageria e consistência

---

## Related

- [[clean-architecture]] — estrutura interna onde ADRs documentam escolhas de camadas
- [[microservices]] — ADRs de decomposição, comunicação e service mesh
- [[event-driven]] — ADRs de message broker, event sourcing vs traditional state
- [[deployment-strategies]] — ADRs de blue/green, canary, feature flags
- [[observability]] — ADRs de stack de monitoring, tracing e alertas
