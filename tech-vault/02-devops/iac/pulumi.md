---
tags: [skill, devops, pulumi]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Pulumi]
---

# Pulumi

## Overview

Pulumi é uma plataforma IaC (Infrastructure as Code) que usa linguagens de programação de propósito geral — [[typescript]], [[python]], Go, C#, Java — em vez de DSLs. Isso significa que toda a expressividade de uma linguagem real (loops, condicionais, abstrações, testes unitários) fica disponível para infraestrutura. Comparado ao [[terraform]], Pulumi tem uma curva de entrada maior mas oferece poder de abstração superior, especialmente para times que já dominam [[typescript]] ou [[python]]. Integra com [[kubernetes-basics]] via Pulumi Kubernetes Provider e [[github-actions]] para pipelines de CI/CD.

> [!info] Pulumi vs Terraform
> Terraform usa HCL (DSL declarativa), Pulumi usa linguagens reais. Pulumi tem melhor suporte a lógica condicional complexa, componentes reutilizáveis com tipagem e testes unitários nativos. O trade-off é maior complexidade de debugging.

---

## Core Concepts

### TypeScript SDK — Stack Básica

```typescript
// index.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";  // Crosswalk: abstrações de alto nível

const config = new pulumi.Config();
const env = pulumi.getStack();  // "dev", "staging", "production"
const isProd = env === "production";

// VPC com Crosswalk (opinionated, segue AWS best practices)
const vpc = new awsx.ec2.Vpc("main", {
    numberOfAvailabilityZones: isProd ? 3 : 2,
    natGateways: { strategy: isProd ? "OnePerAz" : "Single" },
    tags: { Environment: env, ManagedBy: "pulumi" },
});

// RDS com configuração condicional por ambiente
const db = new aws.rds.Instance("postgres", {
    engine: "postgres",
    engineVersion: "16.2",
    instanceClass: isProd ? "db.t3.large" : "db.t3.micro",
    allocatedStorage: isProd ? 100 : 20,
    multiAz: isProd,
    deletionProtection: isProd,
    dbSubnetGroupName: new aws.rds.SubnetGroup("db-subnets", {
        subnetIds: vpc.privateSubnetIds,
    }).name,
    vpcSecurityGroupIds: [dbSg.id],
    password: config.requireSecret("dbPassword"),  // lê do Pulumi config (criptografado)
    username: "app",
    dbName: "appdb",
    skipFinalSnapshot: !isProd,
    backupRetentionPeriod: isProd ? 7 : 1,
});

// Exportar outputs
export const dbEndpoint = db.endpoint;
export const vpcId = vpc.vpcId;
export const privateSubnetIds = vpc.privateSubnetIds;
```

### Python SDK — Padrões Avançados

```python
# __main__.py
import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s
from typing import Optional

config = pulumi.Config()
stack = pulumi.get_stack()

# ComponentResource — abstração reutilizável (equivalente a módulo Terraform)
class ApiService(pulumi.ComponentResource):
    """Componente que encapsula ECS Service + ALB Target Group + IAM."""

    def __init__(
        self,
        name: str,
        image: str,
        cpu: int = 256,
        memory: int = 512,
        desired_count: int = 1,
        environment: Optional[dict] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("myapp:index:ApiService", name, {}, opts)

        child_opts = pulumi.ResourceOptions(parent=self)

        # Task Definition
        self.task_def = aws.ecs.TaskDefinition(
            f"{name}-task",
            family=name,
            cpu=str(cpu),
            memory=str(memory),
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            container_definitions=pulumi.Output.json_dumps([{
                "name": name,
                "image": image,
                "portMappings": [{"containerPort": 8000}],
                "environment": [
                    {"name": k, "value": v}
                    for k, v in (environment or {}).items()
                ],
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {
                        "awslogs-group": f"/ecs/{name}",
                        "awslogs-region": aws.get_region().name,
                        "awslogs-stream-prefix": "ecs",
                    },
                },
            }]),
            opts=child_opts,
        )

        self.service = aws.ecs.Service(
            f"{name}-service",
            cluster=cluster_arn,
            task_definition=self.task_def.arn,
            desired_count=desired_count,
            launch_type="FARGATE",
            opts=child_opts,
        )

        # Registrar outputs do componente
        self.register_outputs({
            "service_name": self.service.name,
            "task_definition_arn": self.task_def.arn,
        })

# Uso do componente
api = ApiService(
    "api",
    image=f"{ecr_repo.repository_url}:{image_tag}",
    cpu=512,
    memory=1024,
    desired_count=2 if stack == "production" else 1,
    environment={"LOG_LEVEL": "info", "ENV": stack},
)
```

---

## Patterns

### Stack Management e Stack References

Stacks são instâncias isoladas de uma configuração Pulumi — análogo a workspaces do Terraform, mas com suporte a referencias entre stacks:

```typescript
// Stack: networking (gerencia VPC, subnets)
export const vpcId = vpc.id;
export const privateSubnetIds = vpc.privateSubnetIds;

// Stack: application (consome outputs de networking)
import * as pulumi from "@pulumi/pulumi";

const networkStack = new pulumi.StackReference(
    `myorg/networking/${pulumi.getStack()}`  // mesmo ambiente
);

const vpcId = networkStack.getOutput("vpcId");
const subnetIds = networkStack.getOutput("privateSubnetIds");

// Usar outputs de outra stack como inputs
const cluster = new aws.ecs.Cluster("app-cluster", {
    // vpcId é um pulumi.Output<string> — lazy evaluation
});
```

```bash
# Estrutura multi-stack
pulumi stack init dev
pulumi stack init staging
pulumi stack init production

# Configuração por stack (criptografada para secrets)
pulumi config set aws:region us-east-1
pulumi config set --secret dbPassword "super-secret"
pulumi config set desiredCount 3 --stack production

# Ver configuração
pulumi config --stack production
```

### State Backends

Pulumi suporta múltiplos backends para state, similar ao [[terraform]]:

```bash
# Pulumi Cloud (padrão) — gerenciado, com UI
pulumi login

# S3 backend (self-hosted)
pulumi login s3://my-pulumi-state-bucket

# Local backend (desenvolvimento)
pulumi login --local

# Azure Blob Storage
pulumi login azblob://my-state-container

# Configurar backend no projeto
# Pulumi.yaml
name: myapp
runtime: nodejs
backend:
  url: s3://my-pulumi-state-bucket?region=us-east-1&awssdk=v2
```

> [!warning] Migração de Backend
> Migrar state entre backends (`pulumi stack export | pulumi stack import`) requer cuidado. Sempre faça backup antes. Secrets criptografados com a passphrase do backend antigo precisam ser re-encriptados.

### Automation API — Infraestrutura Programática

A Automation API permite usar Pulumi como biblioteca, sem CLI — ideal para plataformas internas de self-service:

```typescript
// automation-api.ts
import { LocalWorkspace, Stack } from "@pulumi/pulumi/automation";
import * as path from "path";

async function deployEnvironment(envName: string, imageTag: string) {
    const workDir = path.join(__dirname, "infra");

    // Criar ou selecionar stack programaticamente
    const stack = await LocalWorkspace.createOrSelectStack({
        stackName: envName,
        workDir,
        projectSettings: {
            name: "myapp",
            runtime: "nodejs",
            backend: { url: "s3://my-state-bucket" },
        },
    });

    // Configurar stack
    await stack.setConfig("imageTag", { value: imageTag });
    await stack.setConfig("environment", { value: envName });

    // Capturar output em tempo real
    const up = await stack.up({
        onOutput: (msg) => console.log(msg),
        onEvent: (event) => {
            if (event.resourcePreEvent) {
                console.log(`Updating: ${event.resourcePreEvent.metadata.urn}`);
            }
        },
    });

    return {
        outputs: up.outputs,
        summary: up.summary,
    };
}

// API endpoint que provisiona infraestrutura sob demanda
app.post("/environments", async (req, res) => {
    const { name, imageTag } = req.body;
    const result = await deployEnvironment(name, imageTag);
    res.json({ endpoint: result.outputs.apiUrl.value });
});
```

> [!tip] Automation API Use Cases
> - Plataformas de preview environments (deploy por PR)
> - Self-service de infraestrutura para devs
> - Testes de integração que provisionam infra real e destroem ao final
> - Pipelines de rotação de credenciais automatizados

### CrossGuard — Policy as Code

```typescript
// policy/index.ts
import { PolicyPack, validateResourceOfType } from "@pulumi/policy";
import * as aws from "@pulumi/aws";

new PolicyPack("security-policies", {
    policies: [
        {
            name: "s3-no-public-access",
            description: "S3 buckets must not have public access enabled",
            enforcementLevel: "mandatory",  // ou "advisory"
            validateResource: validateResourceOfType(
                aws.s3.Bucket,
                (bucket, args, reportViolation) => {
                    if (bucket.acl === "public-read" || bucket.acl === "public-read-write") {
                        reportViolation(
                            `S3 bucket ${args.name} has public ACL. Use private ACL and bucket policies.`
                        );
                    }
                }
            ),
        },
        {
            name: "require-tags",
            description: "All resources must have Environment and Team tags",
            enforcementLevel: "mandatory",
            validateResource: (args, reportViolation) => {
                const tags = (args.props as any).tags || {};
                if (!tags["Environment"]) {
                    reportViolation(`Resource ${args.name} missing required tag: Environment`);
                }
                if (!tags["Team"]) {
                    reportViolation(`Resource ${args.name} missing required tag: Team`);
                }
            },
        },
        {
            name: "rds-encryption-required",
            description: "RDS instances must have encryption at rest",
            enforcementLevel: "mandatory",
            validateResource: validateResourceOfType(
                aws.rds.Instance,
                (instance, args, reportViolation) => {
                    if (!instance.storageEncrypted) {
                        reportViolation(`RDS instance ${args.name} must have storageEncrypted=true`);
                    }
                }
            ),
        },
    ],
});
```

```bash
# Aplicar policy pack durante preview/up
pulumi preview --policy-pack ./policy
pulumi up --policy-pack ./policy

# Policy pack no Pulumi Cloud (aplica a todas as stacks da org)
pulumi policy publish --organization myorg
```

### Dynamic Providers — Recursos Customizados

Quando o provider oficial não suporta um recurso, crie um Dynamic Provider:

```typescript
// providers/github-repo-settings.ts
import * as pulumi from "@pulumi/pulumi";
import { Octokit } from "@octokit/rest";

interface RepoSettingsInputs {
    owner: string;
    repo: string;
    defaultBranch: string;
    requirePrReviews: boolean;
}

const repoSettingsProvider: pulumi.dynamic.ResourceProvider = {
    async create(inputs: RepoSettingsInputs) {
        const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

        await octokit.repos.update({
            owner: inputs.owner,
            repo: inputs.repo,
            default_branch: inputs.defaultBranch,
        });

        if (inputs.requirePrReviews) {
            await octokit.repos.updateBranchProtection({
                owner: inputs.owner,
                repo: inputs.repo,
                branch: inputs.defaultBranch,
                required_pull_request_reviews: { required_approving_review_count: 1 },
                enforce_admins: true,
                required_status_checks: null,
                restrictions: null,
            });
        }

        return { id: `${inputs.owner}/${inputs.repo}`, outs: inputs };
    },

    async delete(id, props) {
        // Cleanup se necessário
    },
};

export class RepoSettings extends pulumi.dynamic.Resource {
    constructor(name: string, args: RepoSettingsInputs, opts?: pulumi.CustomResourceOptions) {
        super(repoSettingsProvider, name, args, opts);
    }
}
```

### Migração do Terraform para Pulumi

```bash
# Converter HCL para Pulumi TypeScript automaticamente
pulumi convert --from terraform --language typescript --out pulumi/

# Importar state existente do Terraform
pulumi import --from terraform terraform.tfstate

# Importar recurso individual
pulumi import aws:s3/bucket:Bucket my-bucket my-existing-bucket-name
```

> [!warning] Limitações da Conversão
> `pulumi convert` gera código funcional mas frequentemente não idiomático. Revise manualmente para substituir recursos individuais por componentes reutilizáveis e aplicar padrões TypeScript/Python corretos.

### Integração com Kubernetes

```typescript
// Provisionar EKS + deployer aplicação via Kubernetes provider
import * as eks from "@pulumi/eks";
import * as k8s from "@pulumi/kubernetes";

const cluster = new eks.Cluster("prod-cluster", {
    version: "1.30",
    nodeGroupOptions: {
        instanceType: "t3.large",
        desiredCapacity: 3,
        minSize: 2,
        maxSize: 10,
    },
    enabledClusterLogTypes: ["api", "audit", "authenticator"],
});

// Provider Kubernetes apontando para o cluster recém-criado
const k8sProvider = new k8s.Provider("eks-provider", {
    kubeconfig: cluster.kubeconfig,
});

// Deploy via Helm com o mesmo provider
const app = new k8s.helm.v3.Release("myapp", {
    chart: "myapp",
    repositoryOpts: { repo: "https://charts.mycompany.com" },
    values: {
        image: { tag: imageTag },
        replicaCount: 3,
        ingress: { enabled: true, host: "api.mycompany.com" },
    },
}, { provider: k8sProvider });

export const clusterName = cluster.eksCluster.name;
export const kubeconfig = cluster.kubeconfig;
```

---

## Gotchas

> [!warning] Armadilhas do Pulumi
> - **Output<T> vs T**: em Pulumi, quase tudo é `Output<T>` (lazy). Não use `toString()` em outputs — use `.apply()` para transformar. Erros de tipo silenciosos são comuns aqui.
> - **pulumi.all()**: para combinar múltiplos outputs, use `pulumi.all([a, b]).apply(([a, b]) => ...)`. Não use `await` em outputs fora de `apply`.
> - **Stack name em StackReference**: o formato é `org/project/stack`. Em CI, o nome da org pode diferir do esperado — use `PULUMI_ORG` env var.
> - **Secrets em config**: `config.requireSecret()` retorna `Output<string>` marcado como secret. Nunca use `config.require()` para valores sensíveis — aparecerá em logs.
> - **Component resources e dependências**: recursos filhos de um `ComponentResource` precisam ter `parent: this` em opts para herdar dependências corretamente.

> [!danger] Automation API e Concorrência
> A Automation API não tem locking nativo como o backend S3+DynamoDB do Terraform. Em plataformas de self-service, implemente seu próprio mecanismo de lock (Redis, banco de dados) para evitar deploys simultâneos na mesma stack.

---

## Snippets

```bash
# Workflow básico
pulumi stack init dev
pulumi up --yes --skip-preview        # deploy direto (CI/CD)
pulumi preview --diff                 # ver diff detalhado
pulumi destroy --yes                  # destruir stack

# Refresh — sincronizar state com realidade
pulumi refresh --yes

# Verificar outputs
pulumi stack output
pulumi stack output dbEndpoint --show-secrets

# Exportar/importar state
pulumi stack export --file backup.json
pulumi stack import --file backup.json

# Visualizar grafo de dependências
pulumi stack graph > graph.dot && dot -Tpng graph.dot -o graph.png

# Testes unitários (Jest/pytest — mock de providers)
pulumi up --target urn:pulumi:dev::myapp::aws:s3/bucket:Bucket::my-bucket
```

```typescript
// Teste unitário com mocking (Jest)
import * as pulumi from "@pulumi/pulumi";

pulumi.runtime.setMocks({
    newResource: (args) => ({
        id: `${args.name}-id`,
        state: { ...args.inputs, arn: `arn:aws:s3:::${args.inputs.bucket}` },
    }),
    call: (args) => ({ result: args.inputs }),
});

import { infra } from "./index";

test("S3 bucket must be private", async () => {
    const bucket = await infra.bucket;
    const acl = await new Promise((resolve) => bucket.acl.apply(resolve));
    expect(acl).toBe("private");
});
```

---

## References

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [Pulumi Crosswalk for AWS](https://www.pulumi.com/docs/clouds/aws/guides/)
- [Automation API Guide](https://www.pulumi.com/docs/using-pulumi/automation-api/)
- [CrossGuard Policy as Code](https://www.pulumi.com/docs/using-pulumi/crossguard/)
- [Pulumi AI — geração de código](https://www.pulumi.com/ai)

## Related

- [[terraform]] — IaC com HCL, alternativa com maior adoção de mercado
- [[typescript]] — SDK principal do Pulumi para infra type-safe
- [[python]] — SDK alternativo, popular em times de dados/ML
- [[kubernetes-basics]] — deploy e gerenciamento de clusters via Pulumi
- [[github-actions]] — integração CI/CD para plan/apply automático
