---
tags: [skill, devops, terraform]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Terraform, TF]
---

# Terraform

## Overview

Terraform é a ferramenta IaC (Infrastructure as Code) mais adotada do mercado, usando HCL (HashiCorp Configuration Language) para descrever infraestrutura de forma declarativa. Gerencia o ciclo de vida completo de recursos: criação, atualização e destruição. Comparado ao [[pulumi]], Terraform usa uma DSL específica vs linguagens de programação completas. Integra com [[kubernetes-basics]] para gerenciar clusters, [[docker]] para registries e [[github-actions]] para CI/CD. Gerenciamento seguro de credenciais conecta com [[secrets-management]].

> [!tip] Terraform vs OpenTofu
> OpenTofu é o fork open-source do Terraform (pós mudança de licença BSL). A sintaxe é compatível. Este documento aplica-se a ambos.

---

## Core Concepts

### HCL Syntax Deep Dive

```hcl
# Locals — expressões e transformações
locals {
  env        = terraform.workspace
  is_prod    = local.env == "production"
  name_prefix = "${var.project}-${local.env}"

  # Conditional e for expressions
  instance_type = local.is_prod ? "t3.large" : "t3.micro"

  # Transformação de lista em map
  subnet_map = {
    for idx, cidr in var.subnet_cidrs :
    "subnet-${idx}" => cidr
  }

  # Flatten de nested lists
  all_tags = merge(
    var.common_tags,
    {
      Environment = local.env
      ManagedBy   = "terraform"
      UpdatedAt   = timestamp()
    }
  )
}

# Dynamic blocks — evitar repetição
resource "aws_security_group" "api" {
  name   = "${local.name_prefix}-api"
  vpc_id = module.vpc.vpc_id

  dynamic "ingress" {
    for_each = var.allowed_ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = var.allowed_cidrs
    }
  }

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [tags["UpdatedAt"]]
  }
}
```

### State Management

```hcl
# Remote backend — S3 com locking via DynamoDB
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "infra/production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:123456789:key/abc123"
    dynamodb_table = "terraform-state-lock"

    # Assume role para CI/CD
    role_arn = "arn:aws:iam::123456789:role/TerraformStateRole"
  }
}
```

```bash
# Workspaces para múltiplos ambientes
terraform workspace new staging
terraform workspace select production
terraform workspace list

# State commands essenciais
terraform state list
terraform state show aws_instance.api
terraform state mv aws_instance.old aws_instance.new   # renomear sem recriar
terraform state rm aws_s3_bucket.temp                  # remover do state sem destruir
terraform state pull > backup.tfstate                  # backup manual
```

### Módulos: Composição e Versionamento

```hcl
# Consumindo módulo do registry
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${local.name_prefix}-vpc"
  cidr = var.vpc_cidr

  azs             = data.aws_availability_zones.available.names
  private_subnets = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 8, k + 10)]

  enable_nat_gateway     = local.is_prod
  single_nat_gateway     = !local.is_prod
  enable_dns_hostnames   = true

  tags = local.all_tags
}

# Módulo local com interface clara
module "ecs_service" {
  source = "./modules/ecs-service"

  name           = "api"
  cluster_id     = module.ecs_cluster.id
  image          = "${module.ecr.repository_url}:${var.image_tag}"
  desired_count  = local.is_prod ? 3 : 1
  cpu            = 512
  memory         = 1024

  environment_variables = {
    DATABASE_URL = module.rds.connection_string
    REDIS_URL    = module.elasticache.primary_endpoint
  }

  secrets = {
    JWT_SECRET = aws_secretsmanager_secret.jwt.arn
  }

  target_group_arn = module.alb.target_group_arns["api"]
}
```

Estrutura de módulo reutilizável:
```
modules/ecs-service/
├── main.tf          # recursos principais
├── variables.tf     # inputs com validações
├── outputs.tf       # outputs expostos
├── versions.tf      # required_providers
└── README.md        # gerado pelo terraform-docs
```

### Data Sources e Import

```hcl
# Data sources — buscar recursos existentes
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "production/db/password"
}
```

```hcl
# Import block (Terraform 1.5+) — preferível ao CLI import
import {
  to = aws_s3_bucket.existing_bucket
  id = "my-existing-bucket-name"
}

resource "aws_s3_bucket" "existing_bucket" {
  bucket = "my-existing-bucket-name"

  # Gerar config automaticamente: terraform plan -generate-config-out=generated.tf
}
```

### Lifecycle Rules e Moved Blocks

```hcl
resource "aws_instance" "api" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = local.instance_type

  lifecycle {
    create_before_destroy = true   # zero-downtime replacement
    prevent_destroy       = local.is_prod  # proteção contra destruição acidental
    replace_triggered_by  = [       # forçar replacement quando outro recurso muda
      aws_launch_template.api.latest_version
    ]
    ignore_changes = [             # ignorar mudanças fora do Terraform
      user_data,
      tags["LastDeployedBy"],
    ]
  }
}

# Moved block — renomear recurso sem destroy/create
moved {
  from = aws_security_group.old_name
  to   = aws_security_group.new_name
}

# Moved dentro de módulo
moved {
  from = aws_instance.api
  to   = module.compute.aws_instance.api
}
```

---

## Patterns

### CI/CD Integration: Plan em PR, Apply no Merge

```yaml
# .github/workflows/terraform.yml — ver [[github-actions]] para detalhes completos
on:
  pull_request:
    paths: ["infra/**"]
  push:
    branches: [main]
    paths: ["infra/**"]

jobs:
  terraform:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write    # OIDC para AWS

    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/TerraformCI
          aws-region: us-east-1

      - run: terraform init -backend-config=backends/${{ env.ENV }}.hcl

      - run: terraform validate

      - run: |
          terraform plan -out=tfplan -detailed-exitcode 2>&1 | tee plan.txt
          echo "exitcode=$?" >> $GITHUB_OUTPUT

      - name: Post plan to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const plan = require('fs').readFileSync('plan.txt', 'utf8')
            github.rest.issues.createComment({
              ...context.repo,
              issue_number: context.issue.number,
              body: `\`\`\`\n${plan.slice(-65000)}\n\`\`\``
            })

      - name: Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve tfplan
```

### Drift Detection

```bash
# Detectar drift entre state e infra real
terraform plan -detailed-exitcode
# exit code 0 = sem mudanças, 1 = erro, 2 = mudanças detectadas

# Drift detection agendado via CI
terraform plan -refresh-only   # atualiza state sem modificar infra
terraform apply -refresh-only  # aceita o drift no state
```

### Terraform Test (1.6+)

```hcl
# tests/vpc.tftest.hcl
variables {
  env        = "test"
  vpc_cidr   = "10.99.0.0/16"
  project    = "myapp"
}

run "vpc_created_correctly" {
  command = plan

  assert {
    condition     = module.vpc.vpc_cidr_block == "10.99.0.0/16"
    error_message = "VPC CIDR incorreto"
  }

  assert {
    condition     = length(module.vpc.private_subnets) == 3
    error_message = "Deve ter 3 subnets privadas"
  }
}

run "security_group_rules" {
  command = apply

  assert {
    condition     = length(aws_security_group.api.ingress) > 0
    error_message = "Security group sem regras de ingress"
  }
}
```

---

## Gotchas

> [!warning] Armadilhas do Terraform
> - **`terraform destroy` acidental**: use `prevent_destroy = true` em recursos críticos e proteja o branch main com aprovação manual.
> - **State em local**: nunca use state local em team/CI. Sempre remote backend com locking.
> - **`count` vs `for_each`**: `count` usa índice numérico — remover item do meio causa destroy/recreate de todos os posteriores. Use `for_each` com strings para recursos que podem ser removidos individualmente.
> - **Sensitive outputs**: marque outputs com dados sensíveis como `sensitive = true`. Ainda assim, ficam no state em plaintext — use backend criptografado.
> - **Provider version pinning**: sem `~> X.Y`, um `terraform init -upgrade` pode quebrar o plano.

> [!danger] Parallel Apply
> Nunca rode `terraform apply` em paralelo no mesmo workspace/state. O DynamoDB lock previne, mas se bypassado (ou em backends sem lock), o state pode corromper. Em CI, use filas ou locks de pipeline.

---

## Snippets

```bash
# Workflow diário
terraform fmt -recursive          # formatar HCL
terraform validate                # validar sintaxe e referências
terraform plan -out=tfplan        # planejar e salvar
terraform show -json tfplan | jq  # inspecionar plano em JSON
terraform apply tfplan            # aplicar plano salvo

# Targeting — aplicar apenas recurso específico
terraform plan -target=module.vpc
terraform apply -target=aws_security_group.api

# Atualizar apenas módulo específico
terraform init -upgrade -target=module.vpc

# Debugging
TF_LOG=DEBUG terraform plan 2>&1 | tee debug.log
```

---

## References

- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Test Framework](https://developer.hashicorp.com/terraform/language/tests)
- [OpenTofu](https://opentofu.org/docs/)

## Related

- [[pulumi]] — IaC com linguagens de programação completas
- [[kubernetes-basics]] — gerenciar clusters EKS/GKE via Terraform
- [[docker]] — ECR/registry via Terraform
- [[github-actions]] — pipeline de plan/apply
- [[secrets-management]] — AWS Secrets Manager, Vault integration
