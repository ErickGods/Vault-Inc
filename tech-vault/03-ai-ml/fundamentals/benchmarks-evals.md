---
tags: [ai-ml, fundamentals, benchmarks, evals, evaluation, mmlu]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Benchmarks, LLM Evals, MMLU, HumanEval, Chatbot Arena]
---

# Benchmarks e Evals de LLMs

## Overview

Benchmarks existem para tornar a seleção de modelos objetiva. Mas há um problema fundamental: **Goodhart's Law** — quando uma medida vira target, ela deixa de ser uma boa medida.

Em prática, isso significa: assim que um benchmark se torna amplamente adotado, os laboratórios de IA otimizam explicitamente para ele. Dados de treino começam a incluir (intencionalmente ou não) questões similares às do benchmark. Os modelos ficam "bons no benchmark" sem necessariamente ficarem melhores na tarefa real que o benchmark pretendia medir.

Este é o ciclo de vida de um benchmark LLM:

```
Benchmark criado → Laboratórios competem → Scores sobem
       ↓                                          ↓
Benchmark saturado ←───── Dados de treino contaminam
       ↓
Novo benchmark criado para substituir
```

Entender esse ciclo é essencial para usar benchmarks corretamente: como sinais de tendência, não como medidas absolutas de capacidade.

### Por Que Benchmarks Ainda Importam

Apesar das limitações, benchmarks bem construídos oferecem:
- Comparação padronizada entre modelos (mesmas condições de teste)
- Reproducibilidade — outros pesquisadores podem verificar resultados
- Sinalização de progresso relativo em capacidades específicas
- Triagem rápida para eliminar modelos claramente inferiores antes de avaliação humana

A chave é usar múltiplos benchmarks em conjunto, entender as limitações de cada um, e complementar com evals customizados do seu domínio específico.

---

## MMLU — Massive Multitask Language Understanding

### Descrição

MMLU (Hendrycks et al., 2020) é o benchmark de knowledge mais utilizado para LLMs. Testa conhecimento em 57 domínios e subdomínios via questões de múltipla escolha (A, B, C, D).

**Domínios cobertos:** matemática elementar, álgebra, física, química, biologia, história, direito, medicina, filosofia, ciência da computação, economia, psicologia, e mais 45 outros.

**Protocolo padrão:** 4-shot few-shot — o modelo recebe 4 exemplos do formato pergunta/resposta antes da questão de teste. Isso testa tanto o conhecimento quanto a capacidade de seguir o formato.

### Scoring

```python
# Scoring do MMLU: accuracy por domínio, depois macro-average
def compute_mmlu_score(results: dict) -> float:
    """
    results: {subject: {"correct": int, "total": int}}
    Retorna: macro-average accuracy entre todos os 57 subjects
    """
    subject_accuracies = []
    for subject, data in results.items():
        acc = data["correct"] / data["total"]
        subject_accuracies.append(acc)

    # Macro-average: cada subject tem peso igual, independente de tamanho
    return sum(subject_accuracies) / len(subject_accuracies)
```

A escolha de macro-average (vs. micro-average por questão) implica que domínios com poucas questões têm o mesmo peso que domínios com muitas — decisão de design que pode ser questionada.

### Limitações

- **Múltipla escolha não testa geração livre** — um modelo pode escolher A por eliminação sem saber a resposta correta
- **Saturação crescente** — modelos topo (GPT-4o, Claude 3.5, Gemini 1.5 Pro) chegam a 85-90%, próximos ao ceiling
- **Contaminação** — questões do MMLU aparecem em web scrapes usados em pré-treino
- **Não testa reasoning multi-step** — a maioria das questões tem resposta em um único passo de raciocínio

> [!info] MMLU Está Saturando
> Modelos top (GPT-4o, Claude 3.7, Gemini 2.0) estão chegando perto do ceiling do MMLU (~90%). Novos benchmarks como GPQA (graduate-level, ~60% humanos experts), MMMU (multimodal) e MATH-500 estão progressivamente substituindo o MMLU como discriminador entre modelos de ponta.

---

## HumanEval — Avaliação de Código Python

### Descrição

HumanEval (Chen et al., 2021, OpenAI) consiste em 164 problemas de programação Python. Cada problema tem:
- Um docstring descrevendo a função a implementar
- Uma assinatura de função
- Unit tests (ocultos durante geração, usados para scoring)

**Exemplo de problema:**

```python
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """
    Check if in given list of numbers, are any two numbers
    closer to each other than given threshold.
    >>> has_close_elements([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3)
    True
    >>> has_close_elements([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05)
    False
    """
```

### Métrica pass@k

pass@k mede a probabilidade de que pelo menos uma das k amostras geradas passe em todos os unit tests.

**Fórmula exata** (sem viés — versão do paper):

```
pass@k = 1 - C(n-c, k) / C(n, k)

Onde:
  n = número total de amostras geradas por problema
  c = número de amostras que passam em todos os tests
  k = número de tentativas "usadas" na métrica
  C(n, k) = combinação n escolha k

Exemplo: n=10 amostras, c=3 corretas, k=1:
  pass@1 = 1 - C(7, 1) / C(10, 1) = 1 - 7/10 = 0.30 = 30%

Com k=10:
  pass@10 = 1 - C(0, 10) / C(10, 10) = 1 - 0/1 = 1.0 = 100%
```

**Por que usar essa fórmula** em vez de simplesmente "quantas vezes passou em k tentativas"? A versão combinatória é não-viesada — produz estimativas mais precisas especialmente quando n é pequeno.

### Limitações

- **Problemas simples** — a maioria são exercícios de programação básica, não problemas do mundo real
- **Satura rápido** — modelos modernos chegam a pass@1 > 80%
- **Contaminação alta** — 164 problemas fixos, amplamente disponíveis online
- **Não testa debugging, refactoring, ou código em produção**

---

## MATH — Problemas Competition-Level

### Descrição

O dataset MATH (Hendrycks et al., 2021) contém 12.500 problemas matemáticos de competição em 5 níveis de dificuldade e 7 tópicos:

| Tópico | Problemas | Dificuldade típica |
|--------|-----------|-------------------|
| Álgebra | ~1.700 | Nível 1-5 |
| Contagem e Probabilidade | ~870 | Nível 2-5 |
| Geometria | ~780 | Nível 2-5 |
| Álgebra Intermediária | ~1.290 | Nível 3-5 |
| Pré-álgebra | ~870 | Nível 1-3 |
| Pré-cálculo | ~780 | Nível 3-5 |
| Teoria dos Números | ~540 | Nível 2-5 |

**Dificuldades:** 1 (fácil, AMC 8) a 5 (muito difícil, AIME/Putnam)

### Scoring

A métrica é **exact match após normalização LaTeX**:

```python
import re
from sympy import simplify, sympify
from sympy.parsing.latex import parse_latex

def normalize_math_answer(answer: str) -> str:
    """
    Normaliza resposta matemática para comparação.
    Remove espaços, LaTeX equivalente, formatos alternativos.
    """
    # Remove espaços extras
    answer = answer.strip()

    # Normaliza LaTeX comum
    answer = answer.replace("\\left(", "(").replace("\\right)", ")")
    answer = answer.replace("\\left[", "[").replace("\\right]", "]")
    answer = re.sub(r'\\,', '', answer)  # remove thin spaces
    answer = re.sub(r'\s+', ' ', answer)

    return answer


def is_correct_math(prediction: str, ground_truth: str) -> bool:
    """
    Compara resposta do modelo com gabarito.
    Tenta exact match primeiro, depois equivalência simbólica.
    """
    pred_norm = normalize_math_answer(prediction)
    gt_norm = normalize_math_answer(ground_truth)

    # Exact match (após normalização)
    if pred_norm == gt_norm:
        return True

    # Tentar equivalência simbólica via sympy
    try:
        pred_sym = parse_latex(pred_norm)
        gt_sym = parse_latex(gt_norm)
        return simplify(pred_sym - gt_sym) == 0
    except Exception:
        return False
```

**Por que MATH é mais difícil de saturar:** Problemas de nível 5 requerem múltiplos steps de reasoning e conhecimento matemático avançado — mais difícil de memorizar por contaminação de treino.

---

## BIG-Bench Hard (BBH)

### Descrição

BIG-Bench Hard (Suzgun et al., 2022) é um subconjunto de 23 tarefas do BIG-Bench original — especificamente as tarefas em que GPT-4 (na época) não superava humanos facilmente. Essas tarefas testam raciocínio:

| Categoria | Tarefas exemplo |
|-----------|----------------|
| Raciocínio Lógico | Boolean expressions, logical deduction, formal fallacies |
| Raciocínio Causal | Causal judgment, physical intuition |
| Lógica Simbólica | Dyck languages, word sorting |
| Multistep | Multi-step arithmetic, tracking shuffled objects |
| Linguístico | Snarks, disambiguation QA |

### Chain-of-Thought Obrigatório

BBH é projetado para ser avaliado com Chain-of-Thought (CoT). Sem CoT, modelos se saem bem pior — a intenção é medir a capacidade de raciocínio step-by-step, não apenas recuperação de fatos.

**Formato padrão:**

```
Few-shot exemplo:
Q: Se A está à esquerda de B, e B está à esquerda de C, 
   quem está mais à direita?
A: Vou raciocinar passo a passo.
   A está à esquerda de B → A < B em posição.
   B está à esquerda de C → B < C em posição.
   Portanto A < B < C → C está mais à direita.
   Resposta: C

Questão de teste: [nova pergunta]
A: Vou raciocinar passo a passo.
```

---

## LMSYS Chatbot Arena

### Descrição

O Chatbot Arena (Chiang et al., 2024) é fundamentalmente diferente dos benchmarks anteriores: usa **avaliação humana cega por comparação pareada** em vez de benchmarks fixos.

Usuários interagem com dois modelos anônimos simultaneamente e votam em qual resposta foi melhor (ou empate). Após votar, os nomes dos modelos são revelados.

### Elo Rating

O sistema usa Elo rating adaptado de xadrez para construir um ranking global:

```python
def expected_score(rating_a: float, rating_b: float) -> float:
    """Probabilidade esperada de A ganhar contra B."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(
    rating_a: float,
    rating_b: float,
    score_a: float,  # 1.0 = A ganhou, 0.5 = empate, 0.0 = B ganhou
    k: float = 32.0,
) -> tuple[float, float]:
    """
    Atualiza ratings Elo após uma partida.

    K=32 é o padrão do Chatbot Arena — maior K significa
    que cada voto tem mais impacto no rating.

    Args:
        rating_a: Rating atual de A
        rating_b: Rating atual de B
        score_a: Resultado para A (1=ganhou, 0.5=empate, 0=perdeu)
        k: Fator de atualização

    Returns:
        (novo_rating_a, novo_rating_b)
    """
    e_a = expected_score(rating_a, rating_b)
    e_b = expected_score(rating_b, rating_a)
    score_b = 1.0 - score_a

    new_rating_a = rating_a + k * (score_a - e_a)
    new_rating_b = rating_b + k * (score_b - e_b)

    return new_rating_a, new_rating_b


# Exemplo: GPT-4o (1300) vs Claude 3.5 (1285), GPT-4o ganhou
r_a, r_b = update_ratings(1300.0, 1285.0, score_a=1.0)
print(f"Após vitória de GPT-4o: GPT-4o={r_a:.1f}, Claude={r_b:.1f}")

# Interpretação: diferença de 100 pontos Elo ≈ 64% win rate do mais forte
diff = 100
win_prob = 1 / (1 + 10 ** (-diff / 400))
print(f"Diferença de {diff} pontos Elo → {win_prob:.1%} win rate")
```

### Por Que Chatbot Arena É Valioso

- **Feedback humano real** em tasks abertas — não questões pré-definidas
- **Diversidade de usuários** — milhares de pessoas com diferentes necessidades
- **Qualquer tipo de task** — código, escrita criativa, análise, conversação

### Vieses do Chatbot Arena

- **Verbosity bias** — respostas mais longas tendem a ganhar mais votos, mesmo que contenham mais conteúdo desnecessário
- **Cultural bias** — usuários majoritariamente anglófonos e de contextos ocidentais
- **Positional bias** — modelo na posição A pode ter vantagem ou desvantagem sistemática
- **Selection bias** — usuários que escolhem usar Chatbot Arena não representam todos os usuários
- **Não reprodutível** — ranking muda conforme novos votos chegam

> [!warning] Chatbot Arena Não É Reprodutível
> O ranking do Chatbot Arena muda conforme novos votos chegam. Um modelo que era #1 hoje pode ser #3 amanhã com a chegada de novos competidores ou mudança no perfil de usuários. Use como sinal de tendência qualitativa, não como medida absoluta e estável.

---

## MT-Bench — Multi-Turn Quality

### Descrição

MT-Bench (Zheng et al., 2023) consiste em 80 perguntas multiturn de alta qualidade cobrindo 8 categorias:

| Categoria | Exemplos |
|-----------|---------|
| Writing | Escreva um artigo sobre X, melhore este texto |
| Roleplay | Assuma o papel de Y e responda |
| Extraction | Extraia informações estruturadas de X |
| Math | Resolva problemas step-by-step |
| Coding | Implemente função, debug código |
| STEM | Explique conceito científico |
| Humanities | Análise histórica, filosófica |
| Others | Classificação, tradução |

Cada questão tem 2 turns: a primeira pergunta e uma follow-up que testa consistência e capacidade multiturn.

### LLM-as-Judge

O diferencial do MT-Bench é usar GPT-4 como juiz automatizado, avaliando respostas de 1 a 10 com critérios explícitos:

```python
MT_BENCH_JUDGE_PROMPT = """
[System]
Please act as an impartial judge and evaluate the quality of the response 
provided by an AI assistant to the user question displayed below. Your 
evaluation should consider factors such as the helpfulness, relevance, 
accuracy, depth, creativity, and level of detail of the response. Be as 
objective as possible. Rate the response on a scale of 1 to 10.

[Question]
{question}

[The Start of Assistant's Answer]
{answer}
[The End of Assistant's Answer]

After providing your explanation, you must rate the response on a scale of 
1 to 10 by strictly following this format: "[[rating]]", for example: 
"Rating: [[5]]".
"""
```

**Vantagem:** Escalável — pode avaliar milhares de respostas sem custo humano.
**Desvantagem:** LLM juiz tem preferência por outputs que se parecem com seu próprio estilo (self-preference bias), e GPT-4 como juiz tende a favorecer respostas similares às do GPT-4.

---

## Como Rodar Evals Localmente — lm-evaluation-harness

O `lm-evaluation-harness` da EleutherAI é a ferramenta padrão para rodar benchmarks padronizados localmente:

```bash
# Instalar
pip install lm_eval

# Rodar MMLU, HellaSwag, ARC Challenge e TruthfulQA em Llama 3 8B
lm_eval --model hf \
    --model_args pretrained=meta-llama/Meta-Llama-3-8B-Instruct \
    --tasks mmlu,hellaswag,arc_challenge,truthfulqa_mc2 \
    --device cuda:0 \
    --batch_size 8 \
    --output_path ./results/llama3_8b \
    --log_samples

# Para modelos maiores com múltiplas GPUs:
lm_eval --model hf \
    --model_args pretrained=meta-llama/Meta-Llama-3-70B-Instruct,dtype=bfloat16,parallelize=True \
    --tasks mmlu \
    --device cuda \
    --batch_size 4 \
    --output_path ./results/llama3_70b

# Rodar apenas um subset do MMLU (mais rápido para testes):
lm_eval --model hf \
    --model_args pretrained=microsoft/phi-2 \
    --tasks mmlu_abstract_algebra,mmlu_college_mathematics \
    --device cuda:0 \
    --batch_size 16 \
    --num_fewshot 4
```

**Resultado típico (JSON):**

```json
{
  "results": {
    "mmlu": {
      "acc,none": 0.6821,
      "acc_stderr,none": 0.0041
    },
    "hellaswag": {
      "acc_norm,none": 0.8134,
      "acc_norm_stderr,none": 0.0039
    }
  },
  "config": {
    "model": "hf",
    "model_args": "pretrained=meta-llama/Meta-Llama-3-8B-Instruct",
    "num_fewshot": 0
  }
}
```

> [!warning] Prompt Sensitivity
> Pequenas mudanças no prompt de eval — capitalização, pontuação, espaços, ordem dos choices — podem mudar resultados em 2-5 pontos percentuais no MMLU. Sempre use a mesma versão exata do prompt e do harness para comparações. Especifique versão do lm-eval e commit hash do modelo nas suas anotações de experimento.

> [!warning] Data Contamination Infla Scores
> Modelos treinados em dados que incluem (mesmo parcialmente) questões de benchmarks públicos têm scores artificialmente inflados. Benchmarks como MMLU e HumanEval são tão conhecidos que provavelmente aparecem em variantes nos dados de treino de todos os modelos grandes. Para comparações honestas entre seus próprios modelos, use evals privados não publicados.

---

## LLM-as-Judge — Metodologia e Vieses

### Quando Usar LLM-as-Judge

LLM-as-judge é valioso quando:
- O volume de avaliações é grande demais para avaliação humana
- As respostas corretas são subjetivas (qualidade de escrita, completude)
- Você precisa de avaliação multidimensional com critérios explícitos

**Não use LLM-as-judge quando:**
- A resposta tem ground truth verificável (use unit tests, exact match)
- O juiz pode ser contaminado por conhecimento sobre quem criou o modelo

### Vieses Documentados

| Viés | Descrição | Mitigação |
|------|-----------|-----------|
| Verbosity bias | Respostas longas ganham pontuação maior independente da qualidade | Instruir o juiz a penalizar padding |
| Self-preference | Claude prefere outputs parecidos com Claude, GPT-4 prefere GPT-4 | Usar múltiplos juízes de diferentes famílias |
| Positional bias | Posição A frequentemente ganha mais em pairwise | Sempre trocar posições e fazer média |
| Sycophancy | Juiz LLM tende a concordar com a resposta que parece mais confiante | Rubrica com critérios objetivos explícitos |

### Protocolo Robusto de Pairwise Comparison

```python
import random
from anthropic import Anthropic

client = Anthropic()

def pairwise_eval_with_swap(
    question: str,
    response_a: str,
    response_b: str,
    criteria: str,
    judge_model: str = "claude-opus-4-5",
    n_judges: int = 1,
) -> dict:
    """
    Avaliação pairwise robusta com swap de posição.

    Executa o julgamento duas vezes (A vs B e B vs A) para
    detectar e corrigir positional bias.

    Args:
        question: Pergunta original
        response_a: Resposta do modelo A
        response_b: Resposta do modelo B
        criteria: Critérios de avaliação em linguagem natural
        judge_model: Modelo a usar como juiz
        n_judges: Número de rodadas de julgamento

    Returns:
        dict com winner, confidence e raciocínio
    """
    JUDGE_PROMPT = """Você é um avaliador imparcial de respostas de IA.

Pergunta original: {question}

Critérios de avaliação:
{criteria}

Resposta 1:
{response_1}

Resposta 2:
{response_2}

Avalie qual resposta é melhor com base nos critérios acima.
NÃO considere o comprimento da resposta como indicador de qualidade.
Responda EXATAMENTE neste formato JSON:
{{
  "winner": "1" ou "2" ou "tie",
  "confidence": "high" ou "medium" ou "low",
  "reasoning": "explicação em 2-3 frases"
}}"""

    results = []

    for _ in range(n_judges):
        # Ordem original: A=1, B=2
        prompt_normal = JUDGE_PROMPT.format(
            question=question,
            criteria=criteria,
            response_1=response_a,
            response_2=response_b,
        )

        # Ordem invertida: B=1, A=2
        prompt_swapped = JUDGE_PROMPT.format(
            question=question,
            criteria=criteria,
            response_1=response_b,
            response_2=response_a,
        )

        import json

        def get_judgment(prompt: str) -> dict:
            response = client.messages.create(
                model=judge_model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            # Extrair JSON da resposta
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)

        judgment_normal = get_judgment(prompt_normal)
        judgment_swapped = get_judgment(prompt_swapped)

        # Normalizar resultado do julgamento invertido
        # winner "1" no swapped = B ganhou (B estava na posição 1)
        if judgment_swapped["winner"] == "1":
            swapped_winner = "B"
        elif judgment_swapped["winner"] == "2":
            swapped_winner = "A"
        else:
            swapped_winner = "tie"

        normal_winner = {"1": "A", "2": "B", "tie": "tie"}[judgment_normal["winner"]]

        results.append({
            "normal": {**judgment_normal, "winner": normal_winner},
            "swapped": {**judgment_swapped, "winner": swapped_winner},
        })

    # Agregar resultados
    winners = []
    for r in results:
        if r["normal"]["winner"] == r["swapped"]["winner"]:
            # Acordo entre as duas ordens → resultado confiável
            winners.append(r["normal"]["winner"])
        else:
            # Desacordo → provável positional bias, registrar como tie
            winners.append("tie")

    from collections import Counter
    winner_counts = Counter(winners)
    final_winner = winner_counts.most_common(1)[0][0]

    return {
        "winner": final_winner,
        "votes": dict(winner_counts),
        "positional_bias_detected": any(
            r["normal"]["winner"] != r["swapped"]["winner"] for r in results
        ),
        "raw_results": results,
    }
```

---

## Evals Customizados para Vault-Inc

> [!tip] Crie Evals do Seu Domínio
> Benchmarks genéricos (MMLU, HumanEval) não medem o que importa para seu produto. 100-500 perguntas do seu domínio específico são mais valiosas do que qualquer benchmark público para tomar decisões de seleção de modelo. Invista na criação desses evals antes de escalar qualquer solução baseada em LLM.

Para a Vault-Inc, os casos de uso mais relevantes são análise de investimentos e decisões de arquitetura de software. Um eval customizado nesses domínios deve testar:

**Para Análise de Investimentos:**
- Análise de demonstrações financeiras (balanço, DRE, DFC)
- Identificação de red flags em documentos de empresas
- Comparação de múltiplos de valuation (P/E, EV/EBITDA, P/B)
- Raciocínio sobre risco/retorno de classes de ativos

**Para Decisões de Arquitetura:**
- Escolha de padrão arquitetural dado requisitos
- Identificação de problemas em código ou sistema design
- Trade-offs de tecnologias específicas (DB, mensageria, etc.)

---

## Código Prático

### 1. Implementar pass@k do Zero

```python
from math import comb
from typing import Callable
import random

def pass_at_k(n: int, c: int, k: int) -> float:
    """
    Calcula pass@k de forma não-viesada.

    Fórmula: pass@k = 1 - C(n-c, k) / C(n, k)

    Args:
        n: Número total de amostras geradas por problema
        c: Número de amostras corretas (que passam nos tests)
        k: Número de tentativas consideradas na métrica

    Returns:
        Probabilidade de que pelo menos uma das k amostras esteja correta

    Raises:
        ValueError: Se c > n ou k > n
    """
    if c > n:
        raise ValueError(f"c ({c}) não pode ser maior que n ({n})")
    if k > n:
        raise ValueError(f"k ({k}) não pode ser maior que n ({n})")
    if n == 0:
        return 0.0

    # Caso especial: se todas as amostras são corretas
    if n - c < k:
        return 1.0

    # Fórmula combinatória não-viesada
    return 1.0 - comb(n - c, k) / comb(n, k)


def evaluate_pass_at_k(
    problems: list[dict],
    generate_fn: Callable,
    test_fn: Callable,
    n_samples: int = 10,
    k_values: list[int] = [1, 5, 10],
) -> dict:
    """
    Avalia pass@k para um conjunto de problemas.

    Args:
        problems: Lista de dicts com 'prompt' e 'tests'
        generate_fn: Função que recebe prompt e retorna n_samples soluções
        test_fn: Função que verifica se solução passa nos tests
        n_samples: Amostras geradas por problema
        k_values: Valores de k para calcular pass@k

    Returns:
        dict com pass@k para cada valor de k e por problema
    """
    problem_results = []

    for i, problem in enumerate(problems):
        print(f"Problema {i+1}/{len(problems)}: {problem.get('name', f'P{i+1}')}")

        # Gerar n_samples soluções
        solutions = generate_fn(problem["prompt"], n=n_samples)

        # Testar cada solução
        correct = 0
        for solution in solutions:
            try:
                passed = test_fn(solution, problem["tests"])
                if passed:
                    correct += 1
            except Exception:
                pass  # Erro em execução = falha

        problem_results.append({
            "problem": problem.get("name", f"P{i+1}"),
            "n": n_samples,
            "c": correct,
        })
        print(f"  Corretas: {correct}/{n_samples} = {correct/n_samples:.1%}")

    # Calcular pass@k agregado (média sobre todos os problemas)
    aggregated = {}
    for k in k_values:
        if k > n_samples:
            continue
        scores = [pass_at_k(r["n"], r["c"], k) for r in problem_results]
        aggregated[f"pass@{k}"] = {
            "mean": sum(scores) / len(scores),
            "per_problem": scores,
        }

    return {
        "summary": aggregated,
        "per_problem": problem_results,
        "n_problems": len(problems),
        "n_samples_per_problem": n_samples,
    }


# Exemplo de uso com problemas de Python simples
def demo_pass_at_k():
    # Dados sintéticos para demonstração
    scenarios = [
        {"n": 10, "c": 0, "k": 1, "expected": 0.0},
        {"n": 10, "c": 10, "k": 1, "expected": 1.0},
        {"n": 10, "c": 3, "k": 1, "expected": 0.3},   # 1 - 7/10
        {"n": 10, "c": 3, "k": 5, "expected": None},  # calcular
    ]

    print("=== Exemplos pass@k ===")
    for s in scenarios:
        result = pass_at_k(s["n"], s["c"], s["k"])
        expected_str = f" (esperado: {s['expected']:.2f})" if s["expected"] is not None else ""
        print(f"  n={s['n']}, c={s['c']}, k={s['k']} → pass@k = {result:.4f}{expected_str}")

demo_pass_at_k()
```

### 2. LLM-as-Judge com Critérios Customizados

```python
from anthropic import Anthropic
import json
from typing import Optional

client = Anthropic()

# Critérios específicos para análise de investimentos (Vault-Inc)
INVESTMENT_EVAL_CRITERIA = """
Avalie a resposta do assistente em análise financeira segundo estes critérios:

1. PRECISÃO FACTUAL (0-3 pts): Números, fórmulas e conceitos financeiros estão corretos?
2. COMPLETUDE (0-3 pts): A resposta aborda todos os aspectos relevantes da pergunta?
3. RACIOCÍNIO (0-3 pts): A lógica analítica é sólida e bem fundamentada?
4. APLICABILIDADE (0-3 pts): A resposta é acionável para decisões de investimento reais?

Pontuação total: 0-12 pontos
"""

ARCHITECTURE_EVAL_CRITERIA = """
Avalie a resposta de arquitetura de software segundo estes critérios:

1. CORREÇÃO TÉCNICA (0-3 pts): Conceitos e trade-offs estão corretos?
2. CONTEXTUALIDADE (0-3 pts): A resposta considera os requisitos específicos do cenário?
3. TRADE-OFFS (0-3 pts): Pontos positivos e negativos são discutidos honestamente?
4. IMPLEMENTABILIDADE (0-3 pts): A solução é realista e implementável?

Pontuação total: 0-12 pontos
"""

JUDGE_PROMPT_TEMPLATE = """Você é um avaliador especializado. Avalie a resposta abaixo segundo os critérios fornecidos.

=== PERGUNTA ===
{question}

=== RESPOSTA DO ASSISTENTE ===
{response}

=== CRITÉRIOS DE AVALIAÇÃO ===
{criteria}

Responda EXATAMENTE neste formato JSON (sem markdown):
{{
  "scores": {{
    "criterion_1": <0-3>,
    "criterion_2": <0-3>,
    "criterion_3": <0-3>,
    "criterion_4": <0-3>
  }},
  "total": <0-12>,
  "strengths": ["ponto forte 1", "ponto forte 2"],
  "weaknesses": ["ponto fraco 1"],
  "verdict": "excelente|bom|adequado|insuficiente"
}}"""


def evaluate_with_custom_criteria(
    question: str,
    response: str,
    domain: str = "investment",  # "investment" ou "architecture"
    judge_model: str = "claude-opus-4-5",
) -> dict:
    """
    Avalia uma resposta de LLM com critérios específicos do domínio Vault-Inc.

    Args:
        question: Pergunta original feita ao modelo
        response: Resposta do modelo a ser avaliada
        domain: Domínio da avaliação (investment ou architecture)
        judge_model: Modelo Claude a usar como juiz

    Returns:
        dict com scores por critério, total e veredicto
    """
    criteria = INVESTMENT_EVAL_CRITERIA if domain == "investment" else ARCHITECTURE_EVAL_CRITERIA

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        question=question,
        response=response,
        criteria=criteria,
    )

    judge_response = client.messages.create(
        model=judge_model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    result_text = judge_response.content[0].text.strip()

    # Parsear JSON
    evaluation = json.loads(result_text)

    # Adicionar metadados
    evaluation["domain"] = domain
    evaluation["judge_model"] = judge_model
    evaluation["normalized_score"] = evaluation["total"] / 12  # 0.0 a 1.0

    return evaluation


def batch_evaluate(
    test_cases: list[dict],
    model_responses: list[str],
    domain: str = "investment",
) -> dict:
    """
    Avalia múltiplos casos de teste em batch.

    Args:
        test_cases: Lista de dicts com "question" e opcionalmente "reference_answer"
        model_responses: Respostas do modelo para cada test case
        domain: Domínio de avaliação

    Returns:
        dict com scores por caso e sumário estatístico
    """
    assert len(test_cases) == len(model_responses), "Número de casos e respostas deve ser igual"

    results = []
    for i, (case, response) in enumerate(zip(test_cases, model_responses)):
        print(f"Avaliando caso {i+1}/{len(test_cases)}...")
        eval_result = evaluate_with_custom_criteria(
            question=case["question"],
            response=response,
            domain=domain,
        )
        eval_result["case_id"] = i
        eval_result["question"] = case["question"][:100] + "..."  # Truncar para legibilidade
        results.append(eval_result)

    # Calcular estatísticas
    scores = [r["normalized_score"] for r in results]
    verdicts = [r["verdict"] for r in results]

    from collections import Counter
    verdict_counts = Counter(verdicts)

    summary = {
        "n_cases": len(results),
        "mean_score": sum(scores) / len(scores),
        "min_score": min(scores),
        "max_score": max(scores),
        "verdict_distribution": dict(verdict_counts),
        "cases_above_0_7": sum(1 for s in scores if s >= 0.7),
        "cases_below_0_5": sum(1 for s in scores if s < 0.5),
    }

    return {
        "summary": summary,
        "per_case": results,
    }
```

### 3. Win Rate Evaluation entre Dois Modelos

```python
import anthropic
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class ModelConfig:
    name: str
    display_name: str
    client: anthropic.Anthropic = field(default_factory=anthropic.Anthropic)
    model_id: str = "claude-opus-4-5"


def run_win_rate_eval(
    test_questions: list[str],
    model_a: ModelConfig,
    model_b: ModelConfig,
    judge_model: str = "claude-opus-4-5",
    criteria: str = "Qual resposta é mais útil, precisa e clara?",
    swap_positions: bool = True,
) -> dict:
    """
    Calcula win rate entre dois modelos com protocolo rigoroso.

    Executa julgamento com e sem swap de posição para detectar
    positional bias. Agrega resultados com desempate.

    Args:
        test_questions: Lista de perguntas de teste
        model_a: Configuração do modelo A
        model_b: Configuração do modelo B
        judge_model: Modelo a usar como juiz
        criteria: Critério de julgamento
        swap_positions: Se True, executa swap para corrigir positional bias

    Returns:
        dict com win rates, ties e análise de bias
    """
    judge_client = anthropic.Anthropic()

    wins_a = 0
    wins_b = 0
    ties = 0
    bias_detected_count = 0

    results_detail = []

    for i, question in enumerate(test_questions):
        print(f"\nQuestão {i+1}/{len(test_questions)}")
        print(f"  Q: {question[:80]}...")

        # Gerar respostas dos dois modelos
        def get_response(model_cfg: ModelConfig, q: str) -> str:
            response = model_cfg.client.messages.create(
                model=model_cfg.model_id,
                max_tokens=512,
                messages=[{"role": "user", "content": q}],
            )
            return response.content[0].text

        response_a = get_response(model_a, question)
        response_b = get_response(model_b, question)

        # Julgar na ordem original
        def judge(resp_1: str, resp_2: str) -> str:
            prompt = f"""Pergunta: {question}

Resposta 1:
{resp_1}

Resposta 2:
{resp_2}

Critério: {criteria}

Responda apenas "1", "2" ou "tie"."""
            r = judge_client.messages.create(
                model=judge_model,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            verdict = r.content[0].text.strip()
            if verdict not in ["1", "2", "tie"]:
                return "tie"  # Fallback
            return verdict

        verdict_normal = judge(response_a, response_b)

        # Traduzir para A/B/tie
        def translate_verdict(v: str, a_is_1: bool) -> str:
            if v == "tie":
                return "tie"
            elif v == "1":
                return "A" if a_is_1 else "B"
            else:
                return "B" if a_is_1 else "A"

        result_normal = translate_verdict(verdict_normal, a_is_1=True)

        final_result = result_normal
        bias_detected = False

        if swap_positions:
            verdict_swapped = judge(response_b, response_a)
            result_swapped = translate_verdict(verdict_swapped, a_is_1=False)

            if result_normal != result_swapped:
                # Discordância → positional bias detectado → tie conservador
                bias_detected = True
                bias_detected_count += 1
                final_result = "tie"
            else:
                final_result = result_normal

        # Contabilizar
        if final_result == "A":
            wins_a += 1
        elif final_result == "B":
            wins_b += 1
        else:
            ties += 1

        results_detail.append({
            "question": question,
            "winner": final_result,
            "bias_detected": bias_detected,
        })

        print(f"  Vencedor: {final_result} {'(bias detectado, tie)' if bias_detected else ''}")

    total = len(test_questions)
    total_decided = wins_a + wins_b
    if total_decided == 0:
        total_decided = 1  # Evitar divisão por zero

    print(f"\n{'='*50}")
    print(f"RESULTADO FINAL ({total} questões)")
    print(f"{'='*50}")
    print(f"{model_a.display_name}: {wins_a} vitórias ({wins_a/total:.1%})")
    print(f"{model_b.display_name}: {wins_b} vitórias ({wins_b/total:.1%})")
    print(f"Empates: {ties} ({ties/total:.1%})")
    print(f"Positional bias detectado: {bias_detected_count} casos ({bias_detected_count/total:.1%})")
    print(f"Win rate A (excluindo ties): {wins_a/total_decided:.1%}")

    return {
        "model_a": model_a.display_name,
        "model_b": model_b.display_name,
        "total_questions": total,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "ties": ties,
        "win_rate_a": wins_a / total,
        "win_rate_b": wins_b / total,
        "win_rate_a_excl_ties": wins_a / total_decided,
        "positional_bias_count": bias_detected_count,
        "detail": results_detail,
    }
```

---

## Referências

- [MMLU](https://arxiv.org/abs/2009.03300) — Measuring Massive Multitask Language Understanding (Hendrycks et al., 2020)
- [HumanEval](https://arxiv.org/abs/2107.03374) — Evaluating Large Language Models Trained on Code (Chen et al., 2021)
- [BIG-Bench Hard](https://arxiv.org/abs/2210.09261) — Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them (Suzgun et al., 2022)
- [Chatbot Arena](https://arxiv.org/abs/2403.04132) — Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference (Chiang et al., 2024)
- [LLM-as-Judge](https://arxiv.org/abs/2306.05685) — Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (Zheng et al., 2023)
- [MATH Dataset](https://arxiv.org/abs/2103.03874) — Measuring Mathematical Problem Solving With the MATH Dataset (Hendrycks et al., 2021)
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) — ferramenta padrão para rodar evals

---

## Relacionado

- [[pretraining]] — onde modelos adquirem o conhecimento medido por benchmarks
- [[rlhf-alignment]] — como RLHF e DPO afetam performance em evals subjetivos
- [[fine-tuning-peft]] — como fine-tuning em dados de benchmark pode inflar scores
- [[prompt-engineering]] — sensibilidade de prompt afeta todos os benchmarks
- [[claude-api]] — implementar pipelines de eval com Anthropic API
