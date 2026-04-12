---
tags: [skill, devops, argocd]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [ArgoCD, Argo CD]
---

# ArgoCD

## Overview

ArgoCD é um operador Kubernetes que implementa **GitOps**: o Git é a única fonte de verdade para o estado desejado do cluster. O ArgoCD observa repositórios Git continuamente e reconcilia o estado real do cluster com o declarado — sem scripts de deploy imperativo, sem "funciona na minha máquina".

Os quatro princípios GitOps (DIVA):
- **Declarative** — todo o estado desejado é descrito como código
- **Immutable** — mudanças acontecem via commits, não mutação direta
- **Versioned** — histórico completo, auditável, revertível
- **Automated** — reconciliação contínua e automática

ArgoCD é o runtime desses princípios no Kubernetes. Integra-se ao [[github-actions]] e [[gitlab-ci]] via push de manifests ao repositório GitOps, e expande o que [[kubernetes-basics]] oferece com UI, RBAC, e multi-cluster.

Ver também: [[kubernetes-basics]], [[github-actions]], [[gitlab-ci]], [[deployment-strategies]], [[terraform]]

---

## Core Concepts

### Application CRD

A `Application` é o recurso central. Define: onde estão os manifests (source) e onde aplicar (destination).

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io   # cascade delete
spec:
  project: production

  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: apps/my-app/overlays/production

  destination:
    server: https://kubernetes.default.svc
    namespace: my-app

  syncPolicy:
    automated:
      prune: true          # remove recursos que sumiram do Git
      selfHeal: true       # reverte mudanças manuais no cluster
      allowEmpty: false    # nunca sincroniza se source estiver vazio
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - ApplyOutOfSyncOnly=true    # só re-aplica o que mudou
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Sync Policies

**Manual** — sync só ocorre via UI, CLI (`argocd app sync`), ou API. Útil para produção com gates humanos.

**Automated** — ArgoCD monitora o repo e aplica mudanças automaticamente. Combinar com `selfHeal` garante drift correction — qualquer `kubectl edit` manual é revertido.

```bash
# CLI commands essenciais
argocd app sync my-app --prune                    # sync forçado
argocd app sync my-app --dry-run                  # preview sem aplicar
argocd app diff my-app                            # mostra diff entre Git e cluster
argocd app rollback my-app 3                      # rollback para revision 3
argocd app history my-app                         # lista de syncs anteriores
argocd app set my-app --sync-policy automated     # habilita auto-sync via CLI
```

### Health Checks

ArgoCD avalia a saúde dos recursos com checks customizáveis via Lua scripts.

```yaml
# argocd-cm ConfigMap — health check customizado para CRD
data:
  resource.customizations.health.CronJob: |
    hs = {}
    if obj.status ~= nil then
      if obj.status.active ~= nil and #obj.status.active > 0 then
        hs.status = "Progressing"
        hs.message = "Job running"
        return hs
      end
    end
    hs.status = "Healthy"
    return hs

  # Override para Deployment — considera degraded se < 50% replicas
  resource.customizations.health.apps_Deployment: |
    hs = {}
    if obj.status ~= nil then
      local desired = obj.spec.replicas or 1
      local ready = obj.status.readyReplicas or 0
      if ready >= math.ceil(desired * 0.5) then
        hs.status = "Healthy"
      else
        hs.status = "Degraded"
        hs.message = string.format("%d/%d replicas ready", ready, desired)
      end
    end
    return hs
```

---

## Patterns

### Helm Integration

ArgoCD pode renderizar charts Helm nativamente sem `helm install` — os manifests renderizados são gerenciados pelo ArgoCD.

```yaml
source:
  repoURL: https://charts.bitnami.com/bitnami
  chart: postgresql
  targetRevision: 13.4.0
  helm:
    releaseName: postgres
    values: |
      auth:
        database: mydb
        username: myuser
      primary:
        persistence:
          size: 20Gi
    # Ou referência a arquivo de values no mesmo repo
    valueFiles:
      - values.yaml
      - values-production.yaml
```

**Multi-source Application** (ArgoCD v2.6+) — chart de um registry + values de outro repo:

```yaml
sources:
  - repoURL: https://charts.example.com
    chart: my-app
    targetRevision: 1.2.3
    helm:
      valueFiles:
        - $values/envs/production/values.yaml
  - repoURL: https://github.com/org/gitops-config
    targetRevision: main
    ref: values     # referência usada acima como $values
```

### Kustomize Integration

```yaml
source:
  repoURL: https://github.com/org/gitops-repo
  targetRevision: main
  path: apps/my-app/overlays/production
  kustomize:
    images:
      - my-app=ghcr.io/org/my-app:v1.2.3   # image tag override sem editar kustomization.yaml
    namePrefix: prod-
    commonLabels:
      env: production
```

**Update automático de imagem com ArgoCD Image Updater:**

```yaml
# Annotation na Application para auto-update de tag
metadata:
  annotations:
    argocd-image-updater.argoproj.io/image-list: my-app=ghcr.io/org/my-app
    argocd-image-updater.argoproj.io/my-app.update-strategy: semver
    argocd-image-updater.argoproj.io/my-app.semver-constraint: ">=1.0.0 <2.0.0"
    argocd-image-updater.argoproj.io/write-back-method: git   # commit a nova tag no repo
```

### ApplicationSets — Multi-Cluster e Multi-Environment

ApplicationSet gera múltiplas Applications automaticamente a partir de generators.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-app-all-envs
spec:
  generators:
    # Generator de lista: define parâmetros por ambiente
    - list:
        elements:
          - cluster: staging
            url: https://staging.k8s.example.com
            namespace: my-app
            values_file: values-staging.yaml
          - cluster: production
            url: https://prod.k8s.example.com
            namespace: my-app
            values_file: values-production.yaml

    # Ou generator de clusters registrados no ArgoCD
    # - clusters:
    #     selector:
    #       matchLabels:
    #         env: production

  template:
    metadata:
      name: "my-app-{{cluster}}"
    spec:
      project: default
      source:
        repoURL: https://github.com/org/gitops-repo
        targetRevision: main
        path: apps/my-app
        helm:
          valueFiles:
            - "{{values_file}}"
      destination:
        server: "{{url}}"
        namespace: "{{namespace}}"
      syncPolicy:
        automated:
          selfHeal: true
```

### Sync Waves e Hooks

Sync waves controlam a **ordem** de aplicação dentro de um sync. Hooks executam jobs em momentos específicos do ciclo.

```yaml
# Roda antes dos outros recursos (wave -1)
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
    argocd.argoproj.io/sync-wave: "-1"
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: ghcr.io/org/my-app:$IMAGE_TAG
          command: ["python", "manage.py", "migrate"]
---
# Roda após sync completar com sucesso
apiVersion: batch/v1
kind: Job
metadata:
  name: smoke-test
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookFailed
    argocd.argoproj.io/sync-wave: "5"
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: smoke
          image: ghcr.io/org/smoke-tests:latest
          env:
            - name: TARGET_URL
              value: https://my-app.example.com
```

### Notifications

```yaml
# argocd-notifications-cm
data:
  trigger.on-sync-failed: |
    - when: app.status.operationState.phase in ['Error', 'Failed']
      send: [slack-message]

  template.slack-message: |
    message: |
      Application {{.app.metadata.name}} sync {{.app.status.operationState.phase}}
      Revision: {{.app.status.sync.revision}}
      {{if .app.status.operationState.message}}
      Message: {{.app.status.operationState.message}}
      {{end}}
```

---

## Gotchas

> [!bug] `prune: true` pode deletar recursos não-gerenciados
> Se um recurso no cluster tem o label `app.kubernetes.io/managed-by: argocd` mas não está no Git, ele será deletado no próximo sync. Use `argocd app set --sync-option NoPrune=true` para recursos que devem ser ignorados.

> [!bug] Helm hooks ignorados pelo ArgoCD
> Helm hooks (`helm.sh/hook: pre-upgrade`) são **ignorados** pelo ArgoCD — ele não usa `helm upgrade`, apenas renderiza os manifests. Use ArgoCD sync hooks (`argocd.argoproj.io/hook`) no lugar.

> [!warning] selfHeal vs mudanças legítimas de runtime
> `selfHeal: true` reverte qualquer mudança no cluster, incluindo HPA scaling e status updates em CRDs. Configure `ignoreDifferences` para campos que devem ser ignorados:

```yaml
ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
      - /spec/replicas   # HPA gerencia isso, não o Git
  - group: ""
    kind: Secret
    jsonPointers:
      - /data            # secrets injetados externamente
```

> [!tip] App-of-Apps pattern
> Para gerenciar muitas Applications, crie uma Application "root" que aponta para um diretório contendo outros arquivos de Application. O ArgoCD recursivamente gerencia tudo.

---

## Snippets

### Login e Setup Inicial

```bash
# Port-forward para acessar UI localmente
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Senha inicial (gerada automaticamente)
kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath="{.data.password}" | base64 -d

# Login via CLI
argocd login localhost:8080 --username admin --insecure

# Registrar cluster externo
argocd cluster add production-context --name production
```

### RBAC Customizado

```yaml
# argocd-rbac-cm
data:
  policy.csv: |
    # Developers: sync em staging, read-only em prod
    p, role:developer, applications, sync, staging/*, allow
    p, role:developer, applications, get, production/*, allow
    p, role:developer, applications, sync, production/*, deny

    # Binding de grupo SSO
    g, org:team-backend, role:developer

  policy.default: role:readonly
  scopes: "[groups, email]"
```

---

## References

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [ApplicationSet Controller](https://argo-cd.readthedocs.io/en/stable/user-guide/application-set/)
- [ArgoCD Image Updater](https://argocd-image-updater.readthedocs.io/)
- [GitOps Principles](https://opengitops.dev/)

## Related

- [[kubernetes-basics]] — primitivas que o ArgoCD gerencia
- [[github-actions]] — pipeline que faz push das tags de imagem
- [[gitlab-ci]] — alternativa de CI que triggera updates GitOps
- [[deployment-strategies]] — sync waves implementam canary/blue-green
- [[terraform]] — infraestrutura como código paralelo ao GitOps de app
