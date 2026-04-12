---
tags: [finance, investments, equities, growth, value, garp]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Growth vs Value, GARP]
---

# Growth vs Value Investing

## Overview

Growth e Value são os dois principais **estilos de investimento** em ações. Value busca empresas negociadas abaixo do valor intrínseco (Buffett, Graham). Growth busca empresas com crescimento de receita e lucro acima da média (Fisher, Lynch). GARP (Growth at a Reasonable Price) tenta combinar os dois.

Historicamente, value teve melhor performance de longo prazo (Fama-French), mas nos últimos 15 anos growth dominou por conta de tech e juros baixos.

---

## Core Concepts

### Value Investing

**Tese**: comprar barato em relação a fundamentos.

**Características das ações value**:
- P/L baixo (< média do mercado)
- P/VPA baixo (< 1,5)
- Dividend Yield alto
- Crescimento moderado
- Setores: bancos, utilities, commodities, indústria

**Mestres**: Graham, Buffett, Klarman, Schloss, Pabrai.

### Growth Investing

**Tese**: pagar mais hoje por crescimento futuro acelerado.

**Características das ações growth**:
- P/L alto (>20)
- Crescimento de receita > 15% a.a.
- Reinveste lucros (paga pouco dividendo)
- Margens expandindo
- Setores: tech, biotech, consumo discricionário

**Mestres**: Philip Fisher, Peter Lynch, Bill O'Neil, Cathie Wood.

### GARP (Growth at Reasonable Price)

Híbrido popularizado por Peter Lynch. Critérios típicos:
- PEG ≤ 1,0
- ROE > 15%
- Crescimento de lucros 15-25% a.a.
- D/E moderado

```
PEG = (P/L) / Crescimento esperado %
```

### Fama-French Three Factor Model

Incluiu **Value (HML)** como fator que explica retornos além do beta de mercado e tamanho (SMB). Value premium = small + value bate large + growth no longo prazo.

> [!warning] Value Trap
> Nem toda ação barata é value. Empresas em decadência estrutural parecem baratas mas continuam baratas. Distinguir **temporariamente fora de moda** (oportunidade) de **terminalmente em declínio** (armadilha).

---

## How to Apply

### Screening Value

```
P/L < 12
P/VPA < 1,5
ROE > 12%
Dívida/PL < 1
Dividend Yield > 4%
Lucro positivo nos últimos 5 anos
```

### Screening Growth

```
Crescimento receita > 15% (3 anos)
Crescimento EPS > 20%
Margem bruta > 40%
ROE > 15%
Insider ownership relevante
```

### Mix por Ciclo

| Regime | Estilo Vencedor |
|--------|-----------------|
| Juros caindo | Growth |
| Juros subindo | Value |
| Recessão | Value defensivo (utilities) |
| Recuperação | Growth cíclico |
| Bull market maduro | Quality (mix) |

---

## Examples

> [!example] Value Clássico
> Itaú em 2016: P/L 7, P/VPA 1,3, DY 5%, ROE 19% — value clássico. Subiu 200% nos anos seguintes.

> [!example] Growth Clássico
> Mercado Livre em 2017: P/L > 100, mas crescimento de receita > 60% a.a. Subiu 10x até 2021.

> [!example] GARP
> Localiza pré-fusão Unidas: P/L 15, crescimento de 25% a.a., ROE 18%. PEG = 0,6 → muito atrativo.

---

## Gotchas

> [!warning] Erros Comuns
> - **Value trap**: confundir barato com valor
> - **Growth pricing collapse**: pagar caro por crescimento que não vem
> - **Style drift**: trocar de estilo no pior momento (top de growth, fundo de value)
> - **Backtest sem ajuste de inflação/juros**: regimes mudam
> - **Confundir momentum com growth**

---

## Brazilian Context

- **Mercado brasileiro é mais value** que growth (poucas teses de tech puro)
- **Value brasileiro**: bancos, energia, sanitárias, commodities
- **Growth brasileiro**: Mercado Livre (mas BDR), MGLU3 (caso de bull e bust), Locaweb
- **Selic alta** estruturalmente favorece value (lucros hoje > promessas futuras)
- **Benchmarks**: IDIV (dividendos/value) vs IBrX (geral)

> [!info] Index Value vs Growth Brasil
> ETFs brasileiros não cobrem value/growth puros. Investidor sofisticado faz screening próprio via Status Invest, Fundamentus, Bloomberg.

---

## Formulas

```
# PEG
PEG = (P/L) / g (em %)

# Value composite (Greenblatt Magic Formula)
Score = Rank(EBIT/EV) + Rank(ROIC)
# Comprar top do score

# Growth score (composição comum)
Score = Crescimento Receita + Crescimento EPS + ROE
```

---

## References

- Lynch, P. — *One Up on Wall Street*
- Fisher, P. — *Common Stocks and Uncommon Profits*
- Greenblatt, J. — *The Little Book That Beats the Market*
- Fama, E.; French, K. — *Common Risk Factors in Stock Returns* (1993)
- O'Neil, W. — *How to Make Money in Stocks* (CAN SLIM)

---

## Related

- [[stocks-fundamentals]] — Base
- [[valuation-multiples]] — Métricas de value
- [[warren-buffett-framework]] — Quality + value
- [[graham-net-net]] — Deep value
- [[factor-investing]] — Value como fator
- [[momentum-strategies]] — Estilo alternativo
- [[investment-checklist]] — Validação
