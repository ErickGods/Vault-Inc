---
tags: [finance, investments, derivatives, options, black-scholes, greeks]
status: active
complexity: advanced
context: global
updated: 2026-04-07
aliases: [Options, Opções, Calls, Puts]
---

# Options Basics

## Overview

Opções são contratos derivativos que dão ao comprador o **direito (não a obrigação)** de comprar (call) ou vender (put) um ativo a um preço fixo (strike) até uma data futura (vencimento). São instrumentos versáteis: podem ser usados para **especular**, **hedgear** ou **gerar renda**. Mas são também armas afiadas — opções podem evaporar 100% do capital rapidamente.

A precificação moderna nasceu com o modelo de **Black-Scholes-Merton** (1973), que rendeu Nobel a Scholes e Merton em 1997.

---

## Core Concepts

### Tipos Básicos

- **Call**: direito de **comprar** o ativo a um preço (strike) até uma data
- **Put**: direito de **vender** o ativo a um preço até uma data

### Posições

| Posição | Cenário Lucrativo | Risco |
|---------|------------------|-------|
| **Long Call** | Ativo sobe forte | Limitado ao prêmio pago |
| **Short Call** | Ativo cai/lateral | Ilimitado (se naked) |
| **Long Put** | Ativo cai forte | Limitado ao prêmio |
| **Short Put** | Ativo sobe/lateral | Alto (até strike × qtd) |

### Estilos

- **Americana**: pode ser exercida **a qualquer momento** até o vencimento (padrão B3)
- **Europeia**: só no vencimento (padrão índice/cambial)

### Valor Intrínseco vs Valor Extrínseco

```
Prêmio = Valor Intrínseco + Valor Extrínseco
```

- **Valor Intrínseco**: o que valeria se exercida agora
  - Call: max(0, Spot - Strike)
  - Put: max(0, Strike - Spot)
- **Valor Extrínseco** (tempo + volatilidade)

### Moneyness

| Estado | Call | Put |
|--------|------|-----|
| **ITM (In-the-Money)** | Spot > Strike | Spot < Strike |
| **ATM (At-the-Money)** | Spot ≈ Strike | Spot ≈ Strike |
| **OTM (Out-of-the-Money)** | Spot < Strike | Spot > Strike |

### Black-Scholes (Call Europeu)

```
C = S × N(d1) - K × e^(-rt) × N(d2)

d1 = [ln(S/K) + (r + σ²/2)t] / (σ√t)
d2 = d1 - σ√t
```

Onde:
- S = preço do ativo
- K = strike
- t = tempo até vencimento (anos)
- r = taxa livre de risco
- σ = volatilidade
- N(·) = CDF normal padrão

### Greeks

| Grego | Mede | Interpretação |
|-------|------|---------------|
| **Delta (Δ)** | ∂P/∂S | Sensibilidade ao preço (~prob ITM) |
| **Gamma (Γ)** | ∂²P/∂S² | Mudança do Delta |
| **Theta (Θ)** | ∂P/∂t | Decaimento temporal |
| **Vega (ν)** | ∂P/∂σ | Sensibilidade à vol |
| **Rho (ρ)** | ∂P/∂r | Sensibilidade aos juros |

> [!warning] Theta Decay
> Opções perdem valor com o tempo. Comprar opções é correr contra o relógio — vender é a favor (até a tese virar).

---

## How to Apply

### Estratégias Comuns

**Para gerar renda:**
- **Covered Call**: vender call sobre ações que possui
- **Cash-Secured Put**: vender put coberta por caixa para comprar a desconto

**Para hedgear:**
- **Protective Put**: comprar put para proteger ações
- **Collar**: comprar put + vender call (zero cost)

**Para especular:**
- **Long Call/Put**: alavancagem direcional
- **Straddle**: long call + long put no mesmo strike (aposta em volatilidade)
- **Strangle**: similar com strikes diferentes
- **Vertical Spread**: comprar e vender mesmo tipo, strikes diferentes (limita risco)

### Volatilidade Implícita (IV)

A vol implícita no preço da opção é a **expectativa de mercado** sobre o futuro. Comprar opção quando IV é baixa, vender quando IV é alta — princípio básico.

**VIX**: índice de volatilidade implícita do S&P 500 ("índice do medo"). > 30 = stress; < 15 = complacência.

---

## Examples

> [!example] Covered Call em PETR4
> Possui 100 PETR4 a R$ 35
> Vende 1 call PETRJ40 (strike R$ 40, vence 60 dias) por R$ 1,00
> Recebe R$ 100 de prêmio (~3% sobre o investimento em 60 dias)
>
> Cenários:
> - Petr4 < 40: opção vira pó, fica com prêmio + ações
> - Petr4 > 40: vende ações a 40 + R$ 1 prêmio = R$ 4.100 (vs custo R$ 3.500 = +17%)

> [!example] Long Put como Hedge
> Possui 100 ações VALE3 a R$ 65 (R$ 6.500)
> Compra 1 put strike R$ 60, vence 3 meses, pago R$ 2,00 (R$ 200)
> Cobre crash até R$ 60. Custo: 3% como "seguro" trimestral.

---

## Gotchas

> [!warning] Riscos Mortais
> - **Naked short call**: perda **ilimitada** se ativo dispara
> - **Theta decay**: comprar OTM com pouco tempo = lottery ticket
> - **Liquidez baixa**: spreads enormes em opções fora do padrão
> - **Exercício inesperado**: opções americanas podem ser exercidas antes
> - **Margem**: short options exigem margem; pode haver chamadas
> - **Dividendos**: ex-data afeta opções (especialmente americanas)
> - **Pin risk**: vencimento perto do strike é arriscado

> [!quote] Nassim Taleb
> *"Vendedores de opções jantam como galinhas e cagam como elefantes."* — pequenos lucros, grandes perdas eventuais.

---

## Brazilian Context

### Mercado de Opções B3

- **Ações**: opções sobre ações líquidas (PETR, VALE, ITUB, BBAS)
- **Índice**: opções de IBOV
- **Vencimentos**: 3ª segunda do mês
- **Estilo**: ações = americanas; índice = europeias
- **Liquidez**: concentrada em PETR4 e VALE3

### Tributação

- **Day trade**: 20% sobre ganho
- **Swing**: 15% sobre ganho
- **Sem isenção** dos R$ 20k
- **DARF mensal**

### Aluguel de Ações (BTC)

Para vender opção descoberta sobre ações, é comum **alugar ações** via BTC (B3) — cobra-se taxa para tomar emprestado. Comum em estratégias short.

> [!info] Iniciante? Comece Devagar
> Estratégias seguras para começar: **covered call** com ações que já possui. Evite long puts/calls especulativas até dominar Greeks.

---

## Formulas

```
# Put-call parity
C - P = S - K × e^(-rt)

# Delta de call (aproximação)
Δ_call = N(d1)

# Delta de put
Δ_put = N(d1) - 1

# Break-even
Long Call: BE = Strike + Prêmio pago
Long Put:  BE = Strike - Prêmio pago

# P&L máximo (long call)
Lucro = max(0, S_T - K) - Prêmio
```

---

## References

- Hull, J. — *Options, Futures and Other Derivatives*
- Natenberg, S. — *Option Volatility and Pricing*
- Taleb, N. — *Dynamic Hedging*
- McMillan, L. — *Options as a Strategic Investment*

---

## Related

- [[futures]] — Outro derivativo
- [[hedging-strategies]] — Uso defensivo
- [[position-sizing]] — Sizing em opções
- [[backtesting-basics]] — Testar estratégias
- [[behavioral-finance]] — Vieses em derivativos
- [[tax-optimization-br]] — IR sobre opções
