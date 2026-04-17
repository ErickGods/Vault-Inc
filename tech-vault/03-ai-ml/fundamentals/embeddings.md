---
tags: [ai-ml, fundamentals, embeddings, vector-search, semantic-similarity]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Embeddings, Vector Embeddings, Semantic Embeddings]
---

# Embeddings

## Overview

Embeddings são representações numéricas densas de dados (texto, imagem, áudio) em espaços vetoriais de alta dimensionalidade, onde a proximidade geométrica reflete similaridade semântica. Um embedding transforma tokens ou sentenças em vetores de ponto flutuante (ex: 1536 dimensões) de forma que "gato" e "felino" ficam próximos no espaço, enquanto "gato" e "banco" ficam distantes.

Embeddings são a fundação do retrieval semântico em [[rag-architecture]], alimentam o sistema de busca em [[vector-dbs]], e são produzidos internamente pelo attention mechanism em [[transformer-architecture]]. Entender embeddings profundamente é pré-requisito para construir sistemas RAG de alta qualidade.

> [!tip] Intuição Central
> Um espaço vetorial de embeddings bem treinado captura relações analógicas: `vec("rei") - vec("homem") + vec("mulher") ≈ vec("rainha")`. A aritmética vetorial é semântica.

---

## Como Funciona

### Geometria do Espaço Vetorial

Embeddings vivem em espaços de alta dimensionalidade onde distância é semântica. Três métricas dominam:

#### Cosine Similarity

Mede o ângulo entre dois vetores, ignorando magnitude:

```
cos(θ) = (A·B) / (|A|·|B|)
```

- Range: [-1, 1] onde 1 = idênticos, 0 = ortogonais, -1 = opostos
- **Quando usar:** textos de comprimentos variados. Normaliza o fato de documentos longos produzirem vetores de maior magnitude, focando apenas na direção semântica.

#### Euclidean Distance (L2)

Distância "reta" entre dois pontos no espaço:

```
d(A,B) = sqrt(Σ(a_i - b_i)²)
```

- Range: [0, ∞) onde 0 = idênticos
- **Quando usar:** espaços onde magnitude importa (ex: embeddings de imagem, embeddings de recomendação onde intensidade de preferência é relevante). Sensível a outliers em dimensões individuais.

#### Dot Product

Produto escalar entre vetores:

```
A·B = Σ(a_i · b_i)
```

- Range: (-∞, +∞)
- **Quando usar:** quando o modelo foi explicitamente treinado com dot product como objective (ex: `text-embedding-3` da OpenAI). Mais rápido computacionalmente que cosine pois evita a normalização.

#### Relação Entre Cosine e Dot Product

Para vetores normalizados (L2 norm = 1):

```
cos_sim(A,B) = dot(A/|A|, B/|B|) = dot(A_norm, B_norm)
```

Isso significa que normalizar vetores antes de armazenar no vector DB permite usar dot product com resultado idêntico ao cosine similarity — e dot product é mais rápido na maioria das implementações SIMD.

---

### Arquitetura de Modelos de Embedding

#### Bi-Encoder

Duas torres de encoder independentes: uma para a query, outra para o documento. O score de similaridade é calculado após o encoding:

```
sim(q, d) = cos(enc(q), enc(d))
```

- **Vantagem:** documentos podem ser pré-computados (pre-encode) offline. Na query time, só a query é encodada e compara-se contra o índice.
- **Limitação:** sem interação entre query e documento durante o encoding — menos expressivo.
- **Exemplos:** SBERT (Sentence-BERT), E5, BGE, Voyage

#### Cross-Encoder

Query e documento são concatenados e processados juntos por um único encoder:

```
score(q, d) = linear(enc([q; SEP; d])[:, CLS])
```

- **Vantagem:** máxima qualidade — o modelo vê a interação entre query e documento em todas as camadas de atenção.
- **Limitação:** não é possível pre-computar. Cada par (query, documento) requer uma inferência separada — inviável para retrieval em larga escala.
- **Uso principal:** re-ranking. Primeiro o bi-encoder recupera top-100 candidatos, depois o cross-encoder re-ranqueia para top-10.

#### Mean Pooling vs [CLS] Token Pooling

Após o encoder transformer, existe a questão de como colapsar a sequência de token embeddings em um único vetor:

| Método | Descrição | Qualidade |
|--------|-----------|-----------|
| **[CLS] Pooling** | Usa apenas o embedding do token especial [CLS] | BERT-base usa, mas [CLS] nem sempre captura semântica global |
| **Mean Pooling** | Média de todos os token embeddings da sequência | Geralmente superior para similaridade semântica |

SBERT demonstrou empiricamente que mean pooling supera [CLS] pooling em quase todos os benchmarks de similaridade de sentenças. A intuição: [CLS] foi treinado para classificação (NSP em BERT), não para representação de sentenças.

#### Dimensões Típicas

```
384  →  MiniLM (all-MiniLM-L6-v2) — leve e rápido
768  →  BERT-base, MPNet-base — equilibrado
1024 →  Large models, E5-large, BGE-M3 — alta qualidade
1536 →  text-embedding-3-small (OpenAI) — API padrão
3072 →  text-embedding-3-large (OpenAI) — máxima qualidade OpenAI
```

---

### Modelos Principais

| Modelo | Dimensões | MTEB Score | Tokens max | Uso |
|--------|-----------|-----------|-----------|-----|
| all-MiniLM-L6-v2 | 384 | ~56 | 256 | Rápido, local |
| all-mpnet-base-v2 | 768 | ~57 | 384 | Equilibrado |
| text-embedding-3-small | 1536 | ~62 | 8191 | OpenAI barato |
| text-embedding-3-large | 3072 | ~64 | 8191 | OpenAI melhor |
| E5-large-v2 | 1024 | ~63 | 512 | Open-source forte |
| BGE-M3 | 1024 | ~67 | 8192 | Multilingual SOTA |
| Voyage-3 | 1024 | ~68 | 32000 | RAG especializado |

> [!note] MTEB Benchmark
> MTEB (Massive Text Embedding Benchmark) é o padrão da indústria para comparar modelos de embedding. Cobre 56 datasets em 8 categorias de tarefas: retrieval, clustering, classification, reranking, STS, summarization, bitext mining, pair classification. Um modelo com MTEB ~67 é substancialmente melhor que ~57 em tarefas reais de RAG.

---

### Matryoshka Representation Learning (MRL)

MRL é uma técnica de treinamento que produz embeddings "telescópicos" — você pode truncar as primeiras N dimensões e ainda obter um embedding de qualidade razoável.

**Por que funciona:** durante o treinamento, o modelo é otimizado simultaneamente com múltiplas dimensionalidades:

```python
# Loss hierárquico MRL (pseudocódigo)
loss = sum(
    weight_d * contrastive_loss(embeddings[:d])
    for d in [64, 128, 256, 512, 1024, 1536, 3072]
)
```

O gradiente força as primeiras dimensões a conterem a informação mais importante, com dimensões extras adicionando progressivamente mais detalhe.

**Como `text-embedding-3` implementa:**

```python
from openai import OpenAI

client = OpenAI()

# Embedding completo (3072 dims)
response_full = client.embeddings.create(
    model="text-embedding-3-large",
    input="exemplo de texto",
)
emb_full = response_full.data[0].embedding  # len = 3072

# Embedding truncado via dimensions parameter (1024 dims)
response_trunc = client.embeddings.create(
    model="text-embedding-3-large",
    input="exemplo de texto",
    dimensions=1024,  # MRL: trunca e re-normaliza
)
emb_trunc = response_trunc.data[0].embedding  # len = 1024
```

**Trade-off de qualidade vs custo:**

| Dims | MTEB Score (approx) | Storage vs 3072 | Latência |
|------|--------------------|--------------------|---------|
| 256  | ~60 | -92% | Mínima |
| 512  | ~62 | -83% | Baixa |
| 1024 | ~63 | -67% | Média |
| 1536 | ~63.5 | -50% | Média |
| 3072 | ~64 | baseline | Alta |

1536 dims em vez de 3072 economiza 50% de armazenamento com apenas ~2% de perda de qualidade — excelente trade-off para produção.

---

### Anisotropia

**O problema:** embeddings de LLMs tendem a ocupar apenas um cone estreito do espaço vetorial, em vez de distribuir-se uniformemente. Isso reduz a discriminabilidade — vetores de textos semanticamente distintos ficam artificialmente próximos.

**Como medir:**

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Corpus aleatório
texts = ["texto aleatório " + str(i) for i in range(1000)]
embeddings = model.encode(texts, normalize_embeddings=True)

# Mean cosine similarity entre pares aleatórios
n = 500
idx1 = np.random.choice(len(embeddings), n)
idx2 = np.random.choice(len(embeddings), n)
similarities = np.sum(embeddings[idx1] * embeddings[idx2], axis=1)

print(f"Mean cosine similarity (random pairs): {similarities.mean():.3f}")
# Ideal: próximo de 0.0
# Problemático: 0.5+ (indica anisotropia severa)
```

**Soluções:**

1. **Whitening (Z-score por dimensão):**

```python
def whiten_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """Aplica z-score normalização por dimensão para reduzir anisotropia."""
    mean = embeddings.mean(axis=0)
    std = embeddings.std(axis=0) + 1e-8  # evita divisão por zero
    whitened = (embeddings - mean) / std
    # Re-normaliza para L2 = 1
    norms = np.linalg.norm(whitened, axis=1, keepdims=True)
    return whitened / norms
```

2. **PCA Whitening:** aplica PCA e normaliza pela raiz dos eigenvalues, decorrelacionando as dimensões.

---

### Dimensionality Reduction

Redução de dimensionalidade serve dois propósitos distintos: **armazenamento eficiente** e **visualização**.

#### PCA (Principal Component Analysis)

- **Tipo:** linear
- **Preserva:** variância máxima global
- **Uso:** reduzir antes de armazenar em vector DB (ex: 1536 → 256 dims), pré-processamento antes de clustering
- **Limitação:** não captura relações não-lineares

```python
from sklearn.decomposition import PCA
import numpy as np

embeddings = np.load("embeddings.npy")  # shape: (N, 1536)

pca = PCA(n_components=256)
reduced = pca.fit_transform(embeddings)  # shape: (N, 256)

print(f"Variância explicada: {pca.explained_variance_ratio_.sum():.2%}")
# Geralmente ~85-90% com n_components=256 para embeddings densos
```

#### UMAP (Uniform Manifold Approximation and Projection)

- **Tipo:** não-linear
- **Preserva:** estrutura local e global do manifold
- **Uso:** visualização 2D/3D, pré-clustering, redução funcional moderada
- **Vantagem sobre t-SNE:** preserva distâncias globais, escalável, reproduzível

#### t-SNE

- **Tipo:** não-linear
- **Preserva:** estrutura local (vizinhanças)
- **Uso:** **apenas visualização 2D/3D**
- **NÃO usar para:** redução funcional downstream — t-SNE não preserva distâncias globais, e o mapeamento não é generalizável para novos pontos

| Técnica | Tipo | Preserva Global | Escalável | Generalizável | Uso |
|---------|------|-----------------|-----------|---------------|-----|
| PCA | Linear | Sim | Sim | Sim | Armazenamento, clustering |
| UMAP | Não-linear | Parcial | Sim | Sim | Visualização, clustering |
| t-SNE | Não-linear | Não | Limitado | Não | Apenas visualização |

---

## Implementação Prática

### 1. Geração de Embeddings com Sentence-Transformers

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

def gerar_embeddings(textos: List[str], modelo: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """
    Gera embeddings normalizados para uma lista de textos.
    Retorna array shape (N, D) com L2 norm = 1.
    """
    model = SentenceTransformer(modelo)
    embeddings = model.encode(
        textos,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,  # L2 = 1 — permite usar dot product como cosine
    )
    return embeddings  # np.ndarray float32

def busca_cosine(
    query: str,
    corpus: List[str],
    corpus_embeddings: np.ndarray,
    modelo: str = "all-MiniLM-L6-v2",
    top_k: int = 5,
) -> List[dict]:
    """
    Busca semântica por cosine similarity (via dot product em vetores normalizados).
    """
    model = SentenceTransformer(modelo)
    query_emb = model.encode([query], normalize_embeddings=True)[0]

    # Dot product = cosine similarity quando ambos estão normalizados
    scores = corpus_embeddings @ query_emb  # shape: (N,)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {"texto": corpus[i], "score": float(scores[i])}
        for i in top_indices
    ]


# --- Exemplo de uso ---
corpus = [
    "Transformers são a arquitetura dominante em NLP desde 2017.",
    "Redes neurais recorrentes processam sequências token por token.",
    "Embeddings mapeiam texto para espaços vetoriais densos.",
    "O mecanismo de atenção computa pesos de relevância entre tokens.",
    "BERT usa transformers bidirecionais pré-treinados em MLM.",
    "Futebol é o esporte mais popular do mundo.",
    "O Brasil ganhou 5 Copas do Mundo de futebol.",
]

corpus_embs = gerar_embeddings(corpus)
resultados = busca_cosine("como funciona atenção em transformers?", corpus, corpus_embs)

for r in resultados:
    print(f"[{r['score']:.3f}] {r['texto']}")
```

---

### 2. Comparação de Qualidade Entre Modelos

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from itertools import combinations

# Corpus em português com pares de alta/baixa similaridade
pares_similares = [
    ("O carro está na garagem.", "O automóvel está estacionado."),
    ("Inteligência artificial muda o mercado de trabalho.", "IA transforma o emprego."),
    ("Receita de bolo de chocolate.", "Como fazer bolo de chocolate em casa."),
]

pares_diferentes = [
    ("O carro está na garagem.", "A IA transforma o emprego."),
    ("Receita de bolo de chocolate.", "O automóvel está estacionado."),
    ("Inteligência artificial muda o mercado de trabalho.", "Receita de bolo de chocolate."),
]

modelos = [
    "all-MiniLM-L6-v2",       # 384 dims, rápido
    "all-mpnet-base-v2",       # 768 dims, equilibrado
    "paraphrase-multilingual-mpnet-base-v2",  # multilingual
]

def avaliar_modelo(nome_modelo: str) -> dict:
    model = SentenceTransformer(nome_modelo)

    sims_positivas = []
    for t1, t2 in pares_similares:
        e1 = model.encode([t1], normalize_embeddings=True)[0]
        e2 = model.encode([t2], normalize_embeddings=True)[0]
        sims_positivas.append(float(e1 @ e2))

    sims_negativas = []
    for t1, t2 in pares_diferentes:
        e1 = model.encode([t1], normalize_embeddings=True)[0]
        e2 = model.encode([t2], normalize_embeddings=True)[0]
        sims_negativas.append(float(e1 @ e2))

    return {
        "modelo": nome_modelo,
        "sim_positiva_media": np.mean(sims_positivas),
        "sim_negativa_media": np.mean(sims_negativas),
        "gap": np.mean(sims_positivas) - np.mean(sims_negativas),
    }

print(f"{'Modelo':<45} {'Sim+':>6} {'Sim-':>6} {'Gap':>6}")
print("-" * 70)
for modelo in modelos:
    r = avaliar_modelo(modelo)
    print(f"{r['modelo']:<45} {r['sim_positiva_media']:>6.3f} {r['sim_negativa_media']:>6.3f} {r['gap']:>6.3f}")

# Gap maior = melhor discriminação semântica
```

---

### 3. Visualização UMAP 2D

```python
import numpy as np
import matplotlib.pyplot as plt
import umap
from sentence_transformers import SentenceTransformer

# Corpus categorizado
categorias = {
    "tecnologia": [
        "Machine learning usa dados para treinar modelos.",
        "Redes neurais aprendem representações hierárquicas.",
        "Python é a linguagem dominante em data science.",
        "GPU acelera o treinamento de modelos deep learning.",
        "Transformers revolucionaram o processamento de linguagem natural.",
    ],
    "esportes": [
        "Futebol é o esporte mais popular do mundo.",
        "O Brasil venceu a Copa do Mundo cinco vezes.",
        "Tênis é disputado em quadras de saibro, grama e piso duro.",
        "Basquete foi inventado em 1891 por James Naismith.",
        "A Fórmula 1 é a categoria máxima do automobilismo.",
    ],
    "culinária": [
        "Bolo de chocolate leva cacau em pó ou chocolate amargo.",
        "Arroz e feijão é o prato típico brasileiro.",
        "Macarrão al dente deve ser cozido em água com sal.",
        "Churrasco brasileiro usa cortes bovinos como picanha.",
        "Pão de queijo é uma receita mineira com polvilho.",
    ],
}

textos = []
labels = []
cores = {"tecnologia": "blue", "esportes": "green", "culinária": "red"}
cor_lista = []

for categoria, texts in categorias.items():
    textos.extend(texts)
    labels.extend([categoria] * len(texts))
    cor_lista.extend([cores[categoria]] * len(texts))

# Gerar embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(textos, normalize_embeddings=True)

# Reduzir para 2D com UMAP
reducer = umap.UMAP(
    n_components=2,
    n_neighbors=5,      # vizinhança local (menor = mais local)
    min_dist=0.3,       # compactação dos clusters
    metric="cosine",    # mesma métrica usada na busca
    random_state=42,
)
embedding_2d = reducer.fit_transform(embeddings)

# Plot
fig, ax = plt.subplots(figsize=(10, 7))
for categoria, cor in cores.items():
    mask = [l == categoria for l in labels]
    x = embedding_2d[mask, 0]
    y = embedding_2d[mask, 1]
    ax.scatter(x, y, c=cor, label=categoria, s=100, alpha=0.8)

# Anotar pontos
for i, texto in enumerate(textos):
    ax.annotate(
        texto[:30] + "...",
        (embedding_2d[i, 0], embedding_2d[i, 1]),
        fontsize=6,
        alpha=0.6,
    )

ax.legend(fontsize=12)
ax.set_title("UMAP 2D — Clusters Semânticos por Categoria", fontsize=14)
ax.set_xlabel("UMAP-1")
ax.set_ylabel("UMAP-2")
plt.tight_layout()
plt.savefig("embeddings_umap.png", dpi=150)
plt.show()
```

---

### 4. Nearest Neighbor Search com NumPy (Sem Vector DB)

```python
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SearchResult:
    idx: int
    text: str
    score: float

class NumpyVectorStore:
    """
    Vector store simples em memória usando NumPy.
    Para produção use [[vector-dbs]] (Pinecone, Weaviate, Qdrant).
    Suporta até ~100k vetores eficientemente em RAM.
    """

    def __init__(self):
        self.embeddings: Optional[np.ndarray] = None  # (N, D)
        self.texts: List[str] = []

    def add(self, texts: List[str], embeddings: np.ndarray):
        """Adiciona vetores ao store. Assume embeddings já normalizados (L2=1)."""
        self.texts.extend(texts)
        if self.embeddings is None:
            self.embeddings = embeddings.astype(np.float32)
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings.astype(np.float32)])

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """
        Busca os top_k vizinhos mais próximos por dot product.
        O(N*D) — adequado para até ~100k vetores.
        """
        if self.embeddings is None:
            return []

        # Normaliza query se necessário
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm

        # Dot product matricial: O(N*D)
        scores = self.embeddings @ query_embedding  # shape: (N,)

        # Top-K sem ordenar tudo (O(N) em vez de O(N log N))
        if top_k >= len(scores):
            top_indices = np.argsort(scores)[::-1]
        else:
            # np.argpartition é O(N) para pegar top-K sem sort completo
            partition = np.argpartition(scores, -top_k)[-top_k:]
            top_indices = partition[np.argsort(scores[partition])[::-1]]

        return [
            SearchResult(idx=int(i), text=self.texts[i], score=float(scores[i]))
            for i in top_indices
        ]

    def save(self, path: str):
        """Persiste o store em disco."""
        np.save(f"{path}_embeddings.npy", self.embeddings)
        with open(f"{path}_texts.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(self.texts))

    @classmethod
    def load(cls, path: str) -> "NumpyVectorStore":
        """Carrega store do disco."""
        store = cls()
        store.embeddings = np.load(f"{path}_embeddings.npy")
        with open(f"{path}_texts.txt", encoding="utf-8") as f:
            store.texts = f.read().splitlines()
        return store


# --- Exemplo de uso ---
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
store = NumpyVectorStore()

documentos = [
    "Embeddings são representações vetoriais de texto.",
    "Transformers usam mecanismo de atenção multi-head.",
    "RAG combina retrieval e geração para reduzir alucinações.",
    "Vector databases indexam embeddings para busca eficiente.",
    "Fine-tuning adapta um modelo pré-treinado a uma tarefa específica.",
]

embs = model.encode(documentos, normalize_embeddings=True)
store.add(documentos, embs)

query = "como funciona busca semântica em vetores?"
query_emb = model.encode([query], normalize_embeddings=True)[0]
resultados = store.search(query_emb, top_k=3)

for r in resultados:
    print(f"[{r.score:.3f}] {r.text}")
```

---

### 5. API de Embeddings — OpenAI e Anthropic

#### OpenAI

```python
from openai import OpenAI
import numpy as np

client = OpenAI()  # usa OPENAI_API_KEY do ambiente

def embed_openai(
    texts: list[str],
    model: str = "text-embedding-3-small",
    dimensions: int | None = None,  # MRL: None = dimensões completas
) -> np.ndarray:
    """
    Gera embeddings via OpenAI API.

    text-embedding-3-small: 1536 dims, barato (~$0.02/1M tokens)
    text-embedding-3-large: 3072 dims, melhor (~$0.13/1M tokens)
    """
    kwargs = {"model": model, "input": texts}
    if dimensions:
        kwargs["dimensions"] = dimensions  # MRL truncation

    response = client.embeddings.create(**kwargs)

    # OpenAI retorna embeddings já normalizados para L2 = 1
    return np.array([item.embedding for item in response.data], dtype=np.float32)


# Exemplo com MRL — economiza 50% de storage
embs_1536 = embed_openai(["exemplo de texto"], dimensions=1536)
embs_3072 = embed_openai(["exemplo de texto"])  # full 3072

print(f"Shape 1536: {embs_1536.shape}")
print(f"Shape 3072: {embs_3072.shape}")
print(f"L2 norm (deve ser ~1.0): {np.linalg.norm(embs_1536[0]):.4f}")
```

#### Voyage AI (RAG especializado)

```python
import voyageai
import numpy as np

client = voyageai.Client()  # usa VOYAGE_API_KEY

def embed_voyage(
    texts: list[str],
    input_type: str = "document",  # "query" ou "document"
    model: str = "voyage-3",
) -> np.ndarray:
    """
    Voyage-3: 1024 dims, MTEB ~68, 32k tokens max.
    input_type="query" para queries de busca.
    input_type="document" para documentos do corpus.
    """
    result = client.embed(texts, model=model, input_type=input_type)
    return np.array(result.embeddings, dtype=np.float32)


# Assimetria query vs documento — crítica para qualidade
doc_embs = embed_voyage(["Transformers usam atenção multi-head."], input_type="document")
query_emb = embed_voyage(["como funciona atenção?"], input_type="query")

score = float(doc_embs[0] @ query_emb[0])
print(f"Score: {score:.3f}")
```

> [!note] Anthropic e Embeddings
> A API da Anthropic (Claude) não oferece endpoint de embeddings — Claude é um modelo generativo, não de embedding. Para embeddings em produção com Anthropic use: `text-embedding-3` (OpenAI), `Voyage-3` (Anthropic investiu na Voyage AI), ou modelos open-source via sentence-transformers.

---

## Comparativos

### Bi-Encoder vs Cross-Encoder

| Aspecto | Bi-Encoder | Cross-Encoder |
|---------|-----------|---------------|
| **Arquitetura** | Duas torres independentes | Um encoder com Q+D concatenados |
| **Pre-compute** | Sim — documentos podem ser indexados offline | Não — requer re-inferência por query |
| **Latência de retrieval** | Baixa (busca vetorial + 1 encoding) | Alta (N encodings por query) |
| **Qualidade** | Boa (sem interação Q-D no encoding) | Excelente (interação total Q-D) |
| **Escala** | Milhões/bilhões de documentos | Dezenas de candidatos (pós-retrieval) |
| **Uso ideal** | First-stage retrieval | Re-ranking de candidatos |
| **Exemplos** | SBERT, E5, BGE, Voyage | ms-marco-MiniLM-L-6-v2, bge-reranker |
| **Padrão recomendado** | Bi-encoder → top-100 → Cross-encoder → top-10 | — |

### Redução de Dimensionalidade

| Técnica | Tipo | Global | Local | Generalizável | Determinístico | Uso Principal |
|---------|------|--------|-------|---------------|----------------|---------------|
| **PCA** | Linear | Sim | Parcial | Sim | Sim | Storage, clustering |
| **UMAP** | Não-linear | Parcial | Sim | Sim | Com seed | Visualização, clustering |
| **t-SNE** | Não-linear | Não | Sim | Não | Com seed | Apenas visualização |

---

## Gotchas

> [!warning] Embeddings de Modelos Diferentes São Incompatíveis
> Você NÃO pode misturar embeddings de modelos diferentes num mesmo vector store. "similar" em OpenAI text-embedding-3 e "similar" em BGE-M3 são espaços vetoriais completamente diferentes. Comparar embeddings de modelos distintos produz scores sem sentido semântico.

> [!warning] Textos Longos Diluem o Embedding
> Mean pooling sobre 2048 tokens produz um embedding que "médias" todo o documento. Para documentos longos, use chunking (ex: 256-512 tokens com overlap de 50-100 tokens) antes de embeddar. Um documento com 10 tópicos terá um embedding que representa a "média" dos tópicos — não é bom para retrieval específico.

> [!warning] Query ≠ Documento em Modelos Assimétricos
> Modelos como E5 e BGE usam prefixos diferentes para query e documento:
> - E5: `"query: "` e `"passage: "`
> - BGE: `"Represent this sentence: "` para queries (documentos sem prefixo)
> - BGE-M3: `"Represent this sentence for searching relevant passages: "` para queries
>
> Usar o prefixo errado degrada retrieval quality significativamente. Leia a documentação do modelo.

```python
# Correto — E5 com prefixos assimétricos
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/e5-large-v2")

query = "query: como transformers funcionam?"
doc = "passage: Transformers usam mecanismo de atenção multi-head para processar sequências."

q_emb = model.encode([query], normalize_embeddings=True)[0]
d_emb = model.encode([doc], normalize_embeddings=True)[0]

score = float(q_emb @ d_emb)
print(f"Score com prefixo correto: {score:.3f}")  # ~0.85

# Errado — sem prefixo
q_emb_wrong = model.encode(["como transformers funcionam?"], normalize_embeddings=True)[0]
score_wrong = float(q_emb_wrong @ d_emb)
print(f"Score sem prefixo: {score_wrong:.3f}")  # ~0.70 — degradação
```

> [!warning] Embedding Drift Ao Trocar de Modelo
> Ao mudar o modelo de embedding, TODOS os documentos precisam ser re-embedados e o vector store recriado do zero. Não há compatibilidade entre versões ou modelos diferentes. Planeje migrações com cuidado — inclui downtime ou dual-write.

> [!tip] Normalizar Antes de Armazenar
> Normalizar embeddings para L2 = 1 antes de armazenar no vector DB permite usar dot product em vez de cosine similarity (equivalentes para vetores normalizados) — dot product é mais rápido na maioria dos vector DBs por evitar a divisão pela norma em runtime.

```python
# Normalizar embeddings antes de inserir no vector DB
import numpy as np

def normalizar_l2(embeddings: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings / np.maximum(norms, 1e-8)  # evita divisão por zero

embs = np.random.randn(100, 1536).astype(np.float32)
embs_norm = normalizar_l2(embs)
print(np.linalg.norm(embs_norm, axis=1).mean())  # deve ser ~1.0
```

---

## Snippets

### Chunking com Overlap para Documentos Longos

```python
from typing import List

def chunk_texto(
    texto: str,
    chunk_size: int = 400,    # tokens aproximados (palavras * 1.3)
    overlap: int = 80,
    separador: str = ". ",
) -> List[str]:
    """
    Divide texto em chunks com overlap para evitar perda de contexto nas bordas.
    Usa separação por sentenças quando possível.
    """
    # Split por sentenças
    sentencas = texto.replace(".\n", ". ").split(separador)
    sentencas = [s.strip() for s in sentencas if s.strip()]

    chunks = []
    buffer = []
    buffer_len = 0

    for sentenca in sentencas:
        palavras = len(sentenca.split())
        tokens_aprox = int(palavras * 1.3)

        if buffer_len + tokens_aprox > chunk_size and buffer:
            chunks.append(separador.join(buffer))
            # Mantém overlap: últimas N palavras
            overlap_words = 0
            new_buffer = []
            for s in reversed(buffer):
                overlap_words += len(s.split())
                new_buffer.insert(0, s)
                if overlap_words >= overlap:
                    break
            buffer = new_buffer
            buffer_len = sum(int(len(s.split()) * 1.3) for s in buffer)

        buffer.append(sentenca)
        buffer_len += tokens_aprox

    if buffer:
        chunks.append(separador.join(buffer))

    return chunks


# --- Uso ---
texto_longo = """
Transformers revolucionaram o processamento de linguagem natural desde 2017.
O mecanismo de atenção permite que o modelo capture dependências de longo alcance.
Embeddings são produzidos pelo pooling dos hidden states do encoder.
Redes bidirecionais como BERT veem contexto esquerdo e direito simultaneamente.
""" * 20  # simula documento longo

chunks = chunk_texto(texto_longo, chunk_size=400, overlap=80)
print(f"Total de chunks: {len(chunks)}")
for i, c in enumerate(chunks[:3]):
    print(f"Chunk {i}: {c[:100]}...")
```

### Pipeline RAG Completo com Re-ranking

```python
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np
from typing import List

class RAGRetriever:
    """
    Pipeline retrieval em duas etapas:
    1. Bi-encoder: recupera top-N candidatos rapidamente
    2. Cross-encoder: re-ranqueia para precisão máxima
    """

    def __init__(
        self,
        bi_encoder_model: str = "all-MiniLM-L6-v2",
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.bi_encoder = SentenceTransformer(bi_encoder_model)
        self.cross_encoder = CrossEncoder(cross_encoder_model)
        self.corpus: List[str] = []
        self.corpus_embeddings: np.ndarray | None = None

    def index(self, documentos: List[str]):
        self.corpus = documentos
        self.corpus_embeddings = self.bi_encoder.encode(
            documentos,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def retrieve(self, query: str, top_k_retrieval: int = 20, top_k_final: int = 5) -> List[dict]:
        # Stage 1: bi-encoder retrieval (rápido)
        query_emb = self.bi_encoder.encode([query], normalize_embeddings=True)[0]
        bi_scores = self.corpus_embeddings @ query_emb
        top_indices = np.argsort(bi_scores)[::-1][:top_k_retrieval]
        candidatos = [(int(i), self.corpus[i]) for i in top_indices]

        # Stage 2: cross-encoder re-ranking (preciso)
        pares = [(query, doc) for _, doc in candidatos]
        cross_scores = self.cross_encoder.predict(pares)

        # Combina índices originais com scores do cross-encoder
        resultados = [
            {"idx": candidatos[i][0], "texto": candidatos[i][1], "score": float(cross_scores[i])}
            for i in range(len(candidatos))
        ]
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:top_k_final]


# --- Uso ---
retriever = RAGRetriever()
retriever.index([
    "Transformers usam self-attention para modelar dependências em sequências.",
    "BERT é um modelo pré-treinado bidirecional da Google.",
    "Embeddings mapeiam tokens para vetores densos.",
    "O mecanismo de atenção pondera a relevância de cada token para os outros.",
    "Fine-tuning adapta um modelo pré-treinado a uma tarefa específica.",
])

results = retriever.retrieve("como atenção funciona em transformers?")
for r in results:
    print(f"[{r['score']:.3f}] {r['texto']}")
```

### Detecção de Drift de Embeddings

```python
import numpy as np
from scipy.stats import ks_2samp

def detectar_drift_embeddings(
    embs_baseline: np.ndarray,
    embs_producao: np.ndarray,
    threshold: float = 0.05,
) -> dict:
    """
    Detecta drift de distribuição entre embeddings baseline e produção.
    Usa KS-test por dimensão. P-value < threshold indica drift significativo.
    """
    n_dims = embs_baseline.shape[1]
    p_values = []

    for dim in range(n_dims):
        _, p = ks_2samp(embs_baseline[:, dim], embs_producao[:, dim])
        p_values.append(p)

    p_values = np.array(p_values)
    frac_drift = (p_values < threshold).mean()

    return {
        "frac_dimensoes_com_drift": float(frac_drift),
        "drift_detectado": frac_drift > 0.1,  # >10% das dims em drift = alerta
        "p_value_medio": float(p_values.mean()),
        "dims_mais_afetadas": np.argsort(p_values)[:10].tolist(),
    }
```

---

## References

- [SBERT: Sentence-BERT — Sentence Embeddings using Siamese BERT-Networks (Reimers & Gurevych, 2019)](https://arxiv.org/abs/1908.10084) — Apresentou bi-encoders com mean pooling para similaridade semântica
- [Matryoshka Representation Learning (Kusupati et al., 2022)](https://arxiv.org/abs/2205.13147) — MRL: embeddings truncáveis sem perda proporcional de qualidade
- [BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity (Chen et al., 2024)](https://arxiv.org/abs/2309.07597) — SOTA multilingual, suporte a dense/sparse/multi-vector retrieval
- [MTEB: Massive Text Embedding Benchmark (Muennighoff et al., 2022)](https://arxiv.org/abs/2210.07316) — Benchmark padrão da indústria com 56 datasets em 8 tarefas
- [OpenAI Text Embedding Models](https://platform.openai.com/docs/guides/embeddings) — Documentação oficial text-embedding-3 e MRL
- [Sentence Transformers Documentation](https://www.sbert.net/) — Biblioteca open-source para bi-encoders e cross-encoders

---

## Related

- [[transformer-architecture]] — a arquitetura que produz os embeddings via pooling dos hidden states
- [[tokenization]] — tokens são convertidos em embeddings pelo embedding layer antes do transformer
- [[rag-architecture]] — embeddings são o coração do RAG para retrieval semântico
- [[vector-dbs]] — onde os embeddings são armazenados e buscados em produção
- [[kv-cache-attention]] — embeddings de posição vs embeddings de tokens no mecanismo de atenção
- [[vram-estimation]] — vocab_size × d_model define o tamanho da embedding table e impacto em VRAM
