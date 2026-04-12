---
tags: [skill, databases, vector-dbs]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Vector Databases, VectorDB]
---

# Vector Databases

## Overview

Bancos vetoriais armazenam e consultam vetores de alta dimensão (embeddings) via similaridade semântica ao invés de igualdade exata. São a fundação de sistemas [[rag-architecture]] modernos — onde [[langchain]] ou frameworks similares orquestram o pipeline de recuperação antes de passar contexto para modelos como os acessados via [[claude-api]].

A escolha entre Pinecone, Weaviate, Chroma, Qdrant ou [[postgresql]] com pgvector não é trivial: envolve trade-offs entre latência, throughput, suporte a metadados, custo operacional e integração com o restante da stack. Estratégias de [[prompt-engineering]] dependem diretamente da qualidade do retrieval.

---

## Core Concepts

### Similarity Metrics

**Cosine Similarity** — mede o ângulo entre vetores (ignora magnitude). Padrão para text embeddings normalizados.

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
Range: [-1, 1] → higher is more similar
```

**Dot Product** — equivalente a cosine quando vetores são L2-normalized. Mais rápido computacionalmente (sem divisão).

```
dot_product(A, B) = Σ(Aᵢ × Bᵢ)
Only meaningful for normalized vectors
```

**Euclidean Distance (L2)** — distância geométrica no espaço n-dimensional. Melhor para embeddings onde magnitude é relevante.

```
l2_distance(A, B) = √(Σ(Aᵢ - Bᵢ)²)
Range: [0, ∞) → lower is more similar
```

> [!tip] Qual métrica usar?
> Para OpenAI e modelos similares (text-embedding-3-*), use cosine ou dot product com vetores normalizados. Para modelos de imagem e multimodais, euclidean pode ser mais representativo. Consulte sempre a documentação do modelo.

### Indexing Algorithms

**HNSW (Hierarchical Navigable Small World)** — grafo multi-camada onde cada nó conecta a neighbors por proximidade. Busca via navegação greedy descendo as camadas.

```
Parâmetros críticos:
- M: número de conexões por nó (default 16). Maior M = melhor recall, mais memória
- ef_construction: tamanho da lista de candidatos durante build (default 200)
- ef_search: tamanho da lista durante query (runtime tunable)

Trade-off: M=64, ef_construction=400 → 95%+ recall, 3x mais memória e build time
```

**IVF (Inverted File Index)** — clusteriza vetores em N centroids (via k-means). Query busca apenas nos `nprobe` clusters mais próximos do vetor de busca.

```
Parâmetros:
- lists: número de clusters (regra: sqrt(total_vectors))
- probes: clusters a inspecionar na query (maior = melhor recall, mais lento)

Melhor que HNSW para datasets estáticos muito grandes (>10M vetores)
Requer treinamento (build é mais lento)
```

**PQ (Product Quantization)** — comprime vetores dividindo em subvetores e quantizando cada um. Reduz memória 8-32x com degradação de recall controlada.

```
Normalmente combinado: IVF + PQ (= IVFPQ) para datasets massivos
Ou: HNSW + PQ (= HNSWPQ) para manter velocidade com compressão
```

### Chunking Strategies

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Fixed-size with overlap (baseline)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,        # tokens or characters
    chunk_overlap=64,      # 12.5% overlap — preserves context at boundaries
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]  # priority order
)

# Semantic chunking — split at semantic boundaries (more compute, better quality)
# Group sentences with similar embeddings; split when similarity drops
def semantic_chunk(text, model, threshold=0.3):
    sentences = sent_tokenize(text)
    embeddings = model.encode(sentences)
    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        sim = cosine_similarity(embeddings[i-1], embeddings[i])
        if sim < threshold:
            chunks.append(" ".join(current))
            current = [sentences[i]]
        else:
            current.append(sentences[i])
    chunks.append(" ".join(current))
    return chunks
```

### Metadata Filtering

```python
# Qdrant: payload filters (pre-filtering before ANN search)
from qdrant_client.models import Filter, FieldCondition, Range, MatchValue

results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="tenant_id", match=MatchValue(value="tenant_abc")),
            FieldCondition(key="created_at", range=Range(gte=1700000000)),
        ],
        should=[
            FieldCondition(key="doc_type", match=MatchValue(value="technical")),
        ]
    ),
    limit=10,
    with_payload=True
)
```

### Hybrid Search (Dense + Sparse)

Combina ANN search (semântico) com BM25/keyword search (lexical) para melhor recall geral.

```python
# Weaviate: hybrid search with Alpha parameter
result = client.query.get("Document", ["content", "title"]) \
    .with_hybrid(
        query="postgresql indexing strategies",
        alpha=0.75,   # 0.0 = pure BM25, 1.0 = pure vector, 0.75 = favor semantic
        properties=["content", "title"]
    ) \
    .with_limit(10) \
    .do()

# Pinecone: sparse-dense hybrid
response = index.query(
    vector=dense_embedding,           # from embedding model
    sparse_vector={"indices": bm25_indices, "values": bm25_scores},  # from BM25
    top_k=10,
    include_metadata=True
)
```

---

## Patterns

### Vendor Comparison

| Feature | Pinecone | Qdrant | Weaviate | Chroma | pgvector |
|---------|----------|--------|----------|--------|----------|
| Hosting | Managed only | Self-host + Cloud | Both | Self-host | Self-host |
| Max dimensions | 20,000 | Unlimited | Unlimited | Unlimited | 2,000 |
| Hybrid search | Yes (sparse+dense) | Yes | Yes | No | With FTS |
| Filtering | Metadata | Payload | GraphQL | Metadata | SQL WHERE |
| Namespaces | Yes (free tier limited) | Collections | Classes | Collections | Tables/schemas |
| HNSW tuning | Limited | Full control | Full control | Limited | Full control |
| Best for | Managed simplicity | OSS production | Multi-modal | Local dev/testing | Existing Postgres |

### pgvector Production Setup

```sql
-- pgvector with IVFFlat index (better for large, relatively static datasets)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(id),
    chunk_index INT,
    content TEXT,
    embedding vector(1536),  -- OpenAI text-embedding-3-small
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- IVFFlat: lists ≈ sqrt(row_count)
-- Build AFTER inserting data (index quality depends on having data to cluster)
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200);

-- Set probes at query time (session level for tuning)
SET ivfflat.probes = 20;

-- Hybrid: vector + full-text in one query
SELECT dc.id, dc.content, dc.metadata,
    1 - (dc.embedding <=> $1) AS vector_score,
    ts_rank(to_tsvector('english', dc.content), plainto_tsquery($2)) AS text_score
FROM document_chunks dc
WHERE dc.metadata @> jsonb_build_object('tenant_id', $3)
ORDER BY (0.7 * (1 - (dc.embedding <=> $1))) + (0.3 * ts_rank(...)) DESC
LIMIT 10;
```

### Qdrant Production Collection

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, HnswConfigDiff,
    OptimizersConfigDiff, QuantizationConfig, ScalarQuantization
)

client = QdrantClient(url="http://localhost:6333", api_key="...")

client.create_collection(
    collection_name="knowledge_base",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(
            m=32,               # higher = better recall, more memory
            ef_construct=200,
            full_scan_threshold=10000  # use HNSW only above this count
        )
    ),
    quantization_config=QuantizationConfig(
        scalar=ScalarQuantization(
            type="int8",
            quantile=0.99,
            always_ram=True    # keep quantized index in RAM
        )
    ),
    optimizers_config=OptimizersConfigDiff(
        indexing_threshold=20000  # delay index build until 20k vectors
    )
)
```

### Re-ranking Pipeline

```python
# Two-stage retrieval: fast ANN (recall@100) → slow re-ranker (precision@10)
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Stage 1: fast ANN retrieval (over-fetch)
candidates = vector_db.search(query_embedding, limit=100)

# Stage 2: cross-encoder re-ranking (reads full content pairs)
pairs = [(query_text, c.content) for c in candidates]
scores = cross_encoder.predict(pairs)

# Return top-10 re-ranked results
reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:10]
```

---

## Gotchas

> [!danger] Embedding Model Lock-in
> Todos os vetores no índice devem usar o mesmo modelo e versão. Migrar de text-embedding-ada-002 para text-embedding-3-large exige re-embedding de todo o corpus. Armazene o `model_id` nos metadados de cada chunk.

> [!warning] Dimensionalidade vs Performance
> Mais dimensões ≠ melhor qualidade. text-embedding-3-small (1536 dims) frequentemente supera modelos maiores em tasks específicas. Teste com Matryoshka truncation antes de optar por 3072 dims.

> [!warning] Index Build vs Query Performance
> HNSW com M=64 e ef_construction=400 melhora recall mas aumenta tempo de build em 4-6x e uso de memória em 2x. Para dados que mudam frequentemente, HNSW com parâmetros menores é mais prático.

> [!tip] Chunking é o Maior Fator de Qualidade
> A escolha de chunk size e overlap impacta retrieval mais do que a escolha de algoritmo de index. Chunks muito pequenos perdem contexto; muito grandes diluem a relevância semântica. 256-512 tokens com 10-15% overlap é um bom ponto de partida.

> [!example] Metadata Filtering Cardinality
> Filtros em campos de alta cardinalidade (user_id com milhões de valores) podem forçar full scan mesmo com index. Qdrant e Weaviate usam payload indexes separados — crie-os explicitamente para campos filtrados frequentemente.

---

## References

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Weaviate Docs](https://weaviate.io/developers/weaviate)
- [HNSW Paper — Malkov & Yashunin](https://arxiv.org/abs/1603.09320)
- [Pinecone Learning Center](https://www.pinecone.io/learn/)

## Related

- [[rag-architecture]]
- [[langchain]]
- [[postgresql]]
- [[claude-api]]
- [[prompt-engineering]]
