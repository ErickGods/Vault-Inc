---
tags: [skill, data-engineering, dagster]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Dagster]
---

# Dagster

## Overview

Dagster é uma plataforma de orquestração de dados orientada a **assets** (Software-Defined Assets). Em vez de modelar workflows como sequências de tasks, Dagster modela o que você **produz** — tabelas, arquivos, modelos ML. O scheduler e o lineage derivam automaticamente do grafo de dependências entre assets.

> [!important] Asset-Centric Paradigm
> A diferença fundamental em relação ao [[apache-airflow]]: no Airflow você define *como* executar; no Dagster você define *o que* existe. Assets são entidades de primeira classe com metadata, partições e observações.

---

## Core Concepts

### Software-Defined Assets

```python
# assets/orders.py
from dagster import asset, AssetIn
import pandas as pd

@asset(
    group_name="raw",
    description="Ordens brutas extraídas da API de vendas",
    metadata={"source": "sales-api", "owner": "data-team"},
)
def raw_orders() -> pd.DataFrame:
    """Extrai ordens do sistema de vendas."""
    import requests
    resp = requests.get("https://api.company.com/orders")
    return pd.DataFrame(resp.json()["data"])


@asset(
    ins={"raw_orders": AssetIn()},
    group_name="silver",
    description="Ordens limpas e normalizadas",
)
def cleaned_orders(raw_orders: pd.DataFrame) -> pd.DataFrame:
    df = raw_orders.copy()
    df = df.dropna(subset=["order_id", "customer_id"])
    df["amount"] = df["amount"].astype(float)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


@asset(
    ins={"cleaned_orders": AssetIn()},
    group_name="gold",
    compute_kind="pandas",
)
def daily_revenue(cleaned_orders: pd.DataFrame) -> pd.DataFrame:
    return (
        cleaned_orders
        .groupby(cleaned_orders["created_at"].dt.date)["amount"]
        .sum()
        .reset_index()
        .rename(columns={"created_at": "date", "amount": "revenue"})
    )
```

### Ops e Jobs

Quando você precisa de lógica procedural (não assets), use **ops** + **jobs**:

```python
from dagster import op, job, Out, In

@op(out={"data": Out(pd.DataFrame)})
def extract_op(context) -> pd.DataFrame:
    context.log.info("Extraindo dados...")
    return pd.read_parquet("s3://bucket/raw/data.parquet")

@op(ins={"data": In(pd.DataFrame)})
def load_op(context, data: pd.DataFrame):
    data.to_sql("table", context.resources.db_conn, if_exists="append")

@job(resource_defs={"db_conn": postgres_resource})
def etl_job():
    load_op(extract_op())
```

### Resources

Resources são dependências externas injetadas (conexões, clientes de API, etc.):

```python
from dagster import resource, ConfigurableResource
from sqlalchemy import create_engine

class PostgresResource(ConfigurableResource):
    connection_string: str

    def get_engine(self):
        return create_engine(self.connection_string)

    def execute(self, query: str):
        with self.get_engine().connect() as conn:
            return conn.execute(query)

# Uso no asset
@asset(required_resource_keys={"postgres"})
def load_to_db(context, cleaned_orders: pd.DataFrame):
    context.resources.postgres.execute(
        "DELETE FROM orders WHERE date = CURRENT_DATE"
    )
    cleaned_orders.to_sql("orders", context.resources.postgres.get_engine())
```

### IO Managers

IO Managers controlam como assets são persistidos e carregados entre execuções:

```python
from dagster import IOManager, io_manager
import pandas as pd

class ParquetIOManager(IOManager):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def handle_output(self, context, obj: pd.DataFrame):
        path = f"{self.base_path}/{context.asset_key.path[-1]}.parquet"
        obj.to_parquet(path, index=False)
        context.add_output_metadata({"rows": len(obj), "path": path})

    def load_input(self, context) -> pd.DataFrame:
        path = f"{self.base_path}/{context.asset_key.path[-1]}.parquet"
        return pd.read_parquet(path)

@io_manager(config_schema={"base_path": str})
def parquet_io_manager(init_context):
    return ParquetIOManager(init_context.resource_config["base_path"])
```

> [!tip] IO Manager vs XCom
> IO Managers são a solução Dagster para o problema que [[apache-airflow]] resolve com XCom — mas de forma muito mais robusta, suportando objetos grandes e backends plugáveis (S3, GCS, Delta).

### Partitions

Assets particionados para processamento incremental:

```python
from dagster import DailyPartitionsDefinition, asset

daily_partitions = DailyPartitionsDefinition(start_date="2026-01-01")

@asset(partitions_def=daily_partitions)
def partitioned_orders(context) -> pd.DataFrame:
    partition_date = context.partition_key  # "2026-04-05"
    return pd.read_parquet(f"s3://bucket/orders/date={partition_date}/")
```

### Schedules e Sensors

```python
from dagster import ScheduleDefinition, AssetSelection, define_asset_job, sensor, RunRequest

# Schedule simples
nightly_job = define_asset_job(
    "nightly_etl",
    selection=AssetSelection.groups("silver", "gold")
)

nightly_schedule = ScheduleDefinition(
    job=nightly_job,
    cron_schedule="0 2 * * *",  # 2am UTC
)

# Sensor — dispara quando novo arquivo chega no S3
@sensor(job=nightly_job)
def s3_sensor(context):
    import boto3
    s3 = boto3.client("s3")
    objects = s3.list_objects_v2(Bucket="raw-data", Prefix="landing/")
    new_files = [o for o in objects.get("Contents", []) if "processed" not in o["Key"]]
    if new_files:
        yield RunRequest(run_key=new_files[0]["Key"])
```

---

## Patterns

### Asset Observations

Observar um asset sem materializá-lo (útil para datasets externos):

```python
from dagster import AssetObservation, asset, Output

@asset
def external_table(context):
    row_count = query_db("SELECT COUNT(*) FROM external.orders")
    context.log_event(
        AssetObservation(asset_key="external_table", metadata={"row_count": row_count})
    )
    # Não retorna nada — apenas observa
```

### dbt Integration

```python
from dagster_dbt import dbt_assets, DbtProject

dbt_project = DbtProject(project_dir="/opt/dbt", target="prod")

@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_models(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
```

Dagster + [[dbt]] é uma das integrações mais poderosas: os modelos dbt viram assets Dagster com lineage automático.

---

## Gotchas

> [!bug] Asset Key Conflicts
> Se dois assets têm o mesmo `key_prefix` e nome, o Dagster silenciosamente usa apenas um. Use `group_name` para organizar, mas certifique-se que `asset_key` é único globalmente.

> [!warning] Resource Configuration
> Resources configurados via `Definitions` são globais. Em testes, use `with_resources()` para substituir por mocks sem alterar o código de produção.

> [!tip] Dagit UI
> O Dagit (UI do Dagster) exibe lineage visual, status de partições e logs estruturados. Use `dagster dev` localmente para explorar o asset graph antes de deployar.

---

## Snippets

### Definitions — Entry Point

```python
# definitions.py
from dagster import Definitions, load_assets_from_modules
from . import assets, resources

defs = Definitions(
    assets=load_assets_from_modules([assets]),
    resources={
        "postgres": resources.PostgresResource(
            connection_string="postgresql://user:pass@host/db"
        ),
        "io_manager": parquet_io_manager.configured({"base_path": "s3://bucket/assets"}),
    },
    schedules=[nightly_schedule],
    sensors=[s3_sensor],
)
```

### Freshness Policies

```python
from dagster import FreshnessPolicy

@asset(freshness_policy=FreshnessPolicy(maximum_lag_minutes=60))
def real_time_metrics() -> dict:
    ...
```

---

## References

- [Dagster Docs — Software-Defined Assets](https://docs.dagster.io/concepts/assets/software-defined-assets)
- [Dagster Docs — IO Managers](https://docs.dagster.io/concepts/io-management/io-managers)
- [Dagster + dbt Integration](https://docs.dagster.io/integrations/dbt)

---

## Related

- [[apache-airflow]] — comparação: task-centric vs asset-centric
- [[prefect]] — alternativa com foco em flows Python
- [[python]] — linguagem nativa do Dagster
- [[dbt]] — integração nativa via dagster-dbt
- [[docker]] — deployment via Docker Compose ou K8s
