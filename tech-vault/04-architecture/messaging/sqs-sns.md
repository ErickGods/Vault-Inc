---
tags: [skill, architecture, sqs-sns]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [SQS, SNS, AWS Messaging]
---

# SQS + SNS

## Overview

SQS (Simple Queue Service) e SNS (Simple Notification Service) são os serviços de mensageria managed da AWS. SQS é pull-based (consumers fazem polling), SNS é push-based (broker entrega para subscribers). Juntos formam o padrão fanout-to-queues, base de [[messaging-patterns]] serverless na AWS. Comparado a [[rabbitmq]] (broker rico com AMQP) e [[nats]] (ultra-performance), SQS/SNS priorizam simplicidade operacional e integração nativa com o ecossistema AWS. Provisionados via [[terraform]] e integrados com [[event-driven]] architectures.

> [!info] SQS vs SNS em uma linha
> SNS distribui uma mensagem para múltiplos destinos (fan-out). SQS armazena mensagens para serem consumidas por workers. Use SNS → SQS para fan-out com durabilidade.

## Core Concepts

### SQS Standard vs FIFO

| Característica | Standard | FIFO |
|---------------|----------|------|
| Throughput | Ilimitado (~unlimited TPS) | 300 TPS (3000 com batching) |
| Ordenação | Best-effort | Estrita por MessageGroupId |
| Deduplicação | Possível duplicatas (at-least-once) | Exata (exactly-once dentro de 5 min) |
| Latência | Menor | Ligeiramente maior |
| Caso de uso | Processamento paralelo, jobs, pipelines | Pedidos, transações financeiras, eventos sequenciais |

```python
import boto3
import json
import hashlib

sqs = boto3.client("sqs", region_name="us-east-1")

# Enviar para Standard Queue
sqs.send_message(
    QueueUrl=STANDARD_QUEUE_URL,
    MessageBody=json.dumps({"event": "user.signup", "user_id": 42}),
    MessageAttributes={
        "EventType": {"DataType": "String", "StringValue": "user.signup"},
        "Version":   {"DataType": "Number", "StringValue": "1"},
    },
    DelaySeconds=0,    # 0-900s delay por mensagem
)

# Enviar para FIFO Queue
event_body = json.dumps({"order_id": 100, "status": "created"})
sqs.send_message(
    QueueUrl=FIFO_QUEUE_URL,       # URL deve terminar em .fifo
    MessageBody=event_body,
    MessageGroupId="order-100",    # Mensagens do mesmo grupo são ordenadas e sequenciais
    MessageDeduplicationId=hashlib.sha256(event_body.encode()).hexdigest(),
    # Alternativa: habilitar ContentBasedDeduplication no queue level
)
```

### Visibility Timeout

Após um consumer receber uma mensagem, ela fica invisível por `VisibilityTimeout` segundos. Se não for deletada, retorna à fila (retry automático).

```python
# Long polling — espera até 20s por mensagens (reduz requisições vazias e custo)
messages = sqs.receive_message(
    QueueUrl=QUEUE_URL,
    MaxNumberOfMessages=10,           # até 10 por batch
    WaitTimeSeconds=20,               # long polling (short polling = 0)
    VisibilityTimeout=300,            # override por receive (5 min)
    MessageAttributeNames=["All"],
    AttributeNames=["All"],           # inclui ApproximateReceiveCount, SentTimestamp
)

for msg in messages.get("Messages", []):
    receive_count = int(msg["Attributes"].get("ApproximateReceiveCount", 1))

    # Extender visibilidade se processamento demorado
    if receive_count > 3:
        sqs.change_message_visibility(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=msg["ReceiptHandle"],
            VisibilityTimeout=600,    # mais 10 min
        )

    try:
        process(json.loads(msg["Body"]))
        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"])
    except Exception:
        pass  # Não deleta → retorna após VisibilityTimeout → vai para DLQ após maxReceiveCount
```

### Dead Letter Queue (DLQ) e Redrive Policy

```python
# Criar DLQ
dlq = sqs.create_queue(
    QueueName="orders-dlq",
    Attributes={"MessageRetentionPeriod": str(14 * 24 * 3600)},  # 14 dias
)
dlq_arn = sqs.get_queue_attributes(
    QueueUrl=dlq["QueueUrl"], AttributeNames=["QueueArn"]
)["Attributes"]["QueueArn"]

# Criar main queue com redrive para DLQ
main_queue = sqs.create_queue(
    QueueName="orders-processing",
    Attributes={
        "RedrivePolicy": json.dumps({
            "deadLetterTargetArn": dlq_arn,
            "maxReceiveCount": "3",   # após 3 falhas, vai para DLQ
        }),
        "VisibilityTimeout": "300",
        "ReceiveMessageWaitTimeSeconds": "20",
    },
)

# Redrive manual: mover mensagens da DLQ de volta para main queue (AWS Console ou API)
sqs.start_message_move_task(
    SourceArn=dlq_arn,
    DestinationArn=main_queue_arn,
    MaxNumberOfMessagesPerSecond=10,
)
```

### Batch Operations

```python
# Envio em batch (até 10 mensagens por request, até 256 KB total)
entries = [
    {
        "Id": str(i),
        "MessageBody": json.dumps({"item_id": i}),
        "MessageAttributes": {
            "Priority": {"DataType": "Number", "StringValue": str(i % 3)},
        },
    }
    for i in range(10)
]
response = sqs.send_message_batch(QueueUrl=QUEUE_URL, Entries=entries)
failed = response.get("Failed", [])

# Delete em batch após processamento bem-sucedido
delete_entries = [
    {"Id": msg["MessageId"], "ReceiptHandle": msg["ReceiptHandle"]}
    for msg in processed_messages
]
sqs.delete_message_batch(QueueUrl=QUEUE_URL, Entries=delete_entries)
```

### SNS Topics e Subscriptions

```python
sns = boto3.client("sns", region_name="us-east-1")

# Criar topic (Standard ou FIFO)
topic = sns.create_topic(
    Name="order-events",
    Attributes={"DisplayName": "Order Events"},
    Tags=[{"Key": "env", "Value": "production"}],
)
topic_arn = topic["TopicArn"]

# Subscrever SQS queue ao topic (fanout)
sns.subscribe(
    TopicArn=topic_arn,
    Protocol="sqs",
    Endpoint=main_queue_arn,
    Attributes={
        "FilterPolicy": json.dumps({
            "EventType": ["order.created", "order.cancelled"],  # content-based filtering
            "Priority": [{"numeric": [">=", 2]}],
        }),
        "FilterPolicyScope": "MessageAttributes",  # ou MessageBody
        "RawMessageDelivery": "true",   # entrega corpo direto sem wrapper SNS
    },
)

# Publicar evento
sns.publish(
    TopicArn=topic_arn,
    Message=json.dumps({"order_id": 42, "total": 199.99}),
    MessageAttributes={
        "EventType": {"DataType": "String", "StringValue": "order.created"},
        "Priority":  {"DataType": "Number", "StringValue": "3"},
    },
    Subject="Order Created",
)
```

### Filtering Policies Avançadas

```json
{
  "EventType":    ["order.created", "order.cancelled"],
  "Region":       [{"prefix": "us-"}],
  "Amount":       [{"numeric": [">=", 100, "<", 10000]}],
  "IsTest":       [{"exists": false}],
  "CustomerTier": ["premium", "enterprise"]
}
```

> [!info] Filter Policy Scope
> `MessageAttributes` (padrão) filtra pelos atributos da mensagem. `MessageBody` filtra pelo corpo JSON — mais flexível mas requer que o corpo seja JSON válido com os atributos no nível raiz.

## Patterns

### SNS → SQS Fan-out

```hcl
# terraform: SNS fan-out para múltiplas SQS queues
resource "aws_sns_topic" "order_events" { name = "order-events" }

resource "aws_sqs_queue" "order_processing" { name = "order-processing" }
resource "aws_sqs_queue" "order_analytics"  { name = "order-analytics" }
resource "aws_sqs_queue" "order_email"      { name = "order-email" }

resource "aws_sns_topic_subscription" "processing" {
  topic_arn     = aws_sns_topic.order_events.arn
  protocol      = "sqs"
  endpoint      = aws_sqs_queue.order_processing.arn
  filter_policy = jsonencode({ EventType = ["order.created"] })
}

# SQS queue policy: permite SNS publicar
resource "aws_sqs_queue_policy" "allow_sns" {
  queue_url = aws_sqs_queue.order_processing.id
  policy = jsonencode({
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "sns.amazonaws.com" }
      Action    = "sqs:SendMessage"
      Resource  = aws_sqs_queue.order_processing.arn
      Condition = { ArnEquals = { "aws:SourceArn" = aws_sns_topic.order_events.arn } }
    }]
  })
}
```

### Lambda Trigger com Error Handling

```python
# Lambda function com SQS trigger — processa em batch
import json
from typing import Any

def handler(event: dict, context: Any) -> dict:
    batch_item_failures = []

    for record in event["Records"]:
        message_id = record["messageId"]
        try:
            body = json.loads(record["body"])
            # SNS wrapping: corpo real está em body["Message"] se RawMessageDelivery=false
            if "Message" in body and "TopicArn" in body:
                payload = json.loads(body["Message"])
            else:
                payload = body
            process_order(payload)
        except Exception as e:
            # Report failure — Lambda re-processa apenas esses itens
            batch_item_failures.append({"itemIdentifier": message_id})
            logger.error(f"Failed {message_id}: {e}")

    # Partial batch response — requer ReportBatchItemFailures no event source mapping
    return {"batchItemFailures": batch_item_failures}
```

## Gotchas

> [!danger] SQS não garante ordering em Standard Queues — projete para idempotência
> Mensagens podem chegar fora de ordem e duplicadas. Use FIFO se ordering for crítico e implemente idempotency keys em todos os consumers Standard.

> [!warning] SNS entrega "at-least-once" — subscribers podem receber duplicatas
> Implemente deduplicação no consumer usando o `MessageId` do SNS como chave de idempotência em uma tabela DynamoDB ou Redis com TTL.

> [!warning] Visibility Timeout deve ser maior que o tempo máximo de processamento
> Se o processamento levar mais que o timeout, a mensagem retorna à fila e outro consumer pode processá-la simultaneamente. Use `change_message_visibility` para heartbeat em jobs longos.

> [!tip] Custo: long polling reduz custo em ~99%
> Short polling (WaitTimeSeconds=0) faz uma request por segundo por consumer. Long polling (20s) custa 1/20 das requests. Configure sempre `WaitTimeSeconds=20` na fila e no receive call.

## Snippets

```python
# Encryption at rest com KMS
sqs.create_queue(
    QueueName="secure-queue",
    Attributes={
        "KmsMasterKeyId": "alias/aws/sqs",  # ou custom KMS key ARN
        "KmsDataKeyReusePeriodSeconds": "300",
    },
)
```

## References

- [SQS Developer Guide](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/)
- [SNS Developer Guide](https://docs.aws.amazon.com/sns/latest/dg/)
- [SQS FIFO Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues.html)
- [Lambda SQS Event Source Mapping](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)

## Related

- [[messaging-patterns]] — padrões de mensageria implementados com SQS/SNS
- [[rabbitmq]] — alternativa self-hosted com AMQP
- [[nats]] — alternativa de ultra-baixa latência
- [[terraform]] — provisionamento de filas, topics e políticas
- [[event-driven]] — arquitetura orientada a eventos com SQS/SNS
