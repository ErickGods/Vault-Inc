---
tags: [moc, architecture]
status: active
level: advanced
updated: 2026-04-05
aliases: [Architecture MOC]
created: 2026-04-05
---

# 🏗️ Architecture MOC

## Visão Geral

Este MOC cobre o domínio de arquitetura de software: padrões arquiteturais, decisões de design, serviços cloud e sistemas de mensageria. Arquitetura não é sobre escolher o framework mais moderno — é sobre tomar decisões que equilibram simplicidade, escalabilidade, manutenibilidade e custo ao longo do tempo.

O vault documenta padrões que foram validados em produção, não apenas teoria. Cada arquivo inclui trade-offs reais, quando usar e quando evitar, e exemplos de implementação.

> [!info] Cobertura
> Esta seção (`04-architecture/`) contém 11 arquivos cobrindo padrões clássicos, registros de decisões arquiteturais (ADRs), cloud services e sistemas de mensageria.

---

## 📊 Dashboard

```dataview
TABLE status, level, updated
FROM "tech-vault/04-architecture"
SORT updated DESC
```

---

## 🗺️ Skills Map

### Architectural Patterns

| Arquivo | Padrão | Status |
|---------|--------|--------|
| [[microservices]] | Arquitetura de microserviços | ✅ active |
| [[event-driven]] | Event-driven architecture (EDA) | ✅ active |
| [[clean-architecture]] | Clean Architecture e suas variantes | ✅ active |

### Architecture Decision Records

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[adr-template]] | Template e processo para ADRs | ✅ active |

### Cloud Services

| Arquivo | Serviço | Status |
|---------|---------|--------|
| [[cloudinary]] | Cloudinary — gestão de mídia | ✅ active |
| [[s3-storage-patterns]] | AWS S3 — padrões de armazenamento | ✅ active |
| [[media-pipeline]] | Pipelines de processamento de mídia | 🚧 draft |

### Messaging & Event Streaming

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[rabbitmq]] | RabbitMQ — message broker AMQP | ✅ active |
| [[sqs-sns]] | AWS SQS/SNS — mensageria gerenciada | ✅ active |
| [[nats]] | NATS — messaging de alta performance | 🚧 draft |
| [[messaging-patterns]] | Padrões: saga, outbox, dead letter queue | ✅ active |

---

## ⚡ Quick Access

- [[clean-architecture]] — Estrutura de código independente de frameworks
- [[microservices]] — Quando e como decompor um sistema
- [[event-driven]] — Desacoplamento via eventos
- [[messaging-patterns]] — Padrões de confiabilidade em mensageria
- [[adr-template]] — Documentar decisões arquiteturais
- [[s3-storage-patterns]] — Armazenamento de objetos em produção

---

## 🏛️ Padrões Arquiteturais

### Monolith First

> [!tip] Regra Geral
> Comece com monolito bem estruturado. Extraia microserviços apenas quando houver necessidade real: diferentes requisitos de escala, times independentes ou domínios com ciclos de deploy muito diferentes. Veja [[microservices]] para os sinais de quando migrar.

```
Monolito Modular → Módulos claros → Extrair quando necessário → Microserviços
```

### Clean Architecture Layers

```
┌─────────────────────────────────┐
│         Frameworks & Drivers    │  ← FastAPI, SQLAlchemy, Redis
├─────────────────────────────────┤
│         Interface Adapters      │  ← Controllers, Presenters, Gateways
├─────────────────────────────────┤
│         Application Use Cases   │  ← Regras de negócio da aplicação
├─────────────────────────────────┤
│         Domain Entities         │  ← Entidades e regras de negócio core
└─────────────────────────────────┘
         Dependências apontam para dentro →
```

Detalhes e exemplos em Python: [[clean-architecture]].

---

## 📨 Messaging Patterns

> [!info] Escolhendo o Message Broker
> - **[[rabbitmq]]** → filas de trabalho, roteamento complexo, AMQP padrão
> - **[[sqs-sns]]** → managed AWS, fan-out, sem infraestrutura para gerenciar
> - **[[nats]]** → ultra-baixa latência, sistemas distribuídos, edge computing
> - **Kafka** → event streaming, alta throughput (ver [[data-engineering-moc]])

### Padrões Críticos de Confiabilidade

```
Outbox Pattern:
  1. Escrever evento na tabela outbox (mesma transação do dado)
  2. Worker lê outbox e publica no broker
  3. Delete/mark após confirmação de entrega

Saga Pattern:
  - Choreography: cada serviço reage a eventos
  - Orchestration: orquestrador central controla o fluxo
```

Ver [[messaging-patterns]] para implementações detalhadas.

---

## ☁️ Cloud Services

### Storage Hierarchy

```
Objetos grandes → [[s3-storage-patterns]] (AWS S3 / R2)
Mídia (imagens/vídeo) → [[cloudinary]] (transformações automáticas)
Cache → Redis (ver [[engineering-moc]])
Banco de dados → PostgreSQL (ver [[engineering-moc]])
```

### Media Pipeline

```
Upload → S3 raw → [[media-pipeline]] → thumbnails/transcoding → [[cloudinary]] CDN
```

---

## 📋 Architecture Decision Records (ADRs)

> [!example] Quando Criar um ADR
> Crie um ADR para qualquer decisão que:
> - Seja difícil ou cara de reverter
> - Afete múltiplos times ou componentes
> - Envolva trade-offs não óbvios
> - Precise ser explicada para novos membros do time

Template em [[adr-template]]. Armazenar ADRs no repositório junto ao código (`docs/adr/`).

---

## 🔗 Integrações com Outros Domínios

- **DevOps** → [[devops-moc]] — como os componentes arquiteturais são deployados e monitorados
- **Engineering** → [[engineering-moc]] — tecnologias que implementam os padrões arquiteturais
- **Data Engineering** → [[data-engineering-moc]] — [[kafka]] e pipelines de dados se conectam à EDA
- **Infrastructure** → [[infrastructure-moc]] — cloud resources que suportam os serviços

---

## ⚠️ Anti-Padrões a Evitar

> [!warning] Armadilhas Comuns
> 1. **Microserviços prematuros** — distribuição adiciona complexidade exponencial
> 2. **Shared database em microserviços** — quebra o isolamento de domínio
> 3. **Comunicação síncrona entre todos os serviços** — cria acoplamento temporal
> 4. **ADRs apenas como formalidade** — deve ser consultado antes de reverter decisões
> 5. **Ignorar o padrão Outbox** — mensagens perdidas em falhas de rede são difíceis de debugar
