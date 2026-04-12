---
tags: [skill, architecture, microservices]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Microservices, Microsserviços]
---

# Microservices Architecture

## Overview

Microservices é um estilo arquitetural onde uma aplicação é decomposta em serviços pequenos, autônomos e deployáveis independentemente. Cada serviço roda em seu próprio processo, se comunica via mecanismos leves (HTTP/gRPC/mensageria) e é construído em torno de capacidades de negócio.

> [!important] Regra de Ouro
> Um microserviço deve poder ser reescrito em 2 semanas por um único desenvolvedor. Se for maior que isso, considere dividir.

A principal motivação não é técnica — é organizacional. Conway's Law diz que sistemas espelham estruturas de comunicação das organizações que os criam. Microservices permitem que times sejam autônomos end-to-end.

---

## Core Concepts

### Domain-Driven Design e Bounded Contexts

A decomposição correta de serviços começa por [[event-driven]] e domain analysis, não por entidades técnicas.

- **Bounded Context**: limite explícito dentro do qual um modelo de domínio é válido. "Order" em Vendas != "Order" em Logística.
- **Ubiquitous Language**: linguagem compartilhada entre devs e domain experts dentro de um bounded context.
- **Context Map**: diagrama de relacionamentos entre bounded contexts (upstream/downstream, shared kernel, anti-corruption layer).

> [!tip] Padrão Strangler Fig
> Para migrar um monolito: envolva o monolito com um proxy (API Gateway), migre funcionalidades gradualmente para novos serviços, e vá "estrangulando" o monolito. Nunca big-bang rewrite.

### Database per Service

Cada serviço possui seu próprio datastore — schema isolation é inegociável para autonomia real.

```sql
-- ❌ ERRADO: serviços compartilhando schema
SELECT o.*, u.email FROM orders o JOIN users.accounts u ON o.user_id = u.id;

-- ✅ CORRETO: serviço de orders chama API do serviço de users
-- GET /users/{id} -> { email: "..." }
-- Dados desnormalizados no próprio schema quando necessário
```

Consequências: joins cross-service viram chamadas de rede ou eventos. Eventual consistency é o preço da autonomia.

---

## Patterns

### Comunicação Síncrona: REST vs gRPC

| Aspecto | REST/HTTP | gRPC |
|---|---|---|
| Protocolo | HTTP/1.1, HTTP/2 | HTTP/2 obrigatório |
| Serialização | JSON (verbose) | Protobuf (binário, ~5x menor) |
| Contrato | OpenAPI (opcional) | `.proto` (obrigatório) |
| Streaming | SSE/WebSocket separado | Nativo (client/server/bidi) |
| Browser | Sim | Precisa grpc-web |

```protobuf
// user.proto — contrato forte entre serviços
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);
}

message GetUserRequest {
  string user_id = 1;
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  google.protobuf.Timestamp created_at = 4;
}
```

### Comunicação Assíncrona e Saga Pattern

Para transações distribuídas, o padrão Saga evita 2PC (two-phase commit), que é um antipadrão em microservices por criar acoplamento forte.

**Choreography Saga** — serviços reagem a eventos sem coordenador central:

```
OrderService  ──(OrderCreated)──►  InventoryService
                                         │
                               (InventoryReserved)
                                         │
                                         ▼
                                   PaymentService
                                         │
                              (PaymentProcessed)──► OrderService (completa)
                              (PaymentFailed) ──► InventoryService (compensa)
```

**Orchestration Saga** — um coordenador (orquestrador) dirige os participantes:

```python
# Orquestrador explícito — mais fácil de debugar, mas cria acoplamento
class CreateOrderSaga:
    async def execute(self, order_data: dict) -> SagaResult:
        # Step 1: Reserve inventory
        inventory_result = await self.inventory_client.reserve(order_data["items"])
        if not inventory_result.success:
            return SagaResult.failed("inventory_unavailable")

        # Step 2: Process payment
        payment_result = await self.payment_client.charge(order_data["payment"])
        if not payment_result.success:
            # Compensating transaction
            await self.inventory_client.release(inventory_result.reservation_id)
            return SagaResult.failed("payment_declined")

        # Step 3: Confirm order
        await self.order_repo.confirm(order_data["order_id"])
        return SagaResult.success()
```

> [!warning] Choreography vs Orchestration
> Choreography escala melhor mas é difícil de rastrear (qual serviço falhou?). Orchestration é mais simples de debugar mas o orquestrador vira God Object. Use [[observability]] com distributed tracing em ambos.

### API Gateway

O gateway é o ponto de entrada único para clientes externos. Responsabilidades:

- **Routing**: `GET /api/v1/orders` → Order Service
- **Rate Limiting**: token bucket, sliding window por client_id
- **Authentication**: JWT validation antes de encaminhar (offload dos serviços)
- **Request Aggregation**: BFF (Backend for Frontend) combina múltiplos serviços
- **Circuit Breaker**: evita cascade failures

```yaml
# Kong Gateway — declarativo
services:
  - name: order-service
    url: http://order-svc:8080
    routes:
      - name: orders-route
        paths: ["/api/v1/orders"]
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          policy: redis
      - name: jwt
        config:
          secret_is_base64: false
```

### Service Mesh

Um service mesh (Istio, Linkerd) injeta um sidecar proxy (Envoy) em cada pod, interceptando todo tráfego de rede. Isso move concerns transversais para fora do código da aplicação.

Capabilities sem mudança no código da aplicação:
- mTLS automático entre todos os serviços
- Circuit breaking e retry policies via CRDs
- Distributed tracing (sem instrumentação manual)
- Traffic splitting para canary deployments

```yaml
# Istio VirtualService — canary deployment 10% para v2
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: order-service
spec:
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: order-service
            subset: v2
    - route:
        - destination:
            host: order-service
            subset: v1
          weight: 90
        - destination:
            host: order-service
            subset: v2
          weight: 10
```

---

## Gotchas

> [!danger] Distributed Monolith
> O maior antipadrão: criar "microservices" que são deployados separadamente mas se chamam sincronamente em cadeia para cada request. Qualquer falha derruba tudo, mas você tem toda a complexidade de um sistema distribuído sem os benefícios.

> [!warning] Too Many Services Too Soon
> Microservices são o ponto de chegada, não de partida. Comece com um monolito bem modularizado ([[clean-architecture]]), identifique os bounded contexts reais com dados de produção, depois extraia serviços onde há necessidade clara (escala diferente, times diferentes, linguagens diferentes).

> [!bug] Chatty Services
> Se o serviço A faz 5 chamadas síncronas para o serviço B para processar 1 request, há vazamento de abstração. Redesenhe a API ou consolide os serviços.

**Checklist de health antes de ir para produção:**
- [ ] Health check endpoints `/health` e `/ready` implementados
- [ ] Circuit breaker configurado para todas as dependências externas
- [ ] Retry com exponential backoff + jitter
- [ ] Timeout definido em todas as chamadas de rede
- [ ] Structured logging com correlation ID
- [ ] Distributed tracing integrado ([[observability]])
- [ ] Graceful shutdown (drain connections, complete in-flight)

---

## Snippets

### Health Check Padronizado

```python
# FastAPI — health check para Kubernetes probes
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    dependencies: dict[str, str]

@app.get("/health/ready", response_model=HealthResponse)
async def readiness_probe():
    """Kubernetes readiness — falha se não pronto para tráfego."""
    deps = {}
    try:
        await db.execute("SELECT 1")
        deps["database"] = "ok"
    except Exception:
        deps["database"] = "error"
        return JSONResponse(status_code=503, content={"status": "not_ready"})

    return HealthResponse(
        status="ready",
        timestamp=datetime.utcnow(),
        dependencies=deps
    )

@app.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness — apenas confirma que o processo não travou."""
    return {"status": "alive"}
```

### Circuit Breaker com Tenacity

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, CircuitBreaker
)
import httpx

circuit_breaker = CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=0.5, max=10),
    retry=retry_if_exception_type(httpx.TransportError),
)
async def call_inventory_service(item_ids: list[str]) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            "http://inventory-svc/reserve",
            json={"item_ids": item_ids},
        )
        response.raise_for_status()
        return response.json()
```

---

## References

- **Building Microservices** — Sam Newman (2nd ed., 2021) — livro referência
- **Microservices Patterns** — Chris Richardson — padrões práticos com código
- [microservices.io](https://microservices.io) — catálogo de padrões por Chris Richardson
- [[kubernetes-basics]] — orquestração de containers para microservices
- [[docker]] — containerização e build pipelines
- [[messaging-patterns]] — comunicação assíncrona entre serviços
- [[observability]] — tracing, metrics, logs em sistemas distribuídos

---

## Related

- [[event-driven]] — arquitetura baseada em eventos, complementar a microservices
- [[clean-architecture]] — como estruturar o código dentro de cada serviço
- [[kubernetes-basics]] — plataforma de orquestração para microservices
- [[messaging-patterns]] — padrões de mensageria (pub/sub, queues, topics)
- [[docker]] — containerização dos serviços
- [[observability]] — instrumentação, tracing e alertas
