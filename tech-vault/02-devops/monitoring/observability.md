---
tags: [skill, devops, observability]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Observability, Monitoring]
---

# Observability

## Overview

Observabilidade é a capacidade de entender o estado interno de um sistema a partir de suas saídas externas — logs, métricas e traces. Diferente de "monitoramento" (verificar se algo está quebrado), observabilidade permite perguntar *por quê* algo está quebrado, mesmo sem ter antecipado o problema. Este documento cobre o stack completo: OpenTelemetry, Prometheus, Grafana, Loki e Jaeger/Tempo, além de estratégias de SLOs. Integra com [[kubernetes-basics]] para discovery automático, [[docker]] para coleta de logs, [[github-actions]] para métricas de pipeline, [[fastapi]] para instrumentação e [[deployment-strategies]] para tracking de deploys.

> [!info] Os Três Pilares
> **Logs** = o que aconteceu | **Metrics** = quantas vezes / quão rápido | **Traces** = onde o tempo foi gasto

---

## Core Concepts

### OpenTelemetry (OTel)

OpenTelemetry é o padrão vendor-neutral para instrumentação. Unifica coleta de traces, métricas e logs num único SDK e protocolo (OTLP).

#### SDK e Auto-Instrumentação (Python/FastAPI)

```python
# otel_setup.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION

def setup_telemetry(app, service_name: str, service_version: str):
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "deployment.environment": os.getenv("ENV", "production"),
    })

    # Traces
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://otel-collector:4317"),
            max_export_batch_size=512,
            export_timeout_millis=30_000,
        )
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint="http://otel-collector:4317"),
        export_interval_millis=60_000,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))

    # Auto-instrumentação
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(enable_commenter=True)
    RedisInstrumentor().instrument()
```

#### OTel Collector

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  prometheus:
    config:
      scrape_configs:
        - job_name: otel-collector
          static_configs:
            - targets: [localhost:8888]

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  resource:
    attributes:
      - key: cluster
        value: production
        action: upsert

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, resource]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
```

---

## Patterns

### Prometheus: PromQL e Recording Rules

PromQL avançado para análise de latência com histogramas:

```promql
# Latência P99 nos últimos 5 minutos
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service, endpoint)
)

# Taxa de erros por serviço
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
  /
sum(rate(http_requests_total[5m])) by (service)

# Apdex Score (satisfeitos < 300ms, tolerados < 1200ms)
(
  sum(rate(http_request_duration_seconds_bucket{le="0.3"}[5m])) by (service)
  +
  sum(rate(http_request_duration_seconds_bucket{le="1.2"}[5m])) by (service)
    * 0.5
)
/ sum(rate(http_request_duration_seconds_count[5m])) by (service)
```

```yaml
# prometheus/recording_rules.yml
groups:
  - name: api_aggregations
    interval: 30s
    rules:
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job, status)

      - record: job:http_request_duration_p99:rate5m
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le)
          )

  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
            /
          sum(rate(http_requests_total[5m])) by (service)
          > 0.05
        for: 5m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "Error rate {{ $value | humanizePercentage }} on {{ $labels.service }}"
          runbook: "https://wiki.company.com/runbooks/high-error-rate"
          dashboard: "https://grafana.company.com/d/api-overview"

      - alert: SLOBudgetBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h])) by (service)
              /
            sum(rate(http_requests_total[1h])) by (service)
          ) > (14.4 * 0.001)   # 14.4x burn rate para 1h window
        for: 2m
        labels:
          severity: critical
```

### Prometheus Service Discovery no Kubernetes

```yaml
# prometheus.yml
scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: service
```

Anotações no pod para ativar scraping:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Grafana: Dashboards e Variáveis

```json
// Dashboard variable — seletor de serviço dinâmico
{
  "name": "service",
  "type": "query",
  "query": "label_values(http_requests_total, service)",
  "refresh": 2,
  "multi": true,
  "includeAll": true
}
```

```promql
# Panel: Request Rate com variável
sum(rate(http_requests_total{service=~"$service"}[5m])) by (service, status)
```

### Loki e LogQL

```logql
# Erros nos últimos 15 minutos por serviço
{namespace="production", app=~"$service"} |= "ERROR"
  | json
  | line_format "{{.service}} {{.level}} {{.message}}"

# Taxa de linhas de log de erro
sum(rate({namespace="production"} |= "ERROR" [5m])) by (app)

# Extração de campos e filtro
{app="api"}
  | logfmt
  | status_code >= 500
  | duration > 1s
  | line_format "{{.method}} {{.path}} {{.status_code}} {{.duration}}"
```

Correlação Loki → Grafana: configurar `derivedFields` para extrair `trace_id` dos logs e linkar diretamente no Tempo.

### Jaeger / Tempo: Distributed Tracing

```python
# Span manual com atributos
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer(__name__)

async def process_order(order_id: str):
    with tracer.start_as_current_span(
        "process_order",
        kind=SpanKind.INTERNAL,
        attributes={
            "order.id": order_id,
            "order.source": "api",
        }
    ) as span:
        try:
            result = await _validate_order(order_id)
            span.set_attribute("order.items_count", len(result.items))
            return result
        except OrderNotFound as e:
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR, str(e))
            raise
```

```yaml
# Tempo config com exemplars (link metrics → traces)
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: s3.amazonaws.com

distributor:
  receivers:
    otlp:
      protocols:
        grpc:

query_frontend:
  search:
    max_duration: 0   # busca ilimitada
```

### SLOs, SLIs e Error Budgets

```yaml
# SLO Definition (usando Sloth ou similar)
# 99.9% de requests retornam 2xx em < 500ms nos últimos 30 dias
slo:
  name: api-availability
  service: api
  objective: 99.9
  description: "API deve retornar respostas bem-sucedidas em menos de 500ms"

  sli:
    events:
      error_query: |
        sum(rate(http_requests_total{job="api", status=~"5.."}[{{.window}}]))
        +
        sum(rate(http_request_duration_seconds_count{job="api", le="0.5"}[{{.window}}]))
          - sum(rate(http_request_duration_seconds_bucket{job="api", le="0.5"}[{{.window}}]))
      total_query: |
        sum(rate(http_requests_total{job="api"}[{{.window}}]))

  alerting:
    page_alert:
      labels:
        severity: critical
    ticket_alert:
      labels:
        severity: warning
```

Error budget cálculo:
- 30 days × 0.1% = 43.2 minutos de downtime permitidos
- Burn rate 14.4x → esgota budget em 2h (alerta crítico)
- Burn rate 6x → esgota em 5h (alerta de atenção)

---

## Gotchas

> [!warning] Armadilhas de Observabilidade
> - **High cardinality**: labels com valores ilimitados (user_id, order_id) destroem o Prometheus. Use apenas labels de baixa cardinalidade.
> - **Alertas cause-based**: alertar em "CPU alta" ou "disco cheio" gera ruído. Alerte em sintomas: latência, error rate, saturation.
> - **Sampling de traces**: 100% sampling em produção é caro. Use tail-based sampling no OTel Collector para capturar apenas traces lentos/com erro.
> - **Log verbosity**: logs de debug em produção explodem storage do Loki. Configure níveis por ambiente.
> - **Clock skew**: traces distribuídos requerem NTP sincronizado entre todos os nós.

> [!danger] Prometheus Retention
> Prometheus por padrão retém dados por apenas 15 dias. Para histórico longo, use Thanos ou Cortex com object storage (S3/GCS). Sem isso, dashboards históricos ficam vazios.

---

## Snippets

```bash
# Verificar targets do Prometheus
curl http://prometheus:9090/api/v1/targets | jq '.data.activeTargets[] | {job, health, lastError}'

# Testar PromQL via API
curl -G http://prometheus:9090/api/v1/query \
  --data-urlencode 'query=up{job="api"}'

# Recarregar config do Prometheus sem restart
curl -X POST http://prometheus:9090/-/reload

# Verificar saúde do OTel Collector
curl http://otel-collector:13133/
```

---

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Google SRE Book — SLOs](https://sre.google/sre-book/service-level-objectives/)
- [Grafana Loki LogQL](https://grafana.com/docs/loki/latest/logql/)
- [Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)

## Related

- [[kubernetes-basics]] — service discovery e pod annotations
- [[docker]] — coleta de logs de containers
- [[github-actions]] — métricas de pipeline e deploy tracking
- [[fastapi]] — instrumentação da aplicação
- [[deployment-strategies]] — tracking de deploys no Grafana
