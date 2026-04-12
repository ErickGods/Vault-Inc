---
tags: [skill, architecture, nats]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [NATS]
---

# NATS

## Overview

NATS é um sistema de mensageria cloud-native escrito em Go, projetado para performance extrema (milhões de msgs/s com latência sub-milissegundo) e operação simples. Core NATS é fire-and-forget pub/sub; JetStream adiciona persistência, replay e exactly-once delivery. Ao contrário de [[rabbitmq]] (AMQP, broker rico) e [[sqs-sns]] (managed, AWS-locked), NATS é minimalista, vendor-neutral e roda excelente em [[kubernetes-basics]]. Base para implementar [[messaging-patterns]] de alta performance em arquiteturas [[event-driven]].

> [!info] Core NATS vs JetStream
> Core NATS: in-memory, sem persistência, sem ACK — se não há subscriber, mensagem é perdida. JetStream: persiste em disco, replay, ACK policies, at-least-once e exactly-once.

## Core Concepts

### Core NATS — Pub/Sub e Request-Reply

```go
// Go client — nats.go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/nats-io/nats.go"
)

func main() {
    nc, err := nats.Connect(
        "nats://localhost:4222",
        nats.Name("my-service"),
        nats.MaxReconnects(10),
        nats.ReconnectWait(2*time.Second),
        nats.ErrorHandler(func(nc *nats.Conn, sub *nats.Subscription, err error) {
            fmt.Printf("NATS error: %v\n", err)
        }),
    )
    if err != nil { panic(err) }
    defer nc.Drain()  // Drain espera mensagens pendentes antes de fechar

    // Publish simples
    nc.Publish("orders.created", []byte(`{"order_id":42}`))

    // Subscribe com wildcard
    // "orders.*"  → orders.created, orders.cancelled (1 token)
    // "orders.>"  → orders.created, orders.us.west.created (1 ou mais tokens)
    nc.Subscribe("orders.*", func(msg *nats.Msg) {
        fmt.Printf("Received on %s: %s\n", msg.Subject, string(msg.Data))
    })

    // Request-Reply síncrono (timeout)
    response, err := nc.Request("pricing.calculate",
        []byte(`{"product_id":1,"qty":10}`),
        2*time.Second,
    )
    if err != nil { fmt.Println("Timeout or no responder") }
    fmt.Println(string(response.Data))

    // Responder (servidor do request-reply)
    nc.Subscribe("pricing.calculate", func(msg *nats.Msg) {
        // msg.Reply é o subject de reply temporário
        price := calculatePrice(msg.Data)
        msg.Respond(price)
    })
}
```

### Queue Groups (Competing Consumers)

```go
// Múltiplos subscribers no mesmo queue group = load balancing automático
// Apenas UM membro do grupo recebe cada mensagem
for i := 0; i < 3; i++ {
    workerID := i
    nc.QueueSubscribe("jobs.process", "workers", func(msg *nats.Msg) {
        fmt.Printf("Worker %d processing: %s\n", workerID, msg.Data)
        processJob(msg.Data)
    })
}
```

### JetStream — Streams e Consumers

```go
js, err := nc.JetStream()

// Criar Stream (persistência em disco, retenção configurável)
js.AddStream(&nats.StreamConfig{
    Name:       "ORDERS",
    Subjects:   []string{"orders.>"},    // captura todos os subjects orders.*
    MaxAge:     7 * 24 * time.Hour,      // retenção de 7 dias
    MaxBytes:   10 * 1024 * 1024 * 1024, // 10 GB
    Storage:    nats.FileStorage,        // FileStorage ou MemoryStorage
    Replicas:   3,                       // replicação em cluster de 3 nodes
    Retention:  nats.LimitsPolicy,       // LimitsPolicy, InterestPolicy, WorkQueuePolicy
    Discard:    nats.DiscardOld,         // descarta mensagens antigas quando atinge limite
    MaxMsgSize: 1024 * 1024,            // 1 MB max por mensagem
})

// Consumer Push (broker entrega para subscriber)
sub, _ := js.Subscribe("orders.>", func(msg *nats.Msg) {
    msg.Ack()   // AckExplicit (padrão com JetStream)
    // msg.Nak()         — reentrega imediata
    // msg.NakWithDelay(5*time.Second) — reentrega com delay
    // msg.Term()        — descarta permanentemente (vai para DLQ se configurado)
    // msg.InProgress()  — heartbeat, estende prazo de ACK
},
    nats.Durable("order-processor"),      // consumer durável (sobrevive restart)
    nats.DeliverAll(),                    // replay desde o início do stream
    nats.AckExplicit(),                   // requer ACK manual
    nats.MaxDeliver(3),                   // max redeliveries
    nats.AckWait(30*time.Second),         // prazo para ACK
    nats.MaxAckPending(100),              // max mensagens sem ACK simultâneas
)

// Consumer Pull (consumer faz fetch — melhor para controle de backpressure)
sub2, _ := js.PullSubscribe("orders.>",
    "order-puller",
    nats.BindStream("ORDERS"),
)

msgs, err := sub2.Fetch(10, nats.MaxWait(5*time.Second))
for _, msg := range msgs {
    process(msg.Data)
    msg.Ack()
}
```

### ACK Policies

| Policy | Descrição | Use case |
|--------|-----------|----------|
| `AckExplicit` | ACK manual por mensagem | Produção — controle total |
| `AckAll` | ACK até e incluindo a mensagem | Processamento serial |
| `AckNone` | Sem ACK requerido | Logs, métricas, fire-and-forget |

### Key-Value Store

```go
// NATS KV — construído sobre JetStream Streams
kv, _ := js.CreateKeyValue(&nats.KeyValueConfig{
    Bucket:  "config",
    History: 5,                    // mantém 5 revisões por chave
    TTL:     24 * time.Hour,       // expiração por entrada
    Storage: nats.FileStorage,
})

kv.Put("feature.darkmode", []byte("true"))
kv.Put("rate.limit", []byte("1000"))

entry, _ := kv.Get("feature.darkmode")
fmt.Printf("Revision %d: %s\n", entry.Revision(), string(entry.Value()))

// Watch — recebe updates em tempo real (stream de mudanças)
watcher, _ := kv.WatchAll()
defer watcher.Stop()
for update := range watcher.Updates() {
    if update == nil { break }  // nil = snapshot completo entregue
    fmt.Printf("Key %s changed: %s (op: %v)\n",
        update.Key(), update.Value(), update.Operation())
}
```

### Subjects e Wildcards

```
# Hierarquia recomendada: <domínio>.<entidade>.<ação>.<versão>
orders.payment.processed.v1
orders.fulfillment.shipped.v1
orders.return.initiated.v1

# Wildcards
orders.*              # → orders.payment, orders.fulfillment (1 token)
orders.>              # → tudo dentro de orders (qualquer profundidade)
*.payment.*           # → orders.payment.processed, billing.payment.failed
```

## Patterns

### Security — TLS + NKey + JWT

```bash
# Gerar NKey para user
nsc add operator MyOrg
nsc add account Production
nsc add user service-worker --account Production
nsc generate creds --account Production --name service-worker > service-worker.creds
```

```go
// Autenticação com credentials file (NKey + JWT)
nc, _ := nats.Connect("nats://nats.internal:4222",
    nats.UserCredentials("/etc/nats/service-worker.creds"),
    nats.RootCAs("/etc/ssl/certs/nats-ca.pem"),
    nats.ClientCert("/etc/ssl/certs/client.pem", "/etc/ssl/private/client-key.pem"),
)
```

### Leaf Nodes e Super-Clusters

```
Internet ←→ [Hub Cluster NYC + LON + TKY]  ← super-cluster
                        ↕ Leaf connections
            [Leaf Node: AWS us-east-1]
            [Leaf Node: GCP europe-west1]
            [Leaf Node: On-premises DC]
```

Leaf nodes conectam ao hub com TLS, expõem subjects locais seletivamente — reduz latência para publishers/subscribers próximos ao leaf, replica para o hub conforme necessário.

### NATS CLI para Debug

```bash
# Instalar
brew install nats-io/nats-tools/nats

nats stream ls                          # listar streams
nats stream info ORDERS                 # detalhes do stream
nats consumer ls ORDERS                 # listar consumers
nats consumer info ORDERS order-processor

nats pub orders.created '{"id":1}'     # publicar mensagem
nats sub "orders.>"                    # subscribe e imprimir

nats bench orders.created --msgs=100000 --size=512   # benchmark
# Saída típica em localhost: ~4M msgs/s single publisher
```

## Gotchas

> [!danger] Core NATS descarta mensagens sem subscribers — não é durável por padrão
> Se nenhum subscriber está ativo quando uma mensagem é publicada em Core NATS (sem JetStream), ela é perdida permanentemente. Use JetStream para qualquer workload que necessite durabilidade.

> [!warning] JetStream consumer durable sem ACK acumula pending delivery
> Se um consumer durable não processa (ou ACK) mensagens, elas acumulam como "pending". Isso bloqueia o progresso do consumer e pode consumir memória do cluster. Monitore `nats consumer info` e configure `MaxAckPending`.

> [!warning] Cluster JetStream requer número ímpar de nodes para quorum Raft
> 1 node = sem HA, 3 nodes = tolera 1 falha, 5 nodes = tolera 2 falhas. Nunca use 2 ou 4 nodes em produção — split-brain sem resolução.

> [!tip] NATS tem latência de ~200 microsegundos — muito abaixo de RabbitMQ e SQS
> Para sistemas de telemetria, jogos em tempo real e controle de IoT onde microssegundos importam, NATS é a escolha. Para workloads batch e baixa frequência, [[sqs-sns]] ou [[rabbitmq]] são mais simples.

## Snippets

```yaml
# NATS Server config (nats.conf)
port: 4222
http_port: 8222    # monitoring

jetstream {
  store_dir: /data/nats
  max_memory_store: 4GB
  max_file_store: 100GB
}

cluster {
  name: production
  port: 6222
  routes: [
    nats://nats-1:6222
    nats://nats-2:6222
    nats://nats-3:6222
  ]
}
```

## References

- [NATS Documentation](https://docs.nats.io/)
- [JetStream Concepts](https://docs.nats.io/nats-concepts/jetstream)
- [NATS Security — NKey + JWT](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro)
- [NATS Benchmarks](https://nats.io/blog/nats-benchmarking/)

## Related

- [[messaging-patterns]] — padrões implementados com NATS JetStream
- [[rabbitmq]] — alternativa com AMQP e roteamento rico
- [[sqs-sns]] — alternativa managed AWS
- [[kubernetes-basics]] — deploy de NATS cluster via Helm
- [[event-driven]] — arquiteturas event-driven de alta performance com NATS
