---
tags: [snippet, docker]
status: active
level: advanced
updated: 2026-04-05
aliases: [Docker Snippets]
created: 2026-04-05
---

# Docker Snippets

Dockerfiles e configurações de compose prontos para produção. Cobre Python, Node, Rust e padrões de orquestração com referências a [[docker]], [[docker-compose-patterns]], [[bash-snippets]], [[kubernetes-basics]] e [[python-snippets]].

---

## Dockerfile: Python Multi-Stage

```dockerfile
# syntax=docker/dockerfile:1.6
# Stage 1: Builder — instala dependências e compila
FROM python:3.12-slim AS builder

WORKDIR /build

# Cache de dependências separado do código
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime — imagem mínima
FROM python:3.12-slim AS runtime

# Usuário não-root por segurança
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app

# Copiar apenas o necessário do builder
COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup . .

# Metadata e configuração
LABEL org.opencontainers.image.source="https://github.com/org/repo"
LABEL org.opencontainers.image.version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

USER appuser
EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## Dockerfile: Node.js Multi-Stage

```dockerfile
# syntax=docker/dockerfile:1.6
FROM node:20-alpine AS deps

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Stage de build para TypeScript/Next.js
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage final mínimo
FROM node:20-alpine AS runtime
RUN addgroup -S nodejs && adduser -S nextjs -G nodejs
WORKDIR /app

COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --chown=nextjs:nodejs package.json .

USER nextjs
EXPOSE 3000
ENV NODE_ENV=production PORT=3000

HEALTHCHECK --interval=30s --timeout=10s \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

---

## Dockerfile: Rust Multi-Stage

```dockerfile
# syntax=docker/dockerfile:1.6
# Cache de dependências via chef pattern
FROM lukemathwalker/cargo-chef:latest-rust-1.78 AS chef
WORKDIR /app

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
# Cache de build de dependências
RUN cargo chef cook --release --recipe-path recipe.json
COPY . .
RUN cargo build --release

# Imagem mínima: apenas o binário
FROM debian:bookworm-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libssl3 && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY --from=builder /app/target/release/myapp /usr/local/bin/myapp
USER appuser
EXPOSE 8080
CMD ["/usr/local/bin/myapp"]
```

---

## Docker Compose: Web + DB + Cache

```yaml
# docker-compose.yml — Stack completa para desenvolvimento
name: myapp

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://cache:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    networks:
      - internal
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./migrations/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal
    restart: unless-stopped

  cache:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - internal
    restart: unless-stopped

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    networks:
      - internal
      - external
    restart: unless-stopped

volumes:
  pg_data:
    driver: local
  redis_data:
    driver: local

networks:
  internal:
    driver: bridge
    internal: true
  external:
    driver: bridge
```

---

## Health Checks Avançados

```dockerfile
# Health check HTTP com curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Health check com script customizado
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh
HEALTHCHECK --interval=20s --timeout=5s \
  CMD ["/usr/local/bin/healthcheck.sh"]
```

```bash
#!/bin/bash
# healthcheck.sh — verificação composta
set -e
# Verificar API
curl -f http://localhost:8000/health > /dev/null 2>&1 || exit 1
# Verificar conexão com DB
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null || exit 1
echo "healthy"
```

---

## Volume Mounts & Network Configs

```yaml
# Volumes com opções avançadas
volumes:
  app_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /host/data

  nfs_share:
    driver: local
    driver_opts:
      type: nfs
      o: "addr=192.168.1.100,rw"
      device: ":/exports/shared"

# Network com configuração personalizada
networks:
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
    driver_opts:
      com.docker.network.bridge.name: br-backend
```

---

## Cleanup Commands

```bash
# Remover tudo que não está em uso
docker system prune -af --volumes

# Remover imagens dangling
docker image prune -f

# Remover containers parados
docker container prune -f

# Remover volumes não usados
docker volume prune -f

# Remover redes não usadas
docker network prune -f

# Ver uso de disco
docker system df -v

# Limpar imagens de build antigos (manter últimas 3)
docker images --format "{{.Repository}}:{{.Tag}}" | grep "myapp" | \
  tail -n +4 | xargs -r docker rmi

# Remover containers por label
docker ps -a --filter "label=env=staging" -q | xargs -r docker rm -f
```

---

## Debugging Containers

```bash
# Entrar em container em execução
docker exec -it container_name bash

# Entrar como root em container com usuário não-root
docker exec -u root -it container_name bash

# Inspecionar logs com filtro de tempo
docker logs --since="2024-01-01T00:00:00" --until="2024-01-02T00:00:00" container_name

# Seguir logs de múltiplos containers com docker compose
docker compose logs -f --tail=50 api db

# Copiar arquivo de/para container
docker cp container_name:/app/logs/error.log ./error.log
docker cp ./config.json container_name:/app/config.json

# Inspecionar configuração completa
docker inspect container_name | jq '.[0].HostConfig'

# Monitorar stats em tempo real
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Depurar container que para imediatamente (override entrypoint)
docker run -it --entrypoint /bin/bash myimage:latest

# Verificar camadas da imagem
docker history myimage:latest --no-trunc

# Analisar tamanho de cada camada
docker image inspect myimage:latest | jq '.[0].RootFS.Layers | length'

# Exportar e importar imagem sem registry
docker save myimage:latest | gzip > myimage.tar.gz
docker load < myimage.tar.gz
```

---

> [!tip] Multi-Stage é Obrigatório
> Sempre use multi-stage builds em produção. A imagem final de Python (slim) fica ~150MB contra ~1GB de uma imagem com build tools. Para Rust, o binário estático vai para ~30MB. Veja mais em [[docker]].

> [!warning] Segurança em Produção
> Nunca rode containers como root. Use `USER` no Dockerfile e evite `--privileged`. Para orquestração em escala, veja [[kubernetes-basics]].

> [!info] Automatização
> Combine com [[bash-snippets]] para scripts de build e deploy automatizados em pipelines CI/CD. Para aplicações Python, veja [[python-snippets]] e os padrões de [[docker-compose-patterns]].
