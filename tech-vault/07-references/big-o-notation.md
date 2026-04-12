---
tags: [reference, algorithms]
status: active
level: advanced
updated: 2026-04-05
aliases: [Big O, Big O Notation, Complexidade]
created: 2026-04-05
---

# Big O Notation

Referência de complexidades de tempo e espaço para estruturas de dados e algoritmos. Essencial para decisões de [[database-optimization]] e escrita de código eficiente em [[python]] e [[rust]]. Relacionado a padrões de regex em [[regex-cheatsheet]] e estruturas de dados em [[git-cheatsheet]].

---

## Hierarquia de Complexidades

| Notação | Nome | n=10 | n=100 | n=1.000 | n=1.000.000 |
|---------|------|------|-------|---------|-------------|
| O(1) | Constante | 1 | 1 | 1 | 1 |
| O(log n) | Logarítmica | 3 | 7 | 10 | 20 |
| O(n) | Linear | 10 | 100 | 1.000 | 1.000.000 |
| O(n log n) | Linearítmica | 33 | 664 | 9.966 | ~20.000.000 |
| O(n²) | Quadrática | 100 | 10.000 | 1.000.000 | 10¹² |
| O(n³) | Cúbica | 1.000 | 1.000.000 | 10⁹ | 10¹⁸ |
| O(2ⁿ) | Exponencial | 1.024 | ~10³⁰ | impossível | impossível |
| O(n!) | Fatorial | 3.628.800 | impossível | impossível | impossível |

> [!important] Crescimento Assintótico
> Big O descreve o comportamento para **n grande**. Para n pequeno (< 50), constantes e coeficientes importam mais do que a classe de complexidade.

---

## Algoritmos de Ordenação

| Algoritmo | Melhor | Médio | Pior | Espaço | Estável |
|-----------|--------|-------|------|--------|---------|
| **Bubble Sort** | O(n) | O(n²) | O(n²) | O(1) | Sim |
| **Selection Sort** | O(n²) | O(n²) | O(n²) | O(1) | Não |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | Sim |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Sim |
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | Não |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | Não |
| **Tim Sort** | O(n) | O(n log n) | O(n log n) | O(n) | Sim |
| **Radix Sort** | O(nk) | O(nk) | O(nk) | O(n+k) | Sim |
| **Counting Sort** | O(n+k) | O(n+k) | O(n+k) | O(k) | Sim |

> [!info] Tim Sort
> Python (`list.sort()`) e Java usam **Tim Sort**, uma variação híbrida de Merge + Insertion Sort. É O(n) para arrays quase-ordenados e O(n log n) no pior caso.

---

## Algoritmos de Busca

| Algoritmo | Melhor | Médio | Pior | Espaço | Requisito |
|-----------|--------|-------|------|--------|-----------|
| **Linear Search** | O(1) | O(n) | O(n) | O(1) | Nenhum |
| **Binary Search** | O(1) | O(log n) | O(log n) | O(1) | Array ordenado |
| **Jump Search** | O(1) | O(√n) | O(√n) | O(1) | Array ordenado |
| **Interpolation Search** | O(1) | O(log log n) | O(n) | O(1) | Distribuição uniforme |
| **Hash Lookup** | O(1) | O(1) | O(n) | O(n) | Hash table |

---

## Algoritmos de Grafos

| Algoritmo | Tempo | Espaço | Uso Principal |
|-----------|-------|--------|---------------|
| **BFS** | O(V + E) | O(V) | Caminho mais curto (não ponderado) |
| **DFS** | O(V + E) | O(V) | Componentes conexos, topological sort |
| **Dijkstra** | O((V + E) log V) | O(V) | Caminho mínimo (pesos positivos) |
| **Bellman-Ford** | O(V · E) | O(V) | Caminho mínimo (pesos negativos) |
| **Floyd-Warshall** | O(V³) | O(V²) | Todos os pares mais curtos |
| **Kruskal** | O(E log E) | O(V) | Árvore geradora mínima |
| **Prim** | O((V + E) log V) | O(V) | Árvore geradora mínima |
| **A*** | O(E) | O(V) | Busca heurística em grafos |

> [!note] V = Vértices, E = Arestas
> Para grafos densos (E ≈ V²), algoritmos O(V²) podem superar O(E log V) na prática devido a menor overhead de memória.

---

## Operações em Estruturas de Dados

### Arrays e Listas

| Estrutura | Acesso | Busca | Inserção | Deleção | Espaço |
|-----------|--------|-------|----------|---------|--------|
| **Array** | O(1) | O(n) | O(n) | O(n) | O(n) |
| **Dynamic Array** (list) | O(1) | O(n) | O(1)* | O(n) | O(n) |
| **Linked List** | O(n) | O(n) | O(1) | O(1)** | O(n) |
| **Doubly Linked List** | O(n) | O(n) | O(1) | O(1)** | O(n) |

\* Amortizado | \*\* Se o nó é conhecido

### Árvores

| Estrutura | Acesso | Busca | Inserção | Deleção | Espaço |
|-----------|--------|-------|----------|---------|--------|
| **BST** (balanceada) | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **BST** (degenerada) | O(n) | O(n) | O(n) | O(n) | O(n) |
| **AVL Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **Red-Black Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **B-Tree** | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| **Trie** | O(k) | O(k) | O(k) | O(k) | O(n·k) |

> [!info] B-Tree em Bancos de Dados
> PostgreSQL usa **B-Tree** para índices padrão — O(log n) para busca, inserção e deleção. Relevante para [[database-optimization]].

### Hash Tables, Heaps e Outros

| Estrutura | Operação | Melhor/Médio | Pior | Espaço |
|-----------|----------|--------------|------|--------|
| **Hash Table** | Busca/Insert/Delete | O(1) | O(n) | O(n) |
| **Min/Max Heap** | Insert | O(log n) | O(log n) | O(n) |
| **Min/Max Heap** | Peek | O(1) | O(1) | — |
| **Min/Max Heap** | Extract min/max | O(log n) | O(log n) | — |
| **Stack** | Push/Pop/Peek | O(1) | O(1) | O(n) |
| **Queue** | Enqueue/Dequeue | O(1) | O(1) | O(n) |
| **Deque** | Todas as operações | O(1) | O(1) | O(n) |

---

## Análise Amortizada

A análise amortizada distribui o custo de operações caras ao longo de várias operações baratas.

| Estrutura | Operação | Custo Pior Caso | Custo Amortizado |
|-----------|----------|-----------------|------------------|
| Dynamic Array (append) | Push | O(n) (resize) | **O(1)** |
| Hash Table | Insert | O(n) (rehash) | **O(1)** |
| Splay Tree | Any | O(n) | **O(log n)** |
| Fibonacci Heap | Decrease key | O(log n) | **O(1)** |

```python
# Demonstração: Dynamic Array cresce por fator 2
# - n/2 operações após último resize são O(1)
# - 1 operação de resize é O(n)
# - Custo total: O(n) para n operações → O(1) amortizado

class DynamicArray:
    def __init__(self):
        self._data = [None] * 1
        self._size = 0

    def append(self, item):
        if self._size == len(self._data):           # O(n) raramente
            self._resize(2 * len(self._data))
        self._data[self._size] = item               # O(1) frequentemente
        self._size += 1

    def _resize(self, new_cap: int):
        old = self._data
        self._data = [None] * new_cap
        for i in range(self._size):
            self._data[i] = old[i]
```

---

## Quando O(n²) Vence O(n log n)

> [!important] Constantes Importam para n Pequeno
> Big O ignora constantes, mas na prática elas importam:

| Cenário | Recomendação | Motivo |
|---------|-------------|--------|
| n < 10 | Qualquer algoritmo | Diferença é negligenciável |
| n < 50 | Insertion Sort | Cache-friendly, sem overhead |
| Array quase ordenado | Insertion Sort ou Tim Sort | O(n) no melhor caso |
| Array pequeno em recursão | Insertion Sort | Evita overhead de pilha |
| Strings curtas em hash map | Busca linear em lista | Sem custo de hashing |
| Multiplicação de matrizes pequenas | O(n³) direto | Strassen O(n^2.8) tem overhead alto |

```python
# Python usa Insertion Sort para subproblemas pequenos em Tim Sort
# CPython: threshold é ~64 elementos

# Exemplo: binary search vs linear search para n pequeno
import timeit

data = list(range(20))  # n = 20

# Linear O(n): mais rápido em n pequeno por ser cache-local
linear = timeit.timeit(lambda: 15 in data, number=100_000)

# Binary O(log n): overhead de função e divisão
import bisect
binary = timeit.timeit(lambda: bisect.bisect_left(data, 15), number=100_000)

# Para n=20, linear pode ser comparável ou mais rápido
print(f"Linear: {linear:.4f}s | Binary: {binary:.4f}s")
```

---

## Complexidade de Algoritmos Comuns em Python

| Operação | Estrutura | Complexidade |
|----------|-----------|--------------|
| `x in list` | list | O(n) |
| `x in set` | set | O(1) avg |
| `list.append()` | list | O(1) amort. |
| `list.insert(0, x)` | list | O(n) |
| `list.sort()` | list | O(n log n) |
| `dict[key]` | dict | O(1) avg |
| `heapq.heappush` | heap | O(log n) |
| `collections.deque.append` | deque | O(1) |
| `sorted(iterable)` | any | O(n log n) |
| `str + str` em loop | str | O(n²) total |
| `"".join(list)` | str | O(n) |

> [!warning] Concatenação de Strings em Loop
> `s += chunk` em um loop Python é O(n²) total. Use `"".join(parts)` ou `io.StringIO` — O(n).

---

## Implicações Práticas

```python
# RUIM: O(n²) — busca em lista
def find_duplicates_slow(items: list) -> list:
    dupes = []
    for i, x in enumerate(items):
        if x in items[i+1:]:  # O(n) por iteração
            dupes.append(x)
    return dupes

# BOM: O(n) — busca em set
from collections import Counter

def find_duplicates_fast(items: list) -> list:
    return [x for x, count in Counter(items).items() if count > 1]

# RUIM: O(n log n) desnecessário para "existe em conjunto"
def has_common_slow(a: list, b: list) -> bool:
    return len(set(a) & set(b)) > 0  # O(n + m) mas cria set completo

# BOM: O(n) com early exit
def has_common_fast(a: list, b: list) -> bool:
    s = set(a)
    return any(x in s for x in b)  # para no primeiro match
```

---

> [!info] Ferramentas de Análise
> - `timeit` — medir tempo de execução em Python
> - `cProfile` / `py-spy` — profiling de CPU
> - `tracemalloc` — análise de memória
> - `EXPLAIN ANALYZE` no PostgreSQL — complexidade de queries (ver [[database-optimization]])

> [!info] Ver também
> - Otimização de queries de banco: [[database-optimization]]
> - Implementações em Python: [[python]]
> - Implementações performáticas em sistemas: [[rust]]
> - Padrões de regex e sua complexidade: [[regex-cheatsheet]]
