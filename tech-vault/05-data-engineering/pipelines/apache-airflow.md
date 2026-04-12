---
tags: [skill, data-engineering, airflow]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Airflow, Apache Airflow]
---

# Apache Airflow

## Overview

Apache Airflow é uma plataforma de orquestração de workflows baseada em Python. Workflows são definidos como DAGs (Directed Acyclic Graphs) — código Python que descreve dependências entre tarefas. Airflow não move dados; ele **orquestra** a execução de sistemas externos.

> [!important] Airflow Philosophy
> "Workflows as code" — cada DAG é um arquivo Python versionável, testável e reutilizável. Evite usar Airflow como motor de processamento; use-o para coordenar [[dbt]], [[spark]], ou jobs em [[kubernetes-basics]].

---

## Core Concepts

### DAG (Directed Acyclic Graph)

```python
# airflow/dags/example_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["alerts@company.com"],
}

with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    schedule_interval="0 6 * * *",   # 6am UTC diariamente
    start_date=days_ago(1),
    catchup=False,
    tags=["etl", "production"],
    max_active_runs=1,
) as dag:
    ...
```

### Operators

**PythonOperator** — executa uma função Python callable:

```python
from airflow.operators.python import PythonOperator

def extract_data(**context):
    execution_date = context["ds"]  # "2026-04-05"
    # lógica de extração
    return {"rows": 5000}

extract = PythonOperator(
    task_id="extract",
    python_callable=extract_data,
    provide_context=True,
)
```

**BashOperator** — executa shell scripts:

```python
from airflow.operators.bash import BashOperator

run_dbt = BashOperator(
    task_id="run_dbt_models",
    bash_command="dbt run --profiles-dir /opt/airflow/dbt --target prod",
    env={"DBT_DATABASE_URL": "{{ var.value.db_url }}"},
)
```

**DockerOperator** — executa containers isolados (sem poluir o ambiente Airflow):

```python
from airflow.providers.docker.operators.docker import DockerOperator

docker_task = DockerOperator(
    task_id="run_spark_job",
    image="spark-etl:3.5.0",
    command="spark-submit /jobs/process.py --date {{ ds }}",
    docker_url="unix://var/run/docker.sock",
    network_mode="bridge",
    auto_remove=True,
)
```

**KubernetesPodOperator** — executa Pods no [[kubernetes-basics]]:

```python
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s

spark_job = KubernetesPodOperator(
    task_id="spark_k8s_job",
    name="spark-etl-pod",
    namespace="data-jobs",
    image="spark-etl:3.5.0",
    arguments=["--date", "{{ ds }}"],
    resources=k8s.V1ResourceRequirements(
        requests={"cpu": "2", "memory": "4Gi"},
        limits={"cpu": "4", "memory": "8Gi"},
    ),
    is_delete_operator_pod=True,
    get_logs=True,
    in_cluster=True,
)
```

### Sensors

Sensors aguardam uma condição antes de prosseguir:

```python
from airflow.sensors.filesystem import FileSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

# Aguarda arquivo no S3
wait_for_file = S3KeySensor(
    task_id="wait_for_s3_file",
    bucket_name="raw-data-bucket",
    bucket_key="landing/{{ ds_nodash }}/data.parquet",
    aws_conn_id="aws_default",
    poke_interval=60,      # verifica a cada 60s
    timeout=3600,          # timeout em 1h
    mode="reschedule",     # libera worker slot enquanto aguarda
)
```

> [!warning] Sensor Mode
> Use `mode="reschedule"` em produção. `mode="poke"` mantém o worker slot ocupado — pode causar deadlock com pools pequenos.

### XCom (Cross-Communication)

XCom permite troca de pequenas mensagens entre tasks:

```python
def push_value(**context):
    # Push explícito
    context["ti"].xcom_push(key="row_count", value=42000)

def pull_value(**context):
    ti = context["ti"]
    count = ti.xcom_pull(task_ids="extract", key="row_count")
    print(f"Processando {count} linhas")
```

> [!caution] XCom Limitations
> XCom é armazenado no metadata DB. Não use para transferir DataFrames ou arquivos grandes. Para volumes maiores, use S3/GCS e passe apenas o path via XCom.

### TaskFlow API (Airflow 2.x)

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule_interval="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def modern_pipeline():

    @task()
    def extract() -> dict:
        return {"source": "api", "records": 1500}

    @task()
    def transform(data: dict) -> dict:
        data["records_processed"] = data["records"] * 2
        return data

    @task()
    def load(data: dict):
        print(f"Carregando {data['records_processed']} registros")

    # Dependências inferidas automaticamente por XCom
    load(transform(extract()))

pipeline = modern_pipeline()
```

---

## Patterns

### Dynamic DAG Generation

```python
# Gera um DAG por cliente/tenant
import yaml
from pathlib import Path

configs = yaml.safe_load(Path("/opt/airflow/configs/clients.yaml").read_text())

for client in configs["clients"]:
    dag_id = f"etl_{client['name']}"

    with DAG(dag_id=dag_id, schedule_interval=client["schedule"], ...) as dag:
        extract = PythonOperator(
            task_id="extract",
            python_callable=extract_data,
            op_kwargs={"client_id": client["id"]},
        )
        globals()[dag_id] = dag  # registra o DAG no Airflow
```

### Connections e Pools

```bash
# Via CLI
airflow connections add 'postgres_prod' \
  --conn-type postgres \
  --conn-host db.company.com \
  --conn-login etl_user \
  --conn-password '{{ secrets.DB_PASS }}' \
  --conn-port 5432

# Pool para limitar concorrência em fonte externa
airflow pools set api_pool 5 "Max 5 calls to external API"
```

```python
task = PythonOperator(
    task_id="call_api",
    python_callable=fetch_from_api,
    pool="api_pool",
    pool_slots=1,
)
```

### KubernetesExecutor

```yaml
# airflow.cfg ou values.yaml (Helm)
[core]
executor = KubernetesExecutor

[kubernetes]
namespace = airflow
worker_container_repository = my-registry/airflow
worker_container_tag = 2.8.0
delete_worker_pods = True
```

Com KubernetesExecutor, cada task é um Pod — isolamento total, sem contention de recursos.

---

## Gotchas

> [!bug] Catchup e Data Inconsistency
> `catchup=True` com `start_date` no passado dispara todas as runs perdidas. Em produção, sempre use `catchup=False` e gerencie backfills manualmente com `airflow dags backfill`.

> [!warning] Importação de DAGs
> Airflow varre a pasta `dags/` a cada `dag_dir_list_interval` segundos. Imports lentos (ex: `import pandas`) no nível do módulo atrasam o scheduler. Use imports dentro dos callables.

> [!tip] Idempotência
> Toda task deve ser idempotente: rodar duas vezes com os mesmos inputs produz o mesmo resultado. Use `DELETE WHERE date = '{{ ds }}'` antes de inserções.

---

## Snippets

### Trigger Rule para Controle de Fluxo

```python
from airflow.utils.trigger_rule import TriggerRule

notify_failure = EmailOperator(
    task_id="notify_on_failure",
    trigger_rule=TriggerRule.ONE_FAILED,  # dispara se qualquer upstream falhar
    to="oncall@company.com",
    subject="Pipeline falhou: {{ dag.dag_id }}",
    html_content="Checar logs em {{ ti.log_url }}",
)
```

### Template com Jinja

```python
query = """
    SELECT *
    FROM orders
    WHERE DATE(created_at) = '{{ ds }}'
      AND updated_at >= '{{ prev_ds }}'
    LIMIT {{ var.value.batch_size | default(10000) }}
"""
```

---

## References

- [Airflow Docs — TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
- [Airflow Docs — KubernetesExecutor](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/executor/kubernetes.html)
- [Astronomer Best Practices](https://docs.astronomer.io/learn/best-practices-for-airflow)

---

## Related

- [[dagster]] — alternativa moderna com software-defined assets
- [[prefect]] — alternativa Python-native com Prefect Cloud
- [[docker]] — DockerOperator para isolamento de tasks
- [[kubernetes-basics]] — KubernetesPodOperator e KubernetesExecutor
- [[python]] — linguagem base para DAGs e callables
- [[dbt]] — orquestração de modelos dbt via BashOperator ou DbtOperator
