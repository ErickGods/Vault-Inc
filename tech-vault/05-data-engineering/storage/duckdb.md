---
tags: [skill, data-engineering, duckdb]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [DuckDB]
---

# DuckDB

## Overview

DuckDB é um banco de dados OLAP **in-process** — sem servidor, sem configuração, zero dependências. Roda dentro do processo Python/R/Go como uma biblioteca. Executa SQL analítico sobre Parquet, CSV, JSON, Arrow e [[delta-lake]] diretamente em memória ou em arquivo local. É o "SQLite para analytics".

> [!important] DuckDB Use Cases
> DuckDB não é um substituto para [[postgresql]] em workloads OLTP. Ele brilha em: exploração de dados, transformações analíticas, substituição local do Spark para datasets < 100GB, e como engine SQL para [[data-lake-patterns]] em arquivos Parquet/Delta no S3.

---

## Core Concepts

### Instalação e Conexão

```python
pip install duckdb
# Com extensões
pip install duckdb 'duckdb[all]'
```

```python
import duckdb

# In-memory (temporário)
con = duckdb.connect()

# Persistido em arquivo
con = duckdb.connect("analytics.duckdb")

# Read-only (múltiplos leitores simultâneos)
con = duckdb.connect("analytics.duckdb", read_only=True)
```

### Leitura Direta de Arquivos

DuckDB lê arquivos sem importar dados — os arquivos **são** as tabelas:

```python
# Parquet — local ou S3
result = con.execute("""
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_spent
    FROM read_parquet('data/orders/**/*.parquet')
    WHERE YEAR(created_at) = 2026
    GROUP BY customer_id
    ORDER BY total_spent DESC
    LIMIT 100
""").df()

# CSV com inferência automática de schema
con.execute("""
    SELECT * FROM read_csv_auto('data/customers.csv', header=True)
    LIMIT 5
""")

# JSON
con.execute("""
    SELECT unnest(orders) AS order
    FROM read_json_auto('data/response.json')
""")

# Múltiplos arquivos com glob
con.execute("SELECT * FROM 'data/year=2026/month=*/day=*/*.parquet'")
```

### Extensions

```sql
-- Instalar e carregar extensões
INSTALL httpfs;    -- S3, HTTP, GCS
INSTALL delta;     -- Delta Lake
INSTALL iceberg;   -- Apache Iceberg
INSTALL postgres;  -- PostgreSQL scanner
INSTALL spatial;   -- PostGIS-like spatial

LOAD httpfs;
LOAD delta;
```

```python
# Configurar S3
con.execute("""
    SET s3_region     = 'us-east-1';
    SET s3_access_key_id     = 'AKIA...';
    SET s3_secret_access_key = 'secret';
""")

# Ler Delta Lake no S3
con.execute("""
    SELECT COUNT(*), AVG(amount)
    FROM delta_scan('s3://data-lake/silver/orders/')
""")

# Ler Iceberg
con.execute("""
    SELECT * FROM iceberg_scan('s3://data-lake/iceberg/orders/metadata/v2.metadata.json')
    LIMIT 10
""")
```

### Python API — Relation API

```python
# Relation API — lazy evaluation, não executa até ser materializado
rel = con.table("orders")  # tabela registrada

result = (
    rel
    .filter("amount > 100")
    .aggregate("customer_id, COUNT(*) AS cnt, SUM(amount) AS total", "customer_id")
    .order("total DESC")
    .limit(50)
)

# Materializar como diferentes formatos
df = result.df()           # pandas DataFrame
arrow = result.arrow()     # PyArrow Table
polars_df = result.pl()    # Polars DataFrame (duckdb >= 0.10)
result.show()              # print formatado
```

### Integração com Pandas e Polars

```python
import pandas as pd
import polars as pl

# Pandas -> DuckDB (sem cópia, via Arrow)
orders_pd = pd.read_parquet("orders.parquet")
result = con.execute("SELECT * FROM orders_pd WHERE amount > 500").df()

# Polars -> DuckDB
orders_pl = pl.read_parquet("orders.parquet")
result = con.execute("SELECT AVG(amount) FROM orders_pl").fetchone()[0]

# DuckDB -> Polars
polars_result = con.execute("SELECT * FROM delta_scan('s3://...')").pl()

# Registrar DataFrame como tabela virtual
con.register("temp_orders", orders_pd)
con.execute("CREATE TABLE filtered AS SELECT * FROM temp_orders WHERE year = 2026")
```

---

## Patterns

### Remote Files (S3, HTTP)

```python
# HTTP direto — útil para datasets públicos
con.execute("""
    SELECT * FROM read_parquet(
        'https://datasets.company.com/public/nyc_taxi_2026.parquet'
    )
    LIMIT 1000
""")

# Credenciais por provider
con.execute("""
    CREATE SECRET aws_secret (
        TYPE S3,
        PROVIDER CREDENTIAL_CHAIN,  -- usa ~/.aws/credentials ou IAM role
        REGION 'us-east-1'
    )
""")
```

### SQL Features Avançadas

```sql
-- Window functions
SELECT
    order_id,
    customer_id,
    amount,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY created_at
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_spent,
    PERCENT_RANK() OVER (PARTITION BY DATE_TRUNC('month', created_at)
                         ORDER BY amount DESC) AS percentile_in_month
FROM orders;

-- PIVOT nativo (DuckDB >= 0.8)
PIVOT orders
ON status
USING SUM(amount)
GROUP BY customer_id;

-- UNPIVOT
UNPIVOT monthly_sales
ON jan, fev, mar, apr
INTO NAME month VALUE sales;

-- ASOF JOIN — join temporal aproximado
SELECT t.customer_id, t.amount, p.price_at_time
FROM transactions t
ASOF JOIN prices p ON t.product_id = p.product_id
                   AND t.created_at >= p.effective_date;

-- Macro (UDF SQL)
CREATE MACRO normalize_amount(amt, currency) AS
    CASE currency
        WHEN 'BRL' THEN amt / 5.0
        WHEN 'EUR' THEN amt * 1.08
        ELSE amt
    END;
```

### Performance e Tuning

```python
# Configuração de performance
con.execute("""
    SET threads = 8;                       -- usar todos os cores
    SET memory_limit = '16GB';             -- limite de RAM
    SET temp_directory = '/tmp/duckdb/';   -- spill to disk se necessário
    SET enable_progress_bar = true;
""")

# Persistir resultado como Parquet (muito mais rápido que INSERT)
con.execute("""
    COPY (
        SELECT customer_id, SUM(amount) AS ltv
        FROM delta_scan('s3://data-lake/silver/orders/')
        GROUP BY customer_id
    ) TO 's3://data-lake/gold/customer_ltv.parquet'
    (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)
""")

# Criar índice (ART — Adaptive Radix Tree)
con.execute("CREATE INDEX idx_customer ON orders(customer_id)")
```

> [!tip] DuckDB vs Spark para ETL Local
> Para datasets que cabem em memória do seu laptop (ou servidor de dados de 64-128GB RAM), DuckDB é **10-100x mais rápido** que Spark e não requer cluster. Use Spark para datasets verdadeiramente distribuídos ou streaming.

---

## Gotchas

> [!bug] Single-Writer Limitation
> DuckDB suporta apenas **um writer por vez** (por arquivo de banco). Se múltiplos processos tentam escrever no mesmo arquivo `.duckdb`, apenas um terá acesso — os outros aguardam ou falham. Para concorrência, use `read_only=True` nos leitores.

> [!warning] In-Memory Limits
> Por padrão, DuckDB usa até 80% da RAM disponível. Para queries que excedem a memória, ele faz spill para disk (configurado por `temp_directory`). Monitore com `PRAGMA memory_usage`.

> [!caution] S3 e Credenciais
> Ao usar DuckDB em ambientes efêmeros (Lambda, containers), prefira `PROVIDER CREDENTIAL_CHAIN` para usar IAM roles em vez de hardcodar chaves. O `httpfs` extension suporta AWS STS e instance metadata.

---

## Snippets

### ETL Pipeline com DuckDB

```python
def run_etl(date: str):
    con = duckdb.connect()
    con.execute("LOAD httpfs; LOAD delta;")
    con.execute(f"SET s3_region='us-east-1'")

    # Extract + Transform em SQL
    con.execute(f"""
        CREATE TABLE silver_orders AS
        SELECT
            order_id,
            customer_id,
            ROUND(amount, 2)               AS amount,
            UPPER(status)                  AS status,
            CAST(created_at AS TIMESTAMP)  AS created_at,
            '{date}'::DATE                 AS partition_date
        FROM delta_scan('s3://data-lake/bronze/orders/')
        WHERE created_at::DATE = '{date}'::DATE
          AND order_id IS NOT NULL
    """)

    row_count = con.execute("SELECT COUNT(*) FROM silver_orders").fetchone()[0]

    # Load
    con.execute(f"""
        COPY silver_orders
        TO 's3://data-lake/silver/orders/date={date}/data.parquet'
        (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    return row_count
```

### Benchmark de Queries com [[postgresql]]

```python
# Comparar performance DuckDB vs PostgreSQL
import time

queries = {
    "duckdb": lambda: con.execute("SELECT COUNT(*), AVG(amount) FROM read_parquet('orders.parquet')").fetchone(),
    "postgres": lambda: pg_conn.execute("SELECT COUNT(*), AVG(amount) FROM orders").fetchone(),
}

for name, fn in queries.items():
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    print(f"{name}: {result} em {elapsed:.3f}s")
```

---

## References

- [DuckDB Documentation](https://duckdb.org/docs/)
- [DuckDB Extensions](https://duckdb.org/docs/extensions/overview)
- [DuckDB vs Spark — Benchmark](https://benchmark.clickhouse.com/)

---

## Related

- [[postgresql]] — OLTP database; DuckDB complementa para analytics
- [[python]] — API principal de uso do DuckDB
- [[delta-lake]] — DuckDB lê tabelas Delta via extensão nativa
- [[data-lake-patterns]] — DuckDB como engine analítico sobre data lake
- [[dbt]] — dbt suporta DuckDB como adapter para desenvolvimento local
