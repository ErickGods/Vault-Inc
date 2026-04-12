---
tags: [skill, devops, reverse-proxy]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Reverse Proxy, Nginx, Traefik, Caddy]
---

# Reverse Proxy

## Overview

Reverse proxy é o ponto central de entrada de trafego em qualquer infraestrutura moderna. Diferente de forward proxy (cliente -> proxy -> internet), reverse proxy fica na borda do servidor: recebe requisicoes externas e as distribui para backends internos. Alem de roteamento, concentra SSL/TLS termination, rate limiting, autenticacao, compressao e observabilidade em um unico ponto.

> [!info] Comparativo Rapido
> **Nginx** — alta performance, config declarativa, ecosystem maduro, melhor para trafego de alta carga.
> **Traefik** — auto-discovery via labels Docker/K8s, ideal para ambientes dinamicos com muitos servicos.
> **Caddy** — HTTPS automatico via ACME, config minimalista, excelente para projetos menores.

---

## Core Concepts

### Nginx — Estrutura e Configuracao Avancada

Nginx usa modelo event-driven non-blocking com workers. Cada `worker_process` lida com milhares de conexoes concorrentes sem criar threads.

**Estrutura hierarquica de configuracao:**
```nginx
# /etc/nginx/nginx.conf
worker_processes auto;  # Um worker por CPU core
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;           # Linux — mais eficiente que select/poll
    multi_accept on;
}

http {
    # Otimizacoes de performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;

    # Compressao
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript;

    # Upstream pool — backend servers
    upstream api_backend {
        least_conn;  # Algoritmo: least connections (melhor que round-robin para requests variaveis)
        server 10.0.0.10:3000 weight=3;
        server 10.0.0.11:3000 weight=1;
        server 10.0.0.12:3000 backup;  # Usado apenas se primarios falharem

        keepalive 32;  # Conexoes persistentes ao backend
    }

    include /etc/nginx/conf.d/*.conf;
}
```

**Virtual host com SSL/TLS e proxy reverso:**
```nginx
# /etc/nginx/conf.d/api.conf
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;  # Redirect HTTP -> HTTPS
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # Certificados
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # TLS hardening
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://api_backend;
        proxy_http_version 1.1;

        # Headers para backend saber o cliente real
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering — desabilitar para SSE/streaming
        proxy_buffering off;
    }

    # WebSocket proxying
    location /ws/ {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;  # Manter conexao WebSocket aberta
    }

    # Health check endpoint (nao logado)
    location /health {
        access_log off;
        proxy_pass http://api_backend;
    }
}
```

### Traefik — Auto-Discovery com Docker e Kubernetes

Traefik le labels de containers Docker ou anotacoes de recursos Kubernetes em tempo real, sem necessidade de reiniciar ou recarregar config.

**`docker-compose.yml` com Traefik:**
```yaml
services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=false"
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--metrics.prometheus=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`traefik.example.com`)"
      - "traefik.http.routers.dashboard.tls=true"
      - "traefik.http.routers.dashboard.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=admin:$$apr1$$..."

  api:
    image: myapi:latest
    labels:
      - "traefik.enable=true"
      # Router
      - "traefik.http.routers.api.rule=Host(`api.example.com`) && PathPrefix(`/v1`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      # Middlewares encadeados
      - "traefik.http.routers.api.middlewares=rate-limit@docker,headers@docker"
      # Rate limiting middleware
      - "traefik.http.middlewares.rate-limit.ratelimit.average=100"
      - "traefik.http.middlewares.rate-limit.ratelimit.burst=50"
      # Security headers middleware
      - "traefik.http.middlewares.headers.headers.stsSeconds=31536000"
      - "traefik.http.middlewares.headers.headers.stsIncludeSubdomains=true"
      # Service — porta do container
      - "traefik.http.services.api.loadbalancer.server.port=3000"
      # Health check
      - "traefik.http.services.api.loadbalancer.healthcheck.path=/health"
      - "traefik.http.services.api.loadbalancer.healthcheck.interval=10s"
```

**Traefik IngressRoute para Kubernetes:**
```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: api-route
  namespace: production
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`api.example.com`) && PathPrefix(`/v1`)
      kind: Rule
      services:
        - name: api-service
          port: 3000
      middlewares:
        - name: rate-limit
        - name: strip-prefix
  tls:
    certResolver: letsencrypt
---
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: strip-prefix
spec:
  stripPrefix:
    prefixes:
      - /v1
```

### Caddy — HTTPS Automatico e Caddyfile

```caddyfile
# Caddyfile — HTTPS automatico via Let's Encrypt ou ZeroSSL
{
    email admin@example.com
    # Usar staging ACME para testes
    # acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
}

api.example.com {
    # Proxy reverso simples
    reverse_proxy /api/* backend:3000 {
        # Load balancing entre multiplos backends
        to backend1:3000 backend2:3000 backend3:3000
        lb_policy round_robin

        # Health checks
        health_uri /health
        health_interval 10s
        health_timeout 2s

        # Headers
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }

    # Rate limiting via Caddy plugin
    rate_limit {
        zone dynamic {
            key {remote_host}
            events 100
            window 1m
        }
    }

    # Logging estruturado
    log {
        output file /var/log/caddy/access.log
        format json
    }
}
```

---

## Patterns

### SSL/TLS Termination

O proxy termina SSL e se comunica com backends via HTTP interno. Reduz carga de CPU nos backends e centraliza gestao de certificados.

```
Client --[HTTPS]--> Reverse Proxy --[HTTP]--> Backend
                  (SSL terminado aqui)
```

Para comunicacao backend segura (mTLS interno), use certificados internos ou [[vpn-setup]].

### Health Checks e Circuit Breaker

```nginx
# Nginx — remover backend unhealthy automaticamente
upstream api_backend {
    server 10.0.0.10:3000;
    server 10.0.0.11:3000;

    # Remover apos 3 falhas em 30s, tentar novamente apos 30s
    server 10.0.0.10:3000 max_fails=3 fail_timeout=30s;
}
```

### Comparativo

| Feature              | Nginx         | Traefik       | Caddy         |
|----------------------|---------------|---------------|---------------|
| Auto-discovery       | No            | Yes (Docker/K8s) | Limited    |
| HTTPS automático     | Manual/certbot | Yes (ACME)   | Yes (nativo)  |
| Performance          | Excelente     | Bom           | Bom           |
| Config hot-reload    | Parcial       | Total         | Total         |
| Dashboard UI         | Nginx Plus    | Built-in      | Plugin        |
| Ecosystem/plugins    | Enorme        | Bom           | Crescendo     |

---

## Gotchas

> [!warning] X-Forwarded-For e Seguranca
> Nunca confie em `X-Forwarded-For` sem configurar `set_real_ip_from` no Nginx. Um cliente malicioso pode forjar este header para bypassar rate limiting por IP.

> [!bug] WebSocket e Timeouts
> WebSockets precisam de `proxy_read_timeout` alto (ex: 3600s). O default de 60s fecha conexoes inativas, causando reconexoes frequentes em clientes.

> [!warning] Traefik Docker Socket Security
> Montar `/var/run/docker.sock` no Traefik e equivalente a acesso root no host. Use socket proxy (tecnologiaseguranca/docker-socket-proxy) para limitar acesso.

> [!tip] Buffering e Streaming
> Para SSE (Server-Sent Events) ou streaming responses, desabilite `proxy_buffering off` no Nginx. Com buffering ativo, o cliente nao recebe dados ate o buffer encher.

---

## Snippets

```bash
# Testar config Nginx sem reiniciar
nginx -t && nginx -s reload

# Verificar qual upstream esta recebendo trafego (Nginx Plus / stub_status)
curl http://localhost/nginx_status

# Traefik — ver rotas ativas via API
curl http://localhost:8080/api/http/routers | jq '.[] | {name: .name, rule: .rule}'
```

```bash
# Gerar certificado self-signed para testes internos
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt \
  -subj "/CN=internal.example.com"
```

---

## References

- [Nginx Docs — ngx_http_proxy_module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [Traefik v3 Documentation](https://doc.traefik.io/traefik/)
- [Caddy Documentation](https://caddyserver.com/docs/)

---

## Related

- [[docker]] — Containers como backends do proxy
- [[kubernetes-basics]] — IngressRoute e Ingress controllers
- [[dns-and-cdn]] — DNS apontando para o proxy, CDN na frente
- [[vpn-setup]] — Acesso a servicos internos sem expor publicamente
- [[deployment-strategies]] — Blue/Green e Canary com upstream Nginx
