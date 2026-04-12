---
tags: [skill, architecture, rabbitmq]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [RabbitMQ]
---

# RabbitMQ

## Overview

RabbitMQ é um message broker baseado no protocolo AMQP 0-9-1 (com suporte a MQTT e STOMP via plugins). Implementa o modelo de roteamento flexível com exchanges e bindings, diferenciando-se de [[sqs-sns]] (fila simples gerenciada) e [[nats]] (pub/sub ultraperformático sem persistência por padrão). Fundamental para implementar [[messaging-patterns]] como Dead Letter, Retry com backoff e fanout. Integra-se naturalmente com [[docker]] e [[microservices]] e compõe arquiteturas [[event-driven]].

> [!info] AMQP Model em uma linha
> Producer → Exchange → Binding → Queue → Consumer. O exchange decide para quais queues rotear, baseado no tipo e routing key.

## Core Concepts

### Tipos de Exchange

```python
# pika — cliente AMQP para Python
import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost", port=5672,
        credentials=pika.PlainCredentials("user", "password"),
        heartbeat=600,
        blocked_connection_timeout=300,
    )
)
channel = connection.channel()

# Direct Exchange — routing key exata
channel.exchange_declare(exchange="orders.direct", exchange_type="direct", durable=True)
channel.basic_publish(
    exchange="orders.direct",
    routing_key="order.created",   # binding key deve ser idêntica
    body=json.dumps({"order_id": 42}),
    properties=pika.BasicProperties(
        delivery_mode=2,           # mensagem persistente (survive restart)
        content_type="application/json",
        message_id="uuid-here",
        timestamp=int(time.time()),
    ),
)

# Topic Exchange — routing key com wildcards (* = 1 palavra, # = 0 ou mais)
# "order.*.created" → "order.eu.created", "order.us.created"
# "order.#"         → qualquer coisa começando com "order."
channel.exchange_declare(exchange="events.topic", exchange_type="topic", durable=True)

# Fanout Exchange — ignora routing key, envia para TODAS as queues vinculadas
channel.exchange_declare(exchange="broadcast.fanout", exchange_type="fanout", durable=True)

# Headers Exchange — roteamento por headers AMQP, ignora routing key
channel.exchange_declare(exchange="metadata.headers", exchange_type="headers", durable=True)
channel.queue_bind(
    exchange="metadata.headers",
    queue="premium-queue",
    arguments={"x-match": "all", "tier": "premium", "region": "us"},  # all ou any
)
```

### Tipos de Queue

**Classic Queue** — padrão, suporta todas as features mas sem replicação automática.
**Quorum Queue** — baseado em Raft, replicada, durável e tolerante a falhas. Substitui mirrored queues.
**Stream** — log de mensagens com replay, similar ao Kafka. Consumidores mantêm offset próprio.

```python
# Quorum Queue (recomendada para produção)
channel.queue_declare(
    queue="orders.processing",
    durable=True,
    arguments={
        "x-queue-type": "quorum",
        "x-delivery-limit": 5,            # max re-deliveries antes de DLX
        "x-dead-letter-exchange": "orders.dlx",
        "x-dead-letter-routing-key": "dead.orders.processing",
    },
)

# Stream Queue
channel.queue_declare(
    queue="audit.events",
    durable=True,
    arguments={
        "x-queue-type": "stream",
        "x-max-length-bytes": 10 * 1024 * 1024 * 1024,  # 10 GB retention
        "x-stream-max-segment-size-bytes": 100 * 1024 * 1024,  # 100 MB/segment
    },
)
```

### Dead Letter Exchange (DLX)

Mensagens são movidas para DLX quando: TTL expira, fila atinge `x-max-length`, consumer rejeita com `requeue=False`.

```python
# Setup DLX + DLQ
channel.exchange_declare(exchange="orders.dlx", exchange_type="direct", durable=True)
channel.queue_declare(
    queue="orders.dead",
    durable=True,
    arguments={
        "x-message-ttl": 7 * 24 * 60 * 60 * 1000,  # 7 dias na DLQ
    },
)
channel.queue_bind(
    exchange="orders.dlx",
    queue="orders.dead",
    routing_key="dead.orders.processing",
)

# Consumer com rejeição explícita
def process_order(ch, method, properties, body):
    try:
        order = json.loads(body)
        handle_order(order)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except RetryableError:
        # Requeue para nova tentativa (cuidado com loops infinitos)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except PermanentError:
        # Manda para DLX sem requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

### Prefetch Count e QoS

```python
# QoS: quantas mensagens o broker envia sem ACK do consumer
channel.basic_qos(prefetch_count=10)  # 10 mensagens em flight por consumer
# prefetch_count=1 → processamento serial garantido (mais seguro, menor throughput)
# prefetch_count=0 → sem limite (risco de overwhelm do consumer)

# Em quorum queues, prefetch é por consumer (não por canal)
channel.basic_qos(prefetch_count=20, global_qos=False)  # por consumer
```

### Publisher Confirms

Garante que o broker recebeu e persistiu a mensagem antes de prosseguir:

```python
channel.confirm_delivery()  # ativa publisher confirms no canal

try:
    channel.basic_publish(
        exchange="orders.direct",
        routing_key="order.created",
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
        mandatory=True,   # retorna se não houver binding (aciona on_return)
    )
    # basic_publish com confirm_delivery levanta UnroutableError se mandatory e sem binding
except pika.exceptions.UnroutableError:
    logger.error("Mensagem não roteável — nenhuma fila vinculada")
```

### Consumer Acknowledgements

```python
# Manual ACK (sempre preferido para workloads críticos)
channel.basic_consume(
    queue="orders.processing",
    on_message_callback=process_order,
    auto_ack=False,    # NUNCA use auto_ack=True em produção com processamento real
)

# Timeout de ACK — quorum queues têm consumer timeout (padrão: 30 min)
# Configure via policy ou rabbitmq.conf:
# consumer_timeout = 1800000
```

## Patterns

### Retry com Backoff Exponencial

```python
def publish_with_retry(payload: dict, attempt: int = 0, max_attempts: int = 5):
    delay_ms = min(1000 * (2 ** attempt), 30000)  # cap em 30s
    channel.queue_declare(
        queue=f"orders.retry.{delay_ms}ms",
        durable=True,
        arguments={
            "x-message-ttl": delay_ms,
            "x-dead-letter-exchange": "orders.direct",
            "x-dead-letter-routing-key": "order.created",
        },
    )
    props = pika.BasicProperties(
        delivery_mode=2,
        headers={"x-attempt": attempt + 1, "x-max-attempts": max_attempts},
    )
    channel.basic_publish(
        exchange="",
        routing_key=f"orders.retry.{delay_ms}ms",
        body=json.dumps(payload),
        properties=props,
    )
```

### Clustering e Quorum Queues

```yaml
# docker-compose para cluster RabbitMQ 3 nodes
services:
  rabbitmq1:
    image: rabbitmq:3.13-management
    environment:
      RABBITMQ_ERLANG_COOKIE: "secret-cookie"
      RABBITMQ_NODENAME: rabbit@rabbitmq1
    volumes:
      - ./rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf

  rabbitmq2:
    image: rabbitmq:3.13-management
    environment:
      RABBITMQ_ERLANG_COOKIE: "secret-cookie"
      RABBITMQ_NODENAME: rabbit@rabbitmq2

  rabbitmq3:
    image: rabbitmq:3.13-management
    environment:
      RABBITMQ_ERLANG_COOKIE: "secret-cookie"
      RABBITMQ_NODENAME: rabbit@rabbitmq3
```

```ini
# rabbitmq.conf
cluster_formation.peer_discovery_backend = rabbit_peer_discovery_classic_config
cluster_formation.classic_config.nodes.1 = rabbit@rabbitmq1
cluster_formation.classic_config.nodes.2 = rabbit@rabbitmq2
cluster_formation.classic_config.nodes.3 = rabbit@rabbitmq3
# Quorum queue requer mínimo 3 nodes para maioria (2 de 3)
```

## Gotchas

> [!danger] Mirrored Queues estão deprecated desde RabbitMQ 3.9 — use Quorum Queues
> Classic mirrored queues têm problemas de split-brain e performance. Quorum queues (Raft-based) são mais seguras e performáticas para workloads críticos.

> [!warning] Connection vs Channel — não abuse de connections
> AMQP é multiplexado: uma connection TCP suporta múltiplos channels (virtual connections). Crie uma connection por processo/thread e channels por operação lógica. Muitas connections simultâneas degradam o broker.

> [!warning] auto_ack=True causa perda de mensagens em caso de crash
> O broker marca a mensagem como entregue imediatamente. Se o consumer crashar antes de processar, a mensagem é perdida permanentemente.

> [!tip] Management Plugin — use para observabilidade
> `rabbitmq-plugins enable rabbitmq_management` expõe HTTP API em :15672 e UI de gerenciamento. Monitore: queue depth, consumer count, publish/deliver rates e unacked messages.

## Snippets

```bash
# CLI de administração
rabbitmqctl list_queues name messages consumers
rabbitmqctl list_exchanges name type durable
rabbitmqctl list_bindings
rabbitmqadmin get queue=orders.dead count=10   # inspecionar DLQ
```

```python
# Connection pool com pika (thread-safe via ThreadedConnection)
from pika.adapters.blocking_connection import BlockingChannel
import threading

_local = threading.local()

def get_channel() -> BlockingChannel:
    if not hasattr(_local, "channel") or _local.channel.is_closed:
        conn = pika.BlockingConnection(params)
        _local.channel = conn.channel()
        _local.channel.basic_qos(prefetch_count=10)
    return _local.channel
```

## References

- [RabbitMQ Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues)
- [Publisher Confirms](https://www.rabbitmq.com/docs/confirms)
- [Dead Letter Exchanges](https://www.rabbitmq.com/docs/dlx)
- [AMQP 0-9-1 Model](https://www.rabbitmq.com/tutorials/amqp-concepts)

## Related

- [[messaging-patterns]] — padrões arquiteturais implementados com RabbitMQ
- [[sqs-sns]] — alternativa managed AWS sem AMQP
- [[nats]] — alternativa de alta performance para pub/sub simples
- [[docker]] — containerização e clustering de RabbitMQ
- [[event-driven]] — arquitetura orientada a eventos com RabbitMQ
- [[microservices]] — comunicação assíncrona entre serviços
