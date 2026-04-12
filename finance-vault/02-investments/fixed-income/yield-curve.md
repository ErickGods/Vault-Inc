---
tags: [finance, investments, fixed-income, yield-curve, macro]
status: active
complexity: advanced
context: global
updated: 2026-04-07
aliases: [Yield Curve, Curva de Juros, Estrutura a Termo]
---

# Yield Curve

## Overview

A Yield Curve (curva de juros) é a representação gráfica das taxas de juros de títulos de mesma qualidade de crédito (geralmente Treasuries ou títulos públicos) por **diferentes prazos de vencimento**. É uma das ferramentas mais poderosas de análise macro: contém informação sobre **expectativas de juros, inflação, crescimento e probabilidade de recessão**.

A inversão da curva (juros curtos > longos) precedeu **todas** as recessões americanas dos últimos 60 anos.

---

## Core Concepts

### Formatos da Curva

- **Normal (positively sloped)**: longos > curtos. Sinal de expectativa de crescimento e inflação saudável
- **Plana**: longos ≈ curtos. Incerteza
- **Invertida**: curtos > longos. Mercado precifica corte futuro de juros — sinal recessivo
- **Steepening**: spread aumentando
- **Flattening**: spread diminuindo

### Spread 10y-2y (US)

```
Spread = Yield_10y - Yield_2y
```

**Inversão (Spread < 0)** é o leading indicator clássico de recessão.

### Teorias Explicativas

1. **Pure Expectations**: yields longos = média esperada dos curtos futuros
2. **Liquidity Preference**: investidores exigem prêmio para prazos longos
3. **Market Segmentation**: cada prazo tem oferta/demanda própria
4. **Preferred Habitat**: combinação das anteriores

### Componentes do Yield

```
Yield Nominal = Real Yield + Inflação Esperada + Prêmio de Risco
```

- **Real Yield**: derivável de TIPS / NTN-B
- **Breakeven Inflation**: yield nominal - real
- **Term Premium**: prêmio por prazo

---

## How to Apply

### Sinais de Investimento

| Curva | Sinal | Estratégia |
|-------|-------|-----------|
| **Steep + crescente** | Início de recuperação | Ações cíclicas, bancos |
| **Plana** | Final de ciclo | Defensivos, qualidade |
| **Invertida** | Recessão à vista | Bonds longos, defensivos, cash |
| **Re-steepening** | BC pivot | Bull steepener — bonds longos primeiro |

### Bull vs Bear Steepening/Flattening

- **Bull Steepening**: curtos caem mais que longos (BC corta juros)
- **Bear Steepening**: longos sobem mais que curtos (inflação ou risco fiscal)
- **Bull Flattening**: longos caem mais que curtos (flight to quality)
- **Bear Flattening**: curtos sobem mais que longos (BC sobe juros)

### Carry Trade na Curva

Vender curto + comprar longo capta o term premium. Funciona em curvas íngremes; perigoso em curvas planas/invertidas (carry vs convexidade).

---

## Examples

> [!example] Inversão 2022-2023 (US)
> Em julho/2022, spread 10y-2y inverteu (-0,2%). Em julho/2023 atingiu -1,1% (mais profunda em 40 anos).
> Recessão técnica? Pelo NBER, ainda não — mas o sinal seguia válido até 2025.
> S&P 500 caiu -19% em 2022, recuperou em 2023.

> [!example] Curva Brasileira
> Em outubro/2024:
> - DI Jan/2026: 12,5%
> - DI Jan/2030: 13,2%
> - DI Jan/2035: 13,5%
> Curva levemente positiva, mas com prêmio fiscal alto na ponta longa.

---

## Gotchas

> [!warning] Limitações
> - **Lag de 12-24 meses** entre inversão e recessão — não use para timing
> - **QE distorce a curva** (Fed comprando longas)
> - **Term premium negativo** em algumas épocas torna comparação histórica difícil
> - **Curva BR ≠ curva US**: prêmio fiscal e cambial dominam no Brasil
> - **Prefixados curtos** podem distorcer leitura por carregamento de Selic

---

## Brazilian Context

### Curva DI x Pré

A curva mais acompanhada no Brasil é a **DI futuro** (juros interbancários de cada vencimento). Sinaliza expectativa do mercado para Selic futura.

- **DI Jan/26, Jan/27, Jan/28...**: cada vencimento é um ponto da curva
- **Inflação implícita**: diferença entre prefixado e NTN-B (mesmo prazo)
- **Prêmio fiscal**: alta da curva longa quando sobe risco fiscal

### Onde Acompanhar

- **Anbima**: curva ETTJ (estrutura a termo) diária
- **BCB**: focus survey, expectativas
- **B3**: DI futuro tempo real

> [!info] Inflação Implícita BR
> ```
> Implícita = (1+Pré_n) / (1+NTN-B_n) - 1
> ```
> Útil para decidir entre prefixado e IPCA+ no Tesouro Direto.

---

## Formulas

```
# Term spread
Spread = Y_long - Y_short

# Forward rate (1 ano daqui a 1)
f_1,2 = [(1+y_2)^2 / (1+y_1)] - 1

# Inflação implícita
π_implícita = [(1+y_nominal)/(1+y_real)] - 1

# Duration sensitivity (recap)
ΔP/P ≈ -Duration × Δy
```

---

## References

- Estrella, A.; Mishkin, F. — *The Yield Curve as a Predictor of Recession* (1996)
- Fabozzi, F. — *Bond Markets and Strategies*
- BCB — *Estrutura a Termo da Taxa de Juros*
- Anbima — *Metodologia ETTJ*
- FRED — *Treasury Constant Maturity Rates*

---

## Related

- [[bonds-international]] — Treasuries
- [[tesouro-direto]] — Curva BR
- [[interest-rate-cycles]] — Drivers
- [[ray-dalio-machine]] — Curva nos ciclos de dívida
- [[global-macro-indicators]] — Leading indicator
- [[inflation]] — Componente do yield
