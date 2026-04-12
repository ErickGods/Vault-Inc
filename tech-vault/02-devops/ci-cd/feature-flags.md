---
tags: [skill, devops, feature-flags]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Feature Flags, Feature Toggles]
---

# Feature Flags

## Overview

Feature flags (também chamados feature toggles) são condicionais em runtime que controlam a ativação de comportamentos sem novo deploy. São a cola entre [[deployment-strategies]] e desenvolvimento contínuo: permitem que código seja deployado em produção mas não ativado, desacoplando **deploy** de **release**.

Sem feature flags, toda mudança de comportamento exige um deploy — e todo deploy é um momento de risco. Com flags, você pode deployar código inacabado (escondido atrás da flag), ativar para um subset de usuários, executar experimentos A/B com métricas, e desligar features problemáticas instantaneamente sem rollback.

São fundamentais para trunk-based development: todo mundo commita no mesmo branch, features incompletas ficam encapsuladas em flags.

Ver também: [[deployment-strategies]], [[github-actions]], [[observability]], [[fastapi]], [[nextjs]]

---

## Core Concepts

### Tipos de Feature Flags

| Tipo | Vida útil | Uso | Exemplo |
|---|---|---|---|
| **Release** | Dias/semanas | Rollout gradual de feature | Nova UI de checkout |
| **Experiment** | Semanas | A/B testing com métricas | Botão verde vs azul |
| **Ops** | Permanente | Kill switch operacional | Circuit breaker de feature |
| **Permission** | Permanente | Entitlement por plano/papel | Feature premium |

> [!important] Flags são dívida técnica
> Flags release e experiment têm vida curta por design. Flags que não são removidas após o rollout viram "flag debt" — código morto condicional que nunca é limpo. Trate cada flag como um ticket de cleanup com deadline.

### Plataformas: Comparação

**LaunchDarkly**
- SaaS maduro, baixíssima latência via SDK com cache local (flag rules não precisam de chamada de rede por request)
- Experimentos com análise estatística integrada
- RBAC granular, aprovações, auditoria completa
- Custo: caro para scale — pricing por MAU

**Unleash**
- Open-source, self-hosted ou cloud
- Estratégias nativas: gradualRollout, userWithId, remoteAddress, applicationHostname
- SDK em todas as linguagens principais
- Custo: infra própria no self-hosted; previsível em escala

**Flagsmith**
- Open-source, foco em feature flags + remote config
- Suporta flags com **valores** (não só boolean): strings, JSON, números
- Ideal para configuração dinâmica além de flags binárias
- Edge API para performance

---

## Patterns

### Implementação com LaunchDarkly (Python)

```python
import ldclient
from ldclient.config import Config
from ldclient import Context

# Inicialização — única vez na startup
ldclient.set_config(Config("sdk-key-here"))
client = ldclient.get()

# Context rico — base para targeting rules
def build_ld_context(user) -> Context:
    return Context.builder(user.id) \
        .kind("user") \
        .set("email", user.email) \
        .set("plan", user.subscription_plan) \
        .set("country", user.country) \
        .set("beta_tester", user.is_beta_tester) \
        .build()

# Avaliação de flag
def show_new_checkout(user) -> bool:
    context = build_ld_context(user)
    return client.variation("new-checkout-ui", context, False)

# Flag com variation detail — para logging/debugging
def get_checkout_variant(user) -> str:
    context = build_ld_context(user)
    detail = client.variation_detail("checkout-experiment", context, "control")
    # detail.reason contém por que essa variation foi retornada
    logger.debug("Flag reason: %s", detail.reason)
    return detail.value
```

### Implementação com Unleash (TypeScript / Next.js)

```typescript
// lib/unleash.ts
import { initialize, isEnabled, getVariant } from "unleash-client";

export const unleash = initialize({
  url: process.env.UNLEASH_URL!,
  appName: "my-nextjs-app",
  customHeaders: {
    Authorization: process.env.UNLEASH_API_TOKEN!,
  },
  refreshInterval: 15,      // polling a cada 15s
  metricsInterval: 60,
});

// Hook React para Server Components
export async function isFeatureEnabled(
  flagName: string,
  userId: string,
  properties?: Record<string, string>
): Promise<boolean> {
  return isEnabled(flagName, {
    userId,
    properties,
    sessionId: properties?.sessionId,
  });
}

// Em um Server Component Next.js
// app/checkout/page.tsx
import { isFeatureEnabled } from "@/lib/unleash";
import { auth } from "@/lib/auth";

export default async function CheckoutPage() {
  const session = await auth();
  const showNewFlow = await isFeatureEnabled(
    "new-checkout-flow",
    session.user.id,
    { plan: session.user.plan }
  );

  return showNewFlow ? <NewCheckout /> : <LegacyCheckout />;
}
```

### Gradual Rollout com Percentagem

```python
# Unleash — estratégia gradualRollout
# Configurado via UI/API: rollout 0% → 5% → 25% → 50% → 100%

# LaunchDarkly — targeting rule por percentagem
# UI: "Roll out to 10% of users" → métrica → aumenta gradualmente

# Implementação manual (quando não tem plataforma)
import hashlib

def is_in_rollout(user_id: str, flag_name: str, percentage: int) -> bool:
    """
    Determinístico: mesmo user_id + flag_name sempre retorna o mesmo resultado.
    Muda o salt (flag_name) para cada flag — evita que os mesmos 10%
    sejam sempre os primeiros a ver tudo.
    """
    key = f"{flag_name}:{user_id}"
    hash_value = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)
    bucket = hash_value % 100
    return bucket < percentage
```

### Kill Switches com FastAPI

```python
# Kill switch para feature problemática — desabilita imediatamente
from fastapi import APIRouter, Depends, HTTPException
from functools import wraps

router = APIRouter()

def require_feature(flag_name: str):
    """Decorator que rejeita a request se a feature estiver desabilitada."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request, **kwargs):
            user = request.state.user
            if not await feature_flag_service.is_enabled(flag_name, user.id):
                raise HTTPException(
                    status_code=404,
                    detail="Feature not available"
                )
            return await func(*args, request=request, **kwargs)
        return wrapper
    return decorator

@router.post("/api/v2/checkout")
@require_feature("new-checkout-api")
async def new_checkout(request: Request, body: CheckoutRequest):
    # Automaticamente retorna 404 se flag desabilitada
    return await checkout_service.process_v2(body)
```

### Experimentação com Métricas (A/B Testing)

```python
# Integração flag + evento de métricas
async def handle_checkout(user_id: str, cart: Cart):
    variant = ld_client.variation("checkout-cta-text", context, "control")

    # Track event para análise
    ld_client.track(
        "checkout_completed",
        context,
        metric_value=float(cart.total)
    )

    # Também enviar para [[observability]] (Datadog, Grafana)
    metrics.increment(
        "checkout.completed",
        tags=[
            f"variant:{variant}",
            f"user_plan:{user.plan}",
        ],
        value=cart.total
    )

    return variant
```

> [!tip] Significância estatística
> Não analise resultados antes de atingir o tamanho de amostra calculado. Use calculadoras de power analysis (ex: Evan Miller's) para definir quantos usuários/conversões são necessários para detectar o efeito mínimo relevante com 95% de confiança.

### Trunk-Based Development com Flags

```python
# ANTES: branch de feature separado por semanas
# git checkout -b feature/new-recommendation-engine

# DEPOIS: tudo no trunk, encapsulado em flag
class ProductRecommendationService:
    async def get_recommendations(self, user_id: str) -> list[Product]:
        if await flags.is_enabled("ml-recommendations-v2", user_id):
            # Novo algoritmo ML — em desenvolvimento
            return await self._ml_recommendations(user_id)
        else:
            # Algoritmo atual — sempre funcional
            return await self._collaborative_filter(user_id)

    async def _ml_recommendations(self, user_id: str) -> list[Product]:
        # Pode estar incompleto — nunca ativado em prod até pronto
        ...
```

### Flag Lifecycle Management

```
1. CREATE   → Flag criada com descrição, owner, e data de expiração planejada
2. ROLLOUT  → 0% → 5% → 25% → 50% → 100% com gate de métricas entre cada step
3. STABLE   → Flag em 100%, código legacy ainda existe
4. CLEANUP  → Remove branch morto do código, deleta a flag
5. (DEAD)   → Flag nunca limpa → flag debt → comportamento inesperado em prod
```

```bash
# Automação: listar flags não alteradas há mais de 30 dias (LaunchDarkly API)
curl -H "Authorization: $LD_API_TOKEN" \
  "https://app.launchdarkly.com/api/v2/flags/my-project" \
  | jq '.items[] | select(.updatedDate < (now - 30*24*3600) * 1000) | .key'
```

---

## Gotchas

> [!bug] Flag evaluation em hot paths
> Em endpoints com alto throughput, cada avaliação de flag que faz chamada de rede adiciona latência. Use SDKs com cache local (LaunchDarkly streaming, Unleash bootstrap) — a flag é avaliada in-memory, não via HTTP.

> [!bug] Inconsistência em operações assíncronas
> Se um job em background roda com uma variante diferente da que o usuário viu no frontend, podem ocorrer estados inconsistentes. Passe a variante escolhida como parâmetro explícito, não reavalie no worker.

> [!warning] Flags em testes automatizados
> Nunca dependa do estado de flags em testes de integração sem controle explícito. Use SDK mock/stub ou um ambiente de flags dedicado para CI. Flags alteradas em prod não devem quebrar testes.

> [!tip] Remote Config além de booleans
> Flags com valores (Flagsmith, LaunchDarkly multivariate) permitem mudar configurações sem deploy: timeouts, limites de rate limiting, textos de UI, URLs de APIs. Mais poderoso que variáveis de ambiente que exigem restart.

---

## Snippets

### Bootstrap com Flagsmith (zero network latency)

```python
import flagsmith
from flagsmith import Flagsmith

# Bootstrap com flags do último estado conhecido
# Nunca falha se o servidor Flagsmith estiver offline
client = Flagsmith(
    environment_key="env-key",
    default_flag_handler=lambda flag_name: DefaultFlag(
        enabled=False,
        value=None
    ),
    enable_local_evaluation=True,   # avalia localmente com regras cacheadas
)

flags = client.get_environment_flags()
is_dark_mode = flags.is_feature_enabled("dark_mode")
api_timeout = flags.get_feature_value("api_timeout_ms") or 5000
```

### Cleanup Automatizado via CI

```yaml
# .github/workflows/flag-audit.yml
on:
  schedule:
    - cron: "0 9 * * 1"   # toda segunda-feira às 9h

jobs:
  audit-flags:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Find stale flags in code
        run: |
          # Busca flags no código que não existem mais no LaunchDarkly
          grep -rh 'variation("\|is_enabled("' src/ \
            | grep -oP '(?<=")[a-z-]+(?=")' \
            | sort -u > flags-in-code.txt
          # Comparar com flags ativas na plataforma
          # Criar issues para flags obsoletas
```

---

## References

- [LaunchDarkly Documentation](https://docs.launchdarkly.com/)
- [Unleash Documentation](https://docs.getunleash.io/)
- [Flagsmith Documentation](https://docs.flagsmith.com/)
- [Pete Hodgson — Feature Toggles](https://martinfowler.com/articles/feature-toggles.html)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)

## Related

- [[deployment-strategies]] — flags como alternativa a canary para controle fino
- [[github-actions]] — pipeline não precisa saber de flags — deploy e release desacoplados
- [[observability]] — métricas de experimentos e monitoramento de variantes
- [[fastapi]] — implementação de flags em APIs Python
- [[nextjs]] — flags em Server Components e edge runtime
