---
tags: [skill, databases, planetscale]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [PlanetScale]
---

# PlanetScale

## Overview

PlanetScale é um banco de dados MySQL compatível construído sobre o Vitess — o mesmo sistema que o YouTube usa para escalar MySQL horizontalmente. O diferencial não é apenas escala: é o workflow de desenvolvimento com branching de banco de dados, deploy requests com análise de impacto e migrações sem bloqueio de tabelas.

Para projetos que precisam de MySQL com garantias de escala horizontal e um workflow de CI/CD para schema changes, PlanetScale oferece uma proposta sólida. Comparado ao [[supabase]] (baseado em [[postgresql]]), o foco é diferente: PlanetScale prioriza sharding transparente e zero-downtime migrations. Estratégias de deploy em [[deployment-strategies]]. Ver [[database-optimization]] para tuning. Containerizar localmente com [[docker]].

---

## Core Concepts

### Vitess Under the Hood

Vitess adiciona uma camada de sharding horizontal sobre MySQL, com um VTGate como proxy inteligente que roteia queries para os shards corretos.

```
Client → VTGate (query routing) → VTTablet (MySQL proxy) → MySQL

VTGate responsabilities:
- Parse queries and rewrite them for sharding
- Scatter-gather for cross-shard queries
- Connection pooling (multiplexing thousands of app connections)
- Schema tracking across all shards
```

**Limitações do Vitess que afetam o PlanetScale:**

```sql
-- PROIBIDO: Foreign keys (Vitess não suporta FK cross-shard)
-- PlanetScale enforces this: FK constraints são bloqueadas por padrão
-- Referential integrity deve ser tratada na aplicação

-- PROIBIDO: Queries sem índice em tabelas grandes (full scatter)
-- SELECT * FROM users WHERE LOWER(email) = 'test@example.com'
-- ^ Sem índice, faz scatter para todos os shards

-- PERMITIDO com limitações: JOINs
-- JOINs que ficam no mesmo shard são eficientes
-- JOINs cross-shard são reescritos como nested loop (pode ser lento)
```

### Database Branching Workflow

O branching do PlanetScale funciona como Git para schemas — cada branch tem sua própria cópia do schema e pode receber migrations independentemente.

```bash
# Install PlanetScale CLI
brew install planetscale/tap/pscale

# Authenticate
pscale auth login

# List databases
pscale database list

# Create a feature branch from main
pscale branch create my-database add-user-preferences --from main

# Connect to branch for local development (creates a local proxy)
pscale connect my-database add-user-preferences --port 3309
# Now connect your app to mysql://root@127.0.0.1:3309/my-database

# Run migrations against the branch
mysql -h 127.0.0.1 -P 3309 -u root my-database < migration.sql

# Compare schema diff between branches
pscale branch diff my-database add-user-preferences

# Create deploy request (like a PR for schema changes)
pscale deploy-request create my-database add-user-preferences

# List deploy requests
pscale deploy-request list my-database

# Deploy (merges schema changes to main)
pscale deploy-request deploy my-database 1
```

### Deploy Requests — Safe Migrations

Deploy Requests são a implementação do non-blocking schema changes do PlanetScale, usando a técnica "expand-contract" (ghost/pt-online-schema-change internamente via VReplication).

```
Flow for adding a column:
1. Create branch → apply migration → create deploy request
2. PlanetScale analyzes: is this a breaking change?
   - ADD COLUMN (nullable or with default) → safe ✓
   - DROP COLUMN → breaking (data loss) — requires "revert" window
   - ADD UNIQUE INDEX → may fail if duplicates exist → analyzed before deploy
3. Deploy executes without locking the table:
   - Creates shadow table with new schema
   - Copies data in chunks (VReplication)
   - Applies writes to both tables during copy
   - Atomic cutover at the end
4. Revert window (30 minutes): can roll back by keeping old column
```

```bash
# Check deploy request status and impact analysis
pscale deploy-request show my-database 1

# Output example:
# Schema changes:
# + ALTER TABLE users ADD COLUMN preferences JSON
# Impact: Non-breaking addition. Estimated time: ~4 minutes for 2.1M rows.
# Warnings: None
```

### Connection Strings — Serverless Driver

O driver serverless `@planetscale/database` usa HTTP/2 em vez de TCP, permitindo conexões de ambientes sem TCP persistente (Cloudflare Workers, Vercel Edge, Deno Deploy).

```typescript
// @planetscale/database — HTTP driver (serverless/edge compatible)
import { connect } from '@planetscale/database'

const conn = connect({
  host: process.env.DATABASE_HOST,
  username: process.env.DATABASE_USERNAME,
  password: process.env.DATABASE_PASSWORD,
  // Optional: fetch override for edge environments
  fetch: (url, init) => fetch(url, { ...init, cache: 'no-store' })
})

// Execute query
const { rows } = await conn.execute(
  'SELECT id, name, email FROM users WHERE tenant_id = ? AND is_active = 1 LIMIT ?',
  [tenantId, 20]
)

// Transaction
const results = await conn.transaction(async (tx) => {
  const [order] = await tx.execute(
    'INSERT INTO orders (customer_id, total, status) VALUES (?, ?, ?)',
    [customerId, total, 'pending']
  )
  await tx.execute(
    'INSERT INTO order_items (order_id, product_id, quantity) VALUES ?',
    [cartItems.map(item => [order.insertId, item.id, item.qty])]
  )
  return order.insertId
})
```

```typescript
// With Drizzle ORM + PlanetScale (popular Next.js stack)
import { drizzle } from 'drizzle-orm/planetscale-serverless'
import { connect } from '@planetscale/database'

const connection = connect({ url: process.env.DATABASE_URL })
export const db = drizzle(connection, { schema })

// Query with type safety
const users = await db.select()
  .from(schema.users)
  .where(eq(schema.users.tenantId, tenantId))
  .limit(20)
```

### Schema Design for Vitess/Sharding

```sql
-- Avoid: auto_increment as primary key on sharded tables
-- (creates hotspot on the max-value shard)
-- Use: UUID or ULID for distributed uniqueness

CREATE TABLE orders (
  id CHAR(26) NOT NULL,           -- ULID: sortable + unique
  tenant_id VARCHAR(64) NOT NULL, -- used as vindex (shard key)
  customer_id CHAR(26) NOT NULL,
  total DECIMAL(10, 2) NOT NULL,
  status ENUM('pending','confirmed','shipped','delivered','cancelled') NOT NULL,
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  INDEX idx_tenant_customer (tenant_id, customer_id),
  INDEX idx_tenant_status_created (tenant_id, status, created_at DESC)
  -- No FK constraints: enforced at application layer
);

-- Vschema configuration (PlanetScale manages this internally)
-- Defines how rows are distributed across shards
-- tenant_id as vindex ensures same-tenant data co-located
```

### Boost — Query Caching

PlanetScale Boost é um cache de queries integrado, sem necessidade de [[redis]] externo para casos simples.

```sql
-- Enable Boost for a specific query pattern
-- (configured via PlanetScale dashboard or API)
-- Boost intercepts identical queries and serves from cache

-- Cache invalidation: automatic on table writes
-- TTL: configurable per table (1s to 60s)
-- Best for: read-heavy, moderately stale data (analytics, leaderboards, catalog)
```

### Insights — Query Analytics

```bash
# PlanetScale Insights provides:
# - Slowest queries (p50, p95, p99 latency)
# - Most frequent queries
# - Queries causing full table scans (missing indexes)
# - Rows examined vs rows returned ratio

# Access via dashboard: app.planetscale.com/org/database/insights
# Or via API:
curl -H "Authorization: $PSCALE_TOKEN" \
  "https://api.planetscale.com/v1/organizations/myorg/databases/mydb/query-statistics"
```

---

## Patterns

### Non-Blocking Column Addition

```sql
-- Safe pattern for adding columns to large production tables:

-- Step 1 (deploy request): Add nullable column
ALTER TABLE users ADD COLUMN preferences JSON DEFAULT NULL;

-- Step 2 (background job): Backfill in batches to avoid lock
-- Run in application code:
UPDATE users SET preferences = '{}' WHERE id BETWEEN ? AND ? AND preferences IS NULL;

-- Step 3 (second deploy request): Add NOT NULL constraint + default
ALTER TABLE users MODIFY COLUMN preferences JSON NOT NULL DEFAULT (JSON_OBJECT());
```

### Optimistic Locking Without FK

```sql
-- Without FK constraints, implement optimistic locking with version column
CREATE TABLE inventory (
  product_id CHAR(26) NOT NULL,
  quantity INT UNSIGNED NOT NULL,
  version INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (product_id)
);

-- Application-level referential integrity
UPDATE inventory
SET quantity = quantity - ?, version = version + 1
WHERE product_id = ? AND quantity >= ? AND version = ?;
-- If affected_rows = 0: concurrent modification detected → retry
```

---

## Gotchas

> [!danger] Sem Foreign Keys — Integridade é Responsabilidade sua
> Vitess não suporta FK constraints cross-shard. PlanetScale bloqueia FKs por padrão. Toda integridade referencial deve ser implementada na aplicação. Orphaned records são um risco real sem disciplina.

> [!warning] Scatter Queries São Caros
> Queries sem a coluna de shard key na cláusula WHERE fazem scatter para todos os shards. Com 10 shards, uma query sem índice é executada 10x. Sempre inclua o shard key (tenant_id, user_id) nos filtros principais.

> [!warning] PlanetScale Removeu o Free Tier em 2024
> Em março de 2024, PlanetScale descontinuou o plano gratuito. O Hobby plan mínimo tem custo. Para projetos pessoais, considere [[supabase]] (free tier disponível) ou self-hosted [[postgresql]].

> [!tip] Branching para Testes de Carga
> Use branches para testes de carga antes de fazer deploy em main. Um branch pode ser populado com dados de produção via dump e usado para validar performance de queries com o novo schema.

> [!info] Revert Window de 30 Minutos
> Após deploy de um request, há 30 minutos para fazer revert sem perda de dados. Após esse período, colunas removidas ou tabelas dropadas não são recuperáveis. Monitore deploys ativamente.

---

## References

- [PlanetScale Documentation](https://planetscale.com/docs)
- [Vitess Documentation](https://vitess.io/docs/)
- [Non-blocking Schema Changes](https://planetscale.com/docs/concepts/nonblocking-schema-changes)
- [@planetscale/database Driver](https://github.com/planetscale/database-js)
- [Drizzle + PlanetScale](https://orm.drizzle.team/docs/get-started-mysql)

## Related

- [[database-optimization]]
- [[postgresql]]
- [[deployment-strategies]]
- [[supabase]]
- [[docker]]
