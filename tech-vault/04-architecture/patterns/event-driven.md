---
tags: [skill, architecture, event-driven]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Event-Driven Architecture, EDA]
---

# Event-Driven Architecture

## Overview

Event-Driven Architecture (EDA) é um paradigma onde componentes se comunicam produzindo, detectando e reagindo a eventos. Um **evento** é um registro imutável de algo que aconteceu no passado — não um comando, não uma query, mas um fato.

> [!important] Evento vs Comando vs Query
> - **Evento**: `OrderWasPlaced` — algo aconteceu, produtor não sabe quem vai consumir
> - **Comando**: `PlaceOrder` — instrução para fazer algo, dirigido a um destinatário
> - **Query**: `GetOrder` — requisição de informação, sem side effects

EDA desacopla produtores de consumidores no tempo e no espaço. O produtor não precisa saber se há 0, 1 ou 100 consumidores. Integra naturalmente com [[microservices]] e [[kafka]].

---

## Core Concepts

### Event Sourcing

Em vez de armazenar o **estado atual** de uma entidade, armazena-se a **sequência de eventos** que levou a esse estado. O estado atual é derivado por replay dos eventos.

```
Estado Tradicional (snapshot):
  orders table: { id: 1, status: "shipped", total: 150.00 }

Event Sourcing:
  events table:
    { id: 1, type: "OrderCreated",   payload: {...}, timestamp: T1 }
    { id: 2, type: "ItemAdded",      payload: {...}, timestamp: T2 }
    { id: 3, type: "PaymentApplied", payload: {...}, timestamp: T3 }
    { id: 4, type: "OrderShipped",   payload: {...}, timestamp: T4 }
```

**Benefícios:**
- Audit log completo e imutável gratuitamente
- Time-travel: reconstituir estado em qualquer ponto do tempo
- Múltiplas projeções do mesmo dado para diferentes read models
- Debugging: reproduzir bugs com exatamente os eventos que ocorreram

**Snapshots** — para entidades com muitos eventos, salva-se snapshot periódico para evitar replay completo:

```python
class OrderAggregate:
    def __init__(self):
        self.version = 0
        self.status = None
        self.items = []
        self.total = 0

    @classmethod
    async def load(cls, order_id: str, event_store: EventStore) -> "OrderAggregate":
        order = cls()
        # Tenta carregar snapshot mais recente
        snapshot = await event_store.get_snapshot(order_id)
        if snapshot:
            order.__dict__.update(snapshot.state)
            from_version = snapshot.version
        else:
            from_version = 0

        # Aplica apenas eventos após o snapshot
        events = await event_store.get_events(order_id, from_version=from_version)
        for event in events:
            order.apply(event)
        return order

    def apply(self, event: DomainEvent):
        handler = getattr(self, f"on_{event.type}", None)
        if handler:
            handler(event.payload)
        self.version += 1

    def on_OrderCreated(self, payload):
        self.status = "created"
        self.total = 0

    def on_PaymentApplied(self, payload):
        self.status = "paid"
```

### CQRS — Command Query Responsibility Segregation

Separação completa entre o modelo de escrita (commands, que produzem eventos) e o modelo de leitura (queries, que consomem projeções otimizadas).

```
Write Side (Command Model):
  Client ──► Command ──► Command Handler ──► Aggregate ──► Events ──► Event Store

Read Side (Query Model):
  Event Store ──► Projector ──► Read Model (denormalized, query-optimized)
  Client ──► Query ──► Read Model ──► Response (fast, no joins)
```

> [!tip] Read Models são descartáveis
> A fonte da verdade são os eventos. Read models podem ser dropados e reconstruídos via replay a qualquer momento. Isso permite mudar o schema do read model sem migration complexa.

```python
# Projeção: constrói read model a partir de eventos
class OrderSummaryProjection:
    """Projeção desnormalizada para listagem de pedidos."""

    async def handle(self, event: DomainEvent):
        match event.type:
            case "OrderCreated":
                await self.db.execute("""
                    INSERT INTO order_summaries (id, user_id, status, created_at)
                    VALUES (:id, :user_id, 'created', :created_at)
                """, event.payload)

            case "PaymentApplied":
                await self.db.execute("""
                    UPDATE order_summaries
                    SET status = 'paid', total = :total
                    WHERE id = :order_id
                """, event.payload)

            case "OrderShipped":
                await self.db.execute("""
                    UPDATE order_summaries
                    SET status = 'shipped', shipped_at = :shipped_at
                    WHERE id = :order_id
                """, event.payload)
```

---

## Patterns

### Domain Events vs Integration Events

| Tipo | Escopo | Consumidor | Contrato |
|------|--------|------------|---------|
| Domain Event | Dentro do bounded context | Mesmo serviço/agregado | Schema interno, pode mudar |
| Integration Event | Entre bounded contexts | Outros serviços | Contrato público, versionado |

```python
# Domain Event — detalhe interno do domínio
@dataclass
class OrderItemsValidated:
    order_id: str
    validated_items: list[ValidatedItem]  # tipo interno

# Integration Event — contrato público entre serviços
@dataclass
class OrderPlacedV2:
    """v2: adicionado campo `currency` — backward compatible."""
    event_id: str              # para idempotência
    order_id: str
    customer_id: str
    total_amount: Decimal
    currency: str = "BRL"      # novo campo com default
    occurred_at: datetime
```

### Idempotência e Deduplicação

Em sistemas distribuídos, **at-least-once delivery** é garantia comum. O mesmo evento pode ser entregue múltiplas vezes. O consumidor deve ser idempotente.

```python
class IdempotentEventHandler:
    async def handle(self, event: IntegrationEvent):
        # Verifica se já processou este evento
        already_processed = await self.processed_events.exists(event.event_id)
        if already_processed:
            logger.info(f"Skipping duplicate event {event.event_id}")
            return

        # Processa o evento dentro de uma transação
        async with self.db.transaction():
            await self._process(event)
            # Marca como processado atomicamente com o efeito
            await self.processed_events.mark(
                event_id=event.event_id,
                processed_at=datetime.utcnow(),
                handler=self.__class__.__name__,
            )
```

### Dead Letter Queue (DLQ)

Eventos que falham repetidamente são movidos para a DLQ para análise sem bloquear o fluxo principal.

```python
# Configuração de DLQ no [[rabbitmq]]
channel.queue_declare(
    queue="orders.process",
    arguments={
        "x-dead-letter-exchange": "dlx",
        "x-dead-letter-routing-key": "orders.process.dlq",
        "x-message-ttl": 86400000,  # 24h TTL na DLQ
        "x-max-retries": 3,
    }
)

# Consumer com retry e DLQ routing
async def consume_with_retry(message: aio_pika.IncomingMessage):
    retry_count = int(message.headers.get("x-retry-count", 0))
    try:
        await process_order_event(message.body)
        await message.ack()
    except RetryableError as e:
        if retry_count < 3:
            # Re-publica com retry count incrementado
            await republish_with_delay(message, retry_count + 1, delay_seconds=2**retry_count)
            await message.ack()
        else:
            # Esgotou retries — vai para DLQ
            await message.reject(requeue=False)
            logger.error(f"Event sent to DLQ after {retry_count} retries: {e}")
```

### Ordering Guarantees e Particionamento

[[kafka]] garante ordem **dentro de uma partição**. A chave de particionamento deve ser a entidade que precisa de ordem serial.

```python
# Produtor Kafka — usa order_id como chave para garantir ordem
producer.produce(
    topic="orders",
    key=order_id.encode(),       # mesma chave → mesma partição → ordem garantida
    value=event.model_dump_json().encode(),
    on_delivery=delivery_callback,
)

# Problema: se um consumidor processar eventos de ordens diferentes em paralelo,
# eventos de MESMA ordem devem ir para o mesmo worker (consistent hashing)
```

> [!warning] Ordering vs Throughput Trade-off
> Mais partições = mais paralelismo = mais throughput, mas cada partição é processada sequencialmente. Particione pela entidade que precisa de consistência serial, não globalmente.

### Eventual Consistency e Conflict Resolution

```python
# Last-Write-Wins com vector clocks (simplificado)
@dataclass
class VersionedState:
    data: dict
    vector_clock: dict[str, int]  # { "node_id": sequence }

    def happens_before(self, other: "VersionedState") -> bool:
        return all(
            self.vector_clock.get(node, 0) <= other.vector_clock.get(node, 0)
            for node in set(self.vector_clock) | set(other.vector_clock)
        ) and self.vector_clock != other.vector_clock

    def is_concurrent_with(self, other: "VersionedState") -> bool:
        return not self.happens_before(other) and not other.happens_before(self)
```

---

## Gotchas

> [!danger] Event Schema Evolution
> Eventos são imutáveis e ficam no event store para sempre. Uma mudança breaking no schema pode impedir o replay de eventos antigos. Use sempre backward-compatible changes: adicione campos com defaults, nunca remova ou renomeie campos de eventos já publicados. Versione explicitamente: `OrderPlacedV1`, `OrderPlacedV2`.

> [!warning] Eventual Consistency na UI
> Após um comando, a leitura imediata pode retornar estado desatualizado. Solução: use **optimistic UI** (exibe estado esperado imediatamente) ou **read-your-writes consistency** (redireciona reads para o write model por curto período após o comando).

> [!bug] Event Ordering em Múltiplos Consumidores
> Em [[kafka]], dois consumidores no mesmo grupo consumer group lendo partições diferentes podem processar eventos de diferentes ordens. Designe a chave de partição para manter eventos causalmente relacionados na mesma partição.

---

## Snippets

### Event Store Simples (PostgreSQL)

```sql
-- Tabela de eventos — append-only, nunca UPDATE/DELETE
CREATE TABLE events (
    id          BIGSERIAL PRIMARY KEY,
    stream_id   UUID NOT NULL,           -- ex: order_id
    stream_type VARCHAR(100) NOT NULL,   -- ex: 'Order'
    event_type  VARCHAR(100) NOT NULL,   -- ex: 'OrderCreated'
    payload     JSONB NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}',
    version     INTEGER NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (stream_id, version)          -- optimistic concurrency
);

CREATE INDEX idx_events_stream ON events (stream_id, version);
CREATE INDEX idx_events_type ON events (event_type, occurred_at);
```

---

## References

- **Designing Event-Driven Systems** — Ben Stopford (free PDF, Confluent)
- **Event Sourcing** — Greg Young — [cqrs.nu](https://cqrs.nu) (artigos originais)
- **Versioning in an Event Sourced System** — Greg Young (e-book)
- [[kafka]] — plataforma de streaming distribuído
- [[rabbitmq]] — message broker com suporte a AMQP
- [[sqs-sns]] — serviços de mensageria AWS
- [[nats]] — messaging leve para cloud-native
- [[messaging-patterns]] — padrões gerais de mensageria

---

## Related

- [[microservices]] — EDA é o principal mecanismo de comunicação entre microservices
- [[messaging-patterns]] — pub/sub, queues, topics, fan-out
- [[kafka]] — implementação de referência para event streaming
- [[rabbitmq]] — broker para padrões assíncronos complexos
- [[sqs-sns]] — alternativa gerenciada na AWS
- [[nats]] — broker ultra-leve para IoT e edge
