---
tags: [skill, databases, redis]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Redis]
---

# Redis

## Overview

Redis é um in-memory data structure store que opera como banco de dados, cache e message broker simultaneamente. A performance vem da combinação de operações single-threaded (elimina race conditions) com estruturas de dados nativas otimizadas em C. Latência de sub-milissegundo para 99th percentile é realista em hardware adequado.

Para arquiteturas modernas, Redis complementa [[postgresql]] como camada de cache L2, serve como backend para filas via Streams, e implementa padrões de [[messaging-patterns]] sem a complexidade de [[rabbitmq]]. Containerizado via [[docker]] em dev, Redis Cluster em produção. Performance tuning em [[database-optimization]].

---

## Core Concepts

### Data Structures

**Strings** — binários, até 512 MB. Suportam operações atômicas numéricas.

```bash
SET user:session:abc123 '{"user_id":1,"role":"admin"}' EX 3600 NX
# EX: TTL em segundos | NX: só seta se não existir (atômico)

INCR page:views:home          # atomic counter, no race condition
INCRBY inventory:item:42 -5   # decrement stock atomically
GETSET rate_limit:user:1 0    # get old value + reset atomically
```

**Hashes** — field-value pairs. Eficientes para objetos: um Hash com < 128 fields usa ziplist (compacto).

```bash
HSET user:1 name "Alice" email "alice@example.com" tier "premium" login_count 0
HINCRBY user:1 login_count 1
HMGET user:1 name tier           # fetch multiple fields
HGETALL user:1
# Use HSCAN for large hashes — never HGETALL in production on big hashes
```

**Lists** — linked lists. LPUSH/RPUSH O(1). Ideal para queues, recents, timelines.

```bash
LPUSH notifications:user:1 '{"type":"mention","from":"bob"}'
LRANGE notifications:user:1 0 19   # paginate: first 20
BRPOP job_queue:high job_queue:low 30  # blocking pop, priority order, 30s timeout
LMPOP 5 job_queue:high job_queue:low LEFT COUNT 10  # Redis 7.0+: atomic batch dequeue
```

**Sets** — unordered unique values. O(1) add/remove/lookup. Set operations in O(N).

```bash
SADD active_users:2026-04-05 user:1 user:2 user:3
SCARD active_users:2026-04-05         # count
SINTERSTORE result active_users:2026-04-05 premium_users  # intersection → new set
SUNIONSTORE weekly_active result_mon result_tue result_wed result_thu result_fri
```

**Sorted Sets (ZSets)** — unique members with a float score. O(log N) operations. The workhorse for leaderboards, scheduling, rate limiting.

```bash
ZADD leaderboard:game:1 NX 9850.5 "player:alice"   # NX: only add new
ZINCRBY leaderboard:game:1 100 "player:alice"        # atomic score increment
ZRANGEBYSCORE leaderboard:game:1 8000 +inf WITHSCORES LIMIT 0 10
ZREVRANK leaderboard:game:1 "player:alice"           # rank from top

# Scheduled jobs: score = Unix timestamp of execution
ZADD scheduled_jobs 1754000000 "job:send_email:1234"
ZRANGEBYSCORE scheduled_jobs 0 (current_time) LIMIT 0 50  # due jobs
```

**HyperLogLog** — probabilistic cardinality estimation. 12 KB fixed memory regardless of input size. ~0.81% error rate.

```bash
PFADD unique_visitors:2026-04-05 user:1 user:2 user:3
PFCOUNT unique_visitors:2026-04-05     # estimate unique count
PFMERGE unique_visitors:week unique_visitors:2026-04-01 unique_visitors:2026-04-02
```

### Streams (Event Sourcing)

Redis Streams is a persistent, append-only log — like Kafka but embedded in Redis.

```bash
# Producer: append to stream
XADD events:orders '*' order_id 123 status shipped customer_id 456
# '*' = auto-generate ID (timestamp-sequence)

# Consumer Group: competing consumers with acknowledgment
XGROUP CREATE events:orders processing_group $ MKSTREAM
XREADGROUP GROUP processing_group worker-1 COUNT 10 BLOCK 5000 STREAMS events:orders >
# '>' means: deliver only new (undelivered) messages

# Acknowledge processed message
XACK events:orders processing_group 1680000000000-0

# Check pending (unacknowledged) messages — for dead letter handling
XPENDING events:orders processing_group - + 10
```

### Pub/Sub

```bash
# Subscribe (blocking)
SUBSCRIBE channel:notifications:user:1

# Pattern subscribe
PSUBSCRIBE channel:notifications:*

# Publish (fire-and-forget — no persistence, no ACK)
PUBLISH channel:notifications:user:1 '{"type":"message","from":"bob"}'
```

> [!warning] Pub/Sub vs Streams
> Pub/Sub tem zero persistência — se o subscriber estiver offline, a mensagem é perdida. Para reliable messaging, use Streams com consumer groups.

### Lua Scripting

Lua scripts são atômicos — executam sem interrupção. Eliminam race conditions em operações compostas.

```lua
-- Rate limiter: sliding window (Lua ensures atomicity)
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
local count = redis.call('ZCARD', key)

if count < limit then
  redis.call('ZADD', key, now, now .. math.random())
  redis.call('EXPIRE', key, window)
  return 1  -- allowed
else
  return 0  -- rate limited
end
```

```bash
# Load and call script
EVAL "$(cat rate_limit.lua)" 1 rate:user:1 100 60000 1680000000000
# Or with EVALSHA after SCRIPT LOAD for efficiency
```

### Distributed Locking — Redlock Algorithm

```python
# Redlock requires N >= 3 independent Redis instances
# Acquire lock on majority (N/2 + 1) within validity time

import redis
import time
import uuid

def acquire_lock(clients, resource, ttl_ms=10000):
    lock_id = str(uuid.uuid4())
    start = time.time()
    acquired = 0

    for client in clients:
        try:
            ok = client.set(f"lock:{resource}", lock_id, px=ttl_ms, nx=True)
            if ok:
                acquired += 1
        except Exception:
            pass

    elapsed_ms = (time.time() - start) * 1000
    validity = ttl_ms - elapsed_ms - 200  # clock drift buffer

    if acquired >= (len(clients) // 2 + 1) and validity > 0:
        return lock_id  # lock acquired
    else:
        # Release partial locks
        release_lock(clients, resource, lock_id)
        return None
```

### Clustering — Hash Slots

Redis Cluster shards data across 16384 hash slots distributed among master nodes.

```bash
# Hash slot calculation: CRC16(key) % 16384
# Hash tags: {user:1}:session and {user:1}:profile → same slot
redis-cli --cluster create \
  192.168.1.1:7001 192.168.1.2:7002 192.168.1.3:7003 \
  --cluster-replicas 1

# Check slot distribution
redis-cli --cluster check 192.168.1.1:7001

# Resharding (move slots)
redis-cli --cluster reshard 192.168.1.1:7001
```

### Persistence: RDB vs AOF

| Feature | RDB | AOF |
|---------|-----|-----|
| Recovery speed | Fast (binary snapshot) | Slow (replay commands) |
| Data loss risk | Minutes (snapshot interval) | 1 second (fsync=everysec) |
| File size | Small | Large (grows until rewrite) |
| Use case | Backup, fast restart | Durability required |

```bash
# redis.conf — hybrid persistence (recommended for production)
save 900 1       # RDB: if 1 key changed in 900s
save 300 10
save 60 10000
appendonly yes
appendfsync everysec      # balance between performance and durability
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

### Pipelining

```python
# Without pipeline: N round trips
# With pipeline: 1 round trip for N commands

import redis
r = redis.Redis()

pipe = r.pipeline(transaction=False)  # transaction=False = no MULTI/EXEC overhead
for user_id in user_ids:
    pipe.hgetall(f"user:{user_id}")
results = pipe.execute()  # single network round trip
```

---

## Patterns

### Session Store Pattern

```bash
# Store session with sliding expiration
SET session:{token} {user_json} EX 3600
# On each request, reset TTL
EXPIRE session:{token} 3600
```

### Cache-Aside with TTL Jitter

```python
def get_user(user_id: int):
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    user = db.query(User).get(user_id)
    # Jitter prevents cache stampede: base TTL ± 10%
    ttl = 300 + random.randint(-30, 30)
    redis.setex(f"user:{user_id}", ttl, json.dumps(user.dict()))
    return user
```

---

## Gotchas

> [!danger] KEYS Command in Production
> `KEYS *` bloqueia o event loop do Redis inteiro enquanto escaneia. Em produção com 10M+ keys, pode travar o servidor por segundos. Use sempre `SCAN` com cursor.

> [!warning] Memory Eviction Policies
> Configure `maxmemory-policy allkeys-lru` (ou `allkeys-lfu`) quando Redis for usado como cache puro. Sem policy, Redis rejeita writes quando atinge `maxmemory`.

> [!tip] Key Expiry não é Instantâneo
> Redis expira keys de duas formas: lazy (na próxima leitura) e active sampling (20 keys/segundo por default). Em cargas com muitas keys expirando, aumente `hz 20` no redis.conf.

> [!warning] Cluster Cross-Slot Operations
> No Redis Cluster, `MGET`, `SUNION`, e outras operações multi-key falham se as keys estão em slots diferentes. Use hash tags `{prefix}` para forçar co-location.

---

## References

- [Redis Documentation](https://redis.io/docs/)
- [Redis Streams Introduction](https://redis.io/docs/data-types/streams/)
- [Redlock Algorithm](https://redis.io/docs/manual/patterns/distributed-locks/)
- [Redis Cluster Specification](https://redis.io/docs/reference/cluster-spec/)

## Related

- [[postgresql]]
- [[docker]]
- [[messaging-patterns]]
- [[rabbitmq]]
- [[database-optimization]]
