---
tags: [finance, investments, derivatives, futures, mini-indice, mini-dolar]
status: active
complexity: advanced
context: global
updated: 2026-04-07
aliases: [Futures, Futuros, Mini-Índice, Mini-Dólar, WIN, WDO]
---

# Futures Contracts

## Overview

Futuros são contratos **padronizados** negociados em bolsa para comprar ou vender um ativo a preço pré-determinado em data futura. Diferente das opções, futuros são **obrigações simétricas**: ambas as partes devem cumprir. Surgiram para hedge de produtores agrícolas, mas hoje cobrem desde commodities até índices de ações, juros, moedas e até cripto.

No Brasil, os futuros mais negociados pelo varejo são **Mini-Índice (WIN)** e **Mini-Dólar (WDO)** — populares para day trade pela alta alavancagem.

---

## Core Concepts

### Características

- **Padronizados**: tamanho, vencimento, qualidade definidos pela bolsa
- **Margem**: depósito de garantia (5-15% do nocional)
- **Marcação a mercado diária**: ganhos/perdas creditados no caixa todo dia
- **Câmara de compensação**: B3/CME garante a contraparte
- **Alavancagem alta**: 1:10 a 1:20 típico

### Futuros vs Forwards

| | Futuros | Forwards |
|---|---------|----------|
| Negociação | Bolsa | OTC |
| Padronização | Sim | Não |
| Margem | Sim | Não |
| MtM diário | Sim | Não |
| Risco contraparte | Câmara | Direta |

### Conceitos-Chave

**Contrato Futuro = Contrato à vista + custo de carregamento**

```
F = S × e^((r - q)×t)
```

Onde:
- S = preço spot
- r = taxa livre de risco
- q = dividend yield (ou cupom)
- t = tempo até vencimento

### Contango vs Backwardation

- **Contango**: F > S (custo de carregamento positivo)
- **Backwardation**: F < S (escassez física, prêmio para spot)

### Tipos por Subjacente

- **Equity index futures**: ES (S&P), NQ (Nasdaq), WIN (IBOV mini)
- **Currency futures**: 6E (Euro), 6J (Yen), WDO (USD/BRL mini)
- **Interest rate futures**: ZN (10y note), DI (Brasil)
- **Commodity futures**: CL (WTI), GC (ouro), ZS (soja)
- **Crypto futures**: BTC, ETH (CME)

---

## How to Apply

### Mini-Índice (WIN) — B3

- **Subjacente**: Ibovespa
- **Tamanho**: 0,2 × IBOV em pontos × R$ 1
- **Tick**: 5 pontos (R$ 1 por mini)
- **Margem**: ~R$ 100-300 por contrato (varia)
- **Vencimentos**: meses pares (G2, J4, M6, Q8, V10, Z12)
- **Contrato cheio (IND)**: 5x o mini

> [!example] WIN
> IBOV = 130.000 pontos
> 1 mini WIN = 130.000 × 0,2 × R$ 1 = R$ 26.000 de exposição
> Movimento de 1 ponto = R$ 0,20 por mini
> Movimento de 100 pontos = R$ 20

### Mini-Dólar (WDO) — B3

- **Subjacente**: USD/BRL
- **Tamanho**: US$ 10.000
- **Tick**: 0,5 ponto = R$ 5
- **Margem**: ~R$ 200-500
- **Vencimentos**: todos os meses

### Estratégias com Futuros

1. **Hedge cambial**: exportador vende WDO para travar câmbio
2. **Hedge de portfólio**: vender WIN para proteger ações
3. **Especulação direcional**: day trade alavancado
4. **Spread trading**: comprar 1 vencimento + vender outro
5. **Carry trade**: explorar contango em commodities

---

## Examples

> [!example] Hedge de Portfólio
> Possui R$ 200k em ações brasileiras
> Quer hedge tático antes de evento de risco
> Vende mini-WIN equivalente:
>
> R$ 200.000 / R$ 26.000 (1 mini) ≈ 8 mini-WIN
>
> Se IBOV cai 5%, ações perdem R$ 10k mas hedge ganha ~R$ 10,4k.

> [!example] Especulação WDO
> Compra 1 mini-WDO a 5.100 (USD/BRL)
> Margem: R$ 300
> Dólar sobe para 5.150 → +50 pontos × R$ 10 = +R$ 500
> Retorno: 167% sobre margem em horas
> Mas: -50 pontos = -R$ 500 (perda > margem)

---

## Gotchas

> [!warning] Alavancagem é Faca de Dois Gumes
> - **Margem call**: se o saldo cai abaixo do mínimo, exige aporte ou liquida posição
> - **Movimentos rápidos**: WIN pode mover 500 pontos em minutos = R$ 100/mini
> - **Day trade contra você**: spreads, slippage, custos
> - **Gap de abertura**: WDO abre com gap pelo overnight global
> - **Falta de liquidez** no after-hours
> - **Roll over**: trocar de contrato no vencimento gera custo

> [!quote] Estatística B3
> ~90% dos day traders perdem dinheiro no primeiro ano. Futuros são onde mais se queima capital de varejo.

---

## Brazilian Context

### Tributação

- **Day trade**: 20% sobre ganho líquido + 1% IR retido na fonte
- **Swing trade**: 15% sobre ganho líquido
- **Sem isenção** R$ 20k
- **Compensação de prejuízos**: dentro da mesma modalidade
- **DARF**: cód. 6015 mensal

### Custos

- **Corretagem**: zero ou ~R$ 0,50 por mini
- **Emolumentos B3**: ~R$ 0,40 por mini
- **Imposto**: 20%/15% sobre lucro
- **Custódia**: zerada para day trade

### Sistema de Margem

B3 calcula margem por SPAN (Standard Portfolio Analysis of Risk). Exige garantias em **dinheiro, títulos públicos, ações ou ouro**.

> [!info] Profit, MetaTrader, TryD
> Plataformas profissionais para futuros B3. Necessárias para execução rápida e DOM (book de ordens).

---

## Formulas

```
# Preço futuro
F = S × e^((r - q)×t)

# P&L de contrato
P&L = (F_venda - F_compra) × Multiplicador × Nº contratos

# Margem
Margem = Margem_inicial × Nº contratos

# Alavancagem efetiva
Lev = Nocional / Margem

# Valor do tick
Tick value = Tick size × Multiplicador
```

---

## References

- Hull, J. — *Options, Futures and Other Derivatives*
- B3 — *Manual de Procedimentos Operacionais*
- CME Group — *Futures Education*
- Schwager, J. — *Market Wizards*

---

## Related

- [[options-basics]] — Outro derivativo
- [[hedging-strategies]] — Uso defensivo
- [[position-sizing]] — Sizing alavancado
- [[backtesting-basics]] — Estratégias quant
- [[brazilian-market-b3]] — Estrutura B3
- [[commodities]] — Subjacentes futuros
- [[risk-tolerance]] — Necessária para futuros
