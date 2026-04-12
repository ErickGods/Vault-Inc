---
tags: [snippet, sql]
status: active
level: advanced
updated: 2026-04-05
aliases: [SQL Snippets]
created: 2026-04-05
---

# SQL Snippets

Queries prontas para PostgreSQL cobrindo CTEs, window functions, JSONB, upserts e padrões de performance. Referências: [[postgresql]], [[database-optimization]], [[dbt]], [[supabase]] e [[python-snippets]].

---

## CTEs Simples e Encadeadas

```sql
-- CTE básica para legibilidade
WITH active_users AS (
    SELECT id, name, email, created_at
    FROM users
    WHERE status = 'active'
      AND deleted_at IS NULL
),
recent_orders AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(total) AS total_spent
    FROM orders
    WHERE created_at >= NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    u.id,
    u.name,
    u.email,
    COALESCE(o.order_count, 0)  AS orders_last_30d,
    COALESCE(o.total_spent, 0)  AS spent_last_30d
FROM active_users u
LEFT JOIN recent_orders o ON o.user_id = u.id
ORDER BY o.total_spent DESC NULLS LAST;
```

---

## CTEs Recursivas

```sql
-- Hierarquia de categorias (árvore N-nível)
WITH RECURSIVE category_tree AS (
    -- Anchor: raízes (sem pai)
    SELECT
        id,
        name,
        parent_id,
        0                    AS depth,
        ARRAY[id]            AS path,
        name::TEXT           AS full_path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursão: filhos
    SELECT
        c.id,
        c.name,
        c.parent_id,
        ct.depth + 1,
        ct.path || c.id,
        ct.full_path || ' > ' || c.name
    FROM categories c
    JOIN category_tree ct ON ct.id = c.parent_id
    WHERE ct.depth < 10  -- evitar loops infinitos
)
SELECT id, name, depth, full_path
FROM category_tree
ORDER BY path;

-- Sequência de Fibonacci via CTE recursiva
WITH RECURSIVE fib(n, a, b) AS (
    SELECT 1, 0, 1
    UNION ALL
    SELECT n + 1, b, a + b FROM fib WHERE n < 20
)
SELECT n, a AS fibonacci FROM fib;
```

---

## Window Functions

```sql
-- ROW_NUMBER, RANK, DENSE_RANK
SELECT
    id,
    department,
    salary,
    ROW_NUMBER()  OVER (PARTITION BY department ORDER BY salary DESC) AS row_num,
    RANK()        OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK()  OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank,
    NTILE(4)      OVER (PARTITION BY department ORDER BY salary DESC) AS quartile
FROM employees;

-- LAG e LEAD: variação dia a dia
SELECT
    date,
    revenue,
    LAG(revenue, 1)  OVER (ORDER BY date)     AS prev_day_revenue,
    LEAD(revenue, 1) OVER (ORDER BY date)     AS next_day_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS daily_change,
    ROUND(
        (revenue - LAG(revenue, 1) OVER (ORDER BY date))
        / NULLIF(LAG(revenue, 1) OVER (ORDER BY date), 0) * 100, 2
    ) AS pct_change
FROM daily_sales
ORDER BY date;

-- Running total e média móvel
SELECT
    date,
    amount,
    SUM(amount)  OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS running_total,
    AVG(amount)  OVER (ORDER BY date ROWS 6 PRECEDING)         AS moving_avg_7d,
    MAX(amount)  OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS max_7d
FROM transactions;

-- FIRST_VALUE / LAST_VALUE com frame explícito
SELECT
    employee_id,
    department,
    salary,
    FIRST_VALUE(salary) OVER w AS min_dept_salary,
    LAST_VALUE(salary)  OVER w AS max_dept_salary
FROM employees
WINDOW w AS (
    PARTITION BY department
    ORDER BY salary
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
);
```

---

## Upserts (ON CONFLICT)

```sql
-- Upsert simples: insert ou update
INSERT INTO users (id, email, name, updated_at)
VALUES ('uuid-here', 'user@example.com', 'Alice', NOW())
ON CONFLICT (id)
DO UPDATE SET
    email      = EXCLUDED.email,
    name       = EXCLUDED.name,
    updated_at = EXCLUDED.updated_at
WHERE users.updated_at < EXCLUDED.updated_at;  -- só atualiza se mais recente

-- Upsert com constraint composta
INSERT INTO user_preferences (user_id, key, value)
VALUES ('uuid', 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();

-- Insert ignorando duplicatas (DO NOTHING)
INSERT INTO event_log (event_id, user_id, action, created_at)
SELECT gen_random_uuid(), $1, $2, NOW()
ON CONFLICT (user_id, action, DATE(created_at)) DO NOTHING;

-- Bulk upsert eficiente
INSERT INTO products (sku, name, price, stock)
SELECT sku, name, price, stock
FROM (VALUES
    ('SKU-001', 'Widget A', 9.99, 100),
    ('SKU-002', 'Widget B', 14.99, 50)
) AS data(sku, name, price, stock)
ON CONFLICT (sku) DO UPDATE SET
    name    = EXCLUDED.name,
    price   = EXCLUDED.price,
    stock   = EXCLUDED.stock + products.stock,  -- somar estoque
    updated_at = NOW();
```

---

## JSONB Queries

```sql
-- Criar tabela com JSONB e índices
CREATE TABLE events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type        TEXT NOT NULL,
    payload     JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_payload_gin  ON events USING GIN (payload);
CREATE INDEX idx_events_type_created ON events (type, created_at DESC);

-- Queries básicas JSONB
SELECT payload->>'user_id'              AS user_id,
       payload->'metadata'->>'source'   AS source,
       (payload->>'amount')::NUMERIC    AS amount
FROM events
WHERE type = 'payment'
  AND payload @> '{"status": "completed"}'
  AND (payload->>'amount')::NUMERIC > 100;

-- Atualizar campo aninhado
UPDATE events
SET payload = jsonb_set(payload, '{metadata, processed}', 'true'::jsonb)
WHERE id = 'uuid-here';

-- Remover chave de JSONB
UPDATE events
SET payload = payload - 'sensitive_field'
WHERE type = 'user_data';

-- Expandir array JSONB
SELECT e.id, item->>'product_id' AS product_id, (item->>'qty')::INT AS qty
FROM orders e,
     jsonb_array_elements(e.payload->'items') AS item
WHERE (item->>'qty')::INT > 5;

-- Agregar para JSONB
SELECT
    user_id,
    jsonb_agg(jsonb_build_object('event', type, 'at', created_at) ORDER BY created_at) AS history
FROM events
GROUP BY user_id;
```

---

## Aggregations Avançadas

```sql
-- FILTER para agregações condicionais
SELECT
    DATE_TRUNC('month', created_at)                          AS month,
    COUNT(*)                                                  AS total_orders,
    COUNT(*) FILTER (WHERE status = 'completed')             AS completed,
    COUNT(*) FILTER (WHERE status = 'cancelled')             AS cancelled,
    SUM(total)  FILTER (WHERE status = 'completed')          AS revenue,
    AVG(total)  FILTER (WHERE status = 'completed')          AS avg_order_value
FROM orders
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;

-- GROUPING SETS / ROLLUP / CUBE
SELECT
    department,
    job_title,
    SUM(salary) AS total_salary,
    COUNT(*)    AS headcount
FROM employees
GROUP BY ROLLUP (department, job_title)
ORDER BY department NULLS LAST, job_title NULLS LAST;

-- Percentis e estatísticas
SELECT
    department,
    PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY salary) AS median_salary,
    PERCENTILE_CONT(0.9)  WITHIN GROUP (ORDER BY salary) AS p90_salary,
    PERCENTILE_DISC(0.25) WITHIN GROUP (ORDER BY salary) AS p25_salary,
    MODE() WITHIN GROUP (ORDER BY job_grade)              AS most_common_grade
FROM employees
GROUP BY department;
```

---

## Performance: EXPLAIN & Indexes

```sql
-- Analisar plano de execução
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.name
ORDER BY order_count DESC
LIMIT 10;

-- Criar índice concorrente (sem lock)
CREATE INDEX CONCURRENTLY idx_orders_user_created
ON orders (user_id, created_at DESC)
WHERE status != 'cancelled';

-- Índice parcial para queries frequentes
CREATE INDEX idx_users_active
ON users (email, created_at)
WHERE status = 'active' AND deleted_at IS NULL;

-- Índice de expressão
CREATE INDEX idx_users_email_lower
ON users (LOWER(email));

-- Verificar índices não usados
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%pkey%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Vacuum e estatísticas
VACUUM ANALYZE orders;

-- Ver tamanho de tabelas e índices
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(oid)) AS total_size,
    pg_size_pretty(pg_relation_size(oid))       AS table_size,
    pg_size_pretty(pg_indexes_size(oid))        AS index_size
FROM pg_class
WHERE relkind = 'r' AND relnamespace = 'public'::regnamespace
ORDER BY pg_total_relation_size(oid) DESC;
```

---

## Migration Patterns

```sql
-- Adicionar coluna sem lock (PostgreSQL 11+)
ALTER TABLE orders ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Adicionar coluna com default sem rewrite (PostgreSQL 11+)
ALTER TABLE users ADD COLUMN last_login TIMESTAMPTZ DEFAULT NULL;

-- Rename seguro com zero downtime (passo a passo)
-- 1. Adicionar nova coluna
ALTER TABLE users ADD COLUMN full_name TEXT;
-- 2. Trigger para manter sincronizado
CREATE OR REPLACE FUNCTION sync_full_name() RETURNS trigger AS $$
BEGIN
  NEW.full_name := NEW.first_name || ' ' || NEW.last_name;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_sync_full_name
  BEFORE INSERT OR UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION sync_full_name();
-- 3. Backfill
UPDATE users SET full_name = first_name || ' ' || last_name WHERE full_name IS NULL;
-- 4. Adicionar NOT NULL após backfill
ALTER TABLE users ALTER COLUMN full_name SET NOT NULL;

-- Criar partição de tabela por data
CREATE TABLE events_2024 PARTITION OF events
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Monitorar locks ativos
SELECT pid, query_start, state, wait_event_type, wait_event, left(query, 100)
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
ORDER BY query_start;
```

---

> [!tip] CTEs Materializadas
> No PostgreSQL 12+, CTEs são "fence" (materializadas) por padrão. Use `WITH RECURSIVE ... AS MATERIALIZED` explicitamente ou `AS NOT MATERIALIZED` quando quiser que o planner otimize.

> [!warning] ON CONFLICT e Locks
> Upserts com `ON CONFLICT DO UPDATE` ainda adquirem row locks. Em alta concorrência, avalie se `ON CONFLICT DO NOTHING` + retry na aplicação é mais adequado.

> [!info] Ver também
> - Otimização de queries: [[database-optimization]]
> - Transformações dbt: [[dbt]]
> - Backend Postgres gerenciado: [[supabase]]
> - Conexão via Python: [[python-snippets]]
