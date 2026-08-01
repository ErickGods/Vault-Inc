---
house: tech
domain: devops
type: index
updated: 2026-07-29
---

# Índice — DevOps

## CI/CD — `tech/02-devops/ci-cd/`

| Nota | O que responde | Nível |
|---|---|---|
| [[github-actions]] | Montar pipeline no GitHub além de "rodar teste": sintaxe de workflow, matrix builds, reusable workflows via `workflow_call`, composite actions e self-hosted runners. O ponto de segurança que muda a arquitetura do pipeline é OIDC para autenticar na cloud sem segredo de longa duração. Traz cache avançado, e as três pegadinhas que fazem pipeline verde mentir: contexto indisponível para o evento, output entre jobs sem serialização, e `continue-on-error` que não afeta `needs`. | advanced |
| [[gitlab-ci]] | Trabalhar com o modelo mais opinativo do GitLab: stages como primitiva contra DAG via `needs` para paralelismo máximo, `rules` no lugar de `only/except`, `include`/`extends`, environments com aprovação, registry integrado, pipelines pai-filho e merge trains — que reduzem broken build ao custo de tempo de CI. Traz review apps dinâmicas, SAST automático e `interruptible: true` para não pagar por pipeline obsoleto. | advanced |
| [[deployment-strategies]] | Escolher **como** a versão nova substitui a antiga, sabendo o que cada opção custa: blue/green (rollback em segundos, infra dobrada), canary (validação com tráfego real, quebra com sessão stateful), rolling update (sem custo extra, rollback em minutos). Traz a tabela de tempo de rollback por mecanismo, A/B testing, shadow launching, e o padrão expand/contract para migrar schema sem downtime. Insiste que health check insuficiente produz falso positivo — o deploy "passa" e o serviço está quebrado. | advanced |
| [[feature-flags]] | Desacoplar deploy de release e medir o que foi ativado: os quatro tipos de flag por vida útil (release, experiment, ops, permission), rollout percentual, kill switch, experimentação com significância estatística e trunk-based development. Compara LaunchDarkly, Unleash e Flagsmith, e trata o ciclo de vida com cleanup automatizado via CI — porque **flag é dívida técnica** e flag esquecida vira caminho de código não testado. | advanced |
| [[argocd]] | Adotar GitOps de verdade: o Git como única fonte de verdade e reconciliação contínua no lugar de script de deploy imperativo. Cobre o CRD Application, sync policies com `selfHeal` (e o conflito com mudança legítima de runtime), health checks, integração com Helm e Kustomize, ApplicationSets para multi-cluster, sync waves e o padrão app-of-apps. Aviso caro: `prune: true` deleta recurso não gerenciado. | advanced |

## Containers — `tech/02-devops/containers/`

| Nota | O que responde | Nível |
|---|---|---|
| [[docker-compose-patterns]] | Orquestrar múltiplos serviços em dev e staging sem improviso: extension fields `x-` e YAML anchors para não repetir bloco, profiles separando dev/test/prod, health checks com `depends_on: condition` para ordem real de subida. Cobre volumes named/bind/tmpfs, redes e aliases, override files por ambiente e gestão de variáveis. Alerta para o `docker compose down` que leva o volume junto. | advanced |
| [[kubernetes-basics]] | Sair do "roda container" para operar workload declarativo: pods, services, deployments com rolling update contra recreate, ConfigMaps e Secrets, Ingress com TLS, HPA com CPU e custom metrics, RBAC, Helm charts e PodDisruptionBudget. A falha que causa downtime silencioso: rolling update sem readiness probe manda tráfego para pod que ainda não subiu. | advanced |

## Infraestrutura como código — `tech/02-devops/iac/`

| Nota | O que responde | Nível |
|---|---|---|
| [[terraform]] | Provisionar infraestrutura declarativa com HCL e sobreviver ao state: remote state, módulos com versionamento, data sources e `import`, lifecycle rules e `moved` blocks para refatorar sem destruir recurso. Traz o fluxo de CI/CD que funciona (plan no PR, apply no merge), drift detection e `terraform test` (1.6+), além da relação com OpenTofu. | advanced |
| [[pulumi]] | Decidir se vale trocar a DSL por linguagem de programação real em infraestrutura — loops, condicionais, abstração e teste unitário — e o que isso custa em curva de entrada. Cobre SDKs TypeScript e Python, stack references, state backends, Automation API para infraestrutura programática, CrossGuard como policy as code, dynamic providers e a migração vinda do Terraform, com as limitações da conversão automática declaradas. | advanced |

## Monitoramento — `tech/02-devops/monitoring/`

| Nota | O que responde | Nível |
|---|---|---|
| [[observability]] | Instrumentar para perguntar **por quê** algo quebrou, não só **se** quebrou: OpenTelemetry com auto-instrumentação e Collector, Prometheus com PromQL e recording rules, service discovery no Kubernetes, dashboards e variáveis no Grafana, Loki com LogQL e tracing distribuído com Jaeger/Tempo. Fecha com SLI, SLO e error budget — que é o que transforma métrica em decisão de parar ou seguir lançando. Trata retenção do Prometheus como restrição de projeto, não detalhe. | advanced |

## Redes — `tech/02-devops/networking/`

| Nota | O que responde | Nível |
|---|---|---|
| [[reverse-proxy]] | Escolher e configurar a borda: comparativo Nginx, Traefik e Caddy por auto-discovery, HTTPS automático, performance, hot-reload e ecossistema. Cobre terminação SSL/TLS, health checks e circuit breaker, `X-Forwarded-For` e o risco de confiar nele sem validar, WebSocket com timeout correto, buffering contra streaming, e a exposição do socket Docker pelo Traefik. | advanced |
| [[dns-and-cdn]] | Operar as duas camadas que precedem qualquer requisição: tipos de registro, estratégia de TTL durante mudança, CNAME no apex e o conflito com e-mail, routing policies do Route53, e configuração avançada de Cloudflare — incluindo o que o modo proxied esconde e o que o modo DNS-only expõe. Cobre estratégias de cache no edge, cache poisoning via `Vary`, multi-CDN, edge functions contra origin e DDoS em camadas. | advanced |
| [[vpn-setup]] | Dar acesso seguro a recurso interno sem abrir porta: WireGuard configurado do zero e Tailscale abstraindo NAT traversal, com ACLs. Cobre site-to-site, mesh, split tunneling, integração com Docker e sidecar em Kubernetes. Duas correções de conceito que evitam incidente: `AllowedIPs` **não é firewall**, e MTU errado gera fragmentação que parece problema de aplicação. | advanced |

## Segurança — `tech/02-devops/security/`

| Nota | O que responde | Nível |
|---|---|---|
| [[secrets-management]] | Tirar credencial do repositório e do ambiente e dar a ela ciclo de vida: HashiCorp Vault com secrets dinâmicos, AppRole contra token direto, e o procedimento de seal e disaster recovery. Cobre SOPS para criptografar arquivo versionado em Git (e o que isso faz com diff em PR), Doppler, AWS Secrets Manager, Sealed Secrets e External Secrets no Kubernetes — partindo do fato de que **Secret do Kubernetes é base64, não criptografia**. Traz a hierarquia por ambiente, o padrão de rotação e audit logging. | advanced |
