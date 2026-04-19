---
tags: [spec, design, tech-vault, ai-ml, fundamentals]
status: approved
created: 2026-04-14
updated: 2026-04-14
---

# AI/LLM Fundamentals — Design Spec

## Objetivo

Adicionar 13 arquivos de referência enciclopédica (nível deep technical) à pasta `tech-vault/03-ai-ml/fundamentals/`, cobrindo fundamentos de modelos de linguagem, treinamento, inferência, hardware e avaliação. Conteúdo em Português BR com termos técnicos em inglês quando padrão da indústria.

## Contexto

### Estado Atual

O `tech-vault/03-ai-ml/` já contém:

| Subpasta | Arquivos |
|----------|----------|
| `ai-frameworks/` | autogen, claude-code-superpowers, crewai, openai-agents-sdk, vercel-ai-sdk |
| `llm-patterns/` | multi-agent-systems, prompt-engineering, rag-architecture |
| `mcp/` | mcp-servers-guide |
| `tools/` | claude-api |

Faltam os fundamentos técnicos que explicam **como os sistemas de IA funcionam por baixo** — arquitetura de transformers, hardware, training, inferência e avaliação.

### Decisões de Design

- **Abordagem:** Um arquivo por tópico (13 arquivos), sem agrupar
- **Localização:** `tech-vault/03-ai-ml/fundamentals/` (nova subpasta)
- **Profundidade:** Deep technical — fórmulas matemáticas, pseudocódigo, implementações PyTorch/HuggingFace
- **Padrão:** Segue o padrão existente do vault (frontmatter YAML + estrutura de seções)
- **Idioma:** Português BR, termos técnicos em inglês

---

## Estrutura de Arquivos

```
tech-vault/03-ai-ml/fundamentals/
├── transformer-architecture.md
├── tokenization.md
├── embeddings.md
├── pretraining.md
├── fine-tuning-peft.md
├── rlhf-alignment.md
├── kv-cache-attention.md
├── quantization.md
├── inference-engines.md
├── gpu-architecture.md
├── specialized-hardware.md
├── vram-estimation.md
└── benchmarks-evals.md
```

---

## Conteúdo por Arquivo

### 1. `transformer-architecture.md`
**Tópicos:** Self-attention (fórmula QKV completa), multi-head attention, positional encoding (sinusoidal, RoPE, ALiBi), FFN com SwiGLU, LayerNorm vs RMSNorm, decoder-only vs encoder-decoder vs encoder-only, escala de parâmetros.

**Fórmulas centrais:**
- Attention: `Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) * V`
- RoPE: rotação complexa por posição
- SwiGLU: `SwiGLU(x) = Swish(xW) ⊗ (xV)`

---

### 2. `tokenization.md`
**Tópicos:** BPE (algoritmo completo com pseudocódigo), WordPiece, SentencePiece/Unigram, tiktoken, vocabulário size vs latência vs custo, tokenização multilingual e fertility rates, impacto de tokenização ruim no raciocínio.

---

### 3. `embeddings.md`
**Tópicos:** Espaço vetorial semântico, métricas de similaridade (coseno, L2, dot product — quando usar cada uma), modelos de embedding (sentence-transformers, text-embedding-3-large, E5, BGE), anisotropia e colapso de representação, dimensionality reduction (PCA, UMAP, t-SNE), matryoshka embeddings.

---

### 4. `pretraining.md`
**Tópicos:** Next-token prediction (cross-entropy loss), data pipelines (deduplication com MinHash, quality filtering, Common Crawl), curriculum learning, scaling laws de Chinchilla (fórmula L = f(N, D)), compute-optimal training, chinchilla-optimal vs overtraining para inferência.

---

### 5. `fine-tuning-peft.md`
**Tópicos:** Full fine-tuning vs PEFT, LoRA (decomposição de posto baixo: `W' = W + BA` onde `B ∈ R^{d×r}`, `A ∈ R^{r×k}`), rank selection, alpha scaling, QLoRA (4-bit NF4 quantization + double quantization), merge de adapters, quando fine-tuning supera RAG e vice-versa.

---

### 6. `rlhf-alignment.md`
**Tópicos:** SFT → Reward Model → PPO pipeline (com equação de reward do PPO), DPO (Direct Preference Optimization — simplificação sem RM separado), Constitutional AI e RLAIF, problemas de reward hacking e Goodhart's Law, diferenças entre RLHF, DPO, ORPO, GRPO.

---

### 7. `kv-cache-attention.md`
**Tópicos:** Como o KV cache funciona (por que só K e V são cacheados), paged attention (vLLM — analogia com virtual memory), sliding window attention (Mistral), GQA (Grouped Query Attention) vs MQA vs MHA, Flash Attention (algoritmo IO-aware — tiles, HBM vs SRAM), impacto em VRAM por token.

---

### 8. `quantization.md`
**Tópicos:** Float32 → FP16 → BF16 → INT8 → INT4 (trade-offs de range e precisão), GPTQ (post-training quantization via second-order info), AWQ (activation-aware), GGUF/llama.cpp (Q4_K_M, Q8_0 etc.), perplexidade como métrica de qualidade, quantização por camada vs uniforme, outlier channels.

---

### 9. `inference-engines.md`
**Tópicos:** vLLM (paged attention + continuous batching), llama.cpp (CPU inference, GGUF), TensorRT-LLM (NVIDIA — kernel fusion, in-flight batching), Ollama (developer experience), comparativo de throughput tokens/seg, tensor parallelism vs pipeline parallelism, speculative decoding.

---

### 10. `gpu-architecture.md`
**Tópicos:** CUDA cores vs Tensor Cores (matrix multiply units), warp (32 threads SIMT), occupancy, VRAM HBM2e vs HBM3, memory bandwidth vs FLOPS (arithmetic intensity), hierarquia de memória (registros → L1 → L2 → HBM), comparativo A100/H100/RTX 4090/RTX 4080, NVLink e multi-GPU.

---

### 11. `specialized-hardware.md`
**Tópicos:** Google TPU v4/v5 (systolic arrays — como a matrix multiply é feita em hardware), Groq LPU (deterministic execution, zero runtime overhead), Cerebras WSE (wafer-scale engine — por que eliminar interchip latency importa), AWS Trainium/Inferentia 2, Apple Neural Engine (ANE), Tenstorrent.

---

### 12. `vram-estimation.md`
**Tópicos:** Fórmula de VRAM para inferência (`params × bytes_per_param + KV cache`), bytes por parâmetro por dtype (FP32=4, FP16=2, INT8=1, INT4=0.5), ativações e batch size, optimizer states para treinamento (Adam: 12 bytes/param), exemplos práticos completos:
- Llama 3 8B em FP16 → quantos GB?
- Llama 3 70B em Q4 → cabe em 2× RTX 4090?
- Fine-tuning Mistral 7B com QLoRA em 1× GPU 24GB?

---

### 13. `benchmarks-evals.md`
**Tópicos:** MMLU (57 tarefas, few-shot, metodologia de scoring), HumanEval (pass@k, por que é fácil de saturar), MATH (cadeia de raciocínio), LMSYS Chatbot Arena (Elo rating — cálculo, vieses, como a arena funciona), BIG-Bench Hard, como rodar evals locais com `lm-evaluation-harness`, LLM-as-judge (vieses conhecidos: verbosity bias, self-preference).

---

## Padrão Interno de Cada Arquivo

```yaml
---
tags: [ai-ml, fundamentals, <topic>]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [<alias1>, <alias2>]
---
```

### Seções (em ordem)

1. **Overview** — o que é, por que importa, contexto histórico breve
2. **Como Funciona** — matemática, fórmulas com notação LaTeX, diagramas mermaid
3. **Implementação Prática** — código Python funcional (PyTorch, HuggingFace, etc.)
4. **Comparativos** — tabelas quando há múltiplas variantes (ex: tipos de quantização)
5. **Gotchas** — callouts `> [!warning]` com armadilhas reais de produção
6. **Snippets** — blocos prontos para copiar e usar
7. **References** — papers originais (arxiv), docs oficiais
8. **Related** — wikilinks Obsidian para arquivos relacionados do vault

---

## Wikilinks Planejados

### Entre os novos arquivos

| De | Para |
|----|------|
| `transformer-architecture` | `kv-cache-attention`, `gpu-architecture`, `embeddings`, `tokenization` |
| `fine-tuning-peft` | `rlhf-alignment`, `vram-estimation`, `quantization`, `pretraining` |
| `inference-engines` | `quantization`, `gpu-architecture`, `vram-estimation`, `kv-cache-attention` |
| `pretraining` | `tokenization`, `benchmarks-evals`, `gpu-architecture` |
| `gpu-architecture` | `specialized-hardware`, `vram-estimation` |
| `quantization` | `vram-estimation`, `inference-engines` |

### Para arquivos existentes no vault

Todos os novos arquivos linkam para arquivos existentes relevantes:
- `[[rag-architecture]]` — embeddings, inference engines
- `[[prompt-engineering]]` — transformer architecture, tokenization
- `[[claude-api]]` — benchmarks, fine-tuning
- `[[vector-dbs]]` — embeddings
- `[[langchain]]` — inference engines, fine-tuning

---

## MOC a Atualizar

Após criação dos arquivos, atualizar `tech-vault/00-moc/ai-ml-moc.md` com seção "Fundamentos" listando os 13 novos arquivos.

---

## Critérios de Qualidade

- [ ] Frontmatter YAML válido em todos os arquivos
- [ ] Fórmulas matemáticas em LaTeX (compatível com Obsidian)
- [ ] Código Python funcional e testável
- [ ] Pelo menos 3 wikilinks por arquivo
- [ ] Callouts Obsidian usados (`> [!tip]`, `> [!warning]`, `> [!info]`)
- [ ] Papers originais citados nas references
- [ ] Conteúdo em Português BR, termos técnicos em inglês
- [ ] Mínimo ~600 linhas por arquivo (nível enciclopédico)
