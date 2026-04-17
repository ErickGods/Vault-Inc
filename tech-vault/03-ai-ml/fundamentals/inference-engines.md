---
tags: [ai-ml, fundamentals, inference, vllm, tensorrt, serving]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Inference Engines, vLLM, TensorRT-LLM, Ollama, LLM Serving]
---

# Inference Engines para LLMs

## Overview

Frameworks de ML genéricos como HuggingFace Transformers são excelentes para experimentação e fine-tuning, mas foram projetados para flexibilidade — não para servir LLMs em produção de forma eficiente. Inference engines especializados existem porque LLMs têm padrões muito específicos que podem ser explorados para ganhos massivos de throughput e latência:

1. **Geração autoregressiva:** tokens são gerados um por vez — cada step processa apenas 1 token novo (decode phase), enquanto o prefill processa o prompt inteiro uma vez
2. **Comprimento de sequência variável:** requests chegam com prompts de tamanhos arbitrários e geram quantidades diferentes de tokens
3. **Memory-bound decode:** a fase de decodificação é limitada pela bandwidth de memória para leitura do KV cache, não pela capacidade de compute
4. **KV cache como recurso compartilhado:** múltiplos requests competem pela mesma VRAM para seus KV caches

Integra com [[quantization]], [[gpu-architecture]], [[vram-estimation]], [[kv-cache-attention]] e [[specialized-hardware]].

> [!tip] Chunk Prefill Para Latência Consistente
> Em vLLM, `--enable-chunked-prefill` divide prefills longos (>512 tokens) em chunks, evitando que um request longo bloqueie todos os decodes ativos. Essencial para latência P99 consistente com workloads mistos.

---

## Métricas de Serving

Antes de comparar engines, é essencial entender as métricas que importam:

### TTFT — Time to First Token

Latência desde o envio do request até o recebimento do primeiro token gerado. Corresponde ao tempo da fase de **prefill** (processar o prompt inteiro).

- Dominada por: comprimento do prompt, nível de paralelismo, chunked prefill
- Workloads interativos (chat): TTFT crítico, deve ficar < 500ms
- Workloads batch: TTFT menos importante que throughput total

### TBT / TPOT — Time Between Tokens

Latência entre tokens consecutivos durante a geração (após o primeiro). Também chamado de TPOT (Time Per Output Token).

- Dominada por: KV cache bandwidth (memory-bound), batch size
- Para experência fluida em chat: TBT < 30ms (equivalente a ~33 tokens/segundo para o usuário)
- TBT é determinado por: `model_size_bytes / gpu_memory_bandwidth_bytes_per_sec / n_parallel_requests`

### Throughput

Tokens por segundo total do servidor, considerando todos os requests simultâneos.

```
throughput = (total_tokens_gerados) / (tempo_total)
```

Throughput e latência têm trade-off: aumentar batch size sobe throughput mas aumenta TBT e TTFT.

### Percentis de Latência

```
P50 (mediana): metade dos requests terminam abaixo desse valor
P90:           90% dos requests terminam abaixo desse valor
P99:           99% dos requests terminam abaixo desse valor — o mais crítico para SLAs
```

P99 é o mais importante para SLAs de produção. Um sistema com P50=100ms e P99=5000ms tem qualidade muito diferente de um com P50=150ms e P99=300ms.

---

## Continuous Batching (Orca)

### Batching Estático: O Problema

No serving original de GPT-3 e primeiros modelos, o servidor aguardava um batch completo antes de processar. Isso criava dois problemas:

1. **Head-of-line blocking:** um request longo (ex: 2000 tokens de output) bloqueava todos os outros no mesmo batch
2. **Subutilização:** se um request terminasse cedo, a GPU ficava parcialmente ociosa até o fim do batch

### Continuous Batching: Iteration-Level Scheduling

Introduzido pelo paper Orca (Yu et al., 2022), continuous batching trata cada **iteration** (um passo de decode) como uma unidade de escalonamento:

- A cada iteration, o scheduler verifica se há novos requests esperando
- Requests que terminaram liberam seus slots imediatamente
- Novos requests entram no próximo batch assim que há slot disponível
- Requests com prefills longos são processados em paralelo com decodes de outros requests

**Impacto:** speedup de 2-23x em throughput comparado a static batching, dependendo da distribuição de comprimento dos requests.

```
Batching estático:
  t=0: [R1-decode, R2-decode, R3-decode, R4-decode] → batch de 4
  t=1: [R1-decode, R2-decode, R3-decode, R4-decode] → mesmo batch (R4 terminou mas aguarda)
  ...
  t=N: R4 já terminou, mas aguardou até R1 completar

Continuous batching:
  t=0: [R1-decode, R2-decode, R3-decode, R4-decode]
  t=1: [R1-decode, R2-decode, R3-decode, R5-novo]   ← R4 saiu, R5 entrou imediatamente
  t=2: [R1-decode, R2-decode, R5-decode, R6-novo]
```

---

## Tensor Parallelism vs Pipeline Parallelism

### Tensor Parallelism (TP)

Divide as matrizes de peso entre múltiplas GPUs. Cada GPU processa uma fração do tensor.

Para uma camada linear Y = XW^T com TP-degree p:
- GPU_i possui colunas W_{:, i*d/p : (i+1)*d/p}
- Cada GPU computa uma fração da saída
- Um `all-reduce` combina os resultados ao fim de cada camada

**Características:**
- Comunicação: frequente (a cada camada), mas menor volume
- Latência: baixa — todas as GPUs trabalham sincronizadas
- Requer: alta bandwidth entre GPUs (NVLink essencial)
- Melhor para: latência mínima, modelos menores

> [!warning] Tensor Parallelism Requer NVLink em Produção
> Para tensor parallelism entre GPUs, a comunicação all-reduce a cada camada requer alta bandwidth. PCIe 4.0 x16 (~32 GB/s bidirecional) é insuficiente — use NVLink (600+ GB/s) para latência aceitável.

### Pipeline Parallelism (PP)

Divide as camadas entre GPUs. GPU_0 processa camadas 0-N/p, GPU_1 processa camadas N/p-2N/p, etc.

**Características:**
- Comunicação: apenas nas fronteiras entre estágios (ativações do último token da GPU_i para GPU_{i+1})
- Eficiência: pipeline bubbles (GPUs ociosas enquanto aguardam o estágio anterior)
- Melhor para: throughput em batches grandes, modelos muito grandes (>8 GPUs)

### Quando Usar Cada Estratégia

| Cenário | Recomendação |
|---------|-------------|
| Modelo cabe em 1 GPU | Sem paralelismo |
| 2-4 GPUs, mesma máquina, NVLink | Tensor Parallelism |
| 4-8 GPUs, mesma máquina, NVLink | TP=4 ou TP=8 |
| >8 GPUs ou múltiplas máquinas | Híbrido: TP dentro da máquina + PP entre máquinas |

---

## vLLM

vLLM é o inference engine open-source mais usado em produção para LLMs. Combina Paged Attention, continuous batching e suporte a múltiplos formatos de quantização em uma API OpenAI-compatible.

### Características Principais

- **Paged Attention:** KV cache paginado elimina fragmentação de memória (ver [[kv-cache-attention]])
- **Continuous batching:** iteration-level scheduling nativo
- **Quantização:** GPTQ, AWQ, FP8, GGUF, bitsandbytes
- **Prefix caching:** system prompts idênticos entre requests compartilham KV cache (zero custo após o primeiro)
- **Chunked prefill:** divide prefills longos para não bloquear decodes
- **API compatível com OpenAI:** substituição drop-in para aplicações existentes

> [!warning] vLLM API Versions
> vLLM mudou APIs significativamente entre versões. A API de v0.4.x, v0.5.x, e v0.6.x+ são diferentes. Fixe a versão no requirements.txt e verifique o changelog antes de upgrades.

### Servidor vLLM Completo com Python Client

```python
# SERVIDOR — iniciar em linha de comando:
# pip install vllm
# vllm serve meta-llama/Llama-3-8B-Instruct \
#     --host 0.0.0.0 \
#     --port 8000 \
#     --quantization awq \
#     --gpu-memory-utilization 0.9 \
#     --max-model-len 8192 \
#     --enable-chunked-prefill \
#     --enable-prefix-caching \
#     --tensor-parallel-size 1

# CLIENT — usar OpenAI SDK com endpoint vLLM
from openai import OpenAI
import asyncio
from openai import AsyncOpenAI


def criar_cliente_vllm(host: str = "localhost", port: int = 8000) -> OpenAI:
    """Cria cliente OpenAI apontando para servidor vLLM local."""
    return OpenAI(
        base_url=f"http://{host}:{port}/v1",
        api_key="vllm",  # vLLM não valida a API key por padrão
    )


def gerar_resposta(
    client: OpenAI,
    prompt: str,
    model: str = "meta-llama/Llama-3-8B-Instruct",
    max_tokens: int = 512,
    temperature: float = 0.7,
    system_prompt: str = "Você é um assistente técnico especializado.",
) -> str:
    """Geração síncrona via API OpenAI-compatible do vLLM."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def gerar_streaming(
    client: OpenAI,
    prompt: str,
    model: str = "meta-llama/Llama-3-8B-Instruct",
    max_tokens: int = 512,
) -> str:
    """Geração com streaming — imprime tokens conforme chegam."""
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        stream=True,
    )

    full_response = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_response += delta

    print()  # newline final
    return full_response


async def gerar_em_paralelo(
    prompts: list[str],
    model: str = "meta-llama/Llama-3-8B-Instruct",
    host: str = "localhost",
    port: int = 8000,
    max_tokens: int = 256,
    concurrency: int = 10,
) -> list[str]:
    """
    Envia múltiplos requests concorrentemente para maximizar throughput.
    O vLLM processa em continuous batches automaticamente.
    """
    client = AsyncOpenAI(
        base_url=f"http://{host}:{port}/v1",
        api_key="vllm",
    )

    semaphore = asyncio.Semaphore(concurrency)

    async def gerar_um(prompt: str) -> str:
        async with semaphore:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content

    tasks = [gerar_um(prompt) for prompt in prompts]
    respostas = await asyncio.gather(*tasks)
    return list(respostas)
```

### Benchmark de Throughput

```python
import asyncio
import time
from openai import AsyncOpenAI


async def benchmark_throughput(
    host: str = "localhost",
    port: int = 8000,
    model: str = "meta-llama/Llama-3-8B-Instruct",
    n_requests: int = 100,
    max_tokens: int = 200,
    concurrency_levels: list[int] = [1, 4, 8, 16, 32],
):
    """
    Benchmark de throughput do servidor vLLM em diferentes níveis de concorrência.
    Mede tokens/segundo e latências P50/P90/P99.
    """
    import statistics

    prompt = (
        "Explique em detalhes técnicos como funciona o mecanismo de atenção "
        "em transformers, incluindo as matrizes Q, K, V e o cálculo do softmax."
    )

    client = AsyncOpenAI(
        base_url=f"http://{host}:{port}/v1",
        api_key="vllm",
        timeout=120.0,
    )

    print(f"\n{'Concorrência':<14} {'Throughput':>12} {'P50 (ms)':>10} {'P90 (ms)':>10} {'P99 (ms)':>10}")
    print("-" * 60)

    for concurrency in concurrency_levels:
        semaphore = asyncio.Semaphore(concurrency)
        latencies = []

        async def request_com_medicao() -> int:
            async with semaphore:
                t0 = time.perf_counter()
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.0,
                )
                elapsed = time.perf_counter() - t0
                latencies.append(elapsed * 1000)  # ms
                return response.usage.completion_tokens

        t_start = time.perf_counter()
        tokens_list = await asyncio.gather(*[request_com_medicao() for _ in range(n_requests)])
        t_total = time.perf_counter() - t_start

        total_tokens = sum(tokens_list)
        throughput = total_tokens / t_total

        latencies_sorted = sorted(latencies)
        p50 = statistics.median(latencies_sorted)
        p90 = latencies_sorted[int(0.90 * len(latencies_sorted))]
        p99 = latencies_sorted[int(0.99 * len(latencies_sorted))]

        print(
            f"{concurrency:<14} {throughput:>11.1f}t/s "
            f"{p50:>9.0f}ms {p90:>9.0f}ms {p99:>9.0f}ms"
        )


if __name__ == "__main__":
    asyncio.run(benchmark_throughput())
```

> [!warning] GPU Memory Utilization
> O parâmetro `--gpu-memory-utilization 0.9` no vLLM reserva 90% da VRAM para o KV cache pool. Se o modelo não cabe, o servidor falha ao iniciar. Para modelos grandes, ajuste para 0.85 e monitore OOM errors.

### Containerização com Docker

```python
# Gerar docker-compose.yml programaticamente
def gerar_docker_compose_vllm(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
    port: int = 8000,
    gpu_memory_utilization: float = 0.9,
    quantization: str = "awq",
    tensor_parallel_size: int = 1,
    hf_token: str = "${HF_TOKEN}",  # variável de ambiente
) -> str:
    """
    Gera docker-compose.yml para servir vLLM em produção.
    """
    compose = f"""version: "3.8"

services:
  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "{port}:{port}"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    environment:
      - HUGGING_FACE_HUB_TOKEN={hf_token}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: {tensor_parallel_size}
              capabilities: [gpu]
    command: >
      --model {model_name}
      --host 0.0.0.0
      --port {port}
      --quantization {quantization}
      --gpu-memory-utilization {gpu_memory_utilization}
      --tensor-parallel-size {tensor_parallel_size}
      --enable-chunked-prefill
      --enable-prefix-caching
      --max-model-len 8192
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s

  # Opcional: Prometheus + Grafana para observabilidade
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
"""
    return compose


def gerar_prometheus_config(vllm_host: str = "vllm", vllm_port: int = 8000) -> str:
    """Configuração Prometheus para métricas do vLLM."""
    return f"""global:
  scrape_interval: 15s

scrape_configs:
  - job_name: vllm
    static_configs:
      - targets: ["{vllm_host}:{vllm_port}"]
    metrics_path: /metrics
"""
```

---

## llama.cpp

llama.cpp é uma implementação em C/C++ de inferência de LLMs, projetado para máxima compatibilidade: roda em CPU, Apple Silicon (Metal), NVIDIA (CUDA) e AMD (ROCm).

### Quando Usar llama.cpp / Ollama

- Desenvolvimento local sem GPU dedicada
- Hardware consumer com GPU pequena (GPU offloading parcial)
- Apple Silicon (M1/M2/M3) — Metal backend altamente otimizado
- Edge inference e dispositivos embarcados
- Prototipagem rápida sem configuração de ambiente CUDA

### GPU Offloading Parcial

Uma característica única do llama.cpp: quando o modelo não cabe inteiramente na GPU, é possível enviar N camadas para a GPU e processar as restantes na CPU:

```bash
# 0 camadas na GPU — só CPU
llama-cli -m llama-3-8b-q4_k_m.gguf --n-gpu-layers 0

# 20 camadas na GPU, resto na CPU — equilíbrio
llama-cli -m llama-3-8b-q4_k_m.gguf --n-gpu-layers 20

# Todas as camadas na GPU — máximo desempenho
llama-cli -m llama-3-8b-q4_k_m.gguf --n-gpu-layers -1
```

---

## TensorRT-LLM (NVIDIA)

TensorRT-LLM é a solução NVIDIA para inferência de máxima performance em GPUs H100/A100. Compila modelos em "engines" altamente otimizados para o hardware alvo.

### Kernel Fusion

A principal otimização do TensorRT-LLM é a fusão de kernels CUDA: combinar múltiplas operações (layernorm + attention + softmax + FFN) em um único kernel elimina round-trips desnecessários entre SRAM e HBM.

Por exemplo, uma sequência típica de attention:
```
Padrão:     Q = norm(x) → [HBM] → linear(Q) → [HBM] → scores = QK^T → [HBM] → softmax → [HBM] → ...
Fusionado:  norm(x) + linear(Q) + QK^T + softmax → um único kernel, resultados em SRAM
```

### Fluxo de Trabalho

1. Exportar modelo do HuggingFace para formato TensorRT-LLM
2. Compilar engine (pode demorar 30min+ para modelos grandes)
3. Servir com Triton Inference Server ou API própria

```python
# Exemplo simplificado de configuração TensorRT-LLM
# pip install tensorrt-llm (requer CUDA 12+, cuDNN)

def configurar_tensorrt_llm(
    model_name: str = "meta-llama/Llama-3-8B-Instruct",
    output_dir: str = "./trt-engine",
    dtype: str = "float16",  # float16, bfloat16, ou float8
    tp_size: int = 1,        # tensor parallelism
    max_batch_size: int = 16,
    max_input_len: int = 4096,
    max_output_len: int = 1024,
) -> dict:
    """
    Retorna a configuração para compilar engine TensorRT-LLM.
    A compilação real é feita via CLI:
      trtllm-build --checkpoint_dir <ckpt> --output_dir <engine> ...
    """
    config = {
        "checkpoint_dir": f"{model_name.replace('/', '_')}_ckpt",
        "output_dir": output_dir,
        "dtype": dtype,
        "tp_size": tp_size,
        "max_batch_size": max_batch_size,
        "max_input_len": max_input_len,
        "max_seq_len": max_input_len + max_output_len,
        "use_fused_mlp": True,
        "use_paged_context_fmha": True,
        "tokens_per_block": 64,
        "kv_cache_free_gpu_memory_fraction": 0.85,
    }

    # Comando CLI equivalente
    cli_command = (
        f"trtllm-build "
        f"--checkpoint_dir {config['checkpoint_dir']} "
        f"--output_dir {config['output_dir']} "
        f"--dtype {dtype} "
        f"--max_batch_size {max_batch_size} "
        f"--max_seq_len {config['max_seq_len']} "
        f"--use_fused_mlp enable "
        f"--use_paged_context_fmha enable "
        f"--workers {tp_size}"
    )

    return {"config": config, "cli_command": cli_command}
```

---

## Ollama

Ollama é um wrapper sobre llama.cpp com UX orientada a desenvolvedores. Abstrai completamente a configuração e oferece uma experiência similar a `docker pull`.

```bash
# Instalar e usar
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b          # baixa e descompacta modelo GGUF
ollama run llama3.1:8b           # chat interativo no terminal
ollama serve                     # API REST em localhost:11434
```

### API REST do Ollama

```python
import httpx
import json


def chat_ollama(
    prompt: str,
    model: str = "llama3.1:8b",
    host: str = "localhost",
    port: int = 11434,
    stream: bool = False,
) -> str:
    """Geração via API REST do Ollama."""
    url = f"http://{host}:{port}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream,
    }

    if stream:
        full_response = ""
        with httpx.stream("POST", url, json=payload, timeout=120) as response:
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    print(content, end="", flush=True)
                    full_response += content
        print()
        return full_response
    else:
        response = httpx.post(url, json=payload, timeout=120)
        return response.json()["message"]["content"]


def listar_modelos_ollama(host: str = "localhost", port: int = 11434) -> list[dict]:
    """Lista modelos instalados no Ollama."""
    response = httpx.get(f"http://{host}:{port}/api/tags")
    return response.json().get("models", [])
```

### Modelfile para Customização

```python
def gerar_modelfile(
    base_model: str = "llama3.1:8b",
    system_prompt: str = "Você é um assistente técnico da Vault Inc.",
    temperature: float = 0.7,
    context_window: int = 8192,
) -> str:
    """
    Gera um Ollama Modelfile para customizar system prompt e parâmetros.

    Uso:
        ollama create vault-assistant -f Modelfile
        ollama run vault-assistant
    """
    return f"""FROM {base_model}

SYSTEM \"\"\"{system_prompt}\"\"\"

PARAMETER temperature {temperature}
PARAMETER num_ctx {context_window}
PARAMETER stop "<|eot_id|>"
"""
```

---

## Speculative Decoding

### Conceito

Speculative decoding (Chen et al., 2023) aproveita o fato de que um modelo draft pequeno pode antecipar tokens prováveis, que o modelo principal verifica em paralelo.

**Fluxo:**
1. Modelo draft (ex: Llama 3.2 1B) gera K tokens de forma autoregressiva — muito rápido
2. Modelo principal (ex: Llama 3.1 70B) verifica os K tokens em um único forward pass paralelo
3. Se o token i foi aceito pelo modelo principal: manter; se rejeitado: descartar tokens i+1..K e usar a distribuição correta do modelo principal para o token i

**Speedup esperado:** 2-3x para tarefas onde o draft model acerta frequentemente (código repetitivo, texto estruturado, completar padrões previsíveis).

**Draft model sizing:** tipicamente 10-20x menor que o modelo principal. A qualidade do draft afeta diretamente a taxa de aceitação — e portanto o speedup.

```python
import torch
import torch.nn.functional as F
from typing import Optional


def speculative_decode_step(
    draft_model,
    target_model,
    tokenizer,
    input_ids: torch.Tensor,
    k: int = 4,
    temperature: float = 1.0,
    max_new_tokens: int = 50,
) -> torch.Tensor:
    """
    Implementação didática de speculative decoding.
    Em produção, use a implementação nativa do vLLM ou TensorRT-LLM.

    Args:
        k: número de tokens que o draft model gera por ciclo
        temperature: temperatura para sampling
    """
    generated = input_ids.clone()

    for _ in range(max_new_tokens // k + 1):
        # Passo 1: Draft model gera K tokens
        draft_tokens = []
        draft_probs = []
        draft_input = generated.clone()

        for _ in range(k):
            with torch.no_grad():
                draft_out = draft_model(draft_input)
                logits = draft_out.logits[:, -1, :] / max(temperature, 1e-5)
                probs = F.softmax(logits, dim=-1)
                token = torch.multinomial(probs, num_samples=1)
                draft_tokens.append(token)
                draft_probs.append(probs)
                draft_input = torch.cat([draft_input, token], dim=1)

        # Passo 2: Target model verifica todos os K tokens em um forward pass
        candidate_ids = torch.cat([generated] + draft_tokens, dim=1)
        with torch.no_grad():
            target_out = target_model(candidate_ids)
            # logits nas posições dos K tokens draft
            target_logits = target_out.logits[:, len(generated[0]) - 1 : -1, :]
            target_logits = target_logits / max(temperature, 1e-5)
            target_probs = F.softmax(target_logits, dim=-1)

        # Passo 3: Aceitar/rejeitar com rejection sampling
        accepted_count = 0
        for i in range(k):
            draft_token = draft_tokens[i]
            p_draft = draft_probs[i].gather(1, draft_token)
            p_target = target_probs[:, i, :].gather(1, draft_token)

            # Probabilidade de aceitar = min(1, p_target / p_draft)
            accept_prob = torch.clamp(p_target / (p_draft + 1e-8), max=1.0)
            r = torch.rand_like(accept_prob)

            if r.item() <= accept_prob.item():
                generated = torch.cat([generated, draft_token], dim=1)
                accepted_count += 1
            else:
                # Rejeitar: amostrar token corrigido do target
                corrected_probs = torch.clamp(
                    target_probs[:, i, :] - draft_probs[i], min=0
                )
                corrected_probs = corrected_probs / (corrected_probs.sum() + 1e-8)
                corrected_token = torch.multinomial(corrected_probs, num_samples=1)
                generated = torch.cat([generated, corrected_token], dim=1)
                break  # Ciclo seguinte começa do token corrigido

        # Sempre adiciona um token do target após os aceitos
        if accepted_count == k:
            last_target_probs = F.softmax(
                target_out.logits[:, -1, :] / max(temperature, 1e-5), dim=-1
            )
            bonus_token = torch.multinomial(last_target_probs, num_samples=1)
            generated = torch.cat([generated, bonus_token], dim=1)

        if generated.shape[1] >= input_ids.shape[1] + max_new_tokens:
            break

    return generated
```

---

## Tabela Comparativa de Engines

| Engine | Backend | Throughput | Latência | Facilidade | Produção |
|--------|---------|-----------|---------|-----------|---------|
| vLLM | CUDA | ★★★★★ | ★★★★ | ★★★★ | ★★★★★ |
| TensorRT-LLM | CUDA | ★★★★★ | ★★★★★ | ★★ | ★★★★ |
| llama.cpp | CPU/CUDA/Metal | ★★★ | ★★★ | ★★★★★ | ★★★ |
| Ollama | llama.cpp | ★★ | ★★★ | ★★★★★ | ★★ |
| HF Transformers | CUDA | ★★ | ★★ | ★★★★★ | ★ |

**Guia de escolha:**
- **Produção GPU NVIDIA:** vLLM (fácil) ou TensorRT-LLM (máxima performance)
- **Produção Apple Silicon:** llama.cpp com Metal backend
- **Desenvolvimento local:** Ollama
- **Pesquisa e experimentação:** HuggingFace Transformers
- **Hardware misto CPU+GPU:** llama.cpp com `--n-gpu-layers`

---

## Referências

- vLLM / Paged Attention — [arxiv:2309.06180](https://arxiv.org/abs/2309.06180)
- Orca / Continuous Batching — [arxiv:2207.04836](https://arxiv.org/abs/2207.04836)
- Speculative Decoding — [arxiv:2211.17192](https://arxiv.org/abs/2211.17192)
- TensorRT-LLM — [NVIDIA Docs](https://nvidia.github.io/TensorRT-LLM/)
- llama.cpp — [GitHub: ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

---

## Related

- [[quantization]] — GPTQ, AWQ e GGUF usados pelos inference engines
- [[gpu-architecture]] — NVLink, HBM bandwidth e Tensor Cores que determinam performance
- [[vram-estimation]] — calcular VRAM necessária para modelo + KV cache em produção
- [[kv-cache-attention]] — paged attention e Flash Attention implementados nos engines
- [[specialized-hardware]] — H100, A100, Apple M-series e seus trade-offs para inferência
