---
tags: [skill, architecture, messaging-patterns]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Messaging Patterns]
---

# Messaging Patterns

## Overview

Messaging patterns são soluções arquiteturais recorrentes para comunicação assíncrona entre serviços. São independentes de tecnologia — aplicam-se a [[rabbitmq]], [[sqs-sns]], [[nats]], [[kafka]] e outros brokers. A escolha correta de padrão define a resiliência, consistência e escalabilidade de sistemas [[event-driven]] e [[microservices]]. Este documento cataloga os padrões fundamentais com suas implementações, trade-offs e anti-patterns mais comuns.

> [!info] Padrão vs Implementação
> Um padrão como "Saga" é uma solução conceitual. A implementação varia: pode usar [[rabbitmq]] com DLX para compensação, ou [[nats]] JetStream para sequenciamento de steps. Entender o padrão permite aplicá-lo em qualquer broker.

## Core Concepts

### Entrega Semântica: At-Most-Once, At-Least-Once, Exactly-Once

```
At-Most-Once:   Perda possível, sem duplicata. (Core NATS sem JetStream, UDP)
At-Least-Once:  Duplicata possível, sem perda. (SQS, RabbitMQ com ack, NATS JetStream)
Exactly-Once:   Nem perda nem duplicata. (Kafka idempotent producer + transactions,
                SQS FIFO com deduplication ID, NATS JetStream com ack+dedup)
```

> [!warning] Exactly-once é caro e raro na prática
> A maioria dos sistemas usa at-least-once + idempotência no consumer. É mais simples e resiliente do que tentar garantir exactly-once no nível do broker.

### Idempotência no Consumer

```python
import hashlib
import redis

r = redis.Redis()

def idempotent_process(message_id: str, payload: dict) -> bool:
    """Retorna True se processou, False se já foi processado antes."""
    dedup_key = f"processed:{message_id}"

    # SET NX com TTL — atômico, sem race condition
    was_set = r.set(dedup_key, "1", nx=True, ex=86400)  # TTL 24h
    if not was_set:
        # Já processado anteriormente — ignorar silenciosamente
        return False

    try:
        apply_business_logic(payload)
        return True
    except Exception:
        # Falha: remover a key para permitir retry
        r.delete(dedup_key)
        raise
```

## Patterns

### 1. Pub/Sub (Publicação-Assinatura)

Decoupling entre producers e consumers. O producer não sabe quantos nem quais consumers existem.

```python
# Publisher — agnóstico de consumers
def publish_order_event(order: dict, event_type: str):
    sns.publish(
        TopicArn=ORDER_EVENTS_TOPIC,
        Message=json.dumps(order),
        MessageAttributes={
            "EventType": {"DataType": "String", "StringValue": event_type},
        },
    )

# Múltiplos consumers independentes subscrevem o mesmo topic:
# - inventory-service: atualiza estoque
# - email-service: envia confirmação
# - analytics-service: registra para relatórios
# Cada um recebe cópia independente da mensagem
```

### 2. Competing Consumers (Worker Pool)

Múltiplos consumers competem por mensagens de uma fila — load balancing automático e paralelismo:

```python
# RabbitMQ: QueueSubscribe ou múltiplos consumers na mesma queue
# SQS: múltiplos workers fazendo polling na mesma queue
# NATS: QueueSubscribe com mesmo group name

import threading

def start_worker_pool(queue_url: str, num_workers: int = 5):
    def worker(worker_id: int):
        while True:
            messages = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,
                VisibilityTimeout=300,
            ).get("Messages", [])

            for msg in messages:
                try:
                    process(json.loads(msg["Body"]))
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg["ReceiptHandle"]
                    )
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed: {e}")
                    # Não deleta → retorna à fila após VisibilityTimeout

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_workers)]
    for t in threads:
        t.start()
```

### 3. Request-Reply

Consumer responde ao producer em um canal de reply temporário — RPC sobre mensageria:

```python
# NATS request-reply (mais elegante que implementação manual)
response = await nc.request("inventory.check",
    json.dumps({"product_id": "SKU-001"}).encode(), timeout=3.0)
result = json.loads(response.data)

# RabbitMQ: correlation_id + reply_to
import uuid
correlation_id = str(uuid.uuid4())
channel.basic_publish(
    exchange="",
    routing_key="inventory.check",
    properties=pika.BasicProperties(
        reply_to="amq.rabbitmq.reply-to",   # direct reply queue
        correlation_id=correlation_id,
        expiration="3000",
    ),
    body=json.dumps({"product_id": "SKU-001"}),
)
# Consumer correlaciona pela correlation_id
```

### 4. Dead Letter Handling

Mensagens que falharam repetidamente são movidas para uma DLQ para inspeção e replay manual:

```python
class DLQProcessor:
    """Reprocessa mensagens da DLQ após investigação."""

    def replay_dlq_message(self, receipt_handle: str, fix_payload: dict = None):
        """Move mensagem da DLQ de volta para a fila principal."""
        msg = self.sqs.receive_message(
            QueueUrl=DLQ_URL, ReceiptHandle=receipt_handle
        )
        body = json.loads(msg["Body"])

        if fix_payload:
            body.update(fix_payload)  # corrige o payload antes do replay

        self.sqs.send_message(
            QueueUrl=MAIN_QUEUE_URL,
            MessageBody=json.dumps(body),
            MessageAttributes={
                "ReplayedFrom": {"DataType": "String", "StringValue": "dlq"},
                "OriginalMessageId": {"DataType": "String",
                                      "StringValue": msg["MessageId"]},
            },
        )
        self.sqs.delete_message(QueueUrl=DLQ_URL, ReceiptHandle=receipt_handle)

    def bulk_replay(self, max_messages: int = 100):
        """Replay em massa de mensagens da DLQ."""
        replayed = 0
        while replayed < max_messages:
            messages = self.sqs.receive_message(
                QueueUrl=DLQ_URL, MaxNumberOfMessages=10, WaitTimeSeconds=5
            ).get("Messages", [])
            if not messages:
                break
            for msg in messages:
                self.sqs.send_message(QueueUrl=MAIN_QUEUE_URL, MessageBody=msg["Body"])
                self.sqs.delete_message(QueueUrl=DLQ_URL, ReceiptHandle=msg["ReceiptHandle"])
                replayed += 1
```

### 5. Transactional Outbox

Garante consistência entre gravação no banco e publicação de evento — elimina o dual-write problem:

```python
# PROBLEMA: banco + broker são sistemas distintos — não há transação global
# SOLUÇÃO: gravar evento na mesma transação do banco, publicar via polling

# 1. Gravação transacional (dentro de uma transaction do banco)
async def create_order(order_data: dict, db: AsyncSession) -> Order:
    async with db.begin():
        order = Order(**order_data)
        db.add(order)

        # Outbox: evento gravado na mesma transação
        outbox_event = OutboxEvent(
            aggregate_type="Order",
            aggregate_id=str(order.id),
            event_type="order.created",
            payload=json.dumps(order.to_dict()),
            status="pending",
        )
        db.add(outbox_event)
        # Se a transação falhar, nem order nem outbox_event são gravados
    return order

# 2. Outbox Poller — processo independente publica eventos pendentes
async def outbox_poller():
    while True:
        async with db.begin():
            events = await db.execute(
                select(OutboxEvent)
                .where(OutboxEvent.status == "pending")
                .order_by(OutboxEvent.created_at)
                .limit(50)
                .with_for_update(skip_locked=True)  # evita processar mesmo evento em paralelo
            )
            for event in events.scalars():
                try:
                    await publish_to_broker(event.event_type, event.payload)
                    event.status = "published"
                    event.published_at = datetime.utcnow()
                except Exception as e:
                    event.retries += 1
                    event.last_error = str(e)
                    if event.retries >= 5:
                        event.status = "failed"
        await asyncio.sleep(1)
```

### 6. Saga — Choreography vs Orchestration

Saga distribui uma transação longa em steps locais com compensação em caso de falha:

```python
# --- CHOREOGRAPHY: cada serviço reage a eventos e publica próximo ---
# Vantagem: descentralizado, serviços independentes
# Desvantagem: difícil de rastrear o fluxo completo

# Order Service
async def on_order_created(event: dict):
    # Tenta reservar pagamento
    await publish("payment.reserve", {"order_id": event["order_id"], "amount": event["total"]})

# Payment Service
async def on_payment_reserved(event: dict):
    await publish("inventory.reserve", {"order_id": event["order_id"], "items": event["items"]})

async def on_payment_failed(event: dict):
    # Compensação: cancela order
    await publish("order.cancel", {"order_id": event["order_id"], "reason": "payment_failed"})

# Inventory Service
async def on_inventory_reserved(event: dict):
    await publish("shipping.schedule", {"order_id": event["order_id"]})

async def on_inventory_failed(event: dict):
    # Compensação: estorna pagamento
    await publish("payment.refund", {"order_id": event["order_id"]})

# --- ORCHESTRATION: um orquestrador central controla o fluxo ---
# Vantagem: visibilidade central, fácil de debugar e monitorar
# Desvantagem: acoplamento ao orquestrador (ponto central de falha)

class OrderSagaOrchestrator:
    async def execute(self, order_id: str):
        saga_state = await self.load_or_create_saga(order_id)

        try:
            if saga_state.step == "start":
                await self.call_service("payment-service", "reserve", order_id)
                saga_state.step = "payment_reserved"

            if saga_state.step == "payment_reserved":
                await self.call_service("inventory-service", "reserve", order_id)
                saga_state.step = "inventory_reserved"

            if saga_state.step == "inventory_reserved":
                await self.call_service("shipping-service", "schedule", order_id)
                saga_state.step = "completed"

        except ServiceError as e:
            await self.compensate(saga_state, e)

    async def compensate(self, state, error):
        """Executa compensações em ordem reversa."""
        if state.step in ("inventory_reserved", "completed"):
            await self.call_service("inventory-service", "release", state.order_id)
        if state.step in ("payment_reserved", "inventory_reserved", "completed"):
            await self.call_service("payment-service", "refund", state.order_id)
```

### 7. Envelope Pattern

Encapsula metadados de contexto em toda mensagem — fundamental para rastreabilidade e versionamento:

```python
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class MessageEnvelope:
    # Metadados de identidade
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    causation_id: str | None = None   # message_id que causou este evento

    # Metadados de contexto
    event_type: str = ""
    event_version: str = "v1"
    source_service: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Payload
    payload: dict = field(default_factory=dict)

    # Rastreabilidade
    trace_id: str | None = None     # OpenTelemetry trace
    span_id: str | None = None

def wrap_message(event_type: str, payload: dict, source: str,
                 correlation_id: str = None, causation_id: str = None) -> dict:
    from opentelemetry import trace
    span = trace.get_current_span()
    ctx = span.get_span_context()

    return MessageEnvelope(
        event_type=event_type,
        source_service=source,
        correlation_id=correlation_id or str(uuid.uuid4()),
        causation_id=causation_id,
        payload=payload,
        trace_id=format(ctx.trace_id, "032x") if ctx.is_valid else None,
        span_id=format(ctx.span_id, "016x") if ctx.is_valid else None,
    ).__dict__
```

### 8. Deduplicação e Ordering

```python
# Deduplicação com sliding window via Redis
class MessageDeduplicator:
    def __init__(self, redis_client, window_seconds: int = 86400):
        self.redis = redis_client
        self.window = window_seconds

    def is_duplicate(self, message_id: str) -> bool:
        key = f"dedup:{message_id}"
        result = self.redis.set(key, "1", nx=True, ex=self.window)
        return result is None  # None = já existia (duplicata)

# Ordering garantido: use partition key / MessageGroupId
# SQS FIFO: mesmo MessageGroupId → ordenação estrita, sem paralelo no grupo
# NATS JetStream: subjects por entidade, consumer por partition:
#   orders.order-123 → sempre para o mesmo consumer leaf
```

## Gotchas

> [!danger] Two-phase commit distribuído é anti-pattern em microservices
> Coordenar transações via 2PC entre serviços é frágil, lento e introduz acoplamento temporal. Use Saga + compensação ou Outbox para consistência eventual.

> [!warning] Choreography sem observabilidade vira "event spaghetti"
> Em sistemas com muitos serviços usando choreography, o fluxo de negócio fica invisível. Use correlation_id + distributed tracing (OpenTelemetry) para rastrear sagas e sempre monitore eventos de compensação.

> [!warning] Outbox poller com `SELECT FOR UPDATE` pode criar hotspot
> Em alto volume, o poller vira gargalo. Use `SKIP LOCKED` para paralelismo seguro, ou adote Debezium (CDC) para capturar mudanças no WAL do banco sem polling.

> [!tip] Idempotência é mais fácil que exactly-once no broker
> Implementar idempotência no consumer com Redis/DynamoDB é mais simples, portável e testável do que depender de exactly-once delivery do broker. Trate cada mensagem como potencialmente duplicada.

## Snippets

```python
# Circuit breaker simples para publicação de mensagens
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # normal
    OPEN = "open"           # failing, rejecting calls
    HALF_OPEN = "half_open" # testing recovery

class MessageCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def call(self, publish_fn, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker OPEN — rejecting publish")

        try:
            result = publish_fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.threshold:
            self.state = CircuitState.OPEN
```

```bash
# Verificar mensagens acumuladas (SQS)
aws sqs get-queue-attributes \
  --queue-url $QUEUE_URL \
  --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible

# Monitorar DLQ (RabbitMQ)
rabbitmqadmin get queue=orders.dead count=10 --format=pretty_json

# NATS: inspecionar consumer lag
nats consumer info ORDERS order-processor --json | jq '.num_pending, .num_redelivered'
```

## References

- [Enterprise Integration Patterns — Gregor Hohpe](https://www.enterpriseintegrationpatterns.com/)
- [Saga Pattern — Chris Richardson](https://microservices.io/patterns/data/saga.html)
- [Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html)
- [Competing Consumers](https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers)
- [Dead Letter Queue Pattern](https://aws.amazon.com/blogs/compute/designing-durable-serverless-apps-with-dlqs-for-amazon-sns-sqs-lambda/)

## Related

- [[rabbitmq]] — implementação: DLX, topic exchange, quorum queues, publisher confirms
- [[sqs-sns]] — implementação: FIFO, visibility timeout, SNS filtering, Lambda triggers
- [[nats]] — implementação: JetStream consumers, KV store, request-reply
- [[kafka]] — implementação: partitions, consumer groups, compaction, exactly-once
- [[event-driven]] — arquitetura que aplica estes padrões como first-class citizens
- [[microservices]] — contexto onde estes padrões resolvem comunicação inter-serviço
