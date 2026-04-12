---
tags: [skill, devops, secrets-management]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Secrets Management, Vault]
---

# Secrets Management

## Overview

Gerenciar segredos (senhas, API keys, certificados, tokens) e um dos problemas mais criticos em DevOps. Segredos em repositorios git, variaveisde ambiente inseguras, e credenciais estaticas que nunca rotacionam sao as causas mais comuns de incidentes de seguranca. A solucao envolve ferramentas como HashiCorp Vault para storage dinamico, SOPS para criptografia de arquivos em git, e External Secrets Operator para integrar clouds providers com Kubernetes.

> [!danger] Nunca Faca Isso
> `git add .env && git commit` — credenciais em repositorios vazam mesmo apos `git rm` porque permanecem no historico. Use `git secret` ou SOPS antes de qualquer commit com dados sensiveis.

---

## Core Concepts

### HashiCorp Vault — Arquitetura Completa

Vault e um sistema centralizado de gestao de segredos com audit log, politicas granulares, leases com TTL e rotacao automatica.

**Secrets Engines:**
```bash
# Habilitar diferentes engines
vault secrets enable -path=kv kv-v2          # Key-Value v2 (versionado)
vault secrets enable -path=database database  # Dynamic DB credentials
vault secrets enable -path=pki pki            # Certificate Authority
vault secrets enable -path=transit transit    # Encryption-as-a-Service
vault secrets enable -path=aws aws            # Dynamic AWS credentials

# KV-v2 — armazenar e versionar segredos
vault kv put kv/myapp/database \
  username="appuser" \
  password="$(openssl rand -base64 32)"

# Ler segredo com metadata de versao
vault kv get -format=json kv/myapp/database

# Ver versoes anteriores
vault kv metadata get kv/myapp/database

# Rollback para versao anterior
vault kv rollback -version=2 kv/myapp/database
```

**Dynamic Secrets — Database Engine:**
```bash
# Configurar conexao com PostgreSQL
vault write database/config/mypostgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly,readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@postgres:5432/mydb?sslmode=require" \
  username="vault_admin" \
  password="vault_admin_password"

# Criar role com credenciais temporarias
vault write database/roles/readonly \
  db_name=mypostgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN ENCRYPTED PASSWORD '{{password}}' \
    VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Gerar credenciais temporarias (nova senha a cada chamada)
vault read database/creds/readonly
# Key                Value
# lease_id           database/creds/readonly/abc123
# lease_duration     1h
# username           v-token-readonly-xyz789
# password           A1B2C3D4-generated-randomly
```

**Transit Engine — Encryption as a Service:**
```bash
# Criar chave de criptografia (nunca exportavel)
vault write -f transit/keys/myapp-key

# Criptografar dado sem expor a chave
vault write transit/encrypt/myapp-key \
  plaintext=$(echo "dados-sensiveis" | base64)
# ciphertext: vault:v1:ABC123xyz...

# Descriptografar
vault write transit/decrypt/myapp-key \
  ciphertext="vault:v1:ABC123xyz..."

# Rotacionar chave — dados antigos permanecem descriptografaveis
vault write -f transit/keys/myapp-key/rotate

# Rewrap — re-criptografar com nova versao da chave
vault write transit/rewrap/myapp-key \
  ciphertext="vault:v1:ABC123xyz..."  # Retorna vault:v2:...
```

**Auth Methods:**
```bash
# AppRole — para aplicacoes (CI/CD, servicos)
vault auth enable approle

vault write auth/approle/role/myapp \
  secret_id_ttl=10m \
  token_num_uses=10 \
  token_ttl=20m \
  token_max_ttl=30m \
  secret_id_num_uses=40 \
  policies="myapp-policy"

# Obter RoleID (publico, pode estar no codigo)
vault read auth/approle/role/myapp/role-id

# Gerar SecretID (secreto, injetado pelo CI/CD)
vault write -f auth/approle/role/myapp/secret-id

# Login com AppRole
vault write auth/approle/login \
  role_id="..." \
  secret_id="..."

# Kubernetes Auth — pods se autenticam via ServiceAccount JWT
vault auth enable kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=production \
  policies=myapp-policy \
  ttl=1h
```

**Policies — Controle Granular:**
```hcl
# myapp-policy.hcl
path "kv/data/myapp/*" {
  capabilities = ["read", "list"]
}

path "database/creds/readonly" {
  capabilities = ["read"]
}

path "transit/encrypt/myapp-key" {
  capabilities = ["update"]
}

path "transit/decrypt/myapp-key" {
  capabilities = ["update"]
}

# Deny explicito — sobrescreve qualquer allow
path "kv/data/production/master-keys" {
  capabilities = ["deny"]
}
```

### SOPS — Criptografia de Arquivos em Git

SOPS (Secrets OPerationS) criptografa valores em arquivos YAML/JSON/ENV mantendo as chaves em plaintext (legibilidade em diffs).

**Com age (moderno, preferido):**
```bash
# Gerar chave age
age-keygen -o ~/.config/sops/age/keys.txt
# chave publica: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p

# .sops.yaml — configuracao de criptografia por path
creation_rules:
  - path_regex: .*/production/.*\.yaml$
    age: >-
      age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p,
      age1another-team-member-key...
  - path_regex: .*/staging/.*\.yaml$
    age: age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p

# Criptografar arquivo
sops --encrypt secrets/production/database.yaml > secrets/production/database.enc.yaml

# Editar segredos (abre editor, decripta temporariamente)
sops secrets/production/database.enc.yaml

# Decriptar para uso
sops --decrypt secrets/production/database.enc.yaml | kubectl apply -f -
```

**Integracao com git e CI/CD:**
```yaml
# .github/workflows/deploy.yml
- name: Decrypt secrets
  env:
    SOPS_AGE_KEY: ${{ secrets.SOPS_AGE_PRIVATE_KEY }}
  run: |
    sops --decrypt --output-type=dotenv secrets/production/app.enc.yaml > .env
    # Ou exportar diretamente como env vars:
    eval $(sops --decrypt --output-type=dotenv secrets/production/app.enc.yaml)
```

**Com KMS (AWS/GCP/Azure):**
```bash
# Criptografar com AWS KMS (sem chave local — usa IAM role)
sops --kms arn:aws:kms:us-east-1:123456789:key/abc-123 \
  --encrypt secrets.yaml > secrets.enc.yaml

# CI/CD usa a IAM role do runner, sem chave privada nos secrets
```

### Doppler — Secrets como Servico

```bash
# Instalar e autenticar
doppler login

# Estrutura: Project -> Environment -> Secrets
doppler projects create myapp

# Injetar secrets em processo
doppler run -- node server.js

# Exportar como .env
doppler secrets download --no-file --format env > .env

# Sync para Kubernetes secret
doppler secrets download --format=kubernetes \
  --project myapp --config production | kubectl apply -f -

# CLI para CI/CD (service token, sem interatividade)
DOPPLER_TOKEN=${{ secrets.DOPPLER_TOKEN }} doppler run -- ./deploy.sh
```

### AWS Secrets Manager

```python
import boto3
import json
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region: str = "us-east-1") -> dict:
    client = boto3.client("secretsmanager", region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            raise ValueError(f"Secret {secret_name} not found")
        raise

    if "SecretString" in response:
        return json.loads(response["SecretString"])
    # Binary secret
    return response["SecretBinary"]

# Uso
db_config = get_secret("production/myapp/database")
connection = psycopg2.connect(
    host=db_config["host"],
    user=db_config["username"],
    password=db_config["password"],
    database=db_config["dbname"]
)
```

```bash
# Rotacao automatica via Lambda
aws secretsmanager rotate-secret \
  --secret-id production/myapp/database \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123:function:rotate-db-secret \
  --rotation-rules AutomaticallyAfterDays=30
```

### Kubernetes Secrets — Sealed Secrets e External Secrets

**Sealed Secrets (Bitnami) — criptografar para git:**
```bash
# Instalar controller
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system

# Criar secret encriptado (so o controller pode descriptografar)
kubectl create secret generic db-credentials \
  --from-literal=password=mysecretpassword \
  --dry-run=client -o yaml | \
  kubeseal --controller-namespace kube-system --format yaml > sealed-secret.yaml

# sealed-secret.yaml e seguro para commitar no git
git add sealed-secret.yaml && git commit -m "Add sealed database credentials"
```

**External Secrets Operator — sincronizar de fontes externas:**
```yaml
# ExternalSecret — puxa segredos do AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h  # Resincrona a cada hora
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials  # Nome do K8s Secret criado
    creationPolicy: Owner
  data:
    - secretKey: password      # Chave no K8s Secret
      remoteRef:
        key: production/myapp/database  # Path no Secrets Manager
        property: password             # Campo no JSON

---
# ClusterSecretStore — configuracao da fonte
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets
```

---

## Patterns

### 12-Factor App — Environment Variables

```bash
# Development — .env local (NUNCA commitar)
# .gitignore deve incluir .env, .env.local, .env.*.local

# Staging/Production — injetado pelo orchestrator
# Docker: --env-file ou -e VARIABLE=value
# Kubernetes: secretKeyRef em env
# Heroku/Railway: dashboard de config vars

# Hierarquia de precedencia (maior -> menor):
# 1. Process environment (shell export)
# 2. .env.local
# 3. .env.[NODE_ENV].local
# 4. .env.[NODE_ENV]
# 5. .env
```

### Rotation Pattern

```
1. Gerar nova credencial
2. Atualizar secret store (Vault/AWS SM)
3. Aplicar em novos pods/instancias (rolling update)
4. Verificar que aplicacao funciona com nova credencial
5. Revogar credencial antiga apos grace period (ex: 24h)
6. Audit log confirma que antiga nao e mais usada
```

### Audit Logging

```bash
# Vault — habilitar audit log para arquivo
vault audit enable file file_path=/var/log/vault/audit.log

# Log contém: timestamp, operation, path, response_code
# Nunca contém: valores de segredos (apenas SHA256 de tokens)

# Monitorar acessos suspeitos
grep "\"path\":\"kv/data/production" /var/log/vault/audit.log | \
  jq 'select(.response.auth.display_name != "ci-pipeline")'
```

---

## Gotchas

> [!danger] Vault Seal e Disaster Recovery
> Vault inicia "selado" (sealed) apos restart. Armazene unseal keys (Shamir shares) em locais fisicamente separados. Use Auto Unseal com KMS para ambientes de producao — elimina necessidade de intervencao manual.

> [!warning] K8s Secrets nao sao secretos
> Kubernetes Secrets sao apenas base64-encoded por padrao — qualquer pessoa com `kubectl get secret` ve os valores. Habilite Encryption at Rest no etcd e use RBAC rigoroso ou External Secrets Operator.

> [!bug] SOPS e Diffs em PRs
> Arquivos `.enc.yaml` tem diffs binarios/cifrados que nao sao legíveis em code review. Configure `.gitattributes` com diff driver SOPS para ver diffs decriptados (apenas localmente, com chave disponivel).

> [!tip] AppRole vs Token Direto
> Nunca use Vault tokens de longa duracao em CI/CD. Use AppRole com `secret_id_num_uses=1` e `token_ttl=10m` — cada pipeline run usa um SecretID diferente que expira apos uso.

---

## Snippets

```bash
# Verificar se segredo esta prestes a expirar (Vault lease)
vault list sys/leases/lookup/database/creds/readonly | \
  xargs -I{} vault read sys/leases/lookup/database/creds/readonly/{}

# Renovar lease antes de expirar
vault lease renew database/creds/readonly/abc123

# Revogar credencial comprometida imediatamente
vault lease revoke database/creds/readonly/abc123
# Ou revogar TODOS os leases de uma role
vault lease revoke -prefix database/creds/readonly
```

```bash
# Script de bootstrap para novo servico
#!/bin/bash
# Uso: ./bootstrap-secrets.sh <service_name> <environment>
SERVICE=$1
ENV=$2

# Criar AppRole
vault write auth/approle/role/${SERVICE}-${ENV} \
  policies="${SERVICE}-${ENV}-policy" \
  token_ttl=1h \
  secret_id_ttl=24h

# Obter RoleID para embutir no deploy
ROLE_ID=$(vault read -field=role_id auth/approle/role/${SERVICE}-${ENV}/role-id)
echo "VAULT_ROLE_ID=${ROLE_ID}" >> .env.${ENV}

echo "SecretID sera gerado pelo CI/CD a cada deploy"
```

---

## References

- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
- [SOPS — Mozilla](https://github.com/mozilla/sops)
- [External Secrets Operator](https://external-secrets.io/)
- [Sealed Secrets — Bitnami](https://sealed-secrets.netlify.app/)

---

## Related

- [[github-actions]] — Injetar secrets do Vault/Doppler em workflows
- [[gitlab-ci]] — GitLab CI/CD variables e integracao com Vault
- [[kubernetes-basics]] — Sealed Secrets, External Secrets Operator
- [[terraform]] — Vault provider, gerenciar secrets de infra como codigo
- [[docker]] — Secrets em Docker Swarm, env vars em containers
- [[vpn-setup]] — Chaves WireGuard gerenciadas pelo Vault
