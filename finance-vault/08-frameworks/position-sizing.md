---
tags: [finance, frameworks, position-sizing, risk-management]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Tamanho de Posição, Sizing]
---

# Position Sizing

## Overview

Position Sizing é a decisão de **quanto capital alocar em cada posição individual**. É a ferramenta mais poderosa de gestão de risco — mais importante que a escolha do ativo. Como diz Van Tharp: *"position sizing tells you 'how much' — and 'how much' is what determines whether you survive and thrive in trading."*

Um bom trader/investidor com mau sizing perde dinheiro; um mediano com bom sizing sobrevive e capitaliza.

---

## Core Concepts

### Risk per Trade

Capital máximo que se aceita perder em uma posição se a tese falhar:

```
Risk = Capital × % Risco × Distância ao Stop
```

Regra de bolso: **1-2% do capital total por trade**.

### Kelly Criterion

Fórmula matemática para tamanho ótimo dado vantagem estatística:

```
f* = (p × b - q) / b
```

Onde:
- f* = fração do capital
- p = probabilidade de ganho
- q = 1 - p = probabilidade de perda
- b = razão ganho/perda (payoff)

> [!tip] Half-Kelly
> Kelly puro é matematicamente ótimo mas emocionalmente brutal (drawdowns >50%). Praticantes usam **Half-Kelly** ou **Quarter-Kelly** para suavizar a curva.

### Volatility-Based Sizing

Posições inversamente proporcionais à volatilidade:

```
Tamanho_i = (Capital × Risco_alvo) / (σ_i × Multiplicador)
```

Ativos mais voláteis recebem menor alocação — equaliza risco contribuído.

### Conviction-Based Sizing

Tamanho proporcional à convicção × edge esperado. Buffett: *"diversification is protection against ignorance."*

---

## How to Apply

### Modelo de Stop e Sizing

1. Defina o **stop loss** (preço de saída se errar)
2. Calcule **risco por ação** = Preço atual - Stop
3. Determine **risco total aceitável** (ex: 1% do capital)
4. Calcule **número de ações** = Risco total / Risco por ação

### Pyramiding

Adicionar à posição vencedora conforme tese se confirma. Reduz risco médio mantendo upside.

---

## Examples

> [!example] Cálculo Prático
> Capital: R$ 100.000
> Risco máximo por trade: 1% = R$ 1.000
> Ação PETR4 a R$ 35,00
> Stop loss em R$ 32,00 (risco R$ 3,00/ação)
>
> ```
> Nº de ações = 1.000 / 3,00 = 333 ações
> Capital alocado = 333 × 35 = R$ 11.655 (11,7% do total)
> ```
> Mesmo com 11,7% alocado, o risco real é apenas 1%.

> [!example] Kelly em prática
> Estratégia: 60% acerto, ganha 2x quando acerta, perde 1x quando erra
> ```
> f* = (0,6 × 2 - 0,4) / 2 = 0,4 (40% do capital!)
> Half-Kelly = 20% (mais realista)
> ```

---

## Gotchas

> [!warning] Erros Mortais
> - **All-in em uma tese**: ruína matemática certa em horizonte longo
> - **Aumentar posição em loss** (averaging down sem tese revisada)
> - **Não ter stop**: deixar perda virar "investimento de longo prazo"
> - **Sizing por preço**: comprar mais ações de ativos baratos sem ajustar por volatilidade
> - **Kelly puro**: drawdowns inaceitáveis na prática
> - **Ignorar correlação**: 5 posições de 10% em bancos = 50% no setor

---

## Brazilian Context

- **Lote padrão B3**: 100 ações (lotes fracionários disponíveis para varejo)
- **Custos**: corretagem zero hoje em dia, mas IR de 15% (swing) ou 20% (day) afeta sizing pós-imposto
- **Liquidez baixa em small caps**: respeitar limite de **% do volume diário** (≤10%) para evitar mover preço
- **Margem**: alavancagem padrão BMF 2-5x — multiplica risco

> [!warning] Day Trade no Brasil
> Para day trade, IR é 20% sobre ganhos com retenção de 1% na fonte (dedo-duro). Sizing deve considerar imposto.

---

## Formulas

```
# Risco por trade
Risco_R$ = Capital × % Risco

# Quantidade
Qtd = Risco_R$ / (Preço_entrada - Stop)

# Kelly
f* = (p × b - q) / b
Half-Kelly = f* / 2

# Volatility sizing
Tamanho = (Capital × Vol_alvo) / Vol_ativo

# Risk parity
w_i = (1/σ_i) / Σ(1/σ_j)
```

---

## References

- Tharp, V. — *Trade Your Way to Financial Freedom*
- Kelly, J. — *A New Interpretation of Information Rate* (1956)
- Thorp, E. — *The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market*
- Schwager, J. — *Market Wizards*

---

## Related

- [[capital-allocation]] — Decisão macro de alocação
- [[risk-and-return]] — Trade-off subjacente
- [[investment-checklist]] — Validação pré-trade
- [[backtesting-basics]] — Validar edge antes de aplicar Kelly
- [[risk-tolerance]] — Limite emocional vs matemático
- [[trade-journal-template]] — Tracking de execução
