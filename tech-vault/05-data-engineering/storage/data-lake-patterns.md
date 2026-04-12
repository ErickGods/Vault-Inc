---
tags: [skill, data-engineering, data-lake]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Data Lake, Lakehouse]
---

# Data Lake Patterns

## Overview

Data Lake é um repositório centralizado que armazena dados em formato bruto em escala. A evolução moderna é o **Lakehouse**: combina o armazenamento econômico de um data lake com as garantias ACID e capacidades analíticas de um data warehouse. Ferramentas como [[delta-lake]], Apache Iceberg e Apache Hudi implementam o padrão lakehouse sobre object storage (S3, GCS, ADLS).

> [!important] Lakehouse vs Data Warehouse vs Data Lake
> - **Data Lake**: armazenamento barato, sem estrutura, sem garantias ACID, schema-on-read
> - **Data Warehouse**: ACID, performance, caro, schema-on-write, difícil de escalar
> - **Lakehouse**: ACID sobre object storage, schema evolution, streaming + batch, open formats

---

## Core Concepts

### Medallion Architecture (Bronze / Silver / Gold)

```
S3 Bucket: s3://company-data-lake/
├── bronze/                    # Raw — cópia exata da fonte
│   ├── orders/
│   │   └── year=2026/month=04/day=05/
│   │       └── orders_20260405_143022.parquet
│   └── customers/
│
├── silver/                    # Cleaned — validado, normalizado, deduplicado
│   ├── orders/
│   │   └── _delta_log/        # Delta Lake transaction log
│   │   └── part-0000.parquet
│   └── customers/
│
└── gold/                      # Aggregated — business-ready, otimizado para leitura
    ├── daily_revenue/
    ├── customer_ltv/
    └── product_metrics/
```

**Bronze** — ingestão idempotente, sem transformação:
- Dados chegam como vieram da fonte (JSON, CSV, Avro)
- Incluir metadados de ingestão: `_ingest_ts`, `_source_file`, `_pipeline_run_id`
- Nunca deletar; apenas adicionar

**Silver** — qualidade e conformidade:
- Validação de schema e tipos
- Deduplicação por chave natural
- Padronização de formatos (datas, moedas, strings)
- Filtering de registros inválidos (com quarentena)

**Gold** — modelos analíticos:
- Agregações específicas por domínio de negócio
- Otimizado para ferramentas BI (Tableau, Power BI, Superset)
- Pode ter [[dbt]] models como camada de transformação

### File Formats

| Formato | Encoding | Melhor para | Compressão | Schema Evolution |
|---------|----------|-------------|------------|-----------------|
| **Parquet** | Colunar | Analytics OLAP | Excelente | Compatibilidade backward |
| **ORC** | Colunar | Hive, Spark | Muito boa | Limitada |
| **Avro** | Row-based | Streaming, CDC | Boa | Excelente (Schema Registry) |
| **Delta** | Parquet + log | Lakehouse ACID | Excelente | Full schema evolution |
| **Iceberg** | Parquet/ORC + metadata | Multi-engine | Excelente | Full schema evolution |

```python
# Escrevendo Parquet com Snappy — padrão otimizado
df.write.mode("overwrite") \
    .option("compression", "snappy") \
    .option("maxRecordsPerFile", 1_000_000) \
    .partitionBy("year", "month", "day") \
    .parquet("s3://data-lake/silver/orders/")
```

### Partitioning Strategies

```python
# Particionamento por data — mais comum para dados temporais
df.write.partitionBy("year", "month", "day").parquet(path)
# Resultado: s3://bucket/year=2026/month=04/day=05/part-0000.parquet

# CUIDADO: over-partitioning cria "small files problem"
# Regra de ouro: partições de ~128MB a 1GB cada

# Z-ORDER para queries multi-dimensionais (Delta Lake)
spark.sql("""
    OPTIMIZE delta.`s3://data-lake/silver/orders`
    ZORDER BY (customer_id, created_at)
""")

# Hive-style vs. Hidden partitioning (Iceberg)
# Iceberg suporta partition transforms: year(), month(), day(), hour(), bucket(), truncate()
spark.sql("""
    CREATE TABLE catalog.silver.orders
    USING iceberg
    PARTITIONED BY (days(created_at), bucket(16, customer_id))
    ...
""")
```

> [!warning] Small Files Problem
> Partições com muitos arquivos pequenos (< 10MB) degradam performance massivamente. Cada arquivo = uma operação de metadados no S3. Use `OPTIMIZE` (Delta) ou `rewrite_data_files` (Iceberg) periodicamente.

### Schema Evolution

```python
# Adicionando coluna — operação segura (backward compatible)
df_new = df.withColumn("discount_pct", lit(0.0))
df_new.write.option("mergeSchema", "true").mode("append") \
    .format("delta").save(path)

# Renomear coluna — requer schema migration explícita
spark.sql("ALTER TABLE silver.orders RENAME COLUMN amt TO amount")

# Evoluindo schema com [[dbt]] (via contract)
# schema.yml
# models:
#   - name: orders
#     config:
#       contract:
#         enforced: true
#     columns:
#       - name: order_id
#         data_type: varchar
#         constraints:
#           - type: not_null
#           - type: unique
```

---

## Patterns

### Data Catalog

**Hive Metastore** — catálogo tradicional, amplamente suportado:
```python
spark = SparkSession.builder \
    .config("spark.sql.warehouse.dir", "s3://data-lake/warehouse/") \
    .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
    .enableHiveSupport() \
    .getOrCreate()

spark.sql("SHOW DATABASES")
spark.sql("DESCRIBE EXTENDED silver.orders")
```

**Unity Catalog (Databricks)** — governance unificado:
```sql
-- 3-level namespace: catalog.schema.table
CREATE CATALOG prod_catalog;
CREATE SCHEMA prod_catalog.silver;

-- Row-level security
CREATE ROW FILTER pii_filter ON prod_catalog.silver.customers
    USING (current_user() IN ('admin@company.com') OR country = 'BR');

-- Column masking
ALTER TABLE prod_catalog.silver.customers
    ALTER COLUMN cpf SET MASK pii_mask_function;
```

**Apache Iceberg** — open table format, multi-engine:
```python
# Spark + Iceberg
spark = SparkSession.builder \
    .config("spark.sql.catalog.hive_prod", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.hive_prod.type", "hive") \
    .config("spark.sql.catalog.hive_prod.uri", "thrift://hive-metastore:9083") \
    .getOrCreate()

spark.sql("""
    CREATE TABLE hive_prod.silver.orders (
        order_id    STRING NOT NULL,
        customer_id STRING,
        amount      DOUBLE,
        created_at  TIMESTAMP
    )
    USING iceberg
    PARTITIONED BY (days(created_at))
""")
```

### Data Governance

```python
# Exemplo de Data Quality check antes de promover Bronze -> Silver
from great_expectations.dataset import SparkDFDataset

def validate_bronze_orders(df):
    ge_df = SparkDFDataset(df)

    results = ge_df.expect_column_values_to_not_be_null("order_id")
    assert results["success"], "order_id contém nulos"

    results = ge_df.expect_column_values_to_be_between("amount", 0, 1_000_000)
    assert results["success"], "amount fora do range esperado"

    results = ge_df.expect_column_values_to_match_regex(
        "customer_id", r"^[A-Z0-9]{8}$"
    )
    assert results["success"], "customer_id com formato inválido"
```

---

## Gotchas

> [!bug] Partition Pruning Miss
> Se o filtro usa uma função sobre a coluna de partição (`WHERE year(created_at) = 2026`), o Spark não consegue fazer partition pruning. Use `WHERE year = 2026 AND month = 4` com colunas de partição explícitas.

> [!warning] S3 Eventual Consistency
> Operações de listagem no S3 eram eventually consistent (pré-2020). Com S3 strong consistency (desde 2020), isso não é mais um problema — mas ainda relevante para outros object stores (GCS, MinIO).

> [!tip] Compaction Scheduling
> Agende jobs de compaction e vacuum fora do horário de pico. Delta Lake `OPTIMIZE` + `VACUUM` e Iceberg `rewrite_data_files` + `expire_snapshots` devem rodar diariamente em tabelas com alta escrita.

---

## Snippets

### Leitura Eficiente com [[duckdb]]

```sql
-- DuckDB lê Parquet diretamente do S3
SET s3_region='us-east-1';
SET s3_access_key_id='AKIA...';
SET s3_secret_access_key='...';

SELECT
    DATE_TRUNC('day', created_at) AS day,
    SUM(amount) AS revenue
FROM read_parquet('s3://data-lake/silver/orders/year=2026/**/*.parquet')
WHERE year = 2026 AND month = 4
GROUP BY 1
ORDER BY 1;
```

---

## References

- [Databricks — Lakehouse Architecture](https://www.databricks.com/glossary/data-lakehouse)
- [Apache Iceberg — Table Spec](https://iceberg.apache.org/spec/)
- [Delta Lake Documentation](https://docs.delta.io/)

---

## Related

- [[delta-lake]] — implementação ACID lakehouse da Databricks
- [[s3-storage-patterns]] — padrões de armazenamento no S3
- [[dbt]] — transformações SQL na camada silver/gold
- [[spark]] — engine principal para processamento no data lake
- [[duckdb]] — consultas analíticas ad-hoc sobre arquivos Parquet
