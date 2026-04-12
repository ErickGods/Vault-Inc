---
tags: [finance, analysis, fundamental, valuation, multiples]
status: active
complexity: intermediate
context: global
updated: 2026-04-07
aliases: [Valuation por Múltiplos, Múltiplos]
---

# Valuation by Multiples

## Overview

Valuation por múltiplos é o método **relativo** de avaliação: compara-se o preço de um ativo a uma métrica financeira (lucro, receita, EBITDA, patrimônio) e se contrasta com peers ou histórico. É rápido, intuitivo e amplamente usado — mas perigoso quando aplicado sem rigor.

Damodaran resume: *"DCF é mais rigoroso, múltiplos são mais usados."* Bons analistas dominam ambos e os usam como check cruzado.

---

## Core Concepts

### Tipos de Múltiplos

**De Equity** (preço por ação):
- P/L (P/E) — Preço / Lucro
- P/VPA (P/B) — Preço / Valor Patrimonial
- P/Receita (P/S) — Preço / Receita
- P/FCF — Preço / Free Cash Flow

**De Enterprise Value** (mais comparável entre empresas com estruturas de capital diferentes):
- EV/EBITDA
- EV/EBIT
- EV/Receita
- EV/FCFF

> [!tip] Quando Usar EV vs P
> Use **EV/EBITDA** para comparar empresas com alavancagens diferentes. Use **P/L** apenas entre empresas com estruturas de capital similares.

### P/L (Price-to-Earnings)

```
P/L = Preço / LPA = Market Cap / Lucro Líquido
```

Significa: anos de lucro atual para "pagar" o preço. P/L 15 = pagaria em 15 anos se lucro fosse constante.

**Earnings Yield** = 1/PL → comparável diretamente a yields de bonds.

### PEG Ratio (Peter Lynch)

```
PEG = (P/L) / Crescimento esperado %
```

PEG ≤ 1,0 = ação subvalorizada relativa ao crescimento.

### EV/EBITDA

Múltiplo favorito de M&A. Neutro em estrutura de capital, ignora D&A (relevante em capital-intensivos), mas tem o problema de [[income-statement|EBITDA]] ignorar capex.

### Justified P/L (Modelo de Gordon)

```
P/L Justo = (1 - b) × (1+g) / (r - g)
```

Onde b = retention ratio, g = crescimento, r = custo de equity.

Mostra que múltiplo "justo" depende de **crescimento, payout e risco**.

---

## How to Apply

### Processo Comparativo

1. **Identificar peers** verdadeiros (mesmo setor, porte, geografia, modelo)
2. **Coletar múltiplos** históricos e atuais (TTM e forward)
3. **Calcular mediana e quartis** do grupo
4. **Ajustar por diferenças** de crescimento, margens, risco
5. **Posicionar a empresa** no ranking
6. **Triangular** com DCF e múltiplos históricos da própria empresa

### Match com DCF

Use múltiplos para **sanity check** do DCF. Se DCF dá P/L implícito de 50x num setor que negocia a 15x, ou tem premissas erradas ou tese contrarian extraordinária.

---

## Examples

> [!example] Análise de Peers (Bancos)
> | Banco | P/L | P/VPA | ROE | Div Yield |
> |-------|-----|-------|-----|-----------|
> | ITUB4 | 8,5 | 1,8 | 21% | 6% |
> | BBDC4 | 7,0 | 1,2 | 17% | 7% |
> | SANB11 | 6,5 | 1,1 | 15% | 6% |
> | BBAS3 | 4,5 | 0,9 | 19% | 9% |
> | **Mediana** | **6,75** | **1,15** | **18%** | **6,5%** |
>
> BBAS3 negocia abaixo da mediana com ROE acima — possível desconto por risco político (estatal).

> [!example] PEG
> Empresa com P/L = 20 e crescimento esperado de 25% a.a.:
> PEG = 20 / 25 = 0,8 → barata para o crescimento
>
> Empresa com P/L = 12 e crescimento de 5%:
> PEG = 12 / 5 = 2,4 → cara para o crescimento

---

## Gotchas

> [!warning] Armadilhas
> - **Comparar peras com maçãs**: peers errados invalidam tudo
> - **Lucros não-recorrentes**: P/L distorcido por one-times
> - **Empresas com prejuízo**: P/L é inútil ou negativo
> - **Cíclicas no pico**: P/L baixo no pico do ciclo é armadilha (compra cara)
> - **Ignorar contabilidade criativa**: EBITDA ajustado pode esconder problemas
> - **Múltiplos de mercados eufóricos**: comprar a múltiplos altos exige crescimento que raramente ocorre
> - **Não considerar growth/quality differential**

> [!quote] Damodaran
> *"A multiple without a story is just a number. A story without a multiple is just a hope."*

---

## Brazilian Context

Múltiplos típicos no Brasil:

| Setor | P/L típico | EV/EBITDA |
|-------|-----------|-----------|
| Bancos | 6-10 | n/a |
| Utilities (energia) | 8-12 | 6-8 |
| Varejo | 12-20 | 8-12 |
| Commodities (Vale, Petr) | 4-8 | 3-5 |
| Tech | 20-40 | 15-25 |
| FIIs | n/a | n/a (use P/VPA e Yield) |

> [!info] Particularidades
> - **JCP** distorce P/L vs peers internacionais (deduzido como despesa financeira)
> - **Cíclicas**: usar earnings normalizados ou múltiplos históricos
> - **Bancos**: P/VPA e ROE são mais relevantes que EV/EBITDA
> - **FIIs**: P/VPA e Dividend Yield são as métricas-chave

---

## Formulas

```
# P/L
P/L = Preço / LPA
LPA = Lucro Líquido / Nº ações

# Earnings Yield
EY = LPA / Preço = 1 / P/L

# P/VPA
P/VPA = Preço / VPA
VPA = PL / Nº ações

# EV/EBITDA
EV = Market Cap + Dívida Líquida + Minoritários - Investimentos
EV/EBITDA = EV / EBITDA

# PEG
PEG = (P/L) / g (em %)

# Justified P/L (Gordon)
P/L* = [(1-b)(1+g)] / (r - g)
```

---

## References

- Damodaran, A. — *The Little Book of Valuation*
- Koller, Goedhart, Wessels — *Valuation*
- Lynch, P. — *One Up on Wall Street*
- Greenwald, B. — *Value Investing: From Graham to Buffett*

---

## Related

- [[valuation-dcf]] — Método absoluto
- [[warren-buffett-framework]] — Combina múltiplos e qualidade
- [[graham-net-net]] — Múltiplos defensivos
- [[key-ratios]] — Ratios financeiros
- [[ratio-formulas]] — Fórmulas
- [[investment-checklist]] — Validação
- [[stock-analysis-template]] — Template
