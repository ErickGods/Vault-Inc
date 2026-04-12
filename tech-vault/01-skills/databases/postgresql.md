---
tags: [skill, databases, postgresql]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [PostgreSQL, Postgres, pg]
---

# PostgreSQL

## Overview

PostgreSQL é um banco de dados relacional objeto-orientado com mais de 35 anos de desenvolvimento ativo. Diferente de outros SGBDs, o Postgres oferece extensibilidade real: você pode criar tipos de dados, operadores, funções e até métodos de acesso customizados. Para cargas de trabalho avançadas, combina ACID compliance com recursos que rivalizam com bancos especializados — JSONB para documentos, pgvector para embeddings, TimescaleDB para séries temporais.

O ecossistema moderno usa Postgres como base para [[supabase]], integra com [[fastapi]] e [[django]] via ORMs sofisticados, e frequentemente complementa com [[redis]] para cache. Containerizar com [[docker]] é o padrão para desenvolvimento e staging. Ver [[database-optimization]] para tuning de performance.

---

## Core Concepts

### Advanced Indexing

**B-Tree** is the default and handles equality + range queries. Always the starting point.

**GIN (Generalized Inverted Index)** — optimal for composite values (arrays, JSONB, full-text search). Each element in the collection is indexed separately.

```sql
-- GIN for JSONB document search
CREATE INDEX idx_users_metadata_gin ON users USING GIN (metadata);

-- GIN for full-text search
CREATE INDEX idx_articles_fts ON articles USING GIN (to_tsvector('portuguese', title || ' ' || body));

-- Query using the GIN index
SELECT * FROM articles
WHERE to_tsvector('portuguese', title || ' ' || body) @@ to_tsquery('postgresql & performance');
```

**GiST (Generalized Search Tree)** — extensible index for geometric types, ranges, full-text (alternative to GIN). Lossy, requires recheck, but supports more operator classes.

```sql
-- GiST for IP range queries (requires cidr type)
CREATE INDEX idx_network_ranges ON ip_allowlist USING GIST (network inet_ops);

-- GiST for geometric proximity
CREATE INDEX idx_locations_gist ON stores USING GIST (coordinates);
SELECT * FROM stores WHERE coordinates <-> point(40.7128, -74.0060) < 10;
```

**BRIN (Block Range INdex)** — ultra-small index for naturally ordered data (timestamps, sequential IDs). Stores min/max per block range.

```sql
-- BRIN for time-series data — massive size savings
CREATE INDEX idx_events_created_brin ON events USING BRIN (created_at) WITH (pages_per_range = 128);
-- BRIN index is ~1000x smaller than B-tree for monotonic data
```

**Partial Indexes** — index only rows matching a condition. Dramatically reduces size and speeds up selective queries.

```sql
-- Only index active users (99% of queries filter by is_active = true)
CREATE INDEX idx_users_email_active ON users (email) WHERE is_active = true;

-- Only index unprocessed jobs (hot path)
CREATE INDEX idx_jobs_pending ON jobs (created_at, priority) WHERE status = 'pending';
```

**Covering Indexes** — `INCLUDE` columns to enable index-only scans, avoiding heap access entirely.

```sql
-- Query: SELECT email, name FROM users WHERE tenant_id = $1 ORDER BY created_at
-- Without covering index: index scan + heap fetch for each row
CREATE INDEX idx_users_tenant_covering ON users (tenant_id, created_at)
INCLUDE (email, name);
-- Now: index-only scan — zero heap access
```

### CTEs and Recursive Queries

```sql
-- Recursive CTE: org hierarchy traversal
WITH RECURSIVE org_tree AS (
  -- Anchor member
  SELECT id, name, manager_id, 0 AS depth, ARRAY[id] AS path
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- Recursive member
  SELECT e.id, e.name, e.manager_id, ot.depth + 1, ot.path || e.id
  FROM employees e
  JOIN org_tree ot ON e.manager_id = ot.id
  WHERE NOT e.id = ANY(ot.path) -- cycle guard
)
SELECT * FROM org_tree ORDER BY depth, name;

-- Writeable CTE: UPDATE with RETURNING piped into INSERT
WITH updated AS (
  UPDATE orders SET status = 'shipped', shipped_at = NOW()
  WHERE status = 'packed' AND created_at < NOW() - INTERVAL '2 hours'
  RETURNING id, customer_id, total
)
INSERT INTO audit_log (entity_type, entity_id, action, metadata)
SELECT 'order', id, 'auto_shipped', jsonb_build_object('total', total)
FROM updated;
```

### Window Functions

```sql
-- Running total + rank within partition
SELECT
  customer_id,
  order_date,
  amount,
  SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total,
  RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC) AS spend_rank,
  LAG(amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_amount,
  amount - LAG(amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS delta
FROM orders;

-- NTILE: bucket customers into quartiles by LTV
SELECT customer_id, ltv,
  NTILE(4) OVER (ORDER BY ltv DESC) AS quartile
FROM customer_summary;
```

### Table Partitioning

```sql
-- Range partitioning by month (most common for time-series)
CREATE TABLE events (
  id BIGSERIAL,
  created_at TIMESTAMPTZ NOT NULL,
  event_type TEXT,
  payload JSONB
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2026_01 PARTITION OF events
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE events_2026_02 PARTITION OF events
  FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Each partition can have its own indexes
CREATE INDEX ON events_2026_01 (event_type, created_at);

-- Hash partitioning for even distribution
CREATE TABLE user_sessions (
  session_id UUID NOT NULL,
  user_id BIGINT NOT NULL,
  data JSONB
) PARTITION BY HASH (user_id);

CREATE TABLE user_sessions_0 PARTITION OF user_sessions FOR VALUES WITH (modulus 4, remainder 0);
CREATE TABLE user_sessions_1 PARTITION OF user_sessions FOR VALUES WITH (modulus 4, remainder 1);
```

### JSONB Deep Dive

```sql
-- JSONB operators
SELECT metadata -> 'address' ->> 'city' FROM users;      -- text extraction
SELECT metadata @> '{"role": "admin"}'::jsonb FROM users; -- containment
SELECT metadata ?| ARRAY['premium', 'trial'] FROM users;  -- key exists (any)

-- JSONB path queries (PostgreSQL 12+)
SELECT jsonb_path_query(payload, '$.items[*] ? (@.price > 100)')
FROM orders;

-- Update nested JSONB field
UPDATE users
SET metadata = jsonb_set(metadata, '{address, city}', '"São Paulo"')
WHERE id = $1;

-- GIN index on specific JSONB path
CREATE INDEX idx_users_role ON users USING GIN ((metadata -> 'role'));
```

### Extensions

```sql
-- pgvector: vector similarity search
CREATE EXTENSION vector;
ALTER TABLE documents ADD COLUMN embedding vector(1536);
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
SELECT id, content FROM documents ORDER BY embedding <=> $1 LIMIT 10;

-- pg_trgm: fuzzy string matching
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);
SELECT * FROM products WHERE name % 'postgresq'; -- similarity threshold

-- TimescaleDB: time-series
SELECT create_hypertable('metrics', 'time');
SELECT add_retention_policy('metrics', INTERVAL '90 days');
```

### LISTEN/NOTIFY and Logical Replication

```sql
-- LISTEN/NOTIFY for real-time pub/sub within Postgres
LISTEN order_updates;
NOTIFY order_updates, '{"order_id": 123, "status": "shipped"}';

-- In application code (Python asyncpg)
-- await conn.add_listener('order_updates', callback)

-- Logical replication slot for CDC
SELECT pg_create_logical_replication_slot('my_slot', 'pgoutput');
SELECT * FROM pg_logical_slot_peek_changes('my_slot', NULL, NULL);
```

---

## Patterns

### pg_stat Views for Diagnostics

```sql
-- Find slow queries (requires pg_stat_statements)
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 20;

-- Index usage stats — find unused indexes
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexname NOT LIKE '%pkey%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Table bloat detection
SELECT relname, n_dead_tup, n_live_tup,
  round(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 2) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_ratio DESC;
```

---

## Gotchas

> [!warning] VACUUM e Bloat
> PostgreSQL não sobrescreve rows atualizados — cria versões novas (MVCC). Rows mortos acumulam bloat. Configure `autovacuum_vacuum_scale_factor = 0.01` para tabelas grandes em vez do padrão 0.2.

> [!danger] Lock Escalation em Migrations
> `ALTER TABLE ADD COLUMN` com default value faz full table rewrite em versões < 11. Em Postgres 11+, defaults não-voláteis são safe. Use `pg_repack` ou `ALTER TABLE ... SET DEFAULT` + backfill para tabelas grandes em produção.

> [!warning] Connection Limits
> Postgres spawns um processo por conexão. Com 500+ conexões simultâneas, o overhead de context switching degrada tudo. Use PgBouncer em transaction mode como proxy — ver [[database-optimization]].

> [!tip] EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
> Sempre use `BUFFERS` para ver cache hits vs disk reads, e `FORMAT JSON` para análise programática. O custo estimado em `EXPLAIN` é em "unidades arbitrárias" baseadas em `seq_page_cost`.

---

## References

- [PostgreSQL 16 Docs](https://www.postgresql.org/docs/16/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [USE THE INDEX, LUKE](https://use-the-index-luke.com/)
- [pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html)

## Related

- [[database-optimization]]
- [[supabase]]
- [[django]]
- [[fastapi]]
- [[redis]]
- [[docker]]
