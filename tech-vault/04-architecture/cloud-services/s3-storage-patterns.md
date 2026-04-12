---
tags: [skill, architecture, s3]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [S3, AWS S3, Object Storage]
---

# S3 Storage Patterns

## Overview

Amazon S3 é o serviço de object storage da AWS, base de praticamente toda arquitetura de dados na nuvem. Vai muito além de "um lugar para guardar arquivos" — com lifecycle policies, replication, event notifications e S3 Select, serve como fundação de [[data-lake-patterns]], CDN origins e sistemas de media como o [[media-pipeline]]. Provisionado via [[terraform]], integra-se ao [[cloudinary]] como origem e ao [[secrets-management]] para chaves de acesso.

> [!info] Object Storage vs Block vs File
> S3 é eventual consistency (para puts novos é strong read-after-write desde 2020), sem hierarquia real de diretórios (prefixes são convenção), sem lock de arquivo. Ideal para blobs imutáveis de qualquer tamanho.

## Core Concepts

### Presigned URLs

Delegam acesso temporário sem expor credenciais AWS. Funcionam para GET (download) e PUT (upload direto do cliente).

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    config=Config(signature_version="s3v4"),
)

# Upload presigned — cliente faz PUT direto no S3
def generate_upload_url(bucket: str, key: str, content_type: str, expires: int = 300):
    return s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ContentType": content_type,
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": settings.KMS_KEY_ID,
        },
        ExpiresIn=expires,
        HttpMethod="PUT",
    )

# Download presigned com Content-Disposition
def generate_download_url(bucket: str, key: str, filename: str, expires: int = 3600):
    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ResponseContentDisposition": f'attachment; filename="{filename}"',
        },
        ExpiresIn=expires,
    )
```

> [!warning] Presigned URL expira no momento de geração, não de uso
> Se o token AWS que gerou a URL expirar antes da URL, o acesso é negado mesmo que a URL ainda esteja no prazo. Use IAM roles com tokens de longa duração para geração de presigned URLs críticas.

### Lifecycle Policies

Automatizam transição entre storage classes e expiração:

```json
{
  "Rules": [
    {
      "ID": "media-tiering",
      "Status": "Enabled",
      "Filter": { "Prefix": "uploads/" },
      "Transitions": [
        { "Days": 30,  "StorageClass": "STANDARD_IA" },
        { "Days": 90,  "StorageClass": "GLACIER_IR" },
        { "Days": 365, "StorageClass": "DEEP_ARCHIVE" }
      ],
      "NoncurrentVersionTransitions": [
        { "NoncurrentDays": 7, "StorageClass": "STANDARD_IA" }
      ],
      "NoncurrentVersionExpiration": { "NoncurrentDays": 30 },
      "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 3 }
    }
  ]
}
```

**Storage Classes (custo crescente de retrieval, decrescente de storage):**
- `STANDARD` — acesso frequente, latência ms, sem taxa de retrieval
- `STANDARD_IA` — acesso infrequente, taxa de retrieval por GB, mínimo 30 dias
- `GLACIER_IR` — retrieval em ms, custo ~60% menor que STANDARD
- `GLACIER_FLEXIBLE` — retrieval 3-5h (bulk: 5-12h, expedited: 1-5min)
- `DEEP_ARCHIVE` — mais barato (~$0.00099/GB/mês), retrieval 12-48h
- `INTELLIGENT_TIERING` — move automaticamente entre tiers, ideal para padrões imprevisíveis

### Versioning e MFA Delete

```python
# Habilitar versioning via boto3
s3.put_bucket_versioning(
    Bucket=bucket_name,
    VersioningConfiguration={"Status": "Enabled"},
)

# Listar versões de um objeto
response = s3.list_object_versions(Bucket=bucket_name, Prefix="important/file.pdf")
for version in response.get("Versions", []):
    print(version["VersionId"], version["LastModified"], version["IsLatest"])

# Deletar versão específica (requer MFA Delete se habilitado)
s3.delete_object(
    Bucket=bucket_name,
    Key="important/file.pdf",
    VersionId="abc123xyz",
)
```

MFA Delete previne deleção de versões ou desabilitação de versioning sem token MFA — proteção contra ransomware e erros humanos.

### Replicação Multi-Region

**CRR (Cross-Region Replication)** — entre regiões diferentes, para DR e redução de latência global.
**SRR (Same-Region Replication)** — mesma região, para isolamento de contas ou ambientes.

```hcl
# terraform — configuração de CRR
resource "aws_s3_bucket_replication_configuration" "replication" {
  bucket = aws_s3_bucket.source.id
  role   = aws_iam_role.replication.arn

  rule {
    id     = "replicate-all"
    status = "Enabled"

    filter { prefix = "" }

    destination {
      bucket        = aws_s3_bucket.destination.arn
      storage_class = "STANDARD_IA"

      replication_time {
        status  = "Enabled"
        time { minutes = 15 }  # S3 RTC — 99.99% em 15 min
      }
      metrics { status = "Enabled" }
    }

    delete_marker_replication { status = "Enabled" }
  }
}
```

### Encryption

| Modo | Chave gerenciada por | Use case |
|------|---------------------|----------|
| SSE-S3 (AES-256) | AWS | Compliance básico, sem custo adicional |
| SSE-KMS | AWS KMS (sua key) | Audit trail, key rotation, cross-account |
| SSE-C | Cliente (você) | Controle total da chave, sem armazenar na AWS |
| CSE | Cliente antes do upload | Dados ultra-sensíveis, zero-trust na AWS |

```python
# Upload com SSE-KMS
s3.put_object(
    Bucket=bucket,
    Key=key,
    Body=data,
    ServerSideEncryption="aws:kms",
    SSEKMSKeyId=f"arn:aws:kms:{region}:{account_id}:key/{key_id}",
)

# Bucket policy para forçar encryption em todo upload
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::my-bucket/*",
  "Condition": {
    "StringNotEquals": {
      "s3:x-amz-server-side-encryption": "aws:kms"
    }
  }
}
```

### Event Notifications

S3 pode disparar eventos para SNS, SQS ou Lambda em criações, deleções e restaurações:

```python
# Terraform: notificação para SQS em uploads de imagens
resource "aws_s3_bucket_notification" "uploads" {
  bucket = aws_s3_bucket.media.id

  queue {
    id            = "image-processing"
    queue_arn     = aws_sqs_queue.image_processor.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "uploads/raw/"
    filter_suffix = ".jpg"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.thumbnail_generator.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/raw/"
    filter_suffix       = ".png"
  }
}
```

### S3 Select

Consulta SQL diretamente em objetos CSV, JSON ou Parquet sem baixar o arquivo inteiro:

```python
response = s3.select_object_content(
    Bucket=bucket,
    Key="data/events-2026-04.csv",
    ExpressionType="SQL",
    Expression="SELECT s.user_id, s.event_type FROM S3Object s WHERE s.event_type = 'purchase'",
    InputSerialization={"CSV": {"FileHeaderInfo": "Use"}, "CompressionType": "GZIP"},
    OutputSerialization={"JSON": {"RecordDelimiter": "\n"}},
)
for event in response["Payload"]:
    if "Records" in event:
        print(event["Records"]["Payload"].decode())
```

## Patterns

### Bucket Policy vs IAM

**Bucket Policy:** controla acesso ao bucket independente de IAM, pode permitir acesso cross-account e de serviços AWS. Avaliado junto com IAM — o acesso é concedido se QUALQUER política permite e NENHUMA nega explicitamente.

```json
{
  "Effect": "Allow",
  "Principal": { "Service": "cloudfront.amazonaws.com" },
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::my-cdn-bucket/*",
  "Condition": {
    "StringEquals": {
      "AWS:SourceArn": "arn:aws:cloudfront::123456789:distribution/ABCDEF123"
    }
  }
}
```

Use Origin Access Control (OAC) ao integrar com CloudFront para servir o [[media-pipeline]] — bloqueia acesso direto ao S3.

### Multipart Upload para Arquivos Grandes

```python
import boto3
from boto3.s3.transfer import TransferConfig

config = TransferConfig(
    multipart_threshold=1024 * 25,    # 25 MB
    max_concurrency=10,
    multipart_chunksize=1024 * 25,
    use_threads=True,
)

s3.upload_file(
    local_path,
    bucket,
    s3_key,
    Config=config,
    ExtraArgs={"ServerSideEncryption": "aws:kms"},
)
```

## Gotchas

> [!danger] ListObjects tem custo e pode ser lento em buckets com milhões de objetos
> Prefira S3 Inventory (relatório CSV/Parquet agendado) para análises em escala. `list_objects_v2` com prefix pagina em 1000 objetos por request.

> [!warning] Delete Markers não liberam storage em versioned buckets
> Com versioning ativo, "deletar" cria um delete marker. As versões antigas permanecem e acumulam custo. Configure lifecycle para expirar noncurrent versions.

> [!tip] Intelligent Tiering tem custo de monitoramento por objeto
> $0.0025 por 1000 objetos/mês para monitoramento. Para objetos pequenos e abundantes (<128KB), o custo de monitoramento supera a economia de tiering.

## References

- [S3 User Guide — Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [S3 Lifecycle Configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [S3 Replication](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html)
- [S3 Select](https://docs.aws.amazon.com/AmazonS3/latest/userguide/selecting-content-from-objects.html)

## Related

- [[cloudinary]] — CDN e transformações sobre ativos armazenados no S3
- [[media-pipeline]] — S3 como origem do pipeline de mídia
- [[terraform]] — provisionamento de buckets, policies e replication
- [[data-lake-patterns]] — S3 como camada de storage do data lake
- [[secrets-management]] — gerenciamento de credenciais AWS para acesso ao S3
