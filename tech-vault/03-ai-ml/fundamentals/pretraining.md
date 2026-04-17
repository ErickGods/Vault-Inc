---
tags: [ai-ml, fundamentals, pretraining, scaling-laws, training]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Pretraining, LLM Pretraining, Scaling Laws, Chinchilla]
---

# Pré-Treinamento de LLMs e Scaling Laws

## Overview

Pré-treinamento é a primeira e mais custosa etapa do pipeline de desenvolvimento de Large Language Models. O modelo é treinado do zero em um corpus massivo de texto, aprendendo representações estatísticas da linguagem, fatos sobre o mundo e padrões de raciocínio — tudo de forma auto-supervisionada, sem rótulos humanos.

É fundamental entender a distinção entre as três grandes fases de treinamento:

| Fase | Objetivo | Dados | Custo relativo |
|------|----------|-------|----------------|
| **Pre-training** | Aprender distribuição geral da linguagem | Trilhões de tokens web, livros, código | $$$$$ (GPU-years) |
| **SFT (Supervised Fine-Tuning)** | Aprender a seguir instruções em formato chat | Milhares a milhões de demonstrations | $$ (GPU-hours) |
| **RLHF / DPO** | Alinhar comportamento com preferências humanas | Pares de preferência humana | $$$ (GPU-days) |

O pré-treinamento consome entre 80-95% do compute total do pipeline. O custo de treinar GPT-4 foi estimado em mais de $100 milhões em compute. Isso se deve a três fatores combinados:

1. **Scale de compute**: treinar um modelo de 70B parâmetros por 2T tokens requer ~10^23 FLOPs — equivalente a milhares de GPUs por meses
2. **Scale de dados**: coletar, limpar e deduplicar trilhões de tokens requer infraestrutura de petabytes
3. **Energia**: clusters de treinamento consomem megawatts — Llama 3 400B foi estimado em 39 milhões de kWh de energia

Após o pré-treinamento, o modelo sabe "prever o próximo token" mas não sabe "seguir instruções". SFT e RLHF são necessários para transformar um base model em um assistant model.

Relaciona-se com: [[transformer-architecture]], [[tokenization]], [[gpu-architecture]], [[fine-tuning-peft]], [[benchmarks-evals]], [[vram-estimation]]

---

## Training Objective

### Cross-Entropy Loss para Next-Token Prediction

O objetivo de treinamento do pré-treinamento é deceptivamente simples: dado o contexto anterior, prever o próximo token. A loss é a cross-entropy negativa média sobre todos os tokens da sequência:

```
L = -(1/T) * Σ_{t=1}^{T} log P(x_t | x_1, ..., x_{t-1}; θ)
```

Onde:
- `T` = número de tokens na sequência
- `x_t` = token na posição t
- `x_1, ..., x_{t-1}` = contexto anterior (todos os tokens precedentes)
- `θ` = parâmetros do modelo

O modelo é treinado para maximizar a log-probabilidade de cada token dado seu contexto. Na prática, minimizamos a loss negativa via gradient descent.

### Por Que Funciona: A Conexão com Compreensão

A razão pela qual prever o próximo token é suficiente para emergir compreensão é profunda e ainda debatida academicamente. A intuição central é:

**Prever bem o próximo token requer entender tudo que o influencia:**

- Para prever `"A capital da França é ___"`, o modelo precisa saber que a resposta é "Paris" — portanto aprende fatos geográficos
- Para prever código Python sintaticamente correto, o modelo precisa entender a gramática da linguagem
- Para prever a conclusão lógica de um argumento, o modelo precisa entender lógica
- Para prever diálogos coerentes, o modelo precisa modelar intenção e contexto social

Este fenômeno é conhecido como **emergência** — capacidades complexas surgindo de um objetivo simples de auto-supervisão.

### Relação com Information Theory

A cross-entropy tem uma interpretação direta em teoria da informação:

**Perplexidade = exp(L)**

A perplexidade mede "quantas escolhas igualmente prováveis o modelo efetivamente considera a cada step". Um modelo perfeito teria perplexidade 1 (sempre prevê o token correto com certeza). Um modelo aleatório com vocabulário de 50,000 tokens teria perplexidade 50,000.

Valores típicos:
- Texto em inglês com GPT-4: ~5-10
- Texto em inglês com modelos menores (7B): ~8-15
- Código Python com modelos especializados: ~3-8
- Texto aleatório: ~vocabulário size

> [!info] Perplexidade Como Métrica
> Perplexidade = exp(cross-entropy loss). Um modelo perfeito teria perplexidade 1. Texto natural em inglês tem perplexidade ~20-50 para modelos grandes. Use para monitorar treinamento e comparar modelos na mesma distribuição. Importante: perplexidade só é comparável entre modelos que usam o mesmo tokenizador — diferentes vocabulários produzem valores incomparáveis.

A relação matemática entre loss e perplexidade é direta:

```python
import math

def loss_to_perplexity(loss: float) -> float:
    """Converte cross-entropy loss para perplexidade."""
    return math.exp(loss)

def perplexity_to_loss(perplexity: float) -> float:
    """Converte perplexidade para cross-entropy loss."""
    return math.log(perplexity)

# Exemplos
print(loss_to_perplexity(2.3))   # ~10 — bom modelo em inglês
print(loss_to_perplexity(3.9))   # ~50 — modelo menor ou domínio diferente
print(loss_to_perplexity(0.0))   # 1.0 — modelo perfeito (impossível na prática)
```

---

## Data Pipelines

### Fontes de Dados

O pré-treinamento de LLMs modernos usa uma mistura cuidadosamente curada de fontes:

| Fonte | Exemplos | Proporção típica | Tipo de conhecimento |
|-------|----------|-----------------|---------------------|
| **Web crawl** | Common Crawl, C4 | 40-70% | Geral, amplo |
| **Livros** | Books3, Gutenberg, OpenLibrary | 10-20% | Narrativa longa, raciocínio |
| **Código** | GitHub, StackOverflow | 10-20% | Programação, lógica estruturada |
| **Artigos científicos** | arXiv, PubMed, S2ORC | 5-10% | Raciocínio técnico |
| **Enciclopédias** | Wikipedia, Wikidata | 3-8% | Fatos verificados |
| **Conversas** | Reddit, fóruns | 5-15% | Diálogo, QA |

A proporção é uma decisão de design. Common Crawl bruto contém petabytes de texto mas tem qualidade muito variada — requer pipeline extenso de filtragem.

### MinHash LSH para Deduplication

Duplicatas no dataset de treinamento causam dois problemas sérios:
1. **Memorização**: o modelo memoriza texto repetido em vez de aprender padrões generalizáveis
2. **Inflação de benchmarks**: se exemplos dos benchmarks aparecem muitas vezes no treino, os scores são inflados artificialmente

MinHash LSH (Locality-Sensitive Hashing) é o algoritmo padrão para deduplicação em escala de web:

**Como funciona:**

1. **Shingling**: converter cada documento em um conjunto de n-gramas de caracteres (shingles)
   - Exemplo: "hello world" com n=3 → {"hel", "ell", "llo", "lo ", "o w", " wo", "wor", "orl", "rld"}
   
2. **MinHashing**: gerar uma assinatura compacta (signature) para cada documento
   - Aplicar k funções hash diferentes ao conjunto de shingles
   - Para cada função hash, registrar o valor mínimo (minhash)
   - O vetor de k minhashes é a assinatura do documento (~200 valores inteiros)
   - **Propriedade fundamental**: P(minhash_i(A) == minhash_i(B)) = Jaccard(A, B)

3. **Bandas**: dividir a assinatura em b bandas de r linhas cada (b × r = k)
   - Dois documentos são "candidatos" se pelo menos uma banda é idêntica
   - Threshold de similaridade: t ≈ (1/b)^(1/r)
   
4. **Exact deduplication**: para cada par candidato, calcular Jaccard exato
   - Se Jaccard > threshold (tipicamente 0.8), manter apenas um documento

```python
from datasketch import MinHash, MinHashLSH

def build_minhash(text: str, num_perm: int = 128) -> MinHash:
    """Cria assinatura MinHash para um documento."""
    m = MinHash(num_perm=num_perm)
    # Shingling com n=5 caracteres
    shingles = {text[i:i+5].encode('utf-8') for i in range(len(text) - 4)}
    for shingle in shingles:
        m.update(shingle)
    return m

def deduplicate_corpus(documents: list[str], threshold: float = 0.8) -> list[str]:
    """Remove documentos duplicados usando MinHash LSH."""
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    unique_docs = []
    
    for i, doc in enumerate(documents):
        mh = build_minhash(doc)
        key = f"doc_{i}"
        
        # Verifica se já existe documento similar
        result = lsh.query(mh)
        if not result:
            lsh.insert(key, mh)
            unique_docs.append(doc)
        # Se similar encontrado, descarta este documento
    
    return unique_docs
```

### Quality Filtering Heurísticas

Após deduplicação, aplica-se uma série de filtros heurísticos para remover conteúdo de baixa qualidade:

**Filtros baseados em comprimento:**
- Remover documentos com menos de 200 palavras (fragmentos incoerentes)
- Remover documentos com mais de 100,000 palavras sem estrutura (spam ou conteúdo gerado)
- Remover linhas com menos de 3 palavras (listas de links, menus de navegação)

**Filtros baseados em proporções:**
- **Proporção alfanumérica**: remover documentos onde <50% dos caracteres são alfanuméricos (menus, templates, código binário)
- **Razão de caracteres especiais**: remover documentos com >30% de símbolos especiais
- **Stop word coverage**: documentos sem palavras comuns da língua provavelmente são spam ou código

**Filtragem por perplexidade com KenLM:**
- Treinar um modelo de linguagem n-gram leve (KenLM) em texto de alta qualidade (Wikipedia)
- Calcular perplexidade de cada documento neste modelo de referência
- Remover documentos com perplexidade muito alta (texto sem sentido, spam) ou muito baixa (texto repetitivo)
- O threshold típico remove os 20% mais extremos em ambas as direções

```python
import kenlm
import math

def compute_kenlm_perplexity(model: kenlm.Model, text: str) -> float:
    """Calcula perplexidade de um texto usando modelo KenLM."""
    log_prob = model.score(text)  # log10 probability
    num_words = len(text.split())
    if num_words == 0:
        return float('inf')
    # Converter de log10 para perplexidade
    perplexity = 10 ** (-log_prob / num_words)
    return perplexity

def quality_filter(
    text: str,
    kenlm_model: kenlm.Model,
    min_words: int = 200,
    min_alphanum_ratio: float = 0.5,
    max_perplexity: float = 1500,
    min_perplexity: float = 50,
) -> bool:
    """
    Retorna True se o documento passa nos filtros de qualidade.
    Retorna False se deve ser descartado.
    """
    words = text.split()
    
    # Filtro de comprimento
    if len(words) < min_words:
        return False
    
    # Filtro de proporção alfanumérica
    alphanum_chars = sum(1 for c in text if c.isalnum())
    if len(text) > 0 and alphanum_chars / len(text) < min_alphanum_ratio:
        return False
    
    # Filtro de perplexidade
    ppl = compute_kenlm_perplexity(kenlm_model, text)
    if ppl > max_perplexity or ppl < min_perplexity:
        return False
    
    return True
```

### Decontamination

Decontamination é o processo de remover do conjunto de treino qualquer texto que apareça nos benchmarks de avaliação. Sem isso, os scores nos benchmarks são inflados e enganosos.

**Processo padrão:**
1. Extrair todos os prompts e respostas dos benchmarks (MMLU, HumanEval, GSM8K, etc.)
2. Gerar n-gramas de 13 palavras de cada item do benchmark
3. Remover documentos de treino que contenham qualquer n-grama dos benchmarks
4. Documentar quais documentos foram removidos e por qual benchmark

> [!warning] Data Contamination
> Se os dados de avaliação (benchmarks) aparecerem no conjunto de treino, os resultados são inflados e inválidos. Use decontamination antes de publicar benchmarks. Estudos mostraram que GPT-3.5 e GPT-4 podem ter contaminação em benchmarks como GSM8K e HumanEval, tornando comparações diretas suspeitas. Todo paper que reporta resultados deve incluir análise de contaminação.

---

## Scaling Laws (Chinchilla — Hoffmann et al., 2022)

### A Equação de Loss

A contribuição central do paper Chinchilla (arxiv:2203.15556) foi derivar empiricamente como a loss de um modelo escala com o número de parâmetros e tokens de treinamento:

```
L(N, D) = E + A/N^α + B/D^β
```

Onde:
- `E` = entropia irredutível dos dados — o "teto" de qualquer modelo de linguagem, determinado pela natureza estocástica da linguagem humana
- `N` = número de parâmetros do modelo
- `D` = número de tokens de treinamento
- `A`, `B` = constantes positivas estimadas empiricamente
- `α ≈ 0.34` — expoente do scaling com parâmetros
- `β ≈ 0.28` — expoente do scaling com dados

A loss decresce como uma lei de potência tanto com N quanto com D, mas com taxas diferentes. Importante: os dois termos são **substitutos imperfeitos** — tokens adicionais não compensam indefinidamente a falta de parâmetros, e vice-versa.

### Compute-Optimal Training

Dado um budget computacional fixo `C` (medido em FLOPs), qual a combinação ótima de `N` e `D`?

A relação entre compute, parâmetros e tokens é aproximada por:

```
C ≈ 6 × N × D
```

(6 porque cada token requer ~2N FLOPs no forward pass e ~4N no backward, totalizando 6N por token)

Maximizando a performance sujeito ao constraint de compute, Chinchilla derivou:

```
N_opt ∝ C^0.5
D_opt ∝ C^0.5
```

Ou seja, **parâmetros e tokens devem crescer proporcionalmente** com o budget de compute — aproximadamente na proporção de 20 tokens por parâmetro.

### Implicações Práticas

Esta descoberta teve consequências enormes para a indústria:

**GPT-3 (175B params, 300B tokens) era dramatically undertrained:**
- Compute-optimal para 175B parâmetros: ~3.5T tokens
- GPT-3 usou apenas 300B tokens — menos de 10% do ideal

**Chinchilla (70B params, 1.4T tokens) superou GPT-3 em quase todos os benchmarks com menos parâmetros** — demonstrando que a proporção importa mais que o tamanho absoluto.

**Llama 2 7B treinado com 2T tokens** é compute-optimal para *inferência* (não para treinamento), porque em deployment, você quer o menor modelo possível que atinja a qualidade desejada — mais fácil de servir, mais barato, menor latência.

> [!tip] Regra dos 20 Tokens por Parâmetro
> Para modelos que serão usados em inferência (não apenas treinamento), treine com ~20x mais tokens do que parâmetros. Llama 3 8B com 15T tokens é compute-optimal para deployment. Mais tokens > mais parâmetros dado o mesmo budget. A intuição: tokens são dados de treinamento gratuitos (custo marginal zero), parâmetros custam VRAM em cada inferência.

---

## Infrastructure: Distributed Training

### Cálculo de FLOPs

Antes de falar em infraestrutura, é fundamental entender como calcular o compute necessário:

```
FLOPs_por_token ≈ 6 × N (forward + backward ≈ 3x forward, forward ≈ 2N)
FLOPs_total = 6 × N × D
```

**Exemplo prático — Llama 3 8B:**
- N = 8 × 10^9 parâmetros
- D = 15 × 10^12 tokens
- FLOPs_total = 6 × 8×10^9 × 15×10^12 = 7.2 × 10^23 FLOPs

Em termos de hardware: uma H100 GPU entrega ~2 × 10^15 FLOPs/s em BF16. Para 7.2 × 10^23 FLOPs:
- Tempo em 1 H100: 7.2×10^23 / 2×10^15 = 3.6×10^8 segundos ≈ 11.4 anos
- Tempo em 1024 H100s (eficiência 40%): ~16 dias

```python
def estimate_training_compute(
    num_params: float,      # número de parâmetros
    num_tokens: float,      # número de tokens de treinamento
    gpu_flops: float = 2e15,  # FLOPs/s por GPU (H100 BF16)
    num_gpus: int = 1024,
    efficiency: float = 0.4,  # MFU (Model FLOP Utilization)
) -> dict:
    """
    Estima compute e tempo de treinamento.
    
    Args:
        num_params: parâmetros do modelo (ex: 8e9 para 8B)
        num_tokens: tokens de treinamento (ex: 15e12 para 15T)
        gpu_flops: FLOPs/s por GPU em mixed precision
        num_gpus: número de GPUs no cluster
        efficiency: utilização efetiva de FLOPs (30-50% é realista)
    
    Returns:
        dict com FLOPs total, dias de treinamento, custo estimado
    """
    total_flops = 6 * num_params * num_tokens
    
    # Compute efetivo do cluster
    cluster_flops_per_sec = gpu_flops * num_gpus * efficiency
    
    # Tempo de treinamento
    training_seconds = total_flops / cluster_flops_per_sec
    training_days = training_seconds / 86400
    
    # Custo estimado (H100 ~$3/hora em cloud)
    cost_usd = (training_seconds / 3600) * num_gpus * 3.0
    
    return {
        "total_flops": total_flops,
        "total_flops_scientific": f"{total_flops:.2e}",
        "training_days": round(training_days, 1),
        "cost_usd_millions": round(cost_usd / 1e6, 2),
        "cluster_config": f"{num_gpus}x H100",
    }

# Exemplo: Llama 3 8B
result = estimate_training_compute(
    num_params=8e9,
    num_tokens=15e12,
    num_gpus=1024,
)
print(result)
# {'total_flops': 7.2e+23, 'training_days': 24.3, 'cost_usd_millions': 2.15, ...}

# Exemplo: modelo hipotético 70B com 2T tokens
result_70b = estimate_training_compute(
    num_params=70e9,
    num_tokens=2e12,
    num_gpus=2048,
)
print(result_70b)
```

### ZeRO Parallelism (DeepSpeed)

Com modelos de dezenas ou centenas de bilhões de parâmetros, um único nó de GPU não tem VRAM suficiente. ZeRO (Zero Redundancy Optimizer) elimina redundância nos estados distribuídos:

**ZeRO Stage 1 — Optimizer State Partitioning:**
- Estados do optimizer Adam (momentum, variance) são particionados entre GPUs
- Cada GPU mantém 1/N dos estados do optimizer
- Redução de VRAM para estados do optimizer: 4x (com Adam em FP32, optimizer states = 12 bytes/param vs pesos = 2 bytes/param em FP16)
- Pesos e gradientes ainda são replicados em todas as GPUs

**ZeRO Stage 2 — + Gradient Partitioning:**
- Além do Stage 1, gradientes também são particionados
- Após backward pass, cada GPU mantém apenas os gradientes para seus parâmetros
- Redução adicional de 2-8x em uso de VRAM
- Overhead de comunicação moderado (all-reduce nos gradientes)

**ZeRO Stage 3 — + Parameter Partitioning:**
- Parâmetros do modelo também são particionados
- Cada GPU mantém apenas 1/N dos pesos
- Para forward/backward, parâmetros são coletados on-the-fly via all-gather
- Permite treinar modelos que não cabem em nenhuma GPU individualmente
- Maior overhead de comunicação — use apenas quando necessário

### Tensor Parallelism (Megatron-LM)

Tensor Parallelism divide as matrizes de peso dentro de cada layer entre GPUs. Para uma projeção linear Y = XW:
- Particionar W em colunas entre N GPUs: W = [W_1 | W_2 | ... | W_N]
- Cada GPU computa X × W_i localmente
- Resultado final requer all-reduce para combinar outputs

Requer GPUs com high-bandwidth interconnect (NVLink) — latência de comunicação é crítica pois acontece em cada forward pass. Ideal para GPUs no mesmo nó.

### Pipeline Parallelism

Pipeline Parallelism distribui layers do transformer entre GPUs diferentes:
- GPU 0: layers 0-8 (embedding + primeiros layers)
- GPU 1: layers 9-16
- GPU 2: layers 17-24
- GPU 3: layers 25-32 + output head

Para esconder latência de comunicação, usa micro-batching com pipeline schedule (1F1B ou interleaved). Um batch é dividido em micro-batches que percorrem o pipeline em ondas.

### Gradient Checkpointing

Durante o backward pass, o framework precisa das ativações de cada layer (calculadas no forward) para computar os gradientes. Armazenar todas as ativações requer VRAM proporcional ao número de layers × tamanho do batch × tamanho da ativação.

Gradient checkpointing resolve isso com um trade-off de compute por memória:
- Durante o forward, **não armazena** as ativações intermediárias (economiza VRAM)
- Durante o backward, **recalcula** as ativações on-the-fly para cada layer
- Custo: ~33% de compute adicional no backward
- Benefício: VRAM de ativações reduzida de O(layers) para O(√layers)

```python
# Gradient checkpointing no HuggingFace Transformers
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Ativar gradient checkpointing ANTES de iniciar o treinamento
model.gradient_checkpointing_enable()

# Verificar que está ativo
print(f"Gradient checkpointing ativo: {model.is_gradient_checkpointing}")

# Com Trainer do HuggingFace, também pode ser configurado via TrainingArguments:
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./output",
    gradient_checkpointing=True,                    # ativa checkpointing
    gradient_checkpointing_kwargs={"use_reentrant": False},  # recomendado PyTorch >= 2.0
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,                  # effective batch = 4 * 8 * n_gpus
    bf16=True,                                      # mixed precision BF16
    learning_rate=3e-4,
    max_steps=10000,
)
```

### Mixed Precision Training

Treinar em FP16/BF16 reduz uso de VRAM pela metade e aumenta throughput em hardware moderno (Tensor Cores da NVIDIA operam 2-8x mais rápido em FP16/BF16 vs FP32).

**Problema do FP16:** range dinâmico pequeno (max ~65504) causa underflow de gradientes pequenos.

**Solução — Loss Scaling:**
1. Multiplicar a loss por um fator de escala grande (ex: 65536) antes do backward
2. Dividir os gradientes pelo mesmo fator antes do optimizer step
3. Ajustar o fator dinamicamente: aumentar quando não ocorre overflow, diminuir quando overflow é detectado

**BF16 vs FP16:**
- BF16 tem o mesmo range dinâmico que FP32 (mas menos precisão)
- BF16 não precisa de loss scaling — mais estável
- Requer hardware Ampere ou mais recente (A100, H100, RTX 3090+)
- **Recomendação atual**: use BF16 quando possível

---

## Inspecionando Dados de Treinamento

```python
# Como inspecionar distribuição de dados de um dataset HuggingFace
from datasets import load_dataset
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

def inspect_dataset(dataset_name: str, split: str = "train", n_samples: int = 10000):
    """
    Carrega e inspeciona distribuição básica de um dataset.
    """
    print(f"Carregando {dataset_name}...")
    dataset = load_dataset(dataset_name, split=f"{split}[:{n_samples}]", streaming=False)
    
    texts = dataset["text"] if "text" in dataset.column_names else dataset["content"]
    
    # Distribuição de comprimentos (em palavras)
    lengths = [len(t.split()) for t in texts]
    
    print(f"\n=== Dataset: {dataset_name} ({n_samples} amostras) ===")
    print(f"Comprimento médio: {np.mean(lengths):.0f} palavras")
    print(f"Comprimento mediano: {np.median(lengths):.0f} palavras")
    print(f"p95: {np.percentile(lengths, 95):.0f} palavras")
    print(f"p99: {np.percentile(lengths, 99):.0f} palavras")
    print(f"Mínimo: {min(lengths)} palavras")
    print(f"Máximo: {max(lengths)} palavras")
    
    # Proporção alfanumérica média
    def alphanum_ratio(text: str) -> float:
        if not text:
            return 0.0
        return sum(1 for c in text if c.isalnum()) / len(text)
    
    ratios = [alphanum_ratio(t) for t in texts]
    print(f"\nProporção alfanumérica média: {np.mean(ratios):.3f}")
    print(f"Documentos com ratio < 0.5: {sum(1 for r in ratios if r < 0.5)} ({sum(1 for r in ratios if r < 0.5)/n_samples*100:.1f}%)")
    
    # Amostra de documentos curtos (potencialmente baixa qualidade)
    short_docs = [(i, t) for i, (t, l) in enumerate(zip(texts, lengths)) if l < 50]
    print(f"\nDocumentos com < 50 palavras: {len(short_docs)} ({len(short_docs)/n_samples*100:.1f}%)")
    
    if short_docs:
        print("\nAmostra de documentos curtos:")
        for i, doc in short_docs[:3]:
            print(f"  [{i}]: {doc[:200]!r}")
    
    return {
        "lengths": lengths,
        "alphanum_ratios": ratios,
        "n_short": len(short_docs),
    }

# Uso
# stats = inspect_dataset("allenai/c4", split="train")
# stats = inspect_dataset("togethercomputer/RedPajama-Data-1T-Sample")
```

---

## Monitoring Durante Treinamento

Durante pré-treinamento, as métricas críticas a monitorar são:

**Loss curves:**
- A training loss deve diminuir suavemente — spikes indicam problemas numéricos ou batches corrompidos
- Verificar grad norm: se muito alta (>10), considerar gradient clipping mais agressivo
- Loss NaN/Inf = training instability — geralmente causada por LR alto ou bugs no dataset

**Métricas de saúde do treino:**
- **Model FLOP Utilization (MFU)**: FLOPs teóricos / FLOPs reais do hardware — alvo >40%
- **GPU memory usage**: deve ser estável, não crescer ao longo do tempo (memory leak)
- **Throughput** (tokens/segundo): deve ser estável — quedas indicam problemas de I/O ou comunicação

> [!warning] Catastrophic Forgetting
> Continuar pré-treinamento sobre um modelo já treinado pode degradar capacidades existentes se a distribuição dos novos dados for diferente. Use replay buffers ou domain-adaptive pretraining cuidadosamente. Um exemplo comum: adaptar um modelo de inglês para português com um corpus pequeno e monolíngue pode degradar o inglês drasticamente. A solução é misturar dados antigos com novos em proporção controlada (ex: 90% novo domínio, 10% dados originais).

---

## Checkpoints e Avaliação

Durante o treinamento, checkpoints são salvos periodicamente (ex: a cada 1000 steps). Cada checkpoint é avaliado em um conjunto de validation set para monitorar a generalização.

**Frequência recomendada:**
- Checkpoint: a cada 1000-5000 steps (dependendo da duração do treinamento)
- Avaliação em benchmarks: a cada 10,000-50,000 steps (mais custoso)
- Alerta de anomalia: a cada step (monitoring automático de loss e grad norm)

**Benchmarks durante pré-treinamento:**
- Não use os mesmos benchmarks que você reportará no paper (contaminação)
- Use um conjunto separado de held-out validation data
- Perihelion-style evaluation: perplexidade em domínios específicos (código, matemática, diálogo)

---

## References

- [Chinchilla: Training Compute-Optimal Language Models (Hoffmann et al., 2022)](https://arxiv.org/abs/2203.15556)
- [GPT-3: Language Models are Few-Shot Learners (Brown et al., 2020)](https://arxiv.org/abs/2005.14165)
- [Scaling Laws for Neural Language Models (Kaplan et al., 2020)](https://arxiv.org/abs/2001.08361)
- [ZeRO: Memory Optimizations Toward Training Trillion Parameter Models (Rajbhandari et al., 2019)](https://arxiv.org/abs/1910.02054)
- [RedPajama: An Open-Source Recipe to Reproduce LLaMA Training Dataset](https://github.com/togethercomputer/RedPajama-Data)
- [Dolma: An Open Corpus of Three Trillion Tokens (Soldaini et al., 2023)](https://huggingface.co/datasets/allenai/dolma)
- [Megatron-LM: Training Multi-Billion Parameter Language Models (Shoeybi et al., 2019)](https://arxiv.org/abs/1909.08053)

---

## Related

- [[transformer-architecture]] — arquitetura do modelo sendo treinado
- [[tokenization]] — como texto é convertido em tokens para o treinamento
- [[gpu-architecture]] — hardware subjacente e suas limitações de memória/compute
- [[fine-tuning-peft]] — etapa seguinte após pré-treinamento
- [[benchmarks-evals]] — como avaliar modelos pré-treinados corretamente
- [[vram-estimation]] — calcular requisitos de memória para treinamento e inferência
