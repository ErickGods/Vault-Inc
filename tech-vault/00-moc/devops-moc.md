---
tags: [moc, devops]
status: active
level: advanced
updated: 2026-04-05
aliases: [DevOps MOC]
created: 2026-04-05
---

# ⚙️ DevOps MOC

## Visão Geral

Este MOC cobre o domínio de DevOps: automação de CI/CD, orquestração de containers, monitoramento, infraestrutura como código e segurança operacional. O objetivo é documentar os padrões e ferramentas que garantem deploys confiáveis, observabilidade e resiliência dos sistemas em produção.

DevOps moderno não é apenas automatizar deploys — é criar loops de feedback rápidos, detectar problemas antes que afetem usuários e manter infraestrutura que se auto-documenta através de código.

> [!info] Cobertura
> Esta seção (`02-devops/`) contém 13 arquivos organizados em CI/CD, containers, monitoramento, IaC, networking e segurança.

---

## 📊 Dashboard

```dataview
TABLE status, level, updated
FROM "tech-vault/02-devops"
SORT updated DESC
```

---

## 🗺️ Skills Map

### CI/CD — Continuous Integration & Delivery

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[github-actions]] | GitHub Actions — pipelines declarativos | ✅ active |
| [[gitlab-ci]] | GitLab CI/CD — pipelines self-hosted | ✅ active |
| [[argocd]] | ArgoCD — GitOps para Kubernetes | ✅ active |
| [[deployment-strategies]] | Blue/Green, Canary, Rolling | ✅ active |
| [[feature-flags]] | Feature flags com LaunchDarkly/Unleash | 🚧 draft |

### Containers & Orchestration

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[docker-compose-patterns]] | Docker Compose para dev e staging | ✅ active |
| [[kubernetes-basics]] | Kubernetes — orquestração de containers | ✅ active |

### Monitoring & Observability

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[observability]] | Logs, métricas e traces (LGTM stack) | ✅ active |

### Infrastructure as Code

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[terraform]] | Terraform — IaC multi-cloud | ✅ active |
| [[pulumi]] | Pulumi — IaC com linguagens de programação | 🚧 draft |

### Networking

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[vpn-setup]] | WireGuard e OpenVPN | ✅ active |
| [[reverse-proxy]] | Nginx, Caddy e Traefik | ✅ active |
| [[dns-and-cdn]] | DNS, CDN e edge caching | ✅ active |

### Security

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[secrets-management]] | Vault, AWS Secrets Manager, SOPS | ✅ active |

---

## ⚡ Quick Access

- [[github-actions]] — Pipeline padrão para projetos no GitHub
- [[deployment-strategies]] — Escolha a estratégia certa para cada contexto
- [[kubernetes-basics]] — Orquestração de containers em produção
- [[terraform]] — Provisionar infraestrutura cloud com código
- [[observability]] — Configurar logging, métricas e traces
- [[secrets-management]] — Nunca hardcodar segredos

---

## 🔄 CI/CD Pipeline Padrão

> [!tip] Pipeline Recomendado para Projetos Python/Node
> Um pipeline completo deve ter pelo menos: lint → test → build → security scan → deploy → smoke test. Veja [[github-actions]] para templates prontos.

```yaml
# Estrutura típica de pipeline — detalhes em [[github-actions]]
stages:
  - lint-and-format     # ruff, eslint, prettier
  - unit-tests          # pytest, vitest
  - integration-tests   # testes com banco real
  - security-scan       # trivy, snyk
  - build-image         # docker build + push
  - deploy-staging      # deploy automático
  - smoke-tests         # validação pós-deploy
  - deploy-production   # manual ou automático
```

---

## 🚀 Deployment Strategies

> [!info] Escolhendo a Estratégia
> - **Rolling Update** → zero-downtime simples, sem custo extra de infra
> - **Blue/Green** → rollback instantâneo, mas custo dobrado temporariamente
> - **Canary** → validação com % do tráfego real, ideal para features críticas
> - **Feature Flags** → deploy desacoplado do release, máxima flexibilidade

Para detalhes de implementação, veja [[deployment-strategies]] e [[feature-flags]].

---

## 📡 Observability Stack

### LGTM Stack (recomendado)
- **Loki** — aggregação de logs
- **Grafana** — dashboards e alertas
- **Tempo** — distributed tracing
- **Mimir/Prometheus** — métricas

```bash
# Iniciar stack de observabilidade local — ver [[docker-compose-patterns]]
docker compose -f observability/docker-compose.yml up -d
```

Ver [[observability]] para configuração detalhada e instrumentação de aplicações.

---

## 🔒 Security Posture

> [!warning] Regras de Ouro de Segurança
> 1. Nunca commitar segredos — use [[secrets-management]]
> 2. Scan de imagens Docker em todo pipeline — trivy ou snyk
> 3. Least privilege em IAM roles — nunca `*` em produção
> 4. Network policies no Kubernetes — isolar namespaces
> 5. Rotate secrets automaticamente — integrar com Vault

---

## 🌐 Networking Patterns

```
Internet → CDN (Cloudflare) → Load Balancer → Reverse Proxy → App
                                                    ↓
                                              [[reverse-proxy]]
                                         (Nginx/Caddy/Traefik)
```

- [[dns-and-cdn]] — configuração de DNS, registros, CDN edge caching
- [[reverse-proxy]] — roteamento, TLS termination, rate limiting
- [[vpn-setup]] — acesso seguro a recursos internos

---

## 🔗 Integrações com Outros Domínios

- **Engineering** → [[engineering-moc]] — como os apps são construídos antes de deployar
- **Infrastructure** → [[infrastructure-moc]] — cloud resources e redes subjacentes
- **Architecture** → [[architecture-moc]] — padrões como [[microservices]] que definem a topologia de deploy

---

## 📋 Checklist de Produção

> [!example] Antes de ir para Produção
> - [ ] Pipeline CI/CD configurado com testes automatizados
> - [ ] Imagens Docker com scan de vulnerabilidades
> - [ ] Secrets fora do código (usar [[secrets-management]])
> - [ ] Health checks configurados nos containers
> - [ ] Alertas de métricas configurados (ver [[observability]])
> - [ ] Estratégia de rollback documentada (ver [[deployment-strategies]])
> - [ ] Backups testados e automatizados
> - [ ] Runbook de incidentes atualizado
