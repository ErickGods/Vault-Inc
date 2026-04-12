---
tags: [skill, data-engineering, prefect]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Prefect]
---

# Prefect

## Overview

Prefect é uma plataforma de orquestração de workflows orientada a **flows** e **tasks** Python. Diferente do [[apache-airflow]] (que exige definição estática de DAGs), Prefect permite workflows dinâmicos com controle de fluxo nativo Python (`if`, `for`, `try/except`). A versão 2.x (Prefect 2 / "Orion") reescreveu completamente a arquitetura.

> [!important] Prefect Philosophy
> "Your code, your infra." Flows são funções Python normais decoradas — sem DSL proprietária. O servidor Prefect apenas registra execuções e estados; a computação acontece onde você quiser.

---

## Core Concepts

### Flows e Tasks

```python
# flows/etl_pipeline.py
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta
import pandas as pd

@task(
    retries=3,
    retry_delay_seconds=30,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
    tags=["extraction", "api"],
)
def extract_orders(date: str) -> pd.DataFrame:
    logger = get_run_logger()
    logger.info(f"Extraindo ordens para {date}")
    # Caching automático: mesmos inputs = resultado em cache
    return pd.read_parquet(f"s3://raw/orders/date={date}/")


@task(retries=2)
def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .dropna(subset=["order_id"])
        .assign(amount=lambda x: x["amount"].astype(float))
    )


@task
def load_orders(df: pd.DataFrame, target_table: str):
    logger = get_run_logger()
    df.to_parquet(f"s3://silver/{target_table}/data.parquet", index=False)
    logger.info(f"Carregadas {len(df)} linhas em {target_table}")


@flow(name="ETL Orders Pipeline", log_prints=True)
def etl_pipeline(date: str = "2026-04-05", target: str = "orders_clean"):
    raw = extract_orders(date)
    cleaned = transform_orders(raw)
    load_orders(cleaned, target)
```

### Deployments

Deployments transformam flows em processos agendados e gerenciados:

```python
# deployment.py
from prefect import flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=etl_pipeline,
    name="production-daily",
    schedule=CronSchedule(cron="0 6 * * *", timezone="America/Sao_Paulo"),
    parameters={"date": "{{ now | strftime('%Y-%m-%d') }}"},
    work_pool_name="kubernetes-pool",
    work_queue_name="high-priority",
    tags=["prod", "etl"],
    version="1.2.0",
)
deployment.apply()
```

```bash
# CLI alternativa
prefect deploy --name production-daily --cron "0 6 * * *" --pool kubernetes-pool
```

### Work Pools

Work pools definem a infraestrutura de execução:

```yaml
# prefect.yaml
deployments:
  - name: etl-daily
    work_pool:
      name: kubernetes-pool
      job_variables:
        image: my-registry/prefect-flows:latest
        namespace: data-jobs
        cpu_request: "2"
        memory_request: "4Gi"
        service_account_name: prefect-runner
```

Tipos de work pool:
- `process` — execução local como subprocesso
- `kubernetes` — Pod por flow run no [[kubernetes-basics]]
- `docker` — container [[docker]] por run
- `ecs` — AWS ECS Task
- `vertex-ai` — Google Vertex AI Custom Job

### Blocks

Blocks são configurações reutilizáveis e versionadas para credenciais e conexões:

```python
from prefect_aws import S3Bucket, AwsCredentials
from prefect_sqlalchemy import SqlAlchemyConnector

# Criar e salvar block (uma vez)
aws_creds = AwsCredentials(
    aws_access_key_id="AKIA...",
    aws_secret_access_key="secret",
    region_name="us-east-1",
)
aws_creds.save("prod-aws-creds")

s3_bucket = S3Bucket(
    bucket_name="data-lake-prod",
    credentials=aws_creds,
)
s3_bucket.save("prod-data-lake")

# Usar no flow
@task
def upload_to_s3(df: pd.DataFrame):
    s3 = S3Bucket.load("prod-data-lake")
    s3.upload_from_dataframe(df, to_path="silver/orders.parquet")
```

### Results e Caching

```python
from prefect.filesystems import S3
from prefect.results import PersistedResultBlob

# Configurar backend de resultados no flow
@flow(
    result_storage=S3(bucket_path="s3://prefect-results/"),
    result_serializer="pickle",
    persist_result=True,
)
def cacheable_flow():
    ...
```

> [!tip] Cache Strategy
> `cache_key_fn=task_input_hash` gera uma chave baseada nos inputs. Se os mesmos dados forem processados novamente (ex: retry de pipeline), a task retorna o resultado em cache sem reprocessar.

---

## Patterns

### Artifacts

Artifacts adicionam metadata visível na UI do Prefect Cloud:

```python
from prefect.artifacts import create_table_artifact, create_markdown_artifact

@task
def process_and_report(df: pd.DataFrame):
    summary = df.describe().to_dict()

    create_table_artifact(
        key="data-summary",
        table=df.head(10).to_dict("records"),
        description="Amostra dos dados processados",
    )

    create_markdown_artifact(
        key="pipeline-report",
        markdown=f"## Relatório\n- **Linhas**: {len(df)}\n- **Colunas**: {len(df.columns)}",
    )
```

### Automations

Automations são regras event-driven no Prefect Cloud:

```yaml
# Via API / UI
trigger:
  type: flow-run-state-change
  state: Failed
  flow_name: "ETL Orders Pipeline"

action:
  type: send-notification
  block_document_id: slack-webhook-block-id
  body: "Flow {{ flow.name }} falhou: {{ flow_run.name }}"
```

### Dynamic Task Mapping

```python
@flow
def parallel_pipeline(dates: list[str]):
    # Executa extract em paralelo para cada data
    raw_dfs = extract_orders.map(dates)
    cleaned_dfs = transform_orders.map(raw_dfs)
    load_orders.map(cleaned_dfs, ["orders_clean"] * len(dates))
```

> [!info] .map() vs Loops
> `.map()` submete todas as tasks de uma vez para execução paralela. Um `for` loop com `submit()` faz o mesmo, mas `.map()` é mais idiomático e suporta `wait_for`.

### Subflows

```python
@flow
def child_flow(table: str):
    data = extract_orders("2026-04-05")
    load_orders(data, table)

@flow
def parent_flow():
    # Subflows executam sincronamente por padrão
    child_flow("table_a")
    child_flow("table_b")

    # Ou em paralelo
    futures = [child_flow.submit("table_c"), child_flow.submit("table_d")]
    for f in futures:
        f.result()
```

---

## Gotchas

> [!bug] Async Flows
> Flows assíncronos requerem `asyncio.run()` ou um event loop ativo. Em notebooks Jupyter, use `await flow()` diretamente — não `flow()`.

> [!warning] Task Dependencies sem Retorno
> Se uma task não retorna nada mas depende de outra, use `wait_for=[upstream_task_future]` para garantir a ordem de execução.

> [!caution] Prefect Cloud vs Self-Hosted
> Prefect Cloud gratuito tem limites de runs/mês. Self-hosted (Prefect Server) é gratuito mas requer infraestrutura própria. O código dos flows é idêntico — apenas o `PREFECT_API_URL` muda.

---

## Snippets

### Executar Flow Localmente

```bash
# Desenvolvimento
python flows/etl_pipeline.py

# Com parâmetros
prefect run deployment 'ETL Orders Pipeline/production-daily' \
  --param date=2026-04-01
```

### Profile Configuration

```bash
prefect profile create prod
prefect profile use prod
prefect config set PREFECT_API_URL="https://api.prefect.cloud/api/accounts/.../workspaces/..."
prefect config set PREFECT_API_KEY="pnu_..."
```

---

## References

- [Prefect Docs — Concepts](https://docs.prefect.io/latest/concepts/)
- [Prefect Docs — Work Pools](https://docs.prefect.io/latest/concepts/work-pools/)
- [Prefect Recipes](https://github.com/PrefectHQ/prefect-recipes)

---

## Related

- [[apache-airflow]] — comparação: DAG estática vs flow dinâmico
- [[dagster]] — alternativa asset-centric
- [[python]] — linguagem nativa dos flows Prefect
- [[docker]] — work pool Docker para isolamento de execução
- [[kubernetes-basics]] — work pool Kubernetes para escalabilidade
