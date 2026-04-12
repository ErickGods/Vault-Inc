---
tags: [skill, ai-ml, rag-architecture]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [RAG, Retrieval Augmented Generation]
---

# RAG Architecture

## Overview

Retrieval Augmented Generation (RAG) é a arquitetura padrão para grounding de LLMs em bases de conhecimento privadas ou atualizadas. Em vez de fine-tuning, injeta contexto relevante recuperado dinamicamente no prompt — mais barato, auditável e atualizável.

Componentes críticos: chunking, embedding, vector search (ver [[vector-dbs]]), re-ranking e geração. Orquestração via [[langchain]] ou pipelines customizados. Dados estruturados podem viver em [[postgresql]] com pgvector. Prompts de geração seguem padrões de [[prompt-engineering]]. Produção geralmente envolve a [[claude-api]] como gerador final.

> [!tip] RAG vs Fine-tuning
> Use RAG quando o conhecimento muda frequentemente ou precisa ser auditável. Use fine-tuning para adaptar estilo, tom ou capacidade de reasoning — não para injetar fatos novos.

---

## Core Concepts

### Pipeline RAG Clássico

```
Query
  │
  ▼
Query Transformation ──► Embedding ──► Vector Search
                                            │
                                            ▼
                                       Re-ranking
                                            │
                                            ▼
                                    Contextual Compression
                                            │
                                            ▼
                                    Prompt Assembly
                                            │
                                            ▼
                                        LLM Generation
                                            │
                                            ▼
                                    Output Validation
```

### Chunking Strategies Comparadas

| Estratégia | Descrição | Chunk Size | Melhor para |
|-----------|-----------|------------|-------------|
| Fixed-size | Divide por N tokens com overlap | 512 tok / 50 overlap | Texto homogêneo |
| Recursive | Divide por `\n\n`, `\n`, `. `, ` ` em cascata | Variável | Prosa geral |
| Semantic | Agrupa frases por similaridade embedada | Variável | Documentos longos |
| Document-aware | Respeita headings, tabelas, código | Estrutural | Markdown, PDFs |

---

## Patterns

### 1. Chunking com Document-Aware Splitting

```python
# document_chunker.py — chunking que respeita estrutura Markdown
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def chunk_markdown_document(text: str) -> list[dict]:
    # Primeiro: divide por headers para manter contexto hierárquico
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"), ("##", "h2"), ("###", "h3")
        ],
        strip_headers=False,
    )
    header_chunks = header_splitter.split_text(text)

    # Segundo: subdivide chunks grandes respeitando sentenças
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    final_chunks = []
    for chunk in header_chunks:
        sub_chunks = char_splitter.split_documents([chunk])
        # Propaga metadata de header para todos os sub-chunks
        for sc in sub_chunks:
            sc.metadata.update(chunk.metadata)
            final_chunks.append(sc)

    return final_chunks
```

### 2. Hybrid Search: Dense + Sparse (BM25)

Busca híbrida combina embeddings semânticos (recall alto) com BM25 lexical (precisão para termos técnicos/raros):

```python
# hybrid_search.py — RRF fusion de dense + sparse
from rank_bm25 import BM25Okapi
import numpy as np

def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[int]:
    """Combina múltiplos rankings via Reciprocal Rank Fusion."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)

class HybridRetriever:
    def __init__(self, docs: list[str], vector_store):
        self.bm25 = BM25Okapi([d.split() for d in docs])
        self.vector_store = vector_store
        self.docs = docs

    def retrieve(self, query: str, top_k: int = 10) -> list[str]:
        # Dense retrieval via embeddings
        dense_results = self.vector_store.similarity_search(query, k=top_k * 2)
        dense_ids = [self.docs.index(r.page_content) for r in dense_results]

        # Sparse retrieval via BM25
        bm25_scores = self.bm25.get_scores(query.split())
        sparse_ids = np.argsort(bm25_scores)[::-1][:top_k * 2].tolist()

        # Fusão via RRF
        fused = reciprocal_rank_fusion([dense_ids, sparse_ids])
        return [self.docs[i] for i in fused[:top_k]]
```

### 3. Re-ranking com Cross-Encoder

```python
# reranker.py — Cohere Rerank ou sentence-transformers cross-encoder
from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: list[str], top_n: int = 5) -> list[tuple[str, float]]:
        pairs = [(query, doc) for doc in documents]
        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )
        return ranked[:top_n]

# Alternativa via Cohere API (melhor qualidade, custo por chamada)
import cohere

def cohere_rerank(query: str, docs: list[str], top_n: int = 5) -> list[dict]:
    co = cohere.Client()
    results = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=docs,
        top_n=top_n,
        return_documents=True,
    )
    return [{"text": r.document.text, "score": r.relevance_score} for r in results.results]
```

### 4. Query Transformation

**HyDE (Hypothetical Document Embeddings)** — gera documento hipotético como proxy para busca:

```python
# hyde.py — busca via documento hipotético gerado pelo LLM
async def hyde_retrieve(query: str, retriever, llm_client) -> list[str]:
    # Gera resposta hipotética sem contexto real
    hypothetical_doc = await llm_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"Write a short document that would perfectly answer: {query}"
        }]
    )
    hyde_text = hypothetical_doc.content[0].text

    # Usa embedding do doc hipotético para buscar docs reais
    return retriever.retrieve(hyde_text)
```

**Multi-Query** — gera variações da query para cobrir diferentes perspectivas:

```python
async def multi_query_retrieve(query: str, retriever, llm_client, n: int = 3) -> list[str]:
    expansion_prompt = f"""Generate {n} different phrasings of this question to improve retrieval.
    Return ONLY the questions, one per line.
    Original: {query}"""

    response = await llm_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        messages=[{"role": "user", "content": expansion_prompt}]
    )

    queries = [query] + response.content[0].text.strip().split("\n")
    all_docs = []
    seen = set()

    for q in queries:
        for doc in retriever.retrieve(q, top_k=5):
            if doc not in seen:
                seen.add(doc)
                all_docs.append(doc)

    return all_docs[:15]  # deduplicated union
```

### 5. Contextual Compression

Remove partes irrelevantes dos chunks antes de enviar ao LLM, reduzindo tokens e ruído:

```python
# contextual_compression.py
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import ContextualCompressionRetriever

def build_compressed_retriever(base_retriever, llm):
    compressor = LLMChainExtractor.from_llm(llm)
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever,
    )

# Alternativa: extração baseada em embeddings (mais rápida, sem LLM call)
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain_openai import OpenAIEmbeddings

embedding_filter = EmbeddingsFilter(
    embeddings=OpenAIEmbeddings(),
    similarity_threshold=0.76,  # remove sentenças com similaridade < 0.76
)
```

### 6. Parent Document Retriever

Indexa chunks pequenos (melhor recall) mas retorna documento pai completo (melhor contexto):

```python
# parent_doc_retriever.py
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

retriever = ParentDocumentRetriever(
    vectorstore=vector_store,    # indexa chunks filhos pequenos
    docstore=InMemoryStore(),    # armazena documentos pais completos
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
# Busca encontra chunks de 400 tokens, mas retorna pais de 2000 tokens
```

### 7. GraphRAG — Conhecimento Estruturado em Grafos

```python
# graphrag_sketch.py — conceito de GraphRAG (Microsoft)
# Constrói knowledge graph de entidades e relações, não apenas chunks planos

class GraphRAGRetriever:
    """
    1. Extract: LLM extrai (entidade, relação, entidade) de cada chunk
    2. Build: Constrói grafo de conhecimento (NetworkX ou Neo4j)
    3. Community Detection: Agrupa entidades por Leiden algorithm
    4. Summarize: LLM sumariza cada comunidade
    5. Query: Busca global via community summaries + local via subgrafos
    """
    def retrieve(self, query: str, mode: str = "local") -> list[str]:
        if mode == "global":
            return self._global_search(query)   # community summaries
        elif mode == "local":
            return self._local_search(query)    # subgrafo de entidades
        else:
            # Drift search: combina embedding com graph traversal
            return self._drift_search(query)
```

---

## Gotchas

> [!danger] Chunk Size é Context-Dependent
> Não existe tamanho de chunk universal. Documentos técnicos densos funcionam melhor com chunks menores (256-400 tokens). Narrativas longas precisam de chunks maiores (800-1200 tokens). Sempre avalie com RAGAS.

> [!warning] Embedding Model Lock-in
> Trocar o modelo de embedding requer re-indexar TODO o vector store. Documente o modelo usado com cada índice e versione os índices separadamente dos dados.

> [!warning] Lost in the Middle
> LLMs têm pior performance com contexto no meio do prompt. Ordene chunks recuperados com os mais relevantes no início e no fim — nunca apenas em ordem de score.

> [!note] Latência em Produção
> Pipeline completo (query transform + hybrid search + rerank + compress) pode adicionar 2-4s de latência. Use caching agressivo de embeddings de queries frequentes e resultados de rerank.

---

## Snippets

### Avaliação com RAGAS

```python
# ragas_eval.py — métricas de qualidade de RAG
from ragas import evaluate
from ragas.metrics import (
    faithfulness,          # resposta suportada pelo contexto?
    answer_relevancy,      # resposta relevante à pergunta?
    context_recall,        # contexto cobre a ground truth?
    context_precision,     # contexto recuperado é preciso?
    answer_correctness,    # resposta correta vs ground truth?
)
from datasets import Dataset

eval_dataset = Dataset.from_dict({
    "question": ["What is RAG?", "How does BM25 work?"],
    "answer": ["RAG combines retrieval...", "BM25 uses term frequency..."],
    "contexts": [["chunk1", "chunk2"], ["chunk3"]],
    "ground_truth": ["RAG stands for...", "BM25 is a ranking function..."],
})

results = evaluate(
    dataset=eval_dataset,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    llm=judge_llm,
    embeddings=eval_embeddings,
)
print(results)  # DataFrame com scores por métrica
```

### Caching de Embeddings com Redis

```python
# embedding_cache.py
import hashlib
import redis
import numpy as np

class CachedEmbeddings:
    def __init__(self, base_embeddings, redis_client: redis.Redis, ttl: int = 86400):
        self.base = base_embeddings
        self.r = redis_client
        self.ttl = ttl

    def embed_query(self, text: str) -> list[float]:
        cache_key = f"emb:{hashlib.sha256(text.encode()).hexdigest()}"
        cached = self.r.get(cache_key)
        if cached:
            return np.frombuffer(cached, dtype=np.float32).tolist()

        embedding = self.base.embed_query(text)
        self.r.setex(cache_key, self.ttl, np.array(embedding, dtype=np.float32).tobytes())
        return embedding
```

---

## References

- [RAG Survey: Naive, Advanced, Modular (Gao et al., 2023)](https://arxiv.org/abs/2312.10997)
- [RAGAS: Automated Evaluation of RAG Pipelines](https://docs.ragas.io/)
- [GraphRAG: Microsoft Research](https://microsoft.github.io/graphrag/)
- [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval (Sarthi et al., 2024)](https://arxiv.org/abs/2401.18059)
- [HyDE: Precise Zero-Shot Dense Retrieval (Gao et al., 2022)](https://arxiv.org/abs/2212.10496)
- [LangChain RAG How-Tos](https://python.langchain.com/docs/how_to/#qa-with-rag)

---

## Related

- [[vector-dbs]] — Chroma, Pinecone, Weaviate, pgvector para armazenamento de embeddings
- [[langchain]] — orquestração de pipelines RAG com retrievers e chains
- [[postgresql]] — pgvector extension para RAG sem infra externa
- [[prompt-engineering]] — design do prompt de geração com contexto recuperado
- [[claude-api]] — modelo de geração final que consome o contexto RAG
