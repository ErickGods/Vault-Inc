---
tags: [moc, data-engineering]
status: active
level: advanced
updated: 2026-04-05
aliases: [Data Engineering MOC]
created: 2026-04-05
---

# 📊 Data Engineering MOC

## Visão Geral

Este MOC cobre o domínio de engenharia de dados: orquestração de pipelines, streaming de eventos, armazenamento analítico e transformação de dados. Enquanto a engenharia de software foca em sistemas transacionais (OLTP), a engenharia de dados foca em sistemas analíticos (OLAP) e na movimentação confiável de dados entre sistemas.

O stack moderno de dados converge em torno de conceitos como lakehouse architecture, transformações declarativas com dbt, e orquestração baseada em assets. Esta seção documenta as ferramentas e padrões que constroem pipelines de dados confiáveis e observáveis.

> [!info] Cobertura
> Esta seção (`05-data-engineering/`) contém 10 arquivos cobrindo orquestração, streaming, storage analítico e transformação.

> [!tip] Modern Data Stack
> O stack moderno de dados tende a ser: ingestão → storage (data lake) → transformação (dbt) → serving (data warehouse). As ferramentas neste MOC cobrem cada camada.

---

## 📊 Dashboard

```dataview
TABLE status, level, updated
FROM "tech-vault/05-data-engineering"
SORT updated DESC
```

---

## 🗺️ Skills Map

### Pipeline Orchestration

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[apache-airflow]] | Apache Airflow — DAGs e agendamento | ✅ active |
| [[dagster]] | Dagster — orquestração baseada em assets | ✅ active |
| [[prefect]] | Prefect — pipelines Pythônicas | ✅ active |

### Streaming

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[kafka]] | Apache Kafka — event streaming | ✅ active |
| [[flink]] | Apache Flink — stream processing | 🚧 draft |

### Storage & Lakehouse

| Arquivo | Tecnologia | Status |
|---------|-----------|--------|
| [[data-lake-patterns]] | Data lake architecture e padrões | ✅ active |
| [[delta-lake]] | Delta Lake — ACID no data lake | ✅ active |
| [[duckdb]] | DuckDB — analytics in-process | ✅ active |

### Transformation

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[dbt]] | dbt — transformações SQL declarativas | ✅ active |
| [[spark]] | Apache Spark — processamento distribuído | ✅ active |

---

## ⚡ Quick Access

- [[dbt]] — Transformações SQL versionadas e testadas
- [[apache-airflow]] — Orquestração de pipelines legados e integrações
- [[dagster]] — Orquestração moderna com lineage automático
- [[kafka]] — Streaming de eventos de alta throughput
- [[duckdb]] — Analytics local e exploração de dados
- [[delta-lake]] — Confiabilidade ACID no data lake

---

## 🏗️ Data Architecture Patterns

### Lakehouse Architecture

```
Fontes Operacionais (PostgreSQL, APIs, Events)
           ↓
    Ingestão (Kafka / batch jobs)
           ↓
    Raw Layer — Data Lake (S3/GCS)
           ↓
    Curated Layer — Delta Lake (ACID + schema)
           ↓
    Transformation — dbt models
           ↓
    Serving Layer — DW / DuckDB / BI tools
```

> [!info] Por que Lakehouse?
> Combina o baixo custo e flexibilidade do data lake com as garantias ACID e performance do data warehouse. [[delta-lake]] adiciona transações, time travel e schema enforcement ao armazenamento em S3.

### Lambda Architecture vs Kappa

```
Lambda:
  Hot path: Kafka → Flink → serving layer (baixa latência)
  Cold path: batch jobs → data lake → transformações

Kappa:
  Tudo via streaming: Kafka → Flink → serving
  Mais simples, mas exige reprocessamento histórico via replay
```

Ver [[kafka]] e [[flink]] para implementação de cada camada.

---

## ⚙️ Orchestration — Comparativo

> [!tip] Escolhendo o Orquestrador
> - **[[apache-airflow]]** → time já conhece, muitas integrações prontas, legado maduro
> - **[[dagster]]** → novo projeto, quer asset lineage, melhor DX para times de dados
> - **[[prefect]]** → simplicidade Python, deploy fácil, boa escolha para times pequenos

```python
# Dagster — definição de asset (conceito central)
# Detalhes completos em [[dagster]]
@asset(
    deps=["raw_orders"],
    description="Pedidos limpos e validados",
)
def cleaned_orders(context, raw_orders: pd.DataFrame) -> pd.DataFrame:
    return raw_orders.dropna().query("amount > 0")
```

---

## 🔄 dbt — Transformações Declarativas

```sql
-- Exemplo de modelo dbt — ver [[dbt]] para padrões completos
-- models/marts/orders_daily.sql
{{ config(materialized='incremental', unique_key='order_date') }}

SELECT
    DATE_TRUNC('day', created_at) AS order_date,
    COUNT(*)                       AS total_orders,
    SUM(amount)                    AS revenue
FROM {{ ref('stg_orders') }}
{% if is_incremental() %}
WHERE created_at >= (SELECT MAX(order_date) FROM {{ this }})
{% endif %}
GROUP BY 1
```

> [!tip] dbt Best Practices
> - Staging models: 1-to-1 com a fonte, apenas renaming e tipos
> - Intermediate: joins e transformações de lógica de negócio
> - Marts: modelos finais consumidos por BI e analistas
> - Testar sempre com `dbt test` antes de merge

---

## 🌊 Kafka — Event Streaming

```
Producers → Topics (particionados) → Consumer Groups → Aplicações
                    ↓
            Schema Registry (Avro/Protobuf)
                    ↓
         Kafka Connect → Data Lake
```

> [!info] Kafka vs SQS/RabbitMQ
> Kafka é event log imutável e replayável — ideal para event sourcing e auditoria. SQS/RabbitMQ são filas de trabalho — mensagem é consumida e deletada. Ver [[architecture-moc]] para o comparativo completo.

---

## 🦆 DuckDB — Analytics In-Process

```sql
-- DuckDB — queries direto em arquivos Parquet — ver [[duckdb]]
SELECT
    year,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM read_parquet('s3://bucket/data/orders/*.parquet')
GROUP BY year
ORDER BY year DESC;
```

> [!tip] Quando Usar DuckDB
> - Exploração local de datasets (até dezenas de GBs)
> - Alternativa a Pandas para transformações analíticas
> - Serving layer leve em aplicações analíticas
> - Substitui Spark para datasets que cabem em uma máquina

---

## 🔗 Integrações com Outros Domínios

- **Architecture** → [[architecture-moc]] — [[kafka]] e [[event-driven]] se sobrepõem; [[s3-storage-patterns]] para o data lake
- **Engineering** → [[engineering-moc]] — [[postgresql]] como fonte de dados; [[python]] em todos os pipelines
- **DevOps** → [[devops-moc]] — CI/CD para pipelines dbt e monitoramento com [[observability]]
- **AI/ML** → [[ai-ml-moc]] — dados curados alimentam RAG pipelines e fine-tuning

---

## 📐 Data Quality Patterns

> [!example] Garantindo Qualidade dos Dados
> 1. **Schema validation** — Great Expectations ou dbt tests
> 2. **Freshness checks** — alertar quando dados param de chegar
> 3. **Volume checks** — desvios estatísticos no volume diário
> 4. **Referential integrity** — chaves estrangeiras válidas entre tabelas
> 5. **Business rules** — `revenue >= 0`, `age BETWEEN 0 AND 150`

Implementar como testes no [[dbt]] ou como sensores no [[apache-airflow]]/[[dagster]].
