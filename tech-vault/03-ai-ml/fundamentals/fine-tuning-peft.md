---
tags: [ai-ml, fundamentals, fine-tuning, lora, qlora, peft]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Fine-tuning, PEFT, LoRA, QLoRA, Parameter-Efficient Fine-Tuning]
---

# Fine-Tuning e PEFT: LoRA, QLoRA e Adaptação Eficiente

## Overview

Fine-tuning é o processo de continuar o treinamento de um modelo pré-treinado em dados específicos de um domínio ou tarefa. O objetivo é especializar o comportamento do modelo sem o custo de treinar do zero.

A primeira decisão arquitetural é: **fine-tuning é realmente necessário?** As alternativas principais são:

| Abordagem | Quando usar | Vantagens | Desvantagens |
|-----------|-------------|-----------|--------------|
| **Prompting** | Tarefas gerais, comportamento já no modelo | Zero custo, zero latência extra | Limitado pelo conhecimento base do modelo |
| **RAG** | Novo conhecimento factual, dados dinâmicos | Atualização fácil, citações | Latência de retrieval, custo por query |
| **Fine-tuning** | Estilo específico, comportamento novo, domínio fechado | Latência baixa, consistência | Custo upfront alto, requer dados |

Fine-tuning só se justifica quando você precisa de **comportamento ou formato de output** que não emerge de prompting e que não é simplesmente "novo conhecimento" (que RAG resolve melhor).

### Full Fine-Tuning vs PEFT

**Full fine-tuning** atualiza todos os parâmetros do modelo. Para um modelo de 7B parâmetros em BF16, só armazenar os pesos requer 14GB — mais os gradientes e estados do optimizer Adam (FP32), chega-se a ~60-80GB de VRAM. Além disso, qualquer erro nos dados de fine-tuning afeta permanentemente todos os pesos.

**PEFT (Parameter-Efficient Fine-Tuning)** é uma família de técnicas que congela a maioria dos parâmetros e treina apenas um subconjunto pequeno. LoRA é hoje o método PEFT dominante.

Relaciona-se com: [[rlhf-alignment]], [[vram-estimation]], [[quantization]], [[pretraining]], [[gpu-architecture]], [[rag-architecture]]

---

## LoRA — Low-Rank Adaptation

### A Álgebra Linear por Trás do LoRA

A intuição do LoRA (arxiv:2106.09685) parte de uma observação empírica: as atualizações de peso durante fine-tuning têm **posto intrínseco baixo** — elas residem em um subespaço de dimensão muito menor que a matriz completa.

Se as atualizações `ΔW` têm posto r << min(d,k), podemos decompô-las em um produto de duas matrizes menores:

```
W' = W + ΔW = W + BA
onde B ∈ ℝ^{d×r}, A ∈ ℝ^{r×k}, r << min(d,k)
```

Durante o treinamento:
- `W` (pesos originais) é **congelado** — seus gradientes não são computados
- Apenas `B` e `A` recebem gradientes e são otimizados
- No forward pass, a saída é: `h = Wx + BAx = Wx + ΔWx`

### Inicialização

A inicialização é crucial para estabilidade:
- `A ~ N(0, σ²)` — inicializada com distribuição normal (tipicamente `σ = 1/√r`)
- `B = 0` — inicializada com zeros

Esta escolha garante que `ΔW = BA = 0` no início do treinamento — o modelo começa idêntico ao modelo base, sem perturbação inicial. Se B fosse aleatória, o início do fine-tuning produziria saídas completamente diferentes do base model.

### Alpha Scaling

O LoRA introduz um hiperparâmetro `α` (alpha) que escala a magnitude da atualização:

```
ΔW_efetivo = (α/r) × BA
```

O fator `(α/r)` normaliza a magnitude da atualização independentemente do rank escolhido. Com `α = 2r`, a escala é constante de 2, independentemente se r=8, r=16 ou r=32.

Na prática, a convenção padrão é:
- Definir `α = r` para neutralidade (escala 1.0)
- Definir `α = 2r` para amplificar as atualizações ligeiramente
- Ajustar `α` como hiperparâmetro de aprendizado junto com o learning rate

### Redução de Parâmetros

A economia de parâmetros é substancial:

```
Parâmetros LoRA = r×d + r×k = r×(d+k)
Parâmetros full = d×k
Razão de redução = d×k / (r×(d+k))
```

**Exemplo concreto** para uma projeção de atenção (d = k = 4096) com r = 16:
- LoRA: 16 × (4096 + 4096) = **131,072 parâmetros**
- Full: 4096 × 4096 = **16,777,216 parâmetros**
- **Redução de 128x**

Para um modelo Llama 3 8B completo, aplicando LoRA em todas as projeções de atenção:
- Full fine-tuning: ~8B parâmetros treináveis
- LoRA r=16 em q/k/v/o projections: ~20M parâmetros treináveis (~0.25%)

---

## Guia de Seleção de Rank

A escolha do rank `r` é o principal hiperparâmetro do LoRA. O rank determina a "expressividade" da adaptação:

| Rank | Parâmetros (por layer 4096d) | Quando usar |
|------|------------------------------|-------------|
| **r=4** | ~32K | Adaptação mínima: apenas estilo e formato de output |
| **r=8** | ~65K | Fine-tuning geral — padrão recomendado para começar |
| **r=16** | ~131K | Domínio mais específico, terminologia especializada |
| **r=32** | ~262K | Tarefas de raciocínio complexo, domínio muito diferente |
| **r=64** | ~524K | Casos extremos; similar ao full fine-tuning em expressividade |
| **r=128+** | ~1M+ | Equivalente ao full fine-tuning em termos de expressividade |

> [!tip] Começar com r=8
> Para 90% dos casos, LoRA com r=8 em q_proj, k_proj, v_proj, o_proj e alpha=16 é suficiente. Só aumente o rank se o eval loss não convergir para o nível desejado. Uma estratégia eficaz: começar com r=8, avaliar no validation set após convergência. Se a loss platônica muito acima do target, dobrar o rank e retreinar. Cada duplicação do rank custa o dobro de VRAM e tempo de treino.

---

## Quais Layers Aplicar LoRA

Nem todas as layers precisam de LoRA. A seleção impacta tanto a qualidade quanto o custo:

**Attention projections (obrigatório):**
- `q_proj` — query projection: controla o que o modelo "procura"
- `k_proj` — key projection: controla o que o modelo "oferece como referência"
- `v_proj` — value projection: controla o que é extraído da atenção
- `o_proj` — output projection: transforma a saída da atenção multi-head

Estas quatro layers são suficientes para a maioria dos fine-tunings. Elas capturam os mecanismos de atenção que determinam quais tokens interagem.

**FFN layers (opcional, melhora para tarefas complexas):**
- `gate_proj` — controla o "portão" da SwiGLU activation
- `up_proj` — projeção de expansão da FFN
- `down_proj` — projeção de contração da FFN

Adicionar LoRA nas FFN layers aumenta os parâmetros treináveis em ~3x, mas melhora performance em tarefas que requerem conhecimento de domínio denso (medicina, direito, matemática).

**Embedding layers (raramente):**
- Apenas quando o vocabulário precisa ser extendido (ex: adicionar tokens de linguagem nova)
- Custo elevado: embeddings têm dimensão vocab_size × d_model (~32K × 4096 = 131M params)

---

## QLoRA: Quantização + LoRA

QLoRA (arxiv:2305.14314) combina quantização do modelo base com LoRA para reduzir dramaticamente os requisitos de VRAM:

### NF4 — Normal Float 4-bit

O modelo base é quantizado para NF4, um formato de 4 bits projetado especificamente para pesos de modelos de linguagem:

**Por que NF4 em vez de INT4 comum:**
- Os pesos de LLMs seguem aproximadamente uma distribuição normal N(0,1) após normalização
- NF4 distribui os 16 valores possíveis (2^4) de forma não-uniforme, concentrando mais valores próximos a zero onde a densidade de probabilidade é maior
- Isso minimiza o erro de quantização esperado para distribuições normais

Na prática: ~0.1 bits de erro a menos por parâmetro vs INT4 para pesos tipicamente distribuídos.

### Double Quantization

QLoRA aplica quantização em dois níveis:
1. **Primeiro nível**: pesos em blocos de 64, cada bloco com sua constante de quantização em FP32
2. **Segundo nível**: as próprias constantes de quantização são quantizadas para FP8

Economia adicional: ~0.37 bits por parâmetro. Para um modelo de 7B parâmetros: ~290MB economizados.

### Paged Optimizers

Durante fine-tuning, os estados do optimizer Adam (momentum + variance) são 2 tensores FP32 do tamanho dos parâmetros treináveis. Para LoRA com 20M parâmetros: 2 × 20M × 4 bytes = 160MB — gerenciável.

O problema ocorre com full fine-tuning ou LoRA de rank muito alto. Paged optimizers usam a memória unificada CUDA para "paginar" os estados do optimizer para a CPU RAM quando a VRAM está cheia, evitando OOM errors ao custo de latência ocasional.

### Resumo: VRAM para Llama 3 8B

| Configuração | VRAM aproximada |
|---|---|
| Full fine-tuning FP32 | ~120GB |
| Full fine-tuning BF16 | ~60GB |
| LoRA r=16 BF16 | ~20GB |
| QLoRA r=16 (NF4 base + BF16 adapters) | ~10GB |

> [!warning] Learning Rate Muito Alto
> Learning rate para fine-tuning deve ser 10-100x menor que para pre-training. Para LoRA: 1e-4 a 3e-4. Para full fine-tuning: 1e-5 a 5e-5. LR alto causa catastrophic forgetting ou divergência. Um sintoma comum: a training loss cai rapidamente mas o validation loss explode — sinal de catastrophic forgetting. Diminua o LR e recomece o treinamento.

---

## Fine-Tuning vs RAG: Tabela Comparativa

A decisão entre fine-tuning e RAG é frequentemente mal compreendida. A tabela abaixo organiza os critérios:

| Critério | Fine-tuning | RAG |
|----------|-------------|-----|
| Novo conhecimento factual | Difícil (memorização fraca) | Ideal |
| Estilo e formato de output | Ideal | Limitado |
| Latência de inferência | Menor (sem retrieval) | Maior |
| Atualização de dados | Requer re-treino | Troca de docs |
| Custo upfront | Alto (GPU) | Baixo |
| Custo por query | Menor | Maior (retrieve + gen) |
| Comportamento específico | Ideal | Limitado |
| Auditabilidade das fontes | Baixa | Alta (citações) |
| Volume de exemplos necessário | Alto (>1000) | Baixo |
| Dados confidenciais | Risco (ficam no modelo) | Controlado (docs isolados) |

**Regra prática:** Se a pergunta é "o modelo sabe X?", use RAG. Se a pergunta é "o modelo responde no formato/tom Y?", use fine-tuning. Em muitos casos de produção, ambos são combinados.

---

## Código Prático

### 1. SFT Completo com QLoRA

```python
# fine_tune_qlora.py
# Dependências: pip install transformers peft trl bitsandbytes datasets accelerate
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM

# ============================================================
# 1. Configuração da quantização NF4 (QLoRA)
# ============================================================
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                          # quantizar para 4-bit
    bnb_4bit_quant_type="nf4",                  # Normal Float 4
    bnb_4bit_compute_dtype=torch.bfloat16,      # compute em BF16 (mais estável que FP16)
    bnb_4bit_use_double_quant=True,             # double quantization (~0.37 bits/param extras)
)

# ============================================================
# 2. Carregar modelo base quantizado
# ============================================================
model_id = "meta-llama/Llama-3.2-3B"  # ~6GB VRAM com NF4

tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token  # Llama não tem pad token por padrão
tokenizer.padding_side = "right"           # padding à direita para SFT

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",                     # distribui automaticamente entre GPUs
    attn_implementation="flash_attention_2",  # mais rápido se disponível
)

# Necessário para QLoRA: prepara o modelo para treinamento com pesos quantizados
model.enable_input_require_grads()

# ============================================================
# 3. Configuração do LoRA
# ============================================================
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,                                   # rank — começar aqui
    lora_alpha=16,                         # alpha = 2*r é convenção comum
    lora_dropout=0.05,                     # regularização leve
    bias="none",                           # não treinar bias terms
    target_modules=[                       # layers onde aplicar LoRA
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        # Descomente para tarefas mais complexas:
        # "gate_proj",
        # "up_proj",
        # "down_proj",
    ],
)

model = get_peft_model(model, lora_config)

# ============================================================
# 4. Dataset — formato instrução/resposta
# ============================================================
def format_instruction(example: dict) -> str:
    """Formata um exemplo no template de instrução do Llama 3."""
    return (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"Você é um assistente útil.<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n"
        f"{example['instruction']}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n"
        f"{example['output']}<|eot_id|>"
    )

# Usar dataset público como exemplo
dataset = load_dataset("yahma/alpaca-cleaned", split="train")
dataset = dataset.map(
    lambda x: {"text": format_instruction(x)},
    remove_columns=dataset.column_names,
)

# Split treino/validação
dataset = dataset.train_test_split(test_size=0.05, seed=42)

# ============================================================
# 5. Training Arguments
# ============================================================
training_args = TrainingArguments(
    output_dir="./llama3-qlora-output",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=8,          # effective batch size = 4 * 8 = 32
    gradient_checkpointing=True,            # economiza VRAM de ativações
    gradient_checkpointing_kwargs={"use_reentrant": False},
    optim="paged_adamw_8bit",               # paged optimizer para QLoRA
    learning_rate=2e-4,                     # LR típico para LoRA
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    weight_decay=0.001,
    bf16=True,                              # compute em BF16
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=500,
    save_total_limit=3,                     # manter apenas 3 checkpoints
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    report_to="tensorboard",               # ou "wandb" se configurado
    dataloader_num_workers=4,
)

# ============================================================
# 6. SFT Trainer
# ============================================================
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=2048,
    packing=True,                           # empacota sequências curtas para eficiência
)

# Iniciar treinamento
trainer.train()

# Salvar adapter LoRA (apenas os pesos treináveis — pequeno!)
trainer.model.save_pretrained("./llama3-qlora-adapter")
tokenizer.save_pretrained("./llama3-qlora-adapter")
print("Adapter salvo em ./llama3-qlora-adapter")
```

### 2. Calcular Parâmetros Treináveis

```python
# Verificar parâmetros treináveis antes e depois de aplicar LoRA
def count_parameters(model) -> dict:
    """
    Conta parâmetros treináveis e totais.
    Retorna dict com detalhes.
    """
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    frozen_params = total_params - trainable_params
    
    return {
        "trainable": trainable_params,
        "total": total_params,
        "frozen": frozen_params,
        "trainable_pct": 100 * trainable_params / total_params,
        "trainable_formatted": f"{trainable_params/1e6:.2f}M",
        "total_formatted": f"{total_params/1e9:.2f}B",
    }

# Antes do LoRA (full fine-tuning hipotético):
from transformers import AutoModelForCausalLM
import torch

base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B",
    torch_dtype=torch.bfloat16,
)
before = count_parameters(base_model)
print(f"Antes do LoRA: {before['total_formatted']} params, todos treináveis")

# Depois do LoRA:
from peft import LoraConfig, get_peft_model, TaskType

lora_cfg = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)
peft_model = get_peft_model(base_model, lora_cfg)
after = count_parameters(peft_model)

print(f"\nDepois do LoRA (r=8):")
print(f"  Treináveis: {after['trainable_formatted']} ({after['trainable_pct']:.2f}%)")
print(f"  Congelados: {after['frozen']/1e9:.2f}B")
print(f"  Total: {after['total_formatted']}")
print(f"\n  Redução de {before['trainable'] / after['trainable']:.0f}x nos parâmetros treináveis")
```

### 3. Merge de Adapter e Salvar Modelo Completo

```python
# merge_adapter.py — combinar base model + adapter em modelo único
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL_ID = "meta-llama/Llama-3.2-3B"
ADAPTER_PATH = "./llama3-qlora-adapter"
OUTPUT_PATH = "./llama3-finetuned-merged"

print("Carregando base model em BF16...")
# IMPORTANTE: carregar sem quantização para o merge
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="cpu",                  # merge na CPU para evitar OOM
)

print("Carregando adapter LoRA...")
peft_model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)

print("Fazendo merge dos pesos...")
# Merge matemático: W_merged = W_base + (alpha/rank) * B @ A
merged_model = peft_model.merge_and_unload()

print(f"Salvando modelo merged em {OUTPUT_PATH}...")
merged_model.save_pretrained(OUTPUT_PATH, safe_serialization=True)

tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)
tokenizer.save_pretrained(OUTPUT_PATH)

print(f"Modelo merged salvo! Pronto para serving sem overhead do adapter.")

# Verificar que o modelo merged funciona corretamente
from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model=OUTPUT_PATH,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
result = pipe("Olá, como você pode me ajudar?", max_new_tokens=100)
print(result[0]["generated_text"])
```

### 4. Verificar Layers com LoRA Aplicado

```python
# Inspecionar quais layers têm LoRA
from peft import PeftModel
from transformers import AutoModelForCausalLM
import torch

def inspect_lora_layers(model: PeftModel) -> None:
    """
    Lista todas as layers com LoRA e seus parâmetros.
    """
    print("=== Layers com LoRA ===\n")
    lora_layers = {}
    
    for name, module in model.named_modules():
        if hasattr(module, 'lora_A') and hasattr(module, 'lora_B'):
            lora_a_size = module.lora_A['default'].weight.shape
            lora_b_size = module.lora_B['default'].weight.shape
            params = (lora_a_size[0] * lora_a_size[1]) + (lora_b_size[0] * lora_b_size[1])
            lora_layers[name] = {
                "A_shape": lora_a_size,
                "B_shape": lora_b_size,
                "params": params,
                "rank": lora_a_size[0],
                "alpha": getattr(module, 'scaling', {}).get('default', 'N/A'),
            }
            print(f"  {name}")
            print(f"    A: {lora_a_size}, B: {lora_b_size}")
            print(f"    Rank: {lora_a_size[0]}, Params: {params:,}")
    
    total_lora_params = sum(v['params'] for v in lora_layers.values())
    print(f"\nTotal de layers com LoRA: {len(lora_layers)}")
    print(f"Total de parâmetros LoRA: {total_lora_params:,} ({total_lora_params/1e6:.2f}M)")

# Uso:
# inspect_lora_layers(peft_model)
```

---

## Callouts de Atenção

> [!warning] Overfitting Rápido
> Com menos de 1000 exemplos, overfitting ocorre em poucos epochs. Use eval loss para early stopping e datasets com diversidade suficiente. Regra de bolso: mínimo 1000 exemplos por "comportamento" que deseja ensinar. Sinais de overfitting: training loss cai mas validation loss sobe, o modelo começa a repetir exatamente os exemplos de treino em vez de generalizar. Solução: reduzir epochs, aumentar dropout no LoRA, ou coletar mais dados.

> [!warning] Contamination Permanente
> Os dados de fine-tuning ficam incorporados no modelo permanentemente. Dados incorretos, enviesados ou com informações confidenciais não podem ser "removidos" sem re-treinar. Este é um risco de compliance importante: se dados de clientes ou informações proprietárias são incluídos no fine-tuning, eles podem ser extraídos por adversários via prompt injection ou membership inference attacks. Sempre anonimize dados antes de fine-tuning.

> [!info] Merge Para Serving
> Em produção, sempre faça merge do adapter antes de servir. Adapters separados têm overhead de computação (~20% mais lento) e complicam o serving pipeline (precisa carregar base model + adapter). Após merge, o modelo é um arquivo de pesos único, sem dependência do adapter ou da biblioteca PEFT. Frameworks como vLLM, TGI e Ollama trabalham melhor com modelos merged.

---

## Dataset de Fine-Tuning: Qualidade > Quantidade

A qualidade dos dados de fine-tuning impacta o resultado mais do que a quantidade. Diretrizes práticas:

**Formato de instrução (recomendado para SFT):**
```json
{
  "instruction": "Resuma o seguinte texto em português em no máximo 3 frases.",
  "input": "A inteligência artificial generativa...",
  "output": "A IA generativa é uma subcategoria..."
}
```

**Critérios de qualidade:**
1. **Diversidade**: variação em comprimento, estilo, complexidade e tópico
2. **Clareza**: a instrução deve ser inequívoca
3. **Consistência**: o output deve ser o que você quer que o modelo produza — não simplesmente "correto"
4. **Balance**: não dominar com um único tipo de tarefa (evita esquecimento das outras)

**Anti-padrões comuns:**
- Incluir respostas "Não sei" ou "Como IA, não posso..." quando você quer respostas completas
- Dados gerados por GPT-4 sem revisão humana (model collapse risk)
- Inconsistência de formato entre exemplos (alguns com markdown, outros sem)
- Respostas muito curtas para perguntas complexas (modelo aprende a ser superficial)

> [!warning] Learning Rate Muito Alto
> Learning rate para fine-tuning deve ser 10-100x menor que para pre-training. Para LoRA: 1e-4 a 3e-4. Para full fine-tuning: 1e-5 a 5e-5. LR alto causa catastrophic forgetting ou divergência. Outra armadilha: usar o mesmo scheduler de pre-training (linear warmup + linear decay) para fine-tuning. Para fine-tuning, cosine scheduler com warmup de 3% funciona melhor empiricamente.

---

## Hiperparâmetros: Referência Rápida

| Hiperparâmetro | Valor padrão | Range razoável | Notas |
|---|---|---|---|
| `r` (rank) | 8 | 4–128 | Começar com 8, dobrar se necessário |
| `lora_alpha` | 16 | r a 2r | alpha/r define a escala efetiva |
| `lora_dropout` | 0.05 | 0.0–0.1 | Mais dropout com poucos dados |
| `learning_rate` | 2e-4 | 1e-4 a 5e-4 | Para LoRA; 10x menor para full FT |
| `num_epochs` | 2–3 | 1–5 | Mais que 3 tende ao overfitting |
| `batch_size` | 16–32 | 8–64 | Efetivo = per_device × grad_accum × n_gpus |
| `warmup_ratio` | 0.03 | 0.01–0.1 | 3% do total de steps |
| `max_seq_length` | 2048 | 512–8192 | Limitar ao necessário para economizar VRAM |

---

## References

- [LoRA: Low-Rank Adaptation of Large Language Models (Hu et al., 2021)](https://arxiv.org/abs/2106.09685)
- [QLoRA: Efficient Finetuning of Quantized LLMs (Dettmers et al., 2023)](https://arxiv.org/abs/2305.14314)
- [LLaMA: Open and Efficient Foundation Language Models (Touvron et al., 2023)](https://arxiv.org/abs/2302.13971)
- [Stanford Alpaca: An Instruction-following LLaMA Model](https://github.com/tatsu-lab/stanford_alpaca)
- [Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90% ChatGPT Quality](https://lmsys.org/blog/2023-03-30-vicuna/)
- [PEFT Library (HuggingFace)](https://github.com/huggingface/peft)
- [TRL Library: Transformer Reinforcement Learning (HuggingFace)](https://github.com/huggingface/trl)

---

## Avaliação Pós Fine-Tuning

Fine-tuning sem avaliação rigorosa é perigoso — o modelo pode parecer melhor na tarefa alvo mas ter regredido em capacidades gerais. A avaliação deve cobrir dois eixos:

**Avaliação na tarefa alvo:**
- Hold-out set do mesmo domínio que os dados de fine-tuning (nunca visto durante treino)
- Métricas específicas da tarefa: ROUGE para sumarização, BLEU para tradução, exact match para QA, pass@k para código
- LLM-as-judge: usar um modelo maior (GPT-4, Claude 3.5) para avaliar qualidade da resposta em escala

**Avaliação de regressão (benchmarks gerais):**
- MMLU: conhecimento geral — fine-tuning agressivo pode reduzir scores
- HellaSwag: senso comum — checar manutenção
- HumanEval ou MBPP: capacidade de código — especialmente relevante se o fine-tuning não foi em código
- MT-Bench: qualidade de conversação multi-turn

```python
# Calcular win rate para avaliar alignment/fine-tuning vs modelo base
from anthropic import Anthropic
import json

client = Anthropic()

def llm_judge_comparison(
    prompt: str,
    response_a: str,
    response_b: str,
    model: str = "claude-opus-4-5",
) -> str:
    """
    Usa LLM como juiz para comparar duas respostas.
    Retorna 'A', 'B' ou 'tie'.
    """
    judge_prompt = f"""Você é um avaliador imparcial. Compare as duas respostas abaixo para o mesmo prompt.

PROMPT DO USUÁRIO:
{prompt}

RESPOSTA A:
{response_a}

RESPOSTA B:
{response_b}

Avalie qual resposta é melhor em termos de: precisão, completude, clareza e utilidade.
Responda com exatamente um dos seguintes: "A", "B" ou "tie"."""

    response = client.messages.create(
        model=model,
        max_tokens=10,
        temperature=0.0,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    verdict = response.content[0].text.strip().upper()
    return verdict if verdict in ("A", "B", "TIE") else "tie"


def compute_win_rate(
    prompts: list[str],
    responses_model_a: list[str],
    responses_model_b: list[str],
) -> dict:
    """
    Computa win rate entre dois modelos usando LLM-as-judge.
    model_a = modelo fine-tunado, model_b = baseline
    """
    results = {"A": 0, "B": 0, "TIE": 0}
    
    for prompt, resp_a, resp_b in zip(prompts, responses_model_a, responses_model_b):
        verdict = llm_judge_comparison(prompt, resp_a, resp_b)
        results[verdict] += 1
    
    total = len(prompts)
    return {
        "win_rate_a": results["A"] / total,
        "win_rate_b": results["B"] / total,
        "tie_rate": results["TIE"] / total,
        "raw_counts": results,
    }
```

---

## Related

- [[rlhf-alignment]] — próximo passo após SFT: alinhar comportamento com preferências
- [[vram-estimation]] — calcular VRAM necessária para fine-tuning e inferência
- [[quantization]] — técnicas de quantização usadas no QLoRA (NF4, INT8, GPTQ)
- [[pretraining]] — etapa anterior: como o modelo base foi criado
- [[gpu-architecture]] — hardware subjacente e limitações de memória
- [[rag-architecture]] — alternativa ao fine-tuning para novo conhecimento factual
