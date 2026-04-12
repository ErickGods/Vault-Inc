---
tags: [skill, data-engineering, delta-lake]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Delta Lake]
---

# Delta Lake

## Overview

Delta Lake é um open-source storage layer que adiciona garantias ACID a data lakes em object storage (S3, GCS, ADLS). Usa um **transaction log** (série de arquivos JSON em `_delta_log/`) para rastrear todas as operações — inserts, updates, deletes, schema changes. É o formato nativo do [[spark]] Databricks e funciona com qualquer engine Spark.

> [!important] Delta Lake Architecture
> Cada tabela Delta é um diretório com arquivos Parquet + `_delta_log/`. O log contém **commits** sequenciais (00000000000000000000.json, 00000000000000000001.json, ...). Cada commit lista quais arquivos foram adicionados/removidos — isso habilita ACID sem lock distribuído.

---

## Core Concepts

### ACID Transactions

```python
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Escrita atômica — ou tudo funciona, ou nada é commitado
(
    df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .partitionBy("year", "month")
    .save("s3://data-lake/silver/orders/")
)

# Leitura isolada — snapshot consistente mesmo durante escritas concorrentes
df = spark.read.format("delta").load("s3://data-lake/silver/orders/")
```

### Time Travel

```python
# Leitura por versão
df_v0 = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("s3://data-lake/silver/orders/")

# Leitura por timestamp
df_yesterday = spark.read.format("delta") \
    .option("timestampAsOf", "2026-04-04 00:00:00") \
    .load("s3://data-lake/silver/orders/")

# Via SQL
spark.sql("""
    SELECT * FROM silver.orders
    VERSION AS OF 10
""")

spark.sql("""
    SELECT * FROM silver.orders
    TIMESTAMP AS OF '2026-04-04'
""")

# Histórico completo
delta_table = DeltaTable.forPath(spark, "s3://data-lake/silver/orders/")
delta_table.history().select("version", "timestamp", "operation", "operationParameters").show()
```

### Schema Enforcement e Evolution

```python
# Schema enforcement — por padrão, Delta rejeita schemas incompatíveis
try:
    df_wrong_schema.write.format("delta").mode("append").save(path)
except Exception as e:
    print(f"Schema inválido: {e}")

# Schema evolution — merge automático de colunas novas
df_with_new_col.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save(path)

# Alteração explícita de schema
spark.sql("ALTER TABLE silver.orders ADD COLUMNS (discount_pct DOUBLE AFTER amount)")
spark.sql("ALTER TABLE silver.orders CHANGE COLUMN status status STRING AFTER amount")
spark.sql("ALTER TABLE silver.orders DROP COLUMN deprecated_field")
```

### MERGE (Upsert)

MERGE é a operação mais poderosa do Delta Lake — implementa SCD Type 1, Type 2, e CDC:

```python
# SCD Type 1 — Upsert simples (sobrescreve)
target = DeltaTable.forName(spark, "silver.customers")

target.alias("target").merge(
    source=df_updates.alias("source"),
    condition="target.customer_id = source.customer_id",
).whenMatchedUpdate(set={
    "name":       "source.name",
    "email":      "source.email",
    "updated_at": "source.updated_at",
}).whenNotMatchedInsertAll() \
 .execute()

# CDC — insere novos, atualiza existentes, deleta removidos
target.alias("t").merge(
    source=cdc_df.alias("s"),
    condition="t.order_id = s.order_id",
).whenMatchedDelete(
    condition="s.operation = 'DELETE'"
).whenMatchedUpdate(
    condition="s.operation = 'UPDATE'",
    set={"status": "s.status", "updated_at": "s.updated_at"},
).whenNotMatchedInsert(
    condition="s.operation = 'INSERT'",
    values={"order_id": "s.order_id", "amount": "s.amount", "status": "s.status"},
).execute()
```

---

## Patterns

### OPTIMIZE e Z-ORDER

```python
# OPTIMIZE — compacta small files em arquivos de ~1GB
spark.sql("OPTIMIZE silver.orders")

# Z-ORDER — co-localiza dados correlacionados para skip eficiente
spark.sql("""
    OPTIMIZE silver.orders
    ZORDER BY (customer_id, created_at)
""")

# Resultado: queries com filtro em customer_id ou created_at
# pulam arquivos inteiros via data skipping (min/max statistics)
```

> [!tip] Z-ORDER Escolha de Colunas
> Z-ORDER é mais eficaz em colunas com alta cardinalidade usadas em filtros frequentes. Não use em colunas de partição (já otimizadas por particionamento). Limite a 2-3 colunas — mais do que isso não melhora.

### Change Data Feed (CDF)

```python
# Habilitar CDF na tabela
spark.sql("""
    ALTER TABLE silver.orders
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Ler apenas mudanças entre versões (para pipelines downstream)
changes = spark.read.format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 10) \
    .option("endingVersion", 20) \
    .table("silver.orders")

# _change_type: insert, update_preimage, update_postimage, delete
changes.filter("_change_type IN ('insert', 'update_postimage')") \
    .drop("_change_type", "_commit_version", "_commit_timestamp") \
    .write.format("delta").mode("append").save("s3://gold/orders/")
```

### UniForm — Iceberg Compatibility

```python
# Delta com UniForm: leitura transparente por engines Iceberg (Trino, Athena, etc.)
spark.sql("""
    CREATE TABLE silver.orders (
        order_id    STRING NOT NULL,
        customer_id STRING,
        amount      DOUBLE
    )
    USING delta
    TBLPROPERTIES (
        'delta.universalFormat.enabledFormats' = 'iceberg'
    )
""")

# A partir deste ponto, engines Iceberg lêem a tabela sem conversão
# Trino, Athena, DuckDB com iceberg extension acessam diretamente
```

### VACUUM

```python
# Remove arquivos não referenciados por nenhuma versão ativa
# Default retention: 7 dias (168 horas)
spark.sql("VACUUM silver.orders RETAIN 168 HOURS")

# DRY RUN — lista arquivos que seriam deletados
spark.sql("VACUUM silver.orders RETAIN 168 HOURS DRY RUN")

# CUIDADO: reduzir retention abaixo do default desabilita time travel para versões antigas
# Não use RETAIN 0 HOURS em produção — pode causar inconsistência com readers concorrentes
```

---

## Gotchas

> [!bug] Concurrent Writes — ConcurrentModificationException
> Escritas concorrentes podem gerar conflito se afetam as mesmas partições. Delta usa **Optimistic Concurrency Control**: tenta o commit, e se outro writer commitou primeiro na mesma partição, falha com retry. Configure `spark.databricks.delta.retryWriteConflict.limit`.

> [!warning] Log Checkpoints
> A cada 10 commits, Delta cria um checkpoint Parquet do estado atual do log. Sem checkpoints, leitura do log começa do início e fica cada vez mais lenta. Garanta que o processo tenha permissão de escrita no `_delta_log/`.

> [!caution] Delta vs Iceberg Escolha
> Delta Lake: ecossistema Spark/Databricks, melhor suporte para MERGE complexo, Z-ORDER. Iceberg: mais portável (suporte nativo em Trino, Athena, Flink), hidden partitioning, partition evolution. Para ambientes multi-engine, prefira Iceberg.

---

## Snippets

### Criar Tabela Gerenciada

```sql
-- SQL
CREATE TABLE IF NOT EXISTS silver.orders (
    order_id     STRING NOT NULL,
    customer_id  STRING NOT NULL,
    amount       DOUBLE,
    status       STRING,
    created_at   TIMESTAMP,
    updated_at   TIMESTAMP
)
USING delta
PARTITIONED BY (DATE(created_at))
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact'   = 'true',
    'delta.enableChangeDataFeed'       = 'true',
    'delta.columnMapping.mode'         = 'name'  -- habilita DROP/RENAME COLUMN
);
```

### Leitura com [[duckdb]]

```sql
-- DuckDB lê Delta nativo via extensão
INSTALL delta;
LOAD delta;

SELECT COUNT(*), SUM(amount)
FROM delta_scan('s3://data-lake/silver/orders/');
```

---

## References

- [Delta Lake Documentation](https://docs.delta.io/latest/index.html)
- [Delta Lake — MERGE INTO Guide](https://docs.delta.io/latest/delta-update.html)
- [Delta UniForm](https://docs.delta.io/latest/delta-uniform.html)

---

## Related

- [[data-lake-patterns]] — medallion architecture e contexto do lakehouse
- [[spark]] — engine principal para operações Delta
- [[dbt]] — transformações sobre tabelas Delta
- [[s3-storage-patterns]] — configuração de acesso ao S3 para Delta
- [[duckdb]] — consultas analíticas diretas em tabelas Delta
