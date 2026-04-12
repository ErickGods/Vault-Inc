---
tags: [skill, devops, github-actions]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [GitHub Actions, GHA]
---

# GitHub Actions

## Overview

GitHub Actions é a plataforma de CI/CD nativa do GitHub — baseada em YAML declarativo, executada em runners efêmeros, e profundamente integrada ao ecossistema GitHub. Vai muito além de "rodar testes": suporta workflows complexos com matrix builds, reusable workflows via `workflow_call`, composite actions empacotando lógica reutilizável, self-hosted runners para workloads específicos, e OIDC para autenticação sem segredos de longa duração em clouds.

A unidade de execução é o **job**, que roda em um runner. Jobs dentro de um workflow são paralelos por padrão; dependências são declaradas com `needs`. Steps dentro de um job são sequenciais.

Ver também: [[docker]], [[deployment-strategies]], [[git-advanced]], [[argocd]], [[secrets-management]]

---

## Core Concepts

### Workflow Syntax Deep Dive

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, "release/**"]
    paths-ignore: ["docs/**", "*.md"]
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        type: choice
        options: [staging, production]
      debug:
        description: "Enable debug logging"
        type: boolean
        default: false

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true   # cancela runs antigas do mesmo branch

env:
  NODE_VERSION: "20"
  REGISTRY: ghcr.io

jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"          # cache integrado do setup-node
      - run: npm ci
      - run: npm run lint

  test:
    needs: lint
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"
      - run: npm ci
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/
          retention-days: 7
```

### Matrix Builds

Matrix strategy permite executar o mesmo job com variações de parâmetros sem duplicar YAML.

```yaml
jobs:
  test-matrix:
    strategy:
      fail-fast: false          # não cancela outras combinações se uma falhar
      matrix:
        os: [ubuntu-24.04, windows-2022, macos-14]
        node: ["18", "20", "22"]
        exclude:
          - os: windows-2022
            node: "18"
        include:
          - os: ubuntu-24.04
            node: "20"
            experimental: false
    runs-on: ${{ matrix.os }}
    continue-on-error: ${{ matrix.experimental || false }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm test
```

---

## Patterns

### Reusable Workflows (workflow_call)

Reusable workflows são a forma de DRY em workflows complexos. O caller passa inputs/secrets; o callee é um workflow independente.

```yaml
# .github/workflows/_deploy.yml  (reusable — prefixo _ por convenção)
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image-tag:
        required: true
        type: string
    secrets:
      DEPLOY_TOKEN:
        required: true
    outputs:
      deployment-url:
        description: "URL do deployment criado"
        value: ${{ jobs.deploy.outputs.url }}

jobs:
  deploy:
    runs-on: ubuntu-24.04
    environment: ${{ inputs.environment }}
    outputs:
      url: ${{ steps.deploy.outputs.url }}
    steps:
      - name: Deploy
        id: deploy
        run: |
          echo "Deploying ${{ inputs.image-tag }} to ${{ inputs.environment }}"
          echo "url=https://${{ inputs.environment }}.example.com" >> $GITHUB_OUTPUT
```

```yaml
# .github/workflows/cd.yml  (caller)
jobs:
  build:
    outputs:
      image-tag: ${{ steps.tag.outputs.tag }}
    steps:
      - id: tag
        run: echo "tag=${{ github.sha }}" >> $GITHUB_OUTPUT

  deploy-staging:
    needs: build
    uses: ./.github/workflows/_deploy.yml
    with:
      environment: staging
      image-tag: ${{ needs.build.outputs.image-tag }}
    secrets:
      DEPLOY_TOKEN: ${{ secrets.STAGING_DEPLOY_TOKEN }}

  deploy-prod:
    needs: [build, deploy-staging]
    uses: ./.github/workflows/_deploy.yml
    with:
      environment: production
      image-tag: ${{ needs.build.outputs.image-tag }}
    secrets:
      DEPLOY_TOKEN: ${{ secrets.PROD_DEPLOY_TOKEN }}
```

### Composite Actions

Composite actions empacotam steps reutilizáveis em uma action local ou pública.

```yaml
# .github/actions/setup-project/action.yml
name: "Setup Project"
description: "Checkout, setup Node, restore cache, install deps"
inputs:
  node-version:
    description: "Node.js version"
    default: "20"
outputs:
  cache-hit:
    description: "Whether cache was restored"
    value: ${{ steps.cache.outputs.cache-hit }}

runs:
  using: composite
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - id: cache
      uses: actions/cache@v4
      with:
        path: ~/.npm
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    - run: npm ci
      shell: bash
```

### OIDC para Cloud Auth (sem segredos de longa duração)

```yaml
jobs:
  deploy:
    permissions:
      id-token: write   # obrigatório para OIDC
      contents: read
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
          aws-region: us-east-1
          # Nenhuma AWS_ACCESS_KEY_ID necessária!
      - run: aws s3 sync ./dist s3://my-bucket/
```

> [!important] OIDC vs Secrets Estáticos
> OIDC tokens são efêmeros (expiram com o job) e não precisam rotação manual. Configure trust policies na AWS/GCP/Azure para aceitar apenas o repositório e branch corretos: `repo:org/repo:ref:refs/heads/main`.

### Caching Avançado com actions/cache

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
    restore-keys: |
      ${{ runner.os }}-gradle-
```

### Self-Hosted Runners

```yaml
jobs:
  build-arm:
    runs-on: [self-hosted, linux, arm64, gpu]   # labels do runner
    steps:
      - run: nvidia-smi   # workload específico de hardware
```

> [!warning] Segurança com Self-Hosted Runners
> Nunca use self-hosted runners em repositórios públicos — PRs de forks executam código arbitrário no seu runner. Use runners efêmeros (registro único) e isolamento via containers ou VMs.

---

## Gotchas

> [!bug] Contextos disponíveis por evento
> `github.event.pull_request.head.sha` só existe em eventos `pull_request`. Em `push`, use `github.sha`. Acessar contextos inexistentes não causa erro — retorna string vazia, causando bugs silenciosos.

> [!bug] Outputs entre jobs requerem serialização
> Outputs são strings. Passar JSON como output: `echo "matrix=$(jq -c . matrix.json)" >> $GITHUB_OUTPUT` e no consumer: `fromJson(needs.job.outputs.matrix)`.

> [!bug] `continue-on-error` não afeta `needs`
> Um job com `continue-on-error: true` que falha ainda marca o workflow como falho para `needs` de outros jobs. Use `if: always()` nos dependentes.

> [!tip] Pinning de Actions por SHA
> `uses: actions/checkout@v4` pode ser alterado por um push de tag. Para segurança supply-chain, pin por SHA: `uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683`.

---

## Snippets

### Publicar Docker Image no GHCR

```yaml
- name: Log in to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: ${{ github.ref == 'refs/heads/main' }}
    tags: |
      ghcr.io/${{ github.repository }}:latest
      ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Criar Environment com Required Reviewers via API

```bash
gh api repos/{owner}/{repo}/environments/production \
  --method PUT \
  --field wait_timer=10 \
  --field reviewers='[{"type":"User","id":12345}]'
```

### Workflow Summary Customizado

```yaml
- name: Write job summary
  run: |
    echo "## Deployment Summary" >> $GITHUB_STEP_SUMMARY
    echo "| Field | Value |" >> $GITHUB_STEP_SUMMARY
    echo "|-------|-------|" >> $GITHUB_STEP_SUMMARY
    echo "| Environment | ${{ inputs.environment }} |" >> $GITHUB_STEP_SUMMARY
    echo "| Image Tag | \`${{ needs.build.outputs.tag }}\` |" >> $GITHUB_STEP_SUMMARY
```

---

## References

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [actions/toolkit](https://github.com/actions/toolkit)

## Related

- [[deployment-strategies]] — estratégias de deploy integradas ao pipeline
- [[docker]] — build e push de imagens
- [[git-advanced]] — triggers baseados em branching strategies
- [[argocd]] — GitOps após o push da imagem
- [[secrets-management]] — gestão de segredos e OIDC
