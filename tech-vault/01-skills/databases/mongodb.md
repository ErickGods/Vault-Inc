---
tags: [skill, databases, mongodb]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [MongoDB, Mongo]
---

# MongoDB

## Overview

MongoDB é um banco de dados orientado a documentos que armazena dados como BSON (Binary JSON). Sua flexibilidade de schema e modelo de dados hierárquico o tornam eficaz para domínios com estruturas variáveis, dados aninhados naturalmente, e cargas de trabalho onde a latência de leitura de um único documento precisa ser mínima (sem joins).

Para casos de uso com dados muito relacionais e transações complexas, [[postgresql]] é superior. MongoDB brilha em catálogos de produtos, logs de eventos, perfis de usuário, e sistemas onde o schema evolui frequentemente. Combina bem com [[redis]] para cache e complementa [[fastapi]] no backend. Otimização avançada em [[database-optimization]]. Containerização via [[docker]].

---

## Core Concepts

### Aggregation Pipeline

O pipeline de agregação é a ferramenta mais poderosa do MongoDB — cada stage transforma os documentos e passa o resultado para o próximo stage.

```javascript
// E-commerce: revenue by category with top products
db.orders.aggregate([
  // Stage 1: filter (uses index)
  {
    $match: {
      status: "completed",
      created_at: { $gte: ISODate("2026-01-01"), $lt: ISODate("2026-04-01") }
    }
  },

  // Stage 2: unwind array into separate documents
  { $unwind: "$items" },

  // Stage 3: lookup (LEFT JOIN) — populate category from another collection
  {
    $lookup: {
      from: "products",
      localField: "items.product_id",
      foreignField: "_id",
      as: "product_info",
      // Pipeline lookup for filtered join (MongoDB 3.6+)
      pipeline: [
        { $project: { name: 1, category: 1, _id: 0 } }
      ]
    }
  },
  { $unwind: "$product_info" },

  // Stage 4: group and compute metrics
  {
    $group: {
      _id: "$product_info.category",
      total_revenue: { $sum: { $multiply: ["$items.quantity", "$items.unit_price"] } },
      order_count: { $addToSet: "$_id" },  // unique orders
      top_product: { $top: { output: "$product_info.name", sortBy: { "items.unit_price": -1 } } }
    }
  },

  // Stage 5: add computed fields
  {
    $addFields: {
      unique_orders: { $size: "$order_count" },
      avg_order_value: { $divide: ["$total_revenue", { $size: "$order_count" }] }
    }
  },

  // Stage 6: sort and limit
  { $sort: { total_revenue: -1 } },
  { $limit: 10 },

  // Stage 7: reshape output
  {
    $project: {
      category: "$_id",
      total_revenue: { $round: ["$total_revenue", 2] },
      unique_orders: 1,
      avg_order_value: { $round: ["$avg_order_value", 2] },
      top_product: 1,
      _id: 0
    }
  }
])
```

**$facet** — multiple pipelines in parallel for faceted search:

```javascript
db.products.aggregate([
  { $match: { $text: { $search: "wireless headphones" } } },
  {
    $facet: {
      results: [
        { $sort: { score: { $meta: "textScore" } } },
        { $skip: 0 }, { $limit: 20 }
      ],
      price_ranges: [
        { $bucket: { groupBy: "$price", boundaries: [0, 50, 100, 200, 500], default: "500+" } }
      ],
      brand_counts: [
        { $group: { _id: "$brand", count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ],
      total: [{ $count: "count" }]
    }
  }
])
```

### Indexes

```javascript
// Compound index — field order matters (ESR rule: Equality, Sort, Range)
db.orders.createIndex(
  { customer_id: 1, status: 1, created_at: -1 },
  { name: "idx_orders_customer_status_date" }
)
// Query: { customer_id: "x", status: "completed" } ORDER BY created_at DESC ✓

// Partial index — only index documents matching the filter
db.jobs.createIndex(
  { scheduled_at: 1, priority: -1 },
  {
    partialFilterExpression: { status: "pending" },
    name: "idx_pending_jobs"
  }
)

// TTL index — automatic document expiry
db.sessions.createIndex(
  { expires_at: 1 },
  { expireAfterSeconds: 0 }  // Delete when expires_at is in the past
)

// Text index for full-text search
db.articles.createIndex(
  { title: "text", body: "text", tags: "text" },
  { weights: { title: 10, tags: 5, body: 1 }, default_language: "portuguese" }
)
db.articles.find({ $text: { $search: "\"postgresql\" performance -mysql" } },
  { score: { $meta: "textScore" } })
  .sort({ score: { $meta: "textScore" } })

// 2dsphere index for geospatial
db.stores.createIndex({ location: "2dsphere" })
db.stores.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-46.6333, -23.5505] },  // São Paulo
      $maxDistance: 5000  // 5km in meters
    }
  }
})

// Wildcard index — for dynamic/unpredictable field access patterns
db.user_attributes.createIndex({ "attributes.$**": 1 })

// Covered query check — explain() should show "stage": "IXSCAN" with no FETCH
db.orders.find(
  { customer_id: "abc" },
  { _id: 0, status: 1, created_at: 1 }
).explain("executionStats")
```

### Replica Sets

```javascript
// Replica set config
rs.initiate({
  _id: "myReplicaSet",
  members: [
    { _id: 0, host: "mongo1:27017", priority: 2 },    // preferred primary
    { _id: 1, host: "mongo2:27017", priority: 1 },
    { _id: 2, host: "mongo3:27017", priority: 0, hidden: true, votes: 0 }  // analytics replica
  ]
})

// Read from secondary (analytics queries)
db.getMongo().setReadPref("secondaryPreferred")

// Write concern: majority ensures durability before acknowledging
db.orders.insertOne(document, { writeConcern: { w: "majority", j: true } })
```

### Sharding — Shard Key Design

```javascript
// Enable sharding on database
sh.enableSharding("myapp")

// Shard key selection is CRITICAL — hard to change after
// Bad: monotonic key (ObjectId, timestamp) → all writes go to one chunk (hotspot)
// Good: compound key with good cardinality

sh.shardCollection("myapp.events", {
  tenant_id: 1,    // equality filter first (good cardinality, good for routing)
  created_at: 1    // range component
})

// Zone sharding: route tenant data to specific shards (data sovereignty)
sh.addShardToZone("shard001", "EU")
sh.updateZoneKeyRange("myapp.events",
  { tenant_id: "eu_tenant_a", created_at: MinKey },
  { tenant_id: "eu_tenant_z", created_at: MaxKey },
  "EU"
)
```

### Multi-Document Transactions

```javascript
// ACID transactions (replica set or sharded cluster required)
const session = client.startSession()
session.startTransaction({
  readConcern: { level: "snapshot" },    // snapshot isolation
  writeConcern: { w: "majority" }
})

try {
  const orders = session.client.db("myapp").collection("orders")
  const inventory = session.client.db("myapp").collection("inventory")

  await orders.insertOne({
    customer_id: userId,
    items: cartItems,
    status: "confirmed",
    total: cartTotal
  }, { session })

  for (const item of cartItems) {
    const result = await inventory.updateOne(
      { product_id: item.id, stock: { $gte: item.quantity } },
      { $inc: { stock: -item.quantity } },
      { session }
    )
    if (result.matchedCount === 0) throw new Error(`Insufficient stock: ${item.id}`)
  }

  await session.commitTransaction()
} catch (err) {
  await session.abortTransaction()
  throw err
} finally {
  session.endSession()
}
```

### Change Streams

```javascript
// Real-time CDC — requires replica set or sharded cluster
const pipeline = [
  { $match: { "operationType": { $in: ["insert", "update"] } } },
  { $match: { "fullDocument.status": "pending" } }
]

const changeStream = db.collection("orders").watch(pipeline, {
  fullDocument: "updateLookup",   // include full document on updates
  resumeAfter: lastResumeToken    // resume after failure
})

changeStream.on("change", async (change) => {
  lastResumeToken = change._id    // persist for fault tolerance
  if (change.operationType === "insert") {
    await processNewOrder(change.fullDocument)
  }
})

changeStream.on("error", (err) => {
  if (err.code === 136) { /* ChangeStreamHistoryLost — resume token expired */ }
})
```

### Atlas Search (Full-Text)

```javascript
// Atlas Search aggregation stage — Lucene under the hood
db.products.aggregate([
  {
    $search: {
      index: "products_search",
      compound: {
        must: [{
          text: {
            query: "wireless bluetooth",
            path: ["name", "description"],
            fuzzy: { maxEdits: 1 }
          }
        }],
        filter: [{
          range: { path: "price", gte: 50, lte: 300 }
        }],
        should: [{
          text: { query: "noise canceling", path: "features", score: { boost: { value: 2 } } }
        }]
      },
      highlight: { path: "description" }
    }
  },
  {
    $project: {
      name: 1, price: 1,
      score: { $meta: "searchScore" },
      highlights: { $meta: "searchHighlights" }
    }
  }
])
```

---

## Gotchas

> [!danger] Shard Key é Imutável no Campo
> Uma vez que um campo é escolhido como shard key, não pode ser alterado por documento após inserção (MongoDB 5.0+ permite mudanças limitadas via resharding, mas é operação custosa). Planeje o shard key antes de inserir dados.

> [!warning] $lookup em Sharded Collections
> `$lookup` entre coleções shardadas pode ser extremamente lento se as coleções não estiverem co-localizadas. Prefira embedding ou desnormalização quando performance de join é crítica.

> [!warning] Índices em Background e Write Performance
> Criar índices em produção com `{ background: true }` (legado) ou o comportamento padrão no MongoDB 4.2+ ainda impacta write throughput. Use janelas de manutenção ou crie índices em réplicas primeiro.

> [!tip] explain() é seu Melhor Amigo
> `db.collection.find({...}).explain("executionStats")` revela se a query usa COLLSCAN (full scan) vs IXSCAN (index). `totalDocsExamined` >> `nReturned` indica índice inadequado.

> [!danger] BSON Document Size Limit
> Documentos BSON têm limite de 16 MB. Para arrays que crescem indefinidamente (logs, eventos), use coleções separadas com referências ou Change Streams, não arrays embarcados.

---

## References

- [MongoDB Aggregation Pipeline](https://www.mongodb.com/docs/manual/aggregation/)
- [Index Strategies](https://www.mongodb.com/docs/manual/applications/indexes/)
- [Sharding](https://www.mongodb.com/docs/manual/sharding/)
- [Atlas Search](https://www.mongodb.com/docs/atlas/atlas-search/)

## Related

- [[postgresql]]
- [[database-optimization]]
- [[docker]]
- [[fastapi]]
- [[redis]]
