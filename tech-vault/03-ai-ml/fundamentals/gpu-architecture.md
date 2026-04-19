---
tags: [ai-ml, fundamentals, gpu, cuda, hardware, nvidia]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [GPU Architecture, CUDA, Tensor Cores, GPU for AI]
---

# GPU Architecture para AI

## Overview

GPUs dominam workloads de AI por uma razão fundamental: **paralelismo massivo**. Uma CPU moderna tem 8–64 cores altamente otimizados para execução sequencial e latência baixa. Uma GPU tem milhares de cores menores, projetados para executar a mesma instrução em milhares de dados simultaneamente (SIMD/SIMT).

O trade-off é intencional: uma GPU é terrível para código sequencial com muitos branches, mas é extraordinariamente eficiente para álgebra linear — que é exatamente o que redes neurais fazem. Multiplicação de matrizes, convolução, operações element-wise em tensores gigantescos: tudo isso é paralelismo de dados puro.

Para contexto, um modelo Llama 3 70B em BF16 requer ~1.4 × 10¹⁵ FLOPs por token gerado. Em uma CPU de 1 TFLOP, isso seria 1.4ms por token — antes de qualquer overhead. Uma GPU H100 com 989 TFLOPS em FP16 resolve isso em microssegundos, desde que a memória seja suficientemente rápida.

Integra com [[specialized-hardware]], [[vram-estimation]], [[inference-engines]], [[kv-cache-attention]] e [[quantization]].

---

## Hierarquia de Execução CUDA

### Estrutura Completa

```
GPU
└── Streaming Multiprocessors (SM)
    ├── Registros (~256KB por SM)
    ├── Shared Memory / L1 Cache (128KB por SM, configurável)
    ├── CUDA Cores (128 por SM em Ampere)
    ├── Tensor Cores (4 por SM em Ampere, 4 por SM em Hopper)
    ├── INT32 Units (64 por SM em Ampere)
    ├── Special Function Units (SFUs) — sin, cos, sqrt
    └── Warps (grupos de 32 threads)
        └── CUDA Threads (32 por warp)
```

Uma GPU A100 tem 108 SMs. Uma H100 SXM tem 132 SMs. Cada SM é uma fábrica de computação independente com sua própria memória compartilhada e scheduler de threads.

### Warps: A Unidade Fundamental de Execução

Um **warp** é um grupo de 32 threads que executam exatamente a mesma instrução ao mesmo tempo — isso é o que SIMT (Single Instruction Multiple Threads) significa. O hardware não tem como executar threads diferentes de um mesmo warp em instruções diferentes: elas são literalmente sincronizadas em hardware.

Implicações práticas:

- **Lançar 64 threads**: usa 2 warps → 64 CUDA cores ativos
- **Lançar 33 threads**: usa 2 warps → 32 CUDA cores eficientes + 1 thread real no segundo warp, mas o hardware ainda executa 32 ciclos
- **Regra prática**: dimensionar blocos em múltiplos de 32

O warp scheduler do SM mantém múltiplos warps prontos para execução e faz context switching entre eles em zero ciclos (hardware, sem custo). Isso é o mecanismo pelo qual GPUs escondem latência de memória: enquanto um warp espera dados da VRAM (600 ciclos de latência), outro warp que já tem seus dados executa.

### Warp Divergence

Warp divergence ocorre quando threads dentro de um mesmo warp tomam caminhos diferentes de execução (if/else, loops com diferentes iterações):

```cuda
// Exemplo de divergência SEVERA
__global__ void bad_kernel(float* data, int* masks, float* out) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    
    if (masks[tid] > 0) {          // Condição diferente por thread!
        out[tid] = sqrt(data[tid]); // Metade das threads executa isto
    } else {
        out[tid] = data[tid] * 2.0f; // Outra metade executa isto
    }
    // Resultado: 2x mais ciclos — ambos os paths são executados
    // sequencialmente com masking. 50% da capacidade desperdiçada.
}
```

O hardware executa **ambos os caminhos** sequencialmente, mascarando (desativando) as threads que não deveriam executar cada path. Performance efetiva: reduzida pela fração de threads no path minoritário.

```cuda
// Versão sem divergência — todas as threads fazem a mesma operação
__global__ void good_kernel(float* data, float* masks_f, float* out) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    
    // Branchless: usa aritmética para evitar divergência
    float mask = masks_f[tid]; // 0.0 ou 1.0, carregado uniformemente
    out[tid] = mask * sqrt(data[tid]) + (1.0f - mask) * data[tid] * 2.0f;
    // Todas as threads fazem a mesma instrução — zero divergência
}
```

> [!warning] Warp Divergence em Attention
> Implementações ingênuas de attention com masking criam divergência de warp quando threads diferentes têm máscaras diferentes (padding masks, causal masks). Flash Attention resolve isso computando atenção por tiles homogêneos: todas as threads de um tile processam posições dentro do mesmo bloco, eliminando divergência causada por masking de sequência variável.

### Ocupância (Occupancy)

Ocupância é a fração de warps ativos vs o máximo possível por SM:

```
Ocupância = warps_ativos / warps_máximos_por_SM
```

Para uma A100 SM: máximo de 64 warps simultâneos. Se seu kernel ativa apenas 16 warps por SM, ocupância = 25%.

Fatores que limitam ocupância:
1. **Registros por thread**: cada thread usa X registros; SM tem 256K registros. Se thread usa 64 registros, máximo de 256K/64 = 4096 threads = 128 warps — mas SM suporta apenas 64, então registros não são o gargalo neste caso
2. **Shared memory por bloco**: SM tem 128KB. Se cada bloco usa 32KB, máximo de 4 blocos por SM
3. **Threads por bloco**: mínimo de 128 threads para usar um SM completamente (4 warps; máximo é 2048 threads)

Alta ocupância não garante alta performance, mas baixa ocupância geralmente indica que você não está escondendo latência de memória.

---

## CUDA Cores vs Tensor Cores

### CUDA Cores

Um CUDA Core executa **uma operação de ponto flutuante por ciclo**: multiplicação, adição, ou fused multiply-add (FMA). Para FP32:

```
Throughput = SMs × CUDA_cores_por_SM × clock_GHz × 2 (FMA conta como 2 FLOPs)

A100: 108 SMs × 64 FP32_cores × 1.41 GHz × 2 = ~19.5 TFLOPS FP32
```

CUDA Cores são essenciais para operações que não são matrix multiply: element-wise ops, reductions, indexing.

### Tensor Cores

Tensor Cores são circuitos de silício dedicados exclusivamente a multiplicação de matrizes. A operação básica é um WMMA (Warp-level Matrix Multiply-Accumulate):

| Geração | Operação | Tipos Suportados | Speedup vs FP32 |
|---------|---------|-----------------|----------------|
| 1ª (Volta, V100) | 4×4×4 | FP16 | 8x |
| 2ª (Turing, RTX 2080) | 8×8×4 | FP16, INT8, INT4 | 8x FP16 |
| 3ª (Ampere, A100) | 8×4×8 | FP16, BF16, TF32, INT8 | 16x TF32, 8x FP16 |
| 4ª (Hopper, H100) | 8×8×4+ | FP16, BF16, FP8, INT8 | 32x com FP8 |

Em Ampere (A100), um único Tensor Core executa uma multiplicação 8×4×8 por ciclo, o equivalente a 256 operações FP16 — vs 2 operações de um CUDA Core FP32.

### API de Baixo Nível: WMMA

```cuda
// WMMA API — acessando Tensor Cores diretamente em CUDA
#include <mma.h>
using namespace nvcuda;

__global__ void tensorcore_gemm(
    half* A, half* B, float* C,
    int M, int N, int K
) {
    // Fragmentos de warp (16×16×16 para Ampere)
    wmma::fragment<wmma::matrix_a, 16, 16, 16, half, wmma::row_major> a_frag;
    wmma::fragment<wmma::matrix_b, 16, 16, 16, half, wmma::col_major> b_frag;
    wmma::fragment<wmma::accumulator, 16, 16, 16, float> c_frag;
    
    wmma::fill_fragment(c_frag, 0.0f);
    
    // Carregar tiles de 16×16 da memória global
    wmma::load_matrix_sync(a_frag, A, K);
    wmma::load_matrix_sync(b_frag, B, N);
    
    // Executar GEMM em Tensor Core — um ciclo de hardware
    wmma::mma_sync(c_frag, a_frag, b_frag, c_frag);
    
    // Armazenar resultado
    wmma::store_matrix_sync(C, c_frag, N, wmma::mem_row_major);
}
```

### Habilitar Tensor Cores em PyTorch

Em Python, você não precisa escrever CUDA para usar Tensor Cores. PyTorch os utiliza automaticamente para GEMM quando os tipos de dados e dimensões são compatíveis:

```python
import torch

# Habilitar TF32 (usa Tensor Cores para FP32 inputs com precisão reduzida)
# Padrão no PyTorch >= 1.12 para matmul
torch.backends.cuda.matmul.allow_tf32 = True

# Habilitar TF32 para convoluções também
torch.backends.cudnn.allow_tf32 = True

# Verificar se Tensor Cores estão sendo usados (requer precisão FP16/BF16)
device = torch.device("cuda")

# FP16: usa Tensor Cores em qualquer GPU Volta+
A = torch.randn(4096, 4096, dtype=torch.float16, device=device)
B = torch.randn(4096, 4096, dtype=torch.float16, device=device)

# Este GEMM usa Tensor Cores automaticamente
with torch.cuda.amp.autocast():
    C = torch.matmul(A, B)

# BF16: usa Tensor Cores em Ampere+ (melhor para treinamento — mesmo range que FP32)
A_bf16 = A.to(torch.bfloat16)
B_bf16 = B.to(torch.bfloat16)
C_bf16 = torch.matmul(A_bf16, B_bf16)  # Tensor Cores em A100/H100

print(f"Resultado: {C_bf16.shape}, dtype={C_bf16.dtype}")
```

```python
# Benchmark: CUDA Core FP32 vs Tensor Core FP16 vs BF16
import torch
import time

device = torch.device("cuda")
N = 4096
n_trials = 100

def benchmark_matmul(dtype, n_trials=100):
    A = torch.randn(N, N, dtype=dtype, device=device)
    B = torch.randn(N, N, dtype=dtype, device=device)
    
    # Warmup
    for _ in range(10):
        _ = torch.matmul(A, B)
    torch.cuda.synchronize()
    
    start = time.perf_counter()
    for _ in range(n_trials):
        _ = torch.matmul(A, B)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    
    flops = 2 * N**3 * n_trials  # 2 FLOPs por multiply-add
    tflops = flops / elapsed / 1e12
    return tflops

fp32_tflops = benchmark_matmul(torch.float32)
fp16_tflops = benchmark_matmul(torch.float16)
bf16_tflops = benchmark_matmul(torch.bfloat16)

print(f"FP32 (CUDA Cores):  {fp32_tflops:.1f} TFLOPS")
print(f"FP16 (Tensor Cores): {fp16_tflops:.1f} TFLOPS")
print(f"BF16 (Tensor Cores): {bf16_tflops:.1f} TFLOPS")
# Resultado típico em A100:
# FP32:  19.5 TFLOPS
# FP16:  77.6 TFLOPS (4x mais, pois Tensor Cores)
# BF16:  77.6 TFLOPS (mesmo hardware)
```

> [!tip] RTX 4090 para Desenvolvimento
> Para desenvolvimento local, a RTX 4090 oferece o melhor custo-benefício: 24GB VRAM, 1008 GB/s bandwidth, Tensor Cores de 4ª geração com suporte a FP8. Suficiente para inferência de modelos até 13B em FP16 e fine-tuning com QLoRA de modelos até 70B com offloading para CPU RAM. O custo (~$1600) amortiza rapidamente vs cloud (H100 a $4-8/hora = ~200-400 horas de breakeven).

---

## Hierarquia de Memória

A performance de qualquer kernel CUDA é determinada pela hierarquia de memória. Entender os trade-offs é fundamental.

### Tabela Completa

| Tipo | Tamanho | Bandwidth | Latência | Scope | Gerenciamento |
|------|---------|-----------|---------|-------|---------------|
| Registros | ~256KB/SM | ~40 TB/s | ~1 ciclo | Thread | Compilador |
| L1 / Shared Mem | 128KB/SM | ~19 TB/s | ~30 ciclos | SM | Programador (shared) / HW (L1) |
| L2 Cache | 40-80MB | ~5 TB/s | ~200 ciclos | GPU | Hardware |
| HBM (VRAM) | 40-192GB | 0.9-3.35 TB/s | ~600 ciclos | GPU | Programador |
| CPU RAM (via PCIe) | TBs | ~32 GB/s | ms | Sistema | Sistema Operacional |
| NVMe SSD | TBs | ~7 GB/s | 100µs-1ms | Sistema | Sistema Operacional |

### Shared Memory: Gerenciamento Manual

Shared memory é SRAM on-chip alocada manualmente pelo programador. Ela persiste durante a vida de um bloco de threads e é compartilhada entre todos os threads do bloco. O uso canônico é reduzir acessos à HBM carregando dados em shared memory uma vez e reutilizando múltiplas vezes.

```cuda
// Matrix multiply com tiling usando shared memory
// Reduz acessos à HBM de O(N³) para O(N³/TILE_SIZE)
#define TILE_SIZE 32

__global__ void tiled_matmul(
    float* A, float* B, float* C,
    int N
) {
    // Tiles em shared memory — carregados da HBM uma vez
    __shared__ float tile_A[TILE_SIZE][TILE_SIZE];
    __shared__ float tile_B[TILE_SIZE][TILE_SIZE];
    
    int row = blockIdx.y * TILE_SIZE + threadIdx.y;
    int col = blockIdx.x * TILE_SIZE + threadIdx.x;
    float sum = 0.0f;
    
    for (int t = 0; t < N / TILE_SIZE; t++) {
        // Cada thread carrega um elemento do tile — acesso coalescido
        tile_A[threadIdx.y][threadIdx.x] = A[row * N + t * TILE_SIZE + threadIdx.x];
        tile_B[threadIdx.y][threadIdx.x] = B[(t * TILE_SIZE + threadIdx.y) * N + col];
        
        __syncthreads(); // Garantir que o tile está completo antes de usar
        
        // Computar produto parcial — acessos à shared memory, não HBM
        for (int k = 0; k < TILE_SIZE; k++) {
            sum += tile_A[threadIdx.y][k] * tile_B[k][threadIdx.x];
        }
        
        __syncthreads(); // Antes de sobrescrever os tiles com próxima iteração
    }
    
    if (row < N && col < N) {
        C[row * N + col] = sum;
    }
}
```

**Flash Attention e Shared Memory**: Flash Attention (arxiv:2205.14135) é o exemplo mais importante de uso de shared memory em AI. O algoritmo divide a matriz de atenção n×n em tiles que cabem em shared memory, evitando múltiplos round-trips para HBM. Para sequências de 4096 tokens em FP16, a matriz de atenção completa seria 4096×4096×2 = 32MB — muito grande para L1/shared memory, mas Flash Attention a processa em tiles de ~64×64 (~8KB) que cabem confortavelmente.

> [!info] HBM vs GDDR6X
> HBM (High Bandwidth Memory) é empilhado em silício (3D stacking), oferece maior bandwidth que GDDR6X mas é muito mais caro de fabricar. H100 SXM com HBM3 tem 3.35 TB/s vs RTX 4090 com GDDR6X e ~1.0 TB/s — 3.3x mais bandwidth. Para workloads memory-bound como inferência de LLMs em batch pequeno, essa diferença é diretamente proporcional ao throughput. Para workloads compute-bound (treinamento com batch grande), a diferença é menos crítica pois o gargalo é nos FLOPS, não na memória.

> [!warning] VRAM Reportada ≠ VRAM Disponível
> O driver CUDA reserva ~500MB-1GB para contexto e outras alocações. Em sistemas com display conectado à GPU (modo desktop), mais VRAM é usada pelo driver gráfico (podendo chegar a 1-2GB adicionais). Sempre subtraia ~1GB do total reportado ao planejar capacidade. Use `torch.cuda.get_device_properties(0).total_memory` para ver o total físico e `torch.cuda.memory_reserved()` vs `torch.cuda.memory_allocated()` para ver uso real.

---

## Arithmetic Intensity e Roofline Model

### Conceito

A **Arithmetic Intensity** de uma operação mede quantas operações de computação são realizadas por byte de memória transferida:

```
Arithmetic Intensity (FLOPs/byte) = Total_FLOPs / Total_Bytes_HBM
```

O **Roofline Model** compara a arithmetic intensity de uma operação com o "ponto de equilíbrio" do hardware:

```
Roofline breakpoint = Peak_FLOPs / Peak_Bandwidth

H100 SXM:
  Peak FP16 = 989 TFLOPS = 989 × 10¹² FLOPs/s
  Peak Bandwidth = 3.35 TB/s = 3.35 × 10¹² bytes/s
  Breakpoint = 989 / 3.35 ≈ 295 FLOPs/byte

A100 80GB:
  Peak FP16 = 312 TFLOPS (sem sparsity)
  Peak Bandwidth = 2.0 TB/s
  Breakpoint = 312 / 2.0 = 156 FLOPs/byte

RTX 4090:
  Peak FP16 = 82.6 TFLOPS
  Peak Bandwidth = 1.008 TB/s
  Breakpoint = 82.6 / 1.008 ≈ 82 FLOPs/byte
```

### Memory-bound vs Compute-bound

```
Se arithmetic_intensity < breakpoint → Memory-bound
  Performance = intensity × bandwidth
  
Se arithmetic_intensity > breakpoint → Compute-bound
  Performance = peak_flops
```

### Análise de Operações em Transformers

```python
# Calculando arithmetic intensity de operações-chave

def arithmetic_intensity(op_name: str, params: dict) -> float:
    """Calcula FLOPs/byte para operações comuns em transformers."""
    
    if op_name == "matrix_vector_multiply":
        # y = Wx: M×N × N×1 → M×1
        M, N = params["M"], params["N"]
        dtype_bytes = params.get("dtype_bytes", 2)  # BF16 default
        
        flops = 2 * M * N  # N MACs por output element, M outputs
        bytes_read = (M * N + N) * dtype_bytes  # W + x
        bytes_write = M * dtype_bytes  # y
        total_bytes = bytes_read + bytes_write
        
        return flops / total_bytes
    
    elif op_name == "matrix_matrix_multiply":
        # C = AB: M×K × K×N → M×N
        M, K, N = params["M"], params["K"], params["N"]
        dtype_bytes = params.get("dtype_bytes", 2)
        
        flops = 2 * M * K * N
        bytes_io = (M * K + K * N + M * N) * dtype_bytes
        
        return flops / bytes_io
    
    elif op_name == "softmax":
        # Softmax: 5 operações por elemento (exp, sum, div, etc.)
        seq_len, d = params["seq_len"], params["d"]
        dtype_bytes = params.get("dtype_bytes", 2)
        
        flops = 5 * seq_len * d
        bytes_io = 2 * seq_len * d * dtype_bytes  # read + write
        
        return flops / bytes_io
    
    elif op_name == "elementwise_gelu":
        # GELU ≈ 8 FLOPs por elemento
        n = params["n"]
        dtype_bytes = params.get("dtype_bytes", 2)
        
        flops = 8 * n
        bytes_io = 2 * n * dtype_bytes
        
        return flops / bytes_io

# Exemplos práticos
# Inferência batch=1: matrix-vector (attention projection)
mv_intensity = arithmetic_intensity("matrix_vector_multiply", {
    "M": 4096, "N": 4096, "dtype_bytes": 2
})
print(f"Matrix-vector (batch=1): {mv_intensity:.1f} FLOPs/byte")
# ≈ 1.3 FLOPs/byte — FORTEMENTE memory-bound em qualquer GPU

# Treinamento batch=128: matrix-matrix
mm_intensity = arithmetic_intensity("matrix_matrix_multiply", {
    "M": 128 * 4096, "K": 4096, "N": 4096, "dtype_bytes": 2
})
print(f"Matrix-matrix (batch=128): {mm_intensity:.1f} FLOPs/byte")
# ≈ 273 FLOPs/byte — compute-bound na H100 (breakpoint=295), memory-bound no A100

# Softmax
sm_intensity = arithmetic_intensity("softmax", {
    "seq_len": 4096, "d": 4096, "dtype_bytes": 2
})
print(f"Softmax: {sm_intensity:.1f} FLOPs/byte")
# ≈ 1.25 FLOPs/byte — extremamente memory-bound

# GELU
gelu_intensity = arithmetic_intensity("elementwise_gelu", {
    "n": 4096 * 11008, "dtype_bytes": 2
})
print(f"GELU: {gelu_intensity:.1f} FLOPs/byte")
# ≈ 2.0 FLOPs/byte — memory-bound
```

**Conclusão prática**: inferência de LLMs em batch=1 é quase inteiramente memory-bound. A GPU mais rápida para inferência single-request é a que tem maior bandwidth de HBM, não maior FLOPS. A H100 tem 3.35 TB/s vs 2.0 TB/s da A100 → ~1.7x mais rápida para inferência em batch pequeno, independente dos FLOPS adicionais.

---

## Comparativo de GPUs

| GPU | VRAM | Bandwidth | FP16 TFLOPS | Tensor Gen | TDP | Tier |
|-----|------|-----------|------------|-----------|-----|------|
| RTX 3090 | 24GB GDDR6X | 936 GB/s | 35.6 | 3ª (Ampere) | 350W | Consumer |
| RTX 4090 | 24GB GDDR6X | 1008 GB/s | 82.6 | 4ª (Ada) | 450W | Consumer |
| A100 40GB | 40GB HBM2e | 1555 GB/s | 77.6 | 3ª (Ampere) | 400W | Data Center |
| A100 80GB | 80GB HBM2e | 2000 GB/s | 77.6 | 3ª (Ampere) | 400W | Data Center |
| H100 SXM | 80GB HBM3 | 3350 GB/s | 989* | 4ª (Hopper) | 700W | Data Center |
| H100 NVL | 188GB HBM3e | 7400 GB/s | 1979* | 4ª (Hopper) | 1000W | Data Center |
| L40S | 48GB GDDR6 | 864 GB/s | 362 | 4ª (Ada) FP8 | 350W | Data Center |
| GH200 | 96GB HBM3 | 4000 GB/s | 1979* | 4ª (Hopper) | 900W | Data Center |

*FP16 com sparsity estruturada 2:4

**Notas importantes sobre as specs:**

- **RTX 4090 vs A100 40GB em inferência**: Bandwidth é o que importa. A100 40GB tem 1555 GB/s vs RTX 4090's 1008 GB/s → A100 é ~1.5x mais rápida para inferência single-request mesmo com FP16 TFLOPS similares
- **H100 NVL**: é na realidade 2× H100 em um único módulo (dual-die), projetado para servir LLMs de 70B+ em formato full FP16
- **L40S**: posicionado como "A100 replacement" para workloads mistas; tem GDDR6 (menor bandwidth que HBM) mas é muito mais barato

---

## NVLink e Multi-GPU

### O Problema do PCIe para AI

PCIe 4.0 x16 oferece 32 GB/s bidirecional (16 GB/s por direção). Para tensor parallelism em transformers, **all-reduce** é executado a cada camada do modelo — uma operação de comunicação coletiva que requer que todas as GPUs compartilhem gradients ou ativações.

Para um modelo com d_model=8192 em BF16 (2 bytes), um all-reduce em cada camada transmite:
```
bytes_por_all_reduce = 2 × d_model × batch × seq_len × 2 bytes
= 2 × 8192 × 1 × 4096 × 2 = 134 MB por all-reduce
```

Com PCIe a 16 GB/s, isso leva ~8ms. Com NVLink 4.0 a 450 GB/s, leva ~0.3ms. Para um modelo com 80 camadas, PCIe adiciona 640ms de latência de comunicação por token — inaceitável.

> [!warning] PCIe para Multi-GPU é Insuficiente para Tensor Parallelism
> Para tensor parallelism (all-reduce a cada camada), PCIe 4.0 x16 (~32 GB/s) cria um gargalo severo. Para um modelo onde o all-reduce é feito a cada camada e cada all-reduce transmite ~100MB, PCIe é 10-20x mais lento que NVLink. Use pipeline parallelism (menos comunicação, executado entre camadas, não dentro delas) se NVLink não estiver disponível — aceitável para treinamento, problemático para inferência.

### NVLink e NVSwitch

```
NVLink 4.0 (Hopper, H100):
  - 18 links por GPU
  - 50 GB/s por link (bidirecional)
  - Total: 900 GB/s por chip

NVSwitch 3.0 (DGX H100):
  - Conecta 8 GPUs H100 em all-to-all
  - Bandwidth efetiva: 900 GB/s por GPU para qualquer destino
  - Sem degradação para comunicação não-local

DGX H100:
  - 8× H100 SXM
  - 640GB VRAM total
  - NVLink all-to-all entre todas as 8 GPUs
  - Pode servir um modelo de 640GB em FP16 ou 1.28TB em INT4
```

### Multi-GPU com PyTorch

```python
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP

def setup_distributed(rank: int, world_size: int):
    """Inicializar processo de comunicação distribuída."""
    dist.init_process_group(
        backend="nccl",     # NCCL é o backend ideal para GPUs NVIDIA
        rank=rank,
        world_size=world_size
    )
    torch.cuda.set_device(rank)

def cleanup_distributed():
    dist.destroy_process_group()

def train_distributed(rank: int, world_size: int, model_config: dict):
    """Treinamento distribuído com DDP."""
    setup_distributed(rank, world_size)
    
    # Modelo vai para a GPU correta
    device = torch.device(f"cuda:{rank}")
    model = SimpleTransformer(**model_config).to(device)
    
    # DDP: sincroniza gradients via all-reduce após cada backward
    model = DDP(model, device_ids=[rank])
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    # Training loop normal — DDP cuida da comunicação automaticamente
    for batch in get_dataloader(rank, world_size):
        inputs, targets = batch
        inputs, targets = inputs.to(device), targets.to(device)
        
        outputs = model(inputs)
        loss = compute_loss(outputs, targets)
        
        optimizer.zero_grad()
        loss.backward()  # Aqui acontece o all-reduce de gradients
        optimizer.step()
        
        if rank == 0:  # Apenas rank 0 faz logging
            print(f"Loss: {loss.item():.4f}")
    
    cleanup_distributed()

# Lançar 8 processos (um por GPU)
if __name__ == "__main__":
    world_size = torch.cuda.device_count()  # 8 para DGX H100
    mp.spawn(
        train_distributed,
        args=(world_size, model_config),
        nprocs=world_size,
        join=True
    )
```

---

## Como Transformers Usam GPUs

### Decomposição de Operações

Um passo de forward pass de um transformer decoder pode ser decomposto em:

```
1. Embedding lookup:         GATHER op — memory-bound, irregular access
2. QKV projection:           GEMM — compute-bound (batch grande), memory-bound (batch=1)
3. Attention scores (QKᵀ):   GEMM — compute-bound para seq_len longa
4. Softmax:                  Element-wise + reduction — memory-bound
5. Attention × V:            GEMM — compute-bound para seq_len longa
6. Output projection:        GEMM — compute/memory-bound
7. Layer norm:               Reduction + element-wise — memory-bound
8. FFN gate projection:      GEMM
9. SiLU/GELU activation:     Element-wise — memory-bound
10. FFN up projection:       GEMM
11. FFN down projection:     GEMM
12. Residual add:            Element-wise — memory-bound
```

GEMMs dominam em FLOPs, mas operações element-wise (softmax, norm, activation) dominam em número de kernel launches e podem dominar em latência se mal implementadas.

**Kernel fusion**: operações element-wise consecutivas podem ser fundidas em um único kernel para reduzir round-trips à HBM:

```python
# Sem fusion: 3 kernel launches, 3x leitura/escrita na HBM
x = layer_norm(x)
x = x + residual
x = gelu(linear(x))

# Com Triton kernel fusion (exemplo conceitual)
import triton
import triton.language as tl

@triton.jit
def fused_add_layernorm_kernel(
    x_ptr, residual_ptr, weight_ptr, bias_ptr, output_ptr,
    N: tl.constexpr, eps: tl.constexpr, BLOCK_SIZE: tl.constexpr
):
    """
    Kernel Triton que funde: residual_add + layer_norm em um único kernel.
    Reduz round-trips à HBM de 4 (2 reads + 2 writes) para 3 (2 reads + 1 write).
    """
    pid = tl.program_id(0)
    offsets = tl.arange(0, BLOCK_SIZE)
    
    x = tl.load(x_ptr + pid * N + offsets, mask=offsets < N)
    res = tl.load(residual_ptr + pid * N + offsets, mask=offsets < N)
    weight = tl.load(weight_ptr + offsets, mask=offsets < N)
    bias = tl.load(bias_ptr + offsets, mask=offsets < N)
    
    # Residual add
    x = x + res
    
    # Layer norm
    mean = tl.sum(x) / N
    variance = tl.sum((x - mean) ** 2) / N
    x_norm = (x - mean) / tl.sqrt(variance + eps)
    
    # Affine transform
    output = x_norm * weight + bias
    tl.store(output_ptr + pid * N + offsets, output, mask=offsets < N)
```

---

## Profiling e Diagnóstico de Performance

### Medir Bandwidth de VRAM

```python
import torch
import time

def measure_memory_bandwidth(size_gb: float = 1.0, n_trials: int = 100) -> float:
    """
    Mede bandwidth efetiva de HBM copiando um buffer de size_gb GB.
    Retorna bandwidth em GB/s.
    """
    device = torch.device("cuda")
    
    # Alocar buffer de size_gb GB em FP32
    n_elements = int(size_gb * 1024**3 / 4)  # 4 bytes por FP32
    src = torch.randn(n_elements, device=device, dtype=torch.float32)
    dst = torch.empty_like(src)
    
    # Warmup
    for _ in range(10):
        dst.copy_(src)
    torch.cuda.synchronize()
    
    start = time.perf_counter()
    for _ in range(n_trials):
        dst.copy_(src)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    
    # Cada cópia: lê size_gb + escreve size_gb = 2 × size_gb de tráfego
    total_bytes = 2 * size_gb * 1024**3 * n_trials
    bandwidth_gbs = total_bytes / elapsed / 1e9
    
    return bandwidth_gbs

bw = measure_memory_bandwidth(size_gb=2.0)
print(f"Bandwidth medida: {bw:.0f} GB/s")
# H100 SXM: ~3200 GB/s (perto do teórico 3350 GB/s)
# A100 80GB: ~1800 GB/s (vs teórico 2000 GB/s)
# RTX 4090: ~900 GB/s (vs teórico 1008 GB/s)
```

### Profiling com torch.profiler

```python
import torch
from torch.profiler import profile, record_function, ProfilerActivity

def profile_transformer_forward(model, inputs):
    """
    Perfila um forward pass de transformer e identifica kernels lentos.
    """
    with profile(
        activities=[
            ProfilerActivity.CPU,
            ProfilerActivity.CUDA,
        ],
        record_shapes=True,
        profile_memory=True,
        with_stack=True,
    ) as prof:
        with record_function("transformer_forward"):
            with torch.no_grad():
                output = model(**inputs)
    
    # Tabela dos kernels mais custosos por CUDA time
    print(prof.key_averages().table(
        sort_by="cuda_time_total",
        row_limit=20
    ))
    
    # Exportar para Chrome trace (visualização interativa)
    prof.export_chrome_trace("trace.json")
    # Abra em chrome://tracing ou perfetto.dev
    
    return prof

# Identificar se operação é memory ou compute bound
def estimate_arithmetic_intensity_empirical(model, inputs):
    """
    Usa nvml para correlacionar FLOPS e bandwidth durante execução.
    Requer: pip install pynvml
    """
    import pynvml
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    
    # Medir utilização antes
    util_before = pynvml.nvmlDeviceGetUtilizationRates(handle)
    mem_before = pynvml.nvmlDeviceGetMemoryInfo(handle)
    
    output = model(**inputs)
    torch.cuda.synchronize()
    
    util_after = pynvml.nvmlDeviceGetUtilizationRates(handle)
    
    print(f"GPU utilization: {util_after.gpu}%")
    print(f"Memory utilization: {util_after.memory}%")
    # Se gpu_util >> mem_util → compute-bound
    # Se mem_util >> gpu_util → memory-bound (ou mais precisamente: memory-bound)
    # Nota: nvml não distingue perfeitamente, mas é um indicador rápido
```

### Verificar Arithmetic Intensity e TF32

```python
def verify_tensor_cores_active(dtype=torch.float16):
    """
    Verifica se Tensor Cores estão sendo usados comparando throughput
    com e sem precisão reduzida.
    """
    device = torch.device("cuda")
    N = 8192  # Múltiplo de 8 para alinhar com Tensor Core tiles
    
    # FP32 — usa CUDA Cores (sem Tensor Cores em modo FP32 puro)
    A_fp32 = torch.randn(N, N, dtype=torch.float32, device=device)
    B_fp32 = torch.randn(N, N, dtype=torch.float32, device=device)
    
    torch.backends.cuda.matmul.allow_tf32 = False  # Força FP32 puro
    t_fp32_pure = _time_matmul(A_fp32, B_fp32)
    
    torch.backends.cuda.matmul.allow_tf32 = True   # Permite TF32 (Tensor Cores)
    t_fp32_tf32 = _time_matmul(A_fp32, B_fp32)
    
    # FP16 — usa Tensor Cores
    A_fp16 = A_fp32.to(dtype)
    B_fp16 = B_fp32.to(dtype)
    t_fp16 = _time_matmul(A_fp16, B_fp16)
    
    flops = 2 * N**3
    print(f"FP32 puro:  {flops/t_fp32_pure/1e12:.1f} TFLOPS")
    print(f"FP32+TF32:  {flops/t_fp32_tf32/1e12:.1f} TFLOPS (Tensor Cores!)")
    print(f"{dtype}:    {flops/t_fp16/1e12:.1f} TFLOPS (Tensor Cores!)")
    print(f"Speedup TF32: {t_fp32_pure/t_fp32_tf32:.1f}x")
    print(f"Speedup FP16: {t_fp32_pure/t_fp16:.1f}x")

def _time_matmul(A, B, n_trials=50):
    """Retorna tempo total em segundos para n_trials matmuls."""
    for _ in range(5):  # warmup
        _ = torch.matmul(A, B)
    torch.cuda.synchronize()
    
    start = time.perf_counter()
    for _ in range(n_trials):
        _ = torch.matmul(A, B)
    torch.cuda.synchronize()
    
    return time.perf_counter() - start

verify_tensor_cores_active()
# Resultado típico A100:
# FP32 puro:  19.5 TFLOPS
# FP32+TF32:  156 TFLOPS  (8x speedup via Tensor Cores!)
# FP16:       312 TFLOPS  (16x speedup via Tensor Cores!)
```

### Monitoramento em Runtime

```python
def gpu_memory_report(device_idx: int = 0):
    """
    Relatório completo de uso de memória GPU.
    """
    if not torch.cuda.is_available():
        print("CUDA não disponível")
        return
    
    device = torch.device(f"cuda:{device_idx}")
    props = torch.cuda.get_device_properties(device_idx)
    
    total_bytes = props.total_memory
    reserved_bytes = torch.cuda.memory_reserved(device_idx)
    allocated_bytes = torch.cuda.memory_allocated(device_idx)
    free_in_reserved = reserved_bytes - allocated_bytes
    
    print(f"GPU: {props.name}")
    print(f"Total VRAM:        {total_bytes/1e9:.1f} GB")
    print(f"Reservado (PyTorch): {reserved_bytes/1e9:.2f} GB")
    print(f"Alocado (tensores): {allocated_bytes/1e9:.2f} GB")
    print(f"Livre no pool:     {free_in_reserved/1e9:.2f} GB")
    print(f"Disponível (real): {(total_bytes-reserved_bytes)/1e9:.2f} GB")
    print()
    print(torch.cuda.memory_summary(device_idx, abbreviated=True))
```

---

## References

- [NVIDIA H100 Tensor Core GPU Architecture Whitepaper](https://resources.nvidia.com/en-us-tensor-core/gtc22-whitepaper-hopper)
- [Making Deep Learning Go Brrrr From First Principles — Horace He (2022)](https://horace.io/brrr_intro.html)
- [Flash Attention: Fast and Memory-Efficient Exact Attention with IO-Awareness (arxiv:2205.14135)](https://arxiv.org/abs/2205.14135)
- [NVIDIA CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- [NVIDIA Ampere Architecture Whitepaper](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf)
- [Triton: An Intermediate Language and Compiler for Tiled Neural Network Computations](https://www.eecs.harvard.edu/~htk/publication/2019-mapl-tillet-kung-cox.pdf)

---

## Related

- [[specialized-hardware]] — TPUs, Groq LPU, Cerebras e outros chips de IA além de GPUs
- [[vram-estimation]] — como calcular VRAM necessária para modelos e treinamento
- [[inference-engines]] — vLLM, TensorRT-LLM, otimizações de serving
- [[kv-cache-attention]] — Flash Attention e otimizações do KV cache
- [[quantization]] — INT8, INT4, FP8 e como afetam uso de VRAM e Tensor Cores
