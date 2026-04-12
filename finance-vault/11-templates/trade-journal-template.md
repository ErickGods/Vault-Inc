---
tags:
  - finance
  - templates
  - journal
aliases:
  - Diário de Trades
  - Trade Journal
complexity: basic
context: global
created: 2026-04-06
updated: 2026-04-06
---

# Trade Journal — {{ticker}} | {{date}}

---

## Informações do Trade

| Campo              | Valor              |
| ------------------ | ------------------ |
| **Data**           | {{date}}           |
| **Ticker**         | {{ticker}}         |
| **Direção**        | {{direction}}      |
| **Preço de Entrada** | {{entry_price}}  |
| **Preço-Alvo**     | {{target_price}}   |
| **Stop Loss**      | {{stop_loss}}      |
| **Risco/Retorno**  | <!-- calcular R:R --> |
| **Timeframe**      | <!-- Intraday / Swing / Position --> |

---

## 1. Setup

**Tipo de setup:**
<!-- Breakout, Pullback, Reversão, Momentum, Mean Reversion, etc. -->

**Indicadores / Sinais utilizados:**
- [ ] Médias Móveis (SMA/EMA):
- [ ] RSI:
- [ ] Volume:
- [ ] Suporte/Resistência:
- [ ] Padrão gráfico:
- [ ] Outro:

**Screenshot do gráfico no momento da entrada:**
<!-- Colar imagem do gráfico aqui -->

---

## 2. Tese do Trade

> [!quote] Por que estou entrando neste trade?
> <!-- Descreva sua tese de forma clara e objetiva. Qual é o edge? Por que agora? -->

**Confluência de fatores:**
1.
2.
3.

**O que invalidaria a tese?**
<!-- Descreva o cenário em que você estaria errado -->

---

## 3. Position Sizing

| Parâmetro                  | Valor      |
| -------------------------- | ---------- |
| Capital total disponível   | R$         |
| Risco máximo por trade     |    %       |
| Valor em risco (R$)        | R$         |
| Tamanho da posição (ações) |            |
| Valor da posição (R$)      | R$         |
| % do portfólio             |    %       |

Regra utilizada: <!-- 1% rule, Kelly Criterion, Fixed Fractional, etc. -->

Veja [[position-sizing]] para metodologias de dimensionamento.

---

## 4. Entry Checklist

Antes de executar, confirme todos os itens:

- [ ] Setup claramente identificado e documentado
- [ ] Relação risco/retorno mínima de 2:1
- [ ] Stop loss definido em nível técnico (não arbitrário)
- [ ] Position size dentro dos limites de risco
- [ ] Não há notícia/evento iminente que possa causar gap
- [ ] Liquidez adequada no book de ofertas
- [ ] Estado emocional neutro (sem FOMO, vingança ou euforia)
- [ ] Trade alinhado com o plano/sistema de trading

---

## 5. Gerenciamento da Posição

**Plano de saída parcial:**
<!-- Ex: realizar 50% no alvo 1, trailing stop no restante -->

**Plano de trailing stop:**
<!-- Como ajustar o stop conforme o trade evolui -->

**Log de atualizações:**

| Data | Ação | Preço | Observação |
| ---- | ---- | ----- | ---------- |
|      |      |       |            |
|      |      |       |            |

---

## 6. Post-Trade Review

> [!warning] Preencher APÓS o encerramento do trade

### Resultado

| Métrica             | Valor      |
| ------------------- | ---------- |
| Data de saída       |            |
| Preço de saída      | R$         |
| P&L (R$)            | R$         |
| P&L (%)             |    %       |
| Duração do trade    |    dias    |
| R múltiplo          |    R       |

### Execução

- [ ] Seguiu o plano de entrada?
- [ ] Seguiu o plano de saída?
- [ ] Respeitou o stop loss?
- [ ] Position size estava correto?

### Análise Emocional

**Estado emocional durante o trade:**
<!-- Calmo, ansioso, confiante demais, indeciso, etc. -->

**Vieses cognitivos identificados:**
- [ ] Viés de confirmação
- [ ] Aversão à perda
- [ ] FOMO (Fear of Missing Out)
- [ ] Overconfidence
- [ ] Anchoring (ancoragem)
- [ ] Sunk cost fallacy
- [ ] Outro:

Veja [[cognitive-biases]] e [[investor-psychology]] para aprofundamento.

### Lições Aprendidas

> [!tip] O que levar para os próximos trades?
> 1.
> 2.
> 3.

**O que fiz bem:**
-

**O que posso melhorar:**
-

**Classificação do trade:** ⭐ / ⭐⭐ / ⭐⭐⭐ / ⭐⭐⭐⭐ / ⭐⭐⭐⭐⭐
<!-- Avalie a EXECUÇÃO, não o resultado. Um trade perdedor pode ter sido bem executado. -->

---

## Referências Cruzadas

- [[investor-psychology]] — Psicologia do investidor
- [[position-sizing]] — Dimensionamento de posição
- [[cognitive-biases]] — Vieses cognitivos no mercado
