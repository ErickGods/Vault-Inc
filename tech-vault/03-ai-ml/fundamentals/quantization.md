---
tags: [ai-ml, fundamentals, quantization, gptq, awq, gguf]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Quantization, GPTQ, AWQ, GGUF, INT4, INT8]
---

# Quantização de LLMs

## Overview

Quantização é o processo de representar pesos (e opcionalmente ativações) de modelos em formatos numéricos de menor precisão — de FP32 ou BF16 para INT8, INT4, ou até INT2. O objetivo é duplo: **reduzir o consumo de VRAM** (proporcional ao número de bits) e **aumentar o throughput** (mais pesos cabem em cache, operações matriciais em menor precisão são mais rápidas em hardware especializado).

A perda de qualidade é inevitável mas controlável. Técnicas modernas como GPTQ, AWQ e quantização K-quants (GGUF) conseguem comprimir modelos em INT4 com degradação de perplexidade inferior a 7% — praticamente imperceptível na maioria dos casos de uso.

Integra com [[vram-estimation]], [[inference-engines]], [[gpu-architecture]], [[fine-tuning-peft]] e [[kv-cache-attention]].

> [!tip] Q4_K_M é o Sweet Spot
> Para a maioria dos casos de uso, Q4_K_M oferece o melhor trade-off: ~4.8 GB para um modelo 8B, <7% de perda de qualidade em perplexidade, e compatível com a maioria do hardware consumer. Comece aqui.

---

## Tipos de Dados — Tabela Completa

| Dtype | Bits | Range | Bytes/param | Treinamento | Inferência |
|-------|------|-------|-------------|------------|-----------|
| FP32 | 32 | ±3.4e38 | 4 | ✅ Master weights | ❌ Muito lento |
| BF16 | 16 | ±3.4e38 | 2 | ✅ Forward/backward | ✅ H100, A100 |
| FP16 | 16 | ±65504 | 2 | ⚠️ Overflow risk | ✅ Geral |
| INT8 | 8 | -128..127 | 1 | ❌ | ✅ LLM.int8() |
| NF4 | 4 | normal dist | 0.5 | ✅ QLoRA base | ✅ |
| INT4 | 4 | -8..7 | 0.5 | ❌ | ✅ GPTQ, AWQ |
| FP8 | 8 | ±448 (E4M3) | 1 | ✅ H100 | ✅ H100 |
| INT2 | 2 | -2..1 | 0.25 | ❌ | ⚠️ Experimental |

### Por Que BF16 Supera FP16 para Treinamento

FP16 e BF16 usam os mesmos 16 bits, mas com alocação diferente:

```
FP16: 1 bit sinal + 5 bits expoente + 10 bits mantissa → range ±65504
BF16: 1 bit sinal + 8 bits expoente + 7 bits mantissa  → range ±3.4e38
```

BF16 mantém o mesmo expoente que FP32, evitando overflow/underflow em gradientes grandes — o principal problema do FP16 em treinamento. A mantissa menor do BF16 tem menor precisão decimal, mas isso é tolerável para gradientes.

> [!info] BF16 vs FP16 em Produção
> Em GPUs NVIDIA Ampere+ (A100, H100, RTX 30/40 series), BF16 é preferível ao FP16 para inferência: mesmo throughput, maior range, sem risco de overflow. Em GPUs mais antigas (V100), use FP16.

---

## Fundamentos Matemáticos de Quantização

### Quantização Simétrica

```
scale = max(|x|) / (2^(bits-1) - 1)
q     = round(x / scale)              # quantizar
x_dq  = q × scale                    # dequantizar (reconstrução com erro)
```

Adequada para distribuições centradas em zero (pesos de transformers, em geral).

### Quantização Assimétrica

```
scale      = (max(x) - min(x)) / (2^bits - 1)
zero_point = round(-min(x) / scale)
q          = round(x / scale + zero_point)    # quantizar
x_dq       = (q - zero_point) × scale        # dequantizar
```

Necessária quando a distribuição não é simétrica (ex: ativações com ReLU, que têm mínimo em 0).

### Block Quantization

Calcular um único `scale` global por tensor pode amplificar o erro em regiões com distribuições localmente muito diferentes. Block quantization resolve isso calculando `scale` (e opcionalmente `zero_point`) por bloco de B pesos (tipicamente B=32 ou B=128).

```python
import torch


def quantize_symmetric_blocked(
    weight: torch.Tensor,
    bits: int = 4,
    block_size: int = 128,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Quantização simétrica por bloco para pesos de LLM.

    Args:
        weight: tensor de pesos, shape (out_features, in_features)
        bits: número de bits alvo (ex: 4 para INT4)
        block_size: número de pesos por bloco de quantização

    Returns:
        (weight_quantized, scales) onde scales tem shape (out_features, n_blocks)
    """
    out_features, in_features = weight.shape
    max_val = 2 ** (bits - 1) - 1  # ex: 7 para INT4

    # Padding para alinhar com block_size
    pad_len = (block_size - in_features % block_size) % block_size
    if pad_len > 0:
        weight = torch.cat([weight, torch.zeros(out_features, pad_len)], dim=1)

    n_blocks = weight.shape[1] // block_size
    weight_blocked = weight.view(out_features, n_blocks, block_size)

    # Scale por bloco: max abs value normalizado
    scales = weight_blocked.abs().max(dim=2).values / max_val
    # scales: (out_features, n_blocks)

    # Quantizar
    scales_expanded = scales.unsqueeze(2)  # (out_features, n_blocks, 1)
    weight_q = torch.clamp(
        torch.round(weight_blocked / scales_expanded),
        -max_val - 1,
        max_val,
    ).to(torch.int8)

    return weight_q, scales


def dequantize_blocked(
    weight_q: torch.Tensor,
    scales: torch.Tensor,
) -> torch.Tensor:
    """Dequantiza pesos quantizados por bloco."""
    out_features, n_blocks, block_size = weight_q.shape
    weight_fp = weight_q.float() * scales.unsqueeze(2)
    return weight_fp.view(out_features, n_blocks * block_size)


def calcular_erro_quantizacao(
    weight_original: torch.Tensor,
    bits: int = 4,
    block_size: int = 128,
) -> dict:
    """Mede o erro de reconstrução da quantização."""
    weight_q, scales = quantize_symmetric_blocked(weight_original, bits, block_size)
    weight_dq = dequantize_blocked(weight_q, scales)

    # Trim para dimensão original se houve padding
    weight_dq = weight_dq[:, :weight_original.shape[1]]

    mse = ((weight_original - weight_dq) ** 2).mean().item()
    max_err = (weight_original - weight_dq).abs().max().item()

    compression = weight_original.numel() * 4 / (weight_q.numel() * bits / 8)

    return {
        "mse": mse,
        "max_abs_error": max_err,
        "snr_db": 10 * torch.log10(
            weight_original.var() / torch.tensor(mse)
        ).item(),
        "compression_ratio": compression,
    }


if __name__ == "__main__":
    # Simular pesos típicos de uma camada linear de LLM
    weight = torch.randn(4096, 4096) * 0.02  # distribuição normal com std típico

    for bits in [8, 4, 2]:
        resultado = calcular_erro_quantizacao(weight, bits=bits)
        print(
            f"INT{bits}: MSE={resultado['mse']:.6f}, "
            f"SNR={resultado['snr_db']:.1f}dB, "
            f"Compressão={resultado['compression_ratio']:.1f}x"
        )
```

---

## Outlier Channels e SmoothQuant

### O Problema dos Outliers

Ativações de LLMs (especialmente modelos maiores) exibem um fenômeno crítico: alguns canais têm magnitudes muito maiores que os demais — os **outlier channels**. Em modelos acima de 6.7B parâmetros, esse fenômeno é consistente e sistemático.

**Impacto na quantização INT8:**
- A escala global é ditada pelos outliers (magnitudes grandes)
- Canais normais ficam com quantização muito granular (muitos valores mapeados para 0)
- Erro de quantização explode nesses canais normais

### SmoothQuant

SmoothQuant resolve isso migrando a "dificuldade" das ativações para os pesos — que são estáticos e mais fáceis de analisar antes do serving.

A formulação matemática:

```
Y = X W^T

# Equivalente com scaling:
Y = (X diag(s)^{-1}) (diag(s) W^T)
  = X̃ W̃^T

onde:
  s_j = max(|X_j|)^α / max(|W_j|)^(1-α)  # escala por canal j
  α ∈ [0, 1]: controla a migração (α=0.5 é um bom padrão)
  X̃ = X diag(s)^{-1}  → ativações suavizadas (outliers reduzidos)
  W̃ = diag(s) W^T     → pesos com outliers absorvidos (offline, sem custo runtime)
```

```python
import torch


def smooth_quant_migration(
    weight: torch.Tensor,           # (out_features, in_features)
    activation_max: torch.Tensor,   # (in_features,) — máx por canal de ativação
    alpha: float = 0.5,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Aplica SmoothQuant: migra dificuldade de quantização das ativações para os pesos.

    Args:
        weight: pesos da camada linear
        activation_max: valor máximo absoluto por canal de ativação (calibração)
        alpha: fator de migração. 0=tudo nas ativações, 1=tudo nos pesos

    Returns:
        (weight_smoothed, smoothing_scale)
        weight_smoothed: pode ser quantizado com menor erro
        smoothing_scale: deve ser aplicado às ativações em runtime (1/scale)
    """
    weight_max = weight.abs().max(dim=0).values  # (in_features,)

    # Escala de smoothing por canal
    smooth_scale = (
        activation_max.pow(alpha) / weight_max.pow(1 - alpha)
    ).clamp(min=1e-5)

    # Absorver nos pesos (offline)
    weight_smoothed = weight * smooth_scale.unsqueeze(0)

    return weight_smoothed, smooth_scale
```

> [!warning] Quantização de Ativações é Mais Difícil
> Pesos são estáticos e fáceis de analisar antes do serving. Ativações são dinâmicas e variam por input. Quantizar ativações (ex: LLM.int8()) requer análise em runtime, o que adiciona overhead.

---

## GPTQ — Post-Training Quantization com Segunda Ordem

### Fundamento Teórico

GPTQ é baseado em OBC/OBQ (Optimal Brain Compression/Quantization), que por sua vez deriva do método Optimal Brain Surgeon. A ideia: ao quantizar um peso w_q, o erro introduzido pode ser compensado ajustando os outros pesos da mesma linha, usando informação de segunda ordem (Hessian da loss).

Para cada peso w_q sendo quantizado na linha de pesos W, a atualização ótima dos demais pesos é:

```
δW = -(w_q - quant(w_q)) / [H^{-1}]_{qq} × [H^{-1}]_{q,:}

onde H é a Hessiana da loss em relação aos pesos da camada,
aproximada por H ≈ 2 X X^T (X = ativações do calibration set)
```

A GPTQ processa os pesos coluna por coluna, propagando o erro residual para as colunas seguintes — processo chamado de **lazy batch updates** com **Cholesky decomposition** para eficiência.

### Características Práticas

- **Calibration dataset:** ~128 amostras aleatórias são suficientes (o dataset de calibração não precisa ser o mesmo de treinamento)
- **Tempo de quantização:** horas para modelos grandes (70B+), mas é offline
- **Qualidade:** geralmente melhor que AWQ em perplexidade, especialmente para bits muito baixos (2-3 bits)

```python
# Quantização com AutoGPTQ
# pip install auto-gptq optimum

from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer
from datasets import load_dataset
import torch


def quantizar_com_gptq(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
    output_dir: str = "./llama-3-8b-gptq-int4",
    bits: int = 4,
    group_size: int = 128,
    n_calibration_samples: int = 128,
    seq_len: int = 2048,
):
    """
    Quantiza modelo com GPTQ.

    Args:
        bits: precisão alvo (2, 3, 4, ou 8)
        group_size: tamanho do grupo para block quantization (-1 = por linha inteira)
        n_calibration_samples: amostras para calibração do Hessian
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

    # Configuração de quantização
    quantize_config = BaseQuantizeConfig(
        bits=bits,
        group_size=group_size,
        desc_act=True,       # reordenar ativações por magnitude (melhora qualidade)
        sym=True,            # quantização simétrica
    )

    # Carregar modelo em FP16 para quantização
    model = AutoGPTQForCausalLM.from_pretrained(
        model_name,
        quantize_config=quantize_config,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    # Preparar dados de calibração (Wikipedia é padrão)
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
    calibration_data = []

    for sample in dataset:
        if len(sample["text"]) < 50:
            continue
        tokens = tokenizer(
            sample["text"],
            return_tensors="pt",
            max_length=seq_len,
            truncation=True,
        )
        if tokens["input_ids"].shape[1] >= seq_len:
            calibration_data.append(tokens["input_ids"])
        if len(calibration_data) >= n_calibration_samples:
            break

    # Executar quantização (processo offline — pode demorar horas para 70B)
    model.quantize(calibration_data)

    # Salvar modelo quantizado
    model.save_quantized(output_dir, use_safetensors=True)
    tokenizer.save_pretrained(output_dir)

    print(f"Modelo quantizado salvo em: {output_dir}")
    return model, tokenizer


def carregar_modelo_gptq(
    model_dir: str = "./llama-3-8b-gptq-int4",
    device: str = "cuda",
):
    """Carrega modelo pré-quantizado com GPTQ."""
    from auto_gptq import AutoGPTQForCausalLM
    from transformers import AutoTokenizer

    model = AutoGPTQForCausalLM.from_quantized(
        model_dir,
        use_safetensors=True,
        device=device,
        inject_fused_attention=True,   # kernel fusado para melhor performance
        inject_fused_mlp=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    return model, tokenizer
```

---

## AWQ — Activation-Aware Weight Quantization

### Observação Central

Lin et al. (2023) observaram que apenas ~1% dos pesos de um LLM são "salientes" — aqueles associados a canais de ativação com alta magnitude. Esses pesos salientes contribuem desproporcionalmente para o erro de quantização quando comprimidos para INT4.

**Solução:** antes de quantizar, aplicar um **scaling** aos pesos salientes para reduzir seu range, tornando-os mais fáceis de representar em baixa precisão.

```
W_scaled = W × diag(s)
W_quantized = quant(W_scaled)

Em runtime: Y = X × W_quantized × diag(s)^{-1}
             (ou equivalentemente: Y = (X × diag(s)^{-1}) × W_quantized,
              onde diag(s)^{-1} é absorvido na camada anterior)
```

O scale `s` é encontrado por grid search sobre os canais de ativação: para cada canal, tenta-se múltiplos valores de s e escolhe o que minimiza o erro de quantização no calibration set.

### AWQ vs GPTQ

| Critério | GPTQ | AWQ |
|---------|------|-----|
| Velocidade de quantização | Lento (horas, 70B) | Rápido (minutos) |
| Qualidade (perplexidade) | Ligeiramente melhor | Comparável |
| Hardware suportado | CUDA | CUDA, Metal (Apple) |
| Manutenção | AutoGPTQ | AutoAWQ, llm-awq |
| INT3 support | Sim | Sim |

```python
# Quantização com AutoAWQ
# pip install autoawq

from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer


def quantizar_com_awq(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
    output_dir: str = "./llama-3-8b-awq",
    bits: int = 4,
    group_size: int = 128,
    zero_point: bool = True,
):
    """
    Quantiza modelo com AWQ.

    Args:
        zero_point: usar quantização assimétrica (recomendado para INT4)
        group_size: tamanho do grupo para block quantization
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoAWQForCausalLM.from_pretrained(model_name, safetensors=True)

    quant_config = {
        "zero_point": zero_point,
        "q_group_size": group_size,
        "w_bit": bits,
        "version": "GEMM",   # GEMM para throughput, GEMV para latência de batch=1
    }

    # Calibração e quantização (minutos, não horas)
    model.quantize(
        tokenizer,
        quant_config=quant_config,
        # AWQ usa WikiText-2 internamente para calibração por padrão
    )

    model.save_quantized(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Modelo AWQ salvo em: {output_dir}")


def carregar_modelo_awq(model_dir: str) -> tuple:
    """Carrega modelo quantizado com AWQ."""
    from awq import AutoAWQForCausalLM
    from transformers import AutoTokenizer

    model = AutoAWQForCausalLM.from_quantized(
        model_dir,
        fuse_layers=True,      # funde camadas para melhor performance
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    return model, tokenizer
```

> [!warning] Primeiras e Últimas Camadas São Sensíveis
> As primeiras camadas do transformer (embedding, primeiras attention layers) e as últimas (lm_head) são mais sensíveis à quantização. GPTQ e AWQ frequentemente deixam essas camadas em maior precisão automaticamente.

---

## Bitsandbytes — Quantização On-the-Fly

A biblioteca `bitsandbytes` permite carregar modelos diretamente em INT8 ou INT4 (NF4) sem precisar executar quantização offline — quantização acontece ao carregar os pesos.

### LLM.int8() — Mixed-Precision INT8

LLM.int8() (Dettmers et al., 2022) resolve o problema dos outlier channels com uma abordagem diferente:
1. Detecta outlier channels em runtime (threshold configurável)
2. Mantém esses canais em FP16 para a multiplicação matricial
3. Quantiza os canais normais para INT8
4. Combina os resultados

```python
# pip install bitsandbytes transformers accelerate

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch


def carregar_int8(model_name: str) -> tuple:
    """Carrega modelo em INT8 com LLM.int8()."""
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,           # outlier threshold (padrão 6.0)
        llm_int8_has_fp16_weight=False,   # economizar VRAM (não manter pesos FP16)
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer


def carregar_nf4(
    model_name: str,
    use_double_quant: bool = True,
) -> tuple:
    """
    Carrega modelo em NF4 (QLoRA style).

    NF4 = Normal Float 4: os 16 níveis de quantização são espaçados segundo
    a distribuição normal, aproveitando que pesos de LLMs seguem distribuição normal.
    Double quantization: quantiza as próprias escalas (adicional ~0.37 bits/param economia).
    """
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",             # NF4 ou "fp4"
        bnb_4bit_compute_dtype=torch.bfloat16, # dtype para computação (dequantiza para BF16)
        bnb_4bit_use_double_quant=use_double_quant,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer


def comparar_uso_vram(model_name: str = "meta-llama/Llama-3-8B-Instruct"):
    """
    Compara consumo de VRAM entre diferentes configurações de quantização.
    Requer GPU com pelo menos 16GB para rodar BF16.
    """
    import gc

    configs = {
        "BF16 (baseline)": {"torch_dtype": torch.bfloat16, "quantization_config": None},
    }

    resultados = {}

    for nome, config in configs.items():
        try:
            torch.cuda.empty_cache()
            gc.collect()

            vram_antes = torch.cuda.memory_allocated() / (1024 ** 3)

            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                **config,
            )

            vram_depois = torch.cuda.memory_allocated() / (1024 ** 3)
            resultados[nome] = vram_depois - vram_antes

            del model
            torch.cuda.empty_cache()
            gc.collect()

        except Exception as e:
            resultados[nome] = f"Erro: {e}"

    print(f"\n{'Configuração':<25} {'VRAM (GB)':>12}")
    print("-" * 40)
    for nome, vram in resultados.items():
        if isinstance(vram, float):
            print(f"{nome:<25} {vram:>11.2f}")
        else:
            print(f"{nome:<25} {vram:>12}")
```

---

## GGUF / llama.cpp

### O Formato GGUF

GGUF (GGML Universal File Format) é o formato de serialização usado pelo llama.cpp para inferência CPU (e GPU parcial). Contém:
- Metadados do modelo (arquitetura, hiperparâmetros, tokenizer)
- Pesos quantizados em variantes de 2 a 8 bits
- Tensors de alta importância em precisão maior (mixed precision)

### Variantes de Quantização GGUF

| Variante | Bits efetivos | Algoritmo | Qualidade | Caso de uso |
|---------|---------------|----------|----------|------------|
| Q2_K | ~2.6 | K-quants | ★★ | VRAM extremamente limitada |
| Q3_K_M | ~3.4 | K-quants mixed | ★★★ | 3GB VRAM |
| Q4_0 | 4.0 | Simples | ★★★ | Velocidade máxima |
| Q4_K_M | ~4.5 | K-quants mixed | ★★★★ | **Sweet spot recomendado** |
| Q5_K_M | ~5.5 | K-quants mixed | ★★★★ | Equilíbrio qualidade/tamanho |
| Q6_K | ~6.6 | K-quants | ★★★★ | Alta qualidade, pouca VRAM extra |
| Q8_0 | 8.0 | INT8 simples | ★★★★★ | Quase sem perda, 2x tamanho vs Q4 |

**K-quants:** usa blocos de tamanho variável e mantém camadas críticas (embedding, lm_head, algumas attention layers) em maior precisão automaticamente.

### Perplexity Tradeoff — Llama 3 8B

| Quantização | Tamanho | PPL (WikiText-2) | Δ vs FP16 |
|------------|---------|-----------------|----------|
| FP16 | 16.0 GB | ~6.10 | baseline |
| Q8_0 | 8.5 GB | ~6.10 | +0.0% |
| Q6_K | 6.1 GB | ~6.20 | +1.6% |
| Q5_K_M | 5.3 GB | ~6.30 | +3.3% |
| Q4_K_M | 4.8 GB | ~6.50 | +6.6% |
| Q4_0 | 4.3 GB | ~7.00 | +14.8% |
| Q2_K | 2.8 GB | ~9.20 | +50.8% |

> [!warning] Perplexidade Não Captura Tudo
> Perplexidade baixa em WikiText-2 não garante boa performance em coding, raciocínio, ou instruction following. Sempre valide em tasks reais antes de escolher quantização para produção.

```python
# Inferência com llama-cpp-python
# pip install llama-cpp-python
# Para GPU: CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python

from llama_cpp import Llama
from pathlib import Path


def carregar_gguf(
    model_path: str,          # ex: "./llama-3-8b-q4_k_m.gguf"
    n_ctx: int = 4096,        # context window
    n_gpu_layers: int = -1,   # -1 = todas as camadas na GPU (se disponível)
    n_threads: int = 8,       # threads CPU para camadas não na GPU
) -> Llama:
    """
    Carrega modelo GGUF com llama.cpp.

    Args:
        n_gpu_layers: número de camadas a offloar para GPU.
                      -1 = todas, 0 = só CPU, N = N camadas na GPU.
                      Útil quando a GPU não tem VRAM suficiente para o modelo completo.
    """
    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_gpu_layers=n_gpu_layers,
        n_threads=n_threads,
        verbose=False,
    )
    return llm


def inferencia_gguf(
    llm: Llama,
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    stream: bool = False,
) -> str:
    """
    Geração com modelo GGUF via llama.cpp.
    """
    messages = [{"role": "user", "content": prompt}]

    if stream:
        # Streaming: imprime tokens conforme gerados
        result = ""
        for chunk in llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        ):
            delta = chunk["choices"][0]["delta"].get("content", "")
            print(delta, end="", flush=True)
            result += delta
        print()
        return result
    else:
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response["choices"][0]["message"]["content"]


def benchmark_gguf_variantes(
    model_dir: str = "./models",
    prompt: str = "Explique como funcionam as redes neurais em detalhes técnicos:",
    max_tokens: int = 200,
):
    """
    Compara velocidade de inferência entre variantes GGUF.
    """
    import time
    import glob

    gguf_files = sorted(glob.glob(f"{model_dir}/*.gguf"))
    if not gguf_files:
        print(f"Nenhum arquivo .gguf encontrado em {model_dir}")
        return

    print(f"\n{'Arquivo':<40} {'Tokens/s':>10} {'Tempo total':>14}")
    print("-" * 68)

    for model_path in gguf_files:
        nome = Path(model_path).stem
        try:
            llm = carregar_gguf(model_path, n_gpu_layers=-1)

            # Warm-up
            inferencia_gguf(llm, "Hello", max_tokens=10)

            start = time.perf_counter()
            inferencia_gguf(llm, prompt, max_tokens=max_tokens)
            elapsed = time.perf_counter() - start

            tokens_per_sec = max_tokens / elapsed
            print(f"{nome:<40} {tokens_per_sec:>10.1f} {elapsed:>13.2f}s")

            del llm

        except Exception as e:
            print(f"{nome:<40} ERRO: {e}")
```

---

## Avaliação de Qualidade Pós-Quantização

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
import math


def calcular_perplexidade(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    dataset_name: str = "wikitext",
    dataset_config: str = "wikitext-2-raw-v1",
    split: str = "test",
    stride: int = 512,
    max_length: int = 2048,
    n_samples: int = 50,
) -> float:
    """
    Calcula perplexidade no WikiText-2 test set.
    Método padrão para comparar qualidade de quantizações.

    Args:
        stride: overlapping stride para janelas deslizantes (padrão: max_length // 4)
        n_samples: número de amostras a avaliar (None = dataset completo)
    """
    dataset = load_dataset(dataset_name, dataset_config, split=split)
    text = "\n\n".join(dataset["text"])

    encodings = tokenizer(text, return_tensors="pt")
    seq_len = encodings.input_ids.shape[1]

    model.eval()
    device = next(model.parameters()).device

    total_log_likelihood = 0.0
    total_tokens = 0
    samples_processed = 0

    for begin_loc in range(0, seq_len - max_length, stride):
        end_loc = begin_loc + max_length
        input_ids = encodings.input_ids[:, begin_loc:end_loc].to(device)
        target_ids = input_ids.clone()

        # Só calcula loss nos tokens do stride atual (não no overlap)
        target_ids[:, :-stride] = -100

        with torch.no_grad():
            outputs = model(input_ids, labels=target_ids)
            log_likelihood = outputs.loss * stride

        total_log_likelihood += log_likelihood.item()
        total_tokens += stride
        samples_processed += 1

        if n_samples and samples_processed >= n_samples:
            break

    avg_log_likelihood = total_log_likelihood / total_tokens
    perplexidade = math.exp(avg_log_likelihood)
    return perplexidade


def comparar_perplexidade_quantizacoes(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
):
    """
    Pipeline completo para comparar perplexidade entre quantizações.
    """
    from transformers import BitsAndBytesConfig

    configs = [
        ("BF16 (baseline)", {}),
        ("INT8 (LLM.int8)", {"quantization_config": BitsAndBytesConfig(load_in_8bit=True)}),
        ("NF4 (QLoRA)", {"quantization_config": BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )}),
    ]

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    resultados = {}

    for nome, kwargs in configs:
        print(f"Avaliando {nome}...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            **kwargs,
        )
        ppl = calcular_perplexidade(model, tokenizer, n_samples=20)
        resultados[nome] = ppl
        print(f"  PPL: {ppl:.3f}")
        del model
        torch.cuda.empty_cache()

    baseline = resultados.get("BF16 (baseline)", None)
    print(f"\n{'Configuração':<25} {'PPL':>8} {'Δ vs BF16':>12}")
    print("-" * 48)
    for nome, ppl in resultados.items():
        delta = (ppl / baseline - 1) * 100 if baseline else 0
        print(f"{nome:<25} {ppl:>8.3f} {delta:>11.1f}%")
```

---

## Referências

- GPTQ — [arxiv:2210.17323](https://arxiv.org/abs/2210.17323)
- AWQ — [arxiv:2306.00978](https://arxiv.org/abs/2306.00978)
- SmoothQuant — [arxiv:2211.10438](https://arxiv.org/abs/2211.10438)
- LLM.int8() — [arxiv:2208.07339](https://arxiv.org/abs/2208.07339)
- QLoRA — [arxiv:2305.14314](https://arxiv.org/abs/2305.14314)

---

## Related

- [[vram-estimation]] — calcular VRAM total incluindo pesos quantizados + KV cache
- [[inference-engines]] — vLLM e TensorRT-LLM suportam GPTQ/AWQ nativamente
- [[gpu-architecture]] — INT4/INT8 Tensor Cores no H100/A100 entregam throughput superior
- [[fine-tuning-peft]] — QLoRA usa NF4 para fine-tuning em hardware consumer
- [[kv-cache-attention]] — KV cache também pode ser quantizado para FP8/INT8
