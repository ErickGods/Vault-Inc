---
tags: [skill, devops, deployment-strategies]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Deployment Strategies, Deploy]
---

# Deployment Strategies

## Overview

Estratégias de deployment determinam **como** uma nova versão de software substitui a anterior em produção. A escolha afeta diretamente disponibilidade, risco, velocidade de rollback, e custo de infraestrutura. Não existe estratégia universalmente superior — cada contexto (stateless vs stateful, tráfego crítico, capacidade de rollback de DB) exige uma escolha diferente.

As dimensões de avaliação são: **blast radius** (impacto se algo der errado), **tempo de rollback**, **consumo de recursos** durante o deploy, e **complexidade operacional**.

Ver também: [[github-actions]], [[gitlab-ci]], [[argocd]], [[kubernetes-basics]], [[feature-flags]], [[docker]]

---

## Core Concepts

### Blue/Green Deployment

Mantém dois ambientes idênticos (blue = atual, green = novo). O tráfego é redirecionado atomicamente após validação do green. Rollback é imediato: basta redirecionar de volta.

```
[Load Balancer]
      │
   100% ──► [Blue  v1.0]  ← ambiente atual
      │
      └──►  [Green v2.0]  ← ambiente novo (aquecendo)

Após switch:
      │
   100% ──► [Green v2.0]  ← novo ativo
      │
      └──►  [Blue  v1.0]  ← standby para rollback
```

**Implementação no Kubernetes:**

```yaml
# Service aponta para selector que muda entre blue e green
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
    slot: green          # muda de 'blue' para 'green' no switch
  ports:
    - port: 80
      targetPort: 8080
---
# Script de switch
kubectl patch service my-app \
  -p '{"spec":{"selector":{"slot":"green"}}}'
```

**Custo:** 2x infraestrutura durante o deploy. Ideal para deploys que precisam de rollback instantâneo e onde custo temporário é aceitável.

### Canary Releases

Roteia uma porcentagem do tráfego para a nova versão gradualmente. Permite detectar problemas com impacto limitado antes de afetar todos os usuários.

```yaml
# Nginx Ingress com canary annotation
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"   # 10% do tráfego
    # Alternativa: canary por header para QA interno
    nginx.ingress.kubernetes.io/canary-by-header: "X-Canary"
    nginx.ingress.kubernetes.io/canary-by-header-value: "always"
spec:
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-canary-svc
                port:
                  number: 80
```

**Progressão automatizada com métricas:**

```yaml
# Argo Rollouts — canary com análise automática
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: {duration: 10m}
        - analysis:
            templates:
              - templateName: success-rate
        - setWeight: 25
        - pause: {duration: 10m}
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100
      analysis:
        successCondition: "result[0] >= 0.99"   # 99% success rate
```

### Rolling Updates

Substitui instâncias gradualmente, uma a uma (ou em lotes). É o default do Kubernetes Deployment.

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2          # até 2 pods extras durante o update
      maxUnavailable: 0    # zero downtime — nunca mata antes de criar
  template:
    spec:
      containers:
        - name: app
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 3
            failureThreshold: 3
```

> [!important] maxUnavailable: 0 + maxSurge: 1
> Essa combinação garante zero downtime mas é mais lenta. Com `maxUnavailable: 1` e `maxSurge: 0`, nunca excede a capacidade mas tem momentos de capacidade reduzida.

---

## Patterns

### A/B Testing

Diferente de canary (foco em estabilidade), A/B testing divide usuários por critérios de negócio para comparar conversão/engagement.

```python
# Roteamento por user ID (sticky sessions)
def route_user(user_id: str) -> str:
    # hash determinístico garante que o mesmo usuário
    # sempre veja a mesma variante
    bucket = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
    if bucket < 50:
        return "variant-a"
    return "variant-b"
```

**Integração com [[feature-flags]]:** use flags para controlar qual variante o usuário recebe, com métricas coletadas por evento.

### Shadow / Dark Launching

Envia tráfego real para a nova versão em paralelo, mas descarta a resposta — valida comportamento sem afetar usuários.

```yaml
# Istio mirror policy
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
spec:
  http:
    - match:
        - uri:
            prefix: /api
      route:
        - destination:
            host: my-app-v1
          weight: 100
      mirror:
        host: my-app-v2    # recebe cópia do tráfego
      mirrorPercentage:
        value: 100.0
```

**Uso típico:** validar performance e comportamento de queries/caches antes de qualquer usuário real ser afetado.

### Zero-Downtime DB Migrations — Expand/Contract

```
Fase 1: EXPAND
  - Adiciona nova coluna (nullable ou com default)
  - Código novo lê/escreve em ambas as colunas
  - Deploy do código

Fase 2: BACKFILL
  - Script popula dados históricos na nova coluna
  - Roda em background, não bloqueia tabela

Fase 3: CONTRACT
  - Remove leitura da coluna antiga do código
  - Deploy
  - Remove coluna antiga da tabela
```

```sql
-- Fase 1: Expand — adiciona coluna sem NOT NULL
ALTER TABLE users ADD COLUMN phone_e164 VARCHAR(20);

-- Fase 2: Backfill em batches para não travar
UPDATE users
SET phone_e164 = normalize_phone(phone)
WHERE id BETWEEN $1 AND $2
  AND phone_e164 IS NULL;

-- Fase 3: Contract — após remover leitura do código
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users ALTER COLUMN phone_e164 SET NOT NULL;
```

### Rollback Strategies

| Estratégia | Tempo | Quando usar |
|---|---|---|
| Blue/Green switch | Segundos | App stateless, sem migração de schema |
| Kubernetes rollback | ~1-2 min | Rolling update, imagem anterior disponível |
| Feature flag kill switch | Milissegundos | Feature encapsulada em flag |
| DB point-in-time restore | 15-60 min | Corrupção de dados, último recurso |

```bash
# Rollback imediato no Kubernetes
kubectl rollout undo deployment/my-app
kubectl rollout undo deployment/my-app --to-revision=3

# Verificar histórico de revisions
kubectl rollout history deployment/my-app
```

---

## Gotchas

> [!bug] Canary com sessões stateful
> Se a aplicação usa sessões server-side (não JWT), o usuário pode alternar entre v1 e v2 na mesma sessão. Use sticky sessions (NGINX `ip_hash` ou cookie-based affinity) ou migre para tokens stateless.

> [!bug] Health checks insuficientes causam falsos positivos
> Um pod que passa no readiness check mas ainda está aquecendo cache/conexões pode receber tráfego prematuro. Use `startupProbe` separado do `readinessProbe` para separar "pronto para receber tráfego" de "processo inicializado".

> [!warning] Blue/Green + banco de dados compartilhado
> Se blue e green compartilham o mesmo banco, migrações de schema que removem colunas quebram a versão antiga imediatamente. Sempre use expand/contract e só faça contract após o blue ser aposentado.

> [!tip] Deployment Freeze Windows
> Em sistemas financeiros ou e-commerce, configure janelas de congelamento automáticas (Black Friday, fechamento fiscal). No Kubernetes, use `PodDisruptionBudget` com `maxUnavailable: 0` e bloqueie pipelines via branch protection ou approval gates no [[github-actions]] / [[gitlab-ci]].

---

## Snippets

### PodDisruptionBudget para Zero-Downtime

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
spec:
  minAvailable: "80%"    # garante 80% dos pods sempre disponíveis
  selector:
    matchLabels:
      app: my-app
```

### Health Check Endpoint Completo

```python
# FastAPI — endpoint de health com verificações reais
@app.get("/healthz")
async def health():
    checks = {}

    # DB check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Cache check
    try:
        await redis.ping()
        checks["cache"] = "ok"
    except Exception:
        checks["cache"] = "error"

    status = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    code = 200 if status == "healthy" else 503

    return JSONResponse({"status": status, "checks": checks}, status_code=code)
```

---

## References

- [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Argo Rollouts](https://argoproj.github.io/argo-rollouts/)
- [Martin Fowler — Branch by Abstraction](https://martinfowler.com/bliki/BranchByAbstraction.html)
- [Expand/Contract Pattern](https://www.prisma.io/dataguide/types/relational/expand-and-contract-pattern)

## Related

- [[github-actions]] — pipeline que executa o deploy
- [[gitlab-ci]] — pipeline alternativo
- [[argocd]] — GitOps com sync automático e rollback
- [[kubernetes-basics]] — primitivas (Deployment, Service, Ingress)
- [[feature-flags]] — complementa canary com controle fino
- [[docker]] — artefato imutável base para cada estratégia
