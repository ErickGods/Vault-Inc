---
tags: [skill, data-engineering, spark]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Spark, Apache Spark, PySpark]
---

# Apache Spark / PySpark

## Overview

Apache Spark é um engine de processamento distribuído de dados em memória. Suporta batch, streaming estruturado, SQL, ML e grafos. O [[python]] API (PySpark) é o mais popular, mas Spark roda em Scala, Java e R. É o engine principal para processamento em [[data-lake-patterns]] e integração com [[delta-lake]].

> [!important] Spark Execution Model
> Spark compila operações em um **DAG de stages**. Cada stage é um conjunto de transformações sem shuffle. O **Catalyst optimizer** reescreve o plano lógico em um plano físico otimizado. **Tungsten** gerencia memória off-heap e geração de bytecode. **AQE** ajusta o plano em runtime baseado em estatísticas reais.

---

## Core Concepts

### SparkSession e Configuração

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("ETL Pipeline")
    .master("k8s://https://k8s-api:6443")  # ou "local[*]", "yarn"
    .config("spark.executor.memory", "8g")
    .config("spark.executor.cores", "4")
    .config("spark.executor.instances", "10")
    .config("spark.sql.adaptive.enabled", "true")       # AQE
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)
```

### RDDs vs DataFrames

```python
# RDD — baixo nível, evitar em código novo
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])
result = rdd.map(lambda x: x * 2).filter(lambda x: x > 4).collect()

# DataFrame — API de alto nível, usa Catalyst + Tungsten
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

schema = StructType([
    StructField("order_id",    StringType(),    nullable=False),
    StructField("customer_id", StringType(),    nullable=True),
    StructField("amount",      DoubleType(),    nullable=True),
    StructField("created_at",  TimestampType(), nullable=True),
])

df = spark.read.schema(schema).parquet("s3://data-lake/bronze/orders/")

# Transformações (lazy — não executam até uma action)
result = (
    df
    .filter(F.col("amount") > 0)
    .filter(F.col("order_id").isNotNull())
    .withColumn("year",  F.year("created_at"))
    .withColumn("month", F.month("created_at"))
    .withColumn("amount_brl", F.col("amount") * F.lit(5.0))
    .dropDuplicates(["order_id"])
)

# Action — dispara a execução
result.write.format("delta").mode("overwrite").partitionBy("year", "month") \
    .save("s3://data-lake/silver/orders/")
```

### Spark SQL

```python
# Registrar DataFrame como view temporária
df.createOrReplaceTempView("orders")

# Executar SQL
revenue = spark.sql("""
    SELECT
        DATE_TRUNC('month', created_at) AS month,
        customer_id,
        COUNT(*)        AS order_count,
        SUM(amount)     AS revenue,
        AVG(amount)     AS avg_order,
        RANK() OVER (
            PARTITION BY DATE_TRUNC('month', created_at)
            ORDER BY SUM(amount) DESC
        ) AS revenue_rank
    FROM orders
    WHERE status = 'PAID'
    GROUP BY 1, 2
""")

revenue.show(20, truncate=False)
revenue.explain("formatted")  # mostrar plano de execução
```

### Structured Streaming

```python
from pyspark.sql.streaming import StreamingQuery

# Source: Kafka
kafka_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "orders")
    .option("startingOffsets", "latest")
    .option("kafka.group.id", "spark-streaming-consumer")
    .load()
)

# Parse JSON payload
from pyspark.sql.types import StructType, StringType, DoubleType
from pyspark.sql import functions as F

order_schema = StructType() \
    .add("order_id",    StringType()) \
    .add("customer_id", StringType()) \
    .add("amount",      DoubleType()) \
    .add("event_time",  StringType())

parsed = (
    kafka_stream
    .select(F.from_json(F.col("value").cast("string"), order_schema).alias("data"))
    .select("data.*")
    .withColumn("event_time", F.to_timestamp("event_time"))
    .withWatermark("event_time", "10 minutes")
)

# Aggregação com janela temporal
windowed = (
    parsed
    .groupBy(
        F.window("event_time", "5 minutes"),
        "customer_id"
    )
    .agg(
        F.count("*").alias("order_count"),
        F.sum("amount").alias("total_amount"),
    )
)

# Sink: Delta Lake
query: StreamingQuery = (
    windowed.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3://checkpoints/orders-stream/")
    .trigger(processingTime="30 seconds")
    .start("s3://data-lake/gold/orders_windowed/")
)

query.awaitTermination()
```

---

## Patterns

### Catalyst Optimizer e Predicate Pushdown

```python
# Spark tenta pushdown de filtros para a fonte de dados
# Parquet: filtros em colunas com statistics são aplicados durante leitura
df = (
    spark.read.parquet("s3://data-lake/silver/orders/")
    .filter(F.col("year") == 2026)      # partition pruning
    .filter(F.col("amount") > 1000)     # predicate pushdown ao Parquet
)

# Ver plano — confirme "PushedFilters" no Physical Plan
df.explain("extended")
```

### Broadcast Join

```python
# Broadcast join — evita shuffle para tabelas pequenas (< spark.sql.autoBroadcastJoinThreshold)
from pyspark.sql.functions import broadcast

small_lookup = spark.table("dim_product")  # ex: 10MB

result = orders.join(
    broadcast(small_lookup),
    on="product_id",
    how="left",
)

# Forçar broadcast via hint
result = orders.join(
    small_lookup.hint("broadcast"),
    on="product_id",
    how="left",
)
```

### AQE — Adaptive Query Execution

```python
# AQE habilitado (Spark 3.2+)
spark.conf.set("spark.sql.adaptive.enabled", "true")

# Coalesce automático de partições após shuffle
# Ex: se shuffle produziu 200 partições de 1MB cada,
# AQE reduz para 10 partições de 20MB — menos tasks, menos overhead

# Skew join: partições muito maiores que outras
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")

# Dynamic partition pruning (DPP) — elimina partições em runtime
result = large_fact.join(
    small_dim.filter(F.col("region") == "BR"),
    on="dim_key"
)
# Spark aplica o filtro de "region=BR" na tabela de fatos em runtime
```

### Cluster Management

```bash
# Kubernetes (spark-submit)
spark-submit \
  --master k8s://https://k8s-api:6443 \
  --deploy-mode cluster \
  --name etl-orders \
  --conf spark.kubernetes.container.image=my-registry/pyspark:3.5 \
  --conf spark.kubernetes.namespace=spark-jobs \
  --conf spark.executor.instances=10 \
  --conf spark.executor.memory=8g \
  --conf spark.executor.cores=4 \
  --conf spark.kubernetes.driver.request.cores=2 \
  --conf spark.kubernetes.executor.request.cores=4 \
  s3a://scripts/etl_orders.py

# YARN (Hadoop cluster)
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --queue high-priority \
  --num-executors 20 \
  --executor-memory 16g \
  etl_orders.py
```

### PySpark Patterns — UDFs e Pandas UDFs

```python
from pyspark.sql.functions import udf, pandas_udf
from pyspark.sql.types import StringType, DoubleType
import pandas as pd

# UDF Python (lento — serialização row-by-row)
@udf(returnType=StringType())
def categorize_order(amount: float) -> str:
    if amount > 10000: return "HIGH"
    elif amount > 1000: return "MEDIUM"
    return "LOW"

# Pandas UDF (vetorizado via Arrow — muito mais rápido)
@pandas_udf(DoubleType())
def apply_discount_vectorized(amounts: pd.Series, discounts: pd.Series) -> pd.Series:
    return amounts * (1 - discounts)

result = orders.withColumn(
    "discounted_amount",
    apply_discount_vectorized(F.col("amount"), F.col("discount_pct"))
)
```

> [!tip] UDF Performance
> Prefira built-in Spark functions (`F.col`, `F.when`, etc.) — são JVM-native e não têm overhead de serialização Python. Se precisar de lógica Python, use Pandas UDF (Arrow) em vez de UDF regular. UDF regular pode ser 10-100x mais lento que built-ins.

---

## Gotchas

> [!bug] Data Skew
> Se uma partição tem muito mais dados que as outras (ex: customer_id nulo em 30% dos registros), um executor fica sobrecarregado enquanto os outros terminam. Use `salting`: adicione um sufixo aleatório à key nula para distribuir.

> [!warning] Collect em Produção
> `.collect()` traz todos os dados para o driver. Em datasets grandes, causa OOM no driver. Use `.show()`, `.take(n)` ou salve direto no storage.

> [!caution] Shuffle Partitions
> O padrão `spark.sql.shuffle.partitions=200` é inadequado para a maioria dos jobs. Regra: `200MB por partição`. Em jobs com poucos dados, 200 partições de 1MB causam overhead massivo. AQE corrige isso automaticamente se habilitado.

---

## Snippets

### MLlib Básico

```python
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline

assembler = VectorAssembler(
    inputCols=["amount", "total_orders", "days_since_last_order"],
    outputCol="features"
)
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")
clf = RandomForestClassifier(
    featuresCol="scaled_features",
    labelCol="churn",
    numTrees=100,
    maxDepth=10,
)

pipeline = Pipeline(stages=[assembler, scaler, clf])
model = pipeline.fit(train_df)
predictions = model.transform(test_df)
```

### Integração com [[kafka]] — Streaming Write

```python
# Escrever resultado de streaming de volta ao Kafka
result.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "order-aggregates") \
    .option("checkpointLocation", "s3://checkpoints/kafka-write/") \
    .outputMode("update") \
    .start()
```

---

## References

- [Spark Documentation — Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [Spark Structured Streaming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [PySpark API Reference](https://spark.apache.org/docs/latest/api/python/index.html)

---

## Related

- [[python]] — PySpark API e desenvolvimento local
- [[kafka]] — source/sink para Spark Structured Streaming
- [[flink]] — alternativa para streaming com menor latência
- [[delta-lake]] — formato nativo para escritas ACID no Spark
- [[data-lake-patterns]] — Spark como engine de processamento no lakehouse
- [[dbt]] — dbt-spark para transformações declarativas no Spark
