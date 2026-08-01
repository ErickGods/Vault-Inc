---
tags: [moc, infrastructure]
status: active
level: advanced
updated: 2026-04-05
aliases: [Infrastructure MOC]
created: 2026-04-05
---

# 🌐 Infrastructure MOC

## Visão Geral

Este MOC é transversal — cobre networking, segurança, cloud e infraestrutura como código, reunindo conteúdos de `02-devops/` e `04-architecture/` que têm caráter de plataforma. Enquanto [[devops-moc]] foca em CI/CD e automação de deploy, e [[architecture-moc]] foca em padrões de design, este MOC foca na camada de plataforma que suporta tudo isso.

Infraestrutura moderna é definida como código, versionada, testável e observável. O objetivo é que nenhum recurso de infraestrutura exista sem ser representado em código e documentado neste vault.

> [!info] Natureza Cross-Cutting
> Este MOC agrega links de múltiplas seções do vault. Os arquivos referenciados vivem em `02-devops/` e `04-architecture/`, mas são reunidos aqui para uma visão holística da camada de infraestrutura.

---

## 📊 Dashboard

```dataview
TABLE status, level, updated
FROM "tech-vault/02-devops/networking" OR "tech-vault/02-devops/security" OR "tech-vault/04-architecture/cloud-services" OR "tech-vault/02-devops/iac"
SORT updated DESC
```

---

## 🗺️ Skills Map

### Networking

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[vpn-setup]] | WireGuard, OpenVPN, túneis seguros | ✅ active |
| [[reverse-proxy]] | Nginx, Caddy, Traefik — TLS e roteamento | ✅ active |
| [[dns-and-cdn]] | DNS records, CDN edge, caching | ✅ active |

### Security

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[secrets-management]] | Vault, AWS Secrets Manager, SOPS | ✅ active |

### Cloud Services

| Arquivo | Serviço | Status |
|---------|---------|--------|
| [[cloudinary]] | CDN e transformações de mídia | ✅ active |
| [[s3-storage-patterns]] | AWS S3 — storage de objetos | ✅ active |
| [[media-pipeline]] | Pipeline de processamento de mídia | 🚧 draft |

### Infrastructure as Code

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[terraform]] | Terraform — IaC multi-cloud declarativo | ✅ active |
| [[pulumi]] | Pulumi — IaC com linguagens de programação | 🚧 draft |

### Container Orchestration

| Arquivo | Ferramenta | Status |
|---------|-----------|--------|
| [[kubernetes-basics]] | Kubernetes — workloads e networking | ✅ active |
| [[docker]] | Docker — imagens e runtime | ✅ active |

---

## ⚡ Quick Access

- [[terraform]] — Provisionar qualquer recurso cloud com código
- [[secrets-management]] — Gerenciar segredos com segurança
- [[reverse-proxy]] — Configurar roteamento e TLS
- [[kubernetes-basics]] — Orquestrar containers em produção
- [[s3-storage-patterns]] — Armazenamento de objetos escalável
- [[dns-and-cdn]] — Configurar domínios e cache global

---

## 🏗️ Diagrama de Infraestrutura Típica

```
Internet
    ↓
Cloudflare (DNS + CDN + DDoS)   ← [[dns-and-cdn]]
    ↓
Load Balancer (AWS ALB / GCP LB)
    ↓
Reverse Proxy (Nginx/Traefik)   ← [[reverse-proxy]]
    ↓
Kubernetes Cluster              ← [[kubernetes-basics]]
├── App Pods
├── Worker Pods
└── Ingress Controller
    ↓
Cloud Services
├── S3 / R2 (objetos)           ← [[s3-storage-patterns]]
├── RDS / Aurora (banco)
├── ElastiCache / Upstash (cache)
└── Secrets Manager             ← [[secrets-management]]
    ↓
VPN (acesso interno)            ← [[vpn-setup]]
```

---

## 🔧 Infrastructure as Code

### Terraform — Fluxo de Trabalho

```bash
# Fluxo básico — detalhes completos em [[terraform]]
terraform init          # inicializar providers
terraform plan          # preview das mudanças
terraform apply         # aplicar mudanças
terraform state list    # listar recursos gerenciados
```

> [!tip] Terraform Best Practices
> - Usar **remote state** (S3 + DynamoDB lock) em produção
> - Separar state por ambiente (`dev/`, `staging/`, `prod/`)
> - **Módulos** para recursos reutilizáveis (VPC, ECS service, etc.)
> - Nunca editar estado manualmente — use `terraform import` se necessário
> - Usar `terraform-docs` para gerar documentação dos módulos

### Pulumi — Diferencial vs Terraform

```typescript
// Pulumi — infraestrutura como TypeScript — ver [[pulumi]]
import * as aws from "@pulumi/aws";

const bucket = new aws.s3.Bucket("app-assets", {
  versioning: { enabled: true },
  serverSideEncryptionConfiguration: {
    rule: {
      applyServerSideEncryptionByDefault: {
        sseAlgorithm: "AES256",
      },
    },
  },
});
```

> [!info] Quando Usar Pulumi vs Terraform
> Use **Pulumi** quando a lógica de infraestrutura é complexa (loops, condicionais, abstração OOP) ou quando o time prefere linguagens tipadas. Use **Terraform** quando a equipe já conhece HCL ou há módulos prontos no registry.

---

## 🔒 Security Layers

### Defense in Depth

```
Camada 1: Rede       → VPC, Security Groups, NACLs
Camada 2: Perímetro  → WAF, DDoS protection (Cloudflare)
Camada 3: Aplicação  → Auth, Rate limiting, Input validation
Camada 4: Dados      → Encryption at rest/transit, [[secrets-management]]
Camada 5: Auditoria  → CloudTrail, audit logs, alertas
```

### Secrets Management Hierarchy

```
Desenvolvimento:  .env local (nunca commitar)
Staging:          SOPS + Git (criptografado)
Produção:         AWS Secrets Manager / HashiCorp Vault
CI/CD:            GitHub Secrets / GitLab Variables
```

Ver [[secrets-management]] para configuração detalhada de cada camada.

---

## ☁️ Cloud Networking

### DNS + CDN Pattern

```
Registro de domínio → Cloudflare DNS (autoritativo)
    ↓
CDN Edge (Cloudflare) → cache de assets estáticos
    ↓
Origin (Load Balancer) → apenas tráfego não-cacheado
```

> [!tip] Configurações Essenciais de DNS
> - **A record** → IP do load balancer
> - **CNAME** → subdomínios (api., app., cdn.)
> - **MX** → configuração de email
> - **TXT** → SPF, DKIM, verificação de domínio
> - **TTL** → baixo durante mudanças, alto em produção estável

Ver [[dns-and-cdn]] para exemplos de configuração Cloudflare e Route53.

---

## 🐳 Kubernetes Architecture

```
Control Plane:
├── kube-apiserver    ← ponto central de controle
├── etcd              ← estado do cluster
├── kube-scheduler    ← alocação de pods
└── kube-controller   ← loops de reconciliação

Worker Nodes:
├── kubelet           ← agente no node
├── kube-proxy        ← networking
└── Container Runtime ← containerd / CRI-O
```

> [!info] Recursos Kubernetes Essenciais
> - **Deployment** → stateless apps com rolling updates
> - **StatefulSet** → apps stateful (bancos, caches)
> - **Service** → DNS e load balancing interno
> - **Ingress** → roteamento HTTP externo
> - **ConfigMap/Secret** → configuração e segredos

Ver [[kubernetes-basics]] para manifests YAML completos e padrões de produção.

---

## 🔗 Integrações com Outros Domínios

- **DevOps** → [[devops-moc]] — CI/CD que deploya para esta infraestrutura
- **Architecture** → [[architecture-moc]] — padrões cloud e storage de objetos
- **Engineering** → [[engineering-moc]] — [[docker]] é a base para containers Kubernetes
- **Data** → [[data-engineering-moc]] — data lake usa [[s3-storage-patterns]] como storage layer

---

## 📋 Checklist de Infraestrutura Segura

> [!example] Auditoria de Segurança
> - [ ] Todos os segredos em [[secrets-management]] (não em variáveis de ambiente hardcoded)
> - [ ] Buckets S3 sem acesso público direto (ver [[s3-storage-patterns]])
> - [ ] TLS habilitado em todos os endpoints (ver [[reverse-proxy]])
> - [ ] IaC versionado em Git com review obrigatório (ver [[terraform]])
> - [ ] VPN para acesso a recursos internos (ver [[vpn-setup]])
> - [ ] Kubernetes RBAC configurado com least privilege
> - [ ] Network policies separando namespaces críticos
