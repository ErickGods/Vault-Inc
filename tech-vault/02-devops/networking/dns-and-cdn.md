---
tags: [skill, devops, dns-cdn]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [DNS, CDN, Cloudflare]
---

# DNS and CDN

## Overview

DNS (Domain Name System) e CDN (Content Delivery Network) sao as camadas de distribuicao e resolucao que precedem qualquer requisicao a sua infraestrutura. Dominar DNS significa entender TTLs, propagacao, registros especializados e armadilhas de cache. CDN vai alem de "cache de arquivos estaticos" — e sobre edge computing, WAF, DDoS mitigation e latencia global.

> [!info] DNS Resolution Chain
> `Browser Cache -> OS Cache -> Resolver ISP -> Root Nameservers -> TLD Nameservers -> Authoritative Nameserver`
> Cada elo tem TTL diferente. Problemas de propagacao sempre acontecem no cache do resolver do ISP.

---

## Core Concepts

### DNS Records — Tipos Essenciais

```
; Zona DNS completa — exemplo.com
; A Record — IPv4
exemplo.com.        300   IN  A     203.0.113.10
www.exemplo.com.    300   IN  A     203.0.113.10

; AAAA Record — IPv6
exemplo.com.        300   IN  AAAA  2001:db8::1

; CNAME — alias para outro hostname (NAO pode ser no apex/root do dominio)
blog.exemplo.com.   3600  IN  CNAME  sites.wordpress.com.
cdn.exemplo.com.    3600  IN  CNAME  d1234abcd.cloudfront.net.

; MX — mail exchange (prioridade: menor = preferencial)
exemplo.com.        3600  IN  MX  10  mail1.example.com.
exemplo.com.        3600  IN  MX  20  mail2.example.com.

; TXT — verificacao de dominio, SPF, DKIM
exemplo.com.        3600  IN  TXT  "v=spf1 include:_spf.google.com ~all"
_dkim._domainkey    3600  IN  TXT  "v=DKIM1; k=rsa; p=MIGfMA0GCS..."
_dmarc.exemplo.com. 3600  IN  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@exemplo.com"

; SRV — servicos com porta especifica
_sip._tcp.exemplo.com. 3600 IN SRV 10 5 5060 sip.exemplo.com.
; formato: prioridade peso porta destino

; NS — nameservers autoritativos
exemplo.com.        86400 IN  NS    ns1.cloudflare.com.
exemplo.com.        86400 IN  NS    ns2.cloudflare.com.

; CAA — Certificate Authority Authorization (seguranca SSL)
exemplo.com.        3600  IN  CAA  0 issue "letsencrypt.org"
exemplo.com.        3600  IN  CAA  0 issue "digicert.com"
```

**CNAME Flattening** — Cloudflare e Route53 resolvem CNAME no apex do dominio retornando A records diretamente, contornando a limitacao do RFC.

```
; Sem CNAME flattening (invalido):
exemplo.com. CNAME myapp.elb.amazonaws.com.  ; ERRO — apex nao permite CNAME

; Com CNAME flattening (Cloudflare/Route53 ALIAS):
; Query para exemplo.com -> Cloudflare resolve myapp.elb.amazonaws.com -> retorna A records
; Cliente ve apenas A records, nunca o CNAME
```

### Cloudflare — Configuracao Avancada

**Modos de proxy:**
- **DNS Only (cinza)**: Cloudflare apenas resolve, sem proxy. IP real exposto.
- **Proxied (laranja)**: Trafego passa pelos IPs da Cloudflare. IP real oculto. WAF/DDoS/Cache ativo.

**Page Rules e Transform Rules:**
```
# Page Rule — Cache Everything para /static/*
URL Pattern: exemplo.com/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 4 hours

# Redirect Rule — www para apex
If: hostname equals www.exemplo.com
Then: redirect to https://exemplo.com${uri} (301)
```

**Workers — Edge Functions:**
```javascript
// Worker: A/B testing no edge, sem latencia de origem
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Ler cookie de variante ou sortear nova
    let variant = request.headers.get('Cookie')?.match(/variant=(\w+)/)?.[1];
    if (!variant) {
      variant = Math.random() < 0.5 ? 'control' : 'experiment';
    }

    // Rotear para origins diferentes por variante
    const origin = variant === 'experiment'
      ? 'https://new-backend.example.com'
      : 'https://old-backend.example.com';

    const response = await fetch(new URL(url.pathname, origin), request);

    // Injetar cookie de variante na resposta
    const newResponse = new Response(response.body, response);
    newResponse.headers.append('Set-Cookie', `variant=${variant}; Path=/; Max-Age=86400`);
    return newResponse;
  }
};
```

**WAF Custom Rules:**
```
# Bloquear requests sem User-Agent valido (bots simples)
(not http.user_agent matches "Mozilla|Chrome|Safari|curl|wget")
AND (http.request.method in {"GET" "POST"})
=> BLOCK

# Rate limit por IP em /api/login
(http.request.uri.path eq "/api/login")
=> Rate Limit: 5 requests/minute per IP => BLOCK 60s

# Desafio CAPTCHA para paises de alto risco
(ip.geoip.country in {"CN" "RU" "KP"})
AND (not ip.src in {<trusted_ips>})
=> MANAGED_CHALLENGE
```

### AWS Route53 — Routing Policies

```bash
# Criar hosted zone
aws route53 create-hosted-zone \
  --name exemplo.com \
  --caller-reference $(date +%s)

# Failover routing — primario/secundario automatico
aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.exemplo.com",
      "Type": "A",
      "SetIdentifier": "primary",
      "Failover": "PRIMARY",
      "HealthCheckId": "abc-health-check-id",
      "AliasTarget": {
        "HostedZoneId": "Z35SXDOTRQ7X7K",
        "DNSName": "primary-alb.us-east-1.elb.amazonaws.com",
        "EvaluateTargetHealth": true
      }
    }
  }]
}'

# Latency-based routing — roteamento pelo menor RTT
# Route53 mede latencia do cliente para cada regiao AWS
# Cria um record por regiao:
# - api.exemplo.com -> us-east-1 (para clientes na America)
# - api.exemplo.com -> eu-west-1 (para clientes na Europa)
# - api.exemplo.com -> ap-southeast-1 (para clientes na Asia)

# Weighted routing — canary deployment via DNS
# 95% do trafego para v1, 5% para v2
# Weight: 95 -> production-alb
# Weight: 5  -> canary-alb
```

### CDN Caching Strategies

**Cache-Control headers e semantica:**
```http
# Cache publico por 1 hora, pode ser revalidado em stale
Cache-Control: public, max-age=3600, stale-while-revalidate=60, stale-if-error=86400

# Imutavel — nunca revalidar (use com hash no filename)
Cache-Control: public, max-age=31536000, immutable

# Privado — apenas browser, nunca CDN
Cache-Control: private, max-age=300

# Sem cache — sempre buscar na origem (mas pode revalidar com ETag)
Cache-Control: no-cache

# Sem armazenamento em lugar algum
Cache-Control: no-store
```

**Estrategia de cache por tipo de conteudo:**
```
/static/js/app.[hash].js    -> max-age=31536000, immutable  (hash muda com deploy)
/static/images/logo.svg     -> max-age=86400                (versao relativamente estavel)
/api/v1/products            -> max-age=60, s-maxage=300      (CDN cache maior que browser)
/api/v1/user/profile        -> private, max-age=0            (dado pessoal, sem CDN)
/                           -> no-cache                       (sempre verificar nova versao)
```

**`s-maxage`** — TTL especifico para CDNs (shared caches), substitui `max-age` para proxies.

**Vary header** — instrui CDN a criar entradas de cache separadas por header:
```http
Vary: Accept-Encoding   # Cache separado para gzip vs identity
Vary: Accept-Language   # Cache separado por idioma (cuidado: aumenta miss rate)
```

### DDoS Protection em Camadas

```
Camada 3/4 (Network/Transport):
├── Cloudflare Magic Transit — absorve volumetric DDoS (Tbps)
├── AWS Shield Advanced — proteção em ELB, CloudFront, Route53
└── Anycast routing — trafego absorvido em multiple PoPs

Camada 7 (Application):
├── Cloudflare WAF — bloqueia HTTP flood, SQLi, XSS
├── Rate limiting por IP, ASN, country
├── Bot Management (ML-based) — distingue bots legítimos de maliciosos
└── Challenge pages (CAPTCHA/JS challenge) para IPs suspeitos
```

---

## Patterns

### DNS Propagation e TTL Strategy

```bash
# Verificar propagacao global
dig +short @8.8.8.8 api.exemplo.com A       # Google DNS
dig +short @1.1.1.1 api.exemplo.com A       # Cloudflare DNS
dig +short @208.67.222.222 api.exemplo.com A # OpenDNS

# Verificar TTL atual
dig api.exemplo.com A +ttl

# Antes de mudanca importante:
# 1. Reduzir TTL para 60s com 24-48h de antecedencia
# 2. Realizar a mudanca de IP/CNAME
# 3. Apos propagacao confirmar, aumentar TTL novamente
```

### Multi-CDN Strategy

Distribuir trafego entre Cloudflare e CloudFront para resiliencia:

```
DNS (Route53 Weighted):
  60% -> Cloudflare (proxy para origem)
  40% -> CloudFront (distribution para mesma origem)

Vantagens:
- Failover automatico se um CDN tiver outage
- Melhor cobertura global (PoPs diferentes)
- Evitar vendor lock-in
```

### Edge Functions vs Origin

```javascript
// Decisao: processar no edge vs origem

// BOM para edge (baixa latencia, sem estado):
// - Autenticacao JWT (verificar assinatura, sem DB lookup)
// - Redirecionamentos geograficos
// - A/B testing via cookie
// - Compressao de response
// - Header manipulation

// RUIM para edge (precisa de estado ou recursos):
// - Queries ao banco de dados
// - Operacoes que precisam de filesystem
// - Processos com alto consumo de CPU/memoria
// - Chamadas a APIs internas com latencia variavel
```

---

## Gotchas

> [!warning] CNAME no Apex e Email
> Usar ALIAS/CNAME flattening no apex pode interferir com registros MX se mal configurado. Sempre verifique que MX records estao na mesma zona e nao dependem do CNAME.

> [!bug] Cloudflare Orange Cloud e IP Exposure
> Sub-dominios sem proxy (DNS only) expoe IPs reais. Um atacante pode mapear todos os sub-dominios para encontrar IPs de origem. Use Cloudflare Spectrum ou certifique que todos os sub-dominios relevantes estao proxied.

> [!warning] Cache Poisoning via Vary
> `Vary: *` instrui CDNs a nunca cachear a resposta. Alguns headers em `Vary` aumentam drasticamente o espaco de cache e reduzem hit rate. Prefira `Accept-Encoding` apenas.

> [!tip] DNS sobre HTTPS (DoH) e Privacidade
> Requests DNS em texto puro podem ser interceptados. Cloudflare (1.1.1.1), Google (8.8.8.8) e browsers modernos suportam DoH. Em infra corporativa, considere DNS privado via [[vpn-setup]] ou resolver interno.

---

## Snippets

```bash
# Verificar todos os records de um dominio
dig exemplo.com ANY +noall +answer

# Trace completo da resolucao DNS
dig +trace api.exemplo.com

# Testar resposta de CDN (headers de cache)
curl -sI https://api.exemplo.com/products | grep -E "cache|age|cf-|x-cache"

# Purge de cache Cloudflare via API
curl -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"files":["https://exemplo.com/api/products"]}'
```

```python
# Monitorar TTL e alertar se proximo de expirar
import dns.resolver
import time

def check_record_ttl(domain, record_type='A', threshold=300):
    answers = dns.resolver.resolve(domain, record_type)
    ttl = answers.rrset.ttl
    if ttl < threshold:
        print(f"WARN: {domain} TTL={ttl}s (abaixo de {threshold}s)")
    return ttl
```

---

## References

- [Cloudflare Learning — DNS](https://www.cloudflare.com/learning/dns/)
- [AWS Route53 Routing Policies](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [MDN — Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control)

---

## Related

- [[reverse-proxy]] — Proxy na frente do CDN/DNS para servicos internos
- [[cloudinary]] — CDN especializado em imagens e transformacoes
- [[s3-storage-patterns]] — S3 como origem para CloudFront
- [[deployment-strategies]] — DNS-based routing para canary/blue-green
- [[vpn-setup]] — DNS privado e resolucao interna via VPN
