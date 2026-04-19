---
tags: [ai-ml, fundamentals, vram, memory, hardware-planning]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [VRAM Estimation, GPU Memory Planning, Model Memory Calculator]
---

# VRAM Estimation — Guia de Referência

## Overview

Antes de comprar hardware, provisionar instâncias de nuvem ou iniciar um experimento de fine-tuning, a pergunta mais fundamental é: **esse modelo cabe na memória disponível?** Responder errado gera dois tipos de custo: comprar hardware insuficiente (OOM em produção) ou superestimar e pagar por memória que não usa.

Este guia cobre as fórmulas exatas, regras rápidas e exemplos práticos com cálculos numéricos para os casos mais comuns: inferência, QLoRA fine-tuning e pré-treinamento completo.

### Regras Rápidas

Para planejamento inicial rápido (precisão ±20%):

```
VRAM_inferência    ≈ params × bytes_dtype × 1.2
VRAM_QLoRA         ≈ params × 0.5 bytes + 8 a 12 GB overhead
VRAM_full_training ≈ params × 16 bytes  (regra do 16x com Adam)
```

Onde `params` está em bilhões e o resultado é em GB — ex: Llama 3 8B em BF16:
`8 × 2 × 1.2 = 19.2 GB`.

---

## Bytes por Dtype

A quantidade de memória por parâmetro depende diretamente do tipo de dado:

| Dtype | Bytes/param | Uso típico | Precisão relativa |
|-------|------------|-----------|------------------|
| FP32 | 4 bytes | Master weights em treino, gradients | Máxima |
| BF16 | 2 bytes | Treinamento moderno, inferência | Alta (range amplo) |
| FP16 | 2 bytes | Inferência, treino legado | Alta (range menor) |
| FP8 (E4M3/E5M2) | 1 byte | Treino H100, inferência agressiva | Boa |
| INT8 | 1 byte | Quantização pós-treino | Moderada |
| INT4 / NF4 | 0.5 bytes | QLoRA, GGUF Q4, produção edge | Aceitável |
| INT2 | 0.25 bytes | Experimental | Baixa |

**BF16 vs FP16:** Mesmos 2 bytes, mas BF16 tem range dinâmico equivalente ao FP32 (8 bits de expoente vs 5 do FP16). BF16 não satura em gradients grandes — por isso substituiu FP16 em treinamento desde Ampere.

---

## Fórmulas Detalhadas

### Inferência

Durante inferência, a VRAM é consumida por quatro componentes:

```
VRAM_pesos      = N_params × bytes_dtype
VRAM_kv_cache   = 2 × n_layers × n_kv_heads × d_head × seq_len × batch × bytes_dtype
VRAM_ativações  ≈ batch × seq_len × d_model × 4 bytes
VRAM_overhead   ≈ 500 MB a 1 GB (CUDA context, bibliotecas, buffers)
VRAM_total      = soma de todos os componentes
```

**Detalhamento do KV cache:**

O fator `2` representa Key e Value (não há cache para Query). Para modelos com GQA (Grouped Query Attention), `n_kv_heads` é menor que `n_attention_heads`:

- MHA (Multi-Head Attention): `n_kv_heads = n_attention_heads`
- GQA (Grouped Query Attention): `n_kv_heads < n_attention_heads` — ex: Llama 3 8B tem 32 attention heads mas apenas 8 KV heads
- MQA (Multi-Query Attention): `n_kv_heads = 1`

GQA reduz o KV cache em proporção direta. Um modelo com 32 attention heads e 8 KV heads usa 4x menos KV cache que um modelo MHA equivalente.

### Full Fine-Tuning com Adam

Adam requer manter 5 cópias dos parâmetros em memória simultânea:

```
Componente              Dtype       Bytes/param
─────────────────────────────────────────────
Master weights          FP32        4
Pesos ativos            BF16        2
Gradients               FP32        4
Adam momentum (m)       FP32        4
Adam variance (v)       FP32        4
─────────────────────────────────────────────
Total                               18 bytes/param
```

A "regra do 16x" é uma aproximação conservadora que arredonda para baixo e assume uso de gradient checkpointing:

```
VRAM_full_finetuning ≈ N_params × 16 bytes
```

Sem gradient checkpointing, ativações adicionam substancialmente (ver Exemplo 4).

### QLoRA

QLoRA (Quantized LoRA) congela o modelo base em INT4/NF4 e treina apenas os adaptadores LoRA em BF16:

```
VRAM_base       = N_base × 0.5 bytes         (INT4/NF4 — congelado)
VRAM_lora       = N_lora × 2 bytes           (adaptadores BF16)
VRAM_adam_lora  = N_lora × 8 bytes           (Adam m + v em FP32)
VRAM_ativações  = f(seq_len, batch, grad_checkpoint)
VRAM_overhead   ≈ 500 MB
```

**N_lora** é muito menor que N_base. Para rank r=16 com 4 projections (q_proj, v_proj, k_proj, o_proj) por camada, e um modelo de 32 camadas com d_model=4096:

```
N_lora por camada ≈ 4 × (d_model × r + r × d_model) = 4 × 2 × 4096 × 16 = 524.288 params
N_lora total (32 camadas) ≈ 16.7M params ≈ 0.2% do modelo base
```

**Ativações com gradient checkpointing:** Armazena apenas checkpoints intermediários, recomputando ativações durante o backward pass. Reduz memória de ativações em 8-10x ao custo de ~30-40% mais compute.

---

## 4 Exemplos Práticos com Cálculos Numéricos

### Exemplo 1 — Llama 3 8B em BF16, Inferência

**Configuração:** batch=1, seq_len=4096, BF16
**Arquitetura Llama 3 8B:** 32 layers, 32 attention heads, 8 KV heads (GQA), d_head=128, d_model=4096

```
Pesos:
  N_params = 8.03 × 10⁹
  VRAM_pesos = 8.03e9 × 2 bytes = 16.06 GB

KV Cache:
  VRAM_kv = 2 × 32 layers × 8 kv_heads × 128 d_head × 4096 seq_len × 1 batch × 2 bytes
  VRAM_kv = 2 × 32 × 8 × 128 × 4096 × 2 = 1.07 GB

Ativações:
  VRAM_ativ ≈ 1 × 4096 × 4096 × 4 = 67 MB ≈ 0.07 GB
  (pequeno pois batch=1)

Overhead:
  VRAM_overhead ≈ 0.5 GB

─────────────────────────────────
TOTAL ≈ 16.06 + 1.07 + 0.07 + 0.5 = 17.7 GB
Arredondando com buffer 5%: ~18.4 GB
```

**Conclusão: cabe em RTX 4090 (24 GB) com folga para batch maior.**

### Exemplo 2 — Llama 3 70B em Q4_K_M, Inferência

**Configuração:** batch=1, seq_len=4096, Q4_K_M (~0.55 bytes efetivos com overhead de escala)
**Arquitetura Llama 3 70B:** 80 layers, 64 attention heads, 8 KV heads (GQA), d_head=128, d_model=8192

```
Pesos (Q4_K_M tem overhead de escala ~10% vs INT4 puro):
  N_params = 70.6 × 10⁹
  VRAM_pesos = 70.6e9 × 0.5 × 1.10 = 38.8 GB

KV Cache:
  VRAM_kv = 2 × 80 × 8 × 128 × 4096 × 1 × 2 bytes
  VRAM_kv = 2 × 80 × 8 × 128 × 4096 × 2 = 2.68 GB

Ativações:
  VRAM_ativ ≈ 1 × 4096 × 8192 × 4 = 134 MB ≈ 0.13 GB

Overhead:
  VRAM_overhead ≈ 0.5 GB

─────────────────────────────────
TOTAL ≈ 38.8 + 2.68 + 0.13 + 0.5 = 42.1 GB
```

**Conclusão: não cabe em 1× RTX 4090 (24 GB). Cabe em 2× RTX 4090 (48 GB) via llama.cpp com tensor parallelism, ou em 1× A100 80 GB.**

### Exemplo 3 — QLoRA Mistral 7B em 1× RTX 4090

**Configuração:** seq_len=2048, batch=4, gradient checkpointing ativo
**Arquitetura Mistral 7B:** 32 layers, 32 attention heads, 8 KV heads, d_head=128, d_model=4096
**LoRA config:** r=16, 4 projections (q, k, v, o), todos os 32 layers

```
Base model INT4/NF4:
  N_base = 7.24 × 10⁹
  VRAM_base = 7.24e9 × 0.5 bytes = 3.62 GB

LoRA weights BF16:
  N_lora = 32 layers × 4 proj × 2 × 4096 × 16 = 16,777,216 ≈ 16.8M params
  VRAM_lora = 16.8e6 × 2 bytes = 33.6 MB ≈ 0.03 GB

Adam states (FP32) para LoRA:
  VRAM_adam = 16.8e6 × 8 bytes = 134 MB ≈ 0.13 GB

Ativações com gradient checkpointing:
  Sem checkpointing: batch × seq_len × d_model × n_layers × 4 bytes
    = 4 × 2048 × 4096 × 32 × 4 = 4.29 GB (por checkpoint de layer)
  Com checkpointing (raiz quadrada de layers ≈ 6 checkpoints):
    VRAM_ativ ≈ 4.29 / 5.3 ≈ 0.81 GB
  Mas batchnorm + misc buffers: total ~2.5 GB empiricamente

4-bit dequant buffers temporários:
  VRAM_dequant ≈ 1.0 GB

Overhead:
  VRAM_overhead ≈ 0.5 GB

─────────────────────────────────
TOTAL ≈ 3.62 + 0.03 + 0.13 + 2.50 + 1.00 + 0.50 = 7.78 GB
Com margem de segurança (fragmentação, picos): ~10-13 GB
```

**Conclusão: viável em RTX 4090 (24 GB) com folga significativa. Dá para aumentar batch para 8 ou seq_len para 4096.**

### Exemplo 4 — Pré-treino Llama 3 8B em 8× H100

**Configuração:** BF16 + FP32 master weights, Adam, gradient checkpointing, ZeRO-3
**Objetivo:** Estimar VRAM total antes de sharding com ZeRO-3

```
Pesos master (FP32):
  VRAM = 8.03e9 × 4 bytes = 32.12 GB

Pesos ativos (BF16):
  VRAM = 8.03e9 × 2 bytes = 16.06 GB

Gradients (FP32):
  VRAM = 8.03e9 × 4 bytes = 32.12 GB

Adam momentum m (FP32):
  VRAM = 8.03e9 × 4 bytes = 32.12 GB

Adam variance v (FP32):
  VRAM = 8.03e9 × 4 bytes = 32.12 GB

Subtotal optimizer state: 144.54 GB

Ativações com gradient checkpointing:
  Batch global = 256 (micro_batch=8 × 8 GPUs × gradient_accum=4)
  Por micro-step: 8 × 4096 × 4096 × 32 layers × 4 bytes = 17.18 GB
  Com checkpointing (redução ~8x): ~2.15 GB por GPU

Overhead (NCCL buffers, CUDA context):
  VRAM_overhead ≈ 2 GB por GPU

─────────────────────────────────
TOTAL sem ZeRO: ~147 GB → não cabe em 1 GPU (80 GB)
Com ZeRO-3 (particiona tudo entre 8 GPUs):
  VRAM por GPU = (144.54 / 8) + 2.15 + 2.0 = 18.07 + 2.15 + 2.0 ≈ 22.2 GB
```

**Conclusão: com ZeRO-3, cada H100 usa ~22-30 GB (folga para batch maior). Treinamento completo viável em 8× H100 SXM (80 GB cada).**

---

## Tabela de Referência Rápida

| Modelo | Params | BF16 | INT8 | Q4_K_M | Hardware mín. (inferência) |
|--------|--------|------|------|--------|---------------------------|
| Phi-3 mini | 3.8B | 7.6 GB | 3.8 GB | 2.1 GB | RTX 3060 12 GB |
| Llama 3 8B | 8B | 16 GB | 8 GB | 4.8 GB | RTX 3080 10 GB |
| Mistral 7B | 7B | 14 GB | 7 GB | 4.3 GB | RTX 3080 10 GB |
| Gemma 2 9B | 9B | 18 GB | 9 GB | 5.4 GB | RTX 3090 24 GB |
| Llama 3 70B | 70B | 140 GB | 70 GB | 38.5 GB | 2× A100 80 GB |
| Llama 3 405B | 405B | 810 GB | 405 GB | 220 GB | 8× H100 80 GB |
| Mixtral 8×7B | ~47B ativo | 94 GB | 47 GB | 26 GB | 2× RTX 4090 |
| Qwen 2.5 72B | 72B | 144 GB | 72 GB | 40 GB | 2× A100 80 GB |

**Nota:** Valores de hardware mínimo assumem batch=1, seq_len≤4096, e que cabe com ~10% de margem. Para produção, adicionar 20% de buffer.

---

> [!warning] nvidia-smi Inclui Overhead do Driver
> O valor exibido pelo `nvidia-smi` inclui o contexto CUDA (~500 MB a 1 GB) e buffers de bibliotecas como cuDNN e NCCL. Para medir o uso real do modelo, use `torch.cuda.memory_allocated()` (memória alocada pelo modelo) ou `torch.cuda.memory_reserved()` (pool reservado pelo PyTorch, inclui fragmentação).

> [!warning] Pesos Quantizados em Disco ≠ VRAM em Runtime
> Um arquivo GGUF Q4 de 5 GB no disco pode exigir 7-9 GB de VRAM durante carregamento — buffers temporários de dequantização, tensores de escala e a estrutura do modelo em memória têm overhead além dos pesos brutos. Sempre teste empiricamente com `torch.cuda.memory_allocated()` após `model.cuda()`.

> [!warning] Gradient Checkpointing Troca Memória por Compute
> Com gradient checkpointing ativo, o PyTorch descarta ativações intermediárias durante o forward pass e as recomputa durante o backward. Isso reduz a VRAM de ativações em aproximadamente 8-10x, mas aumenta o tempo de treino em 30-40% (cada layer é computado duas vezes). Ative com `model.gradient_checkpointing_enable()` antes de treinar.

> [!tip] Reserve 15-20% de Buffer
> As fórmulas acima são aproximações baseadas em arquitetura. Fragmentação de memória, variações de batch, compilações JIT e picos durante backward pass causam OOM inesperado mesmo com estimativas corretas. Planeje para usar no máximo 80-85% da VRAM disponível.

> [!info] VRAM Unificada no Apple Silicon
> Mac Studio M3 Ultra com 192 GB e Mac Studio M4 Ultra com 192 GB podem usar toda essa memória para LLMs — CPU, GPU e Neural Engine acessam o mesmo pool. Um Llama 3 70B em Q4 (38 GB) cabe facilmente com espaço para context window grande. Equivalente a ter 192 GB de "VRAM" por um preço acessível vs. múltiplos H100s.

---

## Código Prático

### 1. Calcular VRAM de Qualquer Modelo HuggingFace Automaticamente

```python
from transformers import AutoConfig
from typing import Optional
import math

def estimate_vram(
    model_name: str,
    dtype: str = "bf16",
    batch_size: int = 1,
    seq_len: int = 4096,
    mode: str = "inference",  # "inference", "qlora", "full_finetune"
    lora_rank: int = 16,
    lora_target_modules: int = 4,  # q, k, v, o projections
    gradient_checkpointing: bool = True,
) -> dict:
    """
    Estima VRAM necessária para um modelo HuggingFace.

    Lê a configuração do modelo (sem baixar os pesos) e aplica
    as fórmulas analíticas para cada componente de memória.

    Args:
        model_name: Nome do modelo no HuggingFace Hub
        dtype: Tipo de dado — "fp32", "fp16", "bf16", "int8", "int4"
        batch_size: Tamanho do batch
        seq_len: Comprimento máximo de sequência
        mode: Cenário de uso
        lora_rank: Rank dos adaptadores LoRA (apenas para "qlora")
        lora_target_modules: Número de projections alvo do LoRA
        gradient_checkpointing: Se gradient checkpointing está ativo

    Returns:
        dict com VRAM por componente e total, tudo em GB
    """
    # Mapeamento de dtype para bytes por parâmetro
    BYTES_PER_PARAM = {
        "fp32": 4.0,
        "fp16": 2.0,
        "bf16": 2.0,
        "fp8": 1.0,
        "int8": 1.0,
        "int4": 0.5,
        "nf4": 0.5,
    }

    bytes_per_param = BYTES_PER_PARAM.get(dtype.lower())
    if bytes_per_param is None:
        raise ValueError(f"dtype '{dtype}' não reconhecido. Use: {list(BYTES_PER_PARAM.keys())}")

    # Carregar config sem baixar pesos
    print(f"Carregando configuração de {model_name}...")
    config = AutoConfig.from_pretrained(model_name)

    # Extrair parâmetros de arquitetura
    # Diferentes modelos usam nomes diferentes para os mesmos campos
    n_params = getattr(config, 'num_parameters', None)

    # Estimar n_params a partir da arquitetura se não disponível diretamente
    n_layers = getattr(config, 'num_hidden_layers', 32)
    d_model = getattr(config, 'hidden_size', 4096)
    n_heads = getattr(config, 'num_attention_heads', 32)
    n_kv_heads = getattr(config, 'num_key_value_heads', n_heads)  # GQA ou MHA
    d_head = d_model // n_heads
    intermediate_size = getattr(config, 'intermediate_size', d_model * 4)
    vocab_size = getattr(config, 'vocab_size', 32000)

    # Calcular número total de parâmetros
    # Embedding: vocab_size × d_model
    params_embed = vocab_size * d_model

    # Attention por layer: Q + K + V + O projections
    params_attn_per_layer = (
        d_model * n_heads * d_head +           # Q
        d_model * n_kv_heads * d_head +        # K (GQA: menor)
        d_model * n_kv_heads * d_head +        # V (GQA: menor)
        n_heads * d_head * d_model             # O
    )

    # FFN por layer (assume SwiGLU: 3 projections × intermediate_size)
    params_ffn_per_layer = 3 * d_model * intermediate_size

    # LayerNorm por layer (~negligível)
    params_ln_per_layer = 4 * d_model

    params_per_layer = params_attn_per_layer + params_ffn_per_layer + params_ln_per_layer
    n_total_params = params_embed + n_layers * params_per_layer + d_model  # +LM head norm

    n_params_billions = n_total_params / 1e9

    print(f"Modelo: {model_name}")
    print(f"Parâmetros estimados: {n_params_billions:.2f}B")
    print(f"Layers: {n_layers}, d_model: {d_model}, KV heads: {n_kv_heads}/{n_heads}")

    result = {
        "model": model_name,
        "params_billions": n_params_billions,
        "dtype": dtype,
        "mode": mode,
        "config": {
            "n_layers": n_layers,
            "d_model": d_model,
            "n_heads": n_heads,
            "n_kv_heads": n_kv_heads,
            "d_head": d_head,
        },
        "vram_gb": {}
    }

    if mode == "inference":
        # Pesos
        vram_weights = n_total_params * bytes_per_param / 1e9

        # KV cache: 2 × layers × kv_heads × d_head × seq × batch × bytes
        vram_kv = (2 * n_layers * n_kv_heads * d_head * seq_len * batch_size * bytes_per_param) / 1e9

        # Ativações
        vram_activations = (batch_size * seq_len * d_model * 4) / 1e9  # FP32

        # Overhead
        vram_overhead = 0.75  # GB

        vram_total = vram_weights + vram_kv + vram_activations + vram_overhead

        result["vram_gb"] = {
            "weights": round(vram_weights, 2),
            "kv_cache": round(vram_kv, 2),
            "activations": round(vram_activations, 2),
            "overhead": vram_overhead,
            "total": round(vram_total, 2),
            "recommended_with_buffer": round(vram_total * 1.2, 2),
        }

    elif mode == "qlora":
        # Base model em INT4
        vram_base = n_total_params * 0.5 / 1e9

        # LoRA params (muito pequeno)
        n_lora_params = n_layers * lora_target_modules * 2 * d_model * lora_rank
        vram_lora = n_lora_params * 2 / 1e9  # BF16

        # Adam states para LoRA (FP32: 2 × 4 bytes)
        vram_adam = n_lora_params * 8 / 1e9

        # Ativações
        base_activations = batch_size * seq_len * d_model * n_layers * 4 / 1e9
        if gradient_checkpointing:
            vram_activations = base_activations / 8  # aproximação
        else:
            vram_activations = base_activations

        # Dequant buffers
        vram_dequant = 1.0  # GB empírico

        vram_overhead = 0.75

        vram_total = vram_base + vram_lora + vram_adam + vram_activations + vram_dequant + vram_overhead

        result["vram_gb"] = {
            "base_int4": round(vram_base, 2),
            "lora_bf16": round(vram_lora, 3),
            "adam_states": round(vram_adam, 3),
            "activations": round(vram_activations, 2),
            "dequant_buffers": vram_dequant,
            "overhead": vram_overhead,
            "total": round(vram_total, 2),
            "recommended_with_buffer": round(vram_total * 1.2, 2),
        }

    elif mode == "full_finetune":
        # 18 bytes por parâmetro com Adam
        vram_optimizer = n_total_params * 18 / 1e9

        # Ativações
        base_activations = batch_size * seq_len * d_model * n_layers * 4 / 1e9
        if gradient_checkpointing:
            vram_activations = base_activations / 8
        else:
            vram_activations = base_activations

        vram_overhead = 2.0  # Maior overhead por NCCL etc

        vram_total = vram_optimizer + vram_activations + vram_overhead

        result["vram_gb"] = {
            "optimizer_states_18x": round(vram_optimizer, 2),
            "activations": round(vram_activations, 2),
            "overhead": vram_overhead,
            "total": round(vram_total, 2),
            "recommended_with_buffer": round(vram_total * 1.2, 2),
        }

    # Sugerir hardware
    total_vram = result["vram_gb"]["recommended_with_buffer"]
    hardware_suggestions = []
    if total_vram <= 12:
        hardware_suggestions.append("RTX 3060 12GB, RTX 4060 Ti 16GB")
    if total_vram <= 16:
        hardware_suggestions.append("RTX 4060 Ti 16GB")
    if total_vram <= 24:
        hardware_suggestions.append("RTX 4090 24GB, RTX 3090 24GB")
    if total_vram <= 40:
        hardware_suggestions.append("A100 40GB, 2× RTX 3090")
    if total_vram <= 48:
        hardware_suggestions.append("2× RTX 4090 48GB")
    if total_vram <= 80:
        hardware_suggestions.append("A100 80GB, H100 80GB")
    if total_vram <= 160:
        hardware_suggestions.append("2× H100 80GB, 2× A100 80GB")
    if total_vram <= 320:
        hardware_suggestions.append("4× H100 80GB")
    if total_vram <= 640:
        hardware_suggestions.append("8× H100 80GB")

    result["hardware_suggestion"] = hardware_suggestions[-1] if hardware_suggestions else "Cluster multi-node"

    return result


# Exemplos de uso
if __name__ == "__main__":
    # Inferência
    result = estimate_vram("meta-llama/Meta-Llama-3-8B-Instruct", dtype="bf16", mode="inference")
    print("\n=== Inferência Llama 3 8B BF16 ===")
    for k, v in result["vram_gb"].items():
        print(f"  {k}: {v} GB")
    print(f"  Hardware sugerido: {result['hardware_suggestion']}")

    # QLoRA
    result = estimate_vram("mistralai/Mistral-7B-Instruct-v0.3", mode="qlora", batch_size=4, seq_len=2048)
    print("\n=== QLoRA Mistral 7B ===")
    for k, v in result["vram_gb"].items():
        print(f"  {k}: {v} GB")
```

### 2. Monitorar VRAM em Runtime

```python
import torch
import gc
from contextlib import contextmanager
from typing import Callable

def vram_snapshot(label: str = "") -> dict:
    """
    Captura snapshot do uso de VRAM com métricas detalhadas.

    Diferença entre allocated e reserved:
    - allocated: memória efetivamente usada por tensores ativos
    - reserved: pool que o PyTorch reservou (inclui fragmentação)
    - free: espaço livre dentro do pool reservado
    """
    if not torch.cuda.is_available():
        return {"error": "CUDA não disponível"}

    allocated = torch.cuda.memory_allocated() / 1e9
    reserved = torch.cuda.memory_reserved() / 1e9
    max_allocated = torch.cuda.max_memory_allocated() / 1e9
    total = torch.cuda.get_device_properties(0).total_memory / 1e9

    snapshot = {
        "label": label,
        "allocated_gb": round(allocated, 3),
        "reserved_gb": round(reserved, 3),
        "max_allocated_gb": round(max_allocated, 3),
        "total_gb": round(total, 3),
        "free_gb": round(total - reserved, 3),
        "fragmentation_gb": round(reserved - allocated, 3),
        "utilization_pct": round(allocated / total * 100, 1),
    }

    if label:
        print(f"\n[VRAM] {label}")
        print(f"  Alocado:      {snapshot['allocated_gb']:.3f} GB")
        print(f"  Reservado:    {snapshot['reserved_gb']:.3f} GB")
        print(f"  Pico:         {snapshot['max_allocated_gb']:.3f} GB")
        print(f"  Total GPU:    {snapshot['total_gb']:.1f} GB")
        print(f"  Livre:        {snapshot['free_gb']:.3f} GB")
        print(f"  Fragmentação: {snapshot['fragmentation_gb']:.3f} GB")
        print(f"  Utilização:   {snapshot['utilization_pct']:.1f}%")

    return snapshot


@contextmanager
def track_vram(label: str = "operation"):
    """Context manager para medir VRAM de um bloco de código."""
    torch.cuda.reset_peak_memory_stats()
    before = torch.cuda.memory_allocated()

    yield

    after = torch.cuda.memory_allocated()
    peak = torch.cuda.max_memory_allocated()

    delta = (after - before) / 1e9
    peak_delta = (peak - before) / 1e9

    print(f"[{label}]")
    print(f"  Delta: {delta:+.3f} GB")
    print(f"  Peak durante operação: {peak_delta:.3f} GB acima do baseline")


def print_memory_summary():
    """Imprime sumário completo de memória (similar a nvidia-smi mas mais detalhado)."""
    print(torch.cuda.memory_summary(abbreviated=True))


# Exemplo de uso
def monitor_model_loading():
    """Demonstra monitoramento durante carregamento e inferência."""
    from transformers import AutoModelForCausalLM, AutoTokenizer

    vram_snapshot("Antes de qualquer carregamento")

    with track_vram("Carregar modelo"):
        model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            torch_dtype=torch.float16,
            device_map="cuda",
        )

    vram_snapshot("Após carregar modelo")

    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
    inputs = tokenizer("Hello world", return_tensors="pt").to("cuda")

    with track_vram("Inferência (prefill + decode)"):
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=50)

    vram_snapshot("Após inferência")

    # Liberar memória
    del model
    gc.collect()
    torch.cuda.empty_cache()

    vram_snapshot("Após liberar modelo")
```

### 3. Calcular KV Cache Exato Dado Parâmetros do Modelo

```python
def calculate_kv_cache(
    n_layers: int,
    n_kv_heads: int,
    d_head: int,
    seq_len: int,
    batch_size: int,
    dtype_bytes: float = 2.0,  # BF16
    unit: str = "GB",
) -> dict:
    """
    Calcula o tamanho do KV cache com precisão.

    Fórmula:
        KV_cache = 2 × n_layers × n_kv_heads × d_head × seq_len × batch × bytes

    O fator 2 representa Key e Value (Query não é cacheado).
    Para modelos GQA, n_kv_heads < n_attention_heads.

    Exemplos:
        Llama 3 8B:  n_layers=32, n_kv_heads=8,  d_head=128
        Llama 3 70B: n_layers=80, n_kv_heads=8,  d_head=128
        Mistral 7B:  n_layers=32, n_kv_heads=8,  d_head=128
        GPT-4 (est): n_layers=128, n_kv_heads=?, d_head=?
    """
    multiplier = {"GB": 1e9, "MB": 1e6, "KB": 1e3}[unit]

    # Tamanho total do KV cache
    total_bytes = 2 * n_layers * n_kv_heads * d_head * seq_len * batch_size * dtype_bytes

    total = total_bytes / multiplier

    # Por token (útil para calcular custo de aumentar seq_len)
    per_token_bytes = 2 * n_layers * n_kv_heads * d_head * dtype_bytes
    per_token = per_token_bytes / multiplier

    # Por layer (útil para paged attention)
    per_layer_bytes = 2 * n_kv_heads * d_head * seq_len * batch_size * dtype_bytes
    per_layer = per_layer_bytes / multiplier

    print(f"KV Cache Analysis:")
    print(f"  Config: {n_layers} layers × {n_kv_heads} KV heads × d_head={d_head}")
    print(f"  Seq len: {seq_len}, Batch: {batch_size}, dtype: {dtype_bytes*8:.0f}-bit")
    print(f"  Total: {total:.3f} {unit}")
    print(f"  Por token: {per_token*1000:.4f} M{unit[0]}B/token")
    print(f"  Por layer: {per_layer:.4f} {unit}")

    # Escalar para diferentes seq_lens
    print(f"\n  Scaling por seq_len (batch={batch_size}):")
    for sl in [512, 1024, 2048, 4096, 8192, 16384, 32768, 131072]:
        scaled = 2 * n_layers * n_kv_heads * d_head * sl * batch_size * dtype_bytes / multiplier
        marker = " ← atual" if sl == seq_len else ""
        print(f"    {sl:7d} tokens: {scaled:.3f} {unit}{marker}")

    return {
        "total": round(total, 4),
        "per_token": round(per_token, 6),
        "per_layer": round(per_layer, 4),
        "unit": unit,
    }


# Exemplos práticos
print("=== Llama 3 8B (GQA: 8 KV heads) ===")
calculate_kv_cache(n_layers=32, n_kv_heads=8, d_head=128, seq_len=4096, batch_size=1)

print("\n=== Llama 3 70B (GQA: 8 KV heads) ===")
calculate_kv_cache(n_layers=80, n_kv_heads=8, d_head=128, seq_len=4096, batch_size=1)

print("\n=== GPT-2 Large (MHA: 16 KV heads) ===")
calculate_kv_cache(n_layers=36, n_kv_heads=16, d_head=64, seq_len=1024, batch_size=1)
```

### 4. Script "Cabe no Meu Hardware?" — Verificador Automático

```python
import subprocess
import json
import torch
from dataclasses import dataclass

@dataclass
class GPUInfo:
    name: str
    total_vram_gb: float
    available_vram_gb: float

def get_gpu_info() -> list[GPUInfo]:
    """Detecta GPUs disponíveis e VRAM livre."""
    gpus = []
    if not torch.cuda.is_available():
        print("CUDA não disponível. Verificando Apple Silicon...")
        # Para Apple Silicon, verificar memória do sistema
        import platform
        if platform.system() == "Darwin":
            import subprocess
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType", "-json"],
                capture_output=True, text=True
            )
            # Aproximação: toda RAM disponível para modelos
            import psutil
            total_ram = psutil.virtual_memory().total / 1e9
            available_ram = psutil.virtual_memory().available / 1e9
            gpus.append(GPUInfo("Apple Silicon (Unified Memory)", total_ram, available_ram))
        return gpus

    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        total = props.total_memory / 1e9
        # VRAM disponível = total - já alocado
        torch.cuda.set_device(i)
        allocated = torch.cuda.memory_reserved(i) / 1e9
        available = total - allocated
        gpus.append(GPUInfo(props.name, total, available))

    return gpus


def check_model_fits(
    model_name: str,
    dtype: str = "bf16",
    mode: str = "inference",
    batch_size: int = 1,
    seq_len: int = 4096,
    lora_rank: int = 16,
) -> dict:
    """
    Verifica se um modelo cabe no hardware disponível.

    Detecta automaticamente as GPUs presentes e compara
    com a estimativa de VRAM necessária.

    Returns:
        dict com resultado (fits=True/False) e detalhes
    """
    # Detectar hardware
    gpus = get_gpu_info()
    if not gpus:
        return {"error": "Nenhuma GPU detectada"}

    # Calcular VRAM necessária
    vram_estimate = estimate_vram(
        model_name, dtype=dtype, mode=mode,
        batch_size=batch_size, seq_len=seq_len,
        lora_rank=lora_rank,
    )

    required_vram = vram_estimate["vram_gb"]["recommended_with_buffer"]

    # Verificar se cabe em cada GPU individualmente
    results = []
    for gpu in gpus:
        fits_single = gpu.available_vram_gb >= required_vram
        results.append({
            "gpu": gpu.name,
            "total_vram_gb": round(gpu.total_vram_gb, 1),
            "available_vram_gb": round(gpu.available_vram_gb, 1),
            "required_vram_gb": required_vram,
            "fits_single_gpu": fits_single,
            "headroom_gb": round(gpu.available_vram_gb - required_vram, 2),
        })

    # Verificar se cabe em todas as GPUs juntas (multi-GPU)
    total_available = sum(g.available_vram_gb for g in gpus)
    fits_multi_gpu = total_available >= required_vram

    # Sumário
    print(f"\n{'='*60}")
    print(f"Modelo: {model_name}")
    print(f"Modo: {mode} | Dtype: {dtype} | Batch: {batch_size} | Seq: {seq_len}")
    print(f"VRAM necessária (com 20% buffer): {required_vram:.1f} GB")
    print(f"{'='*60}")

    for r in results:
        status = "✓ CABE" if r["fits_single_gpu"] else "✗ NÃO CABE"
        print(f"\n{r['gpu']}")
        print(f"  Disponível: {r['available_vram_gb']:.1f} GB / {r['total_vram_gb']:.1f} GB total")
        print(f"  Status: {status}")
        if r["fits_single_gpu"]:
            print(f"  Headroom: {r['headroom_gb']:.1f} GB")
        else:
            shortage = -r["headroom_gb"]
            print(f"  Falta: {shortage:.1f} GB")

    if len(gpus) > 1:
        multi_status = "✓ CABE" if fits_multi_gpu else "✗ NÃO CABE"
        print(f"\nMulti-GPU ({len(gpus)}× GPUs combinadas):")
        print(f"  Total disponível: {total_available:.1f} GB")
        print(f"  Status: {multi_status}")

    return {
        "model": model_name,
        "required_vram_gb": required_vram,
        "gpus": results,
        "fits_any_single_gpu": any(r["fits_single_gpu"] for r in results),
        "fits_multi_gpu": fits_multi_gpu,
        "recommendation": vram_estimate["hardware_suggestion"],
    }


# Exemplo de uso
if __name__ == "__main__":
    # Verificar se Llama 3 8B cabe para inferência
    check_model_fits(
        "meta-llama/Meta-Llama-3-8B-Instruct",
        dtype="bf16",
        mode="inference",
        batch_size=1,
        seq_len=4096,
    )

    # Verificar se QLoRA de Mistral 7B é viável
    check_model_fits(
        "mistralai/Mistral-7B-Instruct-v0.3",
        dtype="nf4",
        mode="qlora",
        batch_size=4,
        seq_len=2048,
    )
```

---

## Referências

- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) — Tim Dettmers et al., 2023
- [ZeRO: Memory Optimizations Toward Training Trillion Parameter Models](https://arxiv.org/abs/1910.02054) — Rajbhandari et al., 2020
- [NVIDIA CUDA Memory Management](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#memory-management) — referência oficial
- [FlashAttention-2](https://arxiv.org/abs/2307.08691) — otimização de memória para attention
- [DeepSpeed ZeRO docs](https://www.deepspeed.ai/tutorials/zero/) — implementação de referência para ZeRO

---

## Relacionado

- [[gpu-architecture]] — entender por que HBM bandwidth é o gargalo
- [[specialized-hardware]] — alternativas com memória on-chip (Groq, Cerebras)
- [[quantization]] — como INT4/GPTQ/AWQ reduzem VRAM de pesos
- [[kv-cache-attention]] — otimizações de KV cache (GQA, paged attention)
- [[fine-tuning-peft]] — QLoRA e LoRA na prática
- [[inference-engines]] — vLLM, llama.cpp e como gerenciam memória em produção
