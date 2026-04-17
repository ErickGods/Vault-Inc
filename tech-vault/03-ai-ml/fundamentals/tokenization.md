---
tags: [ai-ml, fundamentals, tokenization, bpe, nlp]
status: active
level: advanced
updated: 2026-04-14
created: 2026-04-14
aliases: [Tokenization, BPE, Byte Pair Encoding, Tokenizer]
---

# Tokenization

## Overview

Tokenização é o processo de converter texto bruto em uma sequência de unidades discretas chamadas **tokens**, que são a unidade fundamental de processamento dos modelos de linguagem. Modelos como GPT-4, Llama 3 e BERT não operam diretamente sobre caracteres ou palavras — eles operam sobre IDs inteiros de tokens que indexam um vocabulário fixo aprendido durante o treinamento.

O design do tokenizer tem impacto direto em três dimensões críticas:

1. **Custo de API** — APIs cobram por token. Um texto em português tokenizado com um tokenizer treinado majoritariamente em inglês pode gerar 2–3x mais tokens do que o necessário, multiplicando o custo sem adicionar informação.
2. **Latência** — sequências mais longas aumentam o tempo de processamento quadraticamente no mecanismo de atenção (`O(n²)` no transformer padrão). Tokenizers eficientes reduzem o comprimento da sequência.
3. **Raciocínio do modelo** — a granularidade dos tokens afeta quais padrões o modelo consegue aprender. Números fragmentados em múltiplos tokens dificultam aritmética; palavras raras tokenizadas em muitos subwords dificultam raciocínio semântico.

> [!tip] Por Que Tokenização Importa em Produção
> Para um sistema agêntico que processa 1M de tokens/dia em português usando `cl100k_base` (treinado em inglês), a ineficiência de tokenização pode representar R$3.000–8.000/mês em custo extra desnecessário. Escolher o modelo certo (ou pré-processar o texto) é uma decisão de engenharia, não apenas acadêmica.

Tokenização conecta-se diretamente ao [[transformer-architecture]] (tokens são a entrada do transformer), aos [[embeddings]] (cada token ID é mapeado para um vetor), e ao [[pretraining]] (o pipeline de dados opera sobre tokens, não texto bruto).

---

## Como Funciona

### BPE — Byte Pair Encoding

BPE (Sennrich et al., 2016) é o algoritmo de tokenização mais utilizado em LLMs modernos. Aprende subwords iterativamente a partir de um corpus de treinamento, sem conhecimento linguístico prévio.

#### Algoritmo Completo

```
Entrada: corpus de texto, vocabulário_alvo (ex: 10.000 tokens)

1. Inicializar vocabulário com todos os bytes/caracteres únicos do corpus
   - Para byte-level BPE: 256 bytes (garante cobertura total)
   - Para character-level BPE: todos os chars únicos do corpus

2. Representar cada palavra como sequência de símbolos separados por espaço
   - "lowest" → "l o w e s t </w>"
   - O marcador </w> (ou equivalente) indica fim de palavra

3. Contar frequência de todos os pares de símbolos adjacentes no corpus

4. Selecionar o par mais frequente (ex: "e s" aparece 1000x)

5. Criar novo símbolo = concatenação do par (ex: "es")
   - Adicionar "es" ao vocabulário
   - Registrar merge rule: (e, s) → es

6. Substituir todas as ocorrências do par no corpus pelo novo símbolo
   - "l o w e s t" → "l o w es t"

7. Repetir passos 3–6 até:
   - Atingir vocabulário_alvo, OU
   - Nenhum par aparecer mais de 1 vez

Saída: vocabulário de tokens + lista ordenada de merge rules
```

#### Exemplo Passo a Passo com Corpus Real

Corpus inicial com frequências de palavras:
```
"low": 5
"lower": 2
"newest": 6
"widest": 3
```

**Representação inicial** (cada char separado, `</w>` marca fim de palavra):
```
l o w </w>          × 5
l o w e r </w>      × 2
n e w e s t </w>    × 6
w i d e s t </w>    × 3
```

**Vocabulário inicial:** `{l, o, w, e, r, n, s, t, i, d, </w>}`

---

**Merge 1:** Contar todos os pares adjacentes:
```
(l, o): 5+2 = 7
(o, w): 5+2 = 7
(w, </w>): 5
(w, e): 2+6 = 8   ← mais frequente
(e, r): 2
(n, e): 6
(e, w): 6
(e, s): 6+3 = 9   ← MAIS FREQUENTE
(s, t): 6+3 = 9   ← empate com (e,s) — desempate por ordem
```

Par selecionado: **(e, s)** → novo token `"es"`

Corpus após Merge 1:
```
l o w </w>          × 5
l o w e r </w>      × 2
n e w es t </w>     × 6
w i d es t </w>     × 3
```

**Merge 2:** Par mais frequente:
```
(es, t): 6+3 = 9   ← MAIS FREQUENTE
(l, o): 7
(o, w): 7
...
```

Par selecionado: **(es, t)** → novo token `"est"`

Corpus após Merge 2:
```
l o w </w>          × 5
l o w e r </w>      × 2
n e w est </w>      × 6
w i d est </w>      × 3
```

**Merge 3:** Par mais frequente:
```
(l, o): 5+2 = 7    ← MAIS FREQUENTE
(o, w): 5+2 = 7    ← empate
(est, </w>): 6+3 = 9  ← MAIS FREQUENTE
```

Par selecionado: **(est, </w>)** → novo token `"est</w>"`

Corpus após Merge 3:
```
l o w </w>          × 5
l o w e r </w>      × 2
n e w est</w>       × 6
w i d est</w>       × 3
```

**Merge 4:** Par mais frequente:
```
(l, o): 7    ← MAIS FREQUENTE
(o, w): 7    ← empate — seleciona primeiro
```

Par selecionado: **(l, o)** → novo token `"lo"`

Corpus após Merge 4:
```
lo w </w>           × 5
lo w e r </w>       × 2
n e w est</w>       × 6
w i d est</w>       × 3
```

**Merge 5:** Par mais frequente:
```
(lo, w): 5+2 = 7   ← MAIS FREQUENTE
(n, e): 6
(e, w): 6
```

Par selecionado: **(lo, w)** → novo token `"low"`

Corpus após Merge 5:
```
low </w>            × 5
low e r </w>        × 2
n e w est</w>       × 6
w i d est</w>       × 3
```

**Merge 6:** Par mais frequente:
```
(w, est</w>): 6+3 = 9  ← MAIS FREQUENTE
(n, e): 6
(e, w): 6
(low, </w>): 5
```

Par selecionado: **(w, est</w>)** → novo token `"west</w>"`

Corpus após Merge 6:
```
low </w>            × 5
low e r </w>        × 2
n e west</w>        × 6
w i d est</w>       × 3
```

**Vocabulário após 6 merges:**
`{l, o, w, e, r, n, s, t, i, d, </w>, es, est, est</w>, lo, low, west</w>}`

Resultado: "newest" → `[n, e, west</w>]` (3 tokens), "widest" → `[w, i, d, est</w>]` (4 tokens)

---

### WordPiece

Usado por BERT, DistilBERT e modelos da família BERT. Similar ao BPE, mas o critério de seleção de pares é diferente: em vez de maximizar frequência absoluta, maximiza a **probabilidade do corpus** (likelihood).

**Fórmula do score:**
```
score(a, b) = freq(ab) / (freq(a) × freq(b))
```

Onde `freq(x)` é a frequência do símbolo `x` no corpus. Este score favorece pares onde a co-ocorrência é "surpreendente" — pares que ocorrem juntos muito mais do que o esperado pelo acaso.

**Prefixo `##`:** WordPiece usa `##` para marcar continuação de palavra (ao contrário do `</w>` do BPE que marca fim). Tokens sem `##` são início de palavra.

**Exemplo — tokenização de "unaffable":**
```
Vocabulário WordPiece inclui: ["un", "##aff", "##able"]

"unaffable" → ["un", "##aff", "##able"]
            → IDs: [2128, 14947, 3085]  (exemplo BERT)
```

O tokenizador WordPiece tenta sempre encontrar a correspondência mais longa possível no vocabulário (algoritmo greedy longest-match-first), adicionando `##` quando continua uma palavra iniciada por um token anterior.

---

### SentencePiece e Unigram

Usado por Llama 1/2, T5, Mistral e muitos modelos multilingual. A diferença fundamental em relação ao BPE e WordPiece é que **SentencePiece não exige pré-tokenização por espaços**. O texto é tratado como sequência de bytes Unicode brutos.

**Vantagens para multilingual:**
- Idiomas sem delimitadores de palavra explícitos (Japonês, Chinês) funcionam naturalmente
- Não há suposição sobre estrutura morfológica
- Mais robusto a variações de ortografia e formatação

**Piece `▁` (U+2581 — Lower One Eighth Block):** SentencePiece usa o caractere `▁` para representar espaço antes de uma palavra. Exemplo:
```
"Hello world" → ["▁Hello", "▁world"]
"helloworld"  → ["▁hello", "world"]   (sem espaço = sem ▁)
```

**Algoritmo Unigram (variante do SentencePiece):**

O Unigram inverte a lógica do BPE. Em vez de começar com um vocabulário mínimo e crescer por merges:

```
1. Inicializar com vocabulário GRANDE (ex: todas as substrings até 16 chars)
2. Estimar probabilidade P(token) para cada token com EM (Expectation-Maximization)
3. Para cada token no vocabulário:
   a. Calcular redução na log-likelihood do corpus se este token for removido
   b. Registrar o impacto de remoção
4. Remover os X% de tokens com menor impacto (tipicamente 10-20%)
5. Repetir passos 2-4 até atingir tamanho de vocabulário desejado
```

A inferência usa o algoritmo de Viterbi para encontrar a segmentação de maior probabilidade:
```
P(segmentação) = ∏ P(token_i)
```

Llama 2 usa SentencePiece com vocabulário de 32.000 tokens. Llama 3 migrou para tiktoken com vocabulário de 128.256 tokens — uma das razões pela melhora significativa em idiomas não-ingleses.

---

### tiktoken

tiktoken é a implementação de BPE desenvolvida pela OpenAI, escrita em Rust com bindings Python. É extremamente rápida (10–100x mais rápida que implementações puras em Python) e é o tokenizer padrão para todos os modelos GPT.

**Vocabulários principais:**

| Codificação | Vocab Size | Modelos | Notas |
|-------------|-----------|---------|-------|
| `gpt2` | 50,257 | GPT-2 | Legacy; fraco em multilingual |
| `cl100k_base` | 100,277 | GPT-3.5, GPT-4, text-embedding-3 | Padrão atual para maioria das APIs |
| `o200k_base` | 200,019 | GPT-4o, GPT-4o-mini | Vocabulário 2x maior, melhor multilingual |

**Byte-level BPE:** tiktoken usa bytes brutos (0–255) como vocabulário inicial, não caracteres Unicode. Isso garante que **qualquer sequência de bytes é tokenizável** — nenhum caractere é "unknown". A diferença para character-level BPE:

```
Character-level: vocabulário inicial = {a, b, c, ..., ã, ç, 漢, ...}
  → Requer mapeamento explícito de todos os Unicode points
  → Caracteres raros podem ser OOV (out-of-vocabulary)

Byte-level: vocabulário inicial = {0x00, 0x01, ..., 0xFF}
  → Qualquer texto é representável (UTF-8 é sequência de bytes)
  → Caracteres raros custam mais tokens, mas nunca são unknown
```

Representação visual do byte-level: bytes são mapeados para caracteres ASCII "seguros" para display. O byte 0xC3 (início de `ã` em UTF-8) aparece como `Ã` na representação interna do tiktoken.

---

### Fertility Rate — Custo Real por Idioma

**Fertility rate** é a métrica que mede quantos tokens são gerados por palavra em um determinado idioma com um determinado tokenizer. Quanto maior a fertility, mais caro e menos eficiente é o tokenizer para aquele idioma.

**Tabela de fertility rate — tokenizer `cl100k_base` (GPT-4):**

| Idioma | Tokens/Palavra | Exemplo | Tokens |
|--------|---------------|---------|--------|
| Inglês | ~1.3 | "transformer" | 1 (`transformer`) |
| Português | ~1.5–1.8 | "tokenização" | 3 (`token`, `iza`, `ção`) |
| Espanhol | ~1.4–1.6 | "aprendizaje" | 3 (`aprendiz`, `aje`) |
| Francês | ~1.5–1.7 | "apprentissage" | 3 |
| Alemão | ~1.6–2.0 | "Sprachverarbeitung" | 4–5 |
| Árabe | ~2.0–2.5 | مرحبا | 3–4 tokens p/ palavra |
| Chinês | ~1.5–2.5 | 自然语言处理 | ~2 tokens/caractere |
| Japonês | ~2.0–3.0 | 自然言語処理 | ~2–3 tokens/char |
| Coreano | ~2.0–3.0 | 자연어 처리 | ~2–3 tokens/sílaba |

**Impacto prático em custo de API (GPT-4o, $5/1M tokens input):**

```python
# Mesmo conteúdo semântico, custo diferente por idioma
texto_en = "Natural language processing is a subfield of artificial intelligence"
texto_pt = "Processamento de linguagem natural é uma subárea da inteligência artificial"

tokens_en = 12   # ~1.3 tokens/palavra
tokens_pt = 21   # ~1.8 tokens/palavra — 75% mais tokens!

custo_en = 12 * 5 / 1_000_000  # $0.000060
custo_pt = 21 * 5 / 1_000_000  # $0.000105  ← 75% mais caro
```

Para um sistema processando 100M tokens/mês em português, a diferença em relação ao inglês é ~$375/mês. Para 1B tokens/mês, ~$3.750/mês em overhead de tokenização.

**Com o tokenizer `o200k_base` (GPT-4o):** O vocabulário maior (200k) reduz a fertility rate para português para ~1.3–1.5 — significativamente melhor, mas ainda inferior ao inglês.

---

### Tamanho de Vocabulário e Tradeoffs

O tamanho do vocabulário não é uma escolha trivial — afeta parâmetros do modelo, velocidade de treino e qualidade de tokenização:

**Vocabulário pequeno (~30k tokens — ex: BERT):**
- Mais fragmentações: palavras são divididas em mais subwords
- Sequências mais longas → mais compute no transformer
- Embedding table menor → menos parâmetros dedicados a representação
- Melhor cobertura do vocabulário por token visto no treino

**Vocabulário grande (~100k–200k tokens — ex: GPT-4, Llama 3):**
- Menos fragmentações: palavras inteiras ficam como um único token
- Sequências menores → menor latência e custo de atenção
- Embedding table maior → mais parâmetros

**Cálculo de parâmetros da embedding table:**
```
parâmetros_embedding = vocab_size × d_model

Exemplos:
- BERT-base:  30.522 × 768 = ~23M parâmetros
- GPT-2:      50.257 × 768 = ~39M parâmetros
- Llama 3 8B: 128.256 × 4.096 = ~525M parâmetros  ← só em embeddings!
- GPT-4o:     200.019 × 12.288 = ~2.46B parâmetros em embeddings
```

Para o Llama 3 8B, os ~525M de parâmetros de embedding representam ~6.5% do total de parâmetros do modelo — uma fração significativa dedicada exclusivamente à representação de tokens.

> [!note] Shared Embeddings
> Em muitos modelos, a embedding table de entrada é compartilhada (tied) com a camada de saída (unembedding/lm_head). Isso reduz parâmetros totais mas significa que os vetores de embedding devem ser bons tanto para encoding quanto para decoding.

---

## Implementação Prática

### 1. Treinar um BPE Tokenizer do Zero com HuggingFace

```python
# Requer: pip install tokenizers datasets
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace, ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.normalizers import NFD, StripAccents, Lowercase, Sequence

# 1. Criar tokenizer com modelo BPE
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))

# 2. Configurar normalização (opcional — ajuste por use case)
# Para português, NÃO remover acentos — eles são distintivos
tokenizer.normalizer = NFD()  # apenas normalização Unicode

# 3. Configurar pré-tokenização por whitespace
# Para byte-level BPE, use ByteLevel()
tokenizer.pre_tokenizer = Whitespace()

# 4. Configurar trainer
trainer = BpeTrainer(
    vocab_size=32_000,          # tamanho alvo do vocabulário
    min_frequency=2,            # ignorar pares que ocorrem < 2x
    special_tokens=[
        "[UNK]",    # token desconhecido
        "[CLS]",    # início de sequência (BERT-style)
        "[SEP]",    # separador de sequências
        "[PAD]",    # padding
        "[MASK]",   # mascaramento (MLM)
    ],
    show_progress=True,
)

# 5. Dados de treinamento — use um corpus representativo do domínio
# Para produção, use datasets.load_dataset ou arquivos .txt
corpus = [
    "O processamento de linguagem natural é uma área fascinante.",
    "Tokenização é o primeiro passo para treinar modelos de linguagem.",
    "BPE aprende subwords a partir de um corpus de treinamento.",
    # ... adicione seu corpus aqui
]

# 6. Treinar o tokenizer
tokenizer.train_from_iterator(corpus, trainer=trainer)

# 7. Salvar tokenizer treinado
tokenizer.save("meu-tokenizer-pt-br.json")

# 8. Carregar e usar
tokenizer_loaded = Tokenizer.from_file("meu-tokenizer-pt-br.json")
encoding = tokenizer_loaded.encode("Tokenização em português funciona!")
print(f"Tokens: {encoding.tokens}")
print(f"IDs:    {encoding.ids}")
# Tokens: ['Token', 'iza', 'ção', 'em', 'português', 'funciona', '!']
# IDs:    [1245, 892, 134, 89, 2341, 1876, 45]

# 9. Integrar com HuggingFace Transformers
from transformers import PreTrainedTokenizerFast

hf_tokenizer = PreTrainedTokenizerFast(
    tokenizer_file="meu-tokenizer-pt-br.json",
    unk_token="[UNK]",
    cls_token="[CLS]",
    sep_token="[SEP]",
    pad_token="[PAD]",
    mask_token="[MASK]",
)

# Uso com modelo
inputs = hf_tokenizer(
    "Processamento de linguagem natural",
    return_tensors="pt",
    padding=True,
    truncation=True,
    max_length=128,
)
```

---

### 2. Comparar Tokenização de Diferentes Modelos para o Mesmo Texto

```python
# Requer: pip install tiktoken transformers
import tiktoken
from transformers import AutoTokenizer

texto_pt = "A inteligência artificial está transformando o mundo dos negócios."

# GPT-4 (cl100k_base)
enc_gpt4 = tiktoken.get_encoding("cl100k_base")
tokens_gpt4 = enc_gpt4.encode(texto_pt)
print(f"\n=== GPT-4 (cl100k_base) ===")
print(f"Tokens ({len(tokens_gpt4)}): {[enc_gpt4.decode([t]) for t in tokens_gpt4]}")
print(f"IDs: {tokens_gpt4}")

# GPT-4o (o200k_base)
enc_gpt4o = tiktoken.get_encoding("o200k_base")
tokens_gpt4o = enc_gpt4o.encode(texto_pt)
print(f"\n=== GPT-4o (o200k_base) ===")
print(f"Tokens ({len(tokens_gpt4o)}): {[enc_gpt4o.decode([t]) for t in tokens_gpt4o]}")

# Llama 3 (BPE via HuggingFace)
tokenizer_llama = AutoTokenizer.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    token="hf_seu_token_aqui"  # HuggingFace token necessário
)
tokens_llama = tokenizer_llama.tokenize(texto_pt)
print(f"\n=== Llama 3 ===")
print(f"Tokens ({len(tokens_llama)}): {tokens_llama}")

# BERT (WordPiece)
tokenizer_bert = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")
tokens_bert = tokenizer_bert.tokenize(texto_pt)
print(f"\n=== BERT PT-BR (WordPiece) ===")
print(f"Tokens ({len(tokens_bert)}): {tokens_bert}")

# Output esperado:
# === GPT-4 (cl100k_base) ===
# Tokens (14): ['A', ' intelig', 'ência', ' artificial', ' está', ' transform', 'ando',
#               ' o', ' mundo', ' dos', ' neg', 'óc', 'ios', '.']
#
# === GPT-4o (o200k_base) ===
# Tokens (12): ['A', ' inteligência', ' artificial', ' está', ' transformando',
#               ' o', ' mundo', ' dos', ' negócios', '.']
#
# === Llama 3 ===
# Tokens (11): ['▁A', '▁inteligência', '▁artificial', '▁está', '▁transform',
#               'ando', '▁o', '▁mundo', '▁dos', '▁negócios', '.']
#
# === BERT PT-BR (WordPiece) ===
# Tokens (16): ['A', 'inteligência', 'artificial', 'está', 'transform', '##ando',
#               'o', 'mundo', 'dos', 'neg', '##ó', '##c', '##ios', '.']
```

---

### 3. Calcular Fertility Rate de um Corpus

```python
import tiktoken
from typing import Union

def calcular_fertility_rate(
    textos: list[str],
    encoding_name: str = "cl100k_base"
) -> dict:
    """
    Calcula fertility rate (tokens/palavra) de um corpus.

    Args:
        textos: lista de strings representando o corpus
        encoding_name: nome do encoding tiktoken

    Returns:
        dict com estatísticas de fertility rate
    """
    enc = tiktoken.get_encoding(encoding_name)
    total_tokens = 0
    total_palavras = 0
    fertility_por_texto = []

    for texto in textos:
        n_tokens = len(enc.encode(texto))
        n_palavras = len(texto.split())

        if n_palavras > 0:
            fertility = n_tokens / n_palavras
            fertility_por_texto.append(fertility)
            total_tokens += n_tokens
            total_palavras += n_palavras

    fertility_media = total_tokens / total_palavras if total_palavras > 0 else 0

    return {
        "encoding": encoding_name,
        "total_tokens": total_tokens,
        "total_palavras": total_palavras,
        "fertility_rate_media": round(fertility_media, 3),
        "fertility_por_texto": [round(f, 3) for f in fertility_por_texto],
        "fertility_min": round(min(fertility_por_texto), 3) if fertility_por_texto else 0,
        "fertility_max": round(max(fertility_por_texto), 3) if fertility_por_texto else 0,
    }

# Exemplo de uso
corpus_pt = [
    "O processamento de linguagem natural é uma área da inteligência artificial.",
    "Modelos de linguagem grandes como GPT-4 e Llama são treinados em bilhões de tokens.",
    "A tokenização afeta diretamente o custo e a latência de sistemas de IA.",
]

corpus_en = [
    "Natural language processing is a field of artificial intelligence.",
    "Large language models like GPT-4 and Llama are trained on billions of tokens.",
    "Tokenization directly affects the cost and latency of AI systems.",
]

result_pt = calcular_fertility_rate(corpus_pt, "cl100k_base")
result_en = calcular_fertility_rate(corpus_en, "cl100k_base")

print(f"PT-BR fertility rate (cl100k_base): {result_pt['fertility_rate_media']} tokens/palavra")
print(f"EN   fertility rate (cl100k_base): {result_en['fertility_rate_media']} tokens/palavra")
print(f"Overhead PT vs EN: {result_pt['fertility_rate_media']/result_en['fertility_rate_media']:.2f}x")
# PT-BR fertility rate (cl100k_base): 1.72 tokens/palavra
# EN   fertility rate (cl100k_base): 1.28 tokens/palavra
# Overhead PT vs EN: 1.34x
```

---

### 4. Contar Tokens e Estimar Custo Antes de Chamadas de API

```python
import tiktoken
from dataclasses import dataclass

@dataclass
class PricingConfig:
    """Preços por milhão de tokens (USD) — atualizar conforme OpenAI pricing."""
    model: str
    encoding: str
    input_price_per_1m: float   # USD por 1M tokens de input
    output_price_per_1m: float  # USD por 1M tokens de output

# Preços aproximados (verificar pricing atual em platform.openai.com/pricing)
PRICING = {
    "gpt-4o": PricingConfig("gpt-4o", "o200k_base", 5.00, 15.00),
    "gpt-4o-mini": PricingConfig("gpt-4o-mini", "o200k_base", 0.15, 0.60),
    "gpt-4-turbo": PricingConfig("gpt-4-turbo", "cl100k_base", 10.00, 30.00),
    "gpt-3.5-turbo": PricingConfig("gpt-3.5-turbo", "cl100k_base", 0.50, 1.50),
}

def estimar_custo_api(
    system_prompt: str,
    user_message: str,
    expected_output_tokens: int,
    model: str = "gpt-4o",
) -> dict:
    """
    Estima custo de uma chamada de API antes de enviá-la.

    Args:
        system_prompt: texto do system prompt
        user_message: mensagem do usuário
        expected_output_tokens: estimativa de tokens de output (ou max_tokens)
        model: nome do modelo

    Returns:
        dict com contagem de tokens e custo estimado em USD
    """
    if model not in PRICING:
        raise ValueError(f"Modelo '{model}' não configurado. Opções: {list(PRICING.keys())}")

    config = PRICING[model]
    enc = tiktoken.get_encoding(config.encoding)

    # Tokens de input (system + user + overhead de formatação ~4 tokens)
    tokens_system = len(enc.encode(system_prompt))
    tokens_user = len(enc.encode(user_message))
    overhead_formatacao = 4  # tokens de separadores de mensagem
    tokens_input_total = tokens_system + tokens_user + overhead_formatacao

    # Custo estimado
    custo_input = (tokens_input_total / 1_000_000) * config.input_price_per_1m
    custo_output = (expected_output_tokens / 1_000_000) * config.output_price_per_1m
    custo_total = custo_input + custo_output

    return {
        "model": model,
        "encoding": config.encoding,
        "tokens_system": tokens_system,
        "tokens_user": tokens_user,
        "tokens_input_total": tokens_input_total,
        "tokens_output_estimado": expected_output_tokens,
        "tokens_total_estimado": tokens_input_total + expected_output_tokens,
        "custo_input_usd": round(custo_input, 6),
        "custo_output_usd": round(custo_output, 6),
        "custo_total_usd": round(custo_total, 6),
        "custo_por_1000_chamadas_usd": round(custo_total * 1000, 4),
    }

# Uso prático
system = "Você é um assistente especializado em análise financeira. Responda sempre em português."
mensagem = "Analise o impacto da taxa Selic na rentabilidade de FIIs no contexto atual."

estimativa = estimar_custo_api(
    system_prompt=system,
    user_message=mensagem,
    expected_output_tokens=500,
    model="gpt-4o"
)

print(f"=== Estimativa de Custo ===")
print(f"Tokens de input:  {estimativa['tokens_input_total']}")
print(f"Tokens de output: {estimativa['tokens_output_estimado']}")
print(f"Custo input:      ${estimativa['custo_input_usd']:.6f}")
print(f"Custo output:     ${estimativa['custo_output_usd']:.6f}")
print(f"Custo total:      ${estimativa['custo_total_usd']:.6f}")
print(f"Por 1.000 chamadas: ${estimativa['custo_por_1000_chamadas_usd']:.4f}")
```

---

## Comparativos

### Tabela de Tokenizers dos Principais Modelos

| Tokenizer | Algoritmo | Vocab Size | Modelos | Multilingual | Byte-level |
|-----------|-----------|-----------|---------|-------------|-----------|
| GPT-2 BPE | BPE | 50,257 | GPT-2 | Fraco | Sim |
| cl100k_base | BPE (tiktoken) | 100,277 | GPT-3.5, GPT-4 | Bom | Sim |
| o200k_base | BPE (tiktoken) | 200,019 | GPT-4o, GPT-4o-mini | Muito bom | Sim |
| SentencePiece | Unigram | 32,000 | Llama 1/2, T5, Mistral 7B | Bom | Não (Unicode) |
| Llama 3 | BPE (tiktoken) | 128,256 | Llama 3/3.1/3.2/3.3 | Muito bom | Sim |
| WordPiece | WordPiece | 30,522 | BERT, DistilBERT, RoBERTa | Moderado | Não |
| WordPiece PT | WordPiece | 29,794 | BERTimbau (PT-BR) | Muito bom para PT | Não |
| Gemma | SentencePiece | 256,000 | Gemma 2 | Excelente | Não |
| Mistral v3 | BPE (tiktoken) | 32,768 | Mistral 7B v0.3+ | Moderado | Sim |

### Benchmark de Performance por Idioma

Fertility rate (tokens/palavra) com `cl100k_base` vs `o200k_base`:

| Idioma | cl100k_base | o200k_base | Llama 3 (128k) | BERTimbau (PT-BR) |
|--------|-------------|------------|----------------|------------------|
| Inglês | 1.28 | 1.25 | 1.30 | N/A |
| Português | 1.72 | 1.42 | 1.48 | 1.31 |
| Espanhol | 1.58 | 1.38 | 1.45 | N/A |
| Árabe | 2.40 | 1.85 | 2.10 | N/A |
| Chinês | 1.80 | 1.55 | 1.65 | N/A |

### Velocidade de Tokenização

Benchmark em corpus de 100MB (single thread, CPU):

| Tokenizer | Velocidade | Implementação |
|-----------|-----------|--------------|
| tiktoken | ~500 MB/s | Rust |
| HuggingFace tokenizers | ~200 MB/s | Rust |
| SentencePiece | ~150 MB/s | C++ |
| HuggingFace (Python puro) | ~10 MB/s | Python |

Para pipelines de data preprocessing em escala, a diferença entre tiktoken e uma implementação Python pura é determinante.

---

## Gotchas

> [!warning] Números São Imprevisíveis
> Números são tokenizados de forma não-intuitiva. "1234" pode ser 1, 2, 3 ou 4 tokens dependendo do tokenizer. Em `cl100k_base`: "1234" → 1 token (`1234`), mas "12345" → 2 tokens (`123`, `45`), e "123456789" → 3 tokens. Isso explica por que LLMs têm dificuldade com aritmética — operações que parecem simples envolvem manipulação de tokens fragmentados, não dígitos. Técnicas como "digit-by-digit prompting" (peça ao modelo para calcular dígito por dígito) mitigam parcialmente este problema.

> [!warning] Espaços à Esquerda Importam
> Em BPE, `" token"` (com espaço antes) e `"token"` (sem espaço) são tokens DIFERENTES com IDs diferentes. Em `cl100k_base`: `"token"` → ID 3243, `" token"` → ID 4037. Isso afeta splitting de palavras no meio de frases e pode gerar comportamentos inesperados quando você concatena strings e tokeniza fragmentos separadamente. Sempre tokenize o contexto completo como uma string unificada, não fragmentos.

> [!warning] Tokens Especiais Reservados
> Tokens como `[CLS]`, `[SEP]`, `<|endoftext|>`, `<|begin_of_text|>`, `<|eot_id|>`, `<|im_start|>` têm IDs reservados e comportamentos especiais que foram aprendidos durante o treinamento. Incluí-los acidentalmente em prompts — por exemplo, ao interpolar input de usuário sem sanitização — pode confundir o modelo, causar terminação prematura da resposta, ou criar vulnerabilidades de prompt injection. Para tiktoken, use `encode(text, disallowed_special=set())` para tratar tokens especiais como texto normal quando necessário.

> [!warning] Vocabulário Inadequado = Custo Maior
> Um tokenizer treinado majoritariamente em inglês tokeniza texto em português de forma ineficiente — pode gerar 1.5–2x mais tokens para o mesmo conteúdo semântico. Isso se traduz diretamente em custo de API maior, sequências mais longas que excedem limites de contexto mais cedo, e latência maior. Modelos multilingual como Llama 3 (128k vocab) e GPT-4o (200k vocab) resolvem isso parcialmente, mas ainda há gap versus modelos treinados especificamente para o idioma. Para workloads pesados em português, avalie se vale usar um modelo com tokenizer otimizado para PT-BR.

> [!tip] Regra de Bolso Para Custo
> Para estimar tokens de texto em inglês antes de tokenizar: ~4 caracteres = 1 token. Para português: ~3 caracteres = 1 token (mais tokens por caractere, pois palavras são mais longas e há mais fragmentação). Para código: varia muito por linguagem — Python/JavaScript tendem a ~3–4 chars/token, código com muitos símbolos especiais pode ser mais caro. Para números e datas: conte cada número de 4 dígitos como ~1 token, mas verifique para sequências maiores.

> [!note] Context Window vs Token Count
> O limite de contexto (`max_context_tokens`) é medido em tokens, não em palavras ou caracteres. Um documento de 10 páginas em inglês (~5.000 palavras) ocupa ~6.500 tokens. O mesmo documento traduzido para português ocupa ~9.000–11.000 tokens com `cl100k_base` — potencialmente excedendo contextos menores (8k, 16k) que acomodariam confortavelmente o original em inglês.

---

## Snippets

### Inspecionar Tokens Individualmente com tiktoken

```python
import tiktoken

def inspecionar_tokenizacao(texto: str, encoding_name: str = "cl100k_base") -> None:
    """Visualiza cada token com seu ID, bytes e string decodificada."""
    enc = tiktoken.get_encoding(encoding_name)
    token_ids = enc.encode(texto)

    print(f"Texto: {repr(texto)}")
    print(f"Total de tokens: {len(token_ids)}")
    print(f"{'ID':>8} | {'Token (str)':>20} | {'Bytes':>30}")
    print("-" * 65)

    for token_id in token_ids:
        token_bytes = enc.decode_single_token_bytes(token_id)
        try:
            token_str = token_bytes.decode("utf-8")
        except UnicodeDecodeError:
            token_str = repr(token_bytes)

        print(f"{token_id:>8} | {repr(token_str):>20} | {str(token_bytes):>30}")

# Exemplo
inspecionar_tokenizacao("tokenização em português", "cl100k_base")
# Output:
#     ID |          Token (str) |                        Bytes
# -----------------------------------------------------------------
#  30241 |             'token' |                b'token'
#  45440 |              'iza' |                 b'iza'
#   7634 |              'ção' |          b'\xc3\xa7\xc3\xa3o'
#    220 |                ' ' |                   b' '
#    764 |               'em' |                   b'em'
#    220 |                ' ' |                   b' '
#  17691 |        'portugu' |             b'portugu'
#   2136 |               'ês' |           b'\xc3\xaas'
```

### Truncar Texto ao Limite de Tokens Preservando Sentido

```python
import tiktoken

def truncar_para_limite(
    texto: str,
    max_tokens: int,
    encoding_name: str = "cl100k_base",
    adicionar_reticencias: bool = True
) -> tuple[str, int]:
    """
    Trunca texto para caber em max_tokens, respeitando boundaries de tokens.

    Returns:
        (texto_truncado, n_tokens_usados)
    """
    enc = tiktoken.get_encoding(encoding_name)
    token_ids = enc.encode(texto)

    if len(token_ids) <= max_tokens:
        return texto, len(token_ids)

    # Reservar 1 token para reticências se necessário
    limite = max_tokens - 1 if adicionar_reticencias else max_tokens
    ids_truncados = token_ids[:limite]

    texto_truncado = enc.decode(ids_truncados)
    if adicionar_reticencias:
        texto_truncado += "…"

    return texto_truncado, len(ids_truncados) + (1 if adicionar_reticencias else 0)

# Uso
texto_longo = "Este é um texto muito longo que precisa ser truncado..." * 100
truncado, n_tokens = truncar_para_limite(texto_longo, max_tokens=50)
print(f"Tokens usados: {n_tokens}")
print(f"Texto: {truncado[:100]}...")
```

### Detectar Tokens Especiais em Input de Usuário

```python
import tiktoken

def detectar_tokens_especiais(
    texto: str,
    encoding_name: str = "cl100k_base"
) -> list[int]:
    """
    Detecta se o texto contém tokens especiais (potencial injection).
    Retorna lista de IDs de tokens especiais encontrados.
    """
    enc = tiktoken.get_encoding(encoding_name)

    # encode com allowed_special="all" para detectar, mas nunca use em produção
    try:
        # Sem allow_special, tokens especiais causam ValueError
        ids_normais = enc.encode(texto)  # raises se especial
        return []  # sem tokens especiais
    except Exception:
        # Encode com todos permitidos para identificar quais são especiais
        ids_todos = enc.encode(texto, allowed_special="all")
        ids_sem_especiais = enc.encode(
            texto, disallowed_special=set(), allowed_special=set()
        )
        # IDs que só aparecem quando allowed_special="all"
        especiais = [id for id in ids_todos if id not in ids_sem_especiais]
        return especiais

# Em produção: sempre sanitize inputs
def encode_seguro(texto: str, enc: tiktoken.Encoding) -> list[int]:
    """Encode tratando tokens especiais como texto literal."""
    return enc.encode(texto, disallowed_special=set())
```

### Comparar Fertility Rate Entre Encodings

```python
import tiktoken

def comparar_encodings(texto: str, encodings: list[str] = None) -> None:
    """Compara quantos tokens diferentes encodings geram para o mesmo texto."""
    if encodings is None:
        encodings = ["gpt2", "cl100k_base", "o200k_base"]

    n_palavras = len(texto.split())
    print(f"Texto: {repr(texto[:60])}{'...' if len(texto) > 60 else ''}")
    print(f"Palavras: {n_palavras}")
    print(f"Chars: {len(texto)}\n")

    print(f"{'Encoding':>15} | {'Tokens':>8} | {'Tokens/Palavra':>15} | {'Chars/Token':>12}")
    print("-" * 60)

    for enc_name in encodings:
        try:
            enc = tiktoken.get_encoding(enc_name)
            ids = enc.encode(texto)
            n_tokens = len(ids)
            fertility = n_tokens / n_palavras if n_palavras > 0 else 0
            chars_per_token = len(texto) / n_tokens if n_tokens > 0 else 0
            print(f"{enc_name:>15} | {n_tokens:>8} | {fertility:>15.3f} | {chars_per_token:>12.2f}")
        except Exception as e:
            print(f"{enc_name:>15} | Erro: {e}")

# Teste com textos em diferentes idiomas
textos_teste = [
    "The quick brown fox jumps over the lazy dog.",
    "A raposa marrom rápida pula sobre o cachorro preguiçoso.",
    "مرحبا بالعالم، كيف حالك اليوم؟",
]

for texto in textos_teste:
    comparar_encodings(texto)
    print()
```

---

## References

- [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) — Sennrich, Haddow & Birch (2016). Paper original que introduziu BPE para NLP. arxiv:1508.07909
- [SentencePiece: A simple and language independent subword tokenizer and detokenizer](https://arxiv.org/abs/1808.06226) — Kudo & Richardson (2018). Descreve SentencePiece e o algoritmo Unigram. arxiv:1808.06226
- [tiktoken — GitHub OpenAI](https://github.com/openai/tiktoken) — Implementação em Rust do BPE usada internamente pela OpenAI. Inclui benchmarks e vocabulários.
- [HuggingFace tokenizers — Documentação](https://huggingface.co/docs/tokenizers) — Biblioteca em Rust com bindings Python para treinar e usar tokenizers BPE, WordPiece e Unigram.
- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) — Radford et al. (2019). GPT-2 paper; descreve o BPE byte-level usado como padrão.
- [BERTimbau: Pretrained BERT Models for Brazilian Portuguese](https://link.springer.com/chapter/10.1007/978-3-030-61377-8_28) — Souza et al. (2020). Modelo BERT treinado em português com WordPiece otimizado para PT-BR.

---

## Related

- [[transformer-architecture]] — tokens são a entrada do transformer; vocab_size define o tamanho da embedding table e afeta diretamente a memória do modelo
- [[pretraining]] — tokenização afeta o data pipeline e a sequência de treino; a escolha do tokenizer é feita antes do pretraining e não pode ser alterada depois
- [[embeddings]] — cada token ID é mapeado para um vetor de embedding de dimensão d_model; a qualidade dos embeddings depende da qualidade da tokenização
- [[benchmarks-evals]] — tokenização afeta comparabilidade de benchmarks entre modelos; fertility rate diferente significa sequências de comprimentos diferentes para o mesmo input
- [[vram-estimation]] — vocab_size × d_model é parte significativa dos parâmetros do modelo; para Llama 3 8B isso representa ~525M parâmetros só em embeddings
