---
tags: [ai-ml, fundamentals, hardware, tpu, groq, cerebras, inferentia]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Specialized AI Hardware, TPU, Groq LPU, Cerebras, AI Chips]
---

# Specialized AI Hardware

## Overview

GPUs dominam o mercado de IA desde 2012 — e por boas razões. São flexíveis, amplamente suportadas por frameworks como PyTorch e TensorFlow, e têm um ecossistema maduro de ferramentas, profissionais e bibliografias. Porém, flexibilidade tem um custo: GPUs carregam silício dedicado a rasterização gráfica, gerenciamento de displays e pipelines que simplesmente não são necessários para inferência de transformers.

Hardware especializado sacrifica essa flexibilidade em troca de eficiência radical no subconjunto específico de operações que modelos de linguagem executam: multiplicações de matrizes (GEMM), operações de atenção, e movimentação eficiente de pesos entre memória e cores.

O trade-off fundamental é:

| Dimensão | GPU (H100) | Hardware Especializado |
|----------|-----------|----------------------|
| Flexibilidade | Qualquer operação PyTorch | Operações otimizadas fixas |
| Custo de entrada | Alto ($20-30k) | Muito alto ou cloud-only |
| Performance em target | Boa | Excelente |
| Ecosistema | Maduro (PyTorch, JAX) | Fragmentado por vendor |
| Portabilidade | Alta | Baixa (lock-in) |
| Treinamento | Sim | Raramente |

Este documento cobre os principais aceleradores especializados que aparecem em produção: TPUs do Google, LPUs da Groq, WSE da Cerebras, chips AWS Trainium/Inferentia, Neural Engine da Apple e a aposta open-source da Tenstorrent.

---

## Google TPU — Tensor Processing Units

### Arquitetura Systolic Array

O coração do TPU é o systolic array — uma grade de Processing Elements (PEs) que processa dados em fluxo sincronizado, eliminando a necessidade de um banco de memória central compartilhado entre os PEs.

**Como funciona em hardware:**

Em uma multiplicação de matrizes `C = A × B`, o systolic array opera assim:

```
Pesos (B) fluem de cima para baixo:
┌────┬────┬────┐
│ PE │ PE │ PE │  ← row 0 pesos entram aqui
├────┼────┼────┤
│ PE │ PE │ PE │  ← row 1 pesos entram um ciclo depois
├────┼────┼────┤
│ PE │ PE │ PE │  ← row 2 pesos entram dois ciclos depois
└────┴────┴────┘
   ↑    ↑    ↑
Ativações (A) fluem da esquerda para direita
```

Cada PE executa uma operação multiply-accumulate (MAC) e passa o resultado parcial ao PE adjacente. Não há leitura de memória central — dados fluem diretamente entre PEs via conexões físicas. Isso elimina a latência e o consumo de energia associados à contention de memória.

**Vantagens do fluxo sistólico:**
- Cada dado que entra é reutilizado por múltiplos PEs antes de sair — máxima reutilização de dados
- Sem arbitragem de barramento — throughput previsível e determinístico
- Escala bem: um grid 128×128 de PEs realiza 16.384 MACs por ciclo de clock

### TPU v4 e v5p — Especificações

**TPU v4:**
- 275 TFLOPS em BF16
- 32 GB HBM2 por chip
- Interconect ICI (Inter-Chip Interconnect) via optical links — pods de 4096 chips
- Disponível no Google Cloud como v4-8 (1 chip), v4-32 (4 chips), v4-512 (64 chips)...

**TPU v5p (2024):**
- 459 TFLOPS em BF16
- HBM3 — maior bandwidth
- Melhor para modelos de escala trillion-parameter
- Pods de até 8960 chips interconectados

### XLA Compiler

Os TPUs não executam PyTorch diretamente — eles executam XLA (Accelerated Linear Algebra), uma IR (intermediate representation) que compila operações matemáticas em kernels otimizados para o systolic array.

**Fluxo de compilação:**
```
PyTorch/JAX code
      ↓
torch_xla / JAX JIT
      ↓
HLO (High-Level Operations) — IR intermediário
      ↓
XLA optimizer (fusão de ops, layout de memória)
      ↓
LLO (Low-Level Operations) — IR final
      ↓
Código nativo TPU
```

**JAX é o framework nativo para TPU.** JAX usa XLA por padrão e o design funcional (sem estado mutável) é naturalmente compatível com compilação estática.

### Limitações dos TPUs

- Operações não suportadas pelo XLA fazem fallback silencioso para CPU — pode ser catastrófico em performance sem perceber
- Frameworks PyTorch requerem `torch_xla`, que tem lag em relação à versão principal
- Debugging é mais difícil — XLA otimiza agressivamente e o trace de erros é opaco
- Apenas disponível via Google Cloud — sem on-premise para a maioria dos casos
- Compilação inicial (warmup) pode levar minutos

> [!warning] TPUs Requerem XLA
> Modelos PyTorch precisam de conversão via torch_xla. Operações não suportadas silenciosamente caem para CPU — o treinamento pode parecer funcionar mas rodar 50x mais lento sem aviso. Sempre profile antes de assumir que o TPU está sendo usado.

---

## Groq LPU — Language Processing Unit

### Deterministic Execution — O Diferencial

A maioria dos aceleradores tem latência variável: dependendo de como os dados chegam, quais kernels são agendados, como a memória está fragmentada, o tempo de resposta varia. Para aplicações web com SLAs de latência, isso é problemático.

O LPU (Language Processing Unit) da Groq foi projetado para ter **latência fixa e previsível** para qualquer input de tamanho determinado. Isso é possível porque:

1. **Nenhuma cache miss** — todos os pesos ficam em SRAM on-chip (80 MB por TSP)
2. **Execução sem runtime scheduling** — o compilador Groq pré-aloca cada operação a um ciclo de clock específico em tempo de compilação
3. **Sem DRAM** — elimina a variância da latência de acesso à memória externa

### TSP — Tensor Streaming Processor

O chip central da Groq é o TSP (Tensor Streaming Processor):

- **80 MB de SRAM on-chip** por chip — toda a memória ativa fica aqui
- Processamento em streams: pesos são transmitidos através dos cores em sequência, não carregados e descarregados repetidamente
- Clock determinístico: cada operação ocupa um número fixo de ciclos, conhecido em compilação

**Por que 80 MB SRAM e não HBM?**
- SRAM tem latência ~100x menor que HBM
- SRAM tem bandwidth muito maior em acesso aleatório
- Trade-off: SRAM é muito mais cara por GB — portanto chips Groq têm pouca memória mas extremamente rápida

**Para modelos grandes (70B+):** múltiplos chips são interconectados. O Llama 3 70B requer ~8 TSPs em paralelo.

### Performance

Em benchmarks públicos (2024-2025):
- **Llama 3 70B:** 500-800 tokens/segundo em p50 latência, versus ~40-100 t/s em GPU típica
- **Llama 3 8B:** 800-1200 tokens/segundo
- **Time to First Token (TTFT):** 100-300ms — crítico para aplicações interativas

Groq é especialmente valioso para:
- Aplicações de chat com SLA de latência < 500ms
- Pipelines de agentes onde cada step precisa ser rápido para não acumular latência
- Aplicações onde o custo é medido por token gerado (não por GPU-hora)

### Trade-offs do Groq

- **Somente inferência** — arquitetura não suporta backpropagation
- **Modelos pré-compilados** — cada modelo precisa de compilação específica para o TSP; só modelos que a Groq compilou estão disponíveis via API
- **Sem fine-tuning** — não é possível rodar modelos customizados facilmente
- **Custo por token pode ser alto** para workloads de baixo volume

> [!warning] Groq Não Suporta Treinamento
> O LPU é exclusivamente para inferência. Treine em GPU (A100/H100), faça fine-tuning normalmente, depois sirva via Groq para produção de baixa latência. As arquiteturas são complementares.

> [!warning] Vendor Lock-in
> Modelos compilados para o TSP da Groq não rodam em GPU sem recompilação. Avalie cuidadosamente o trade-off entre latência ultralow e portabilidade. Mantenha a capacidade de servir via vLLM/GPU como fallback.

---

## Cerebras WSE-3 — Wafer Scale Engine

### Por Que Wafer-Scale?

Chips convencionais são cortados (diced) de wafers de silício em unidades pequenas — um H100 tem ~814 mm². A Cerebras decidiu não cortar: o WSE-3 é um chip do tamanho de um wafer inteiro.

**WSE-3 specs:**
- **900.000 AI cores** — mais do que qualquer outro chip
- **44 GB de SRAM on-chip** — sem HBM, sem DRAM, tudo on-chip
- **125 PFLOPS em INT8** — pico teórico
- 21,5 trilhões de transistores (vs. 80 bilhões no H100)
- 900.000 mm² de silício (vs. ~814 mm² do H100)

### Por Que Wafer-Scale Elimina Interchip Latency

Em um cluster GPU convencional, comunicação entre GPUs passa por:
```
GPU A → NVLink → NVSwitch → PCIe → NVSwitch → NVLink → GPU B
```

Cada hop adiciona microsegundos. Para modelos que requerem sincronização frequente entre chips (como atenção em long context), isso é gargalo.

No WSE-3, todos os 900.000 cores estão no mesmo chip. Comunicação entre cores é via malha interna com latência de nanosegundos — 1000x menor que interchip.

**Caso de uso ideal:** Modelos gigantescos com comunicação all-to-all frequente, como atenção densa sem GQA, ou modelos de pesquisa com bilhões de parâmetros sendo desenvolvidos iterativamente.

**Limitação:** Custo e disponibilidade — WSE-3 está disponível via Cerebras Cloud ou como hardware físico de preço muito alto. Não é para startups ou uso individual.

---

## AWS Trainium/Inferentia 2

### AWS Trainium — Treinamento Econômico

O Trainium é o chip da AWS projetado especificamente para treinamento de modelos. Disponível em instâncias `trn1`:

- `trn1.2xlarge`: 1 Trainium chip, 32 GB de memória
- `trn1.32xlarge`: 16 Trainium chips, 512 GB de memória, NeuronLink interconnect

**Custo:** AWS afirma 60-70% de redução de custo vs. instâncias GPU equivalentes para cargas de treinamento. Benchmarks independentes confirmam economias de 40-65% dependendo do workload.

**Arquitetura:** Dois NeuronCores v2 por chip, cada um com:
- 1 MB on-chip SRAM por NeuronCore
- Suporte a BF16, FP32, FP8 e INT8
- HBM2 compartilhado entre NeuronCores

### AWS Inferentia 2 — Serving

Para inferência, as instâncias `inf2` usam o Inferentia 2:

- `inf2.xlarge`: 2 Inferentia chips
- `inf2.48xlarge`: 12 Inferentia chips, 384 GB memória total
- Custo por token inferido tipicamente 50-70% menor que instâncias GPU equivalentes

**NeuronLink:** Interconnect proprietário entre chips Inferentia — permite tensores > 16 GB serem shardados entre chips com baixa latência.

### AWS Neuron SDK

O ecossistema de software AWS para Trainium e Inferentia:

```python
# Compilar modelo PyTorch para Neuron
import torch
import torch_neuronx

# Modelo PyTorch normal
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B-Instruct")

# Compilar para Inferentia 2
traced_model = torch_neuronx.trace(
    model,
    example_inputs,
    compiler_workdir="./neuron_cache"
)

# Salvar e carregar modelo compilado
traced_model.save("llama3_8b_inf2.pt")
```

**Limitações do Neuron SDK:**
- Cobertura de operações menor que CUDA — operações não suportadas falham em compilação
- Tempo de compilação pode ser longo (minutos a horas para modelos grandes)
- Requer ajuste de configuração de sequence length e batch size em compilação

---

## Apple Neural Engine — Inferência Edge

### M4 Max e ANE

O Apple Neural Engine (ANE) é o processador especializado em inferência incluído em todos os chips Apple Silicon desde o M1. No M4 Max:

- **~38 TOPS** (Trillion Operations Per Second) em INT8
- Integrado no mesmo die que CPU, GPU e memória unificada
- Acessa a memória unificada diretamente — sem cópia CPU→GPU

**Vantagem crítica: VRAM Unificada**

No M4 Ultra (chip duplo): até 192 GB de VRAM unificada — CPU, GPU e ANE compartilham o mesmo pool de memória física. Um modelo de 70 GB pode ser carregado inteiro sem sharding entre dispositivos.

Comparação com GPU discreta:
| | M4 Ultra | NVIDIA RTX 4090 |
|---|---------|-----------------|
| VRAM total | 192 GB | 24 GB |
| Bandwidth | 800 GB/s | 1008 GB/s |
| Custo (2025) | ~$6.000 | ~$1.600 |
| TDP | 60-120W | 450W |

### MLX Framework

MLX é o framework de machine learning desenvolvido pela Apple especificamente para Apple Silicon:

- Lazy evaluation — operações não são executadas até necessário
- Automatic differentiation — suporta treino, não só inferência
- Funciona em CPU, GPU e ANE automaticamente
- API similar ao NumPy/JAX
- Otimizado para memória unificada — sem transferências explícitas entre dispositivos

**Modelos suportados:** A comunidade MLX-Community no HuggingFace mantém conversões de centenas de modelos.

### Privacidade Edge

O ANE processa dados localmente — nenhum dado sai do dispositivo. Para aplicações com dados sensíveis (saúde, jurídico, financeiro), isso é um diferencial que justifica o custo de desenvolvimento extra.

> [!tip] Apple Silicon para Desenvolvimento
> M3/M4 com MLX: modelos 13B confortáveis em 32-36 GB, modelos 70B viáveis com quantização INT4 em 64-96 GB. M4 Ultra com 192 GB roda Llama 3 405B quantizado. Para protótipos e desenvolvimento local, Apple Silicon é frequentemente a melhor relação custo-benefício vs. GPU discreta.

---

## Tenstorrent — A Aposta Open-Source

### Jim Keller e a Filosofia

Tenstorrent foi fundada por Jim Keller (conhecido por projetos como AMD Zen, Apple A4/A5, Tesla Dojo). A filosofia é diferente dos players anteriores: hardware open-source friendly, arquitetura que pode ser licenciada, e suporte a workloads além de LLMs.

### Wormhole e Blackhole

**Wormhole (2022):**
- 80 núcleos Tensix
- 12 GB GDDR6
- Mesh de Tensix cores interconectados em malha 2D
- RISC-V como instruction set nos Tensix cores

**Blackhole (2024-2025):**
- 140 núcleos Tensix
- Interface PCIe 5.0 e Ethernet 400G
- Múltiplos Blackhole podem ser interconectados peer-to-peer sem switch dedicado

### Arquitetura Tensix

Cada Tensix core é uma unidade computacional autônoma com:
- RISC-V processor para controle local
- Matrix Engine para GEMM
- Vector Engine para operações element-wise
- Roteador de malha — conecta ao Tensix adjacente diretamente

A malha 2D elimina a necessidade de um barramento compartilhado — comunicação é always ponto-a-ponto entre vizinhos. Para topologias de comunicação que se mapeiam bem em 2D (como o pipeline parallelism), isso é muito eficiente.

**TT-Metalium:** SDK de baixo nível para programar Tenstorrent diretamente
**TT-Buda:** Framework de alto nível (descontinuado), substituído por integração com PyTorch 2.0 via Compile

---

## Tabela Comparativa Completa

| Chip | Maker | TFLOPS FP16 | Memória | Melhor para |
|------|-------|-------------|---------|------------|
| H100 SXM | NVIDIA | 989 | 80 GB HBM3 | Treinamento geral |
| A100 80GB | NVIDIA | 312 | 80 GB HBM2e | Treinamento clássico |
| TPU v5p | Google | 459 | HBM | Treino JAX/TF em escala |
| Groq LPU | Groq | 230/chip | 80 MB SRAM | Inferência ultra-rápida |
| WSE-3 | Cerebras | 125.000 (INT8) | 44 GB SRAM | Modelos gigantes |
| Trainium 2 | AWS | ~190/chip | HBM | Treino econômico |
| Inferentia 2 | AWS | ~190/chip | HBM | Serving econômico |
| M4 Max ANE | Apple | ~38 TOPS INT8 | Unificada 128 GB | Edge/dev/privacidade |
| Blackhole | Tenstorrent | Em definição | GDDR6 | Open-source research |

---

## Código Prático

### 1. JAX em TPU — Google Colab

```python
# Rodar este código em Google Colab com runtime TPU
# Runtime → Change runtime type → TPU

import jax
import jax.numpy as jnp

# Verificar dispositivos TPU disponíveis
print(jax.devices())
# Saída esperada: [TpuDevice(id=0, ...), TpuDevice(id=1, ...), ...]

# Operação simples em TPU
x = jnp.ones((1024, 1024))
y = jnp.ones((1024, 1024))

# JIT compila automaticamente para XLA/TPU
@jax.jit
def matmul(a, b):
    return jnp.dot(a, b)

# Primeira chamada compila (warmup ~segundos)
result = matmul(x, y)
result.block_until_ready()  # Sincroniza para medir tempo real

# Chamadas subsequentes executam no TPU diretamente
import time
start = time.perf_counter()
for _ in range(100):
    result = matmul(x, y)
result.block_until_ready()
elapsed = time.perf_counter() - start
print(f"100 matmuls em {elapsed:.3f}s — {100/elapsed:.1f} ops/s")


# Exemplo com modelo real: inferência no TPU com JAX
from transformers import FlaxAutoModelForCausalLM, AutoTokenizer

# Carregar modelo em JAX (Flax) — nativo XLA
model_name = "google/gemma-2b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = FlaxAutoModelForCausalLM.from_pretrained(model_name, dtype=jnp.bfloat16)

# Distribuir entre todos os TPUs do pod
from jax.experimental import mesh_utils
from jax.sharding import Mesh, PartitionSpec, NamedSharding

# Criar mesh de dispositivos
devices = mesh_utils.create_device_mesh((len(jax.devices()),))
mesh = Mesh(devices, axis_names=('batch',))

# Sharding: distribuir batch entre TPUs
batch_sharding = NamedSharding(mesh, PartitionSpec('batch'))

prompt = "Vault Inc é uma empresa de tecnologia que"
inputs = tokenizer(prompt, return_tensors="jax")

# Inferência com JIT
@jax.jit
def generate_step(input_ids, params):
    return model(input_ids, params=params).logits

logits = generate_step(inputs['input_ids'], model.params)
next_token = jnp.argmax(logits[0, -1, :])
print(f"Next token: {tokenizer.decode(next_token)}")
```

### 2. Groq API Python — Medição de Latência

```python
import time
import statistics
from groq import Groq

client = Groq(api_key="sua-chave-aqui")  # ou GROQ_API_KEY env var

def measure_groq_latency(
    prompt: str,
    model: str = "llama-3.1-70b-versatile",
    max_tokens: int = 200,
    n_runs: int = 5
) -> dict:
    """
    Mede latência real da API Groq.

    Métricas coletadas:
    - TTFT: Time to First Token — latência percebida pelo usuário
    - Total time: tempo até último token
    - Tokens per second: throughput de geração
    """
    ttfts = []
    total_times = []
    throughputs = []

    for run in range(n_runs):
        start = time.perf_counter()

        # Streaming para medir TTFT
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stream=True,
        )

        first_token_time = None
        output_tokens = 0

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                output_tokens += 1

        end = time.perf_counter()

        ttft = (first_token_time - start) * 1000  # ms
        total_time = (end - start) * 1000  # ms
        tps = output_tokens / (end - start)

        ttfts.append(ttft)
        total_times.append(total_time)
        throughputs.append(tps)

        # Respeitar rate limits
        if run < n_runs - 1:
            time.sleep(0.5)

    return {
        "model": model,
        "runs": n_runs,
        "ttft_ms": {
            "p50": statistics.median(ttfts),
            "mean": statistics.mean(ttfts),
            "min": min(ttfts),
            "max": max(ttfts),
        },
        "total_ms": {
            "p50": statistics.median(total_times),
            "mean": statistics.mean(total_times),
        },
        "tokens_per_second": {
            "p50": statistics.median(throughputs),
            "mean": statistics.mean(throughputs),
        }
    }


# Uso
results = measure_groq_latency(
    prompt="Explique como funciona um transformer em 3 parágrafos.",
    model="llama-3.1-70b-versatile",
    n_runs=5
)

print(f"Modelo: {results['model']}")
print(f"TTFT p50: {results['ttft_ms']['p50']:.1f}ms")
print(f"TTFT média: {results['ttft_ms']['mean']:.1f}ms")
print(f"Throughput p50: {results['tokens_per_second']['p50']:.0f} t/s")
```

### 3. MLX no Apple Silicon — Rodar Modelo Local

```python
# Requer: pip install mlx-lm
# Funciona apenas em Apple Silicon (M1/M2/M3/M4)

from mlx_lm import load, generate
import time

def run_mlx_model(
    model_name: str = "mlx-community/Llama-3.2-3B-Instruct-4bit",
    prompt: str = "O que é um transformer?",
    max_tokens: int = 200,
    temperature: float = 0.7,
) -> dict:
    """
    Executa inferência com MLX no Apple Silicon.

    O modelo roda no Neural Engine + GPU usando memória unificada.
    Não há cópia CPU→GPU — tudo compartilha o mesmo pool de memória.
    """
    print(f"Carregando {model_name}...")
    load_start = time.perf_counter()

    model, tokenizer = load(model_name)

    load_time = time.perf_counter() - load_start
    print(f"Modelo carregado em {load_time:.1f}s")

    # Preparar prompt no formato correto
    if hasattr(tokenizer, 'apply_chat_template'):
        messages = [{"role": "user", "content": prompt}]
        formatted = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    else:
        formatted = prompt

    # Geração com medição de performance
    gen_start = time.perf_counter()

    response = generate(
        model,
        tokenizer,
        prompt=formatted,
        max_tokens=max_tokens,
        temp=temperature,
        verbose=False,  # True mostra tokens em tempo real
    )

    gen_time = time.perf_counter() - gen_start
    n_tokens = len(tokenizer.encode(response))
    tps = n_tokens / gen_time

    return {
        "response": response,
        "tokens_generated": n_tokens,
        "generation_time_s": gen_time,
        "tokens_per_second": tps,
        "model": model_name,
    }


# Exemplo de uso
result = run_mlx_model(
    model_name="mlx-community/Llama-3.2-3B-Instruct-4bit",
    prompt="Explique o trade-off entre hardware especializado e GPUs para IA.",
    max_tokens=300,
)

print(f"\nResposta: {result['response']}")
print(f"\nPerformance:")
print(f"  Tokens gerados: {result['tokens_generated']}")
print(f"  Tempo: {result['generation_time_s']:.2f}s")
print(f"  Throughput: {result['tokens_per_second']:.1f} t/s")


# Listar modelos disponíveis na MLX Community
def list_available_mlx_models(size_filter: str = None) -> list:
    """
    Modelos populares disponíveis via mlx-community no HuggingFace.
    Instale com: from mlx_lm import load; load("mlx-community/<nome>")
    """
    models = [
        # Llama 3.x
        "mlx-community/Llama-3.2-1B-Instruct-4bit",
        "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
        "mlx-community/Meta-Llama-3.1-70B-Instruct-4bit",  # requer 64+ GB RAM
        # Mistral
        "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
        # Qwen
        "mlx-community/Qwen2.5-7B-Instruct-4bit",
        "mlx-community/Qwen2.5-14B-Instruct-4bit",
        # Phi-3
        "mlx-community/Phi-3.5-mini-instruct-4bit",
        # Gemma
        "mlx-community/gemma-2-9b-it-4bit",
    ]
    if size_filter:
        models = [m for m in models if size_filter in m]
    return models
```

### 4. Comparar Latência: Groq vs OpenAI API

```python
import time
import asyncio
import statistics
from groq import Groq
from openai import OpenAI
from typing import Literal

groq_client = Groq()
openai_client = OpenAI()

async def benchmark_latency(
    prompt: str,
    n_runs: int = 5,
    max_tokens: int = 150,
) -> dict:
    """
    Compara latência entre Groq e OpenAI API.

    Mede TTFT (Time to First Token) e throughput.
    Ambos em modo streaming para capturar TTFT real.
    """

    def measure_openai(prompt: str, max_tokens: int) -> dict:
        start = time.perf_counter()
        stream = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stream=True,
        )
        first_token_t = None
        token_count = 0
        for chunk in stream:
            if chunk.choices[0].delta.content:
                if first_token_t is None:
                    first_token_t = time.perf_counter()
                token_count += 1
        end = time.perf_counter()
        return {
            "ttft_ms": (first_token_t - start) * 1000,
            "total_ms": (end - start) * 1000,
            "tps": token_count / (end - start),
        }

    def measure_groq(prompt: str, max_tokens: int) -> dict:
        start = time.perf_counter()
        stream = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stream=True,
        )
        first_token_t = None
        token_count = 0
        for chunk in stream:
            if chunk.choices[0].delta.content:
                if first_token_t is None:
                    first_token_t = time.perf_counter()
                token_count += 1
        end = time.perf_counter()
        return {
            "ttft_ms": (first_token_t - start) * 1000,
            "total_ms": (end - start) * 1000,
            "tps": token_count / (end - start),
        }

    # Coletar runs para cada API
    groq_results = []
    openai_results = []

    for i in range(n_runs):
        print(f"Run {i+1}/{n_runs}...")
        groq_results.append(measure_groq(prompt, max_tokens))
        time.sleep(0.3)
        openai_results.append(measure_openai(prompt, max_tokens))
        time.sleep(0.3)

    def summarize(results: list) -> dict:
        return {
            "ttft_p50_ms": statistics.median(r["ttft_ms"] for r in results),
            "ttft_mean_ms": statistics.mean(r["ttft_ms"] for r in results),
            "total_p50_ms": statistics.median(r["total_ms"] for r in results),
            "tps_p50": statistics.median(r["tps"] for r in results),
        }

    groq_summary = summarize(groq_results)
    openai_summary = summarize(openai_results)

    print("\n=== RESULTADO ===")
    print(f"{'Métrica':<25} {'Groq (Llama 70B)':<20} {'OpenAI (gpt-4o-mini)'}")
    print("-" * 70)
    print(f"{'TTFT p50 (ms)':<25} {groq_summary['ttft_p50_ms']:<20.1f} {openai_summary['ttft_p50_ms']:.1f}")
    print(f"{'TTFT média (ms)':<25} {groq_summary['ttft_mean_ms']:<20.1f} {openai_summary['ttft_mean_ms']:.1f}")
    print(f"{'Total p50 (ms)':<25} {groq_summary['total_p50_ms']:<20.1f} {openai_summary['total_p50_ms']:.1f}")
    print(f"{'Tokens/s p50':<25} {groq_summary['tps_p50']:<20.0f} {openai_summary['tps_p50']:.0f}")

    speedup_ttft = openai_summary["ttft_p50_ms"] / groq_summary["ttft_p50_ms"]
    speedup_tps = groq_summary["tps_p50"] / openai_summary["tps_p50"]
    print(f"\nGroq é {speedup_ttft:.1f}x mais rápido em TTFT")
    print(f"Groq gera {speedup_tps:.1f}x mais tokens por segundo")

    return {
        "groq": groq_summary,
        "openai": openai_summary,
        "speedup_ttft": speedup_ttft,
        "speedup_tps": speedup_tps,
    }


# Uso
if __name__ == "__main__":
    asyncio.run(benchmark_latency(
        prompt="Liste 5 vantagens de usar hardware especializado para inferência de LLMs.",
        n_runs=5,
        max_tokens=150,
    ))
```

---

> [!info] Futuro Heterogêneo
> A arquitetura ideal de produção combina especialistas: GPU para treino e fine-tuning, Groq ou Inferentia para serving de baixa latência, ANE para edge com privacidade. Arquitete para portabilidade desde o início — use abstrações como vLLM ou LiteLLM que permitem trocar o backend sem mudar o código da aplicação.

---

## Referências

- [Google TPU v4 Whitepaper](https://arxiv.org/abs/2304.01433) — arquitetura systolic array e ICI
- [Groq Architecture Overview](https://wow.groq.com/groq-isca-paper-2022/) — TSP e deterministic execution
- [Cerebras WSE-3 Announcement](https://www.cerebras.net/chip/) — specs completos
- [AWS Neuron Documentation](https://awsdocs-neuron.readthedocs-hosted.com/) — SDK e guias
- [Apple MLX GitHub](https://github.com/ml-explore/mlx) — framework para Apple Silicon
- [Tenstorrent Wormhole](https://tenstorrent.com/hardware/wormhole) — Tensix core architecture

---

## Relacionado

- [[gpu-architecture]] — base para entender o que hardware especializado está otimizando
- [[vram-estimation]] — calcular requisitos de memória para cada plataforma
- [[inference-engines]] — software layer que roda sobre o hardware
- [[pretraining]] — context de onde treinamento acontece (GPU/TPU, não Groq)
