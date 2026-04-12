---
tags: [skill, data-engineering, kafka]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Kafka, Apache Kafka]
---

# Apache Kafka

## Overview

Apache Kafka é uma plataforma de streaming distribuído baseada em log append-only. É o backbone de arquiteturas [[event-driven]] modernas: producers publicam eventos em topics, consumers leem em sua própria velocidade, e o log é retido por tempo configurável. Kafka não é uma fila de mensagens — é um **log de eventos distribuído**.

> [!important] Kafka vs Message Queue
> Filas tradicionais (RabbitMQ, SQS) deletam mensagens após o consumo. Kafka **retém** os eventos (padrão: 7 dias). Múltiplos consumer groups podem reler os mesmos eventos independentemente — fundamental para [[event-driven]] e reprocessamento.

---

## Core Concepts

### Topics, Partitions e Offsets

```
Topic: orders
├── Partition 0: [offset 0] [offset 1] [offset 2] ...
├── Partition 1: [offset 0] [offset 1] ...
└── Partition 2: [offset 0] [offset 1] ...
```

- **Topic**: categoria lógica de eventos
- **Partition**: unidade de paralelismo e ordenação (ordem garantida apenas dentro da partição)
- **Offset**: posição sequencial imutável dentro de uma partição
- **Replication Factor**: quantas cópias de cada partição existem

```bash
# Criar topic com 12 partições e replication factor 3
kafka-topics.sh --create \
  --topic orders \
  --partitions 12 \
  --replication-factor 3 \
  --config retention.ms=604800000 \
  --config compression.type=lz4 \
  --bootstrap-server kafka:9092
```

### Producer

```python
# confluent_kafka (recomendado sobre kafka-python)
from confluent_kafka import Producer
import json

producer = Producer({
    "bootstrap.servers": "kafka-broker-1:9092,kafka-broker-2:9092",
    "acks": "all",              # espera confirmação de todos os ISRs
    "enable.idempotence": True, # exatamente uma vez no producer
    "compression.type": "lz4",
    "batch.size": 65536,        # 64KB por batch
    "linger.ms": 5,             # aguarda 5ms para acumular batch
})

def delivery_callback(err, msg):
    if err:
        print(f"Erro: {err}")
    else:
        print(f"Entregue: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

for order in orders:
    producer.produce(
        topic="orders",
        key=str(order["customer_id"]).encode(),  # key define partição
        value=json.dumps(order).encode(),
        callback=delivery_callback,
    )
    producer.poll(0)  # serve callbacks pendentes

producer.flush()  # aguarda todos os acks
```

### Consumer Groups

```python
from confluent_kafka import Consumer, KafkaException

consumer = Consumer({
    "bootstrap.servers": "kafka:9092",
    "group.id": "orders-processor",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,  # commit manual para controle
    "max.poll.interval.ms": 300000,
})

consumer.subscribe(["orders"])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        order = json.loads(msg.value().decode())
        process_order(order)

        # Commit após processamento bem-sucedido
        consumer.commit(asynchronous=False)
finally:
    consumer.close()
```

> [!info] Consumer Group Rebalancing
> Quando um consumer entra ou sai do grupo, Kafka executa um **rebalance**: redistribui partições entre os consumers ativos. Durante o rebalance, o consumo para. Use `CooperativeStickyAssignor` para minimizar disrupção (rebalance incremental).

### Exactly-Once Semantics (EOS)

```python
# Producer transacional (exatamente uma vez)
producer = Producer({
    "bootstrap.servers": "kafka:9092",
    "transactional.id": "orders-producer-1",  # ID único por instância
    "enable.idempotence": True,
})

producer.init_transactions()

try:
    producer.begin_transaction()

    for order in batch:
        producer.produce("orders", key=order["id"], value=json.dumps(order))

    # Commit atômico: producer offset + consumer offset
    producer.send_offsets_to_transaction(
        consumer.position(consumer.assignment()),
        consumer.consumer_group_metadata(),
    )
    producer.commit_transaction()

except Exception as e:
    producer.abort_transaction()
    raise
```

### Schema Registry (Avro)

Schema Registry centraliza esquemas e garante compatibilidade evolutiva:

```python
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro

value_schema = avro.loads("""
{
  "type": "record",
  "name": "Order",
  "fields": [
    {"name": "order_id",    "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "amount",      "type": "double"},
    {"name": "status",      "type": {"type": "enum", "name": "OrderStatus",
                                      "symbols": ["PENDING", "PAID", "CANCELLED"]}},
    {"name": "created_at",  "type": "long", "logicalType": "timestamp-millis"}
  ]
}
""")

avro_producer = AvroProducer(
    {"bootstrap.servers": "kafka:9092", "schema.registry.url": "http://schema-registry:8081"},
    default_value_schema=value_schema,
)

avro_producer.produce(topic="orders", value={"order_id": "123", "amount": 99.99, ...})
```

Modos de compatibilidade: `BACKWARD` (padrão), `FORWARD`, `FULL`, `NONE`.

---

## Patterns

### Kafka Connect

```json
// Source Connector — Debezium (CDC do PostgreSQL)
{
  "name": "postgres-cdc-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "secret",
    "database.dbname": "app_db",
    "table.include.list": "public.orders,public.customers",
    "topic.prefix": "cdc",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot"
  }
}
```

```json
// Sink Connector — S3
{
  "name": "s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "4",
    "topics": "orders",
    "s3.region": "us-east-1",
    "s3.bucket.name": "data-lake-raw",
    "s3.part.size": "67108864",
    "flush.size": "10000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "'year'=YYYY/'month'=MM/'day'=dd",
    "locale": "en_US",
    "timezone": "UTC"
  }
}
```

### KRaft Mode (sem ZooKeeper)

A partir do Kafka 3.3, KRaft é produção-ready:

```properties
# server.properties (KRaft)
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093
listeners=PLAINTEXT://kafka-1:9092,CONTROLLER://kafka-1:9093
advertised.listeners=PLAINTEXT://kafka-1:9092
log.dirs=/var/lib/kafka/data
```

```bash
# Inicializar cluster KRaft (sem ZooKeeper)
kafka-storage.sh random-uuid  # gera cluster ID
kafka-storage.sh format -t <cluster-id> -c server.properties
kafka-server-start.sh server.properties
```

### Log Compaction

```bash
# Topic com compaction — mantém apenas o último valor por key
kafka-topics.sh --create \
  --topic customer-profiles \
  --partitions 6 \
  --config cleanup.policy=compact \
  --config min.compaction.lag.ms=3600000 \
  --config delete.retention.ms=86400000 \
  --bootstrap-server kafka:9092
```

---

## Gotchas

> [!bug] Consumer Lag Monitoring
> Lag acumulando indica que consumers não conseguem acompanhar a taxa de produção. Monitore com `kafka-consumer-groups.sh --describe` ou Kafka UI. Soluções: aumentar partições, adicionar consumers, otimizar processamento.

> [!warning] Message Ordering
> Kafka garante ordem apenas **dentro de uma partição**. Se você precisa de ordem global, use um topic com 1 partição (mas perde paralelismo) ou inclua sequence numbers nos eventos.

> [!caution] Large Messages
> O tamanho padrão máximo de mensagem é 1MB. Para payloads maiores, use o padrão **Claim Check**: armazene o dado no S3/MinIO e produza apenas a referência no Kafka.

---

## Snippets

### Kafka Streams API

```java
// Java — Kafka Streams
StreamsBuilder builder = new StreamsBuilder();

KStream<String, Order> orders = builder.stream("orders");

KTable<String, Long> orderCounts = orders
    .filter((key, order) -> order.getStatus() == OrderStatus.PAID)
    .groupBy((key, order) -> order.getCustomerId())
    .count(Materialized.as("order-counts-store"));

orderCounts.toStream().to("customer-order-counts");
```

### Docker Compose (KRaft)

```yaml
# docker-compose.yml
services:
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_LISTENERS: "PLAINTEXT://kafka:9092,CONTROLLER://kafka:9093"
      KAFKA_ADVERTISED_LISTENERS: "PLAINTEXT://localhost:9092"
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
    ports:
      - "9092:9092"
```

---

## References

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Developer — Kafka Tutorials](https://developer.confluent.io/tutorials/)
- [Debezium CDC with Kafka](https://debezium.io/documentation/)

---

## Related

- [[flink]] — processamento stateful de streams Kafka
- [[event-driven]] — padrões arquiteturais baseados em eventos
- [[messaging-patterns]] — pub/sub, CDC, CQRS com Kafka
- [[docker]] — deploy local com Docker Compose
- [[kubernetes-basics]] — Kafka no K8s com Strimzi Operator
- [[spark]] — Spark Structured Streaming consume de Kafka
