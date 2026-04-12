---
tags: [skill, data-engineering, dbt]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [dbt, dbt Core, dbt Cloud]
---

# dbt (data build tool)

## Overview

dbt é uma ferramenta de transformação que permite escrever lógica de transformação em SQL e gerenciá-la com boas práticas de engenharia de software: versionamento, testes, documentação e lineage automático. dbt **não move dados** — ele apenas executa SQL no warehouse/lake (BigQuery, Snowflake, Redshift, [[postgresql]], [[spark]], DuckDB).

> [!important] dbt Philosophy
> "Transform data in your warehouse, not your pipeline." dbt assume que os dados já estão no destino (EL foi feito por Fivetran, Airbyte, etc.) e foca exclusivamente no T do ELT.

---

## Core Concepts

### Models

Models são arquivos `.sql` que definem uma transformação. Por padrão, dbt os materializa como views:

```sql
-- models/silver/orders_cleaned.sql
{{
  config(
    materialized = 'table',
    schema       = 'silver',
    tags         = ['daily', 'orders'],
    post_hook    = "GRANT SELECT ON {{ this }} TO ROLE analyst_role"
  )
}}

WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}       -- referência a source declarada
),
validated AS (
    SELECT
        order_id,
        customer_id,
        ROUND(amount::NUMERIC, 2) AS amount,
        UPPER(TRIM(status))       AS status,
        created_at::TIMESTAMP     AS created_at
    FROM source
    WHERE order_id IS NOT NULL
      AND amount > 0
),
deduped AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at DESC) AS rn
    FROM validated
)
SELECT * EXCLUDE (rn) FROM deduped WHERE rn = 1
```

```sql
-- models/gold/customer_ltv.sql
-- {{ ref() }} cria dependência explícita e resolve o nome real da tabela
SELECT
    c.customer_id,
    c.name,
    c.email,
    o.total_orders,
    o.lifetime_value,
    o.avg_order_value,
    o.first_order_at,
    o.last_order_at
FROM {{ ref('customers_cleaned') }} c
LEFT JOIN (
    SELECT
        customer_id,
        COUNT(*)     AS total_orders,
        SUM(amount)  AS lifetime_value,
        AVG(amount)  AS avg_order_value,
        MIN(created_at) AS first_order_at,
        MAX(created_at) AS last_order_at
    FROM {{ ref('orders_cleaned') }}
    GROUP BY customer_id
) o USING (customer_id)
```

### Tests

```yaml
# models/silver/schema.yml
version: 2

sources:
  - name: raw
    database: raw_db
    schema: public
    tables:
      - name: orders
        loaded_at_field: _ingest_ts
        freshness:
          warn_after: {count: 6, period: hour}
          error_after: {count: 24, period: hour}

models:
  - name: orders_cleaned
    description: "Ordens validadas e deduplicadas"
    columns:
      - name: order_id
        description: "ID único da ordem"
        data_tests:
          - not_null
          - unique
      - name: status
        data_tests:
          - not_null
          - accepted_values:
              values: ['PENDING', 'PAID', 'CANCELLED', 'REFUNDED']
      - name: amount
        data_tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "> 0"
      - name: customer_id
        data_tests:
          - not_null
          - relationships:
              to: ref('customers_cleaned')
              field: customer_id
```

**Singular tests** — SQL customizado:

```sql
-- tests/assert_revenue_positive.sql
-- Falha se retornar qualquer linha (linhas = falhas)
SELECT
    DATE_TRUNC('day', created_at) AS day,
    SUM(amount)                   AS daily_revenue
FROM {{ ref('orders_cleaned') }}
GROUP BY 1
HAVING SUM(amount) < 0
```

### Macros (Jinja)

```sql
-- macros/generate_surrogate_key.sql
{% macro generate_surrogate_key(columns) %}
    MD5(CAST(CONCAT_WS('|',
        {% for col in columns %}
            COALESCE(CAST({{ col }} AS VARCHAR), '')
            {%- if not loop.last %},{% endif %}
        {% endfor %}
    ) AS VARCHAR))
{% endmacro %}

-- Uso em model
SELECT
    {{ generate_surrogate_key(['order_id', 'customer_id']) }} AS sk_order,
    *
FROM {{ ref('orders_cleaned') }}
```

```sql
-- macros/incremental_predicate.sql
{% macro get_incremental_start(column, lookback_days=3) %}
    {% if is_incremental() %}
        AND {{ column }} >= (
            SELECT MAX({{ column }}) - INTERVAL '{{ lookback_days }} days'
            FROM {{ this }}
        )
    {% endif %}
{% endmacro %}
```

### Snapshots (SCD Type 2)

```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}

{{
    config(
        target_schema = 'snapshots',
        unique_key    = 'customer_id',
        strategy      = 'updated_at',
        updated_at    = 'updated_at',
        invalidate_hard_deletes = True,
    )
}}

SELECT
    customer_id,
    name,
    email,
    plan,
    updated_at
FROM {{ source('raw', 'customers') }}

{% endsnapshot %}
```

dbt adiciona automaticamente: `dbt_scd_id`, `dbt_updated_at`, `dbt_valid_from`, `dbt_valid_to`.

### Incremental Models

```sql
-- models/silver/orders_incremental.sql
{{
    config(
        materialized         = 'incremental',
        unique_key           = 'order_id',
        incremental_strategy = 'merge',   -- ou 'delete+insert', 'insert_overwrite', 'append'
        on_schema_change     = 'sync_all_columns',
        partition_by         = {
            "field": "created_at",
            "data_type": "timestamp",
            "granularity": "day"
        }
    )
}}

SELECT
    order_id,
    customer_id,
    amount,
    status,
    created_at
FROM {{ source('raw', 'orders') }}

{% if is_incremental() %}
    WHERE created_at > (
        SELECT MAX(created_at) - INTERVAL '3 days'  -- lookback para late arrivals
        FROM {{ this }}
    )
{% endif %}
```

---

## Patterns

### Packages

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.1.0", "<2.0.0"]
  - package: calogica/dbt_expectations   # port do Great Expectations
    version: [">=0.10.0"]
  - package: dbt-labs/dbt_project_evaluator  # linting de projetos dbt
    version: [">=0.10.0"]
```

```bash
dbt deps  # instala packages
```

### Semantic Layer

```yaml
# models/semantic/orders_metric.yml
semantic_models:
  - name: orders
    model: ref('orders_cleaned')
    entities:
      - name: order
        type: primary
        expr: order_id
      - name: customer
        type: foreign
        expr: customer_id
    measures:
      - name: total_revenue
        agg: sum
        expr: amount
      - name: order_count
        agg: count_distinct
        expr: order_id
    dimensions:
      - name: status
        type: categorical
      - name: created_at
        type: time
        type_params:
          time_granularity: day

metrics:
  - name: daily_revenue
    label: "Receita Diária"
    type: simple
    type_params:
      measure: total_revenue
    filter: "{{ Dimension('order__status') }} = 'PAID'"
```

### dbt Cloud — Job Configuration

```yaml
# Execução via API ou dbt Cloud UI
# Job: Full Refresh (semanal)
dbt build --select tag:weekly --full-refresh

# Job: Incremental (diário)
dbt build --select state:modified+ --defer --state /path/to/prod/manifest

# Slim CI — testa apenas o que mudou
dbt build --select state:modified+ --defer --state prod
```

---

## Gotchas

> [!bug] Ref em Ephemeral Models
> Models `ephemeral` são substituídos por CTEs inline — não são tabelas reais. Se um ephemeral model é referenciado por muitos models, o CTE é duplicado em cada query, podendo criar queries massivas.

> [!warning] Incremental + Schema Change
> Com `incremental_strategy='append'`, adicionar colunas ao model não as adiciona à tabela existente. Use `on_schema_change='sync_all_columns'` ou execute `dbt run --full-refresh` após mudanças de schema.

> [!caution] Test Granularity
> Testes `unique` e `not_null` em colunas com bilhões de linhas podem ser lentos. Use `--store-failures` para persistir resultados em tabela e analise separadamente, ou configure `--limit` nos testes.

---

## Snippets

### Executar com [[apache-airflow]]

```python
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id="dbt_run_silver",
    bash_command="""
        dbt run
          --project-dir /opt/dbt
          --profiles-dir /opt/dbt
          --target prod
          --select tag:silver
          --vars '{"execution_date": "{{ ds }}"}'
    """,
)

dbt_test = BashOperator(
    task_id="dbt_test_silver",
    bash_command="dbt test --project-dir /opt/dbt --select tag:silver",
)

dbt_run >> dbt_test
```

### Exposures

```yaml
# models/exposures.yml
exposures:
  - name: revenue_dashboard
    label: "Dashboard de Receita"
    type: dashboard
    maturity: high
    url: "https://tableau.company.com/views/Revenue"
    depends_on:
      - ref('customer_ltv')
      - ref('daily_revenue')
    owner:
      name: "Ana Lima"
      email: "ana@company.com"
```

---

## References

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
- [dbt Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)

---

## Related

- [[postgresql]] — adapter dbt para PostgreSQL/Redshift
- [[spark]] — dbt-spark para transformações no Spark
- [[data-lake-patterns]] — dbt na camada silver/gold do medallion
- [[apache-airflow]] — orquestração de jobs dbt com BashOperator
- [[dagster]] — integração nativa dagster-dbt com assets automáticos
