---
tags: [skill, devops, kubernetes]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Kubernetes, K8s]
---

# Kubernetes Basics

## Overview

Kubernetes (K8s) é o padrão de fato para orquestração de containers em produção. Vai além de simplesmente rodar containers — oferece self-healing, auto-scaling, rolling deployments, service discovery e gerenciamento declarativo de estado. Este documento cobre os conceitos fundamentais até patterns avançados como HPA com custom metrics, RBAC e Helm hooks. Conecta diretamente com [[docker]] para build de imagens, [[argocd]] para GitOps, [[terraform]] para provisionamento do cluster e [[observability]] para monitoramento.

> [!info] Versão de Referência
> Conteúdo baseado em Kubernetes 1.30+. Algumas APIs (e.g., `autoscaling/v2`) podem diferir em versões anteriores.

---

## Core Concepts

### Pods

Pod é a menor unidade deployável no K8s — um ou mais containers que compartilham rede e storage:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-pod
  labels:
    app: api
    version: v1
spec:
  containers:
    - name: api
      image: myapp/api:v1.2.3
      ports:
        - containerPort: 8000
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
      livenessProbe:
        httpGet:
          path: /health/live
          port: 8000
        initialDelaySeconds: 15
        periodSeconds: 20
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8000
        initialDelaySeconds: 5
        periodSeconds: 10
      startupProbe:
        httpGet:
          path: /health/startup
          port: 8000
        failureThreshold: 30
        periodSeconds: 10    # 5 min para inicializar
  initContainers:
    - name: wait-db
      image: busybox:1.36
      command: ['sh', '-c', 'until nc -z db-service 5432; do sleep 2; done']
```

### Services

```yaml
# ClusterIP — interno ao cluster
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP

---
# NodePort — expõe na porta do nó (30000-32767)
apiVersion: v1
kind: Service
metadata:
  name: api-nodeport
spec:
  type: NodePort
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
      nodePort: 30080

---
# LoadBalancer — provisionado pelo cloud provider
apiVersion: v1
kind: Service
metadata:
  name: api-lb
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-internal: "true"
spec:
  type: LoadBalancer
  selector:
    app: api
  ports:
    - port: 443
      targetPort: 8000
```

### Deployments: Rolling Update e Recreate

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  annotations:
    kubernetes.io/change-cause: "v1.2.3 — add rate limiting"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1         # +1 pod além do desejado durante update
      maxUnavailable: 0   # zero downtime
  template:
    metadata:
      labels:
        app: api
        version: v1.2.3
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: myapp/api:v1.2.3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]  # drena conexões antes de terminar
```

```bash
# Rollback
kubectl rollout undo deployment/api
kubectl rollout undo deployment/api --to-revision=2
kubectl rollout history deployment/api
```

---

## Patterns

### ConfigMaps e Secrets

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  LOG_LEVEL: "info"
  MAX_WORKERS: "4"
  config.yaml: |
    server:
      port: 8000
      timeout: 30s
    database:
      pool_size: 10

---
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
type: Opaque
stringData:                  # stringData codifica automaticamente
  DATABASE_URL: "postgresql://user:pass@db:5432/app"
  JWT_SECRET: "super-secret-key"
```

```yaml
# Consumindo no Pod
spec:
  containers:
    - name: api
      envFrom:
        - configMapRef:
            name: api-config
        - secretRef:
            name: api-secrets
      volumeMounts:
        - name: config-volume
          mountPath: /etc/app
  volumes:
    - name: config-volume
      configMap:
        name: api-config
        items:
          - key: config.yaml
            path: config.yaml
```

### Ingress com Nginx e TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.example.com]
      secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
          - path: /static
            pathType: Prefix
            backend:
              service:
                name: static-service
                port:
                  number: 80
```

### HPA com CPU e Custom Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: AverageValue
          averageValue: 400Mi
    - type: Pods                         # custom metric via Prometheus Adapter
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300    # evita flapping
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
```

### RBAC

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api-sa
  namespace: production

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: api-role
  namespace: production
rules:
  - apiGroups: [""]
    resources: [configmaps, secrets]
    verbs: [get, list, watch]
  - apiGroups: [""]
    resources: [pods]
    verbs: [get, list]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: api-rolebinding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: api-sa
    namespace: production
roleRef:
  kind: Role
  name: api-role
  apiGroup: rbac.authorization.k8s.io
```

### Helm Charts

Estrutura básica de um chart:

```
myapp/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── configmap.yaml
│   └── NOTES.txt
└── charts/              # sub-charts (dependências)
```

```yaml
# Chart.yaml
apiVersion: v2
name: myapp
description: My Application
version: 0.3.1
appVersion: "1.2.3"
dependencies:
  - name: postgresql
    version: "13.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  {{- with .Values.image }}
  template:
    spec:
      containers:
        - image: "{{ .repository }}:{{ .tag | default $.Chart.AppVersion }}"
          imagePullPolicy: {{ .pullPolicy }}
  {{- end }}
```

```yaml
# Hooks — executar migrations antes do upgrade
apiVersion: batch/v1
kind: Job
metadata:
  name: migrations
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrations
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["alembic", "upgrade", "head"]
```

### PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
spec:
  minAvailable: 2      # ou maxUnavailable: 1
  selector:
    matchLabels:
      app: api
```

---

## Gotchas

> [!warning] Armadilhas Frequentes
> - **Requests vs Limits**: sem `requests`, o scheduler não consegue alocar pods corretamente. Sem `limits`, um pod pode consumir todos os recursos do nó. Sempre defina ambos.
> - **Liveness vs Readiness**: Liveness incorreta pode causar restart loops. Readiness remove o pod do Service temporariamente — use para warmup, não para checagem de dependências externas.
> - **ImagePullPolicy**: `Always` em produção aumenta latência de startup. Use `IfNotPresent` com tags imutáveis (SHA digest).
> - **Secret encoding**: Secrets são apenas Base64 — não são criptografados por padrão. Use Sealed Secrets ou External Secrets Operator.
> - **Namespace ResourceQuota**: sem quotas, um namespace pode consumir todo o cluster.

> [!danger] Rolling Update sem Readiness Probe
> Um Deployment sem `readinessProbe` move tráfego para o novo pod imediatamente após iniciar, antes de estar pronto. Isso causa erros 5xx durante deploys. **Sempre configure readinessProbe.**

---

## Snippets

```bash
# Debug de Pod com problema
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous   # logs do container anterior
kubectl exec -it <pod-name> -- /bin/sh

# Forçar rollout (mesmo sem mudança de imagem)
kubectl rollout restart deployment/api

# Escalar manualmente
kubectl scale deployment/api --replicas=5

# Verificar eventos do cluster
kubectl get events --sort-by='.lastTimestamp' -n production

# Port-forward para debug local
kubectl port-forward svc/api-service 8080:80 -n production

# Verificar recursos consumidos
kubectl top pods -n production
kubectl top nodes
```

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Patterns Book](https://www.oreilly.com/library/view/kubernetes-patterns/9781492050278/)
- [Production Best Practices](https://learnk8s.io/production-best-practices)

## Related

- [[docker]] — build e registry de imagens
- [[argocd]] — GitOps e CD declarativo
- [[terraform]] — provisionamento de clusters EKS/GKE/AKS
- [[observability]] — monitoramento, traces e alertas
- [[deployment-strategies]] — canary, blue-green, feature flags
