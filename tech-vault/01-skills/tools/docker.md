---
tags: [skill, tools, docker]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Docker]
---

# Docker

## Overview

Docker no nível avançado significa imagens **menores**, **mais seguras** e **reproduzíveis**. O foco está em técnicas de build otimizadas com BuildKit, estratégias de segurança com imagens mínimas, e operação correta de containers em produção — incluindo signal handling e healthchecks. Esses padrões são a base para pipelines sólidas com [[github-actions]] e orquestração com [[kubernetes-basics]].

Veja padrões de composição em [[docker-compose-patterns]], snippets reutilizáveis em [[docker-snippets]], e estratégias de rollout em [[deployment-strategies]].

---

## Core Concepts

### Multi-Stage Builds — Builder Pattern

Multi-stage builds separam o ambiente de compilação do artefato final, eliminando ferramentas de build da imagem de produção.

```dockerfile
# syntax=docker/dockerfile:1.6

# ── Stage 1: dependencies ──────────────────────────────────────
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# ── Stage 2: builder ──────────────────────────────────────────
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ── Stage 3: production ───────────────────────────────────────
FROM node:22-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps    /app/node_modules ./node_modules
COPY --from=builder /app/dist         ./dist
COPY --from=builder /app/package.json ./

# Sinal correto para Node.js com tini
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/server.js"]
```

### Layer Caching Optimization

A ordem das instruções determina a efetividade do cache. Instruções que mudam com frequência devem vir **por último**.

```dockerfile
# RUIM — invalida cache do npm install a cada mudança de código
COPY . .
RUN npm ci

# BOM — npm install usa cache enquanto package.json não mudar
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

> [!tip] Cache miss diagnosis
> Use `docker build --progress=plain` para ver quais layers estão sendo reconstruídas e por quê.

### BuildKit — Mount Caches, SSH e Secrets

BuildKit é o backend de build moderno do Docker. Habilitar: `DOCKER_BUILDKIT=1` ou via `buildx`.

```dockerfile
# Cache persistente para package managers (não vaza no layer final)
RUN --mount=type=cache,target=/root/.npm \
    npm ci --cache /root/.npm

# Cache para pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# SSH forwarding para dependências privadas (sem expor chave na imagem)
RUN --mount=type=ssh \
    git clone git@github.com:org/private-lib.git

# Secrets sem vazar no layer (ex: tokens de registro privado)
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm ci
```

```bash
# Build com SSH agent forwarded
docker buildx build --ssh default=$SSH_AUTH_SOCK .

# Build com secret
docker buildx build --secret id=npm_token,src=.npmtoken .
```

---

## Patterns

### Distroless e Scratch Images

Imagens mínimas reduzem surface de ataque e tamanho drasticamente.

```dockerfile
# Scratch — só o binário (Go, Rust)
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o server ./cmd/server

FROM scratch
COPY --from=builder /app/server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
EXPOSE 8080
ENTRYPOINT ["/server"]

# Distroless para Java
FROM gcr.io/distroless/java21-debian12:nonroot
COPY --from=builder /app/target/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

| Image Type    | Size      | Shell | Package Mgr | CVEs Surface |
|---------------|-----------|-------|-------------|--------------|
| `ubuntu:24`   | ~78MB     | Yes   | Yes         | High         |
| `alpine:3.19` | ~7MB      | Yes   | Yes         | Medium       |
| `distroless`  | ~20-50MB  | No    | No          | Low          |
| `scratch`     | 0B base   | No    | No          | Minimal      |

### Rootless Mode

Rodar como root dentro de container ainda expõe riscos caso haja escape. Use `USER` não-root.

```dockerfile
FROM node:22-alpine

# Criar usuário dedicado com UID explícito
RUN addgroup -S appgroup && adduser -S appuser -G appgroup -u 1001

WORKDIR /app
COPY --chown=appuser:appgroup . .
RUN npm ci --omit=dev

USER appuser
EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
# Verificar usuário em runtime
docker run --rm myapp whoami
# appuser

# Forçar usuário no run (override do Dockerfile)
docker run --user 1001:1001 myapp
```

### Healthchecks

Healthchecks permitem que o Docker (e o [[kubernetes-basics]]) detectem containers não-saudáveis e os reiniciem.

```dockerfile
# HTTP healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

# TCP healthcheck
HEALTHCHECK --interval=15s --timeout=5s \
  CMD nc -z localhost 5432 || exit 1

# Script customizado
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD ["/usr/local/bin/healthcheck.sh"]
```

```bash
# Ver status do healthcheck
docker inspect --format='{{json .State.Health}}' container_name | jq
```

### Signal Handling — STOPSIGNAL e Tini

Containers que ignoram `SIGTERM` causam shutdown lento ou forcado (`SIGKILL` após timeout).

```dockerfile
# Node.js precisa de init process para repassar sinais corretamente
# Opção 1: tini (leve, recomendado)
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]

# Opção 2: --init flag no docker run (usa tini embutido no daemon)
# docker run --init myapp

# Customizar sinal de parada
STOPSIGNAL SIGUSR1
```

```javascript
// Node.js: graceful shutdown handler
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully...');
  await server.close();
  await db.disconnect();
  process.exit(0);
});
```

### .dockerignore

Um `.dockerignore` bem configurado evita enviar arquivos desnecessários ao build context, acelerando builds e evitando vazar dados.

```text
# Dependencies (rebuilt inside container)
node_modules
vendor
.venv
__pycache__

# Build artifacts
dist
build
*.egg-info

# VCS
.git
.gitignore

# Secrets e configs locais
.env
.env.*
*.pem
*.key
secrets/

# Docs e testes (opcional em prod image)
docs
*.md
tests
coverage

# IDE
.vscode
.idea
*.swp
```

> [!warning] .dockerignore não é .gitignore
> O `.dockerignore` usa sintaxe similar mas diferente: não suporta negação de padrões da mesma forma. Teste com `docker build --progress=plain` e verifique o context size no log.

### BuildX — Multi-Platform Builds

```bash
# Criar builder com suporte multi-arch
docker buildx create --name multiarch --driver docker-container --use
docker buildx inspect --bootstrap

# Build para múltiplas plataformas e push
docker buildx build \
  --platform linux/amd64,linux/arm64,linux/arm/v7 \
  --tag registry.io/org/app:latest \
  --push \
  .

# Inspecionar manifesto multi-arch
docker buildx imagetools inspect registry.io/org/app:latest
```

### Security Scanning

```bash
# Trivy — scan de vulnerabilidades em imagem local
trivy image --severity HIGH,CRITICAL myapp:latest

# Trivy no Dockerfile antes do build
trivy config --exit-code 1 Dockerfile

# Docker Scout (integrado ao CLI)
docker scout cves myapp:latest
docker scout recommendations myapp:latest
docker scout compare myapp:latest --to myapp:previous
```

> [!danger] Não ignore CVEs HIGH/CRITICAL em produção
> Configure gates no pipeline do [[github-actions]] para bloquear push quando `trivy` retornar exit code 1. Exemplo:
> ```yaml
> - name: Security scan
>   run: trivy image --exit-code 1 --severity HIGH,CRITICAL $IMAGE
> ```

### Docker Init

`docker init` gera Dockerfile, `.dockerignore` e `compose.yaml` otimizados detectando automaticamente a linguagem do projeto.

```bash
# Inicializar em projeto existente
docker init

# Saída interativa pergunta:
# - Language/platform (Node, Python, Go, Java, Rust...)
# - Version
# - Entrypoint
# Gera arquivos com melhores práticas já aplicadas
```

---

## Gotchas

> [!warning] ADD vs COPY
> Use `COPY` por padrão. `ADD` tem comportamento implícito: descompacta `.tar.gz` automaticamente e aceita URLs remotas — o que torna o build menos previsível e seguro.

> [!warning] Cache de RUN com apt/apk
> Nunca separe `apt-get update` e `apt-get install` em layers diferentes. Se o cache de `update` for reaproveitado com um `install` diferente, pode instalar versões desatualizadas.
> ```dockerfile
> # ERRADO
> RUN apt-get update
> RUN apt-get install -y curl
>
> # CORRETO
> RUN apt-get update && apt-get install -y --no-install-recommends curl \
>     && rm -rf /var/lib/apt/lists/*
> ```

> [!danger] Secrets em variáveis de ambiente
> `ENV TOKEN=abc123` grava o segredo **permanentemente em todos os layers** e é visível via `docker inspect`. Use `--mount=type=secret` do BuildKit ou passe segredos em runtime via orquestrador.

---

## Snippets

```bash
# Tamanho real de cada layer da imagem
docker history --human --format "{{.Size}}\t{{.CreatedBy}}" myapp:latest

# Entrar num container distroless (sem shell) com debug container
docker run -it --pid=container:app --network=container:app \
  busybox sh

# Limpar tudo que não está em uso
docker system prune --volumes --force

# Exportar imagem como tarball
docker save myapp:latest | gzip > myapp.tar.gz
docker load < myapp.tar.gz

# Copiar arquivo de container parado
docker cp container_name:/app/logs/error.log ./error.log
```

---

## References

- [Docker BuildKit documentation](https://docs.docker.com/build/buildkit/)
- [Distroless images — GoogleContainerTools](https://github.com/GoogleContainerTools/distroless)
- [Trivy — Aqua Security](https://github.com/aquasecurity/trivy)
- [Docker Scout](https://docs.docker.com/scout/)
- [tini — tiny init for containers](https://github.com/krallin/tini)

---

## Related

- [[docker-compose-patterns]]
- [[kubernetes-basics]]
- [[github-actions]]
- [[deployment-strategies]]
- [[docker-snippets]]
