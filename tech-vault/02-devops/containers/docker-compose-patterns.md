---
tags: [skill, devops, docker-compose]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Docker Compose, Compose]
---

# Docker Compose Patterns

## Overview

Docker Compose é a ferramenta padrão para orquestração multi-serviço em ambientes locais e de staging. Vai muito além do `docker run` encadeado — suporta profiles, health checks condicionais, extensão via YAML anchors, redes customizadas e override files para múltiplos ambientes. Dominar esses padrões é prerequisito para trabalhar bem com [[docker]] e preparar deploys para [[kubernetes-basics]].

> [!tip] Compose vs K8s
> Compose é ideal para dev/test local e stacks pequenas em produção. Para orquestração em escala, [[kubernetes-basics]] é a escolha certa. O Compose pode ser convertido via `kompose convert`.

---

## Core Concepts

### Extension Fields (x-) e YAML Anchors

Evite repetição de configuração com campos de extensão e âncoras YAML:

```yaml
# docker-compose.yml
x-common-env: &common-env
  TZ: America/Sao_Paulo
  LOG_LEVEL: info

x-restart-policy: &restart-policy
  restart: unless-stopped

x-healthcheck-defaults: &hc-defaults
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

services:
  api:
    <<: *restart-policy
    environment:
      <<: *common-env
      DATABASE_URL: postgresql://user:pass@db:5432/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      <<: *hc-defaults

  worker:
    <<: *restart-policy
    environment:
      <<: *common-env
      QUEUE_URL: redis://redis:6379/0
```

### Profiles para Dev / Test / Prod

Profiles permitem ativar serviços seletivamente sem múltiplos arquivos:

```yaml
services:
  api:
    build: .
    # sem profile = sempre ativo

  db:
    image: postgres:16-alpine
    profiles: [dev, test, prod]

  pgadmin:
    image: dpage/pgadmin4
    profiles: [dev]          # apenas desenvolvimento

  mailhog:
    image: mailhog/mailhog
    profiles: [dev, test]    # intercepta e-mails localmente

  prometheus:
    image: prom/prometheus
    profiles: [monitoring]

  nginx:
    image: nginx:alpine
    profiles: [prod]
```

```bash
# Iniciar apenas serviços de dev
docker compose --profile dev up -d

# Iniciar prod + monitoring
docker compose --profile prod --profile monitoring up -d
```

### Health Checks e depends_on Conditions

`depends_on` com `condition` garante ordem de inicialização baseada em saúde real, não apenas na presença do container:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  migrations:
    build:
      context: .
      target: migrations
    depends_on:
      db:
        condition: service_healthy
    command: alembic upgrade head

  api:
    build: .
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrations:
        condition: service_completed_successfully
    ports:
      - "8000:8000"
```

---

## Patterns

### Volumes: Named, Bind e tmpfs

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data          # named volume (gerenciado pelo Docker)
      - ./init-scripts:/docker-entrypoint-initdb.d:ro  # bind mount read-only

  api:
    build: .
    volumes:
      - .:/app                                    # bind mount para hot-reload
      - /app/node_modules                         # volume anônimo (preserva node_modules)

  cache-warmer:
    image: alpine
    tmpfs:
      - /tmp:size=100m,mode=1777                  # tmpfs para dados temporários

volumes:
  pgdata:
    driver: local
    driver_opts:
      type: none
      device: /data/postgres    # path no host para produção
      o: bind
```

Integração com [[postgresql]] requer atenção aos modos de mount para evitar problemas de permissão no `initdb`.

### Redes Customizadas e Aliases

```yaml
services:
  api:
    networks:
      frontend:
        aliases: [api-service]
      backend:

  db:
    image: postgres:16-alpine
    networks:
      backend:
        aliases: [database, postgres]   # múltiplos aliases para compatibilidade

  redis:
    image: redis:7-alpine
    networks:
      backend:
        aliases: [cache]

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    networks:
      frontend:

networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
  backend:
    driver: bridge
    internal: true    # sem acesso à internet
```

Usando [[redis]] como cache com alias `cache` permite trocar a implementação sem alterar o código da aplicação.

### Override Files por Ambiente

```yaml
# docker-compose.yml — base
services:
  api:
    build: .
    environment:
      - LOG_LEVEL=info

# docker-compose.override.yml — dev (carregado automaticamente)
services:
  api:
    build:
      target: development
    volumes:
      - .:/app
    environment:
      - LOG_LEVEL=debug
      - DEBUG=true
    ports:
      - "8000:8000"
      - "5678:5678"    # debugger port

# docker-compose.prod.yml — produção
services:
  api:
    build:
      target: production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
    restart: always
```

```bash
# Dev (usa override automático)
docker compose up

# Produção (ignora override)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Gerenciamento de Variáveis de Ambiente

```bash
# .env (carregado automaticamente)
COMPOSE_PROJECT_NAME=myapp
COMPOSE_FILE=docker-compose.yml:docker-compose.override.yml
POSTGRES_VERSION=16-alpine
API_IMAGE_TAG=latest

# .env.prod (carregado manualmente)
POSTGRES_VERSION=16
API_IMAGE_TAG=v1.2.3
```

```yaml
services:
  api:
    image: myapp/api:${API_IMAGE_TAG:-latest}
    env_file:
      - .env
      - .env.local        # override local não commitado
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASS}@db:5432/${DB_NAME}
```

```bash
# Carregar env específico
docker compose --env-file .env.prod up -d
```

---

## Gotchas

> [!warning] Armadilhas Comuns
> - **depends_on sem condition**: apenas garante que o container *iniciou*, não que está *saudável*. Sempre use `condition: service_healthy` para bancos de dados.
> - **Bind mounts em Windows/Mac**: performance significativamente pior que em Linux. Use `delegated` ou `cached` (legacy) ou prefira volumes nomeados.
> - **COMPOSE_PROJECT_NAME**: sem definir, Compose usa o nome do diretório. Isso causa colisões ao clonar o mesmo repo em paths diferentes.
> - **Secrets em environment**: variáveis de ambiente são visíveis via `docker inspect`. Para produção, use Docker Secrets ou vault externo.
> - **Redes e `network_mode: host`**: incompatível com port bindings e aliases. Evite em Compose multi-serviço.

> [!danger] Volumes e `docker compose down`
> `docker compose down` NÃO remove volumes nomeados por padrão. Use `down -v` para remover. Em CI, sempre limpe volumes entre runs para evitar estado remanescente.

---

## Snippets

### Stack Completa com PostgreSQL + Redis + API

```yaml
# docker-compose.yml
name: myapp

x-logging: &default-logging
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

services:
  postgres:
    image: postgres:16-alpine
    <<: *default-logging
    environment:
      POSTGRES_DB: ${DB_NAME:-appdb}
      POSTGRES_USER: ${DB_USER:-app}
      POSTGRES_PASSWORD: ${DB_PASS:?DB_PASS is required}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./sql/init:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-app}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks: [backend]

  redis:
    image: redis:7-alpine
    <<: *default-logging
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
    networks: [backend]

  api:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILD_DATE: ${BUILD_DATE:-unknown}
    <<: *default-logging
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file: [.env]
    networks: [frontend, backend]
    deploy:
      resources:
        limits:
          memory: 512M

volumes:
  pgdata:

networks:
  frontend:
  backend:
    internal: true
```

### Script de Health Check Customizado

```bash
#!/bin/sh
# healthcheck.sh — verifica API + DB connectivity
set -e
curl -sf http://localhost:8000/health | grep -q '"status":"ok"'
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null
```

---

## References

- [Compose Specification](https://compose-spec.io/)
- [Docker Compose File Reference v3](https://docs.docker.com/compose/compose-file/)
- [Profiles Documentation](https://docs.docker.com/compose/profiles/)
- [Health Check Best Practices](https://docs.docker.com/engine/reference/builder/#healthcheck)

## Related

- [[docker]] — runtime e Dockerfile patterns
- [[kubernetes-basics]] — orquestração em escala
- [[docker-snippets]] — comandos e one-liners úteis
- [[postgresql]] — configuração e tuning do banco
- [[redis]] — padrões de cache e filas
