---
tags: [ai-ml, fundamentals, kv-cache, attention, flash-attention, inference]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [KV Cache, Paged Attention, Flash Attention, GQA]
---

# KV Cache e Mecanismos de Atenção

## Overview

O KV cache é o componente mais crítico para eficiência de inferência em LLMs modernos. Durante geração autoregressiva, a atenção entre tokens exigiria recomputar todas as interações a cada passo — custo quadrático O(n²) em tempo e memória. O KV cache elimina essa recomputação armazenando as matrizes Key (K) e Value (V) de todos os tokens anteriores, reduzindo o custo de cada passo de decodificação para O(n) em tempo, mas com custo fixo de VRAM proporcional a `seq_len × batch_size`.

A relação com VRAM e throughput é direta: o KV cache compete com os pesos do modelo pela VRAM disponível. Para batches grandes ou contextos longos, o KV cache pode superar o tamanho dos próprios pesos do modelo. O throughput de inferência (tokens/segundo) é frequentemente limitado não pelos FLOPs disponíveis, mas pela bandwidth de memória necessária para ler o KV cache a cada passo de decodificação — um regime memory-bound.

Integra com [[transformer-architecture]], [[inference-engines]], [[vram-estimation]], [[gpu-architecture]] e [[quantization]].

> [!tip] Prefill vs Decode
> A fase de prefill (processar o prompt inteiro) é compute-bound e rápida. A fase de decode (gerar tokens um a um) é memory-bound e limitada pela bandwidth do KV cache. Separate batching strategies para cada fase (chunked prefill) pode melhorar throughput.

---

## Por Que Apenas K e V São Cacheados

### Mecanismo de Atenção Autoregressiva

Em geração autoregressiva, o modelo gera um token por vez. A cada passo t, o mecanismo de atenção computa:

```
Attention(Q_t, K_{1:t}, V_{1:t}) = softmax(Q_t × K_{1:t}^T / √d_head) × V_{1:t}
```

A Query Q_t representa o token atual sendo gerado — ela muda a cada passo porque o token atual muda. Já K_{1:t} e V_{1:t} contêm as representações de todos os tokens anteriores, que permanecem constantes após serem computados.

**Portanto:**
- Q_{t-1} (passo anterior) não é mais necessário — já foi usado
- K_{1:t-1} e V_{1:t-1} (passo anterior) são necessários novamente no passo t
- K_t e V_t (token atual) são computados uma vez e adicionados ao cache

Sem KV cache, cada passo t exigiria recomputar K e V para todos os t tokens anteriores — custo O(n²) total para gerar n tokens. Com KV cache, cada K e V é computado exatamente uma vez — custo O(n) total para as computações de K e V.

### Implementação Básica do KV Cache

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class MultiHeadAttentionWithCache(nn.Module):
    """
    Multi-head attention com KV cache para geração autoregressiva.
    Demonstra o mecanismo de cache em nível didático.
    """

    def __init__(self, d_model: int, n_heads: int, max_seq_len: int = 2048):
        super().__init__()
        assert d_model % n_heads == 0

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.max_seq_len = max_seq_len

        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

    def forward(
        self,
        x: torch.Tensor,                           # (batch, seq_len, d_model)
        kv_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,  # (K_cache, V_cache)
        use_cache: bool = True,
    ) -> Tuple[torch.Tensor, Optional[Tuple[torch.Tensor, torch.Tensor]]]:
        batch, seq_len, _ = x.shape

        # Projetar Q, K, V
        Q = self.W_q(x)  # (batch, seq_len, d_model)
        K = self.W_k(x)  # (batch, seq_len, d_model)
        V = self.W_v(x)  # (batch, seq_len, d_model)

        # Reshape para múltiplas heads
        def reshape_for_heads(t: torch.Tensor) -> torch.Tensor:
            return t.view(batch, -1, self.n_heads, self.d_head).transpose(1, 2)
            # -> (batch, n_heads, seq_len, d_head)

        Q = reshape_for_heads(Q)
        K = reshape_for_heads(K)
        V = reshape_for_heads(V)

        # Concatenar com cache existente (fase de decode)
        if kv_cache is not None:
            K_cache, V_cache = kv_cache
            K = torch.cat([K_cache, K], dim=2)  # concatena na dimensão seq
            V = torch.cat([V_cache, V], dim=2)

        # Salvar novo cache
        new_cache = (K, V) if use_cache else None

        # Scaled dot-product attention
        scale = self.d_head ** -0.5
        scores = torch.matmul(Q, K.transpose(-2, -1)) * scale
        # scores: (batch, n_heads, seq_len_q, seq_len_kv)

        # Causal mask (necessário apenas no prefill)
        if seq_len > 1:  # fase de prefill
            causal_mask = torch.triu(
                torch.ones(seq_len, K.size(2), device=x.device, dtype=torch.bool),
                diagonal=1
            )
            scores = scores.masked_fill(causal_mask, float('-inf'))

        attn_weights = F.softmax(scores, dim=-1)
        attn_output = torch.matmul(attn_weights, V)
        # -> (batch, n_heads, seq_len, d_head)

        # Merge heads
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch, seq_len, self.d_model)

        output = self.W_o(attn_output)
        return output, new_cache


def demonstrate_kv_cache_benefit():
    """
    Mede o ganho de tempo com vs sem KV cache em geração autoregressiva.
    """
    import time

    d_model, n_heads = 512, 8
    batch_size, prompt_len, gen_len = 1, 128, 50

    model = MultiHeadAttentionWithCache(d_model, n_heads)
    model.eval()

    x_prompt = torch.randn(batch_size, prompt_len, d_model)
    x_new_token = torch.randn(batch_size, 1, d_model)

    # --- SEM cache: recomputar tudo a cada token ---
    start = time.perf_counter()
    with torch.no_grad():
        x_full = x_prompt.clone()
        for i in range(gen_len):
            x_new = torch.randn(batch_size, 1, d_model)
            x_full = torch.cat([x_full, x_new], dim=1)
            _, _ = model(x_full, kv_cache=None, use_cache=False)
    time_no_cache = time.perf_counter() - start

    # --- COM cache: processar apenas token novo ---
    start = time.perf_counter()
    with torch.no_grad():
        _, kv_cache = model(x_prompt, kv_cache=None, use_cache=True)
        for i in range(gen_len):
            x_new = torch.randn(batch_size, 1, d_model)
            _, kv_cache = model(x_new, kv_cache=kv_cache, use_cache=True)
    time_with_cache = time.perf_counter() - start

    speedup = time_no_cache / time_with_cache
    print(f"Sem cache:  {time_no_cache:.3f}s")
    print(f"Com cache:  {time_with_cache:.3f}s")
    print(f"Speedup:    {speedup:.1f}x")


if __name__ == "__main__":
    demonstrate_kv_cache_benefit()
```

---

## VRAM do KV Cache — Fórmula e Exemplos

### Fórmula Geral

```
VRAM_KV = 2 × n_layers × n_kv_heads × d_head × seq_len × batch_size × bytes_per_element
```

Onde o fator **2** representa um tensor K + um tensor V.

| Parâmetro | Significado |
|-----------|------------|
| `n_layers` | Número de camadas transformer |
| `n_kv_heads` | Número de heads KV (pode ser < n_heads com GQA/MQA) |
| `d_head` | Dimensão de cada head = `d_model / n_heads` |
| `seq_len` | Comprimento do contexto (prompt + tokens gerados) |
| `batch_size` | Número de requests simultâneos |
| `bytes_per_element` | 2 para FP16/BF16, 1 para INT8, 4 para FP32 |

### Exemplo Numérico: Llama 3 8B

Configuração do modelo:
- `n_layers = 32`
- `n_heads = 32` (Q heads)
- `n_kv_heads = 8` (GQA — KV heads)
- `d_head = 128` (= 4096 / 32)
- Dtype: FP16 (2 bytes)

**Cálculo para batch=1, seq_len=8192:**
```
VRAM_KV = 2 × 32 × 8 × 128 × 8192 × 1 × 2
        = 2 × 32 × 8 × 128 × 8192 × 2
        = 1.073.741.824 bytes
        ≈ 1 GB
```

**Escalando o batch:**

| batch_size | seq_len | VRAM KV | Observação |
|-----------|---------|---------|------------|
| 1 | 8.192 | ~1 GB | Single request |
| 8 | 8.192 | ~8 GB | Pequeno batch |
| 32 | 8.192 | ~32 GB | Batch médio — supera pesos! |
| 1 | 131.072 | ~16 GB | Contexto longo (128K) |
| 8 | 131.072 | ~128 GB | Contexto longo + batch |

> [!warning] KV Cache Cresce com Batch × Seq Len
> VRAM do KV cache é proporcional a batch_size × seq_len. Dobrar o batch size ou o contexto dobra o KV cache. Em produção, o KV cache frequentemente supera os pesos do modelo em memória para batches grandes.

### Calculadora de VRAM em Python

```python
def calcular_vram_kv_cache(
    n_layers: int,
    n_kv_heads: int,
    d_head: int,
    seq_len: int,
    batch_size: int,
    dtype_bytes: int = 2,  # 2=FP16/BF16, 1=INT8/FP8, 4=FP32
) -> dict:
    """
    Calcula o consumo de VRAM do KV cache.

    Returns:
        dict com bytes, megabytes, gigabytes
    """
    bytes_total = 2 * n_layers * n_kv_heads * d_head * seq_len * batch_size * dtype_bytes
    return {
        "bytes": bytes_total,
        "mb": bytes_total / (1024 ** 2),
        "gb": bytes_total / (1024 ** 3),
    }


# Configurações dos modelos mais populares
MODELOS = {
    "Llama 3 8B": {
        "n_layers": 32, "n_kv_heads": 8, "d_head": 128
    },
    "Llama 3 70B": {
        "n_layers": 80, "n_kv_heads": 8, "d_head": 128
    },
    "Mistral 7B": {
        "n_layers": 32, "n_kv_heads": 8, "d_head": 128
    },
    "GPT-2 Large": {
        "n_layers": 36, "n_kv_heads": 20, "d_head": 64
    },
}

if __name__ == "__main__":
    print(f"{'Modelo':<20} {'batch':<8} {'seq_len':<10} {'VRAM KV':>10}")
    print("-" * 52)

    for nome, cfg in MODELOS.items():
        for batch, seq in [(1, 4096), (8, 4096), (1, 32768)]:
            resultado = calcular_vram_kv_cache(
                seq_len=seq,
                batch_size=batch,
                **cfg,
            )
            print(f"{nome:<20} {batch:<8} {seq:<10} {resultado['gb']:>9.2f}GB")
```

---

## GQA, MQA e MHA — Variantes de Atenção

### Tabela Comparativa

| Variante | Q heads | KV heads | VRAM KV | Qualidade | Modelos |
|---------|---------|---------|---------|----------|---------|
| MHA (Multi-Head) | h | h | baseline | ★★★★★ | GPT-2, BERT, GPT-3 |
| MQA (Multi-Query) | h | 1 | 1/h × baseline | ★★★ | Falcon 7B, PaLM |
| GQA (Grouped-Query) | h | g (1<g<h) | g/h × baseline | ★★★★ | Llama 2/3, Mistral |

### GQA em Detalhe

No GQA, queries são divididas em `g` grupos. Todas as queries de um grupo compartilham o mesmo par KV. Isso reduz o tamanho do KV cache de `h` para `g` vezes sem degradação significativa de qualidade.

**Para Llama 3 8B:** 32 Q heads, 8 KV heads → ratio 4:1.
Economia de VRAM versus MHA: o KV cache é apenas 8/32 = **25% do tamanho do MHA**.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class GroupedQueryAttention(nn.Module):
    """
    Grouped Query Attention (GQA) — implementação de referência.
    Usado em Llama 2, Llama 3, Mistral.
    """

    def __init__(
        self,
        d_model: int,
        n_heads: int,        # Q heads (ex: 32)
        n_kv_heads: int,     # KV heads (ex: 8 para GQA, 1 para MQA)
    ):
        super().__init__()
        assert n_heads % n_kv_heads == 0, "n_heads deve ser divisível por n_kv_heads"

        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.n_rep = n_heads // n_kv_heads  # quantas Q heads por grupo KV
        self.d_head = d_model // n_heads

        self.W_q = nn.Linear(d_model, n_heads * self.d_head, bias=False)
        self.W_k = nn.Linear(d_model, n_kv_heads * self.d_head, bias=False)
        self.W_v = nn.Linear(d_model, n_kv_heads * self.d_head, bias=False)
        self.W_o = nn.Linear(n_heads * self.d_head, d_model, bias=False)

    def forward(
        self,
        x: torch.Tensor,
        kv_cache: tuple = None,
    ) -> tuple:
        batch, seq_len, _ = x.shape

        Q = self.W_q(x).view(batch, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(batch, seq_len, self.n_kv_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(batch, seq_len, self.n_kv_heads, self.d_head).transpose(1, 2)

        if kv_cache is not None:
            K_cache, V_cache = kv_cache
            K = torch.cat([K_cache, K], dim=2)
            V = torch.cat([V_cache, V], dim=2)

        new_cache = (K, V)

        # Expandir KV heads para corresponder a Q heads (sem cópia de memória via expand)
        K_expanded = K.unsqueeze(2).expand(
            batch, self.n_kv_heads, self.n_rep, K.size(2), self.d_head
        ).reshape(batch, self.n_heads, K.size(2), self.d_head)

        V_expanded = V.unsqueeze(2).expand(
            batch, self.n_kv_heads, self.n_rep, V.size(2), self.d_head
        ).reshape(batch, self.n_heads, V.size(2), self.d_head)

        scale = math.sqrt(self.d_head)
        scores = torch.matmul(Q, K_expanded.transpose(-2, -1)) / scale

        attn = F.softmax(scores, dim=-1)
        out = torch.matmul(attn, V_expanded)
        out = out.transpose(1, 2).reshape(batch, seq_len, -1)

        return self.W_o(out), new_cache


def comparar_vram_variantes():
    """Demonstra a diferença de VRAM entre MHA, GQA e MQA."""
    n_layers = 32
    seq_len = 8192
    batch = 1
    d_head = 128
    dtype_bytes = 2  # FP16

    variantes = {
        "MHA (h=32)": 32,
        "GQA (g=8)": 8,
        "MQA (g=1)": 1,
    }

    print(f"\n{'Variante':<20} {'KV Heads':<12} {'VRAM KV':>10}")
    print("-" * 44)

    for nome, n_kv_heads in variantes.items():
        vram_bytes = 2 * n_layers * n_kv_heads * d_head * seq_len * batch * dtype_bytes
        vram_gb = vram_bytes / (1024 ** 3)
        print(f"{nome:<20} {n_kv_heads:<12} {vram_gb:>9.2f}GB")
```

---

## Paged Attention (vLLM)

### O Problema da Fragmentação

Em serving tradicional, cada request aloca um bloco contíguo de VRAM para seu KV cache, dimensionado para o comprimento máximo esperado. Problemas:

1. **Fragmentação interna:** se o request usa menos do que o máximo alocado, a VRAM excedente fica inutilizada
2. **Fragmentação externa:** requests de tamanhos diferentes deixam "buracos" entre alocações
3. **Over-provisioning:** é necessário alocar para o pior caso (seq_len máxima) desde o início

Em workloads reais, 20-40% da VRAM do KV cache pode ser desperdiçada por fragmentação.

### Solução: Paginação como Virtual Memory do OS

Paged Attention (introduzido pelo vLLM) adapta o conceito de virtual memory dos sistemas operacionais:

- **Blocos físicos:** chunks fixos de memória (ex: 16 tokens cada)
- **Tabela de blocos:** mapeia slots "virtuais" de cada request para blocos físicos
- **Alocação sob demanda:** blocos são alocados conforme o request cresce, não antecipadamente

```
Request A (200 tokens): slots virtuais [0,1,...,12] → blocos físicos [3,7,12,...]
Request B (50 tokens):  slots virtuais [0,1,2,3]   → blocos físicos [1,5,...]
```

> [!warning] Paged Attention Tem Overhead Para Sequências Curtas
> Para requests com seq_len < 64 tokens, o overhead de gerenciamento de blocos do paged attention pode superar o benefício. Para latência crítica em sequências curtas, considere um serving simples sem paged attention.

### Copy-on-Write para Beam Search

Beam search gera múltiplos "beams" (hipóteses) em paralelo. Com paged attention, múltiplos beams podem **compartilhar blocos físicos** enquanto seus históricos KV são idênticos — e só fazer uma cópia (copy-on-write) quando um beam diverge.

Isso reduz o consumo de memória do beam search de `n_beams × seq_len` para apenas o número de blocos únicos por beam.

### Configuração vLLM

```python
# Iniciar servidor vLLM com paged attention
# Em linha de comando:
# vllm serve meta-llama/Llama-3-8B-Instruct \
#     --quantization awq \
#     --gpu-memory-utilization 0.9 \
#     --max-model-len 8192 \
#     --block-size 16

# Configuração via Python API
from vllm import LLM, SamplingParams

def criar_servidor_vllm(
    model_path: str = "meta-llama/Llama-3-8B-Instruct",
    gpu_memory_utilization: float = 0.9,
    max_model_len: int = 8192,
    block_size: int = 16,
):
    """
    Inicializa LLM com paged attention.

    Args:
        gpu_memory_utilization: Fração da VRAM reservada para KV cache pool
        max_model_len: Comprimento máximo de sequência suportado
        block_size: Tokens por bloco físico no paged attention
    """
    llm = LLM(
        model=model_path,
        gpu_memory_utilization=gpu_memory_utilization,
        max_model_len=max_model_len,
        block_size=block_size,
        enable_prefix_caching=True,  # cache de prefixos repetidos (system prompts)
    )

    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.9,
        max_tokens=512,
    )

    return llm, sampling_params


def gerar_com_vllm(
    llm: "LLM",
    prompts: list[str],
    sampling_params: "SamplingParams",
) -> list[str]:
    """Geração em batch com vLLM — aproveita paged attention automaticamente."""
    outputs = llm.generate(prompts, sampling_params)
    return [output.outputs[0].text for output in outputs]
```

---

## Sliding Window Attention (Mistral)

### Atenção Local com Janela Deslizante

Para sequências muito longas, a atenção global tem custo O(n²) em memória e tempo. Mistral 7B introduziu Sliding Window Attention (SWA): cada token atende apenas aos W tokens mais recentes.

**Complexidade:** O(n × W) em vez de O(n²)
**Para Mistral:** W = 4096 tokens

Para sequências maiores que W, informação de tokens antigos ainda é propagada indiretamente através das camadas (camada L+1 pode "ver" até W² tokens da perspectiva do input original).

### Sink Tokens e Rolling Buffer

Para sequências muito longas com janela fixa:
- **Sink tokens:** os primeiros tokens (ex: tokens de atenção iniciais) são sempre mantidos no cache, pois recebem atenção desproporcional em qualquer posição
- **Rolling buffer:** o KV cache usa uma estrutura circular — tokens mais antigos (além de W) são sobrescritos

```python
import torch


class SlidingWindowAttention(nn.Module):
    """
    Implementação simplificada de Sliding Window Attention.
    Demonstra o conceito de janela local para sequências longas.
    """

    def __init__(self, d_model: int, n_heads: int, window_size: int = 4096):
        super().__init__()
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.window_size = window_size

        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, seq_len, d_model = x.shape

        Q = self.W_q(x).view(batch, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(batch, seq_len, self.n_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(batch, seq_len, self.n_heads, self.d_head).transpose(1, 2)

        scale = math.sqrt(self.d_head)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / scale

        # Máscara: cada posição i só atende a [i - window_size, ..., i]
        mask = torch.full((seq_len, seq_len), float('-inf'), device=x.device)
        for i in range(seq_len):
            start = max(0, i - self.window_size + 1)
            mask[i, start:i + 1] = 0

        scores = scores + mask.unsqueeze(0).unsqueeze(0)
        attn = F.softmax(scores, dim=-1)
        out = torch.matmul(attn, V)

        out = out.transpose(1, 2).reshape(batch, seq_len, d_model)
        return self.W_o(out)
```

---

## Flash Attention — IO-Awareness

### O Gargalo de Memória da Atenção Padrão

Na atenção padrão, o cálculo envolve:
1. Computar scores S = Q × K^T — resultado: matriz n×n em HBM
2. Aplicar softmax em S — leitura/escrita da matriz n×n
3. Computar output O = softmax(S) × V — leitura da matriz n×n

O problema não é a quantidade de FLOPs — é o **volume de dados movidos entre HBM (High Bandwidth Memory) e SRAM (on-chip)**. A matriz n×n materializada é o gargalo.

Para n=8192 tokens, FP16:
- Tamanho da matriz de atenção: 8192 × 8192 × 2 bytes = **~134 MB por head**
- Com 32 heads: ~4.3 GB apenas para a matriz de atenção
- Movimento de dados: escrever para HBM + ler de volta para softmax = bandwidth desperdiçado

### Flash Attention: Tiles + Online Softmax

Flash Attention (Dao et al., 2022) resolve isso com duas ideias:

1. **Tiling:** divide Q, K, V em blocos (tiles) que cabem na SRAM. Computa a atenção bloco a bloco, nunca materializando a matriz n×n completa em HBM.

2. **Online softmax:** computa o softmax de forma incremental, mantendo apenas o máximo atual e a soma acumulada — permitindo processar tiles sem ver a sequência completa.

**Equivalência matemática:** Flash Attention produz exatamente o mesmo resultado que a atenção padrão, apenas com diferente ordem de operações.

| Implementação | Memória | Speedup (inferência) | Speedup (treino) |
|--------------|---------|---------------------|-----------------|
| Atenção padrão | O(n²) | baseline | baseline |
| Flash Attention 1 | O(n) | 2-4x | 2-6x |
| Flash Attention 2 | O(n) | 3-5x | 3-7x |
| Flash Attention 3 (H100) | O(n) | 4-6x | 5-8x |

### Versões do Flash Attention

**Flash Attention 2** (Dao, 2023):
- Melhor paralelização sobre a dimensão de sequência (não apenas sobre batch e heads)
- Suporte nativo a GQA
- Redução de non-matmul FLOPs

**Flash Attention 3** (Shah et al., H100):
- Suporte a FP8 nativo
- Pipeline overlap entre softmax e matmul usando Tensor Cores do H100
- Warp specialization para overlap de compute e memória

> [!warning] Flash Attention e Suporte a Custom Masking
> Flash Attention (versões antigas) não suportava attention bias arbitrário (ex: ALiBi com versões <2.0). Verifique compatibilidade antes de combinar positional encoding customizado com Flash Attention.

### Habilitando Flash Attention no HuggingFace Transformers

```python
# Requer: pip install flash-attn --no-build-isolation
# Requer: GPU Ampere+ (A100, H100, RTX 30/40 series)

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import time


def carregar_modelo_com_flash_attention(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
    use_flash_attention: bool = True,
):
    """
    Carrega modelo com ou sem Flash Attention para comparação.
    """
    attn_implementation = "flash_attention_2" if use_flash_attention else "eager"

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,  # Flash Attention requer BF16 ou FP16
        device_map="auto",
        attn_implementation=attn_implementation,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer


def benchmark_flash_attention(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
    prompt: str = "Explique o funcionamento de transformers em detalhes técnicos:",
    max_new_tokens: int = 200,
    n_runs: int = 3,
):
    """
    Compara latência com e sem Flash Attention.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    resultados = {}

    for use_fa in [False, True]:
        label = "Flash Attention 2" if use_fa else "Atenção Padrão"
        model, _ = carregar_modelo_com_flash_attention(model_name, use_fa)
        model.eval()

        tempos = []
        for _ in range(n_runs):
            torch.cuda.synchronize()
            start = time.perf_counter()

            with torch.no_grad():
                output = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                )

            torch.cuda.synchronize()
            elapsed = time.perf_counter() - start
            n_tokens = output.shape[1] - inputs["input_ids"].shape[1]
            tempos.append(n_tokens / elapsed)

        resultados[label] = {
            "tokens_per_sec": sum(tempos) / len(tempos),
            "latency_s": 1 / (sum(tempos) / len(tempos)),
        }

        del model
        torch.cuda.empty_cache()

    print(f"\n{'Implementação':<25} {'Tokens/s':>12} {'Latência/tok (ms)':>20}")
    print("-" * 60)
    for label, r in resultados.items():
        print(
            f"{label:<25} {r['tokens_per_sec']:>12.1f} "
            f"{r['latency_s'] * 1000:>20.2f}"
        )

    if len(resultados) == 2:
        vals = list(resultados.values())
        speedup = vals[1]["tokens_per_sec"] / vals[0]["tokens_per_sec"]
        print(f"\nSpeedup Flash Attention: {speedup:.2f}x")


def medir_vram_kv_cache_runtime(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
    seq_len: int = 4096,
):
    """
    Mede o tamanho real do KV cache em runtime com HuggingFace.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.eval()

    # Texto de placeholder para preencher seq_len tokens
    tokens = torch.randint(100, 32000, (1, seq_len)).to("cuda")

    torch.cuda.reset_peak_memory_stats()
    vram_antes = torch.cuda.memory_allocated() / (1024 ** 3)

    with torch.no_grad():
        outputs = model(tokens, use_cache=True)
        past_kv = outputs.past_key_values

    vram_depois = torch.cuda.memory_allocated() / (1024 ** 3)

    # Calcular tamanho exato do KV cache
    kv_bytes = sum(
        k.element_size() * k.numel() + v.element_size() * v.numel()
        for k, v in past_kv
    )

    print(f"Modelo: {model_name}")
    print(f"Seq len: {seq_len} tokens")
    print(f"VRAM antes: {vram_antes:.2f} GB")
    print(f"VRAM depois: {vram_depois:.2f} GB")
    print(f"KV cache exato: {kv_bytes / (1024**3):.4f} GB")
    print(f"Camadas: {len(past_kv)}, Shape K[0]: {past_kv[0][0].shape}")
```

---

## Referências

- Flash Attention — [arxiv:2205.14135](https://arxiv.org/abs/2205.14135)
- Flash Attention 2 — [arxiv:2307.08691](https://arxiv.org/abs/2307.08691)
- Paged Attention / vLLM — [arxiv:2309.06180](https://arxiv.org/abs/2309.06180)
- GQA (Grouped Query Attention) — [arxiv:2305.13245](https://arxiv.org/abs/2305.13245)
- Mistral 7B (Sliding Window Attention) — [arxiv:2310.06825](https://arxiv.org/abs/2310.06825)

---

## Related

- [[transformer-architecture]] — arquitetura base onde KV cache é aplicado
- [[inference-engines]] — vLLM, TensorRT-LLM e outros engines que implementam paged attention
- [[vram-estimation]] — estimativa de VRAM total incluindo pesos + KV cache + ativações
- [[gpu-architecture]] — HBM bandwidth e SRAM que determinam speedup do Flash Attention
- [[quantization]] — quantizar KV cache (FP8/INT8) para reduzir ainda mais o consumo de VRAM
