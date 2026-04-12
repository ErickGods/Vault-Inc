---
tags: [skill, databases, database-optimization]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Database Optimization, DB Optimization]
---

# Database Optimization

## Overview

Otimização de banco de dados é a disciplina que converte gargalos de I/O, CPU e memória em performance mensurável. A metodologia correta começa sempre por medir antes de otimizar — o instinto sobre onde está o problema costuma estar errado.

A stack completa envolve: queries bem escritas com índices corretos, [[postgresql]] com autovacuum ajustado, connection pooling via PgBouncer, [[redis]] como camada de cache, [[mongodb]] com aggregation pipeline eficiente, e [[supabase]] com RLS que não penaliza queries. Tudo instrumentado via [[observability]] para detectar regressões. A complexidade algorítmica das operações de banco é análoga ao que se estuda em [[big-o-notation]].

---

## Core Concepts

### EXPLAIN ANALYZE Deep Dive

```sql
-- Full diagnostic output: use all options
EXPLAIN (
  ANALYZE,      -- actually execute the query
  BUFFERS,      -- show cache hits vs disk reads
  VERBOSE,      -- show output columns per node
  FORMAT JSON   -- machine-readable for tooling (e.g., explain.dalibo.com)
) SELECT ...;

-- Key nodes to understand:
-- Seq Scan: full table scan — acceptable for small tables, red flag for large
-- Index Scan: uses index to find rows, then fetches from heap
-- Index Only Scan: satisfies query from index alone (zero heap access) — ideal
-- Bitmap Index Scan + Bitmap Heap Scan: multiple indexes merged via bitmap
-- Hash Join: hash table built from smaller relation
-- Merge Join: requires sorted inputs (often uses indexes)
-- Nested Loop: for each row in outer, scan inner — terrible for large datasets
```

```sql
-- Reading EXPLAIN output
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = '123' AND status = 'pending';

-- Gather  (cost=0.43..8.46 rows=1 width=200) (actual time=0.123..0.456 rows=3 loops=1)
--   ->  Index Scan using idx_orders_customer_status on orders
--         Index Cond: ((customer_id = '123') AND (status = 'pending'))
--         Buffers: shared hit=4 read=0   ← all from cache, 0 disk reads
-- Planning Time: 0.234 ms
-- Execution Time: 0.567 ms

-- "cost=start..total" — planner estimates
-- "actual time=start..end" — real milliseconds
-- "rows=N" — compare estimated vs actual (large difference = stale statistics → ANALYZE)
-- "Buffers: shared hit=N read=M" — hit=cache, read=disk (read >> hit = memory issue)
```

**Identifying problematic patterns:**

```sql
-- Check for sequential scans on large tables
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan,
  seq_tup_read / NULLIF(seq_scan, 0) AS avg_rows_per_seq_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0
  AND seq_tup_read / NULLIF(seq_scan, 0) > 10000  -- scanning >10k rows each time
ORDER BY seq_tup_read DESC;

-- Find queries with bad row estimation (cause poor plan choices)
SELECT query, rows, rows_removed, shared_blks_hit, shared_blks_read,
  shared_blks_read::float / NULLIF(shared_blks_hit + shared_blks_read, 0) AS miss_ratio
FROM pg_stat_statements
WHERE calls > 100
ORDER BY miss_ratio DESC;
```

### Index Strategy Deep Dive

**B-tree index ordering** — the sort order of index columns matters for sort operations:

```sql
-- Query: WHERE status = 'active' ORDER BY created_at DESC NULLS LAST
-- Optimal index:
CREATE INDEX idx_users_status_created ON users (status, created_at DESC NULLS LAST);
-- Without NULLS LAST match: PostgreSQL adds a separate sort step

-- Composite index: equality columns first, then range/sort
-- ESR Rule (MongoDB) applies similarly to PostgreSQL:
-- Equality → Sort → Range
CREATE INDEX idx_orders_customer_status_date
ON orders (customer_id, status, created_at DESC);
-- Supports: WHERE customer_id=? (E)
-- Supports: WHERE customer_id=? ORDER BY created_at DESC (E+S)
-- Supports: WHERE customer_id=? AND status=? ORDER BY created_at DESC (E+E+S)
-- Supports: WHERE customer_id=? AND created_at > ? (E+R — status skipped)
```

**Hash indexes** — O(1) equality lookup, smaller than B-tree, not WAL-logged pre-Postgres 10:

```sql
CREATE INDEX idx_tokens_hash ON api_tokens USING HASH (token_value);
-- Good for: equality-only, no range queries, no sorting
-- Bad for: range queries, LIKE, ORDER BY
```

**Partial and conditional indexes:**

```sql
-- Index only rows that are actually queried
CREATE INDEX idx_active_users ON users (email) WHERE deleted_at IS NULL;
CREATE INDEX idx_pending_payments ON payments (created_at, amount)
  WHERE status IN ('pending', 'processing');

-- Covering index with INCLUDE (PostgreSQL 11+)
-- The INCLUDE columns are stored in leaf nodes but not part of the key
CREATE INDEX idx_orders_covering ON orders (customer_id, status)
  INCLUDE (total, created_at, shipping_address);
-- Query: SELECT total, created_at FROM orders WHERE customer_id=? AND status=?
-- → Index Only Scan: never touches the heap
```

### Connection Pooling — PgBouncer

PostgreSQL spawns one OS process per connection. With 1000 connections, each holding ~5MB memory = 5 GB just for connection overhead.

```ini
# pgbouncer.ini — production configuration
[databases]
myapp = host=127.0.0.1 port=5432 dbname=myapp

[pgbouncer]
listen_port = 6432
listen_addr = *
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

# Transaction mode: connection returned to pool after each transaction
# Best for web apps — allows 10,000 app connections with 100 DB connections
pool_mode = transaction
max_client_conn = 10000    # max app connections
default_pool_size = 25     # DB connections per (user, database) pair
reserve_pool_size = 5      # extra connections for bursts
reserve_pool_timeout = 3

# Timeouts
server_idle_timeout = 600  # return idle server connections to pool
client_idle_timeout = 0    # keep app connections indefinitely
query_timeout = 30         # kill queries running > 30s
```

> [!warning] Transaction Mode Limitations
> Em transaction mode, `SET`, `LISTEN`, advisory locks, e prepared statements de servidor não funcionam entre transações. Prepared statements do lado do cliente (driver-side) são seguros.

**pgcat** — alternativa mais nova, suporta read replicas automaticamente:

```toml
# pgcat.toml
[general]
host = "0.0.0.0"
port = 6432
pool_size = 30

[[pools.myapp.users.myuser.servers]]
host = "primary.db.internal"
port = 5432
role = "primary"

[[pools.myapp.users.myuser.servers]]
host = "replica1.db.internal"
port = 5432
role = "replica"
# pgcat routes SELECT to replicas, writes to primary automatically
```

### VACUUM and Autovacuum Tuning

```sql
-- Check autovacuum effectiveness
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum, last_autoanalyze,
  autovacuum_count, autoanalyze_count
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- Table-level autovacuum tuning for hot tables
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.01,    -- trigger at 1% dead rows (default: 20%)
  autovacuum_analyze_scale_factor = 0.005,  -- analyze at 0.5% changed rows
  autovacuum_vacuum_cost_delay = 2          -- reduce IO throttling (ms, default: 20)
);

-- Manual VACUUM for emergency bloat removal
VACUUM (ANALYZE, VERBOSE) orders;

-- VACUUM FULL: rewrites table, reclaims space — requires AccessExclusiveLock (downtime!)
-- Alternative: pg_repack (no full lock)
-- pg_repack -t orders mydb
```

### Read Replicas and Routing

```python
# SQLAlchemy: route reads to replica, writes to primary
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

primary = create_engine("postgresql://primary:5432/mydb", pool_size=10)
replica = create_engine("postgresql://replica:5432/mydb", pool_size=20)

# Application-level routing
class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        if self._flushing or (clause is not None and clause.get_children()):
            return primary  # writes go to primary
        return replica      # reads go to replica
```

### Caching Layers

**Application-level cache (in-memory):**

```python
import asyncio
from functools import lru_cache
from cachetools import TTLCache

# Simple in-process cache — invalidated on restart
config_cache = TTLCache(maxsize=100, ttl=300)

async def get_feature_flags(tenant_id: str) -> dict:
    if tenant_id in config_cache:
        return config_cache[tenant_id]
    flags = await db.fetch_one("SELECT flags FROM tenant_config WHERE id=$1", tenant_id)
    config_cache[tenant_id] = flags
    return flags
```

**Materialized Views:**

```sql
-- Expensive aggregation computed once, refreshed periodically
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
  DATE_TRUNC('month', created_at) AS month,
  tenant_id,
  SUM(total) AS revenue,
  COUNT(*) AS order_count,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
WHERE status = 'completed'
GROUP BY 1, 2;

CREATE UNIQUE INDEX ON monthly_revenue (month, tenant_id);

-- Concurrent refresh (no lock on reads during refresh)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;

-- Schedule refresh via pg_cron extension
SELECT cron.schedule('refresh-revenue', '0 1 * * *',
  'REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue');
```

### N+1 Detection and Fix

```python
# N+1 pattern: 1 query for list + N queries for each item
# BAD:
posts = await db.fetch("SELECT * FROM posts WHERE author_id=$1", user_id)
for post in posts:
    comments = await db.fetch("SELECT * FROM comments WHERE post_id=$1", post.id)

# GOOD: JOIN in single query
posts_with_comments = await db.fetch("""
  SELECT p.*, json_agg(c.*) FILTER (WHERE c.id IS NOT NULL) AS comments
  FROM posts p
  LEFT JOIN comments c ON c.post_id = p.id
  WHERE p.author_id = $1
  GROUP BY p.id
""", user_id)

# GOOD alternative: 2 queries with IN clause (better than N+1)
posts = await db.fetch("SELECT * FROM posts WHERE author_id=$1", user_id)
post_ids = [p.id for p in posts]
comments = await db.fetch("SELECT * FROM comments WHERE post_id = ANY($1)", post_ids)
# Group comments by post_id in Python
```

### Slow Query Logging

```sql
-- postgresql.conf: log queries slower than 1 second
log_min_duration_statement = 1000  -- milliseconds

-- Also useful:
log_statement = 'none'    -- don't log all statements (too noisy)
log_lock_waits = on       -- log when waiting for locks
deadlock_timeout = 1000   -- detect deadlocks after 1s

-- pg_stat_statements: aggregated query stats (best production tool)
-- Set in postgresql.conf:
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all

-- Query the stats:
SELECT
  LEFT(query, 80) AS query_preview,
  calls,
  round(mean_exec_time::numeric, 2) AS avg_ms,
  round(total_exec_time::numeric, 2) AS total_ms,
  round(stddev_exec_time::numeric, 2) AS stddev_ms,
  round(rows / calls::numeric, 1) AS avg_rows
FROM pg_stat_statements
WHERE calls > 50
ORDER BY mean_exec_time DESC
LIMIT 25;
```

---

## Gotchas

> [!danger] Nunca Optimize sem Medir Primeiro
> O plano de execução real (`EXPLAIN ANALYZE`) deve guiar toda otimização. Criar índices "preventivamente" em colunas erradas desperdiça espaço, aumenta write overhead e pode piorar a performance do planner.

> [!warning] Index Bloat Silencioso
> Índices também acumulam bloat com UPDATEs e DELETEs. `pg_stat_user_indexes` não mostra bloat de índice — use `pgstattuple` extension ou `REINDEX CONCURRENTLY` periodicamente em índices muito modificados.

> [!warning] Statistics Target para Queries Complexas
> O planner usa histogramas de 100 buckets por padrão. Para colunas com distribuição desigual (status com 95% = 'completed'), aumente: `ALTER TABLE orders ALTER COLUMN status SET STATISTICS 500; ANALYZE orders;`

> [!tip] Cache Hit Ratio como SLO
> Um buffer cache hit ratio < 99% indica que o `shared_buffers` está subdimensionado ou que o working set não cabe em memória. Monitore: `SELECT sum(blks_hit)/(sum(blks_hit)+sum(blks_read)) FROM pg_stat_database;`

> [!info] Particionamento Muda o EXPLAIN
> Em tabelas particionadas, o EXPLAIN mostra "Append" ou "Merge Append" sobre os scans das partições relevantes. Partition pruning deve eliminar partições irrelevantes — verifique se aparece "Partitions removed" no output.

---

## References

- [PostgreSQL EXPLAIN Documentation](https://www.postgresql.org/docs/current/sql-explain.html)
- [PgBouncer Documentation](https://www.pgbouncer.org/config.html)
- [pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [explain.dalibo.com — Visual EXPLAIN](https://explain.dalibo.com/)
- [pganalyze Index Advisor](https://pganalyze.com/)
- [USE THE INDEX, LUKE](https://use-the-index-luke.com/)

## Related

- [[postgresql]]
- [[redis]]
- [[mongodb]]
- [[supabase]]
- [[big-o-notation]]
- [[observability]]
