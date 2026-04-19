# AI/LLM Fundamentals — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar 13 arquivos de referência enciclopédica (deep technical) em `tech-vault/03-ai-ml/fundamentals/`, cobrindo a pilha completa de IA/LLM — arquitetura, treinamento, inferência, hardware e avaliação — para servir como base de conhecimento da Vault-Inc e futura fonte para skills e agentes.

**Architecture:** Cada arquivo é autossuficiente (sem dependências de criação entre arquivos), segue o padrão do vault existente (frontmatter YAML + seções padronizadas), e contém fórmulas matemáticas, código Python funcional e wikilinks cruzados. A intenção final é que agentes de IA possam consumir esses arquivos para raciocinar sobre decisões de hardware, treinamento e deployment.

**Tech Stack:** Markdown (Obsidian-flavored), LaTeX inline para fórmulas, Python (PyTorch, HuggingFace Transformers, vLLM), mermaid para diagramas.

**Idioma:** Português BR. Termos técnicos da indústria permanecem em inglês (ex: "fine-tuning", "attention", "quantization").

**Referência de estilo:** Ver `tech-vault/03-ai-ml/llm-patterns/prompt-engineering.md` para o padrão de qualidade esperado. Cada arquivo deve ter no mínimo 600 linhas.

---

## Contexto para Agentes

A Vault-Inc-Library é o centro de conhecimento da Vault Inc, empresa de IA agêntica e investimentos. Os arquivos desta pasta serão usados para:
1. Consulta humana (Erick, founder)
2. Ingestão por agentes de IA (via RAG ou leitura direta)
3. Base para criação de skills especializadas no Claude Code

Por isso, o conteúdo deve ser completo, estruturado e sem ambiguidade — escreva como se um agente de IA fosse usar o arquivo para tomar decisões técnicas reais.

---

## Padrão de Frontmatter (obrigatório em todos os arquivos)

```yaml
---
tags: [ai-ml, fundamentals, <topico-especifico>]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [<Alias Legível>, <Alias Alternativo>]
---
```

## Padrão de Seções (obrigatório em todos os arquivos)

1. `# Título`
2. `## Overview` — o que é, por que importa, onde se encaixa no ecossistema
3. `## Como Funciona` — matemática, fórmulas, algoritmos, diagramas mermaid
4. `## Implementação Prática` — código Python funcional e executável
5. `## Comparativos` — tabelas quando há variantes (nem todos os arquivos precisam)
6. `## Gotchas` — callouts `> [!warning]` com armadilhas reais de produção
7. `## Snippets` — blocos prontos para copy-paste
8. `## References` — papers arxiv, docs oficiais, links
9. `## Related` — wikilinks Obsidian para arquivos relacionados no vault

## Callouts Obsidian (usar consistentemente)

```
> [!tip] Título
> [!warning] Título
> [!info] Título
> [!example] Título
> [!danger] Título
```

---

## Task 0: Criar estrutura de diretório

**Files:**
- Create directory: `tech-vault/03-ai-ml/fundamentals/`

- [ ] **Step 1: Verificar que o diretório não existe**

```bash
ls tech-vault/03-ai-ml/
```

Expected: não existe pasta `fundamentals/`

- [ ] **Step 2: Criar o diretório via criação do primeiro arquivo**

O diretório será criado automaticamente ao criar o primeiro arquivo na Task 1. Nenhuma ação separada necessária.

---

## Task 1: `transformer-architecture.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/transformer-architecture.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

O arquivo deve conter obrigatoriamente:

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, transformer, attention]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Transformer Architecture, Self-Attention, Attention Mechanism]
---
```

**Seções obrigatórias e conteúdo mínimo:**

**Overview:** Introdução ao paper "Attention Is All You Need" (Vaswani et al., 2017). Por que o transformer substituiu RNNs e LSTMs. Decoder-only (GPT, Claude, Llama) vs Encoder-Decoder (T5, BART) vs Encoder-only (BERT). Papel central na IA moderna.

**Como Funciona — Self-Attention:**
Fórmula completa com explicação de cada componente:
```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
```
Onde:
- Q (Query), K (Key), V (Value) são projeções lineares de X
- `d_k` é a dimensão das keys (raiz quadrada evita gradientes muito pequenos após softmax)
- Complexidade: O(n²·d) em memória e tempo

Multi-Head Attention:
```
MultiHead(Q,K,V) = Concat(head_1,...,head_h) * W^O
head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

**Positional Encoding — três variantes:**
1. Sinusoidal (original): `PE(pos,2i) = sin(pos/10000^(2i/d_model))`
2. RoPE (Rotary PE — Llama, Mistral): rotação complexa de Q e K, extrapolação de comprimento
3. ALiBi (MPT, Falcon): bias linear na atenção por distância relativa

**FFN (Feed-Forward Network):**
- Clássico: `FFN(x) = max(0, xW_1 + b_1)W_2 + b_2` (ReLU)
- SwiGLU (Llama 2+): `SwiGLU(x,W,V,b,c) = Swish(xW+b) ⊗ (xV+c)`
- Por que SwiGLU é melhor: gradientes mais suaves, performance empírica

**Normalização:**
- LayerNorm: `LayerNorm(x) = (x - μ) / (σ + ε) * γ + β`
- RMSNorm (Llama): `RMSNorm(x) = x / RMS(x) * γ` onde `RMS(x) = sqrt(mean(x²))`
- Pre-norm vs Post-norm: estabilidade de treinamento

**Diagrama mermaid** do fluxo completo de um decoder-only transformer block.

**Implementação Prática:** Implementação de self-attention from scratch em PyTorch (~50 linhas), e exemplo de uso do `transformers` para inspecionar pesos de atenção de um modelo real (ex: GPT-2).

**Comparativos:** Tabela decoder-only vs encoder-decoder vs encoder-only com exemplos de modelos, casos de uso, vantagens.

**Gotchas:**
- Attention sink (token `<bos>` absorve atenção desproporcionalmente)
- Flash Attention não é exatamente igual ao attention padrão (pequenas diferenças numéricas)
- Positional encoding limita comprimento de contexto — RoPE resolve melhor que sinusoidal

**References:** Paper original (arxiv:1706.03762), RoPE (arxiv:2104.09864), SwiGLU (arxiv:2002.05202), Flash Attention (arxiv:2205.14135)

**Related:** `[[kv-cache-attention]]`, `[[gpu-architecture]]`, `[[embeddings]]`, `[[tokenization]]`, `[[pretraining]]`, `[[prompt-engineering]]`

- [ ] **Step 2: Verificar checklist de qualidade**

```
- [ ] Frontmatter YAML válido com todos os campos
- [ ] Fórmula Attention(Q,K,V) presente e explicada
- [ ] Multi-Head Attention explicado
- [ ] Três variantes de positional encoding (sinusoidal, RoPE, ALiBi)
- [ ] SwiGLU vs ReLU FFN
- [ ] LayerNorm vs RMSNorm com fórmulas
- [ ] Código PyTorch funcional
- [ ] Pelo menos 1 callout > [!warning]
- [ ] Pelo menos 5 wikilinks no Related
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/transformer-architecture.md
git commit -m "docs(ai-fundamentals): add transformer architecture deep-technical reference"
```

---

## Task 2: `tokenization.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/tokenization.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, tokenization, bpe, nlp]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Tokenization, BPE, Byte Pair Encoding, Tokenizer]
---
```

**Conteúdo obrigatório:**

**Overview:** O que é tokenização, por que existe (modelos operam em tokens, não caracteres ou palavras). Impacto direto em custo (preço por token), latência, e capacidade de raciocínio do modelo.

**Como Funciona — BPE (Byte Pair Encoding):**

Pseudocódigo completo do algoritmo:
```
1. Inicializar vocabulário com caracteres individuais
2. Contar frequência de todos os pares de símbolos adjacentes
3. Merge do par mais frequente → novo símbolo
4. Repetir até atingir tamanho de vocabulário desejado
```

Exemplo passo a passo com corpus real pequeno mostrando merges sucessivos.

**WordPiece** (BERT): similar ao BPE mas maximiza probabilidade do corpus em vez de frequência de pares. Subword units com `##` prefix.

**SentencePiece / Unigram** (Llama, T5): trata o texto como sequência de bytes, sem pre-tokenization por espaços. Robusto para múltiplos idiomas. Algoritmo Unigram: começa com vocabulário grande e poda tokens com menor impacto na perda.

**tiktoken** (OpenAI / Claude): implementação em Rust do BPE, extremamente rápida. Vocabulários cl100k_base (GPT-4), o200k_base.

**Tabela comparativa** dos tokenizers com: modelo, algoritmo, tamanho de vocabulário, velocidade, suporte multilingual.

**Fertility Rate:** tokens por palavra em diferentes idiomas. Inglês ~1.3 tokens/palavra, Português ~1.5, Chinês ~2-3. Impacto em custo e raciocínio.

**Implementação Prática:**
- Treinar um BPE tokenizer do zero com `tokenizers` (HuggingFace)
- Comparar tokenização de diferentes modelos para o mesmo texto
- Calcular fertility rate para diferentes idiomas

**Gotchas:**
- Números são tokenizados de forma imprevisível (ex: "1234" pode ser 1-4 tokens)
- Espaços à esquerda importam — " token" ≠ "token"
- Tokens especiais ([CLS], [SEP], <|endoftext|>) reservados
- Vocabulário inadequado para o domínio aumenta custo e reduz acurácia

**References:** BPE original (Sennrich et al., 2016, arxiv:1508.07909), SentencePiece (arxiv:1808.06226), tiktoken repo

**Related:** `[[transformer-architecture]]`, `[[pretraining]]`, `[[embeddings]]`, `[[benchmarks-evals]]`

- [ ] **Step 2: Verificar checklist de qualidade**

```
- [ ] Algoritmo BPE completo em pseudocódigo
- [ ] Exemplo passo a passo com corpus
- [ ] WordPiece, SentencePiece/Unigram explicados
- [ ] Tabela comparativa de tokenizers
- [ ] Fertility rate com números reais para PT-BR
- [ ] Código HuggingFace tokenizers funcional
- [ ] Callouts sobre gotchas numéricos e de espaços
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/tokenization.md
git commit -m "docs(ai-fundamentals): add tokenization deep-technical reference"
```

---

## Task 3: `embeddings.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/embeddings.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, embeddings, vector-search, semantic-similarity]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Embeddings, Vector Embeddings, Semantic Embeddings]
---
```

**Conteúdo obrigatório:**

**Overview:** O que são embeddings — representação de texto como vetores em espaço de alta dimensão. Relação com [[rag-architecture]] e [[vector-dbs]].

**Como Funciona — Geometria do Espaço Vetorial:**

Três métricas de similaridade com fórmulas completas:
- Cosine similarity: `cos(θ) = (A·B) / (|A|·|B|)`
- Euclidean distance (L2): `d(A,B) = sqrt(Σ(a_i - b_i)²)`
- Dot product: `A·B = Σ(a_i·b_i)`

Quando usar cada métrica: cosine para textos (normaliza magnitude), dot product para modelos treinados com ele (ex: OpenAI text-embedding-3), L2 para espaços onde magnitude importa.

**Arquitetura de Modelos de Embedding:**
- Bi-encoder vs Cross-encoder: trade-off velocidade vs qualidade
- Mean pooling vs [CLS] token pooling
- Dimensões: 384 (MiniLM) → 768 (BERT-base) → 1536 (text-embedding-3-small) → 3072 (text-embedding-3-large)

**Modelos principais** com tabela: sentence-transformers (all-MiniLM-L6-v2, all-mpnet-base-v2), OpenAI text-embedding-3-small/large, Cohere embed-v3, E5-large-v2, BGE-M3, Voyage AI.

**Matryoshka Representation Learning (MRL):** embeddings que permitem truncar dimensões sem perda proporcional. Como text-embedding-3 implementa isso.

**Anisotropia:** problema em que embeddings se agrupam em cone estreito do espaço vetorial, reduzindo discriminabilidade. Soluções: whitening, normalização.

**Dimensionality Reduction:**
- PCA: redução linear, preserva variância
- UMAP: não-linear, preserva estrutura local e global, útil para visualização
- t-SNE: visualização 2D/3D, não usar para redução funcional

**Implementação Prática:**
- Gerar embeddings com sentence-transformers e fazer busca por cosine similarity
- Comparar qualidade de diferentes modelos no mesmo corpus
- UMAP 2D de embeddings de diferentes domínios (visualização)
- Implementar nearest neighbor search com numpy (sem vector DB)

**Gotchas:**
- Embeddings de modelos diferentes não são comparáveis entre si
- Comprimento do texto afeta qualidade — textos longos diluem o embedding
- Embedding de queries ≠ embedding de documentos em modelos assimétricos (E5, BGE)
- Drift semântico: re-embedar corpus quando trocar de modelo

**References:** SBERT (arxiv:1908.10084), MRL (arxiv:2205.13147), text-embedding-3 (OpenAI blog), BGE (arxiv:2309.07597)

**Related:** `[[transformer-architecture]]`, `[[rag-architecture]]`, `[[vector-dbs]]`, `[[kv-cache-attention]]`, `[[tokenization]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Fórmulas das 3 métricas de similaridade
- [ ] Quando usar cada métrica
- [ ] Bi-encoder vs cross-encoder
- [ ] Tabela de modelos com dimensões e casos de uso
- [ ] MRL (Matryoshka) explicado
- [ ] Anisotropia e soluções
- [ ] Código sentence-transformers funcional
- [ ] Visualização UMAP em código
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/embeddings.md
git commit -m "docs(ai-fundamentals): add embeddings deep-technical reference"
```

---

## Task 4: `pretraining.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/pretraining.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, pretraining, scaling-laws, training]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Pretraining, LLM Pretraining, Scaling Laws, Chinchilla]
---
```

**Conteúdo obrigatório:**

**Overview:** O que é pré-treinamento, distinção entre pre-training, SFT, RLHF. Por que é tão custoso.

**Como Funciona — Objective de Treinamento:**

Cross-entropy loss para next-token prediction:
```
L = -1/T * Σ log P(x_t | x_<t)
```
Por que funciona: aprender a prever o próximo token implica compreender linguagem, fatos, raciocínio.

**Data Pipelines:**
- Fontes: Common Crawl, Books, Wikipedia, GitHub, arXiv, StackOverflow
- Deduplication com MinHash LSH: como funciona o algoritmo, por que duplicatas são tão prejudiciais
- Quality filtering: heurísticas (comprimento, proporção de caracteres alfanuméricos, perplexidade com modelo de referência)
- Decontamination: remover benchmarks de eval do conjunto de treino

**Scaling Laws (Chinchilla):**

Fórmula de Hoffmann et al. 2022:
```
L(N, D) = E + A/N^α + B/D^β
```
Onde N = parâmetros, D = tokens de treino.

Compute-optimal: `N_opt ≈ D_opt` (proporção 1:20 tokens por parâmetro).

GPT-3 era undertrained. Llama/Mistral: modelos menores treinados com mais tokens → melhores para inferência.

**Curriculum Learning:** ordem dos dados importa. Warm-up com dados de alta qualidade, depois diversidade.

**Infraestrutura:** ZeRO parallelism (estágios 1,2,3), tensor parallelism, pipeline parallelism. Checkpointing de ativações para economizar memória.

**Implementação Prática:**
- Estimar compute necessário: FLOPs = 6 × N × D
- Calcular tokens ótimos dado um budget de compute
- Código para inspecionar distribuição de dados de treino
- Como usar `datasets` HuggingFace para construir data pipeline simples

**Gotchas:**
- Catastrophic forgetting ao continuar pré-treinamento
- Data contamination invalida benchmarks
- Learning rate schedule importa muito (cosine com warmup)
- Gradient clipping (max_norm=1.0) essencial para estabilidade

**References:** Chinchilla (arxiv:2203.15556), GPT-3 (arxiv:2005.14165), RedPajama, Dolma dataset papers

**Related:** `[[transformer-architecture]]`, `[[tokenization]]`, `[[gpu-architecture]]`, `[[fine-tuning-peft]]`, `[[benchmarks-evals]]`, `[[vram-estimation]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Fórmula cross-entropy loss
- [ ] MinHash LSH para deduplication explicado
- [ ] Scaling laws com fórmula de Chinchilla
- [ ] Compute-optimal training ratio
- [ ] ZeRO parallelism stages explicados
- [ ] Cálculo de FLOPs (6×N×D)
- [ ] Código data pipeline
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/pretraining.md
git commit -m "docs(ai-fundamentals): add pretraining and scaling laws deep-technical reference"
```

---

## Task 5: `fine-tuning-peft.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/fine-tuning-peft.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, fine-tuning, lora, qlora, peft]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Fine-tuning, PEFT, LoRA, QLoRA, Parameter-Efficient Fine-Tuning]
---
```

**Conteúdo obrigatório:**

**Overview:** Quando fine-tuning é necessário vs RAG vs prompting. Full fine-tuning vs PEFT. Custo computacional de cada abordagem.

**LoRA — Low-Rank Adaptation:**

Álgebra linear completa:
```
W' = W + ΔW = W + BA
onde B ∈ ℝ^{d×r}, A ∈ ℝ^{r×k}, r << min(d,k)
```
Por que funciona: a "atualização" de pesos durante fine-tuning tem rank intrínseco baixo.

Parâmetros treináveis: `r×(d+k)` vs `d×k` (full). Para r=8, d=k=4096: 65k vs 16M parâmetros.

Alpha scaling: `ΔW = (α/r) * BA`. Por que dividir por r: normalização para estabilidade.

**Seleção de Rank:**
- r=4: tarefas simples de estilo
- r=8: fine-tuning geral (padrão)
- r=16-32: tarefas complexas de raciocínio
- r=64+: raramente vale o custo

**Quais camadas aplicar LoRA:** query, key, value, output projections. Opcional: FFN layers. Embed tokens raramente.

**QLoRA:**
- Modelo base em NF4 (4-bit Normal Float) durante training
- Double quantization: quantizar as constantes de quantização também
- Paged optimizers: mover estados do optimizer para CPU RAM quando GPU satura
- LoRA adapters em FP16 sobre modelo quantizado em 4-bit

**Merge de Adapters:** `W_merged = W_base + (α/r) * BA`. Como fazer com `peft` library. Antes vs depois do merge para serving.

**Fine-tuning vs RAG — quando usar cada um:**

| Critério | Fine-tuning | RAG |
|----------|-------------|-----|
| Conhecimento novo | Difícil (catastrophic forgetting) | Ideal |
| Comportamento/estilo | Ideal | Limitado |
| Latência | Menor (sem retrieval) | Maior |
| Custo upfront | Alto (GPU compute) | Baixo |
| Atualização de dados | Requer re-treino | Troca de documentos |

**Implementação Prática:**
- Fine-tuning com `peft` + `trl` + `transformers` (SFT completo com QLoRA)
- Código para calcular parâmetros treináveis antes/depois de LoRA
- Como fazer merge e upload para HuggingFace Hub

**Gotchas:**
- Overfitting rápido com datasets pequenos (<1000 exemplos)
- Learning rate 10x menor que pre-training (5e-5 → 2e-4)
- Dados de fine-tuning contaminam o modelo permanentemente
- Catastrophic forgetting: usar replay buffer ou regularização

**References:** LoRA (arxiv:2106.09685), QLoRA (arxiv:2305.14314), Alpaca (Stanford), Vicuna

**Related:** `[[rlhf-alignment]]`, `[[vram-estimation]]`, `[[quantization]]`, `[[pretraining]]`, `[[gpu-architecture]]`, `[[rag-architecture]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Fórmula LoRA com álgebra linear completa
- [ ] Cálculo de parâmetros treináveis
- [ ] Alpha scaling explicado
- [ ] QLoRA com NF4 e double quantization
- [ ] Tabela fine-tuning vs RAG
- [ ] Código SFT completo com peft+trl
- [ ] Merge de adapters em código
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/fine-tuning-peft.md
git commit -m "docs(ai-fundamentals): add fine-tuning and PEFT (LoRA/QLoRA) deep-technical reference"
```

---

## Task 6: `rlhf-alignment.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/rlhf-alignment.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, rlhf, alignment, dpo, constitutional-ai]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [RLHF, Alignment, DPO, Constitutional AI, RLAIF]
---
```

**Conteúdo obrigatório:**

**Overview:** Por que alignment é necessário. SFT sozinho não é suficiente. Pipeline completo: Base Model → SFT → RLHF/DPO → Deployed Model.

**Pipeline RLHF:**

1. **SFT (Supervised Fine-Tuning):** treinar no comportamento desejado com demonstrations
2. **Reward Model:** treinar um modelo separado para pontuar respostas com dados de preferência humana (Bradley-Terry model: `P(A > B) = σ(r(A) - r(B))`)
3. **PPO (Proximal Policy Optimization):**
   ```
   L_RLHF = E[r(y|x)] - β * KL(π_θ || π_ref)
   ```
   - `r(y|x)`: score do reward model
   - `β * KL(...)`: penalidade por se distanciar do modelo SFT de referência
   - β controla o trade-off alignment vs capability

**DPO — Direct Preference Optimization:**

Elimina o reward model separado. Loss diretamente sobre pares de preferência (chosen, rejected):
```
L_DPO = -E[log σ(β * log(π_θ(y_w|x)/π_ref(y_w|x)) - β * log(π_θ(y_l|x)/π_ref(y_l|x)))]
```
Por que é mais estável que PPO: sem RL, sem reward hacking.

**Constitutional AI (Anthropic):**
- Modelo critica suas próprias respostas segundo um conjunto de princípios (constituição)
- RLAIF: usar o próprio LLM como reward model em vez de humanos

**Algoritmos mais recentes:**
- ORPO: sem modelo de referência, regularização incorporada à loss
- GRPO (DeepSeek): group relative policy optimization, mais eficiente que PPO
- SimPO: simplificação do DPO sem modelo de referência

**Reward Hacking / Goodhart's Law:** quando o modelo aprende a maximizar o proxy (reward model) em vez do objetivo real. Exemplos clássicos e como mitigar.

**Implementação Prática:**
- Treinar DPO com `trl` library (código completo)
- Criar dataset de preferências no formato correto
- Avaliar alignment com win rate vs modelo base

**Gotchas:**
- Reward model colapsa com muitos passos de PPO
- DPO é sensível à qualidade dos dados de preferência
- KL penalty (β) muito alto: modelo não aprende; muito baixo: reward hacking
- Alignment tax: performance em benchmarks pode cair após RLHF

**References:** InstructGPT/RLHF (arxiv:2203.02155), DPO (arxiv:2305.18290), Constitutional AI (arxiv:2212.08073), ORPO (arxiv:2403.07691)

**Related:** `[[fine-tuning-peft]]`, `[[pretraining]]`, `[[benchmarks-evals]]`, `[[prompt-engineering]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Pipeline RLHF completo (SFT → RM → PPO)
- [ ] Fórmula Bradley-Terry para reward model
- [ ] Fórmula PPO com KL penalty
- [ ] Fórmula DPO completa
- [ ] Constitutional AI e RLAIF explicados
- [ ] Reward hacking com exemplos
- [ ] Código DPO com trl completo
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/rlhf-alignment.md
git commit -m "docs(ai-fundamentals): add RLHF and alignment (DPO, Constitutional AI) deep-technical reference"
```

---

## Task 7: `kv-cache-attention.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/kv-cache-attention.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, kv-cache, attention, flash-attention, inference]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [KV Cache, Paged Attention, Flash Attention, GQA]
---
```

**Conteúdo obrigatório:**

**Overview:** Por que o KV cache é o componente mais crítico de inferência. Relação com VRAM e throughput.

**Como Funciona o KV Cache:**

Em autoregressive generation, a cada novo token gerado, os tokens anteriores são re-computados. O KV cache armazena K e V (não Q, pois Q muda a cada passo).

Por que só K e V? Porque `Attention(Q_t, K_{1:t}, V_{1:t})` — Q do token atual precisa atender a todos os K e V anteriores.

VRAM do KV cache: `2 × n_layers × n_heads × d_head × seq_len × batch_size × bytes_per_element`

Exemplo numérico para Llama 3 8B (32 layers, 32 heads, d_head=128, seq=4096, batch=1, FP16):
`2 × 32 × 32 × 128 × 4096 × 1 × 2 = 2GB`

**Paged Attention (vLLM):**
Analogia com virtual memory do OS. Problema: KV cache de requests diferentes desperdiça memória por fragmentação. Solução: blocos de tamanho fixo (16-32 tokens) alocados dinamicamente, shared entre requests em beam search.

**GQA, MQA, MHA:**

| Variante | Heads Q | Heads KV | VRAM KV cache | Modelos |
|---------|---------|----------|---------------|---------|
| MHA (Multi-Head) | h | h | 1x | GPT-2, BERT |
| MQA (Multi-Query) | h | 1 | 1/h x | Falcon |
| GQA (Grouped-Query) | h | g (g<h) | g/h x | Llama 2/3, Mistral |

Fórmula GQA: grupos de Q compartilham o mesmo par KV.

**Sliding Window Attention (Mistral, Mixtral):**
Cada token atende apenas aos W tokens anteriores. Complexidade O(n×W) em vez de O(n²). Eficaz para sequências longas.

**Flash Attention:**
Problema original: atenção padrão materializa a matriz n×n em HBM → bottleneck de bandwidth.
Flash Attention: divide Q, K, V em tiles e computa atenção em SRAM (muito mais rápida). Mathematically equivalent mas IO-aware.

Flash Attention 2: melhor paralelização, suporte a GQA.
Flash Attention 3 (H100): explora Tensor Cores com FP8.

**Implementação Prática:**
- Como medir o tamanho do KV cache de um modelo em runtime
- Configurar vLLM com paged attention
- Habilitar Flash Attention 2 no HuggingFace

**Gotchas:**
- KV cache cresce linearmente com batch_size × seq_len — principal limitação de batch grande
- Paged attention tem overhead para sequências curtas
- Flash Attention não suporta attention bias arbitrário (ex: ALiBi com versões antigas)

**References:** Flash Attention (arxiv:2205.14135), Flash Attention 2 (arxiv:2307.08691), Paged Attention/vLLM (arxiv:2309.06180), GQA (arxiv:2305.13245)

**Related:** `[[transformer-architecture]]`, `[[inference-engines]]`, `[[vram-estimation]]`, `[[gpu-architecture]]`, `[[quantization]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Por que só K e V são cacheados (explicação clara)
- [ ] Fórmula e exemplo numérico de VRAM do KV cache
- [ ] Paged Attention com analogia de virtual memory
- [ ] Tabela MHA vs MQA vs GQA com modelos reais
- [ ] Flash Attention — IO-awareness explicada
- [ ] Código para medir KV cache em runtime
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/kv-cache-attention.md
git commit -m "docs(ai-fundamentals): add KV cache and attention mechanisms deep-technical reference"
```

---

## Task 8: `quantization.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/quantization.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, quantization, gptq, awq, gguf]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Quantization, GPTQ, AWQ, GGUF, INT4, INT8]
---
```

**Conteúdo obrigatório:**

**Overview:** Por que quantizar — trade-off VRAM/velocidade vs qualidade. Quantização pós-treinamento vs quantization-aware training.

**Tipos de Dados:**

Tabela completa:
| Dtype | Bits | Range | Bytes/param | Uso |
|-------|------|-------|-------------|-----|
| FP32 | 32 | ±3.4e38 | 4 | Treinamento |
| FP16 | 16 | ±65504 | 2 | Inferência padrão |
| BF16 | 16 | ±3.4e38 | 2 | Treinamento (H100) |
| INT8 | 8 | -128..127 | 1 | Inferência quantizada |
| INT4 | 4 | -8..7 | 0.5 | Inferência agressiva |
| NF4 | 4 | distribuição normal | 0.5 | QLoRA |
| FP8 | 8 | ±448 | 1 | H100 training/inference |

Por que BF16 é preferível ao FP16 para treinamento: range maior evita overflow.

**Quantização Simétrica vs Assimétrica:**
- Simétrica: `q = round(x / scale)`, onde `scale = max(|x|) / (2^(bits-1) - 1)`
- Assimétrica: `q = round(x / scale) + zero_point`

**Outlier Channels:** problema — alguns canais têm valores muito maiores que outros, degradando a quantização dos demais. Solução: SmoothQuant (divide outliers entre pesos e ativações).

**GPTQ (Post-Training Quantization):**
Usa informação de segunda ordem (Hessian) para minimizar erro de quantização camada por camada. Layer-wise quantization com OBQ (Optimal Brain Quantization). Requer calibration dataset.

**AWQ (Activation-Aware Weight Quantization):**
Observa que 1% dos pesos "salientes" contribuem com 99% do erro. Protege esses pesos com scaling. Mais rápido que GPTQ, qualidade similar.

**GGUF / llama.cpp:**
Formato de arquivo para inferência em CPU (e GPU parcial). Variantes: Q4_0, Q4_K_M, Q5_K_M, Q8_0.
- K = K-quants (agrupa pesos em blocos com escala compartilhada)
- M = Mixed (camadas críticas em maior precisão)

Comparativo de perplexidade por método para Llama 3 8B.

**Implementação Prática:**
- Quantizar modelo com `bitsandbytes` (INT8/INT4)
- Quantizar com AutoGPTQ
- Quantizar com AWQ (`autoawq`)
- Carregar GGUF com `llama-cpp-python`

**Gotchas:**
- Quantização de ativações é mais difícil que de pesos (valores dinâmicos)
- Primeiras e últimas camadas são mais sensíveis — quantizar menos agressivamente
- Perplexidade não captura tudo — testar em tasks reais
- Dequantização durante serving tem overhead mínimo com INT8, maior com INT4

**References:** GPTQ (arxiv:2210.17323), AWQ (arxiv:2306.00978), SmoothQuant (arxiv:2211.10438), QLoRA (arxiv:2305.14314)

**Related:** `[[vram-estimation]]`, `[[inference-engines]]`, `[[gpu-architecture]]`, `[[fine-tuning-peft]]`, `[[kv-cache-attention]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Tabela completa de dtypes com bytes/param
- [ ] Fórmula quantização simétrica e assimétrica
- [ ] Outlier channels e SmoothQuant
- [ ] GPTQ algoritmo (OBQ, Hessian)
- [ ] AWQ algoritmo (salient weights)
- [ ] GGUF variantes (Q4_K_M etc.) explicadas
- [ ] Código bitsandbytes + AutoGPTQ + AWQ
- [ ] Comparativo de perplexidade por método
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/quantization.md
git commit -m "docs(ai-fundamentals): add quantization (GPTQ, AWQ, GGUF) deep-technical reference"
```

---

## Task 9: `inference-engines.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/inference-engines.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, inference, vllm, tensorrt, serving]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Inference Engines, vLLM, TensorRT-LLM, Ollama, LLM Serving]
---
```

**Conteúdo obrigatório:**

**Overview:** Por que inference engines especializados existem. Diferença entre serving de ML clássico e LLMs. Métricas chave: TTFT (Time to First Token), TBT (Time Between Tokens), throughput (tokens/sec), latência P99.

**Continuous Batching:**
Batching estático: aguarda um batch completo antes de iniciar. Problema: tokens gerados a taxas diferentes — GPU fica ociosa.
Continuous batching (iteration-level scheduling): novos requests entram no batch assim que um slot libera, sem esperar todos terminarem. Throughput 2-23x maior.

**Tensor Parallelism vs Pipeline Parallelism:**
- Tensor: divide os pesos de cada camada entre GPUs. Comunicação all-reduce a cada layer. Melhor latência.
- Pipeline: divide camadas entre GPUs. Comunicação menor mas pipeline bubbles. Melhor throughput.

**vLLM:**
- Paged Attention para KV cache eficiente
- Continuous batching nativo
- Suporte a GPTQ, AWQ, FP8
- OpenAI-compatible API
- Como iniciar servidor: `vllm serve meta-llama/Llama-3-8b-Instruct --quantization awq`

**llama.cpp:**
- Inferência CPU (e GPU parcial via CUDA/Metal)
- GGUF format
- Quantização nativa
- Quando usar: desenvolvimento local, hardware sem GPU dedicada, edge

**TensorRT-LLM (NVIDIA):**
- Kernel fusion: combina múltiplas operações em um kernel CUDA
- In-flight batching
- FP8 em H100
- Requer compilação do modelo (engine build) — mais rígido mas mais rápido

**Ollama:**
- Wrapper sobre llama.cpp com UX developer-friendly
- Model registry, versioning, Modelfile
- Não usar em produção de alto throughput

**Speculative Decoding:**
Modelo "draft" pequeno gera K tokens → modelo grande verifica em paralelo. Speedup de 2-3x sem perda de qualidade. Implementado em vLLM e TensorRT-LLM.

**Comparativo:**

| Engine | Backend | Throughput | Latência | Facilidade | Produção |
|--------|---------|-----------|---------|-----------|---------|
| vLLM | CUDA | ★★★★★ | ★★★★ | ★★★★ | ★★★★★ |
| TensorRT-LLM | CUDA | ★★★★★ | ★★★★★ | ★★ | ★★★★ |
| llama.cpp | CPU/CUDA | ★★★ | ★★★ | ★★★★★ | ★★★ |
| Ollama | llama.cpp | ★★ | ★★★ | ★★★★★ | ★★ |

**Implementação Prática:**
- Servidor vLLM completo com Python client
- Benchmark de throughput com vLLM
- Containerizar vLLM com Docker
- Configurar autoscaling por throughput (tokens/sec)

**Gotchas:**
- vLLM v0.x e v0.6+ têm APIs diferentes
- Quantização muda o throughput mas nem sempre melhora latência por token
- Tensor parallelism requer NVLink para GPUs em produção — PCIe tem bandwidth insuficiente

**References:** vLLM (arxiv:2309.06180), Orca/Continuous Batching (arxiv:2207.04836), Speculative Decoding (arxiv:2211.17192)

**Related:** `[[quantization]]`, `[[gpu-architecture]]`, `[[vram-estimation]]`, `[[kv-cache-attention]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] TTFT, TBT, throughput definidos
- [ ] Continuous batching explicado com diagrama
- [ ] Tensor vs pipeline parallelism
- [ ] Tabela comparativa dos 4 engines
- [ ] Speculative decoding
- [ ] Código vLLM servidor + client completo
- [ ] Docker para vLLM
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/inference-engines.md
git commit -m "docs(ai-fundamentals): add inference engines (vLLM, TensorRT, llama.cpp) deep-technical reference"
```

---

## Task 10: `gpu-architecture.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/gpu-architecture.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, gpu, cuda, hardware, nvidia]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [GPU Architecture, CUDA, Tensor Cores, GPU for AI]
---
```

**Conteúdo obrigatório:**

**Overview:** Por que GPUs dominam AI. SIMD vs SIMT. CPU vs GPU para matrix multiply.

**Hierarquia de Execução CUDA:**
```
GPU
└── Streaming Multiprocessors (SM)
    └── Warps (32 threads cada)
        └── CUDA Threads
```
Warp: unidade de execução. 32 threads executam a mesma instrução simultaneamente (SIMT). Divergência de warp (branch dentro de warp) é o maior inimigo de performance.

**CUDA Cores vs Tensor Cores:**
- CUDA Cores: operações FP32/INT32 escalares
- Tensor Cores: matrix multiply 4×4 em hardware. A100: 312 TFLOPS FP16 com Tensor Cores vs 19.5 TFLOPS FP32 com CUDA Cores.

Operação de Tensor Core: `D = A × B + C` onde A,B,C,D são matrizes. Necessita de dados em formato específico.

**Hierarquia de Memória:**
| Tipo | Capacidade | Bandwidth | Latência |
|------|-----------|-----------|---------|
| Registros | ~256KB/SM | 40 TB/s | ~1 ciclo |
| L1/Shared | 128KB/SM | ~19 TB/s | ~30 ciclos |
| L2 | 50-80MB | ~5 TB/s | ~200 ciclos |
| HBM (VRAM) | 40-192GB | 0.9-3.35 TB/s | ~600 ciclos |

**Memory Bandwidth vs Compute (Arithmetic Intensity):**
```
Arithmetic Intensity = FLOPs / Bytes transferidos
```
LLMs em inferência são memory-bound (intensity < 1). Treinamento é compute-bound.
Roofline model: como saber se seu kernel é memory ou compute bound.

**Comparativo de Hardware:**

| GPU | VRAM | Bandwidth | FP16 TFLOPS | Tensor | Consumo | Preço |
|-----|------|-----------|-------------|--------|---------|-------|
| RTX 4090 | 24GB GDDR6X | 1008 GB/s | 82.6 | 4th gen | 450W | ~$2000 |
| RTX 4080 | 16GB GDDR6X | 717 GB/s | 49 | 4th gen | 320W | ~$1200 |
| A100 80GB | 80GB HBM2e | 2000 GB/s | 77.6 | 3rd gen | 400W | ~$10k |
| H100 SXM | 80GB HBM3 | 3350 GB/s | 989 | 4th gen FP8 | 700W | ~$30k |
| H100 NVL | 188GB HBM3e | 7400 GB/s | 1979 | 4th gen | 1000W | ~$40k |

**NVLink vs PCIe para Multi-GPU:**
NVLink: 600 GB/s bidirecional entre GPUs. PCIe 4.0 x16: 32 GB/s. Para tensor parallelism em produção, NVLink é obrigatório.

**Como GPUs Executam Transformers:**
Matrix multiply (GEMM) — a operação mais frequente. batched GEMM para multi-head attention. Onde Flash Attention encaixa (tiles em SRAM para evitar HBM round-trips).

**Implementação Prática:**
- Medir bandwidth de VRAM com PyTorch
- Perfiling de kernels com `torch.profiler` e NVIDIA Nsight
- Identificar gargalos: memory bound vs compute bound

**Gotchas:**
- VRAM não é só pesos: ativações, optimizer states, overhead do framework
- PCIe 4.0 vs 5.0 importa para CPU-GPU transfers (NVMe e dados)
- Power limit throttling: 4090 em 450W pode ser melhor que 350W (afeta boost clock)

**References:** NVIDIA H100 whitepaper, Flash Attention papers, "Making Deep Learning Go Brrrr" (blog Horace He)

**Related:** `[[specialized-hardware]]`, `[[vram-estimation]]`, `[[inference-engines]]`, `[[kv-cache-attention]]`, `[[quantization]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Hierarquia SM → Warp → Thread explicada
- [ ] CUDA Cores vs Tensor Cores com TFLOPS reais
- [ ] Tabela de hierarquia de memória com bandwidths
- [ ] Arithmetic intensity e roofline model
- [ ] Tabela comparativa de GPUs (4090, A100, H100)
- [ ] NVLink vs PCIe para multi-GPU
- [ ] Código de profiling com torch.profiler
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/gpu-architecture.md
git commit -m "docs(ai-fundamentals): add GPU architecture (CUDA, Tensor Cores, memory hierarchy) deep-technical reference"
```

---

## Task 11: `specialized-hardware.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/specialized-hardware.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, hardware, tpu, groq, cerebras, inferentia]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Specialized AI Hardware, TPU, Groq LPU, Cerebras, AI Chips]
---
```

**Conteúdo obrigatório:**

**Overview:** Por que hardware especializado além de GPUs. Trade-offs: flexibilidade vs eficiência. Quando cada chip faz sentido.

**Google TPU (Tensor Processing Unit):**

Systolic array — como funciona em hardware: dados fluem entre processing elements (PEs) sem passar pela memória central. Matrix multiply nativa em hardware.

TPU v4: 275 TFLOPS BF16, 32GB HBM, interconexão de alta bandwidth entre chips (ICI). Pod de TPUs = centenas de chips interconectados.
TPU v5p: 459 TFLOPS BF16, otimizado para treinamento.

XLA (Accelerated Linear Algebra): compiler que otimiza grafo de operações para TPU. TensorFlow e JAX rodam nativamente. PyTorch/XLA via torch_xla.

Limitações: menos flexível que GPU (operações não-convencionais são lentas), difícil de debugar, ecossistema menor.

**Groq LPU (Language Processing Unit):**

Deterministic execution: sem caches, sem branch prediction, execução com latência fixa e previsível. Por que isso importa: jitter zero → latência consistente para serving.

TSP (Tensor Streaming Processor): 1 chip = 230 TFLOPS, 80MB SRAM on-chip (sem HBM). 

Performance: 500+ tokens/sec para Llama 3 70B (vs ~30 tokens/sec em A100 single). Trade-off: sem flexibilidade para treinamento, batch size limitado.

**Cerebras WSE-3 (Wafer-Scale Engine):**

O maior chip de silício já fabricado: 900,000 AI cores, 44GB SRAM on-chip (sem HBM!), 125 PFLOPS INT8.

Por que wafer-scale: elimina interchip latency. Comunicação entre cores em picossegundos vs millisegundos entre chips.

CS-3 system: conecta múltiplos WSEs via SwarmX fabric. Usado para treinamento de modelos gigantescos.

**AWS Trainium e Inferentia 2:**
- Trainium: chip de treinamento, 95 TFLOPS FP16, barato em EC2 trn1
- Inferentia 2: chip de inferência, baixa latência, integração com SageMaker
- SDK: AWS Neuron (fork do PyTorch/XLA)

**Apple Neural Engine (ANE):**
- Integrado nos chips M1/M2/M3/M4
- Eficiência energética: 38 TOPS com <10W
- Relevância: edge inference, Core ML, llama.cpp com Metal backend

**Tenstorrent:**
- Startup fundada pelo criador do chip do A100 (Jim Keller)
- Wormhole e Blackhole chips: arquitetura mesh de tensix cores
- Open-source friendly (menos walled garden que NVIDIA)

**Comparativo de Hardware:**

| Chip | Maker | TFLOPS FP16 | Memória | Melhor para |
|------|-------|-------------|---------|------------|
| H100 SXM | NVIDIA | 989 | 80GB HBM3 | Treinamento geral |
| TPU v5p | Google | 459 | HBM | Treinamento JAX/TF |
| Groq LPU | Groq | 230/chip | 80MB SRAM | Inferência ultra-rápida |
| WSE-3 | Cerebras | 125,000 | 44GB SRAM | Modelos gigantes |
| Trainium | AWS | 190 | HBM | Treinamento EC2 |
| M4 Max ANE | Apple | ~38 TOPS | unified | Edge/dev |

**Quando usar cada um:**
- Treinamento geral: H100 / A100
- Treinamento custo-eficiente em nuvem: Trainium
- Inferência de baixíssima latência: Groq
- Modelos > 1T parâmetros: Cerebras / TPU Pod
- Desenvolvimento local: Apple Silicon

**Gotchas:**
- TPUs requerem reescrever código para JAX/XLA — não é plug-and-play com PyTorch
- Groq tem limitações de tamanho máximo de modelo por chip
- Cerebras WSE é vendido como sistema dedicado, não cloud commodity
- Inferentia tem ecossistema menor que CUDA

**References:** Google TPU v4 paper, Groq architecture whitepaper, Cerebras WSE-3 announcement, Tenstorrent docs

**Related:** `[[gpu-architecture]]`, `[[vram-estimation]]`, `[[inference-engines]]`, `[[pretraining]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Systolic array explicado em hardware
- [ ] TPU v4/v5 com specs reais
- [ ] Groq LPU — deterministic execution explicado
- [ ] Cerebras WSE wafer-scale explicado
- [ ] AWS Trainium/Inferentia 2
- [ ] Apple Neural Engine
- [ ] Tabela comparativa completa com quando usar cada um
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/specialized-hardware.md
git commit -m "docs(ai-fundamentals): add specialized AI hardware (TPU, Groq, Cerebras) deep-technical reference"
```

---

## Task 12: `vram-estimation.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/vram-estimation.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, vram, memory, hardware-planning]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [VRAM Estimation, GPU Memory Planning, Model Memory Calculator]
---
```

**Conteúdo obrigatório:**

**Overview:** Saber calcular VRAM necessária antes de comprar hardware ou provisionar nuvem é a habilidade mais prática de engenharia de ML. Este arquivo é um guia de referência para estimativas rápidas e cálculos precisos.

**Regra Rápida:**
```
VRAM_inferência ≈ parâmetros × bytes_por_dtype × 1.2 (overhead)
VRAM_treinamento ≈ parâmetros × bytes_por_dtype × 16 (regra do 16x)
```

**Cálculo Detalhado — Inferência:**

```
VRAM_pesos = N_params × bytes_dtype
VRAM_kv_cache = 2 × n_layers × n_heads × d_head × seq_len × batch × bytes_dtype
VRAM_ativações = ~batch × seq_len × d_model × n_layers × bytes_dtype × 0.1 (aproximado)
VRAM_total = VRAM_pesos + VRAM_kv_cache + VRAM_ativações + overhead_framework (~500MB)
```

**Cálculo Detalhado — Treinamento Full Fine-tuning (Adam):**

```
VRAM_pesos = N × 4 bytes (FP32 master weights)
VRAM_gradientes = N × 4 bytes
VRAM_adam_m = N × 4 bytes (first moment)
VRAM_adam_v = N × 4 bytes (second moment)
VRAM_ativações = depende de gradient checkpointing
Total sem checkpointing ≈ N × 16 bytes
```

**Cálculo Detalhado — QLoRA:**
```
VRAM_base = N × 0.5 bytes (INT4)
VRAM_lora = N_lora × 2 bytes (FP16), onde N_lora << N
VRAM_optimizer = N_lora × 8 bytes (Adam sobre LoRA params apenas)
VRAM_ativações = depende de max_seq_len e batch_size
```

**Exemplos Práticos Completos:**

1. **Llama 3 8B em FP16 para inferência:**
   - Pesos: 8B × 2 = 16GB
   - KV cache (32 layers, 32 heads, d=128, seq=4096, batch=1, FP16): 2GB
   - Total ≈ 18.5GB → cabe em RTX 4090 (24GB)? Sim, mas pouco margem para batch maior.

2. **Llama 3 70B em Q4_K_M para inferência:**
   - Pesos: 70B × 0.5 × 1.1 (overhead Q4_K_M) ≈ 38.5GB
   - KV cache (80 layers, 64 heads GQA→8, d=128, seq=4096, FP16): 2.7GB
   - Total ≈ 42GB → cabe em 2× RTX 4090 (48GB)? Sim.

3. **Fine-tuning Mistral 7B com QLoRA em 1× RTX 4090 (24GB):**
   - Base INT4: 7B × 0.5 = 3.5GB
   - LoRA params (r=16, todas as attention layers): ~100M × 2 = 0.2GB
   - Adam sobre LoRA: 0.2 × 4 = 0.8GB
   - Ativações (seq=2048, batch=4, com gradient checkpointing): ~8GB
   - Total ≈ 12.5GB → viável com margem.

4. **GPT-4 scale (1.8T params MoE, estimado) em produção:**
   - Análise de como estimar para modelos cujos pesos não são públicos

**Tabela de Referência Rápida:**

| Modelo | Params | FP16 | INT8 | INT4 | Hardware mínimo |
|--------|--------|------|------|------|-----------------|
| Phi-3 mini | 3.8B | 7.6GB | 3.8GB | 1.9GB | RTX 3060 12GB |
| Llama 3 8B | 8B | 16GB | 8GB | 4GB | RTX 3080 10GB |
| Mistral 7B | 7B | 14GB | 7GB | 3.5GB | RTX 3080 10GB |
| Llama 3 70B | 70B | 140GB | 70GB | 35GB | 2× A100 80GB |
| Llama 3 405B | 405B | 810GB | 405GB | 202GB | 8× H100 |

**Ferramentas e Snippets:**
- Código Python para calcular VRAM de qualquer modelo HuggingFace automaticamente
- Como usar `nvidia-smi` para monitorar VRAM em tempo real
- `torch.cuda.memory_summary()` para breakdown detalhado

**Gotchas:**
- VRAM reportada pelo `nvidia-smi` inclui overhead do driver e CUDA context (~500MB)
- Pesos quantizados em disco ≠ pesos em VRAM (alguns formatos expandem)
- Gradient checkpointing troca memória por compute (recomputa ativações no backward)
- Framework overhead: vLLM reserva pool de memória no início

**Related:** `[[gpu-architecture]]`, `[[specialized-hardware]]`, `[[quantization]]`, `[[kv-cache-attention]]`, `[[fine-tuning-peft]]`, `[[inference-engines]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] Regra rápida (×2, ×16)
- [ ] Fórmulas detalhadas para inferência e treinamento
- [ ] 4 exemplos numéricos completos e verificados
- [ ] Tabela de referência com modelos populares
- [ ] Código para calcular VRAM automaticamente
- [ ] QLoRA VRAM breakdown
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/vram-estimation.md
git commit -m "docs(ai-fundamentals): add VRAM estimation guide with worked examples"
```

---

## Task 13: `benchmarks-evals.md`

**Files:**
- Create: `tech-vault/03-ai-ml/fundamentals/benchmarks-evals.md`

- [ ] **Step 1: Criar o arquivo com conteúdo completo**

**Frontmatter:**
```yaml
---
tags: [ai-ml, fundamentals, benchmarks, evals, evaluation, mmlu]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Benchmarks, LLM Evals, MMLU, HumanEval, Chatbot Arena]
---
```

**Conteúdo obrigatório:**

**Overview:** Por que benchmarks importam e por que também mentem. Goodhart's Law aplicado a evals: quando um benchmark vira target, deixa de ser boa métrica.

**Benchmarks Principais:**

**MMLU (Massive Multitask Language Understanding):**
- 57 tarefas de múltipla escolha (ABCD) cobrindo 57 domínios
- 4-shot few-shot por padrão
- Metodologia de scoring: accuracy por domínio, macro-average
- Limitações: múltipla escolha não testa geração livre, saturação (GPT-4 já ultrapassa humanos em alguns subsets)

**HumanEval:**
- 164 problemas de programação Python com testes unitários
- Métrica pass@k: `pass@k = 1 - C(n-c, k)/C(n, k)` onde n=amostras geradas, c=corretas
- Por que é fácil de saturar: problemas relativamente simples, contaminação de dados de treino

**MATH:**
- 12.500 problemas de matemática competition-level
- 5 dificuldades (1-5), 7 tópicos
- Mais difícil de saturar que HumanEval
- Métricas: exact match após normalização

**BIG-Bench Hard (BBH):**
- 23 tarefas que GPT-4 não conseguia resolver facilmente quando foi criado
- Raciocínio causal, lógica simbólica, raciocínio multistep
- Chain-of-thought obrigatório para melhores resultados

**LMSYS Chatbot Arena:**
- Comparação humana cega (blind pairwise) de modelos
- Rating Elo: `E(A) = 1/(1 + 10^((R_B - R_A)/400))`
- Atualização Elo após cada jogo
- Por que é valioso: feedback humano real em tasks abertas
- Limitações: viés de verbosidade (respostas longas ganham), viés cultural, não reprodutível

**MT-Bench:**
- 80 perguntas multiturn de alta qualidade
- LLM-as-judge (GPT-4 avalia)
- Escalável mas com viés de auto-preferência do juiz

**Como Rodar Evals Localmente:**

`lm-evaluation-harness` (EleutherAI):
```bash
lm_eval --model hf \
    --model_args pretrained=meta-llama/Llama-3-8b-Instruct \
    --tasks mmlu,hellaswag,arc_challenge \
    --device cuda:0 \
    --batch_size 8
```

**LLM-as-Judge — Metodologia e Vieses:**
- Verbosity bias: modelos preferem respostas mais longas
- Self-preference: Claude prefere respostas parecidas com Claude
- Positional bias: resposta na posição A ganha mais em comparações cegas
- Como mitigar: swap positions, múltiplos juízes, critérios explícitos

**Construindo Evals Customizados para Vault-Inc:**
Framework para criar benchmarks domínio-específicos (ex: análise de investimentos, decisões técnicas de arquitetura). Como usar LLM-as-judge com critérios customizados.

**Gotchas:**
- Data contamination: modelo treinado nos benchmarks infla artificialmente o score
- Prompt sensitivity: resultados mudam com small changes no prompt de eval
- Few-shot order matters: ordem dos exemplos afeta performance
- Versões diferentes do mesmo benchmark podem ter diferenças metodológicas

**References:** MMLU (arxiv:2009.03300), HumanEval (arxiv:2107.03374), BIG-Bench (arxiv:2206.04615), Chatbot Arena (arxiv:2403.04132), LLM-as-judge (arxiv:2306.05685)

**Related:** `[[pretraining]]`, `[[rlhf-alignment]]`, `[[fine-tuning-peft]]`, `[[prompt-engineering]]`, `[[claude-api]]`

- [ ] **Step 2: Verificar checklist**

```
- [ ] MMLU metodologia com 57 tarefas
- [ ] HumanEval pass@k fórmula
- [ ] MATH e BBH cobertos
- [ ] Chatbot Arena Elo rating com fórmula
- [ ] Código lm-evaluation-harness completo
- [ ] LLM-as-judge com vieses documentados
- [ ] Framework para evals customizados
- [ ] Mínimo 600 linhas
```

- [ ] **Step 3: Commit**

```bash
git add tech-vault/03-ai-ml/fundamentals/benchmarks-evals.md
git commit -m "docs(ai-fundamentals): add benchmarks and evals deep-technical reference"
```

---

## Task 14: Atualizar `ai-ml-moc.md`

**Files:**
- Modify: `tech-vault/00-moc/ai-ml-moc.md`

- [ ] **Step 1: Adicionar seção "Fundamentos" ao MOC**

Localizar a linha após o bloco `## 📊 Dashboard` (por volta da linha 28) e adicionar nova seção antes de "🗺️ Skills Map":

```markdown
## 🔬 Fundamentos — Como LLMs Funcionam

> [!info] Nova Seção
> Conhecimento técnico profundo sobre arquitetura, hardware e treinamento. Base para criar skills e agentes especializados na Vault-Inc.

### Arquitetura & Representação

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[transformer-architecture]] | Self-attention, Multi-head, RoPE, SwiGLU, LayerNorm | ✅ active |
| [[tokenization]] | BPE, WordPiece, SentencePiece, tiktoken, fertility rates | ✅ active |
| [[embeddings]] | Espaço vetorial, cosine similarity, modelos, MRL, anisotropia | ✅ active |

### Treinamento

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[pretraining]] | Next-token loss, scaling laws Chinchilla, data pipelines | ✅ active |
| [[fine-tuning-peft]] | LoRA, QLoRA, PEFT, fine-tuning vs RAG | ✅ active |
| [[rlhf-alignment]] | RLHF, DPO, Constitutional AI, reward hacking | ✅ active |

### Inferência & Otimização

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[kv-cache-attention]] | KV cache, paged attention, GQA, Flash Attention | ✅ active |
| [[quantization]] | INT4/INT8, GPTQ, AWQ, GGUF/llama.cpp | ✅ active |
| [[inference-engines]] | vLLM, TensorRT-LLM, llama.cpp, speculative decoding | ✅ active |

### Hardware

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[gpu-architecture]] | CUDA cores, Tensor Cores, HBM, arithmetic intensity | ✅ active |
| [[specialized-hardware]] | TPU, Groq LPU, Cerebras, Trainium, Apple ANE | ✅ active |
| [[vram-estimation]] | Fórmulas, exemplos práticos, tabela de referência | ✅ active |

### Avaliação

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[benchmarks-evals]] | MMLU, HumanEval, Chatbot Arena, LLM-as-judge | ✅ active |
```

Também atualizar o callout `> [!info] Cobertura` para refletir que agora são 23 arquivos (10 anteriores + 13 novos).

- [ ] **Step 2: Verificar que os wikilinks estão corretos**

Confirmar que todos os 13 nomes de arquivo entre `[[]]` correspondem exatamente aos nomes dos arquivos criados (sem extensão .md, sem path).

- [ ] **Step 3: Commit**

```bash
git add tech-vault/00-moc/ai-ml-moc.md
git commit -m "docs(moc): add AI fundamentals section to ai-ml-moc with 13 new references"
```

---

## Verificação Final

- [ ] **Confirmar todos os 13 arquivos existem em `tech-vault/03-ai-ml/fundamentals/`**

```bash
ls tech-vault/03-ai-ml/fundamentals/
```

Expected (13 arquivos):
```
benchmarks-evals.md
embeddings.md
fine-tuning-peft.md
gpu-architecture.md
inference-engines.md
kv-cache-attention.md
pretraining.md
quantization.md
rlhf-alignment.md
specialized-hardware.md
tokenization.md
transformer-architecture.md
vram-estimation.md
```

- [ ] **Verificar wikilinks cruzados entre arquivos novos**

Cada arquivo deve ter `Related` seção com pelo menos 4 wikilinks. Fazer busca rápida:

```bash
grep -c "\[\[" tech-vault/03-ai-ml/fundamentals/*.md
```

Expected: todos os arquivos com count > 4.

- [ ] **Commit final de verificação**

```bash
git log --oneline -15
```

Expected: 15 commits (1 por task + 1 do spec).
