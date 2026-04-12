---
tags: [skill, devops, gitlab-ci]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [GitLab CI, GitLab CI/CD]
---

# GitLab CI/CD

## Overview

GitLab CI/CD é a plataforma de automação nativa do GitLab, definida inteiramente em `.gitlab-ci.yml`. É mais opinativa que o [[github-actions]]: tem conceito de **stages** como primitiva de ordenação, suporte nativo a **environments** com aprovações, **merge trains** para serializar merges e evitar broken builds, e **Auto DevOps** para pipelines zero-config. Para workloads complexos, DAG via `needs` elimina a rigidez de stages e permite paralelismo máximo.

O GitLab também oferece um registry de containers integrado, gerenciamento de variáveis por ambiente, e integração com [[argocd]] via push/pull model.

Ver também: [[github-actions]], [[docker]], [[deployment-strategies]], [[argocd]], [[secrets-management]]

---

## Core Concepts

### Estrutura do `.gitlab-ci.yml`

```yaml
# .gitlab-ci.yml
image: node:20-alpine

variables:
  NODE_ENV: test
  DOCKER_DRIVER: overlay2
  # Variáveis definidas aqui são globais; sobrescritas por job ou CI/CD Settings

stages:
  - validate
  - build
  - test
  - security
  - deploy

# Template base com extends
.node-base: &node-base
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - node_modules/
  before_script:
    - npm ci --prefer-offline

lint:
  extends: .node-base
  stage: validate
  script:
    - npm run lint
    - npm run typecheck

unit-test:
  extends: .node-base
  stage: test
  script:
    - npm test -- --coverage --ci
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'   # regex para extrair cobertura
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths:
      - coverage/
    expire_in: 1 week
```

### Stages vs DAG (needs)

Com **stages**, todos os jobs de um stage terminam antes do próximo começar. Com **needs**, você declara dependências explícitas — job C pode começar quando A terminar, sem esperar B.

```yaml
stages: [build, test, deploy]

build-frontend:
  stage: build
  script: npm run build

build-backend:
  stage: build
  script: go build ./...

test-frontend:
  stage: test
  needs: [build-frontend]    # não espera build-backend
  script: npm test

test-backend:
  stage: test
  needs: [build-backend]     # não espera build-frontend
  script: go test ./...

deploy:
  stage: deploy
  needs: [test-frontend, test-backend]   # espera ambos
  script: ./deploy.sh
```

> [!tip] DAG reduz tempo de pipeline
> Em pipelines com muitos jobs independentes, `needs` pode reduzir o tempo total de 40-60% ao eliminar esperas desnecessárias entre stages.

---

## Patterns

### Rules vs Only/Except

`only`/`except` são legados. `rules` é mais expressivo e suporta variáveis, paths, e operadores complexos.

```yaml
deploy-staging:
  script: ./deploy.sh staging
  rules:
    - if: '$CI_COMMIT_BRANCH == "develop"'
      when: on_success
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: never            # não roda em MR pipelines
    - when: never            # default para todo o resto

deploy-prod:
  script: ./deploy.sh production
  rules:
    - if: '$CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/'   # tag semver
      when: manual           # requer aprovação manual
      allow_failure: false
```

### Include e Extends

`include` permite compor pipelines a partir de múltiplos arquivos — essencial para monorepos e templates de equipe.

```yaml
# .gitlab-ci.yml principal
include:
  - local: ".gitlab/ci/build.yml"
  - local: ".gitlab/ci/test.yml"
  - project: "infra/ci-templates"      # template em outro projeto
    ref: main
    file: "/templates/docker-build.yml"
  - template: "Security/SAST.gitlab-ci.yml"   # template nativo do GitLab

# Herança com extends
.deploy-template:
  image: bitnami/kubectl:latest
  before_script:
    - kubectl config use-context $KUBE_CONTEXT

deploy-staging:
  extends: .deploy-template
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy-prod:
  extends: .deploy-template
  environment:
    name: production
    url: https://example.com
  script:
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Environments e Approvals

```yaml
deploy-production:
  stage: deploy
  script:
    - ./deploy.sh production
  environment:
    name: production
    url: https://example.com
    on_stop: stop-production      # job para destruir o ambiente
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual                # botão no UI — requer click humano

stop-production:
  stage: deploy
  script:
    - ./teardown.sh production
  environment:
    name: production
    action: stop
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual
```

**Protected Environments** adicionam uma camada extra: apenas usuários/grupos específicos podem triggerar deploys para `production`, independentemente de permissões no projeto.

### Container Registry Integrado

```yaml
build-image:
  stage: build
  image: docker:26
  services:
    - docker:26-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - |
      docker build \
        --build-arg BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
        --build-arg VCS_REF=$CI_COMMIT_SHORT_SHA \
        --cache-from $CI_REGISTRY_IMAGE:latest \
        -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA \
        -t $CI_REGISTRY_IMAGE:latest \
        .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest
```

### Parent-Child Pipelines

Permitem decompor pipelines monolíticos. O parent spawna children que executam independentemente.

```yaml
# .gitlab-ci.yml (parent)
trigger-service-a:
  stage: build
  trigger:
    include: services/service-a/.gitlab-ci.yml
    strategy: depend    # parent aguarda child terminar

trigger-service-b:
  stage: build
  trigger:
    include: services/service-b/.gitlab-ci.yml
    strategy: depend
  rules:
    - changes:          # só triggera se houver mudanças no serviço
        - services/service-b/**/*
```

### Merge Trains

Merge trains serializam merges para garantir que o commit que chega na main **sempre** passou em CI com o estado atual da main — elimina o "passed CI but broke main" problem.

```
Fila: [MR-A] → [MR-B] → [MR-C]

Pipeline de MR-B roda com: main + MR-A + MR-B
Se MR-A falhar e for removido, MR-B é rebaseado e re-testado.
```

Habilitado em: **Settings → Merge requests → Merge trains**.

> [!warning] Merge trains aumentam tempo de CI
> Cada MR pode ser re-testado múltiplas vezes se trens à frente falharem. É um trade-off entre segurança do branch principal e velocidade de entrega.

---

## Gotchas

> [!bug] Variáveis de CI não são substituídas em `image:`
> `image: $MY_IMAGE:$CI_COMMIT_SHA` funciona, mas variáveis definidas em `variables:` no mesmo job **não** estão disponíveis em `image:` — apenas variáveis de instância/grupo/projeto e variáveis predefinidas de CI.

> [!bug] `needs` com jobs de stages posteriores
> `needs` ignora a ordem de stages por padrão. Se você precisa que um job aguarde outro de stage posterior, use `needs` com `artifacts: false` e declare o stage corretamente.

> [!bug] Cache key com arquivos inexistentes
> Se o arquivo usado na `cache.key.files` não existir no repositório, o GitLab usa a string literal como fallback — pode causar cache misses inesperados em branches que não têm o arquivo.

> [!tip] `interruptible: true` para MR pipelines
> Marque jobs que podem ser interrompidos com `interruptible: true`. Quando um novo commit é pushed em um MR, o pipeline antigo é automaticamente cancelado, economizando minutos de runner.

```yaml
test:
  script: npm test
  interruptible: true   # cancela se novo commit chegar
```

---

## Snippets

### SAST + Dependency Scanning Automático

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml

variables:
  SAST_EXCLUDED_PATHS: "spec, test, tests, tmp"
  DS_EXCLUDED_PATHS: "spec, test, tests, tmp"
```

### Dynamic Environments para Review Apps

```yaml
review:
  stage: deploy
  script:
    - ./deploy-review.sh $CI_COMMIT_REF_SLUG
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    url: https://$CI_COMMIT_REF_SLUG.review.example.com
    on_stop: stop-review
    auto_stop_in: 1 week
  rules:
    - if: '$CI_MERGE_REQUEST_ID'

stop-review:
  stage: deploy
  script:
    - ./teardown-review.sh $CI_COMMIT_REF_SLUG
  environment:
    name: review/$CI_COMMIT_REF_SLUG
    action: stop
  rules:
    - if: '$CI_MERGE_REQUEST_ID'
      when: manual
```

### Downstream Pipeline para Deploy GitOps

```yaml
trigger-gitops:
  stage: deploy
  variables:
    APP_IMAGE_TAG: $CI_COMMIT_SHA
    TARGET_ENV: production
  trigger:
    project: infra/gitops-manifests
    branch: main
    strategy: depend
```

---

## References

- [GitLab CI/CD Reference](https://docs.gitlab.com/ee/ci/yaml/)
- [GitLab CI/CD Best Practices](https://docs.gitlab.com/ee/ci/pipelines/pipeline_efficiency.html)
- [Merge Trains](https://docs.gitlab.com/ee/ci/pipelines/merge_trains.html)
- [Auto DevOps](https://docs.gitlab.com/ee/topics/autodevops/)

## Related

- [[github-actions]] — alternativa GitHub-native com workflow_call
- [[docker]] — build de imagens dentro do pipeline
- [[deployment-strategies]] — o que o pipeline executa
- [[argocd]] — GitOps receiver dos artefatos gerados
- [[secrets-management]] — CI/CD variables e vault integration
