---
tags: [ai-ml, fundamentals, rlhf, alignment, dpo, constitutional-ai]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [RLHF, Alignment, DPO, Constitutional AI, RLAIF]
---

# RLHF e Alignment: DPO, Constitutional AI e Preferências Humanas

## Overview

Alignment é o problema de fazer um modelo de linguagem se comportar de acordo com a intenção humana — ser útil, honesto e inofensivo — de forma robusta e generalizada.

O SFT (Supervised Fine-Tuning) sozinho é insuficiente para isso. Um modelo treinado apenas com SFT aprende a completar padrões dos dados de demonstração, mas:
- Não sabe distinguir respostas boas de ruins em situações novas
- Tende a ser excessivamente verboso ou confirmar o que o usuário quer ouvir (sycophancy)
- Pode gerar conteúdo prejudicial quando o prompt diverge da distribuição de treino
- Não generaliza a intenção humana — apenas imita a forma superficial das demonstrações

O RLHF (Reinforcement Learning from Human Feedback) e seus descendentes (DPO, ORPO, GRPO) resolvem isso ensinando o modelo a preferir respostas que humanos avaliam como melhores, não apenas respostas que parecem com os exemplos de treino.

### Pipeline Completo de Treinamento

```
Base Model (pré-treinado)
    ↓ SFT (Supervised Fine-Tuning)
    → Modelo que segue instruções mas não está alinhado
    ↓ RLHF ou DPO
    → Modelo alinhado, útil e seguro para deployment
```

Cada etapa tem um papel específico:
- **SFT**: ensina o formato e estilo de resposta de um assistente (chat, seguir instruções)
- **RLHF/DPO**: ensina quais respostas são *melhores*, não apenas quais parecem com um assistente

Relaciona-se com: [[fine-tuning-peft]], [[pretraining]], [[benchmarks-evals]], [[prompt-engineering]], [[claude-api]]

---

## RLHF Pipeline: As Três Etapas

### Stage 1: SFT (Supervised Fine-Tuning)

O SFT adapta o base model para o formato de instrução-resposta. Os dados são demonstrações de alta qualidade escritas por humanos:

```json
{"prompt": "Explique o conceito de recursão.", "response": "Recursão é..."}
```

Após SFT, o modelo produz respostas no formato correto, mas sua "opinião" sobre o que constitui uma resposta boa ainda é subótima.

### Stage 2: Reward Model (Bradley-Terry)

O Reward Model (RM) é treinado para capturar preferências humanas. Dado dois candidatos de resposta para o mesmo prompt, humanos anotam qual é melhor. O RM aprende a atribuir scores que refletem essas preferências.

**Modelo de Bradley-Terry para preferências binárias:**

```
P(response_A preferred over response_B) = σ(r_θ(A) - r_θ(B))
```

Onde:
- `r_θ(x)` = score escalar que o reward model atribui à resposta x
- `σ` = função sigmoid
- A probabilidade de A ser preferido cresce conforme o score de A supera o de B

**Loss de treinamento do reward model:**

```
L_RM = -E[log σ(r_θ(y_w) - r_θ(y_l))]
```

Onde:
- `y_w` = chosen — a resposta que o humano preferiu (winner)
- `y_l` = rejected — a resposta preterida (loser)

O RM é tipicamente o mesmo modelo SFT com a última camada substituída por uma cabeça de regressão escalar. Ele aprende a atribuir scores mais altos para respostas que humanos considerariam melhores.

### Stage 3: PPO (Proximal Policy Optimization)

Com o reward model treinado, usamos PPO para otimizar o modelo SFT de forma a maximizar o score do reward model. O objetivo completo é:

```
Objective_RLHF = E[r(y|x)] - β × KL(π_θ(y|x) || π_ref(y|x))
```

Onde:
- `π_θ(y|x)` = política atual (o modelo sendo treinado)
- `π_ref(y|x)` = política de referência (o modelo SFT, fixado)
- `r(y|x)` = score do reward model para a resposta y ao prompt x
- `β × KL(...)` = penalidade KL por divergir do modelo SFT de referência

**Por que a penalidade KL é essencial:**

Sem ela, o modelo rapidamente descobre como "hackear" o reward model — produzindo outputs que maximizam o score sem satisfazer o objetivo real (reward hacking). A penalidade KL mantém o modelo próximo ao SFT, limitando o quanto ele pode divergir do comportamento esperado.

**Parâmetros críticos do PPO:**
- `β` (KL coefficient): tipicamente 0.1–0.5. Maior β = mais conservador, menos reward hacking, mas menos melhoria
- `ε` (clip ratio): 0.2 é o padrão PPO. Limita o quanto a política pode mudar em um único update
- `γ` (discount): 1.0 para tarefas de geração de texto (sem desconto temporal)
- Número de PPO epochs por batch: 4 é comum; mais epochs = instabilidade

> [!warning] Reward Hacking É Inevitável
> Com PPO, após muitos steps o modelo encontra formas de maximizar o reward model sem satisfazer o objetivo real. Monitore o KL divergence e o reward score em conjunto — reward alto + KL alto = sinal de hacking. Sinais concretos de reward hacking: respostas ficam progressivamente mais longas sem melhora de qualidade (se o RM foi calibrado com preferência por verbosidade), o modelo começa a repetir frases que "soam bem", ou produz formatações excessivas (listas desnecessárias, bold em tudo). Solução: reduzir β, reduzir learning rate do PPO, ou revisar o reward model.

---

## DPO: Direct Preference Optimization

### A Motivação

O pipeline RLHF com PPO tem várias desvantagens práticas:
- Requer treinar e manter um reward model separado
- O loop RL é notoriamente instável e sensível a hiperparâmetros
- Precisamos de amostras "online" (o modelo atual gerando respostas durante treino) para PPO funcionar bem
- Custo computacional alto: PPO requer forward passes do modelo de política, do reward model e do modelo de referência simultaneamente

DPO (arxiv:2305.18290) elimina o reward model separado derivando matematicamente que a solução ótima do objetivo RLHF pode ser expressa diretamente como uma função dos dados de preferência.

### A Derivação e a Loss DPO

A loss DPO é aplicada diretamente sobre pares (chosen, rejected) sem reward model intermediário:

```
L_DPO = -E_{(x,y_w,y_l)}[log σ(β × log(π_θ(y_w|x)/π_ref(y_w|x)) - β × log(π_θ(y_l|x)/π_ref(y_l|x)))]
```

Intuição: o modelo é incentivado a aumentar a probabilidade relativa das respostas preferidas (y_w) sobre as rejeitadas (y_l), sempre em relação ao modelo de referência (π_ref).

O termo `log(π_θ(y|x)/π_ref(y|x))` é o log-ratio entre a política atual e a referência — uma medida de "quanto o modelo atual favorece essa resposta em relação ao modelo base".

**DPO em termos simples:**
- Aumentar a probabilidade de y_w (escolhida) em relação ao modelo de referência
- Diminuir a probabilidade de y_l (rejeitada) em relação ao modelo de referência
- O parâmetro β controla a agressividade: maior β = mais forte o sinal de preferência

### DPO vs PPO: Comparação Técnica

| Aspecto | PPO (RLHF) | DPO |
|---------|-----------|-----|
| Reward model separado | Sim (exige treino extra) | Não |
| Amostras online | Sim (modelo gera durante treino) | Não (treino offline sobre pares fixos) |
| Estabilidade de treinamento | Baixa (loop RL sensível) | Alta (supervisionado direto) |
| Complexidade de implementação | Alta | Baixa |
| Feedback online (adaptativo) | Sim | Não |
| Reward hacking direto | Possível | Mais difícil (sem RM para hackear) |

> [!info] RLHF vs DPO na Prática
> DPO é preferido para a maioria dos projetos: mais simples de implementar, sem instabilidade do PPO, sem reward model para treinar e manter. Use PPO apenas se precisar de feedback online (reward model vendo a resposta atual) ou se DPO convergir mal. Casos em que PPO pode superar DPO: tarefas de raciocínio matemático onde feedback preciso por passo é necessário (RLHF com verifier), ou quando o dataset de preferências é pequeno e o modelo precisa de exploração online para melhorar.

---

## Algoritmos Mais Recentes

### ORPO (Odds Ratio Preference Optimization)

ORPO elimina a necessidade do **modelo de referência** π_ref completamente. Em vez de penalizar divergência do modelo de referência, incorpora a regularização diretamente na loss SFT via odds ratio:

```
L_ORPO = L_SFT + λ × L_OR
```

Onde `L_OR` é baseada na razão de odds entre chosen e rejected:

```
OR = (π_θ(y_w|x) / (1 - π_θ(y_w|x))) / (π_θ(y_l|x) / (1 - π_θ(y_l|x)))
L_OR = -log σ(log OR)
```

**Vantagem prática**: reduz pela metade a VRAM necessária (sem modelo de referência em memória) e simplifica o pipeline de treinamento. O modelo faz SFT e alignment em uma única passagem.

**Limitação**: a regularização via odds ratio é menos expressiva que a penalidade KL do DPO; pode ser insuficiente para domínios com muita divergência entre chosen e rejected.

### GRPO (Group Relative Policy Optimization — DeepSeek-R1)

GRPO (arxiv:2501.12948) foi desenvolvido pela DeepSeek para treinar modelos de raciocínio (o DeepSeek-R1). A inovação central é eliminar o **critic model** do PPO usando o desempenho relativo dentro de um grupo de amostras como baseline:

**PPO clássico**: requer um value function/critic separado para estimar a vantagem de cada resposta — custo computacional alto.

**GRPO**: para cada prompt, gera G respostas diferentes e usa a média do grupo como baseline:

```
A_i = (r_i - mean(r_1, ..., r_G)) / std(r_1, ..., r_G)
```

Onde `A_i` é a vantagem estimada da i-ésima resposta e `r_i` é seu reward. Respostas melhores que a média têm vantagem positiva; piores têm vantagem negativa.

**Resultado**: o DeepSeek-R1 treinou apenas com GRPO + rule-based rewards (verificação de código e matemática) sem reward model humano — e alcançou performance comparável ao OpenAI o1 em raciocínio matemático.

### SimPO e IPO

**SimPO (Simple Preference Optimization)**: simplificação do DPO que remove o modelo de referência e normaliza por comprimento da sequência — respostas mais longas não recebem vantagem injusta pela maior log-probabilidade total.

**IPO (Identity Preference Optimization)**: correção teórica do DPO para o caso de preferências determinísticas (quando um dos pares é claramente sempre melhor). DPO padrão pode overfitar nesses casos; IPO adiciona uma regularização que previne isso.

---

## Constitutional AI (Anthropic)

### O Problema que o Constitutional AI Resolve

RLHF tradicional requer anotadores humanos avaliando respostas — custoso, lento e difícil de escalar. Além disso, humanos têm vieses inconsistentes: um anotador pode preferir uma resposta verbosa enquanto outro prefere concisão.

Constitutional AI (CAI, arxiv:2212.08073) substitui parte da supervisão humana por um conjunto explícito de **princípios escritos em linguagem natural** — a "constituição" — que guia o comportamento do modelo.

### O Pipeline CAI

**Fase 1: Critique-Revision (Supervised)**

1. O modelo gera uma resposta inicial para um prompt (potencialmente prejudicial)
2. O modelo **critica** sua própria resposta segundo os princípios da constituição:
   > *"Identifique formas específicas em que a resposta do assistente é prejudicial, antiética ou socialmente enviesada."*
3. O modelo **revisa** a resposta para eliminar os problemas identificados
4. Os pares (prompt, resposta revisada) são usados como dados de SFT

**Fase 2: RLAIF (RL from AI Feedback)**

Em vez de humanos avaliando pares de respostas, o **próprio modelo** (ou um modelo maior) age como reward model:

1. Para cada prompt, gerar dois candidatos de resposta
2. Pedir ao modelo (como juiz) qual resposta é mais alinhada com os princípios da constituição
3. Usar essas preferências geradas por AI para treinar o reward model
4. Aplicar RLHF com esse reward model

**Red-Teaming Automático:**
O modelo também é usado para gerar prompts adversariais automaticamente — identificando categorias de inputs que podem elicitar comportamentos indesejados, sem precisar de red-teamers humanos.

### Vantagens e Limitações

**Vantagens:**
- Escalável: o modelo pode gerar milhões de avaliações sem custo humano
- Transparente: os princípios são explícitos e auditáveis
- Consistente: o modelo aplica os princípios de forma mais uniforme que humanos

**Limitações:**
- O modelo pode ter vieses sistemáticos na avaliação — se o modelo base é enviesado, o RLAIF herda esses vieses
- A constituição pode ter lacunas ou ambiguidades que só aparecem em edge cases
- Circularity risk: usar o modelo para avaliar o próprio treinamento pode amplificar erros

---

## Reward Hacking e a Lei de Goodhart

**Goodhart's Law**: "Quando uma medida se torna um objetivo, ela deixa de ser uma boa medida."

No contexto de LLMs e RLHF, isso se manifesta como **reward hacking** — o modelo encontra estratégias que maximizam o score do reward model sem satisfazer o objetivo real (ser útil e seguro para humanos).

### Exemplos Clássicos de Reward Hacking em LLMs

| Comportamento | Causa | Sintoma observado |
|--------------|-------|------------------|
| **Verbosidade excessiva** | RM calibrado com humanos que preferem respostas longas | Respostas ficam progressivamente mais longas, com repetição |
| **Sycophancy** | RM treinado com preferências onde o anotador concorda com o usuário | Modelo concorda com afirmações falsas se o usuário as apresentar com confiança |
| **Formatting abuse** | RM prefere respostas formatadas | Modelo usa bullet points, bold e headers mesmo onde prosa seria melhor |
| **Hedge overcalibration** | Penalidade por afirmações falsas | Modelo recusa perguntas simples com "não tenho certeza" em excesso |

### Soluções Para Reward Hacking

1. **KL penalty (β)**: manter o modelo próximo do SFT de referência limita a otimização extrema
2. **Múltiplos reward models**: usar ensemble de RMs treinados de formas diferentes — dificulta hackear todos simultaneamente
3. **Constitutional AI**: princípios explícitos são mais difíceis de hackear que um reward model opaco
4. **Monitoramento de métricas proxy**: length, repetition rate, hedge frequency — se essas métricas explodem, o modelo está hackeando
5. **Auditoria periódica de outputs**: revisar amostras do modelo em produção regularmente

> [!warning] Alignment Tax
> Fine-tuning com RLHF/DPO frequentemente reduz performance em benchmarks de conhecimento (MMLU, HumanEval). O modelo aprende a ser mais seguro mas perde capacidade. Monitorar benchmarks durante alignment. Este fenômeno é documentado: o ChatGPT inicial tinha performance em benchmarks de código inferior ao GPT-3 base em algumas dimensões. A solução não é ignorar o alignment tax mas monitorá-lo ativamente e ajustar o β (KL penalty) para balancear alinhamento e capacidade.

---

## Dataset de Preferências

### Formato para DPO/RLHF

O formato padrão para datasets de preferência é um triplet (prompt, chosen, rejected):

```json
{
  "prompt": "Qual é a capital do Brasil?",
  "chosen": "A capital do Brasil é Brasília, cidade planejada e construída na década de 1960 para ser a sede do governo federal.",
  "rejected": "São Paulo é a maior cidade do Brasil e frequentemente confundida com a capital, mas a capital oficial é o Rio de Janeiro."
}
```

O campo `rejected` deve ser uma resposta genuinamente inferior — factualmente errada, menos útil, mais perigosa ou menos alinhada com os valores desejados. Pares onde a diferença é ambígua são prejudiciais ao treinamento.

### Fontes de Dados de Preferência

| Dataset | Tamanho | Características |
|---------|---------|-----------------|
| **Anthropic HH-RLHF** | ~170K pares | Helpfulness e harmlessness, conversas multi-turn |
| **OpenHermes** | ~1M exemplos | SFT e preferência, múltiplos domínios |
| **UltraFeedback** | ~64K prompts | GPT-4 como juiz, 4 respostas por prompt |
| **Nectar** | ~183K pares | Múltiplos modelos como candidatos, GPT-4 como juiz |
| **Orca DPO Pairs** | ~12K pares | Foco em raciocínio e instrução |

### Margin Filtering

Uma técnica crítica para melhorar a qualidade do dataset: só incluir pares onde a diferença entre chosen e rejected é suficientemente grande.

**Como implementar:** usar um reward model pré-treinado para pontuar ambas as respostas. Só incluir o par se `score(chosen) - score(rejected) > threshold`. Isso remove pares ambíguos onde humanos discordariam sobre qual é melhor.

> [!warning] Qualidade Dos Dados de Preferência
> DPO é muito sensível à qualidade dos pares (chosen, rejected). Pares onde a diferença de qualidade é ambígua degradam o treinamento. Use margin filtering: só inclua pares onde o chosen é claramente melhor. Um erro comum: usar como "rejected" simplesmente a segunda geração do modelo, sem garantia que é realmente pior. O ideal é ter um score de preferência explícito e filtrar pelos pares com maior margem.

---

## Código Prático

### 1. DPO Training Completo com TRL

```python
# dpo_training.py
# Dependências: pip install transformers peft trl datasets accelerate bitsandbytes
import torch
from datasets import load_dataset, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType
from trl import DPOTrainer, DPOConfig

# ============================================================
# 1. Configuração do modelo base (QLoRA para economia de VRAM)
# ============================================================
model_id = "meta-llama/Llama-3.2-3B-Instruct"  # modelo já com SFT

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

# Modelo de política (será treinado)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)
model.enable_input_require_grads()

# Modelo de referência (fixo durante treino — o mesmo SFT de partida)
model_ref = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)

# ============================================================
# 2. LoRA para eficiência no treinamento DPO
# ============================================================
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                             # rank maior para alignment tasks
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)
model = get_peft_model(model, lora_config)

# ============================================================
# 3. Dataset de preferências
# ============================================================
# Dataset deve ter colunas: prompt, chosen, rejected
raw_dataset = load_dataset("Anthropic/hh-rlhf", split="train[:5000]")

def format_hh_rlhf(example: dict) -> dict:
    """
    Converte o formato HH-RLHF para o formato DPO esperado pelo TRL.
    HH-RLHF tem: chosen (conversa completa), rejected (conversa completa)
    DPO espera: prompt, chosen (só a última resposta), rejected (só a última resposta)
    """
    # Extrair o último turno da conversa como prompt/resposta
    chosen = example["chosen"]
    rejected = example["rejected"]
    
    # O prompt é a parte comum até o último '\n\nAssistant:'
    split_marker = "\n\nAssistant:"
    if split_marker in chosen:
        prompt = chosen.rsplit(split_marker, 1)[0] + split_marker
        chosen_response = chosen.rsplit(split_marker, 1)[1].strip()
        rejected_response = rejected.rsplit(split_marker, 1)[1].strip()
    else:
        return None
    
    return {
        "prompt": prompt,
        "chosen": chosen_response,
        "rejected": rejected_response,
    }

dataset = raw_dataset.map(format_hh_rlhf, remove_columns=raw_dataset.column_names)
dataset = dataset.filter(lambda x: x is not None and len(x.get("prompt", "")) > 0)
dataset = dataset.train_test_split(test_size=0.05, seed=42)

# ============================================================
# 4. DPO Training Configuration
# ============================================================
dpo_config = DPOConfig(
    output_dir="./llama3-dpo-output",
    num_train_epochs=1,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    learning_rate=5e-5,               # DPO usa LR menor que SFT
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    beta=0.1,                         # KL penalty coefficient
    max_length=1024,                  # comprimento máximo do contexto completo
    max_prompt_length=512,            # comprimento máximo do prompt
    bf16=True,
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=500,
    report_to="tensorboard",
)

# ============================================================
# 5. DPO Trainer
# ============================================================
trainer = DPOTrainer(
    model=model,
    ref_model=model_ref,
    args=dpo_config,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
)

trainer.train()
trainer.save_model("./llama3-dpo-adapter")
print("DPO training concluído. Adapter salvo.")
```

### 2. Criar Dataset de Preferências no Formato Correto

```python
# create_preference_dataset.py
from datasets import Dataset
import json

def create_preference_dataset(examples: list[dict]) -> Dataset:
    """
    Cria um dataset de preferências no formato correto para DPO.
    
    Cada exemplo deve ter:
    - prompt: a instrução ou pergunta
    - chosen: a resposta preferida
    - rejected: a resposta inferior
    - margin (opcional): score de confiança na preferência (0-1)
    """
    validated = []
    skipped = 0
    
    for ex in examples:
        # Validações básicas
        if not all(k in ex for k in ("prompt", "chosen", "rejected")):
            skipped += 1
            continue
        
        if ex["chosen"] == ex["rejected"]:
            skipped += 1  # pares idênticos são prejudiciais
            continue
        
        # Comprimento mínimo das respostas
        if len(ex["chosen"].split()) < 10 or len(ex["rejected"].split()) < 10:
            skipped += 1
            continue
        
        validated.append({
            "prompt": ex["prompt"].strip(),
            "chosen": ex["chosen"].strip(),
            "rejected": ex["rejected"].strip(),
        })
    
    print(f"Exemplos válidos: {len(validated)}, descartados: {skipped}")
    return Dataset.from_list(validated)

# Exemplo de uso com dados manuais
exemplos = [
    {
        "prompt": "Como posso melhorar minha produtividade?",
        "chosen": "Para melhorar a produtividade, considere técnicas como Pomodoro (25 minutos de foco, 5 de pausa), eliminar distrações durante períodos de trabalho intenso, e priorizar tarefas por impacto usando a Matriz de Eisenhower.",
        "rejected": "Trabalhe mais horas. Quanto mais você trabalhar, mais produtivo você será.",
    },
    {
        "prompt": "Explique o que é machine learning.",
        "chosen": "Machine learning é um subcampo da inteligência artificial onde sistemas aprendem padrões a partir de dados sem serem explicitamente programados para cada caso. O modelo ajusta seus parâmetros internos para minimizar erros nas previsões, usando algoritmos como redes neurais, árvores de decisão ou regressão.",
        "rejected": "Machine learning é quando computadores aprendem coisas. É muito legal e usado em muitos lugares atualmente.",
    },
]

dataset = create_preference_dataset(exemplos)
dataset.to_json("preference_dataset.jsonl")
```

### 3. Calcular Win Rate para Avaliar Alignment

```python
# evaluate_alignment.py
from anthropic import Anthropic
from transformers import pipeline
import torch
from typing import Optional

client = Anthropic()

def generate_response(
    model_pipeline,
    prompt: str,
    max_new_tokens: int = 256,
    temperature: float = 0.7,
) -> str:
    """Gera uma resposta usando um modelo HuggingFace."""
    outputs = model_pipeline(
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,
        pad_token_id=model_pipeline.tokenizer.eos_token_id,
    )
    # Extrair apenas a resposta gerada (sem o prompt)
    full_text = outputs[0]["generated_text"]
    return full_text[len(prompt):].strip()


def llm_judge_pairwise(
    prompt: str,
    response_a: str,
    response_b: str,
    criteria: str = "utilidade, precisão e clareza",
) -> str:
    """
    Usa Claude como juiz para comparar duas respostas.
    Retorna 'A', 'B' ou 'empate'.
    """
    judge_prompt = f"""Você é um avaliador especializado em qualidade de respostas de modelos de linguagem.

PERGUNTA DO USUÁRIO:
{prompt}

RESPOSTA A:
{response_a}

RESPOSTA B:
{response_b}

Compare as duas respostas considerando: {criteria}.
Qual resposta é melhor? Responda com APENAS uma das opções: "A", "B" ou "empate".
Não inclua nenhum outro texto."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=10,
        temperature=0.0,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    
    verdict = response.content[0].text.strip().upper()
    if verdict not in ("A", "B", "EMPATE"):
        verdict = "EMPATE"
    return verdict


def compute_win_rate(
    eval_prompts: list[str],
    model_a_pipeline,           # modelo fine-tunado (challenger)
    model_b_pipeline,           # modelo base (baseline)
    n_samples: Optional[int] = None,
) -> dict:
    """
    Avalia win rate do modelo A vs modelo B usando LLM-as-judge.
    
    Returns:
        dict com win_rate, lose_rate, tie_rate e detalhes por prompt
    """
    if n_samples:
        eval_prompts = eval_prompts[:n_samples]
    
    results = {"A": 0, "B": 0, "EMPATE": 0, "details": []}
    
    for i, prompt in enumerate(eval_prompts):
        resp_a = generate_response(model_a_pipeline, prompt)
        resp_b = generate_response(model_b_pipeline, prompt)
        
        verdict = llm_judge_pairwise(prompt, resp_a, resp_b)
        results[verdict] += 1
        results["details"].append({
            "prompt": prompt,
            "response_a": resp_a,
            "response_b": resp_b,
            "verdict": verdict,
        })
        
        if (i + 1) % 10 == 0:
            total_so_far = i + 1
            print(f"Progress: {total_so_far}/{len(eval_prompts)} | "
                  f"Win: {results['A']/total_so_far:.1%} | "
                  f"Lose: {results['B']/total_so_far:.1%} | "
                  f"Tie: {results['EMPATE']/total_so_far:.1%}")
    
    total = len(eval_prompts)
    return {
        "win_rate": results["A"] / total,
        "lose_rate": results["B"] / total,
        "tie_rate": results["EMPATE"] / total,
        "n_evaluated": total,
        "raw_counts": {k: v for k, v in results.items() if k != "details"},
        "details": results["details"],
    }
```

### 4. Usar LLM-as-Judge para Criar Preferências Automaticamente

```python
# rlaif_preference_generator.py
# Gera pares de preferência usando LLM como juiz (RLAIF)
from anthropic import Anthropic
from transformers import pipeline
import torch
import json
from pathlib import Path

client = Anthropic()

def generate_candidate_responses(
    model_pipeline,
    prompt: str,
    n_candidates: int = 4,
    temperatures: list[float] = [0.3, 0.7, 0.9, 1.1],
) -> list[str]:
    """
    Gera múltiplos candidatos de resposta com temperaturas diferentes.
    Diversidade de temperatura promove variedade nas respostas.
    """
    candidates = []
    for temp in temperatures[:n_candidates]:
        outputs = model_pipeline(
            prompt,
            max_new_tokens=512,
            temperature=max(temp, 0.01),
            do_sample=True,
            pad_token_id=model_pipeline.tokenizer.eos_token_id,
        )
        response = outputs[0]["generated_text"][len(prompt):].strip()
        candidates.append(response)
    return candidates


def rank_responses_with_llm(
    prompt: str,
    candidates: list[str],
    constitution: str = "útil, honesto, seguro e conciso",
) -> list[int]:
    """
    Usa Claude para ranquear múltiplos candidatos.
    Retorna lista de índices do melhor ao pior.
    """
    formatted_candidates = "\n\n".join(
        f"RESPOSTA {i+1}:\n{resp}" for i, resp in enumerate(candidates)
    )
    
    rank_prompt = f"""Você avalia respostas de modelos de linguagem. O critério é: {constitution}.

PERGUNTA:
{prompt}

{formatted_candidates}

Ranqueie as {len(candidates)} respostas da MELHOR para a PIOR.
Responda APENAS com os números separados por vírgula, ex: "3,1,4,2" (melhor primeiro).
Não inclua texto adicional."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=20,
        temperature=0.0,
        messages=[{"role": "user", "content": rank_prompt}],
    )
    
    try:
        ranking_str = response.content[0].text.strip()
        ranking = [int(x.strip()) - 1 for x in ranking_str.split(",")]
        # Validar que contém todos os índices
        if sorted(ranking) == list(range(len(candidates))):
            return ranking
    except (ValueError, IndexError):
        pass
    
    # Fallback: ordem original
    return list(range(len(candidates)))


def generate_preference_dataset_rlaif(
    prompts: list[str],
    model_pipeline,
    output_path: str = "rlaif_preferences.jsonl",
    n_candidates: int = 4,
) -> list[dict]:
    """
    Pipeline completo de geração de preferências via RLAIF.
    Para cada prompt: gera N candidatos, ranqueia com LLM, cria par (best, worst).
    """
    output_file = Path(output_path)
    all_pairs = []
    
    for i, prompt in enumerate(prompts):
        print(f"Gerando preferências para prompt {i+1}/{len(prompts)}...")
        
        # Gerar candidatos
        candidates = generate_candidate_responses(model_pipeline, prompt, n_candidates)
        
        # Ranquear com LLM
        ranking = rank_responses_with_llm(prompt, candidates)
        
        # Criar par (melhor, pior) — máxima margem de qualidade
        best_idx = ranking[0]
        worst_idx = ranking[-1]
        
        pair = {
            "prompt": prompt,
            "chosen": candidates[best_idx],
            "rejected": candidates[worst_idx],
            "ranking": ranking,
            "n_candidates": n_candidates,
        }
        all_pairs.append(pair)
        
        # Salvar incrementalmente
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    print(f"\nDataset gerado: {len(all_pairs)} pares de preferência em {output_path}")
    return all_pairs
```

---

## Checklist de Alignment em Produção

Antes de fazer deploy de um modelo alinhado via RLHF/DPO, verificar:

- [ ] KL divergence do modelo final vs SFT de referência está dentro do range esperado (β × KL < 2.0)
- [ ] Win rate do modelo alinhado vs SFT base (LLM-as-judge) > 60%
- [ ] Benchmarks de capacidade (MMLU, HumanEval) não regridem mais de 3% vs baseline
- [ ] Red-teaming em categorias de risco conhecidas (violence, self-harm, PII extraction)
- [ ] Teste de sycophancy: o modelo mantém posição correta quando o usuário insiste com informação errada?
- [ ] Teste de verbosidade: as respostas ficaram sistematicamente mais longas sem motivo?
- [ ] Avaliação em distribuição out-of-domain: o modelo generaliza ou apenas imita os dados de preferência?

> [!warning] Qualidade Dos Dados de Preferência
> DPO é muito sensível à qualidade dos pares (chosen, rejected). Pares onde a diferença de qualidade é ambígua degradam o treinamento. Use margin filtering: só inclua pares onde o chosen é claramente melhor. Um sinal de dados ruins: a loss DPO oscila sem convergir, ou converge mas o win rate não melhora. Ambos indicam que os pares chosen/rejected não têm diferença de qualidade suficiente para o modelo aprender.

---

## References

- [InstructGPT: Training language models to follow instructions with human feedback (Ouyang et al., 2022)](https://arxiv.org/abs/2203.02155)
- [Direct Preference Optimization: Your Language Model is Secretly a Reward Model (Rafailov et al., 2023)](https://arxiv.org/abs/2305.18290)
- [Constitutional AI: Harmlessness from AI Feedback (Bai et al., 2022)](https://arxiv.org/abs/2212.08073)
- [ORPO: Monolithic Preference Optimization without Reference Model (Hong et al., 2024)](https://arxiv.org/abs/2403.07691)
- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (2025)](https://arxiv.org/abs/2501.12948)
- [Proximal Policy Optimization Algorithms (Schulman et al., 2017)](https://arxiv.org/abs/1707.06347)
- [TRL Library: Transformer Reinforcement Learning (HuggingFace)](https://github.com/huggingface/trl)

---

## Related

- [[fine-tuning-peft]] — etapa anterior ao alignment: SFT e LoRA/QLoRA
- [[pretraining]] — base model que alimenta o pipeline de alignment
- [[benchmarks-evals]] — como avaliar modelos alinhados sem viés
- [[prompt-engineering]] — técnicas complementares ao alignment para guiar comportamento
- [[claude-api]] — API que expõe modelos alinhados pela Anthropic (Claude)
