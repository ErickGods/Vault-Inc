---
tags: [skill, data-engineering, flink]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Flink, Apache Flink]
---

# Apache Flink

## Overview

Apache Flink é um engine de processamento de streams stateful e fault-tolerant. Diferente do [[spark]] Structured Streaming (micro-batch), Flink processa eventos **verdadeiramente em tempo real** (record-at-a-time). É ideal para latência sub-segundo, complex event processing e pipelines stateful que consomem de [[kafka]].

> [!important] Flink vs Spark Streaming
> Spark Structured Streaming usa micro-batches (100ms-1s de latência). Flink processa cada evento individualmente com latência tipicamente < 10ms. Para use cases que exigem latência real de milissegundos ou state complexo, Flink é a escolha.

---

## Core Concepts

### DataStream API

```python
# PyFlink — DataStream API
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy, Duration

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)
env.enable_checkpointing(60000)  # checkpoint a cada 60s

# Source: Kafka
kafka_source = (
    KafkaSource.builder()
    .set_bootstrap_servers("kafka:9092")
    .set_topics("orders")
    .set_group_id("flink-processor")
    .set_starting_offsets(KafkaOffsetsInitializer.earliest())
    .set_value_only_deserializer(SimpleStringSchema())
    .build()
)

stream = env.from_source(
    source=kafka_source,
    watermark_strategy=WatermarkStrategy
        .for_bounded_out_of_orderness(Duration.of_seconds(5))
        .with_timestamp_assigner(lambda event, _: parse_timestamp(event)),
    source_name="KafkaOrdersSource",
)

# Transformações
processed = (
    stream
    .map(lambda x: json.loads(x))
    .filter(lambda order: order["status"] == "PAID")
    .key_by(lambda order: order["customer_id"])
)

env.execute("Orders Processing Job")
```

### Windowing

Flink oferece três tipos principais de janelas:

```python
from pyflink.datastream.window import TumblingEventTimeWindows, SlidingEventTimeWindows, SessionEventTimeWindows
from pyflink.common import Time

# Tumbling Window — 5 minutos sem sobreposição
tumbling = (
    keyed_stream
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(SumAggregator())
)

# Sliding Window — janela de 10min que desliza a cada 2min
sliding = (
    keyed_stream
    .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(2)))
    .reduce(lambda a, b: merge_orders(a, b))
)

# Session Window — agrupa eventos com gap < 30min de inatividade
session = (
    keyed_stream
    .window(SessionEventTimeWindows.with_gap(Time.minutes(30)))
    .process(SessionWindowProcessor())
)
```

> [!info] Event Time vs Processing Time
> - **Event Time**: timestamp no evento (recomendado). Handles out-of-order events com watermarks.
> - **Processing Time**: clock do sistema. Simples mas não-determinístico — reprocessamento pode ter resultados diferentes.

### State Management

```python
from pyflink.datastream import KeyedProcessFunction
from pyflink.datastream.state import ValueStateDescriptor, MapStateDescriptor
from pyflink.common.typeinfo import Types

class OrderEnrichmentFunction(KeyedProcessFunction):
    def open(self, runtime_context):
        # Estado por key (customer_id)
        self.order_count = runtime_context.get_state(
            ValueStateDescriptor("order_count", Types.INT())
        )
        self.order_history = runtime_context.get_map_state(
            MapStateDescriptor("order_history", Types.STRING(), Types.FLOAT())
        )

    def process_element(self, order, ctx):
        count = self.order_count.value() or 0
        count += 1
        self.order_count.update(count)

        self.order_history.put(order["order_id"], order["amount"])

        # Emite evento enriquecido
        yield {**order, "lifetime_orders": count}

        # Timer para limpar estado antigo após 24h
        ctx.timer_service().register_event_time_timer(
            ctx.timestamp() + 86_400_000
        )

    def on_timer(self, timestamp, ctx):
        self.order_count.clear()
        self.order_history.clear()
```

### Checkpointing (Exactly-Once)

```python
from pyflink.datastream import CheckpointingMode
from pyflink.datastream.checkpoint_config import ExternalizedCheckpointCleanup

checkpoint_config = env.get_checkpoint_config()
checkpoint_config.set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
checkpoint_config.set_min_pause_between_checkpoints(30000)  # 30s entre checkpoints
checkpoint_config.set_checkpoint_timeout(120000)  # timeout 2min
checkpoint_config.set_max_concurrent_checkpoints(1)
checkpoint_config.enable_externalized_checkpoints(
    ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
)

# State backend — RocksDB para state grande (spills to disk)
env.set_state_backend(EmbeddedRocksDBStateBackend())
env.get_checkpoint_config().set_checkpoint_storage(
    "s3://flink-checkpoints/job-name/"
)
```

---

## Patterns

### Table API e Flink SQL

```python
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

settings = EnvironmentSettings.in_streaming_mode()
t_env = StreamTableEnvironment.create(env, environment_settings=settings)

# Definir tabela Kafka como source
t_env.execute_sql("""
    CREATE TABLE orders (
        order_id    STRING,
        customer_id STRING,
        amount      DOUBLE,
        status      STRING,
        event_time  TIMESTAMP(3),
        WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'orders',
        'properties.bootstrap.servers' = 'kafka:9092',
        'format' = 'json',
        'scan.startup.mode' = 'earliest-offset'
    )
""")

# Definir sink — Iceberg / Delta Lake
t_env.execute_sql("""
    CREATE TABLE silver_orders (
        customer_id STRING,
        window_start TIMESTAMP(3),
        window_end   TIMESTAMP(3),
        total_revenue DOUBLE,
        order_count  BIGINT
    ) WITH (
        'connector' = 'iceberg',
        'catalog-name' = 'hive_catalog',
        'database-name' = 'silver',
        'table-name' = 'orders_aggregated'
    )
""")

# Query com window function
t_env.execute_sql("""
    INSERT INTO silver_orders
    SELECT
        customer_id,
        TUMBLE_START(event_time, INTERVAL '5' MINUTE) AS window_start,
        TUMBLE_END(event_time, INTERVAL '5' MINUTE)   AS window_end,
        SUM(amount)   AS total_revenue,
        COUNT(*)      AS order_count
    FROM orders
    WHERE status = 'PAID'
    GROUP BY customer_id, TUMBLE(event_time, INTERVAL '5' MINUTE)
""")
```

### Complex Event Processing (CEP)

```python
from pyflink.cep import CEP, Pattern
from pyflink.cep.pattern_select_function import PatternSelectFunction

# Detectar fraude: 3+ transações > $500 em menos de 1 minuto
fraud_pattern = (
    Pattern.begin("first")
        .where(lambda event: event["amount"] > 500)
    .next("second")
        .where(lambda event: event["amount"] > 500)
    .next("third")
        .where(lambda event: event["amount"] > 500)
    .within(Time.minutes(1))
)

pattern_stream = CEP.pattern(
    keyed_stream.key_by(lambda e: e["card_id"]),
    fraud_pattern,
)

fraud_alerts = pattern_stream.select(FraudAlertFunction())
fraud_alerts.add_sink(kafka_fraud_sink)
```

### Deployment Modes

| Mode | Uso | Recursos |
|------|-----|----------|
| Session | Desenvolvimento, múltiplos jobs | Cluster compartilhado |
| Per-Job | Produção, isolamento | Cluster por job (depreciado) |
| Application | Produção moderna, K8s | JobManager por aplicação |

```bash
# Application mode no Kubernetes
flink run-application \
  --target kubernetes-application \
  -Dkubernetes.cluster-id=flink-fraud-detector \
  -Dkubernetes.container.image=my-registry/flink-fraud:1.18 \
  -Dkubernetes.namespace=flink-jobs \
  -Dtaskmanager.numberOfTaskSlots=4 \
  local:///opt/flink/usrlib/fraud-detector.jar
```

---

## Gotchas

> [!bug] Watermark Lag
> Se o `boundedOutOfOrderness` for muito pequeno, eventos atrasados serão descartados como **late data**. Se for muito grande, aumenta a latência do processamento. Monitore o watermark lag no Flink UI.

> [!warning] RocksDB State Backend
> O state backend RocksDB é essencial para jobs com state grande (> RAM disponível). Mas adiciona overhead de serialização/deserialização. Use `HashMap` state backend apenas para protótipos ou state pequeno.

> [!caution] Checkpoint Alignment
> Em EXACTLY_ONCE, barriers de checkpoint devem se alinhar em todos os inputs de um operador. Em fontes com skew de throughput, isso pode causar **checkpoint alignment stall**. Use UNALIGNED_CHECKPOINTS para reduzir a latência.

---

## Snippets

### Ler de [[data-lake-patterns]] (Parquet via FileSystem)

```python
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat

file_source = (
    FileSource.for_record_stream_format(
        StreamFormat.text_line_format(),
        "s3a://data-lake/bronze/events/",
    )
    .monitor_continuously(Duration.of_seconds(30))
    .build()
)

stream = env.from_source(file_source, WatermarkStrategy.no_watermarks(), "S3 Source")
```

---

## References

- [Flink Documentation — DataStream API](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/overview/)
- [Flink Documentation — Checkpointing](https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/checkpoints/)
- [Flink SQL Cookbook](https://flink.apache.org/2020/07/28/flink-sql-cookbook.html)

---

## Related

- [[kafka]] — fonte principal de eventos para jobs Flink
- [[spark]] — comparação: micro-batch vs true streaming
- [[python]] — PyFlink para desenvolvimento em Python
- [[docker]] — deploy local com Flink Docker image
- [[data-lake-patterns]] — Flink como writer para Iceberg/Delta
